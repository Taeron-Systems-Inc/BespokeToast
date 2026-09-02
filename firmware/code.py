# SPDX-License-Identifier: MIT
"""BespokeToast entry point.

Assembles the hardware, wires the application to the interface, and runs the
loop. Deliberately thin: everything that decides anything lives in oven/,
where it can be tested without a board.
"""

import gc
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
from oven.history import History
from oven.metrics import Limits as MetricLimits
from oven.profile import Profile, scan as scan_profiles
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


def remember_boot_mode():
    """Record, for the next boot, whether a host is attached.

    boot.py cannot tell -- usb_connected reads False there because
    CircuitPython starts USB afterwards. Here it is reliable, so the answer
    is written to non-volatile memory, which does not care who owns the
    filesystem. The cost is a boot of lag after the cable changes; the
    alternative was locking the host out of its own volume, which happened
    twice before this existed.
    """
    try:
        import microcontroller
        from oven.bootmode import HOST, STANDALONE, decode, encode, name
        seen = HOST if supervisor.runtime.usb_connected else STANDALONE
        if decode(microcontroller.nvm) != seen:
            microcontroller.nvm[0:2] = encode(seen)
            print("# boot mode recorded as %s; it takes effect on the next "
                  "hard reset" % name(seen))
    except Exception as e:
        print("# WARNING could not record the boot mode (%r); the oven may "
              "not be able to log its next run" % e)


def set_rtc(epoch_seconds):
    """Put the network's answer into the board's own clock, then start over.

    The reload is the point. Importing the WiFi stack costs 7280 bytes
    measured, and sys.modules holds that for the life of the program even
    after the connection is dropped -- 22% of a heap that then has to build
    a run screen. It showed immediately: on the boot that first synced the
    clock, the font metrics failed to load and every button label fell back
    to being centred by estimate.

    Deleting the modules by hand did not give it back; it made things
    worse, 25392 free becoming 11472. So instead the clock is written to
    the RTC and the program restarts. The next pass sees a clock that is
    already set, never imports the radio at all, and runs with the full
    heap. It costs one extra boot per power cycle, and nothing per run.
    """
    try:
        import rtc
        import time as _time
        rtc.RTC().datetime = _time.localtime(epoch_seconds)
    except Exception as e:
        print("# clock: could not set the RTC (%r); the time will not "
              "survive this restart" % e)
        return False
    print("# clock: set; restarting so the run gets its memory back")
    try:
        supervisor.reload()
    except Exception as e:
        print("# clock: could not restart (%r); continuing with the radio "
              "still resident" % e)
        return False
    return True


def now_iso():
    """The current UTC time as a sortable stamp, or None if unknown.

    Reads the RTC rather than anything sync_clock returned. sync_clock
    returns None in the ordinary case -- when the clock is already set and
    the radio is deliberately not touched -- so relying on its return value
    put "monotonic+" in the header of every log except the first after a
    power cut, which is exactly backwards.
    """
    try:
        import rtc
        import time as _time
        from oven import timesync
        now = rtc.RTC().datetime
        if now.tm_year < 2025:
            return None
        return timesync.iso(_time.mktime(now))
    except Exception as e:
        print("# clock: cannot read the time (%r)" % e)
        return None


def clock_is_set():
    """Whether this board already knows the date.

    CircuitPython's RTC keeps running as long as the board has power, and
    this oven is powered continuously -- USB carries 5 V from an internal
    converter even with no data host. So the clock survives soft resets and
    auto-reloads, and only a power cut clears it.
    """
    try:
        import rtc
        from oven import timesync
        now = rtc.RTC().datetime
        return now.tm_year >= 2025
    except Exception as e:
        # No rtc module, or it has never been set. Either way the answer is
        # "no", and the caller will go and ask the network.
        print("# clock: not set (%r)" % e)
        return False


