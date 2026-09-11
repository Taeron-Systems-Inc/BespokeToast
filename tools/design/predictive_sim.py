#!/usr/bin/env python3
"""Predictive tracking, through the real Controller and ElementObserver.

The controller's lead (Controller(element_model=..., lead_s=...)) makes
the loop act on where the chamber will be, given the element's stored
heat, instead of where it is. This sweeps the lead on the identified
two-state plant, with pre-charge on, for the profiles and start
temperatures that have been run on hardware.

    python3 tools/design/predictive_sim.py

Everything in the loop is the firmware's own code; only the plant is a
model.
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT + "/firmware")
from oven.controller import FeedForward, PID, TimeProportional, Controller  # noqa: E402
from oven.elementff import ElementModel, ElementObserver, PreCharge          # noqa: E402
from oven.metrics import RunMetrics                                          # noqa: E402
from oven.profile import Profile                                             # noqa: E402

D = json.load(open(ROOT + "/data/oven-characterisation.json"))
EM = D["element_model"]
TA = EM["ambient_c"]
MODEL = ElementModel(g=EM["g"], beta=EM["beta"], gamma=EM["gamma"],
                     d=EM["d"], ambient_c=TA)


class Plant(object):
    """The two-state model, integrated at the control cadence."""
    def __init__(self, start_c, scale=1.0):
        self.tc, self.z, self.scale = start_c, 0.0, scale

    def read(self):
        return int(self.tc * 16) / 16.0

    def step(self, on, dt=0.25):
        u = 1.0 if on else 0.0
        self.z += (MODEL.g * self.scale * u - MODEL.beta * self.z
                   + MODEL.gamma * (self.tc - TA)) * dt
        self.tc += (self.z - MODEL.d * (self.tc - TA)) * dt


def run(profile, start_c, lead_s, scale=1.0, max_pre=40.0):
    plant = Plant(start_c, scale)
    obs = ElementObserver(MODEL)
    ff = FeedForward(heating_rates=D["heating_rate_c_per_s"],
                     cooling_rates=D["cooling_rate_c_per_s"])
    ctl = Controller(profile, coast_tau_s=D["coast_tau_s"], feed_forward=ff,
                     pid=PID(kp=0.22, ki=0.004, kd=0.5, i_max=0.6, i_min=-0.6),
                     element_model=MODEL, lead_s=lead_s)
    wall = 0.0
    applied = 0.0
    # pre-charge, as the App does it
    entry = profile.entry_time_for(start_c)
    need = MODEL.z_for(profile.slope_at(entry), start_c)
    pre_s = 0.0
    if need > 0.0:
        pc = PreCharge(obs, need, max_s=max_pre, margin=1.0)
        tpo = TimeProportional()
        tpo.reset(wall)
        while True:
            obs.update(wall, plant.read(), applied)
            duty = pc.duty(wall)
            if duty is None:
                break
            on = tpo.update(wall, duty)
            applied = 1.0 if on else 0.0
            plant.step(on)
            wall += 0.25
            pre_s += 0.25
        applied = 0.0
    entry = profile.entry_time_for(plant.read())
    run_started = wall - entry
    ctl.reset(wall)
    m = RunMetrics(profile.liquidus_c or 0.0)
    errs = []
    on = False
    while True:
        elapsed = wall - run_started
        if elapsed >= profile.duration:
            break
        temp = plant.read()
        m.add(elapsed, temp)
        if elapsed <= profile.peak[0]:
            errs.append(temp - profile.target_at(elapsed))
        z = obs.update(wall, temp, 1.0 if on else 0.0)
        duty = ctl.duty_for(elapsed, temp, wall, element_z=z)
        on = ctl.relay_state(wall, duty)
        plant.step(on)
        wall += 0.25
    return dict(rms=(sum(e * e for e in errs) / len(errs)) ** 0.5,
                worst=min(errs), over=max(errs), peak=m.peak_c,
                tal=m.time_above_liquidus, pre=pre_s,
                actuations=ctl.tpo.actuations)


def main():
    snl = Profile.load(ROOT + "/firmware/profiles/ts391snl.json")
    lt = Profile.load(ROOT + "/firmware/profiles/ts391lt.json")
    leads = (0.0, 4.0, 6.0, 8.0, 10.0)
    print("%-6s %-9s %5s | " % ("plant", "profile", "start")
          + " | ".join("lead %2.0fs: rms worst over" % L for L in leads))
    for scale, pn in ((1.0, "g*1.0"), (0.8, "g*0.8"), (1.2, "g*1.2")):
        for prof, start in ((lt, 28.4), (lt, 59.4), (snl, 25.0),
                            (snl, 34.1), (snl, 59.4)):
            cells = []
            for L in leads:
                r = run(prof, start, L, scale)
                cells.append("%5.2f %5.1f %+4.1f" % (r["rms"], r["worst"], r["over"]))
            print("%-6s %-9s %4.0fC | %s" % (pn, prof.name[:9], start, " | ".join(cells)))
        print()
    # what the lead costs and buys beyond tracking error
    print("peak, time above liquidus and relay actuations, nominal plant, lead 0 -> 6:")
    for prof, start in ((lt, 28.4), (snl, 25.0), (snl, 59.4)):
        a, b = run(prof, start, 0.0), run(prof, start, 6.0)
        print("  %-9s %4.0fC  peak %5.1f -> %5.1f   tal %3.0f -> %3.0f   actuations %3d -> %3d"
              % (prof.name[:9], start, a["peak"], b["peak"], a["tal"], b["tal"],
                 a["actuations"], b["actuations"]))


if __name__ == "__main__":
    main()
