#!/usr/bin/env python3
"""Identify a two-state oven from real runs, and score it against the one
this project currently simulates with.

NOT WIRED INTO ANYTHING. This is analysis: it reads the captures in
data/plant-id/ and prints how well each model predicts them. Nothing here
runs on the oven and nothing imports it.

    python3 tools/identify_plant.py            cross-validate and score
    python3 tools/identify_plant.py --fit      fit on everything, print it

## Why

The simulator the tests use applies the commanded duty through a 3 s
transport pipe and then believes the measured rate table immediately. The
rate table is right: it is measured, and it carries the whole nonlinearity
of a radiative oven. What it has no room for is that the ELEMENT has to
charge before any of it happens.

From a cold start that is invisible, because a generated profile's opening
is slow anyway -- the low-temperature entries in the rate table encode the
same delay, so the two errors cancel. A warm start skips that opening and
exposes it. Measured on the oven against simulated:

    34.1 C warm start     -24.3 C lag measured,  -4.8 C simulated
    59.4 C warm start     -32.2 C lag measured,  -5.8 C simulated

The model is wrong by 19 and 26 C, in the one case that matters for
back-to-back boards.

## The model

    dTe/dt = a*u - b*(Te - Tc)          element
    dTc/dt = c*(Te - Tc) - d*(Tc - Ta)  chamber, which is what the probe reads

Leave-one-out over four runs, fitting on three and scoring the fourth:

    held out                   two-state   what we simulate with today
    run-0015-bake-125c              4.64                         23.58
    run-0013-ts391snl-hot           5.79                         16.21
    run-0014-ts391lt                6.07                         13.02
    run-0011-ts391snl-warm          6.54                         14.28

Two to five times better on runs it has never seen. Both models are driven
with the same continuous duty here, so the comparison is of structure and
not of how the relay is quantised.

## What is and is not identifiable

Fitted on all four, the element time constant comes out at 13.6-13.9 s and
agrees with the 9-10 s of dead time measured directly from relay-close to
probe-movement -- a first-order lag looks like a shorter pure delay.

The implied element lead at full power lands somewhere in the hundreds of
degrees, which is plausible for a toaster element, but do NOT read a number
off it: repeated fits give 379 C and 564 C from the same data, because a and
c trade off (see below) and only their product is pinned down. The lead is a
sanity check that the structure is not absurd, not a measurement.

Across the folds, though:

    a (element drive)      12.8 .. 79.6      202% spread
    c (element -> chamber)  0.0013 .. 0.0104 150%
    b (element tau)         0.059 .. 0.078    29%
    d (chamber loss)        0.0037 .. 0.0041  10%

a and c trade off against each other: only their product reaches the
chamber, so this data cannot separate them, and no amount of it will. That
is harmless for a feed-forward, which needs the product. The two parameters
that carry physical meaning are the stable ones.

Fitting a SINGLE run gave a 1101 C element lead, which is not plausible.
That is what fitting one run to four parameters buys you, and it is why the
numbers above come from four.

## Why the duty column

The run logs on the oven carry elapsed_s, target_c, actual_c, relay, cold_c
and cpu_c -- no duty. Identification needs the input signal, and the relay
column sampled at 1 Hz is an aliased view of a 4 s time-proportional window
rather than the power actually applied. So these captures come off the
serial console, which prints the commanded duty every control step, and are
decimated to 1 Hz here because a 14 s time constant does not need more.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "plant-id")
CHAR = os.path.join(ROOT, "data", "oven-characterisation.json")

# Ambient measured on the bench the day these runs were made.
AMBIENT_C = 23.5


def load(path):
    """(t, duty, temp) from a capture, relative to its first row."""
    out = []
    for line in open(path):
        if line.startswith("#") or line.startswith("elapsed_s"):
            continue
        p = line.strip().split(",")
        if len(p) < 8:
            continue
        try:
            out.append((float(p[0]), float(p[4]), float(p[2])))
        except ValueError:
            continue
    if not out:
        return out
    t0 = out[0][0]
    return [(t - t0, u, c) for t, u, c in out]


def _interp(table, x):
    if x <= table[0][0]:
        return table[0][1]
    if x >= table[-1][0]:
        return table[-1][1]
    for i in range(1, len(table)):
        if table[i][0] >= x:
            (a, ya), (b, yb) = table[i - 1], table[i]
            return ya + (yb - ya) * (x - a) / (b - a)
    return table[-1][1]


def two_state(par, rows, ambient_c=AMBIENT_C):
    """Chamber temperature predicted by the two-state model."""
    a, b, c, d = par
    te = tc = rows[0][2]
    out = [tc]
    for i in range(1, len(rows)):
        dt = rows[i][0] - rows[i - 1][0]
        if dt <= 0 or dt > 5:
            out.append(tc)
            continue
        u = rows[i - 1][1]
        n = max(1, int(dt / 0.25))
        h = dt / n
        for _ in range(n):
            te_next = te + (a * u - b * (te - tc)) * h
            tc += (c * (te - tc) - d * (tc - ambient_c)) * h
            te = te_next
        out.append(tc)
    return out


def one_state(rows, char=None):
    """What tests/sim/measured.py does: the rate table, plus a transport
    pipe on the drive. Reproduced here so the two can be scored on one
    metric, rather than compared by assertion."""
    d = json.load(open(char or CHAR))
    heat = sorted(d["heating_rate_c_per_s"])
    cool = sorted(d["cooling_rate_c_per_s"])
    tc = rows[0][2]
    pipe = [0.0] * 12                       # 3 s at 0.25 s
    out = [tc]
    for i in range(1, len(rows)):
        dt = rows[i][0] - rows[i - 1][0]
        if dt <= 0 or dt > 5:
            out.append(tc)
            continue
        u = rows[i - 1][1]
        n = max(1, int(dt / 0.25))
        h = dt / n
        for _ in range(n):
            pipe.append(u)
            ue = pipe.pop(0)
            hot = _interp(heat, tc)
            cold = _interp(cool, tc)
            tc += (cold + ue * (hot - cold)) * h
        out.append(tc)
    return out


def rms(model, rows):
    e = [model[i] - rows[i][2] for i in range(len(rows))]
    return (sum(x * x for x in e) / len(e)) ** 0.5


def cost(par, sets):
    if min(par) <= 0:
        return 1e9
    total = 0.0
    n = 0
    for rows in sets:
        m = two_state(par, rows)
        for i, r in enumerate(rows):
            e = m[i] - r[2]
            total += e * e
            n += 1
    return (total / n) ** 0.5


def nelder_mead(f, x0, step, iters=900):
    n = len(x0)
    pts = [list(x0)]
    for i in range(n):
        p = list(x0)
        p[i] += step[i]
        pts.append(p)
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(len(pts)), key=lambda i: vals[i])
        pts = [pts[i] for i in order]
        vals = [vals[i] for i in order]
        if abs(vals[-1] - vals[0]) < 1e-9:
            break
        cen = [sum(p[i] for p in pts[:-1]) / n for i in range(n)]
        ref = [cen[i] + (cen[i] - pts[-1][i]) for i in range(n)]
        fr = f(ref)
        if fr < vals[0]:
            exp = [cen[i] + 2 * (cen[i] - pts[-1][i]) for i in range(n)]
            fe = f(exp)
            pts[-1], vals[-1] = (exp, fe) if fe < fr else (ref, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = ref, fr
        else:
            con = [cen[i] + 0.5 * (pts[-1][i] - cen[i]) for i in range(n)]
            fc = f(con)
            if fc < vals[-1]:
                pts[-1], vals[-1] = con, fc
            else:
                for i in range(1, len(pts)):
                    pts[i] = [(pts[i][j] + pts[0][j]) / 2 for j in range(n)]
                    vals[i] = f(pts[i])
    i = min(range(len(pts)), key=lambda i: vals[i])
    return pts[i], vals[i]


X0 = [40.0, 0.10, 0.0057, 0.0076]
STEP = [8.0, 0.03, 0.002, 0.003]


def captures():
    out = {}
    if not os.path.isdir(DATA):
        return out
    for f in sorted(os.listdir(DATA)):
        if f.endswith(".csv"):
            rows = load(os.path.join(DATA, f))
            if len(rows) > 50:
                out[f[:-4]] = rows
    return out


def main(argv):
    runs = captures()
    if not runs:
        print("no captures in %s" % DATA)
        return 1

    if "--fit" in argv:
        best, err = nelder_mead(lambda p: cost(p, list(runs.values())),
                                X0, STEP)
        print("fitted on all %d runs, rms %.2f C" % (len(runs), err))
        print("  a=%.4f b=%.5f c=%.6f d=%.6f" % tuple(best))
        print("  element time constant %.1f s, lead at full power %.0f C"
              % (1 / best[1], best[0] / best[1]))
        return 0

    print("leave-one-out, and the model the tests use today for comparison")
    print("%-28s %10s %10s" % ("held out", "two-state", "one-state"))
    for held in runs:
        train = [v for k, v in runs.items() if k != held]
        best, _ = nelder_mead(lambda p: cost(p, train), X0, STEP)
        print("%-28s %10.2f %10.2f"
              % (held, rms(two_state(best, runs[held]), runs[held]),
                 rms(one_state(runs[held]), runs[held])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
