# SPDX-License-Identifier: MIT
"""Reflow profiles: loading, validation, interpolation.

A profile is a list of ``[time_s, temperature_c]`` points plus metadata. The
shape is taken from the JSON format found in this project's history, with two
changes.

The recorded ``melting_point`` there was wrong for the alloy it named, and the
stage boundaries were built on that wrong number. So stages are **derived**
here rather than stored: given the liquidus, where the curve crosses it is a
fact about the curve, not something a file can contradict. Duplicated facts
disagree eventually.

Pure stdlib: runs on CircuitPython and under CPython for tests.
"""

import json
import os

CATEGORY_REFLOW = "reflow"
CATEGORY_BAKE = "bake"
CATEGORY_HOLD = "hold"
CATEGORIES = (CATEGORY_REFLOW, CATEGORY_BAKE, CATEGORY_HOLD)


# Refuse anything outside these no matter what a file claims.
ABS_MIN_C = 0.0
ABS_MAX_C = 300.0
MAX_DURATION_S = 24 * 3600


def _interp_rate(table, value):
    """Linear lookup into a measured (temperature, rate) table."""
    if not table:
        return None
    pts = sorted(table)
    if value <= pts[0][0]:
        return pts[0][1]
    if value >= pts[-1][0]:
        return pts[-1][1]
    for i in range(1, len(pts)):
        if pts[i][0] >= value:
            t0, r0 = pts[i - 1]
            t1, r1 = pts[i]
            return r0 + (r1 - r0) * (value - t0) / (t1 - t0)
    return pts[-1][1]


class ProfileError(Exception):
    """A profile could not be loaded, with a reason worth showing a user."""


class ProfileRef(object):
    """A profile that is known about but not loaded.

    Ten profiles cost 24 kB of a heap that has about 180 kB in total, and
    only one of them is ever in use. Measured on the device, that is more
    than the WiFi stack needs to exist at all, and it was being spent to
    keep nine profiles nobody had selected. A ref holds what the picker and
    the console need -- a name and where to find it -- and the points are
    read when the profile is actually chosen.
    """

    __slots__ = ("path", "name", "category", "is_default", "diagnostic")

    def __init__(self, path, name, category, is_default, diagnostic):
        self.path = path
        self.name = name
        self.category = category
        self.is_default = is_default
        self.diagnostic = diagnostic

    def load(self):
        """Read the whole profile. The caller keeps it; nothing is cached."""
        return Profile.load(self.path)

    def __repr__(self):
        return "ProfileRef(%s)" % self.name


def scan(directory, on_warning=None):
    """List the profiles in *directory* without keeping any of them.

    Each file is parsed and validated so a broken profile is reported at
    boot rather than when someone selects it, but only the name and a
    couple of flags survive the call.
    """
    warn = on_warning or (lambda msg: print("# WARNING %s" % msg))
    try:
        names = [n for n in os.listdir(directory) if n.endswith(".json")]
    except OSError as e:
        warn("cannot list %s (%r): no profiles available" % (directory, e))
        return []
    refs = []
    for name in sorted(names):
        path = directory + "/" + name
        try:
            profile = Profile.load(path)
        except Exception as e:
            warn("profile %s rejected: %s" % (name, e))
            continue
        refs.append(ProfileRef(path, profile.name, profile.category,
                               profile.is_default, profile.diagnostic))
        profile = None
    return refs


def for_operators(refs):
    """The profiles a person choosing at the oven should be offered.

    DIAGNOSTIC exists to exercise the firmware and melts nothing. Leaving
    it in the cycle means the button someone presses to find their paste
    steps through a profile that solders no boards, and -- worse -- one
    that could be selected and run by mistake on a real assembly. It stays
    reachable from the console, which is where it is used from.
    """
    return [r for r in refs if not r.diagnostic]


