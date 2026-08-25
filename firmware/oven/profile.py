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

CATEGORY_REFLOW = "reflow"
CATEGORY_BAKE = "bake"
CATEGORY_HOLD = "hold"
CATEGORIES = (CATEGORY_REFLOW, CATEGORY_BAKE, CATEGORY_HOLD)

# Refuse anything outside these no matter what a file claims.
ABS_MIN_C = 0.0
ABS_MAX_C = 300.0
MAX_DURATION_S = 24 * 3600


class ProfileError(Exception):
    """A profile could not be loaded, with a reason worth showing a user."""


class Profile(object):
    __slots__ = ("name", "alloy", "category", "liquidus_c", "reference",
                 "notes", "points", "max_ramp_up_c_per_s")

    def __init__(self, name, points, category=CATEGORY_REFLOW, alloy=None,
                 liquidus_c=None, reference=None, notes=None,
                 max_ramp_up_c_per_s=None):
        self.name = name
        self.points = points
        self.category = category
        self.alloy = alloy
        self.liquidus_c = liquidus_c
        self.reference = reference
        self.notes = notes
        # A paste datasheet's own ramp limit outranks any generic default.
        self.max_ramp_up_c_per_s = max_ramp_up_c_per_s

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
                max_ramp_up_c_per_s=d.get("max_ramp_up_c_per_s"))
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

    def warnings(self, max_ramp_up=None, max_ramp_down=None):
        """Non-fatal concerns, for showing before a run.

        With measured oven capability passed in, this reports demands the
        hardware has never met — the thing you would otherwise discover by
        ruining a board.
        """
        out = []
        if self.category == CATEGORY_REFLOW and self.liquidus_c is not None:
            peak = self.peak[1]
            margin = peak - self.liquidus_c
            if margin < 10:
                out.append(
                    "peak %g C is only %g C above liquidus %g C; joints may "
                    "not fully form" % (peak, margin, self.liquidus_c))
            if self.time_above(self.liquidus_c) < 30:
                out.append("less than 30 s above liquidus")
        if max_ramp_up is not None:
            need = self.max_ramp_up
            if need > max_ramp_up:
                out.append(
                    "profile asks for %.2f C/s rise; this oven has managed "
                    "%.2f C/s, so the peak may be undershot"
                    % (need, max_ramp_up))
        if max_ramp_down is not None:
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
