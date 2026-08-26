#!/usr/bin/env python3
"""Deploy firmware/ to the PyPortal's CIRCUITPY volume.

Refuses to deploy while the oven is running. Writing any file to CIRCUITPY
triggers CircuitPython's auto-reload, which restarts the controller
mid-profile -- with a relay that fails safe, that means the heat stops and
the board is half-soldered, which is a wasted board rather than a fire, but
it is still not something to do by accident.

  python3 tools/deploy.py /mnt/circuitpy            # copy, then verify
  python3 tools/deploy.py /mnt/circuitpy --dry-run
  python3 tools/deploy.py /mnt/circuitpy --force    # deploy anyway (do not)
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "firmware")
CHARACTERISATION = os.path.join(ROOT, "data", "oven-characterisation.json")

SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIX = (".pyc",)


def digest(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def files():
    for base, dirs, names in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in sorted(names):
            if n.endswith(SKIP_SUFFIX):
                continue
            full = os.path.join(base, n)
            yield full, os.path.relpath(full, SRC)


def running_check(dest, port="/dev/ttyACM0", listen_s=3.0):
    """Ask the DEVICE whether it is mid-run, and refuse to deploy if it is.

    The firmware prints a CSV line every control step whose second field is
    the run state, so listening for a few seconds is a direct answer rather
    than an inference.

    This exists because a file-existence check was not enough. Deploying
    rewrites code.py, which soft-reboots the board: doing that during a
    profile aborts the run. It happened -- twice I said I would not deploy
    mid-run and then did, once into a run that was already at 160 C. Relying
    on remembering is what failed, so the check is mechanical now.

    A device that says nothing is treated as unknown, not as idle.
    """
    try:
        import serial
    except ImportError:
        return None                    # cannot check; caller decides
    busy = ("running", "preheat", "cooldown")
    try:
        with serial.Serial(port, 115200, timeout=0.5) as s:
            buf = ""
            end = time.monotonic() + listen_s
            seen = None
            while time.monotonic() < end:
                buf += s.read(512).decode("utf-8", "replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    parts = line.strip().split(",")
                    if len(parts) == 7:
                        seen = parts[1]
            if seen is None:
                return ("no telemetry from %s in %.0f s -- cannot confirm the "
                        "oven is idle" % (port, listen_s))
            if seen in busy:
                return "the oven is %s; deploying would abort it" % seen
            return None
    except Exception as e:
        return "could not read %s (%r) -- cannot confirm the oven is idle" % (
            port, e)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    dest = argv[1]
    dry = "--dry-run" in argv

    if not os.path.isdir(dest):
        print("!! %s is not mounted" % dest)
        return 1
    if not dry and not os.access(dest, os.W_OK):
        print("!! %s is read-only. Remount it writable to deploy." % dest)
        return 1

    blocked = running_check(dest)
    if blocked and "--force" not in argv:
        print("!! refusing to deploy: %s" % blocked)
        print("   deploying rewrites code.py, which soft-reboots the board and")
        print("   aborts whatever it was doing. Wait, or pass --force.")
        return 1
    if blocked:
        print("!! WARNING deploying anyway despite: %s" % blocked)

    planned = list(files())
    if os.path.exists(CHARACTERISATION):
        planned.append((CHARACTERISATION, "characterisation.json"))

    changed = []
    for src, rel in planned:
        dst = os.path.join(dest, rel)
        if not os.path.exists(dst) or digest(src) != digest(dst):
            changed.append((src, rel))

    print("  %d files, %d changed" % (len(planned), len(changed)))
    for _, rel in changed:
        print("    %s" % rel)
    if dry:
        print("  (dry run, nothing written)")
        return 0
    if not changed:
        print("  nothing to do")
        return 0

    for src, rel in changed:
        dst = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    bad = [rel for src, rel in changed
           if digest(src) != digest(os.path.join(dest, rel))]
    if bad:
        print("!! verification failed for: %s" % ", ".join(bad))
        return 1
    print("  deployed and verified; the board will auto-reload")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
