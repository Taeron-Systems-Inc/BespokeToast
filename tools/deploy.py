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


# Directories the repository owns completely, where a file the repository
# does not have is a file that should not be on the board.
#
# profiles/ is the one that matters. Deploy copies and never removed, so
# cutting the shipped set from ten profiles to five left all ten on the
# board -- and a stale profile is not inert, it is offered to whoever is
# choosing one. Sn63Pb37 for a paste nobody stocks, and Hold 150 C, which
# sits above the liquidus of both low-temp pastes.
def frozen_imports(path):
    """(module, name) pairs code.py imports from oven/.

    On a frozen board these names come out of the firmware image, not off
    the volume, so a deploy cannot supply one that is missing. Adding a
    function to oven/ and deploying only code.py leaves the board unable
    to boot: it stops at "ImportError: cannot import name ..." before it
    prints anything, which reads like a dead board rather than a mismatch.
    That happened, and the reason it was not caught here is that every
    check ran against the repository, which had the new name in it.
    """
    import ast
    wanted = []
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("oven"):
            for a in node.names:
                wanted.append((node.module, a.name))
    return wanted


def missing_on_board(pairs, port=None, settle_s=1.0):
    """Names the board's own firmware cannot provide. Asks the board.

    The board is the only thing that knows what was flashed into it. The
    repository does not, and neither does anything else here.
    """
    try:
        import serial
    except ImportError:
        return []
    by_module = {}
    for mod, name in pairs:
        by_module.setdefault(mod, []).append(name)
    try:
        handle = serial.Serial(resolve_port(port), 115200, timeout=0.5)
    except Exception:
        return []
    missing = []
    try:
        for _ in range(3):
            handle.write(b"\x03")
            time.sleep(0.3)
        time.sleep(settle_s)
        handle.read(4000)
        for mod, names in sorted(by_module.items()):
            line = "from %s import %s\r\n" % (mod, ", ".join(sorted(set(names))))
            handle.write(line.encode())
            handle.flush()
            time.sleep(0.6)
            reply = handle.read(4000).decode("utf-8", "replace")
            if "Error" in reply:
                said = [ln.strip() for ln in reply.split("\n")
                        if "Error" in ln]
                missing.append((mod, sorted(set(names)),
                                said[-1] if said else reply.strip()))
    except Exception:
        return []
    finally:
        try:
            handle.write(b"\x04")      # leave it running again
            handle.close()
        except Exception:
            pass
    return missing


OWNED_DIRS = ("profiles",)


def stale(dest):
    """Files under an owned directory that the repository no longer has."""
    gone = []
    have = set(rel for _full, rel in files())
    for owned in OWNED_DIRS:
        there = os.path.join(dest, owned)
        if not os.path.isdir(there):
            continue
        for n in sorted(os.listdir(there)):
            rel = owned + "/" + n
            if rel not in have and not n.startswith("."):
                gone.append(rel)
    return gone


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


# Libraries this firmware carries frozen in flash. A copy of any of these on
# CIRCUITPY is loaded into RAM instead of executed from flash, for no
# benefit -- and the cost is not small. Measured on this board: importing
# adafruit_esp32spi cost 16064 bytes from a .mpy on the filesystem and 16
# bytes frozen, and a whole connected WiFi session went from 22592 bytes to
# 1872. Idle free memory went from 29376 to 36032 simply by moving them out
# of the way.
#
# They arrive by accident: installing the Adafruit bundle drops them in.
FROZEN_IN_FIRMWARE = (
    "adafruit_display_text",
    "adafruit_esp32spi",
    "adafruit_bus_device",
    "adafruit_portalbase",
    "adafruit_requests.mpy",
    "adafruit_requests.py",
    "neopixel.mpy",
    "neopixel.py",
)


def shadowing_frozen_libraries(dest):
    """Names on the volume that shadow something already frozen in flash."""
    return [n for n in FROZEN_IN_FIRMWARE
            if os.path.exists(os.path.join(dest, n))]


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

    shadowed = shadowing_frozen_libraries(dest)
    if shadowed:
        print("!! %s carries copies of libraries this firmware already has"
              % dest)
        print("   frozen in flash. A copy on the filesystem SHADOWS the")
        print("   frozen one and is loaded into RAM instead:")
        for name in shadowed:
            print("     %s" % name)
        print("   Measured: the whole connected WiFi stack costs 1872 bytes")
        print("   frozen and 22592 bytes shadowed. Move them aside:")
        print("     mkdir -p %s/.shadowed && mv %s/{%s} %s/.shadowed/"
              % (dest, dest, ",".join(shadowed), dest))
        if "--force" not in argv:
            return 1

    blocked = running_check(dest)
    if blocked and "--force" not in argv:
        print("!! refusing to deploy: %s" % blocked)
        print("   deploying rewrites code.py, which soft-reboots the board and")
        print("   aborts whatever it was doing. Wait, or pass --force.")
        return 1
    if blocked:
        print("!! WARNING deploying anyway despite: %s" % blocked)

    # When the oven package is frozen into the firmware there must be no
    # copy on the volume: a filesystem copy shadows the frozen one and puts
    # ~48 kB of bytecode back into a 256 kB RAM. Deploying it would silently
    # undo the flash, and everything would still work -- just with a third
    # of the memory.
    frozen_build = not os.path.isdir(os.path.join(dest, "oven"))
    planned = [(src, rel) for src, rel in files()
               if not (frozen_build and rel.startswith("oven/"))]
    if frozen_build:
        skipped = len(list(files())) - len(planned)
        print(".. this board runs a frozen build: skipping %d file(s) under"
              % skipped)
        print("   oven/. Changes to them need a rebuild and a reflash, not a")
        print("   deploy -- see docs/frozen-build.md.")
        gaps = missing_on_board(frozen_imports(os.path.join(SRC, "code.py")))
        if gaps:
            print("!! this code.py imports names the flashed firmware does "
                  "not have:")
            for mod, names, err in gaps:
                print("   from %s import %s" % (mod, ", ".join(names)))
                print("     board says: %s" % err)
            print("   Deploying it would leave the board unable to boot.")
            print("   Rebuild and reflash first: tools/release.py --flash")
            return 1

    if os.path.exists(CHARACTERISATION):
        planned.append((CHARACTERISATION, "characterisation.json"))

    changed = []
    for src, rel in planned:
        dst = os.path.join(dest, rel)
        if not os.path.exists(dst) or digest(src) != digest(dst):
            changed.append((src, rel))

    orphans = stale(dest)
    print("  %d files, %d changed" % (len(planned), len(changed)))
    for _, rel in changed:
        print("    %s" % rel)
    for rel in orphans:
        print("    %s (no longer in the repository -- will be removed)" % rel)
    if dry:
        print("  (dry run, nothing written)")
        return 0
    if not changed and not orphans:
        print("  nothing to do")
        return 0

    for rel in orphans:
        try:
            os.remove(os.path.join(dest, rel))
        except OSError as e:
            print("!! could not remove %s (%r)" % (rel, e))
            return 1

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
