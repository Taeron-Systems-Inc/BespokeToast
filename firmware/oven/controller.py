# SPDX-License-Identifier: MIT
"""Temperature control.

Three parts, each doing one thing:

``FeedForward``  the duty needed just to *hold* a temperature. On an oven this
    large and this slow, feedback alone spends the whole run catching up. The
    feed-forward term does most of the work and the PID only trims it.

``PID``  proportional-integral-derivative on the tracking error, with the
    derivative taken on the measurement rather than the error so that a step
    in the setpoint does not kick the output.

``TimeProportional``  converts a 0-1 duty into relay states over a window,
    with minimum dwell times. A mechanical relay is switched here, so the
    window latches on rather than chattering when duty is high.

And one thing that is not a controller at all:

``predict_peak``  where the oven will end up if heat is removed *now*. On a
    lag-dominant oven, cutting power does not stop the rise: the heat already
    between element and probe keeps arriving. Nothing that decides when to
    stop by looking only at the present temperature can hit a peak.
"""

from oven.ratetable import as_table


def clamp(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)


class FeedForward(object):
    """Duty required to make the oven do what the profile asks.

    Not just to *hold* a temperature -- to follow a commanded rate. The step
    test measures the rate at full power, h(T), and the rate with the relay
    open, c(T). Between them the response is very close to linear in duty:

        dT/dt = c(T) + u * (h(T) - c(T))

    Inverting that gives the duty for any commanded rate:

        u = (rate - c(T)) / (h(T) - c(T))

    with rate=0 recovering the hold duty. This is the inverse plant, so the
    PID is left correcting model error rather than supplying the whole ramp,
    which is what it was doing when tracking error reached 80 C.

    Falls back to a flat estimate when no measured curves are supplied, but
    that fallback is only good for getting a rig off the ground.
    """

    def __init__(self, table=None, heating_rates=None, cooling_rates=None,
                 ambient_c=22.0, full_power_rise_c=300.0):
        # Packed into array('f') rather than kept as lists of pairs. The
        # numbers are identical -- see tests/test_ratetable.py, which checks
        # agreement against the plain interpolation across the whole
        # measured span -- but a Python float is a heap object and a
        # two-element list is another, so sixty pairs cost about 7 kB of a
        # heap with 30 kB free. As arrays they cost a few hundred bytes.
        self.table = as_table(table)
        self.heating_rates = as_table(heating_rates)
        self.cooling_rates = as_table(cooling_rates)
        self.ambient_c = ambient_c
        self.full_power_rise_c = full_power_rise_c

    def duty_for(self, temp_c, rate_c_per_s=0.0):
        if self.heating_rates and self.cooling_rates:
            h = self.heating_rates.at(temp_c)
            c = self.cooling_rates.at(temp_c)
            span = h - c
            if span <= 0:
                return 1.0 if rate_c_per_s > 0 else 0.0
            return clamp((rate_c_per_s - c) / span, 0.0, 1.0)
        if self.table:
            return clamp(self.table.at(temp_c), 0.0, 1.0)
        rise = temp_c - self.ambient_c
        if rise <= 0:
            return 0.0
        return clamp(rise / self.full_power_rise_c, 0.0, 1.0)

    def achievable_rate(self, temp_c, duty=1.0):
        """Fastest rise this oven can produce at *temp_c*. Used to tell an
        operator up front that a profile is asking for more than exists."""
        if not (self.heating_rates and self.cooling_rates):
            return None
        h = self.heating_rates.at(temp_c)
        c = self.cooling_rates.at(temp_c)
        return c + duty * (h - c)


def _interp(table, x):
    if x <= table[0][0]:
        return table[0][1]
    if x >= table[-1][0]:
        return table[-1][1]
    for i in range(1, len(table)):
        if table[i][0] >= x:
            x0, y0 = table[i - 1]
            x1, y1 = table[i]
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return table[-1][1]


