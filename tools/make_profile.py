#!/usr/bin/env python3
"""Build a profile's curve from this oven's measured behaviour.

Three of the shipped profiles say they are derived from
``data/oven-characterisation.json`` and none of them was, in any way a
machine could repeat. The points were worked out once, by hand, against a
characterisation that has since been measured twice more -- so "derived from
measurement" was a claim about how the numbers were arrived at, not a
property anything could check, and the curves could not be rebuilt when the
measurement improved.

This makes the derivation the artifact. A spec in ``data/profile-specs.json``
says what the profile is metallurgically -- soak here, peak there, this much
time above liquidus -- and the curve falls out of the measured rate tables.
Regenerate, and a better characterisation gives a better curve.

  python3 tools/make_profile.py --check          # do the shipped files match?
  python3 tools/make_profile.py --write          # regenerate them
  python3 tools/make_profile.py --write ts391snl

Segments, in the order they appear in a spec:

  {"ramp_to": 150}                climb at `fraction` of measured capability
  {"ramp_to": 180, "rate": 0.4}   climb at a fixed rate (refused if the oven
                                  does not have it)
  {"ramp_to": 90, "over_s": 60}   capability-SHAPED, then scaled to land at
                                  exactly that time -- for a datasheet point
                                  that must be hit
  {"hold_s": 20}                  stay
  {"line_to": 165, "at_s": 240}   a straight line to an absolute time, for
                                  the parts of a curve the manufacturer
                                  specifies and this oven can follow
  {"cool_to": 150}                fall at the measured door-shut rate
  {"cool_to": 138, "door": true}  fall with the door open

Nothing here talks to the oven and nothing here is imported by the firmware.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "firmware"))

CHARACTERISATION = os.path.join(ROOT, "data", "oven-characterisation.json")
SPECS = os.path.join(ROOT, "data", "profile-specs.json")
PROFILES = os.path.join(ROOT, "firmware", "profiles")

# The step the curve is integrated at. Small enough that the rate tables are
# effectively continuous, and nothing downstream sees it: points come out at
# `resolution_c`, not at this.
DT = 0.25

# The door, measured on run 0007 against a known open instant: 1-2 s to show
# at the probe, full effect by 3, and -8.31 C/s at the peak of it. 5.2 is the
# figure the firmware plans descents with, and using the same one here means
# a generated tail and the door prompt cannot disagree.
DOOR_C_PER_S = 5.2


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


class Oven(object):
    """The measured rate tables, and nothing else.

    Deliberately not the simulator from tests/sim: that one models the
    controller chasing a target, which is the wrong question here. A profile
    is a curve to aim at, and the only thing it needs from the oven is how
    fast the oven can move at each temperature.
    """

    def __init__(self, path=None):
        d = json.load(open(path or CHARACTERISATION))
        self.heat = sorted(d["heating_rate_c_per_s"])
        self.cool = sorted(d["cooling_rate_c_per_s"])
        self.ambient_c = d["ambient_c"]
        self.hottest_measured_c = max(t for t, _ in self.heat)
        self.coolest_cooling_c = min(t for t, _ in self.cool)

    def heating_rate(self, temp_c):
        return _interp(self.heat, temp_c)

    def cooling_rate(self, temp_c):
        return _interp(self.cool, temp_c)


class Curve(object):
    """Points accumulated as segments are applied."""

    def __init__(self, start_c, tolerance_c):
        self.t = 0.0
        self.c = float(start_c)
        self.tolerance_c = tolerance_c
        self.points = [(0.0, float(start_c))]
        self.warnings = []
        self._pending = []
        self.worst_chord_c = 0.0

    def _chord_error(self, t_end, c_end):
        """How far the straight line to (t_end, c_end) misses the real curve.

        The profile is stored as points and read back by linear interpolation,
        so the thing that matters is not how far apart the points are but how
        much the chord between two of them departs from the curve they came
        from. Spacing by temperature spends points evenly on a curve whose
        bends are not even: 5 C apart puts sixty-four points on TS391SNL,
        most of them down the straight parts, and pushes the file past the
        2560 bytes the oven's own upload route can take.
        """
        t0, c0 = self.points[-1]
        if t_end <= t0:
            return 0.0
        worst = 0.0
        for t, c in self._pending:
            frac = (t - t0) / (t_end - t0)
            worst = max(worst, abs(c - (c0 + frac * (c_end - c0))))
        return worst

    def _emit(self, force=False):
        last_t, last_c = self.points[-1]
        if self.t <= last_t:
            return
        if force:
            self.worst_chord_c = max(self.worst_chord_c,
                                     self._chord_error(self.t, self.c))
            self.points.append((self.t, self.c))
            self._pending = []
            return
        if self._chord_error(self.t, self.c) > self.tolerance_c:
            # The sample before this one is the last that stayed inside
            # tolerance, so that is the point to keep.
            if len(self._pending) >= 2:
                t_keep, c_keep = self._pending[-2]
                self.worst_chord_c = max(self.worst_chord_c,
                                         self._chord_error(t_keep, c_keep))
                self.points.append((t_keep, c_keep))
                self._pending = [p for p in self._pending if p[0] > t_keep]
        self._pending.append((self.t, self.c))

    def ramp_to(self, target_c, fraction, rate=None, over_s=None,
                oven=None, name=""):
        """Climb, shaped by what the oven can actually do at each degree.

        A straight line asks for the same rate at 240 C as at 60 C, and this
        oven has 0.63 there against 1.69 here. Shaping by the measured curve
        is the difference between a profile the controller follows with
        headroom and one it saturates against for the last thirty degrees.
        """
        if target_c <= self.c:
            raise ValueError("%s: ramp_to %g is not above %g"
                             % (name, target_c, self.c))
        if target_c > oven.hottest_measured_c:
            self.warnings.append(
                "%s: ramps to %g C, above the %g C the step tests reached"
                % (name, target_c, oven.hottest_measured_c))

        # Walk it once at the shape it wants, recording (dt, temp).
        steps = []
        c = self.c
        while c < target_c:
            if rate is not None:
                have = oven.heating_rate(c)
                if rate > have:
                    raise ValueError(
                        "%s: asks %.2f C/s at %.0f C and this oven has %.2f"
                        % (name, rate, c, have))
                r = rate
            else:
                r = oven.heating_rate(c) * fraction
            if r <= 0:
                raise ValueError("%s: no heating rate at %.0f C" % (name, c))
            step = min(DT * r, target_c - c)
            steps.append((step / r, c + step))
            c += step

        natural_s = sum(dt for dt, _ in steps)
        scale = 1.0
        if over_s is not None:
            if natural_s > over_s:
                raise ValueError(
                    "%s: reaching %g C takes %.0f s at %g of capability and "
                    "the spec allows %g" % (name, target_c, natural_s,
                                            fraction, over_s))
            scale = over_s / natural_s

        for dt, c in steps:
            self.t += dt * scale
            self.c = c
            self._emit()
        self._emit(force=True)

    def line_to(self, target_c, at_s, name=""):
        if at_s <= self.t:
            raise ValueError("%s: line_to %g s is not after %g"
                             % (name, at_s, self.t))
        self.t = float(at_s)
        self.c = float(target_c)
        self._emit(force=True)

    def hold(self, seconds):
        self.t += float(seconds)
        self._emit(force=True)

    def cool_to(self, target_c, door=False, oven=None, name=""):
        """Fall at the rate this oven actually falls at.

        A cooling tail is not a wish. Shut, the oven manages -0.13 C/s around
        liquidus for the low-temperature alloys, so a datasheet tail of
        -0.9 C/s describes a run with a person standing at it. Generating the
        tail from measurement is what makes cooling_assumes_open_door a
        derived fact rather than a flag someone has to remember to set.
        """
        if target_c >= self.c:
            raise ValueError("%s: cool_to %g is not below %g"
                             % (name, target_c, self.c))
        hottest = max(t for t, _ in oven.cool)
        if not door and self.c > hottest:
            self.warnings.append(
                "%s: cools from %.0f C and the cooling table stops at %g, so "
                "the top of the tail is the flat extrapolation, not a "
                "measurement" % (name, self.c, hottest))
        c = self.c
        while c > target_c:
            r = -DOOR_C_PER_S if door else oven.cooling_rate(c)
            if r >= 0:
                raise ValueError("%s: no cooling rate at %.0f C" % (name, c))
            step = min(DT * -r, c - target_c)
            self.t += step / -r
            c -= step
            self.c = c
            self._emit()
        self._emit(force=True)


def build(spec, oven):
    """Apply a spec's segments and return (points, warnings)."""
    name = spec["name"]
    curve = Curve(spec.get("start_c", round(oven.ambient_c)),
                  spec.get("tolerance_c", 1.0))
    fraction = spec.get("fraction", 0.8)
    for seg in spec["segments"]:
        if "ramp_to" in seg:
            curve.ramp_to(seg["ramp_to"], seg.get("fraction", fraction),
                          rate=seg.get("rate"), over_s=seg.get("over_s"),
                          oven=oven, name=name)
        elif "line_to" in seg:
            curve.line_to(seg["line_to"], seg["at_s"], name=name)
        elif "hold_s" in seg:
            curve.hold(seg["hold_s"])
        elif "cool_to" in seg:
            curve.cool_to(seg["cool_to"], door=seg.get("door", False),
                          oven=oven, name=name)
        else:
            raise ValueError("%s: unknown segment %r" % (name, seg))
    points = [[round(t, 1), round(c, 1)] for t, c in curve.points]
    return points, curve.warnings, curve.worst_chord_c


