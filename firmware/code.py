# SPDX-License-Identifier: MIT
"""BespokeToast entry point.

Assembles the hardware, wires the application to the interface, and runs the
loop. Deliberately thin: everything that decides anything lives in oven/,
where it can be tested without a board.
"""

import json
import os
import time

import board

from oven.app import App, STATE_IDLE, STATE_RUNNING, STATE_PREHEAT, \
    STATE_COOLDOWN, STATE_REPORT, STATE_FAULT
from oven.controller import Controller, FeedForward, PID
from oven.hardware import Hardware
from oven.metrics import Limits as MetricLimits
from oven.profile import Profile
from oven.ui import layout as L
from oven.ui.display import Display

VERSION = "v2.0-dev"
PROFILE_DIR = "/profiles"
CHARACTERISATION = "/characterisation.json"


def load_characterisation():
    try:
        with open(CHARACTERISATION) as f:
            return json.load(f)
    except Exception:
        return None


def load_profiles():
    out = []
    try:
        names = [n for n in os.listdir(PROFILE_DIR) if n.endswith(".json")]
    except OSError:
        return out
    for name in sorted(names):
        try:
            out.append(Profile.load(PROFILE_DIR + "/" + name))
        except Exception:
            pass                       # a bad profile must not stop boot
    return out


def main():
    hw = Hardware()                    # claims D4 and drives it low
    display = Display(board.DISPLAY)

    data = load_characterisation()
    if data:
        ff = FeedForward(heating_rates=data.get("heating_rate_c_per_s"),
                         cooling_rates=data.get("cooling_rate_c_per_s"))
        coast = data.get("coast_tau_s", 1.2)
    else:
        ff = FeedForward()
        coast = 1.2

    profiles = load_profiles()
    # Alphabetical order would select "4900P (as run)", which measurement
    # shows this oven cannot follow. A profile may declare itself the default.
    selected = None
    for p in profiles:
        if getattr(p, "is_default", False):
            selected = p
            break
    if selected is None and profiles:
        selected = profiles[0]

    display.render(L.splash(VERSION))
    time.sleep(1.2)

    reading = hw.sensor.read()
    display.render(L.self_test([
        ("thermocouple", reading is not None and reading.ok),
        ("relay safe state", not hw.relay.is_on()),
        ("profiles", bool(profiles)),
        ("characterisation", data is not None),
    ]))
    time.sleep(1.5)

    def make_controller(profile):
        return Controller(profile, coast_tau_s=coast, feed_forward=ff,
                          pid=PID(kp=0.03, ki=0.0015, kd=0.5))

    # Every control step is printed as CSV on the serial console. The
    # previous firmware kept no record of any run it ever performed; a host
    # capturing this gets the whole run without the device needing storage.
    print("# t,state,temp_c,target_c,duty,relay,cold_c")

    def emit(row):
        print("%.2f,%s,%s,%s,%.3f,%d,%s" % (
            row["t"], row["state"],
            "" if row["temp"] is None else "%.4f" % row["temp"],
            "" if row["target"] is None else "%.2f" % row["target"],
            row["duty"] or 0.0, 1 if row["relay"] else 0,
            "" if row["cold"] is None else "%.2f" % row["cold"]))

    def announce(name, payload):
        print("# event %s %s" % (name, payload))

    app = App(hw.relay, hw.sensor, hw.clock, make_controller,
              on_event=announce, sample=emit)

    screen = []
    while True:
        app.tick()

        # Touch is polled outside the control step: a press must not be able
        # to delay a control step, and a missed press is merely annoying.
        point = hw.touch.press()
        if point is not None:
            action = L.hit(screen, point[0], point[1])
            if action == "start" and selected is not None:
                problem = app.request_start(selected)
                if problem is not None:
                    print("# start refused: %s" % problem.message)
            elif action == "abort":
                app.abort()
            elif action == "acknowledge":
                app.acknowledge_fault()
            elif action == "done":
                app.state = STATE_IDLE
            elif action == "profiles" and profiles:
                selected = profiles[(profiles.index(selected) + 1) % len(profiles)] \
                    if selected in profiles else profiles[0]

        if app.state == STATE_FAULT:
            screen = L.fault(app.fault.message if app.fault else "unknown")
        elif app.state in (STATE_RUNNING, STATE_PREHEAT):
            remaining = 0.0
            if app.profile is not None:
                remaining = app.profile.duration - app.elapsed
            screen = L.running(app.temperature, app.target, app.elapsed,
                               remaining, app.stage,
                               app.metrics.time_above_liquidus if app.metrics
                               else 0.0,
                               app.profile.liquidus_c if app.profile else None,
                               app.duty, hw.relay.is_on())
        elif app.state == STATE_COOLDOWN:
            screen = L.open_the_door(app.temperature, None)
        elif app.state == STATE_REPORT and app.metrics and app.profile:
            screen = L.report(app.metrics.check(
                MetricLimits.for_profile(app.profile)),
                app.metrics.peak_c, app.metrics.time_above_liquidus)
        else:
            ready = app.temperature is not None and app.temperature < 60.0
            screen = L.home(app.temperature,
                            selected.name if selected else None,
                            ready and selected is not None,
                            None if ready else "oven too hot to start")

        display.render(screen)


try:
    main()
finally:
    # Whatever happens, stop heating. CircuitPython releases the pin on the
    # way out anyway and this oven's relay has a pulldown, but saying it
    # explicitly costs nothing.
    try:
        import digitalio
        _r = digitalio.DigitalInOut(board.D4)
        _r.direction = digitalio.Direction.OUTPUT
        _r.value = False
    except Exception:
        pass
