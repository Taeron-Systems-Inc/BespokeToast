#!/usr/bin/env python3
"""Local dynamics at each plateau of a heat_step_test run.

The identification schedule holds the oven at several temperatures and
square-waves the duty around each. This reads the capture, finds each
plateau's excitation window, and fits a first-order response to it -- so the
question "does the element time constant change with temperature?" gets a
number per plateau instead of one number for the whole range.

    python3 tools/plateau_dynamics.py data/plant-id/ident-2026-09-11.csv

For each plateau it fits, on the excitation window only:

    dTc/dt = k * (u_lagged - u_hold) + drift
    du_lagged/dt = (u - u_lagged) / tau

i.e. a gain, a lag and a drift term, with the hold duty removed so the fit
sees only the square wave. tau is the element charge time constant at that
temperature; k is how much chamber rate one unit of duty buys once the
element has charged, which should agree with h(T) - c(T) from the rate table
if everything is consistent.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from identify_plant import nelder_mead     # noqa: E402


def load(path):
    """Rows of (t, duty, temp) and the step markers, from a console capture."""
    rows, marks = [], []
    for line in open(path):
        line = line.strip()
        if line.startswith("# step "):
            marks.append((len(rows), line[len("# step "):]))
            continue
        if not line or line.startswith("#"):
            continue
        p = line.split(",")
        if len(p) < 8 or not p[0][:1].isdigit():
            continue
        try:
            rows.append((float(p[0]), float(p[4]), float(p[2])))
        except ValueError:
            continue
    return rows, marks


def plateaux(rows, marks):
    """(label, hold_duty, rows) for each excitation window."""
    out = []
    for i, (idx, label) in enumerate(marks):
        if " settle" not in label:
            continue
        name = label.split(" settle")[0]
        # the window runs from the first "up" to the end of the last "down"
        ups = [j for j, (k, l) in enumerate(marks) if l.startswith(name + " up")]
        downs = [j for j, (k, l) in enumerate(marks) if l.startswith(name + " down")]
        if not ups or not downs:
            continue
        start = marks[ups[0]][0]
        last = downs[-1]
        end = marks[last + 1][0] if last + 1 < len(marks) else len(rows)
        window = rows[start:end]
        if len(window) < 40:
            continue
        settle = rows[idx:start]
        hold = sum(u for _, u, _ in settle) / max(1, len(settle))
        out.append((name, hold, window))
    return out


def simulate(par, window, hold):
    k, tau, drift = par
    t0, _, tc = window[0]
    ul = hold
    out = [tc]
    for i in range(1, len(window)):
        dt = window[i][0] - window[i - 1][0]
        if dt <= 0 or dt > 5:
            out.append(tc)
            continue
        u = window[i - 1][1]
        n = max(1, int(dt / 0.25))
        h = dt / n
        for _ in range(n):
            ul += (u - ul) * h / tau
            tc += (k * (ul - hold) + drift) * h
        out.append(tc)
    return out


def fit(window, hold):
    def cost(par):
        if par[1] <= 0.5 or par[0] <= 0:
            return 1e9
        m = simulate(par, window, hold)
        return (sum((m[i] - window[i][2]) ** 2
                    for i in range(len(window))) / len(window)) ** 0.5
    best, err = nelder_mead(cost, [1.0, 12.0, 0.0], [0.5, 5.0, 0.02],
                            iters=600)
    return best, err


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    rows, marks = load(argv[0])
    if not rows:
        print("no rows in %s" % argv[0])
        return 1
    print("%-8s %8s %8s %9s %8s %8s" % ("plateau", "mean C", "hold u",
                                       "gain C/s", "tau s", "rms"))
    for name, hold, window in plateaux(rows, marks):
        (k, tau, drift), err = fit(window, hold)
        mean_c = sum(c for _, _, c in window) / len(window)
        print("%-8s %8.1f %8.3f %9.3f %8.1f %8.2f"
              % (name, mean_c, hold, k, tau, err))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
