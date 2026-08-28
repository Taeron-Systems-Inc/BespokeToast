#!/usr/bin/env python3
"""Start a profile from the host, and supervise it from here as well.

The device already refuses unsafe conditions on its own -- that is the real
protection and it does not depend on this program, the serial link, or the
host staying alive. What this adds is a second, independent opinion: it
watches the same telemetry from outside and commands an abort if the run
stops making sense, and it will not begin at all unless pre-flight passes.

  python3 tools/start_run.py --check           pre-flight only, no heat
  python3 tools/start_run.py --confirmed-empty start and supervise

--confirmed-empty is required and is not a formality. Nothing here can see
inside the oven. Whether the cavity is empty and whether anything flammable
is nearby are human observations, and starting without them would be
pretending to a certainty this program does not have.
"""
import argparse
import re
import sys
import time

def _port():
    """The board's stable path, not a ttyACM number.

    Device numbering is not stable: a hard reset re-enumerated this board
    from ttyACM0 to ttyACM1, and every tool hardcoding ACM0 then failed to
    find a device that was sitting there working. The by-id path is keyed to
    the board UID and survives resets and replugs.
    """
    import glob
    found = sorted(glob.glob("/dev/serial/by-id/*PyPortal*"))
    if found:
        return found[0]
    found = sorted(glob.glob("/dev/ttyACM*"))
    return found[0] if found else "/dev/ttyACM0"


PORT = _port()
STATES = ("idle", "preheat", "running", "cooldown", "report", "fault")

# Pre-flight bounds. Deliberately tighter than the device's own limits: this
# decides whether to begin, and the device decides whether to continue.
MAX_START_OVEN_C = 45.0
MAX_START_ENCLOSURE_C = 45.0
MIN_START_OVEN_C = 5.0

# Host-side supervision.
ABORT_OVEN_C = 250.0          # device trips at 260
ABORT_ENCLOSURE_C = 68.0      # device trips at 70
SILENCE_ABORT_S = 15.0        # no telemetry for this long -> abort
MAX_RUN_S = 2400.0


def open_port():
    import serial
    return serial.Serial(PORT, 115200, timeout=0.5)


def parse(line):
    """Telemetry row -> dict, tolerant of the column set growing.

    It grew once already: adding the controller die temperature took the row
    from seven fields to eight, and a strict length check silently refused
    every pre-flight until it was noticed. Require the fields this needs and
    ignore any extra.
    """
    parts = line.strip().split(",")
    if len(parts) < 7 or parts[1] not in STATES:
        return None

    def num(v):
        try:
            return float(v)
        except ValueError:
            return None

    return {"t": num(parts[0]), "state": parts[1], "temp": num(parts[2]),
            "target": num(parts[3]), "duty": num(parts[4]),
            "relay": parts[5] == "1", "cold": num(parts[6]),
            "cpu": num(parts[7]) if len(parts) > 7 else None}


RAW = [None]


def listen(s, seconds, on_row=None):
    """Collect telemetry, and keep a verbatim copy of everything else.

    Filtering to recognised rows discards tracebacks, which are precisely
    what is wanted when a run stops. That happened twice: a crash on run
    start, and a run dying in cooldown, both diagnosable only by reproducing
    them afterwards.
    """
    buf, rows, end = "", [], time.monotonic() + seconds
    while time.monotonic() < end:
        chunk = s.read(512).decode("utf-8", "replace")
        if chunk and RAW[0]:
            RAW[0].write(chunk)
            RAW[0].flush()
        buf += chunk
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = re.sub(r"\x1b?\]0;[^\\]*\\", "", line)
            row = parse(line)
            if row:
                rows.append(row)
                if on_row:
                    on_row(row)
            elif line.strip().startswith("#"):
                print("   dev: %s" % line.strip()[:110])
    return rows


def preflight(s):
    print("[pre-flight]")
    rows = listen(s, 6.0)
    if not rows:
        return ["no telemetry: the firmware is not running or the port is busy"]
    last = rows[-1]
    problems = []
    if last["state"] != "idle":
        problems.append("device is %s, not idle" % last["state"])
    if last["relay"]:
        problems.append("relay is already energised")
    if last["temp"] is None:
        problems.append("no temperature reading")
    else:
        if not (MIN_START_OVEN_C <= last["temp"] <= MAX_START_OVEN_C):
            problems.append("oven at %.1f C, want %.0f-%.0f"
                            % (last["temp"], MIN_START_OVEN_C, MAX_START_OVEN_C))
    if last["cold"] is not None and last["cold"] > MAX_START_ENCLOSURE_C:
        problems.append("enclosure at %.1f C, want below %.0f -- it rises about "
                        "21 C during a run and peaks after it"
                        % (last["cold"], MAX_START_ENCLOSURE_C))
    # the reading must be alive, not stuck
    temps = {r["temp"] for r in rows if r["temp"] is not None}
    if len(temps) == 1 and len(rows) > 12:
        problems.append("temperature has not changed in %d samples; the probe "
                        "may not be reading" % len(rows))
    print("   oven %.1f C, cold-junction %.1f C, controller die %.1f C, "
          "state %s, relay %s, %d samples"
          % (last["temp"] or -1, last["cold"] or -1, last["cpu"] or -1,
             last["state"], "on" if last["relay"] else "off", len(rows)))
    return problems