class PID(object):
    """Positional PID with derivative on measurement and anti-windup.

    ``update`` returns a correction to add to the feed-forward duty, so it is
    free to go negative.
    """

    def __init__(self, kp=0.02, ki=0.0008, kd=0.4,
                 out_min=-1.0, out_max=1.0, i_min=-0.5, i_max=0.5,
                 derivative_window_s=3.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_min = out_min
        self.out_max = out_max
        self.i_min = i_min
        self.i_max = i_max
        # The derivative is taken across this much history rather than
        # between adjacent samples. At a 4 Hz cadence with a thermocouple
        # quantised to 0.0625 C, one quantisation step between neighbours
        # reads as 0.25 C/s of slope that is not there; with kd=0.5 that is a
        # 0.125 swing in commanded duty out of pure noise, and a 0.5 C jump
        # saturates the term. Measured on hardware, it turned a smooth demand
        # into duty hopping between 0.0 and 1.0 several times a second and
        # cost roughly three times the expected relay actuations.
        self.derivative_window_s = derivative_window_s
        self.reset()

    def reset(self):
        self._i = 0.0
        self._last_meas = None
        self._last_t = None
        self._history = []

    def update(self, t, setpoint, measured):
        err = setpoint - measured
        p = self.kp * err

        self._history.append((t, measured))
        cutoff = t - self.derivative_window_s * 2
        while len(self._history) > 2 and self._history[0][0] < cutoff:
            self._history.pop(0)

        d = 0.0
        i_candidate = self._i
        if self._last_t is not None:
            dt = t - self._last_t
            if dt > 0:
                i_candidate = self._i + self.ki * err * dt
                # Derivative on measurement, negated: it opposes movement, and
                # a setpoint step cannot spike it. Taken across the window so
                # sensor quantisation does not masquerade as slope.
                span = self._slope(t)
                if span is not None:
                    d = -self.kd * span

        out = p + i_candidate + d
        # Anti-windup: only let the integral accumulate if doing so does not
        # push an already-saturated output further into the rail.
        if self.out_min < out < self.out_max:
            self._i = clamp(i_candidate, self.i_min, self.i_max)
        else:
            keep = clamp(i_candidate, self.i_min, self.i_max)
            if (out >= self.out_max and keep < self._i) or \
               (out <= self.out_min and keep > self._i):
                self._i = keep     # unwinding is always allowed

        self._last_meas = measured
        self._last_t = t
        return clamp(p + self._i + d, self.out_min, self.out_max)

    def _slope(self, now):
        """Rate of change of the measurement over the derivative window."""
        oldest = None
        for ts, value in self._history:
            if now - ts <= self.derivative_window_s:
                oldest = (ts, value)
                break
        if oldest is None or len(self._history) < 2:
            return None
        t1, v1 = self._history[-1]
        t0, v0 = oldest
        if t1 - t0 < self.derivative_window_s * 0.5:
            return None            # not enough history yet to trust a slope
        return (v1 - v0) / (t1 - t0)


class TimeProportional(object):
    """Turns a 0-1 duty request into relay states over a fixed window.

    Minimum dwell times keep a mechanical relay from chattering. When the
    requested duty leaves less than ``min_off_s`` of off-time, the window is
    held fully on instead of dropping out briefly — which is why a run
    actuates the relay on the order of tens of times rather than once per
    window.
    """

    def __init__(self, window_s=4.0, min_on_s=0.8, min_off_s=0.8):
        self.window_s = window_s
        self.min_on_s = min_on_s
        self.min_off_s = min_off_s
        self._window_start = None
        self._on_time = 0.0
        self.actuations = 0
        self._state = False

    def reset(self, t=None):
        self._window_start = t
        self._on_time = 0.0
        self.actuations = 0
        self._state = False

    def update(self, t, duty):
        """Return the relay state for time *t* given the requested *duty*."""
        duty = clamp(duty, 0.0, 1.0)
        if self._window_start is None:
            self._window_start = t

        elapsed = t - self._window_start
        if elapsed >= self.window_s:
            self._window_start = t
            elapsed = 0.0
            self._on_time = self._quantise(duty)

        if elapsed == 0.0 and self._on_time == 0.0:
            self._on_time = self._quantise(duty)

        want = elapsed < self._on_time
        if want != self._state:
            if want:
                self.actuations += 1
            self._state = want
        return want

    def _quantise(self, duty):
        on = duty * self.window_s
        if on < self.min_on_s:
            return 0.0
        if self.window_s - on < self.min_off_s:
            return self.window_s     # hold on through the window
        return on


def predict_peak(temp_c, rate_c_per_s, coast_tau_s):
    """Where the oven settles if heat is removed at this instant.

    With heat already in transit between element and probe, cutting power does
    not stop the rise; it decays over the transport lag. Integrating that decay
    gives an overshoot proportional to the current rate, with ``coast_tau_s``
    as the constant of proportionality.

    ``coast_tau_s`` has the dimensions of the transport lag and must be
    measured on the actual oven by a step test (E2). There is deliberately no
    default: a wrong value here either bakes the board or leaves the joints
    unformed, and a plausible-looking constant would hide that nobody has
    measured it.
    """
    if rate_c_per_s <= 0:
        return temp_c
    return temp_c + rate_c_per_s * coast_tau_s


class Controller(object):
    """Feed-forward plus PID, with a predictive cutoff near the peak."""

    def __init__(self, profile, coast_tau_s, feed_forward=None, pid=None,
                 tpo=None, peak_guard_c=0.0):
        if coast_tau_s is None:
            raise ValueError(
                "coast_tau_s must be measured for this oven (experiment E2); "
                "there is no safe default")
        self.profile = profile
        self.ff = feed_forward or FeedForward()
        self.pid = pid or PID()
        # One switching window for every profile, deliberately.
        #
        # A long bake is where the relay wear is: simulation puts a 125 C MSL
        # bake at ~1080 actuations against ~35 for a reflow run, so a relay
        # good for 100k cycles is worth roughly 90 bakes. Widening the window
        # for bakes cuts that hard -- 30 s gives 136 actuations -- but the
        # oven climbs at over a degree a second, so a 30 s slug of heat
        # overshoots the setpoint by 35 C and the loop cannot correct inside
        # its own window. The trade is smooth, with no knee: 8 s still costs
        # 4.7 C. An MSL bake exists to hold 125 C within a few degrees, and
        # trading that for relay life is the wrong way round.
        self.tpo = tpo or TimeProportional()
        self.coast_tau_s = coast_tau_s
        self.peak_guard_c = peak_guard_c
        self.peak_c = profile.peak[1]
        self._last_temp = None
        self._last_t = None
        self.rate_c_per_s = 0.0
        self.coasting = False

    def reset(self, t=0.0):
        self.pid.reset()
        self.tpo.reset(t)
        self._last_temp = None
        self._last_t = None
        self.rate_c_per_s = 0.0
        self.coasting = False

    def duty_for(self, elapsed_s, temp_c, t=None):
        """The duty to request now. Does not touch the relay."""
        t = elapsed_s if t is None else t

        if self._last_t is not None and t > self._last_t:
            dt = t - self._last_t
            self.rate_c_per_s = (temp_c - self._last_temp) / dt
        self._last_t = t
        self._last_temp = temp_c

        target = self.profile.target_at(elapsed_s)

        # Once the predicted landing point reaches the peak, stop. Latching
        # matters: letting it re-engage would put more heat in flight, which
        # is the mistake this exists to prevent.
        if not self.coasting and elapsed_s <= self.profile.peak[0]:
            landing = predict_peak(temp_c, self.rate_c_per_s, self.coast_tau_s)
            if landing >= self.peak_c - self.peak_guard_c:
                self.coasting = True
        if self.coasting:
            # Release as soon as the oven falls below what is being asked for.
            # The earlier condition also required the target to be well below
            # the peak, which silently broke any profile that HOLDS at peak to
            # earn time above liquidus: the cutoff latched on arrival and
            # coasted down through the whole dwell.
            if temp_c < target - 1.0:
                self.coasting = False
                self.pid.reset()
            else:
                return 0.0

        slope = self.profile.slope_at(elapsed_s)
        return clamp(self.ff.duty_for(target, slope)
                     + self.pid.update(t, target, temp_c), 0.0, 1.0)

    def relay_state(self, t, duty):
        return self.tpo.update(t, duty)