class Profile(object):
    __slots__ = ("name", "alloy", "category", "liquidus_c", "reference",
                 "notes", "points", "max_ramp_up_c_per_s", "is_default",
                 "tal_min_s", "tal_max_s", "cooling_assumes_open_door",
                 "diagnostic")

    def __init__(self, name, points, category=CATEGORY_REFLOW, alloy=None,
                 liquidus_c=None, reference=None, notes=None,
                 max_ramp_up_c_per_s=None, is_default=False,
                 tal_min_s=None, tal_max_s=None,
                 cooling_assumes_open_door=False, diagnostic=False):
        self.name = name
        self.points = points
        self.category = category
        self.alloy = alloy
        self.liquidus_c = liquidus_c
        self.reference = reference
        self.notes = notes
        # A paste datasheet's own ramp limit outranks any generic default.
        self.max_ramp_up_c_per_s = max_ramp_up_c_per_s
        # A profile may nominate itself as the one to offer first.
        self.is_default = bool(is_default)
        # J-STD-020's 60-150 s window is written for SAC305. SnBi wants
        # 60-90 s: its liquidus is 138 C, so on an oven that cools slowly the
        # tail above liquidus is set by the cooldown rather than the profile,
        # and too long promotes brittle intermetallic growth.
        self.tal_min_s = tal_min_s
        self.tal_max_s = tal_max_s
        # A profile may declare that its cooling tail assumes the door is
        # opened. Judging such a tail against passive shut-door cooling
        # reports a failure the operator is meant to prevent by acting, which
        # trains people to ignore the warning.
        self.cooling_assumes_open_door = bool(cooling_assumes_open_door)
        # A diagnostic profile exercises the machine, not solder. Alloy
        # warnings about margin above liquidus are meaningless for it, and
        # leaving them on teaches people to dismiss warnings that matter.
        self.diagnostic = bool(diagnostic)

    # -- construction ------------------------------------------------------

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict):
            raise ProfileError("profile must be a JSON object")
        try:
            name = d["name"]
            raw = d["points"]
        except KeyError as e:
            raise ProfileError("profile is missing required field %s" % e)

        points = []
        for i, pt in enumerate(raw):
            if not isinstance(pt, (list, tuple)) or len(pt) != 2:
                raise ProfileError(
                    "point %d must be [time_s, temperature_c]" % i)
            try:
                points.append((float(pt[0]), float(pt[1])))
            except (TypeError, ValueError):
                raise ProfileError("point %d has non-numeric values" % i)

        category = d.get("category", CATEGORY_REFLOW)
        if category not in CATEGORIES:
            raise ProfileError(
                "unknown category %r (expected one of %s)"
                % (category, ", ".join(CATEGORIES)))

        p = cls(name=name, points=points, category=category,
                alloy=d.get("alloy"), liquidus_c=d.get("liquidus_c"),
                reference=d.get("reference"), notes=d.get("notes"),
                max_ramp_up_c_per_s=d.get("max_ramp_up_c_per_s"),
                is_default=d.get("default", False),
                tal_min_s=d.get("tal_min_s"), tal_max_s=d.get("tal_max_s"),
                cooling_assumes_open_door=d.get("cooling_assumes_open_door",
                                                False),
                diagnostic=d.get("diagnostic", False))
        p.validate()
        return p

    @classmethod
    def load(cls, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except ValueError as e:
            raise ProfileError("%s is not valid JSON: %s" % (path, e))
        except OSError as e:
            raise ProfileError("cannot read %s: %s" % (path, e))
        return cls.from_dict(data)

    # -- validation --------------------------------------------------------

    def validate(self):
        """Raise ProfileError if the profile is unusable.

        Deliberately strict. A profile that reaches the control loop has
        already been trusted with a heating element.
        """
        pts = self.points
        if len(pts) < 2:
            raise ProfileError("profile needs at least two points")
        if pts[0][0] != 0:
            raise ProfileError("profile must start at t=0, starts at t=%g"
                               % pts[0][0])
        for i in range(1, len(pts)):
            if pts[i][0] <= pts[i - 1][0]:
                raise ProfileError(
                    "times must strictly increase: point %d is t=%g after "
                    "t=%g" % (i, pts[i][0], pts[i - 1][0]))
        for i, (t, c) in enumerate(pts):
            if not (ABS_MIN_C <= c <= ABS_MAX_C):
                raise ProfileError(
                    "point %d temperature %g C is outside the permitted "
                    "range %g-%g C" % (i, c, ABS_MIN_C, ABS_MAX_C))
        if self.duration > MAX_DURATION_S:
            raise ProfileError("profile is longer than the %d s maximum"
                               % MAX_DURATION_S)
        if self.category == CATEGORY_REFLOW and self.liquidus_c is None:
            raise ProfileError(
                "a reflow profile must declare liquidus_c; stages and time "
                "above liquidus cannot be derived without it")
        if self.liquidus_c is not None:
            if not (ABS_MIN_C <= self.liquidus_c <= ABS_MAX_C):
                raise ProfileError("liquidus_c %g C is out of range"
                                   % self.liquidus_c)

    def warnings(self, max_ramp_up=None, max_ramp_down=None,
                 heating_rates=None):
        """Non-fatal concerns, for showing before a run.

        With measured oven capability passed in, this reports demands the
        hardware has never met — the thing you would otherwise discover by
        ruining a board.
        """
        out = []
        if (self.category == CATEGORY_REFLOW and self.liquidus_c is not None
                and not self.diagnostic):
            peak = self.peak[1]
            margin = peak - self.liquidus_c
            if margin < 10:
                out.append(
                    "peak %g C is only %g C above liquidus %g C; joints may "
                    "not fully form" % (peak, margin, self.liquidus_c))
            tal = self.time_above(self.liquidus_c)
            lo = self.tal_min_s if self.tal_min_s is not None else 30
            hi = self.tal_max_s
            if tal < lo:
                out.append("only %.0f s above liquidus, wants at least %.0f"
                           % (tal, lo))
            if hi is not None and tal > hi:
                out.append("%.0f s above liquidus, more than the %.0f this "
                           "alloy wants" % (tal, hi))
        if heating_rates:
            # Per segment, against what the oven does AT THAT TEMPERATURE.
            # Comparing only against the oven's peak rate hides the case that
            # matters: this oven peaks at 1.85 C/s around 80 C but manages
            # 1.29 at 150 C and 0.75 at 220 C, and reflow profiles demand
            # their fastest rise exactly where it is weakest.
            worst = None
            for i in range(1, len(self.points)):
                t0, c0 = self.points[i - 1]
                t1, c1 = self.points[i]
                need = (c1 - c0) / (t1 - t0)
                if need <= 0:
                    continue
                have = _interp_rate(heating_rates, (c0 + c1) / 2.0)
                if have is not None and need > have:
                    gap = need - have
                    if worst is None or gap > worst[0]:
                        worst = (gap, c0, c1, need, have)
            if worst is not None:
                out.append(
                    "%.0f-%.0f C needs %.2f C/s but this oven does %.2f C/s "
                    "there" % (worst[1], worst[2], worst[3], worst[4]))

        if max_ramp_up is not None:
            need = self.max_ramp_up
            if need > max_ramp_up:
                out.append(
                    "profile asks for %.2f C/s rise; this oven has managed "
                    "%.2f C/s, so the peak may be undershot"
                    % (need, max_ramp_up))
        if max_ramp_down is not None and not self.cooling_assumes_open_door:
            need = -self.max_ramp_down
            if need > max_ramp_down:
                out.append(
                    "profile asks for %.2f C/s fall; this oven has managed "
                    "%.2f C/s, so cooling will lag the profile"
                    % (need, max_ramp_down))
        return out

    # -- queries -----------------------------------------------------------

    @property
    def duration(self):
        return self.points[-1][0]

    @property
    def peak(self):
        """(time, temperature) of the hottest point."""
        return max(self.points, key=lambda p: p[1])

    def entry_time_for(self, temp_c, max_skip_fraction=0.5):
        """Where in the profile an oven already at *temp_c* should start.

        A run that begins warm and starts the clock at zero opens with the
        target below the oven, so the controller correctly withholds heat
        while the profile burns through a ramp the oven has already done.

        This is NOT fixing an observed failure. Two back-to-back SAC305 runs
        from about 50 C both landed inside their J-STD windows -- 236.7 C
        with 103 s above liquidus, and 236.9 C with 100 s -- and simulation
        across starting temperatures from 25 to 80 C passes either way. An
        earlier note here claimed otherwise; it was written from a run that
        was still in progress when it was measured.

        What this does buy is a warm run that takes less time, and a target
        that means something from the first second rather than after the
        profile catches up. In simulation it also lengthens time above
        liquidus slightly, 86 s to 92-98 s. It has not yet been run on
        hardware.

        So the clock starts where the profile has already been satisfied:
        the first point on the RISING part of the curve that is at least as
        hot as the oven. Only the rising part -- matching a temperature on
        the way back down would skip the peak entirely.

        The skip is capped at *max_skip_fraction* of the profile. Beyond
        that the oven is not "a little warm", it is still hot from the last
        run, and quietly running a fraction of a profile would be its own
        kind of wrong. The caller decides what to do about that.
        """
        pts = self.points
        peak_index = 0
        for i in range(len(pts)):
            if pts[i][1] > pts[peak_index][1]:
                peak_index = i
        if temp_c is None or temp_c <= pts[0][1]:
            return 0.0

        limit = self.duration * max_skip_fraction
        previous_t, previous_v = pts[0]
        for i in range(1, peak_index + 1):
            t, v = pts[i]
            if v >= temp_c:
                if v == previous_v:
                    found = t
                else:
                    span = v - previous_v
                    found = previous_t + (t - previous_t) * \
                        (temp_c - previous_v) / span
                return found if found <= limit else limit
            previous_t, previous_v = t, v
        return limit

    def target_at(self, t):
        """Linearly interpolated target temperature at time *t* seconds.

        Clamped at both ends: before the start holds the first temperature,
        after the end holds the last.
        """
        pts = self.points
        if t <= pts[0][0]:
            return pts[0][1]
        if t >= pts[-1][0]:
            return pts[-1][1]
        lo = 0
        hi = len(pts) - 1
        while hi - lo > 1:                      # binary search the segment
            mid = (lo + hi) // 2
            if pts[mid][0] <= t:
                lo = mid
            else:
                hi = mid
        t0, c0 = pts[lo]
        t1, c1 = pts[hi]
        return c0 + (c1 - c0) * (t - t0) / (t1 - t0)

    def slope_at(self, t):
        """Commanded rate of change in C/s at time *t*, for feed-forward."""
        pts = self.points
        if t < pts[0][0] or t >= pts[-1][0]:
            return 0.0
        lo = 0
        hi = len(pts) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if pts[mid][0] <= t:
                lo = mid
            else:
                hi = mid
        t0, c0 = pts[lo]
        t1, c1 = pts[hi]
        return (c1 - c0) / (t1 - t0)

    @property
    def max_ramp_up(self):
        return max(self._slopes()) if self._slopes() else 0.0

    @property
    def max_ramp_down(self):
        return min(self._slopes()) if self._slopes() else 0.0

    def _slopes(self):
        pts = self.points
        return [(pts[i][1] - pts[i - 1][1]) / (pts[i][0] - pts[i - 1][0])
                for i in range(1, len(pts))]

    def time_above(self, threshold_c):
        """Seconds the profile spends at or above *threshold_c*.

        Interpolates the crossings rather than counting whole segments, so a
        threshold partway through a ramp gives the right answer.
        """
        pts = self.points
        total = 0.0
        for i in range(1, len(pts)):
            t0, c0 = pts[i - 1]
            t1, c1 = pts[i]
            a_above = c0 >= threshold_c
            b_above = c1 >= threshold_c
            if a_above and b_above:
                total += t1 - t0
            elif a_above != b_above:
                frac = (threshold_c - c0) / (c1 - c0)
                cross = t0 + frac * (t1 - t0)
                total += (t1 - cross) if b_above else (cross - t0)
        return total

    @property
    def stages(self):
        """Derived stage boundaries as ``(name, t_start, t_end)``.

        Reflow profiles are split by where the curve crosses the liquidus and
        where it peaks. Nothing is read from the file, so a stage boundary
        cannot contradict the curve it describes.
        """
        if self.category != CATEGORY_REFLOW or self.liquidus_c is None:
            return [("hold", 0.0, self.duration)]
        peak_t = self.peak[0]
        up = self._crossing(self.liquidus_c, 0.0, peak_t, rising=True)
        down = self._crossing(self.liquidus_c, peak_t, self.duration,
                              rising=False)
        if up is None:
            return [("preheat", 0.0, peak_t), ("cool", peak_t, self.duration)]
        soak_end = up
        out = [("preheat", 0.0, soak_end * 0.5),
               ("soak", soak_end * 0.5, soak_end),
               ("reflow", soak_end, down if down is not None else self.duration)]
        if down is not None:
            out.append(("cool", down, self.duration))
        return out

    def _crossing(self, level, t_from, t_to, rising):
        pts = self.points
        for i in range(1, len(pts)):
            t0, c0 = pts[i - 1]
            t1, c1 = pts[i]
            if t1 < t_from or t0 > t_to:
                continue
            if rising and c0 < level <= c1:
                return t0 + (level - c0) / (c1 - c0) * (t1 - t0)
            if not rising and c0 >= level > c1:
                return t0 + (level - c0) / (c1 - c0) * (t1 - t0)
        return None

    def __repr__(self):
        return "Profile(%r, %d points, %gs, peak %gC)" % (
            self.name, len(self.points), self.duration, self.peak[1])
