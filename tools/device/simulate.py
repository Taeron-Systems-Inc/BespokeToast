# SPDX-License-Identifier: MIT
"""Run whole profiles on the device against a simulated oven. No heat.

This deliberately does NOT import oven.hardware, so board.D4 is never
claimed and nothing here can energise the relay. What it does exercise is
everything else: the state machine, the controller, the supervisor, the
bounded history, and the real display driving a real screen -- through
preheat, running, cooldown, report and back to idle, at the full reflow
temperature range.

The point is that the expensive failures on this project have all been heap
failures that only appear late in a long run, and a run costs twenty minutes
of heating plus an hour of cooling. Here a full SAC305 profile takes under a
minute, so the same paths can be walked repeatedly in an evening.

The thermal model comes from the measured characterisation, so temperatures
follow a plausible trajectory rather than a ramp -- the supervisor's rate and
stall guards are watching, and they should stay quiet.
"""

import gc
import json
import os
import time

import board

from oven.app import (App, STATE_IDLE, STATE_PREHEAT, STATE_RUNNING,
                      STATE_COOLDOWN, STATE_REPORT, STATE_FAULT)
from oven.controller import Controller, FeedForward, PID
from oven.history import History
from oven import hal
from oven.metrics import Limits as MetricLimits
from oven.profile import Profile
from oven.safety import Supervisor, Limits
from oven.ui import layout as L
from oven.ui import theme as T
from oven.ui.display import Display, preload, largest_free_block

DT = 0.25
AMBIENT = 24.0


def interp(table, x):
    if not table:
        return 0.0
    if x <= table[0][0]:
        return table[0][1]
    if x >= table[-1][0]:
        return table[-1][1]
    for i in range(1, len(table)):
        if table[i][0] >= x:
            (a, ya), (b, yb) = table[i - 1], table[i]
            return ya + (yb - ya) * (x - a) / (b - a)
    return table[-1][1]


class FakeClock(object):
    def __init__(self):
        self.t = 1000.0

    def monotonic(self):
        return self.t


class FakeRelay(object):
    """Records demand. Owns no pin, so it cannot switch anything."""

    def __init__(self):
        self._on = False
        self.actuations = 0

    def set(self, on):
        on = bool(on)
        if on != self._on:
            self.actuations += 1
        self._on = on

    def is_on(self):
        return self._on


class SimulatedOven(object):
    def __init__(self, heating, cooling, start=AMBIENT):
        self.heating = heating
        self.cooling = cooling
        self.temp = start
        self.relay = None
        self.cold = 28.0

    def step(self, dt):
        if self.relay.is_on():
            rate = interp(self.heating, self.temp)
        else:
            rate = interp(self.cooling, self.temp)
        self.temp += rate * dt
        if self.temp < AMBIENT:
            self.temp = AMBIENT
        # The cold junction creeps up over a run, as measured.
        self.cold += 0.0006 * dt * (1 if self.relay.is_on() else -0.3)

    def read(self):
        # Quantised the way the probe is: 0.0625 C steps.
        q = int(self.temp * 16) / 16.0
        return hal.Reading(q, cold=self.cold, faults=hal.FAULT_NONE)


class Rig(object):
    """One App, reused across runs -- which is what code.py does.

    Building a fresh App per profile leaves the previous run's objects to be
    collected and makes the heap look worse than production ever does. The
    interesting question is what a device that has been up for days and run
    many profiles looks like, so the rig is built once and kept.
    """

    def __init__(self, data):
        self.clock = FakeClock()
        self.relay = FakeRelay()
        self.oven = SimulatedOven(data.get("heating_rate_c_per_s"),
                                  data.get("cooling_rate_c_per_s"))
        self.oven.relay = self.relay
        ff = FeedForward(heating_rates=data.get("heating_rate_c_per_s"),
                         cooling_rates=data.get("cooling_rate_c_per_s"))
        coast = data.get("coast_tau_s", 1.2)
        self.events = []
        self.app = App(self.relay, self.oven, self.clock,
                       lambda p: Controller(
                           p, coast_tau_s=coast, feed_forward=ff,
                           pid=PID(kp=0.22, ki=0.004, kd=0.5,
                                   i_max=0.6, i_min=-0.6)),
                       supervisor=Supervisor(Limits()),
                       on_event=lambda n, p: self.events.append(n))
        self.history = History(max_points=150, interval_s=2.0)

    def reset(self):
        """Back to a cold, idle oven, as if a person had walked away."""
        self.relay.actuations = 0        # per run, not cumulative
        self.oven.temp = AMBIENT
        self.oven.cold = 28.0
        self.history.clear()
        self.app.state = STATE_IDLE
        del self.events[:]


