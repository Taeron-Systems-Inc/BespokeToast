#!/usr/bin/env python3
"""Turn a console capture into a data/plant-id/ file.

    python3 tools/capture_to_plant_id.py capture.txt data/plant-id/name.csv

The oven's run logs carry no duty column, so identification works from the
serial console instead, which prints the commanded duty every control step.
This keeps the rows that matter (running, preheat, precharge, steptest),
re-bases time to the first of them, and decimates to 1 Hz -- a 14 s element
time constant does not need 4 Hz, and identify_plant.py fits four times
faster on a quarter of the rows.
"""
import os
import sys

KEEP = ("running", "preheat", "precharge", "steptest")


def convert(src, dst, every=4):
    rows = []
    for line in open(src):
        p = line.strip().split(",")
        if len(p) < 8 or not p[0][:1].isdigit():
            continue
        if p[1] not in KEEP:
            continue
        rows.append(p)
    if not rows:
        raise SystemExit("no usable rows in %s" % src)
    t0 = float(rows[0][0])
    kept = rows[::every]
    with open(dst, "w") as f:
        f.write("# from %s; duty is the COMMANDED duty, which the run log "
                "does not carry\n" % os.path.basename(src))
        f.write("elapsed_s,state,temp_c,target_c,duty,relay,cold_c,cpu_c\n")
        for r in kept:
            r = list(r)
            r[0] = "%.2f" % (float(r[0]) - t0)
            f.write(",".join(r) + "\n")
    return len(kept)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    n = convert(sys.argv[1], sys.argv[2])
    print("%s: %d rows" % (sys.argv[2], n))
