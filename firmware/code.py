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
    selected = profiles[0] if profiles else None

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

    app = App(hw.relay, hw.sensor, hw.clock, make_controller)

    screen = []
    while True:
        app.tick()

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
