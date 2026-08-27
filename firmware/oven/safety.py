# SPDX-License-Identifier: MIT
"""Safety supervision.

The supervisor is the only thing permitted to say yes to heat. The controller
proposes; this decides. It is deliberately separate from the controller so it
can be reasoned about, and tested, on its own.

Three principles shape it.

**Fail closed.** Anything the supervisor cannot make sense of — a missing
reading, a sensor fault flag, a gap in time — denies heat. There is no state in
which "I don't know" allows the relay on.

**Latch.** A tripped fault stays tripped until a person acknowledges it.
Faults that clear themselves hide the thing that caused them.

**Watch the direction that hurts.** A thermocouple failing *low* makes the
control error larger and asks for more heat. Validation therefore runs before
the controller sees a reading, not after.
"""

from . import hal

# Fault codes.
FAULT_NONE = 0
FAULT_OVER_TEMP = 1
FAULT_RATE = 2
FAULT_SENSOR = 3
FAULT_SENSOR_STALE = 4
FAULT_SENSOR_FROZEN = 5
FAULT_STALL = 6
FAULT_ENCLOSURE = 7
FAULT_RUN_TIMEOUT = 8
FAULT_IMPLAUSIBLE_START = 9
FAULT_CPU_HOT = 10

_FAULT_TEXT = {
    FAULT_OVER_TEMP: "over temperature",
    FAULT_RATE: "temperature rising too fast",
    FAULT_SENSOR: "thermocouple fault",
    FAULT_SENSOR_STALE: "no sensor reading",
    FAULT_SENSOR_FROZEN: "sensor reading not changing",
    FAULT_STALL: "heating but temperature not rising",
    FAULT_ENCLOSURE: "electronics enclosure too hot",
    FAULT_RUN_TIMEOUT: "run exceeded its time limit",
    FAULT_IMPLAUSIBLE_START: "starting temperature implausible",
    FAULT_CPU_HOT: "controller too hot",
}


class Limits(object):
    """Bounds the supervisor enforces. Values are defaults; see config."""

    __slots__ = ("max_temp_c", "max_rate_c_per_s", "max_enclosure_c",
                 "stall_window_s", "stall_min_rise_c", "max_run_s",
                 "sensor_stale_s", "sensor_frozen_s", "start_min_c",
                 "start_max_c", "rate_window_s", "max_cpu_c")

    def __init__(self, max_temp_c=260.0, max_rate_c_per_s=4.0,
                 max_enclosure_c=70.0, stall_window_s=90.0,
                 stall_min_rise_c=2.0, max_run_s=3600.0,
                 sensor_stale_s=3.0, sensor_frozen_s=30.0,
                 start_min_c=5.0, start_max_c=60.0,
                 rate_window_s=3.0, max_cpu_c=80.0):
        self.max_temp_c = max_temp_c
        self.max_rate_c_per_s = max_rate_c_per_s
        self.max_enclosure_c = max_enclosure_c
        self.stall_window_s = stall_window_s
        self.stall_min_rise_c = stall_min_rise_c
        self.max_run_s = max_run_s
        self.sensor_stale_s = sensor_stale_s
        self.sensor_frozen_s = sensor_frozen_s
        self.start_min_c = start_min_c
        self.start_max_c = start_max_c
        # max_enclosure_c is set from what the electronics tolerate, not from
        # the enclosure material: the printed parts sit away from the oven and
        # are reached by thermally protected wiring, so softening is not the
        # constraint. The binding part is the TFT, typically rated to 70 °C
        # operating; the SAMD51 is good to 85 °C and the MCP9600 to 125 °C.
        # 60 °C was too tight to run back to back -- the enclosure rises about
        # 21 °C per run and peaks after it, so a second run had to wait.
        #
        # Rate is measured across this window, not between adjacent samples.
        # At 4 Hz on a probe quantised to 0.0625 C, ordinary noise shows up as
        # 8-11 C/s between neighbours on an oven whose real maximum is
        # 1.85 C/s -- so a neighbour-to-neighbour limit is certain to trip on
        # nothing at all. It did, mid-run, on the bench.
        self.rate_window_s = rate_window_s
        # The SAMD51 is rated to 85 °C. Measured, its die does not move during
        # a run -- the cold junction rises 12-15 °C while this stays flat --
        # so tripping here would mean something genuinely unlike any run so
        # far, which is exactly what a guard is for.
        self.max_cpu_c = max_cpu_c


