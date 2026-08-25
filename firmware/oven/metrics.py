# SPDX-License-Identifier: MIT
"""What actually happened during a run.

The previous firmware kept no record of any run it ever performed. These are
the numbers that decide whether the joints are sound, computed as the run
proceeds so they can also be shown live: time above liquidus is the one an
operator wants on screen while it is still possible to do something about it.

Limits follow J-STD-020 for lead-free assembly. They are defaults, not
gospel — a paste datasheet overrides them.
"""


class Limits(object):
    __slots__ = ("max_ramp_up_c_per_s", "max_ramp_down_c_per_s",
                 "tal_min_s", "tal_max_s", "peak_min_c", "peak_max_c",
                 "max_time_to_peak_s")

    def __init__(self, max_ramp_up_c_per_s=3.0, max_ramp_down_c_per_s=6.0,
                 tal_min_s=60.0, tal_max_s=150.0, peak_min_c=235.0,
                 peak_max_c=250.0, max_time_to_peak_s=480.0):
        self.max_ramp_up_c_per_s = max_ramp_up_c_per_s
        self.max_ramp_down_c_per_s = max_ramp_down_c_per_s
        self.tal_min_s = tal_min_s
        self.tal_max_s = tal_max_s
        self.peak_min_c = peak_min_c
        self.peak_max_c = peak_max_c
        self.max_time_to_peak_s = max_time_to_peak_s


    @classmethod
    def for_profile(cls, profile, peak_tolerance_c=10.0):
        """Judge a run against the profile it was asked to follow.

        A generic J-STD peak window is the wrong yardstick for a profile that
        deliberately peaks elsewhere: the datasheet curve for this paste tops
        out below the window, and marking every faithful run as a failure
        teaches operators to ignore the report. The absolute ramp limits stay
        as backstops, with the paste's own preheat limit preferred when it
        declares one.
        """
        peak = profile.peak[1]
        return cls(
            max_ramp_up_c_per_s=(profile.max_ramp_up_c_per_s or 3.0),
            peak_min_c=peak - peak_tolerance_c,
            peak_max_c=peak + peak_tolerance_c,
        )


class RunMetrics(object):
    """Accumulates a run sample by sample.

    Ramp rates are measured over a short window rather than between adjacent
    samples: at a 4 Hz cadence with 0.0625 C sensor resolution, consecutive
    differences are mostly quantisation noise, and a single step would read
    as 0.25 C/s out of nowhere.
    """

    def __init__(self, liquidus_c, rate_window_s=5.0):
        self.liquidus_c = liquidus_c
        self.rate_window_s = rate_window_s
        self.samples = []
        self.peak_c = None
        self.peak_t = None
        self.time_above_liquidus = 0.0
        self.max_ramp_up = 0.0
        self.max_ramp_down = 0.0
        self._last_t = None
        self._last_above = False

    def add(self, t, temp_c):
        if self.peak_c is None or temp_c > self.peak_c:
            self.peak_c = temp_c
            self.peak_t = t

        above = temp_c >= self.liquidus_c
        if self._last_t is not None:
            dt = t - self._last_t
            if above and self._last_above:
                self.time_above_liquidus += dt
            elif above != self._last_above and self.samples:
                # interpolate the crossing instead of counting a whole step
                t0, c0 = self.samples[-1]
                if c0 != temp_c:
                    frac = (self.liquidus_c - c0) / (temp_c - c0)
                    cross = t0 + frac * (t - t0)
                    self.time_above_liquidus += (t - cross) if above else 0.0

        self.samples.append((t, temp_c))
        self._trim()
        rate = self._windowed_rate()
        if rate is not None:
            if rate > self.max_ramp_up:
                self.max_ramp_up = rate
            if rate < self.max_ramp_down:
                self.max_ramp_down = rate

        self._last_t = t
        self._last_above = above

    def _trim(self):
        # keep only what the rate window needs, plus a little slack
        cutoff = self.samples[-1][0] - self.rate_window_s * 2
        while len(self.samples) > 4 and self.samples[0][0] < cutoff:
            self.samples.pop(0)

    def _windowed_rate(self):
        if len(self.samples) < 2:
            return None
        t1, c1 = self.samples[-1]
        for t0, c0 in self.samples:
            if t1 - t0 <= self.rate_window_s:
                if t1 - t0 <= 0:
                    return None
                return (c1 - c0) / (t1 - t0)
        return None

    def time_to_peak(self):
        return self.peak_t

    def check(self, limits=None):
        """Compare against the limits. Returns a list of
        ``(name, value, ok, text)`` so a report can show every line, not just
        the failures."""
        lim = limits or Limits()
        out = []

        def add(name, value, ok, text):
            out.append((name, value, ok, text))

        add("peak", self.peak_c,
            self.peak_c is not None
            and lim.peak_min_c <= self.peak_c <= lim.peak_max_c,
            "%.1f C (want %.0f-%.0f)" % (self.peak_c or 0,
                                         lim.peak_min_c, lim.peak_max_c))
        add("time above liquidus", self.time_above_liquidus,
            lim.tal_min_s <= self.time_above_liquidus <= lim.tal_max_s,
            "%.0f s (want %.0f-%.0f)" % (self.time_above_liquidus,
                                         lim.tal_min_s, lim.tal_max_s))
        add("max ramp up", self.max_ramp_up,
            self.max_ramp_up <= lim.max_ramp_up_c_per_s,
            "%.2f C/s (limit %.1f)" % (self.max_ramp_up,
                                       lim.max_ramp_up_c_per_s))
        add("max ramp down", self.max_ramp_down,
            -self.max_ramp_down <= lim.max_ramp_down_c_per_s,
            "%.2f C/s (limit %.1f)" % (self.max_ramp_down,
                                       lim.max_ramp_down_c_per_s))
        if self.peak_t is not None:
            add("time to peak", self.peak_t,
                self.peak_t <= lim.max_time_to_peak_s,
                "%.0f s (limit %.0f)" % (self.peak_t,
                                         lim.max_time_to_peak_s))
        return out

    def passed(self, limits=None):
        return all(ok for _, _, ok, _ in self.check(limits))
