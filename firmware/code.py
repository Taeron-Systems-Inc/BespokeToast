# SPDX-License-Identifier: MIT
"""BespokeToast entry point.

Assembles the hardware, wires the application to the interface, and runs the
loop. Deliberately thin: everything that decides anything lives in oven/,
where it can be tested without a board.
"""

import json
import os
import sys
import time

import board
import supervisor

from oven.app import App, STATE_IDLE, STATE_RUNNING, STATE_PREHEAT, \
    STATE_COOLDOWN, STATE_REPORT, STATE_FAULT
from oven.controller import Controller, FeedForward, PID
from oven.hardware import Hardware, cpu_temperature
from oven.metrics import Limits as MetricLimits
from oven.profile import Profile
from oven.ui import layout as L
from oven.ui import theme as T
from oven.ui.display import Display, preload

VERSION = "v2.0-dev"

# Commands accepted on the serial console, one per line. This exists so a run
# can be started and supervised from a host when nobody is standing at the
# oven. ABORT is unconditional and always available -- that is the point of
# having it at all.
#
# Reading the console does not disable the REPL: Ctrl-C still interrupts.
PROFILE_DIR = "/profiles"
CHARACTERISATION = "/characterisation.json"


def load_characterisation():
    """The measured plant model.

    Without it the controller falls back to a crude straight-line estimate of
    the oven, which will track badly and could miss a peak entirely. That is
    far too significant to happen quietly.
    """
    try:
        with open(CHARACTERISATION) as f:
            return json.load(f)
    except Exception as e:
        print("# WARNING no %s (%r): falling back to an ESTIMATED oven "
              "model. Tracking will be poor." % (CHARACTERISATION, e))
        return None


def load_profiles():
    out = []
    try:
        names = [n for n in os.listdir(PROFILE_DIR) if n.endswith(".json")]
    except OSError as e:
        print("# WARNING cannot list %s (%r): no profiles available"
              % (PROFILE_DIR, e))
        return out
    for name in sorted(names):
        try:
            out.append(Profile.load(PROFILE_DIR + "/" + name))
        except Exception as e:
            # A bad profile must not stop boot, but a profile that quietly
            # fails to appear is worse than one that refuses loudly.
            print("# WARNING profile %s rejected: %s" % (name, e))
    return out


HARDWARE = None


