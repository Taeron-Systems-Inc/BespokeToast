"""A model that does NOT work, kept so nobody builds it again.

Leave-one-out over the four captures in data/plant-id/, rms in C:

    held out                    elem-lag   two-state   current
    run-0011-ts391snl-warm          7.99        6.54     14.28
    run-0013-ts391snl-hot          12.95        5.79     16.21
    run-0014-ts391lt               17.87        6.06     13.02
    run-0015-bake-125c             18.23        4.64     23.58

It looked like the right idea: keep the measured rate tables exactly, which
carry the whole nonlinearity of a radiative oven and are rule six in
docs/control-loop.md, and add only the missing dynamics by lagging the
element's contribution. On two of four runs it is worse than the model it
was meant to replace.

Why it fails is the useful part. The heat the element delivers depends on
the ELEMENT-CHAMBER TEMPERATURE DIFFERENCE, not on duty and chamber
temperature alone. A cold chamber under a hot element takes heat fast; as
the chamber closes on the element the flow falls, whatever the duty is
doing. The linear two-state model has that coupling -- c*(Te - Tc) -- and
this does not, and no lag on a table can express it.

So the rate tables stay right about steady state, and the two-state model
extends them with dynamics rather than contradicting them: fitted, it
reproduces the same steady-state rates, because it has to.

Lag the ELEMENT'S contribution only. Passive loss responds instantly.

    e_ss   = u * (h(T) - c(T))        what the element gives once charged
    de/dt  = (e_ss - e) / tau         it charges with time constant tau
    dTc/dt = c(T) + e                 loss is instant, element is lagged

lagfit.py lagged the whole of c(T) + u*(h-c), loss included, and scored
7.6-20 C. The chamber loses heat whether the element is charged or not.
"""
import json, sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from identify_plant import load, _interp, rms, one_state, two_state, nelder_mead, cost as cost2, X0, STEP

ROOT = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
D = json.load(open(ROOT + "/data/oven-characterisation.json"))
HEAT = sorted(D["heating_rate_c_per_s"]); COOL = sorted(D["cooling_rate_c_per_s"])

def elem_lag(tau, rows, e0=0.0):
    tc = rows[0][2]; e = e0
    out = [tc]
    for i in range(1, len(rows)):
        dt = rows[i][0] - rows[i-1][0]
        if dt <= 0 or dt > 5:
            out.append(tc); continue
        u = rows[i-1][1]
        n = max(1, int(dt/0.25)); h = dt/n
        for _ in range(n):
            hot = _interp(HEAT, tc); cold = _interp(COOL, tc)
            e += (u * (hot - cold) - e) * h / tau
            tc += (cold + e) * h
        out.append(tc)
    return out

S = ROOT + "/data/plant-id/"
runs = {n[:-4]: load(S + n) for n in sorted(__import__("os").listdir(S)) if n.endswith(".csv")}
runs = {k: v for k, v in runs.items() if len(v) > 50}

print("%-26s %9s %9s %9s %7s" % ("held out", "elem-lag", "two-state", "current", "tau"))
for held in runs:
    train = [v for k, v in runs.items() if k != held]
    best = None
    for i in range(2, 80):
        tau = i * 0.5
        r = (sum(rms(elem_lag(tau, rw), rw) ** 2 * len(rw) for rw in train)
             / sum(len(rw) for rw in train)) ** 0.5
        if best is None or r < best[1]: best = (tau, r)
    tau = best[0]
    p2, _ = nelder_mead(lambda p: cost2(p, train), X0, STEP, iters=400)
    print("%-26s %9.2f %9.2f %9.2f %7.1f" % (
        held, rms(elem_lag(tau, runs[held]), runs[held]),
        rms(two_state(p2, runs[held]), runs[held]),
        rms(one_state(runs[held]), runs[held]), tau))
