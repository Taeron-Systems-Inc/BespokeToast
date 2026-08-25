#!/usr/bin/env python3
"""Fit an oven model to a step-test log (experiment E2).

Reads the CSV produced by the lab runner and extracts the three numbers the
controller needs, plus the one it must not guess:

  gain_c        steady-state rise at full power
  tau_s         thermal time constant
  dead_time_s   transport lag between element and probe
  coast_tau_s   overshoot per unit rate after the relay opens

The heating phase and the cooling phase are fitted separately. Cooling gives
tau on its own — with the relay open the only term left is the loss to
ambient — so it is fitted first and used to constrain the heating fit rather
than letting three parameters trade off freely against one curve.

  python3 fit_model.py oven_log.csv [-o fitted.json]
"""
import csv
import json
import math
import sys


def load(path):
    heat, cool = [], []
    with open(path) as f:
        for row in csv.DictReader(f):
            try:
                t = float(row["t_s"]); h = float(row["hot_c"])
                c = float(row["cold_c"]); cpu = float(row["cpu_c"])
            except (ValueError, KeyError, TypeError):
                continue
            (heat if row["stage"] == "E2H" else
             cool if row["stage"] == "E2C" else []).append((t, h, c, cpu))
    return heat, cool


def fit_cooling(cool, ambient_c):
    """T(t) = amb + (T0-amb) exp(-t/tau). Linear in log space."""
    pts = [(t, h) for t, h, _, _ in cool if h - ambient_c > 2.0]
    if len(pts) < 10:
        return None
    t0, h0 = pts[0]
    xs, ys = [], []
    for t, h in pts:
        xs.append(t - t0)
        ys.append(math.log(h - ambient_c))
    n = len(xs)
    mx = sum(xs) / n; my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    slope = num / den
    return None if slope >= 0 else -1.0 / slope


def simulate(gain, tau, dead, ambient, dt, n):
    """Forward FOPDT response to a unit step, same discretisation as the sim."""
    out = []
    temp = ambient
    pipe = [0.0] * max(1, int(round(dead / dt)))
    for _ in range(n):
        pipe.append(1.0)
        u = pipe.pop(0)
        temp += (gain * u - (temp - ambient)) / tau * dt
        out.append(temp)
    return out


def fit_heating(heat, ambient_c, tau_hint):
    """Search gain and dead time, with tau anchored near the cooling fit."""
    dt = (heat[-1][0] - heat[0][0]) / max(1, len(heat) - 1)
    meas = [h for _, h, _, _ in heat]
    n = len(meas)

    taus = ([tau_hint] if tau_hint is None else
            [tau_hint * f for f in (0.6, 0.8, 1.0, 1.25, 1.6)])
    if tau_hint is None:
        taus = [100, 150, 200, 300, 400, 600]

    best = None
    for tau in taus:
        for gain in range(150, 701, 10):
            for dead in [x * 0.5 for x in range(0, 121)]:
                sim = simulate(gain, tau, dead, ambient_c, dt, n)
                err = sum((a - b) ** 2 for a, b in zip(sim, meas)) / n
                if best is None or err < best[0]:
                    best = (err, gain, tau, dead)
    return best


def coast_from(heat, cool):
    """What the oven does after the relay opens: how far, and for how long."""
    if not cool:
        return None
    cut_temp = heat[-1][1]
    peak_t, peak_c = 0.0, cut_temp
    for t, h, _, _ in cool:
        if h > peak_c:
            peak_c, peak_t = h, t
    rate = None
    tail = [(t, h) for t, h, _, _ in heat if t >= heat[-1][0] - 10.0]
    if len(tail) >= 2 and tail[-1][0] > tail[0][0]:
        rate = (tail[-1][1] - tail[0][1]) / (tail[-1][0] - tail[0][0])
    return {"cut_temp_c": cut_temp, "overshoot_c": peak_c - cut_temp,
            "seconds_to_peak": peak_t, "rate_at_cutoff_c_per_s": rate,
            "coast_tau_s": (peak_c - cut_temp) / rate if rate else None}


def main(argv):
    path = argv[1] if len(argv) > 1 else "oven_log.csv"
    out_path = None
    if "-o" in argv:
        out_path = argv[argv.index("-o") + 1]

    heat, cool = load(path)
    if len(heat) < 20:
        print("not enough heating data (%d rows)" % len(heat)); return 1
    ambient = heat[0][1]

    tau_cool = fit_cooling(cool, ambient) if cool else None
    err, gain, tau, dead = fit_heating(heat, ambient, tau_cool)
    c = coast_from(heat, cool)

    print("  samples          heating %d, cooling %d" % (len(heat), len(cool)))
    print("  ambient          %.2f C" % ambient)
    print("  reached          %.2f C in %.0f s" % (heat[-1][1], heat[-1][0]))
    if tau_cool:
        print("  tau (cooling)    %.0f s     <- fitted alone, constrains the rest" % tau_cool)
    print("  gain_c           %.0f C" % gain)
    print("  tau_s            %.0f s" % tau)
    print("  dead_time_s      %.1f s" % dead)
    print("  fit rms          %.2f C" % math.sqrt(err))
    if c:
        print("  --- coast after the relay opens ---")
        print("  cut at           %.1f C" % c["cut_temp_c"])
        print("  overshoot        %.1f C" % c["overshoot_c"])
        print("  time to peak     %.0f s" % c["seconds_to_peak"])
        if c["rate_at_cutoff_c_per_s"]:
            print("  rate at cutoff   %.2f C/s" % c["rate_at_cutoff_c_per_s"])
            print("  coast_tau_s      %.1f s    <- use this in Controller" % c["coast_tau_s"])
    enc = max(x[2] for x in heat + cool)
    cpu = max(x[3] for x in heat + cool)
    print("  --- enclosure (E8) ---")
    print("  cold junction    peaked %.2f C" % enc)
    print("  cpu die          peaked %.2f C" % cpu)

    result = {"ambient_c": ambient, "gain_c": gain, "tau_s": tau,
              "dead_time_s": dead, "tau_cooling_s": tau_cool,
              "fit_rms_c": math.sqrt(err), "coast": c,
              "enclosure_peak_c": enc, "cpu_peak_c": cpu}
    if out_path:
        json.dump(result, open(out_path, "w"), indent=2)
        print("\n  wrote %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