def command(s, text, wait=2.0):
    """Send a console command and collect what the firmware says back."""
    s.write((text + "\r\n").encode())
    s.flush()
    out, end = [], time.monotonic() + wait
    buf = ""
    while time.monotonic() < end:
        buf += s.read(1024).decode("utf-8", "replace")
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = re.sub(r"\x1b?\]0;[^\\]*\\", "", line).strip()
            if line.startswith("#"):
                out.append(line)
    return out


def supervise(s, log_path):
    """Watch the run from outside and abort if it stops making sense.

    The device's own guards are the real protection and do not depend on any
    of this. These are a second opinion with different failure modes: they
    catch a device that has stopped talking, which the device by definition
    cannot.
    """
    started = time.monotonic()
    last_seen = [time.monotonic()]
    peak = [0.0]
    if RAW[0] is None:
        RAW[0] = open(log_path.replace(".csv", "_raw.log"), "w")
    log = open(log_path, "w")
    log.write("t,state,temp_c,target_c,duty,relay,cold_c,cpu_c\n")

    def on_row(r):
        last_seen[0] = time.monotonic()
        if r["temp"] is not None:
            peak[0] = max(peak[0], r["temp"])
        log.write("%s,%s,%s,%s,%s,%d,%s,%s\n" % (
            r["t"], r["state"], r["temp"], r["target"], r["duty"],
            1 if r["relay"] else 0, r["cold"], r["cpu"]))
        log.flush()

    state = "unknown"
    while True:
        rows = listen(s, 2.0, on_row)
        now = time.monotonic()
        if rows:
            last = rows[-1]
            state = last["state"]
            if last["temp"] is not None and last["temp"] >= ABORT_OVEN_C:
                return abort(s, "oven reached %.1f C" % last["temp"]), peak[0]
            if last["cold"] is not None and last["cold"] >= ABORT_ENCLOSURE_C:
                return abort(s, "enclosure reached %.1f C" % last["cold"]), peak[0]
            if state in ("report", "idle") and now - started > 60:
                print("[done] run finished cleanly, state=%s" % state)
                return None, peak[0]
            if state == "fault":
                print("[fault] the device faulted and latched; heat is off")
                return None, peak[0]
            print("   %-8s %6.1f C  target %-6s relay %s"
                  % (state, last["temp"] or -1,
                     ("%.0f" % last["target"]) if last["target"] else "-",
                     "ON " if last["relay"] else "off"))
        if now - last_seen[0] > SILENCE_ABORT_S:
            return abort(s, "no telemetry for %.0f s" % (now - last_seen[0])), peak[0]
        if now - started > MAX_RUN_S:
            return abort(s, "host timeout at %.0f s" % (now - started)), peak[0]


def abort(s, why):
    print("!! ABORT: %s" % why)
    # Ask nicely first: the firmware's own abort cuts heat and moves to
    # cooldown, which is tidier than yanking it into the REPL.
    for line in command(s, "ABORT", wait=2.0):
        print("   %s" % line)
    for _ in range(3):
        s.write(b"\x03")
        s.flush()
        time.sleep(0.3)
    s.read(8192)
    s.write(b"\x01")
    s.flush()
    time.sleep(0.6)
    s.read(8192)
    s.write(b"import board, digitalio\r\n"
            b"_r = digitalio.DigitalInOut(board.D4)\r\n"
            b"_r.direction = digitalio.Direction.OUTPUT\r\n"
            b"_r.value = False\r\n"
            b"print('RELAY-LOW')\r\n\x04")
    s.flush()
    time.sleep(1.5)
    print("   %s" % s.read(4096).decode("utf-8", "replace").strip()[-60:])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--confirmed-empty", action="store_true")
    args = ap.parse_args(argv[1:])

    s = open_port()
    if RAW[0] is None:
        RAW[0] = open("/tmp/claude-1001/-home-kaan/"
                      "e3791a80-a239-41f2-9f58-11ee423d796e/scratchpad/"
                      "session_raw.log", "a")
    try:
        problems = preflight(s)
        if problems:
            for p in problems:
                print("   !! %s" % p)
            print("[refused]")
            return 1
        print("   pre-flight clear")
        if args.check:
            print("[check only, nothing started]")
            return 0
        if not args.confirmed_empty:
            print("!! --confirmed-empty is required. Nothing here can see "
                  "inside the oven.")
            return 2
        print("[start] issuing START")
        for line in command(s, "START", wait=3.0):
            print("   %s" % line)
        log_path = "/tmp/claude-1001/-home-kaan/" \
                   "e3791a80-a239-41f2-9f58-11ee423d796e/scratchpad/" \
                   "supervised_run.csv"
        _, peak = supervise(s, log_path)
        print("[end] peak %.1f C, log at %s" % (peak, log_path))
        return 0
    finally:
        s.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