def describe(points, liquidus_c):
    """The numbers a person judging a curve wants, from the curve alone.

    These describe what the profile ASKS for. What the oven then does with it
    is a different question, answered by simulating the controller against it
    -- see tests/test_generated_profiles.py.
    """
    peak_c = max(c for _, c in points)
    peak_t = [t for t, c in points if c == peak_c][0]
    out = {"peak_c": peak_c, "time_to_peak_s": peak_t,
           "duration_s": points[-1][0]}

    up = down = 0.0
    for (t0, c0), (t1, c1) in zip(points, points[1:]):
        if t1 <= t0:
            continue
        r = (c1 - c0) / (t1 - t0)
        up = max(up, r)
        down = min(down, r)
    out["max_ramp_up_c_per_s"] = round(up, 2)
    out["max_ramp_down_c_per_s"] = round(down, 2)

    # J-STD-020 puts the Pb-free soak at 150-200 C for 60-120 s, and it is
    # the one part of a reflow curve that is easy to get wrong by accident:
    # it is not a segment anybody draws, it is however long the curve happens
    # to spend crossing that band.
    band = []
    for (t0, c0), (t1, c1) in zip(points, points[1:]):
        for edge in (150.0, 200.0):
            if (c0 < edge) != (c1 < edge) and c1 != c0:
                frac = (edge - c0) / (c1 - c0)
                band.append((t0 + frac * (t1 - t0), edge))
    ups = [t for t, e in band if e == 150.0][:1] + \
          [t for t, e in band if e == 200.0][:1]
    if peak_c > 200.0 and len(ups) == 2:
        out["soak_150_to_200_s"] = round(ups[1] - ups[0], 1)

    if liquidus_c:
        crossings = []
        for (t0, c0), (t1, c1) in zip(points, points[1:]):
            if (c0 < liquidus_c) != (c1 < liquidus_c) and c1 != c0:
                frac = (liquidus_c - c0) / (c1 - c0)
                crossings.append(t0 + frac * (t1 - t0))
        if len(crossings) >= 2:
            out["time_above_liquidus_s"] = round(crossings[-1] - crossings[0], 1)
        # Time within 5 C of peak: J-STD-020 caps it at 30 s, and a profile
        # that earns its time above liquidus by sitting at the top is exactly
        # how that gets exceeded without anyone noticing.
        near = []
        for (t0, c0), (t1, c1) in zip(points, points[1:]):
            lo = peak_c - 5.0
            if (c0 < lo) != (c1 < lo) and c1 != c0:
                frac = (lo - c0) / (c1 - c0)
                near.append(t0 + frac * (t1 - t0))
        if len(near) >= 2:
            out["time_within_5c_of_peak_s"] = round(near[-1] - near[0], 1)
    return out