def sync_clock():
    """Ask the network what time it is, once, at boot.

    The oven has no battery-backed clock, so every run it records is
    otherwise stamped with seconds since boot -- enough to plot a run
    against itself, useless for saying which run it was.

    Only at boot, and only here: the radio needs about 18 kB and the oven
    has roughly 16 kB free once a run is on screen, so it cannot come up
    mid-run. Nothing about the run depends on this succeeding.

    Returns the epoch seconds at boot, or None. Callers add uptime.
    """
    if clock_is_set():
        return None            # already known; do not pay for the radio

    try:
        from oven import netconfig
        from oven.radio import Radio
    except Exception as e:
        print("# clock: no networking available (%r)" % e)
        return None

    networks = netconfig.load()
    if not networks:
        return None
    if not netconfig.may_connect("idle", heating=False):
        return None

    radio = Radio()
    try:
        chosen = netconfig.choose(networks, radio.scan())
        if chosen is None:
            print("# clock: none of the known networks are in range")
            return None
        if not radio.connect(chosen):
            return None
        print("# clock: joined %s as %s" % (chosen.ssid, radio.ip))
        now = radio.utc_now()
        if now is None:
            return None
        from oven import timesync
        print("# clock: %s UTC" % timesync.iso(now))
        set_rtc(now)
        return now
    finally:
        # The connection goes away either way. Holding a socket open for
        # the life of a run is exactly the memory this cannot spare.
        radio.close()