class Fault(object):
    __slots__ = ("code", "detail", "t")

    def __init__(self, code, detail="", t=None):
        self.code = code
        self.detail = detail
        self.t = t

    @property
    def message(self):
        base = _FAULT_TEXT.get(self.code, "unknown fault")
        return "%s: %s" % (base, self.detail) if self.detail else base

    def __repr__(self):
        return "Fault(%s)" % self.message


class Supervisor(object):
    """Gates the relay. Call :meth:`update` every control step."""

    def __init__(self, limits=None):
        self.limits = limits or Limits()
        self.fault = None
        self._run_start = None
        self._last_t = None
        self._last_temp = None
        self._relay_on_since = None
        self._temp_at_relay_on = None
        self._frozen_since = None
        self._frozen_value = None
        self._rate_history = []

    # -- state -------------------------------------------------------------

    @property
    def tripped(self):
        return self.fault is not None

    def allow_heat(self):
        """The only authority for energising the relay."""
        return self.fault is None

    def acknowledge(self):
        """Clear a latched fault. Requires a deliberate act by a person."""
        self.fault = None
        self._reset_tracking()

    def _reset_tracking(self):
        self._last_t = None
        self._last_temp = None
        self._relay_on_since = None
        self._temp_at_relay_on = None
        self._frozen_since = None
        self._frozen_value = None
        self._rate_history = []

    def _trip(self, code, detail, t):
        if self.fault is None:            # keep the first cause, not the last
            self.fault = Fault(code, detail, t)
        return self.fault

    # -- run lifecycle -----------------------------------------------------

    def check_start(self, reading):
        """Pre-flight check. Returns a Fault, or None if it is safe to begin.

        Does not latch: refusing to start is not the same as tripping mid-run,
        and the operator may simply need to wait for the oven to cool.
        """
        if reading is None or reading.hot is None:
            return Fault(FAULT_SENSOR_STALE, "no reading before start")
        if reading.faults:
            return Fault(FAULT_SENSOR,
                         ", ".join(hal.describe_faults(reading.faults)))
        lim = self.limits
        if not (lim.start_min_c <= reading.hot <= lim.start_max_c):
            return Fault(
                FAULT_IMPLAUSIBLE_START,
                "%.1f \u00b0C is outside the %.0f-%.0f \u00b0C band expected "
                "before a run"
                % (reading.hot, lim.start_min_c, lim.start_max_c))
        return None

    def begin_run(self, t):
        self._run_start = t
        self._reset_tracking()

    def end_run(self):
        self._run_start = None
        self._reset_tracking()

    # -- the per-step check ------------------------------------------------

    def _windowed_rate(self, now, window_s):
        """Rate of rise across the window, or None until there is enough
        history to mean anything."""
        oldest = None
        for ts, value in self._rate_history:
            if now - ts <= window_s:
                oldest = (ts, value)
                break
        if oldest is None or len(self._rate_history) < 2:
            return None
        t1, v1 = self._rate_history[-1]
        t0, v0 = oldest
        if t1 - t0 < window_s * 0.5:
            return None
        return (v1 - v0) / (t1 - t0)

    def update(self, t, reading, relay_on):
        """Evaluate one control step. Returns the active Fault, or None.

        *relay_on* is what the relay was actually doing over the step just
        ended, not what is being requested for the next one.
        """
        if self.fault is not None:
            return self.fault

        lim = self.limits

        # No reading at all, or one the driver flagged: refuse immediately.
        if reading is None or reading.hot is None:
            return self._trip(FAULT_SENSOR_STALE, "sensor returned nothing", t)
        if reading.faults:
            return self._trip(
                FAULT_SENSOR,
                ", ".join(hal.describe_faults(reading.faults)), t)

        temp = reading.hot

        # Absolute ceiling. Checked first: it is the one that matters most.
        if temp >= lim.max_temp_c:
            return self._trip(FAULT_OVER_TEMP,
                              "%.1f \u00b0C reached the %.1f \u00b0C limit"
                              % (temp, lim.max_temp_c), t)

        # The enclosure holds the electronics and sits beside the oven.
        if reading.cold is not None and reading.cold >= lim.max_enclosure_c:
            return self._trip(FAULT_ENCLOSURE,
                              "%.1f \u00b0C inside the enclosure, limit %.1f \u00b0C"
                              % (reading.cold, lim.max_enclosure_c), t)

        if reading.cpu is not None and reading.cpu >= lim.max_cpu_c:
            return self._trip(FAULT_CPU_HOT,
                              "%.1f \u00b0C on the controller die, limit "
                              "%.1f \u00b0C" % (reading.cpu, lim.max_cpu_c), t)

        if self._run_start is not None and t - self._run_start > lim.max_run_s:
            return self._trip(FAULT_RUN_TIMEOUT,
                              "%.0f s elapsed, limit %.0f s"
                              % (t - self._run_start, lim.max_run_s), t)

        if self._last_t is not None:
            dt = t - self._last_t

            # A gap in the control cadence means we were not watching.
            #
            # Two cases, and the second was missed at first. If the relay was
            # on through the gap, that is plainly not a step anyone can vouch
            # for. But a gap DURING A RUN is not harmless just because the
            # relay happened to be off at that instant: the profile clock
            # advanced without supervision, so the controller resumes against
            # a timeline that no longer describes the oven and commands heat
            # to catch up. Found by writing a test for a blocking network
            # call -- the exact thing the WiFi stack will introduce.
            in_run = self._run_start is not None
            if dt > lim.sensor_stale_s and (relay_on or in_run):
                return self._trip(
                    FAULT_SENSOR_STALE,
                    "%.1f s without a check %s" % (
                        dt, "while heating" if relay_on else "during a run"), t)

        self._rate_history.append((t, temp))
        cutoff = t - lim.rate_window_s * 2
        while len(self._rate_history) > 2 and self._rate_history[0][0] < cutoff:
            self._rate_history.pop(0)
        rate = self._windowed_rate(t, lim.rate_window_s)
        if rate is not None and rate > lim.max_rate_c_per_s:
            return self._trip(
                FAULT_RATE, "%.1f \u00b0C/s over %.0f s exceeds %.1f \u00b0C/s"
                % (rate, lim.rate_window_s, lim.max_rate_c_per_s), t)



        # A thermocouple reading the identical value for a long stretch while
        # heat is being applied is not measuring anything.
        if relay_on:
            if self._frozen_value is None or temp != self._frozen_value:
                self._frozen_value = temp
                self._frozen_since = t
            elif t - self._frozen_since > lim.sensor_frozen_s:
                return self._trip(
                    FAULT_SENSOR_FROZEN,
                    "%.2f \u00b0C unchanged for %.0f s while heating"
                    % (temp, t - self._frozen_since), t)
        else:
            self._frozen_value = None
            self._frozen_since = None

        # Heat going in with nothing coming out: element or probe failure.
        if relay_on:
            if self._relay_on_since is None:
                self._relay_on_since = t
                self._temp_at_relay_on = temp
            elif t - self._relay_on_since >= lim.stall_window_s:
                rise = temp - self._temp_at_relay_on
                if rise < lim.stall_min_rise_c:
                    return self._trip(
                        FAULT_STALL,
                        "%.1f \u00b0C rise over %.0f s of heating"
                        % (rise, t - self._relay_on_since), t)
                self._relay_on_since = t
                self._temp_at_relay_on = temp
        else:
            self._relay_on_since = None
            self._temp_at_relay_on = None

        self._last_t = t
        self._last_temp = temp
        return None