def run_profile(display, rig, profile, label):
    app, relay, clock, oven = rig.app, rig.relay, rig.clock, rig.oven
    history = rig.history
    rig.reset()
    problem = app.request_start(profile)
    if problem is not None:
        print("SIM %s refused: %s" % (label, problem.message))
        return None

    screen = []
    failures = {}
    last_render = 0.0
    peak = 0.0
    steps = 0
    limit = int((profile.duration + 2400.0) / DT)

    while steps < limit:
        steps += 1
        clock.t += DT
        oven.step(DT)
        app.tick()
        peak = max(peak, oven.temp)

        if app.state in (STATE_RUNNING, STATE_COOLDOWN) and \
                app.temperature is not None:
            mark = app.elapsed if app.state == STATE_RUNNING else clock.t
            try:
                history.add(mark, app.temperature)
            except MemoryError:
                gc.collect()
                failures["history"] = failures.get("history", 0) + 1
        elif app.state in (STATE_IDLE, STATE_PREHEAT) and len(history):
            history.clear()

        try:
            if app.state == STATE_FAULT:
                screen = L.fault(app.fault.message if app.fault else "unknown")
            elif app.state in (STATE_RUNNING, STATE_PREHEAT):
                screen = L.running(
                    app.temperature, app.target, app.elapsed,
                    max(0.0, profile.duration - app.elapsed), app.stage,
                    app.metrics.time_above_liquidus if app.metrics else 0.0,
                    profile.liquidus_c, app.duty, relay.is_on(),
                    history=history.points, profile_points=profile.points,
                    duration_s=profile.duration)
            elif app.state == STATE_COOLDOWN:
                screen = L.open_the_door(app.temperature, -0.7)
            elif app.state == STATE_REPORT and app.metrics:
                screen = L.report(
                    app.metrics.check(MetricLimits.for_profile(profile)),
                    app.metrics.peak_c, app.metrics.time_above_liquidus)
            else:
                screen = L.home(app.temperature, profile.name, True, None)
        except MemoryError:
            gc.collect()
            failures["screen"] = failures.get("screen", 0) + 1

        if clock.t - last_render >= 0.5:
            last_render = clock.t
            try:
                display.render(screen)
            except MemoryError:
                gc.collect()
                failures["render"] = failures.get("render", 0) + 1

        if app.state in (STATE_REPORT, STATE_FAULT):
            break

    gc.collect()
    print("SIM %-22s state=%-7s peak=%5.1f actuations=%3d hist=%3d/%d "
          "free=%6d largest=%5d failures=%s"
          % (label, app.state, peak, relay.actuations, len(history),
             history.decimations, gc.mem_free(), largest_free_block(),
             failures or "none"))
    if app.state == STATE_FAULT:
        print("SIM   !! fault: %s" % (app.fault.message if app.fault else "?"))
    return {"state": app.state, "peak": peak, "failures": failures,
            "events": list(rig.events)}


def main():
    display = Display(board.DISPLAY)
    preload((T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL))
    display.reserve_chart(L.CHART[2], L.CHART[3])
    with open("/characterisation.json") as f:
        data = json.load(f)

    names = sorted(n for n in os.listdir("/profiles") if n.endswith(".json"))
    rig = Rig(data)
    gc.collect()
    print("SIM begin free=%d largest=%d" % (gc.mem_free(), largest_free_block()))

    bad = 0
    for name in names:
        try:
            profile = Profile.load("/profiles/" + name)
        except Exception as e:
            print("SIM %s rejected: %r" % (name, e))
            bad += 1
            continue
        if profile.duration > 3000:
            print("SIM %-22s skipped (%.0f s: a bake, not a reflow)"
                  % (profile.name, profile.duration))
            continue
        result = run_profile(display, rig, profile, profile.name[:22])
        if result is None or result["failures"] or result["state"] == STATE_FAULT:
            bad += 1
    gc.collect()
    print("SIM end free=%d largest=%d problems=%d"
          % (gc.mem_free(), largest_free_block(), bad))
    print("SIM done")


main()