def storage_is_writable():
    """Can the device write to its own filesystem?

    Only when CIRCUITPY is not mounted writable by a host. Asking directly is
    better than assuming: the answer decides whether runs are recorded, and a
    silent no would look exactly like a logging bug later.
    """
    probe = "/.write-probe"
    try:
        with open(probe, "w") as f:
            f.write("x")
        os.remove(probe)
        return True
    except OSError:
        return False


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
    """Catalogue the profiles without keeping them.

    Each file is parsed and validated here, so a broken profile is reported
    at boot rather than when someone presses START with a board in the oven
    -- but only the name and a couple of flags are retained. Holding all ten
    cost 24 kB of a heap with about 180 kB in it, measured on the device,
    for nine profiles nobody had selected.
    """
    return scan_profiles(PROFILE_DIR)


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

    # Run logging. CircuitPython can only write to CIRCUITPY when the volume
    # is NOT writable over USB, which is the opposite of what a development
    # machine wants, so on a bench-connected board this is unavailable.
    #
    # Imported only when it can be used: the module costs 5.9 kB of a heap
    # that has about 22 kB to give, and paying that for a feature that is
    # switched off is how the display ran out of memory in the first place.
    log_writable = storage_is_writable()
    remember_boot_mode()
    logs = None
    LOG_INTERVAL_S = 1.0
    if log_writable:
        from oven.logstore import LogStore, INTERVAL_S as LOG_INTERVAL_S
        logs = LogStore()

    data = load_characterisation()
    have_characterisation = data is not None
    if data:
        ff = FeedForward(heating_rates=data.get("heating_rate_c_per_s"),
                         cooling_rates=data.get("cooling_rate_c_per_s"))
        coast = data.get("coast_tau_s", 1.2)
        # Drop the parsed JSON. FeedForward has packed the curves into
        # array('f'); holding the dict as well keeps the original lists of
        # [temperature, rate] pairs alive for the life of the run, which is
        # the 7 kB the packing was meant to recover. Measured: free went
        # DOWN, from 30352 to 27056, until this line existed.
        data = None
        gc.collect()
    else:
        ff = FeedForward()
        coast = 1.2

    profiles = load_profiles()
    # Alphabetical order would select "4900P (as run)", which measurement
    # shows this oven cannot follow. A profile may declare itself the default.
    chosen = None
    for ref in profiles:
        if ref.is_default:
            chosen = ref
            break
    if chosen is None and profiles:
        chosen = profiles[0]

    # Exactly one profile is resident at a time: the one that is selected.
    selected_ref = [chosen]
    selected_profile = [None]

    def selected():
        """The loaded profile for the current selection, read on demand."""
        if selected_profile[0] is None and selected_ref[0] is not None:
            try:
                selected_profile[0] = selected_ref[0].load()
            except Exception as e:
                print("# WARNING could not load %s (%r)"
                      % (selected_ref[0].name, e))
                return None
        return selected_profile[0]

    def select(ref):
        selected_ref[0] = ref
        selected_profile[0] = None
        gc.collect()

    display.render(L.splash(VERSION))
    time.sleep(1.2)

    reading = hw.sensor.read()
    display.render(L.self_test([
        ("thermocouple", reading is not None and reading.ok),
        ("relay safe state", not hw.relay.is_on()),
        ("profiles", bool(profiles)),
        ("characterisation", have_characterisation),
        ("run logging", log_writable),
    ]))
    if not log_writable:
        print("# run logging unavailable: CIRCUITPY is writable over USB, so "
              "the device cannot write to it. Serial telemetry is unaffected.")
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
    memory_failures = {}

    def note_memory_failure(where):
        """Count a memory failure, and say so without making it worse.

        Printing on every failure allocates, which is precisely what is
        already failing, so this reports on a widening schedule. The totals
        are available from MEM and are printed at the end of a run.
        """
        n = memory_failures.get(where, 0) + 1
        memory_failures[where] = n
        if n in (1, 10, 100, 1000):
            print("# WARNING %s ran out of memory %d time(s); the display "
                  "may be stale, the run is not affected" % (where, n))

    last_log = [0.0]
    logging_run = [False]

    def begin_log(profile):
        if logs is None:
            return
        stamp = now_iso() or ("monotonic+%.0f" % hw.clock.monotonic())
        path = logs.begin(profile.name, VERSION, stamp)
        logging_run[0] = path is not None
        last_log[0] = 0.0
        if path:
            print("# recording this run to %s" % path)

    def end_log():
        if logging_run[0] and logs is not None:
            summary = None
            if app.metrics:
                summary = "peak=%.1f tal=%.0f" % (app.metrics.peak_c,
                                                  app.metrics.time_above_liquidus)
            logs.end(summary)
            logging_run[0] = False

    sync_clock()          # sets the RTC if it is not already set

    print("# t,state,temp_c,target_c,duty,relay,cold_c,cpu_c")

    def emit(row):
        # Formatting and printing a row allocates. Losing a telemetry line
        # is nothing; losing the run because of one is not acceptable.
        try:
            _emit(row)
        except MemoryError:
            gc.collect()
            note_memory_failure("printing telemetry")

    def _emit(row):
        cpu = cpu_temperature()
        # One row a second on the device against four a second on the wire:
        # nothing in a reflow profile moves faster than a second, and it
        # quarters what the flash has to hold.
        if logging_run[0] and row["t"] - last_log[0] >= LOG_INTERVAL_S:
            last_log[0] = row["t"]
            logs.write(row["t"], row["target"], row["temp"], row["relay"],
                       row["cold"], cpu)
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
    # pixels wide, and History is bounded: past its limit it halves its own
    # resolution instead of growing. This was a plain list, and growing it
    # killed a run at 90 C with the relay at full duty -- the allocation that
    # failed was 256 bytes.
    history = History(max_points=150, interval_s=2.0)

    def cooling_rate():
        if len(history) < 4:
            return None
        pts = history.points
        (t0, v0), (t1, v1) = pts[-4], pts[-1]
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

    previous_state = [app.state]

    while True:
        app.tick()

        # A run has ended when it leaves the states that heat or cool. The
        # log is closed here rather than on an event so that an abort, a
        # fault and a normal finish all go through one path.
        if app.state != previous_state[0]:
            if previous_state[0] in (STATE_PREHEAT, STATE_RUNNING,
                                     STATE_COOLDOWN) and \
                    app.state in (STATE_REPORT, STATE_FAULT, STATE_IDLE):
                end_log()
            previous_state[0] = app.state

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
            profile = selected()
            problem = app.request_start(profile) if profile else None
            if profile is None:
                print("# command START refused: no profile")
            elif problem is not None:
                print("# command START refused: %s" % problem.message)
            else:
                print("# command START accepted: %s" % profile.name)
                begin_log(profile)
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
                select(match)
                print("# command PROFILE selected: %s" % match.name)
        elif cmd == "PROFILES":
            for pr in profiles:
                print("# profile %s%s"
                      % (pr.name,
                         " (selected)" if pr is selected_ref[0] else ""))
        elif cmd == "MEM":
            # No "import gc" here: gc is imported at module scope, and a
            # local import would make the name local to the whole of main(),
            # so every other gc.collect() in this function -- including the
            # ones in the MemoryError guards and in select() -- would raise
            # NameError instead of collecting. That is exactly what happened.
            gc.collect()
            from oven.ui.display import largest_free_block
            print("# mem free=%d largest=%s memory_failures=%s"
                  % (gc.mem_free(), largest_free_block(),
                     memory_failures or "none"))
        elif cmd == "STATUS":
            print("# status state=%s temp=%s target=%s relay=%d profile=%s"
                  % (app.state, app.temperature, app.target,
                     1 if hw.relay.is_on() else 0,
                     selected_ref[0].name if selected_ref[0] else None))
        elif cmd:
            print("# unknown command %r" % cmd)

        if app.state in (STATE_RUNNING, STATE_COOLDOWN) and \
                app.temperature is not None:
            now = hw.clock.monotonic()
            # During cooldown the run clock has stopped, so the trace is
            # continued on its own axis rather than restarting at zero.
            mark = app.elapsed if app.state == STATE_RUNNING else now
            # This is the line a run died on. History is bounded now, but a
            # bounded buffer still allocates a tuple per sample, and a chart
            # point is never worth a run.
            try:
                history.add(mark, app.temperature)
            except MemoryError:
                gc.collect()
                note_memory_failure("recording a chart point")
        elif app.state in (STATE_IDLE, STATE_PREHEAT) and len(history):
            history.clear()

        # Touch is polled outside the control step: a press must not be able
        # to delay a control step, and a missed press is merely annoying.
        point = hw.touch.press()
        if point is not None:
            action = L.hit(screen, point[0], point[1])
            if action == "start" and selected_ref[0] is not None:
                # A run started here is the one most likely to have nobody
                # watching it, so it is the one that most needs recording.
                profile = selected()
                problem = app.request_start(profile) if profile else None
                if problem is not None:
                    print("# start refused: %s" % problem.message)
                elif profile is not None:
                    begin_log(profile)
            elif action == "abort":
                app.abort()
            elif action == "acknowledge":
                app.acknowledge_fault()
            elif action == "done":
                app.state = STATE_IDLE
            elif action == "profiles" and profiles:
                if selected_ref[0] in profiles:
                    nxt = (profiles.index(selected_ref[0]) + 1) % len(profiles)
                else:
                    nxt = 0
                select(profiles[nxt])

        # Composing a screen allocates, and the heap late in a run has no
        # large holes left. A MemoryError here used to propagate out of
        # main() and stop the firmware: the exit handler drove the relay
        # low, so it failed safe, but the oven stopped controlling and
        # stopped answering ABORT. The display is never worth a run -- on
        # failure the previous screen simply stays up.
        try:
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
                                   history=history.points,
                                   profile_points=app.profile.points
                                   if app.profile else None,
                                   duration_s=app.profile.duration
                                   if app.profile else None,
                                   open_the_door=app.door_prompted)
            elif app.state == STATE_COOLDOWN:
                screen = L.open_the_door(app.temperature, cooling_rate())
            elif app.state == STATE_REPORT and app.metrics and app.profile:
                screen = L.report(app.metrics.check(
                    MetricLimits.for_profile(app.profile)),
                    app.metrics.peak_c, app.metrics.time_above_liquidus)
            else:
                ready = app.temperature is not None and app.temperature < 60.0
                screen = L.home(app.temperature,
                                selected_ref[0].name if selected_ref[0] else None,
                                ready and selected_ref[0] is not None,
                                None if ready else "oven too hot to start")
        except MemoryError:
            gc.collect()
            note_memory_failure("composing a screen")

        # Rendering at the control cadence rebuilds every label four times a
        # second for no benefit; 2 Hz is beyond what anyone reads and halves
        # the allocation churn.
        now_r = hw.clock.monotonic()
        if now_r - last_render[0] >= 0.5:
            last_render[0] = now_r
            try:
                display.render(screen)
            except MemoryError:
                gc.collect()
                note_memory_failure("drawing the screen")


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
