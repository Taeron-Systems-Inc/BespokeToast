#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Recompute every tracking figure the documentation quotes.

    python3 tools/score_runs.py

Every number in docs/control-loop.md comes out of this, from files in this
repository, so a figure that has drifted from its data shows up as a
difference rather than as a sentence nobody can check. tests/test_scores.py
holds the documented values against it.

Two kinds of record, because they carry different things:

  data/plant-id/*.csv   console captures, 1 Hz, WITH the commanded duty.
                        Scored for tracking: rms and worst lag.
  data/*run-00*.csv     the oven's own run logs, ~4 Hz, no duty column but
                        with the relay state. Scored for the hold: rms,
                        mean, and relay closures per minute.

How the heating phase is scored, and why it is not simply "the whole run":

  * Only `running` rows count. Pre-charge drives the element with the
    profile clock held, so there is no target to be right or wrong about.
  * The leading samples that still carry the profile's t=0 target are
    dropped. On a hot start the entry offset lands a sample or two later,
    and until it does the run looks 30 C ahead of a curve it was never
    asked to follow. Two such samples were a third of the rms.
  * It ends at the peak. The cooling tail is the door's error, not the
    loop's, and on the profiles that need one the operator's reaction time
    is in it.
"""
import glob
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rows(path, ncols):
    out = []
    for line in open(path):
        if line.startswith("#") or line.startswith("elapsed"):
            continue
        p = line.strip().split(",")
        if len(p) < ncols or "" in p[:ncols]:
            continue
        out.append(p)
    return out


def heating(path):
    """(rms, worst_lag, precharge_s, entered_c) for a plant-id capture."""
    rows = [(float(p[0]), p[1], float(p[2]), float(p[3]))
            for p in _rows(path, 8)]
    run = [r for r in rows if r[1] == "running"]
    if not run:
        return None
    start = 0
    for i in range(1, min(6, len(run))):
        if run[i][3] - run[i - 1][3] > 2.0:
            start = i
    heat = run[start:]
    top = max(r[3] for r in heat)
    end = [n for n, r in enumerate(heat) if r[3] >= top - 1e-9][0]
    heat = heat[:end + 1]
    err = [r[2] - r[3] for r in heat]
    return (math.sqrt(sum(e * e for e in err) / len(err)), min(err),
            sum(1.0 for r in rows if r[1] == "precharge"), heat[0][2])


def hold(path):
    """(rms, mean, minutes, closures_per_min, peak) for a run log.

    The hold is every row at the profile's top target, which for a bake is
    the whole point of the run and for anything else is not interesting.
    """
    rows = [(float(p[0]), float(p[1]), float(p[2]), int(p[3]))
            for p in _rows(path, 6)]
    top = max(r[1] for r in rows)
    held = [r for r in rows if abs(r[1] - top) < 0.01]
    err = [r[2] - r[1] for r in held]
    minutes = (held[-1][0] - held[0][0]) / 60.0
    closures = sum(1 for a, b in zip(held, held[1:])
                   if a[3] == 0 and b[3] == 1)
    return (math.sqrt(sum(e * e for e in err) / len(err)),
            sum(err) / len(err), minutes,
            closures / minutes if minutes else 0.0,
            max(r[2] for r in rows))


def by_hour(path):
    rows = [(float(p[0]), float(p[1]), float(p[2])) for p in _rows(path, 6)]
    top = max(r[1] for r in rows)
    held = [r for r in rows if abs(r[1] - top) < 0.01]
    t0 = held[0][0]
    out = []
    for h in range(int((held[-1][0] - t0) // 3600) + 1):
        seg = [r for r in held if h * 3600 <= r[0] - t0 < (h + 1) * 3600]
        if len(seg) < 60:
            continue
        err = [r[2] - r[1] for r in seg]
        out.append(math.sqrt(sum(e * e for e in err) / len(err)))
    return out


def main():
    print("Heating phase, from data/plant-id/ -- rms and worst lag in C\n")
    print("    %-42s %6s %8s %9s" % ("capture", "rms", "worst", "charge"))
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "plant-id",
                                           "run-00*.csv"))):
        s = heating(f)
        if s:
            print("    %-42s %6.2f %+8.1f %7.0f s"
                  % (os.path.basename(f), s[0], s[1], s[2]))

    print("\nThe hold, from the oven's own run logs. A profile that only")
    print("passes through its top target has no hold to score, and shows")
    print("its peak alone.\n")
    print("    %-42s %6s %8s %8s %7s %8s"
          % ("run log", "rms", "mean", "minutes", "cl/min", "peak"))
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*run-00*.csv"))):
        s = hold(f)
        if s[2] < 1.0:
            print("    %-42s %6s %8s %8s %7s %8.1f"
                  % (os.path.basename(f), "--", "--", "--", "--", s[4]))
            continue
        print("    %-42s %6.3f %+8.3f %8.1f %7.2f %8.1f"
              % (os.path.basename(f), s[0], s[1], s[2], s[3], s[4]))

    bake = os.path.join(ROOT, "data", "bake-125c-run-0024-2026-09-16.csv")
    print("\nRun 0024 by hour of hold, rms C: "
          + "  ".join("%.3f" % v for v in by_hour(bake)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