def profile_from_spec(spec, oven):
    """The JSON the oven loads, built from the spec plus the curve."""
    points, warnings, chord = build(spec, oven)
    out = {}
    for key in ("name", "alloy", "category", "liquidus_c", "reference",
                "notes", "tal_min_s", "tal_max_s", "max_ramp_up_c_per_s",
                "default", "diagnostic", "peak_c"):
        if key in spec:
            out[key] = spec[key]

    # Derived, not declared. A curve that falls faster than this oven does
    # with the door shut needs a person, and whether it does is arithmetic.
    shut = min(oven.cooling_rate(c) for _, c in points)
    measured = describe(points, spec.get("liquidus_c"))
    needs_door = measured["max_ramp_down_c_per_s"] < shut - 0.05
    if needs_door:
        out["cooling_assumes_open_door"] = True

    measured["worst_chord_error_c"] = round(chord, 2)
    out["points"] = points
    return out, measured, warnings


def load_specs(path=None):
    return json.load(open(path or SPECS))


def render(profile):
    """One field and one point per line, matching tools/format_profile.py."""
    order = ("alloy", "category", "cooling_assumes_open_door", "default",
             "diagnostic", "liquidus_c", "max_ramp_up_c_per_s", "name",
             "notes", "peak_c", "reference", "tal_max_s", "tal_min_s")
    lines = ["{"]
    keys = [k for k in order if k in profile]
    for k in keys:
        lines.append("  %s: %s," % (json.dumps(k),
                                    json.dumps(profile[k], ensure_ascii=True)))
    lines.append('  "points": [')
    pts = profile["points"]
    for i, (t, c) in enumerate(pts):
        lines.append("    [%s, %s]%s" % (json.dumps(t), json.dumps(c),
                                         "" if i == len(pts) - 1 else ","))
    lines.append("  ]")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("names", nargs="*", help="specs to build (default: all)")
    ap.add_argument("--write", action="store_true",
                    help="write firmware/profiles/<name>.json")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if a shipped file is out of date")
    args = ap.parse_args(argv)

    oven = Oven()
    specs = load_specs()
    names = args.names or sorted(specs)
    stale = []
    for name in names:
        if name not in specs:
            print("!! no spec named %r; have %s"
                  % (name, ", ".join(sorted(specs))))
            return 2
        profile, measured, warnings = profile_from_spec(specs[name], oven)
        text = render(profile)
        path = os.path.join(PROFILES, name + ".json")
        current = open(path).read() if os.path.exists(path) else None

        print("%-24s %d points, %d bytes" % (name, len(profile["points"]),
                                             len(text)))
        for k in sorted(measured):
            print("    %-26s %s" % (k, measured[k]))
        for w in warnings:
            print("    !! %s" % w)
        if len(text) > 2560:
            print("    !! %d bytes: too big for the oven's own upload route"
                  % len(text))

        if args.write:
            open(path, "w").write(text)
            print("    written to %s" % os.path.relpath(path, ROOT))
        elif current != text:
            stale.append(name)
            print("    OUT OF DATE against the spec")

    if args.check and stale:
        print("\n!! %s do not match their specs. Run with --write."
              % ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
