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


STATES = ("idle", "preheat", "running", "cooldown", "report", "fault")


def resolve_port(port=None):
    """Find the PyPortal by its stable by-id name.

    /dev/ttyACM0 is not stable: a hard reset moved the board to ttyACM1 and
    every tool that had the number baked in stopped working at once. The
    by-id symlink is tied to the board's serial number instead.
    """
    if port:
        return port
    import glob
    found = sorted(glob.glob("/dev/serial/by-id/*PyPortal*"))
    return found[0] if found else "/dev/ttyACM0"


def running_check(dest, port=None, listen_s=6.0):
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
    port = resolve_port(port)
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
                    # Keyed on the state name, NOT on len(parts): this
                    # check was written against a 7-field row, then cpu_c was
                    # added and it silently matched nothing ever again. It
                    # failed closed, so nothing burned -- but a guard that
                    # always says "cannot confirm" is a guard you learn to
                    # bypass, which is how it would have killed a run.
                    if len(parts) >= 6 and parts[1] in STATES:
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



def claim_volume_for_the_host(port=None, mount=None, wait_s=30.0):
    """If the oven owns the filesystem, take it back and reset.

    In standalone mode the oven has write access and the host's volume is
    read-only, so a deploy simply cannot write. That is the correct state
    for the oven to be in when it is running on its own -- it is how it
    records a run -- but it is useless for programming.

    Rather than leave someone staring at "Read-only file system", this sets
    the boot mode over the serial console and hard-resets the board. Serial
    is always available when a cable is attached, which is exactly when a
    deploy is happening. Two lock-outs were rescued by hand this way before
    it was automated.
    """
    try:
        import serial
    except ImportError:
        return "pyserial is not installed, so the volume cannot be reclaimed"
    port = resolve_port(port)
    script = (
        "import microcontroller\r\n"
        "microcontroller.nvm[0:2] = bytearray((0x7E, 0xA5))\r\n"
        "import microcontroller; microcontroller.reset()\r\n"
    )
    # Opening the port often fails with EIO on the first try, especially
    # just after the board has re-enumerated. Every manual recovery needed
    # two or three attempts, so this does the same rather than reporting a
    # wall on the first refusal.
    handle = None
    last = None
    for attempt in range(4):
        try:
            handle = serial.Serial(port, 115200, timeout=0.5)
            break
        except Exception as e:
            last = e
            time.sleep(3)
    if handle is None:
        return "could not reach %s after 4 attempts (%r)" % (port, last)
    try:
        time.sleep(1.0)
        for _ in range(3):
            handle.write(b"\x03")
            time.sleep(0.4)
        handle.read(800)
        for line in script.strip().split("\r\n"):
            handle.write((line + "\r\n").encode())
            time.sleep(0.3)
        handle.flush()
    except Exception as e:
        return "could not reclaim over %s (%r)" % (port, e)
    finally:
        try:
            handle.close()
        except Exception:
            pass
    # The board reboots and re-enumerates; the volume comes back writable.
    time.sleep(wait_s)
    return None


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    dest = argv[1]
    dry = "--dry-run" in argv

    if not os.path.isdir(dest):
        print("!! %s is not mounted" % dest)
        return 1
    # A mount left pointing at a stale device node reads as an EMPTY
    # DIRECTORY. The board re-enumerates across hard resets -- sda to sdb and
    # back -- so a deploy can report success while writing nowhere near the
    # device. Refuse rather than write into the void.
    if not os.listdir(dest):
        print("!! %s is empty. The volume is probably mounted from a stale" % dest)
        print("   device node. Remount by label:")
        print("     sudo umount %s && sudo mount -o ro $(blkid -L CIRCUITPY) %s"
              % (dest, dest))
        return 1
    if not os.path.exists(os.path.join(dest, "boot_out.txt")):
        print("!! %s has no boot_out.txt -- this does not look like a "
              "CIRCUITPY volume" % dest)
        return 1
    if not dry and not os.access(dest, os.W_OK):
        # Most likely the oven owns the filesystem, which is correct when it
        # is running standalone and useless for programming. Take it back
        # over serial rather than reporting a wall.
        print(".. %s is read-only; the oven probably owns it. Reclaiming "
              "over serial and resetting the board." % dest)
        problem = claim_volume_for_the_host()
        if problem:
            print("!! could not reclaim the volume: %s" % problem)
            print("   the oven holds the filesystem while it is standalone. "
                  "Set it back by hand over the REPL:")
            print("     import microcontroller")
            print("     microcontroller.nvm[0:2] = bytearray((0x7E, 0xA5))")
            print("     microcontroller.reset()")
            return 1
        print(".. remount the volume and run this again:")
        print("     sudo umount %s; sudo mount -o rw,uid=$(id -u) "
              "$(blkid -L CIRCUITPY) %s" % (dest, dest))
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