def main():
    global HARDWARE
    hw = Hardware()                    # claims D4 and drives it low
    HARDWARE = hw
    display = Display(board.DISPLAY)
    # Warm the font cache here, not inside the first render: see preload().
    preload((T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL))
    # Claim the chart buffer now, while the heap is whole.
    display.reserve_chart(L.CHART[2], L.CHART[3])

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
        # Tuned against the measured plant, not guessed. Run 3 showed the
        # oven lagging the early ramp by up to 15 °C while only 1 % of the
        # samples that were behind had duty saturated -- headroom sitting
        # unused because the gains were too soft. Swept in simulation and
        # checked for robustness against +/-20 % plant error and a warm
        # start; every case stayed inside the peak and time-above-liquidus
        # windows.
        return Controller(profile, coast_tau_s=coast, feed_forward=ff,
                          pid=PID(kp=0.22, ki=0.004, kd=0.5,
                                  i_max=0.6, i_min=-0.6))

    # Every control step is printed as CSV on the serial console. The
    # previous firmware kept no record of any run it ever performed; a host
    # capturing this gets the whole run without the device needing storage.
    # cpu_c is a second thermometer in the same box, on a different chip.
    # The pair is the useful thing: across a full run the MCP9600's cold
    # junction rises 12-15 °C while the SAMD51 die does not move at all, so
    # the box is not warming -- heat is reaching that one chip, almost
    # certainly along the thermocouple wires into its terminals. That is the
    # mechanism behind cold-junction compensation error, and logging both is
    # what turns it from a worry into a measurement.
    print("# t,state,temp_c,target_c,duty,relay,cold_c,cpu_c")

    def emit(row):
        cpu = cpu_temperature()
        print("%.2f,%s,%s,%s,%.3f,%d,%s,%s" % (
            row["t"], row["state"],
            "" if row["temp"] is None else "%.4f" % row["temp"],
            "" if row["target"] is None else "%.2f" % row["target"],
            row["duty"] or 0.0, 1 if row["relay"] else 0,
            "" if row["cold"] is None else "%.2f" % row["cold"],
            "" if cpu is None else "%.2f" % cpu))

    def announce(name, payload):
        print("# event %s %s" % (name, payload))

    app = App(hw.relay, hw.sensor, hw.clock, make_controller,
              on_event=announce, sample=emit)

    # The chart needs a trace. One point every two seconds is plenty at 308
    # pixels wide for a run of a few hundred seconds, and keeps the list
    # short enough to redraw cheaply.
    history = []
    last_point = [None]
    HISTORY_INTERVAL_S = 2.0

    def cooling_rate():
        if len(history) < 4:
            return None
        (t0, v0), (t1, v1) = history[-4], history[-1]
        return None if t1 <= t0 else (v1 - v0) / (t1 - t0)

    screen = []
    last_render = [0.0]
    command = [""]

    def poll_command():
        """Read a line from the console without blocking."""
        try:
            n = supervisor.runtime.serial_bytes_available
        except AttributeError:
            return None
        while n:
            ch = sys.stdin.read(1)
            n -= 1
            if ch in ("\r", "\n"):
                line = command[0].strip().upper()
                command[0] = ""
                if line:
                    return line
            elif len(command[0]) < 32:
                command[0] += ch
        return None

    while True:
        app.tick()

        cmd = poll_command()
        # poll_command returns None on every pass with no complete line, and
        # None has no .startswith. The equality branches tolerated it; the
        # prefix match did not, and it crashed the firmware on the first
        # loop.
        if not cmd:
            pass
        elif cmd == "ABORT":
            app.abort()
            print("# command ABORT accepted, state=%s" % app.state)
        elif cmd == "START":
            problem = app.request_start(selected) if selected else None
            if selected is None:
                print("# command START refused: no profile")
            elif problem is not None:
                print("# command START refused: %s" % problem.message)
            else:
                print("# command START accepted: %s" % selected.name)
        elif cmd == "ACK":
            app.acknowledge_fault()
            print("# command ACK, state=%s" % app.state)
        elif cmd == "DONE":
            # Dismiss a finished run's report. The touchscreen has a DONE
            # button; the console had no equivalent, so a run that finished
            # with nobody present parked on the report screen indefinitely.
            if app.state == STATE_REPORT:
                app.state = STATE_IDLE
            print("# command DONE, state=%s" % app.state)
        elif cmd.startswith("PROFILE "):
            wanted = cmd[8:].strip().lower()
            match = None
            for pr in profiles:
                if wanted in pr.name.lower():
                    match = pr
                    break
            if match is None:
                print("# command PROFILE unknown %r; have: %s"
                      % (wanted, " | ".join(p.name for p in profiles)))
            elif app.state not in (STATE_IDLE, STATE_REPORT):
                print("# command PROFILE refused: oven is %s" % app.state)
            else:
                selected = match
                print("# command PROFILE selected: %s" % selected.name)
        elif cmd == "PROFILES":
            for pr in profiles:
                print("# profile %s%s" % (pr.name,
                                          " (selected)" if pr is selected else ""))
        elif cmd == "MEM":
            import gc
            gc.collect()
            from oven.ui.display import largest_free_block
            print("# mem free=%d largest=%s" % (gc.mem_free(),
                                                largest_free_block()))
        elif cmd == "STATUS":
            print("# status state=%s temp=%s target=%s relay=%d profile=%s"
                  % (app.state, app.temperature, app.target,
                     1 if hw.relay.is_on() else 0,
                     selected.name if selected else None))
        elif cmd:
            print("# unknown command %r" % cmd)

        if app.state in (STATE_RUNNING, STATE_COOLDOWN) and \
                app.temperature is not None:
            now = hw.clock.monotonic()
            if last_point[0] is None or now - last_point[0] >= HISTORY_INTERVAL_S:
                last_point[0] = now
                mark = app.elapsed if app.state == STATE_RUNNING else \
                    (history[-1][0] if history else 0.0) + HISTORY_INTERVAL_S
                history.append((mark, app.temperature))
        elif app.state in (STATE_IDLE, STATE_PREHEAT) and history:
            del history[:]
            last_point[0] = None

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
                               app.duty, hw.relay.is_on(),
                               history=history,
                               profile_points=app.profile.points
                               if app.profile else None,
                               duration_s=app.profile.duration
                               if app.profile else None)
        elif app.state == STATE_COOLDOWN:
            screen = L.open_the_door(app.temperature, cooling_rate())
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

        # Rendering at the control cadence rebuilds every label four times a
        # second for no benefit; 2 Hz is beyond what anyone reads and halves
        # the allocation churn.
        now_r = hw.clock.monotonic()
        if now_r - last_render[0] >= 0.5:
            last_render[0] = now_r
            display.render(screen)


try:
    main()
finally:
    # Whatever happens, stop heating. CircuitPython releases the pin on the
    # way out anyway and this oven's relay has a pulldown, but saying it
    # explicitly costs nothing.
    # Use the relay object that already owns the pin. Constructing a second
    # DigitalInOut on D4 raises "D4 in use" and the drive-low never happens --
    # which is exactly what occurred when the run crashed, leaving the
    # hardware pulldown as the only thing holding the relay off. It held, but
    # the belt-and-braces did not.
    try:
        if HARDWARE is not None:
            HARDWARE.relay.off()
            print("# relay driven low on exit")
        else:
            import digitalio
            _r = digitalio.DigitalInOut(board.D4)
            _r.direction = digitalio.Direction.OUTPUT
            _r.value = False
            print("# relay driven low on exit (fresh pin)")
    except Exception as e:
        print("# WARNING could not drive the relay low on exit (%r); the "
              "pulldown on D4 is now the only thing holding it off" % e)
