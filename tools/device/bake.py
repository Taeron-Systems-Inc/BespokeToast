# SPDX-License-Identifier: MIT
"""The 125 C MSL bake, start to finish, on the device. No heat.

This is the profile the run-timeout fix was for: 15201 s against what used
to be a flat 3600 s ceiling, so it could never have completed. It is also
the only profile long enough to make the chart history decimate repeatedly
and the only one that holds a setpoint for hours, which is where a slow
memory problem would show if there is one.

Stepped at one second rather than the control cadence: four hours at 0.25 s
is a quarter of a million iterations, and what is under test here is the
long-run behaviour, not the loop timing.

Like the other harnesses this never imports oven.hardware, so the relay pin
is never claimed and no heat is possible.
"""

import gc
import json
import time

import board

from oven.app import (App, STATE_IDLE, STATE_RUNNING, STATE_COOLDOWN,
                      STATE_REPORT, STATE_FAULT)
from oven.controller import Controller, FeedForward, PID
from oven.history import History
from oven import hal
from oven.profile import Profile
from oven.safety import Supervisor, Limits
from oven.ui import layout as L
from oven.ui import theme as T
from oven.ui.display import Display, preload, largest_free_block

DT = 1.0
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


class Clock(object):
    def __init__(self):
        self.t = 9000.0

    def monotonic(self):
        return self.t


class Relay(object):
    """Owns no pin: no heat is possible from here."""

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


class Oven(object):
    def __init__(self, heating, cooling):
        self.heating, self.cooling = heating, cooling
        self.temp = AMBIENT
        self.relay = None

    def step(self, dt):
        rate = (interp(self.heating, self.temp) if self.relay.is_on()
                else interp(self.cooling, self.temp))
        self.temp = max(AMBIENT, self.temp + rate * dt)

    def read(self):
        return hal.Reading(int(self.temp * 16) / 16.0, cold=28.0,
                           faults=hal.FAULT_NONE)


def main():
    display = Display(board.DISPLAY)
    preload((T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL))
    display.reserve_chart(L.CHART[2], L.CHART[3])
    with open("/characterisation.json") as f:
        data = json.load(f)
    profile = Profile.load("/profiles/bake-msl-125c.json")

    clock, relay = Clock(), Relay()
    oven = Oven(data.get("heating_rate_c_per_s"),
                data.get("cooling_rate_c_per_s"))
    oven.relay = relay
    ff = FeedForward(heating_rates=data.get("heating_rate_c_per_s"),
                     cooling_rates=data.get("cooling_rate_c_per_s"))
    app = App(relay, oven, clock,
              lambda p: Controller(p, coast_tau_s=data.get("coast_tau_s", 1.2),
                                   feed_forward=ff,
                                   pid=PID(kp=0.22, ki=0.004, kd=0.5,
                                           i_max=0.6, i_min=-0.6)),
              supervisor=Supervisor(Limits()),
              on_event=lambda n, p: None)
    history = History(max_points=150, interval_s=2.0)

    gc.collect()
    print("BAKE begin %.0f s profile, free=%d largest=%d"
          % (profile.duration, gc.mem_free(), largest_free_block()))
    problem = app.request_start(profile)
    if problem is not None:
        print("BAKE refused: %s" % problem.message)
        return

    failures = {}
    last_render = 0.0
    last_note = 0.0
    steps = 0
    over = 0.0
    limit = int((profile.duration + 7200.0) / DT)
    wall0 = time.monotonic()

    while steps < limit:
        steps += 1
        clock.t += DT
        oven.step(DT)
        app.tick()

        if app.state == STATE_RUNNING and app.target is not None:
            if oven.temp - app.target > over:
                over = oven.temp - app.target

        if app.state in (STATE_RUNNING, STATE_COOLDOWN) and \
                app.temperature is not None:
            mark = app.elapsed if app.state == STATE_RUNNING else clock.t
            try:
                history.add(mark, app.temperature)
            except MemoryError:
                gc.collect()
                failures["history"] = failures.get("history", 0) + 1

        try:
            if app.state == STATE_FAULT:
                screen = L.fault(app.fault.message if app.fault else "?")
            elif app.state == STATE_RUNNING:
                screen = L.running(
                    app.temperature, app.target, app.elapsed,
                    max(0.0, profile.duration - app.elapsed), app.stage,
                    0.0, profile.liquidus_c, app.duty, relay.is_on(),
                    history=history.points, profile_points=profile.points,
                    duration_s=profile.duration)
            elif app.state == STATE_COOLDOWN:
                screen = L.open_the_door(app.temperature, -0.4)
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

        if app.elapsed - last_note >= 1800.0 and app.state == STATE_RUNNING:
            last_note = app.elapsed
            gc.collect()
            print("BAKE  %5.0f/%.0f s  %6.1f C (target %5.1f)  hist=%d/%d "
                  "free=%d largest=%d act=%d %.0fs wall"
                  % (app.elapsed, profile.duration, oven.temp, app.target,
                     len(history), history.decimations, gc.mem_free(),
                     largest_free_block(), relay.actuations,
                     time.monotonic() - wall0))

        if app.state in (STATE_REPORT, STATE_FAULT):
            break

    gc.collect()
    print("BAKE end state=%s elapsed=%.0f s max-over-target=%.1f C "
          "actuations=%d hist=%d decimations=%d free=%d largest=%d failures=%s"
          % (app.state, app.elapsed, over, relay.actuations, len(history),
             history.decimations, gc.mem_free(), largest_free_block(),
             failures or "none"))
    if app.state == STATE_FAULT:
        print("BAKE !! fault: %s" % (app.fault.message if app.fault else "?"))
    print("BAKE done")


main()
