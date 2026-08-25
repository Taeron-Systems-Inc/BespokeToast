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


def clamp(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)


class FeedForward(object):
    """Duty required to hold a temperature, in steady state.

    Constructed either from a measured table of ``(temperature, duty)`` pairs
    — which is what experiment E4 produces — or from a straight-line estimate
    until that measurement exists.
    """

    def __init__(self, table=None, ambient_c=22.0, full_power_rise_c=300.0):
        self.table = sorted(table) if table else None
        self.ambient_c = ambient_c
        self.full_power_rise_c = full_power_rise_c

    def duty_for(self, temp_c):
        if self.table:
            return self._interpolate(temp_c)
        # Losses rise roughly with the gap to ambient; holding a temperature
        # needs the duty that replaces exactly those losses.
        rise = temp_c - self.ambient_c
        if rise <= 0:
            return 0.0
        return clamp(rise / self.full_power_rise_c, 0.0, 1.0)

    def _interpolate(self, temp_c):
        tbl = self.table
        if temp_c <= tbl[0][0]:
            return tbl[0][1]
        if temp_c >= tbl[-1][0]:
            return tbl[-1][1]
        for i in range(1, len(tbl)):
            if tbl[i][0] >= temp_c:
                t0, d0 = tbl[i - 1]
                t1, d1 = tbl[i]
                return d0 + (d1 - d0) * (temp_c - t0) / (t1 - t0)
        return tbl[-1][1]


class PID(object):
    """Positional PID with derivative on measurement and anti-windup.

    ``update`` returns a correction to add to the feed-forward duty, so it is
    free to go negative.
    """

    def __init__(self, kp=0.02, ki=0.0008, kd=0.4,
                 out_min=-1.0, out_max=1.0, i_min=-0.5, i_max=0.5):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_min = out_min
        self.out_max = out_max
        self.i_min = i_min
        self.i_max = i_max
        self.reset()

    def reset(self):
        self._i = 0.0
        self._last_meas = None
        self._last_t = None

    def update(self, t, setpoint, measured):
        err = setpoint - measured
        p = self.kp * err

        d = 0.0
        i_candidate = self._i
        if self._last_t is not None:
            dt = t - self._last_t
            if dt > 0:
                i_candidate = self._i + self.ki * err * dt
                # derivative on measurement, negated: opposes movement,
                # and a setpoint step cannot spike it
                d = -self.kd * (measured - self._last_meas) / dt

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


class TimeProportional(object):
    """Turns a 0-1 duty request into relay states over a fixed window.

    Minimum dwell times keep a mechanical relay from chattering. When the
    requested duty leaves less than ``min_off_s`` of off-time, the window is
    held fully on instead of dropping out briefly — which is why a run
    actuates the relay on the order of tens of times rather than once per
    window.
    """

    def __init__(self, window_s=2.0, min_on_s=0.4, min_off_s=0.4):
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
            if target < self.peak_c - 5.0 and temp_c < target:
                self.coasting = False      # past the peak, back under control
            else:
                self.pid.reset()
                return 0.0

        return clamp(self.ff.duty_for(target) + self.pid.update(t, target, temp_c),
                     0.0, 1.0)

    def relay_state(self, t, duty):
        return self.tpo.update(t, duty)
