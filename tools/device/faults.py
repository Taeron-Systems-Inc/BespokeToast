# SPDX-License-Identifier: MIT
"""Drive every fault to the real screen, and back out again. No heat.

Like simulate.py this never imports oven.hardware, so the relay pin is
never claimed. What it checks is the path nobody wants to exercise for the
first time during a real failure: a fault trips, the relay is commanded
off, the fault screen renders on the actual display, ACK clears it, and the
oven returns to idle ready to run again.

The fault screen is the one screen that has to work, and it is drawn when
the heap is at its worst -- late in a run, after everything else has been
allocated. Its border used to be a single full-screen Rect asking for 9600
contiguous bytes, which failed while 70 kB was still free.
"""

import gc
import json

import board

from oven.app import App, STATE_IDLE, STATE_FAULT, STATE_RUNNING
from oven.controller import Controller, FeedForward, PID
from oven import hal
from oven.profile import Profile
from oven.safety import (Supervisor, Limits, FAULT_OVER_TEMP, FAULT_SENSOR,
                         FAULT_SENSOR_STALE, FAULT_SENSOR_FROZEN)
from oven.ui import layout as L
from oven.ui import theme as T
from oven.ui.display import Display, preload, largest_free_block

DT = 0.25


class Clock(object):
    def __init__(self):
        self.t = 5000.0

    def monotonic(self):
        return self.t


class Relay(object):
    """Owns no pin. Records what was asked of it."""

    def __init__(self):
        self._on = False
        self.on_after_fault = 0

    def set(self, on):
        self._on = bool(on)

    def is_on(self):
        return self._on


class Sensor(object):
    """A thermocouple that misbehaves on demand."""

    def __init__(self):
        self.temp = 25.0
        self.faults = hal.FAULT_NONE
        self.freeze = False
        self.return_nothing = False

    def read(self):
        if self.return_nothing:
            return None
        return hal.Reading(self.temp, cold=28.0, faults=self.faults)


def build(display):
    clock, relay, sensor = Clock(), Relay(), Sensor()
    app = App(relay, sensor, clock,
              lambda p: Controller(p, coast_tau_s=1.2,
                                   feed_forward=FeedForward(),
                                   pid=PID(kp=0.22, ki=0.004, kd=0.5)),
              supervisor=Supervisor(Limits()),
              on_event=lambda n, p: None)
    return app, clock, relay, sensor


def draw(display, app):
    """Render whatever the app's state calls for, as code.py would."""
    if app.state == STATE_FAULT:
        screen = L.fault(app.fault.message if app.fault else "unknown")
    else:
        screen = L.home(app.temperature, "SAC305", True, None)
    display.render(screen)
    return screen


def start_running(app, clock, sensor, profile):
    sensor.temp = 25.0
    problem = app.request_start(profile)
    if problem is not None:
        return "refused: %s" % problem.message
    for _ in range(200):
        clock.t += DT
        app.tick()
        if app.state == STATE_RUNNING:
            return None
    return "never reached running (state=%s)" % app.state


def case(display, profile, name, provoke, expect_code):
    app, clock, relay, sensor = build(display)
    problem = start_running(app, clock, sensor, profile)
    if problem:
        print("FAULT %-18s SETUP FAILED %s" % (name, problem))
        return False

    provoke(app, clock, sensor)

    for _ in range(600):
        clock.t += DT
        app.tick()
        if app.state == STATE_FAULT:
            break

    ok = True
    if app.state != STATE_FAULT:
        print("FAULT %-18s did NOT fault" % name)
        return False
    if app.fault.code != expect_code:
        print("FAULT %-18s wrong fault: %s (wanted code %d)"
              % (name, app.fault.message, expect_code))
        ok = False
    if relay.is_on():
        print("FAULT %-18s !! RELAY STILL COMMANDED ON" % name)
        ok = False

    # The screen that has to work, drawn on the real display.
    try:
        draw(display, app)
    except Exception as e:
        print("FAULT %-18s fault screen failed to render: %r" % (name, e))
        ok = False

    # Heat must stay refused while the fault is latched.
    sensor.faults = hal.FAULT_NONE
    sensor.freeze = False
    sensor.return_nothing = False
    sensor.temp = 25.0
    for _ in range(40):
        clock.t += DT
        app.tick()
        if relay.is_on():
            print("FAULT %-18s !! relay re-energised while faulted" % name)
            ok = False
            break

    app.acknowledge_fault()
    if app.state != STATE_IDLE:
        print("FAULT %-18s ACK did not clear it (state=%s)" % (name, app.state))
        ok = False
    draw(display, app)

    # And it must be usable again afterwards.
    problem = start_running(app, clock, sensor, profile)
    if problem:
        print("FAULT %-18s could not run again after ACK: %s" % (name, problem))
        ok = False
    app.abort()

    gc.collect()
    print("FAULT %-18s %s  (%s) free=%d largest=%d"
          % (name, "ok" if ok else "PROBLEM",
             app.fault.message if app.fault else "cleared",
             gc.mem_free(), largest_free_block()))
    return ok


def over_temp(app, clock, sensor):
    sensor.temp = 300.0


def open_circuit(app, clock, sensor):
    sensor.faults = hal.FAULT_OPEN_CIRCUIT


def frozen(app, clock, sensor):
    sensor.temp = 120.0          # never changes again


def no_reading(app, clock, sensor):
    sensor.return_nothing = True


def main():
    display = Display(board.DISPLAY)
    preload((T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL))
    display.reserve_chart(L.CHART[2], L.CHART[3])
    profile = Profile.load("/profiles/ts391snl.json")
    gc.collect()
    print("FAULT begin free=%d largest=%d" % (gc.mem_free(), largest_free_block()))

    bad = 0
    for name, provoke, code in (
            ("over temperature", over_temp, FAULT_OVER_TEMP),
            ("open circuit", open_circuit, FAULT_SENSOR),
            ("frozen sensor", frozen, FAULT_SENSOR_FROZEN),
            ("no reading", no_reading, FAULT_SENSOR_STALE)):
        if not case(display, profile, name, provoke, code):
            bad += 1
    gc.collect()
    print("FAULT end problems=%d free=%d largest=%d"
          % (bad, gc.mem_free(), largest_free_block()))
    print("FAULT done")


main()
