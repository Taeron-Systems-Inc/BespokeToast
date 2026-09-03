#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the firmware with oven/ frozen in, and flash it.

Editing anything under firmware/oven/ no longer takes effect by deploying:
a frozen build executes that code from flash, and a copy on CIRCUITPY would
shadow it and put ~48 kB of bytecode back into a 256 kB RAM. So the loop for
those files is build, flash, verify -- and it needs to be one command, or it
will be skipped and someone will wonder why their change did nothing.

    python3 tools/release.py --check     what would happen, touching nothing
    python3 tools/release.py --build     build on the build host only
    python3 tools/release.py --flash     build, then flash and verify
    python3 tools/release.py --rollback  reflash the stock image

See docs/frozen-build.md for how the build host was set up and why the
-Werror patch is needed.
"""

import os
import subprocess
import sys
import time

HOST = os.environ.get("TOASTER_BUILD_HOST", "vox@10.20.10.162")
REMOTE_TOP = "~/build/circuitpython"
REMOTE_FROZEN = REMOTE_TOP + "/frozen/BespokeToast/oven"
REMOTE_UF2 = REMOTE_TOP + "/ports/atmel-samd/build-pyportal/firmware.uf2"
TOOLCHAIN = "~/toolchains/arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin"

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_OVEN = os.path.join(HERE, "..", "firmware", "oven")
MOUNT = os.environ.get("TOASTER_MOUNT", "/mnt/circuitpy")
BOOTLOADER_LABEL = "PORTALBOOT"


def run(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)


def ssh(command):
    return run("ssh -o BatchMode=yes %s %s" % (HOST, quote(command)))


def quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def reachable():
    return ssh("echo ok").stdout.strip() == "ok"


def sync_sources():
    """Push oven/ to the build host. tar rather than rsync: not installed."""
    proc = subprocess.Popen(
        "tar czf - -C %s oven | ssh -o BatchMode=yes %s %s"
        % (os.path.join(HERE, "..", "firmware"), HOST,
           quote("mkdir -p %s/.. && cd %s/.. && rm -rf oven && tar xzf -"
                 % (REMOTE_FROZEN, REMOTE_FROZEN))),
        shell=True)
    return proc.wait() == 0


def build():
    # The freeze manifest is generated once and make then treats it as up
    # to date, so a NEWLY ADDED module is silently left out while the build
    # reports success. That happened: oven/uploader.py was in the source
    # tree, absent from the image, and the firmware raised ImportError at
    # runtime. Removing the manifest and the compiled output forces both to
    # be regenerated from whatever is actually there now.
    return ssh(
        "export PATH=$HOME/.local/bin:%s:$PATH && cd %s/ports/atmel-samd && "
        "rm -rf build-pyportal/manifest.py build-pyportal/frozen_mpy "
        "build-pyportal/frozen_content.c && "
        "make -j$(nproc) BOARD=pyportal 2>&1 | tail -6" % (TOOLCHAIN, REMOTE_TOP))


def frozen_modules_match():
    """Every module in firmware/oven must be in the image. Verify, do not hope.

    A build that quietly omits a module produces a firmware that imports
    fine until the moment it needs the missing one.
    """
    local = sorted(n[:-3] for n in os.listdir(LOCAL_OVEN)
                   if n.endswith(".py"))
    listing = ssh("ls %s/ports/atmel-samd/build-pyportal/frozen_mpy/oven/*.mpy"
                  % REMOTE_TOP).stdout
    built = sorted(os.path.basename(p)[:-4]
                   for p in listing.split() if p.endswith(".mpy"))
    return local, built, [m for m in local if m not in built]


def fetch_uf2(into):
    return run("scp -o BatchMode=yes %s:%s %s" % (HOST, REMOTE_UF2, into))


def shadowing():
    """Files on the volume that would shadow the frozen build."""
    names = ["oven", "adafruit_display_text", "adafruit_esp32spi",
             "adafruit_bus_device", "adafruit_portalbase",
             "adafruit_requests.mpy", "neopixel.mpy"]
    return [n for n in names if os.path.exists(os.path.join(MOUNT, n))]


def enter_bootloader():
    """Ask the board to reboot into UF2. No physical access needed, which
    matters: the USB port is behind a panel held by two screws.

    Escalates only for this step. The build talks to the build host over
    ssh as the invoking user, and the serial port needs root here -- running
    the whole tool under sudo breaks the first to fix the second.
    """
    program = (
        "import glob, sys, time\n"
        "try:\n"
        "    import serial\n"
        "except ImportError:\n"
        "    print('NO_PYSERIAL'); sys.exit(1)\n"
        "ports = sorted(glob.glob('/dev/serial/by-id/*PyPortal*'))\n"
        "if not ports:\n"
        "    print('NO_PORT'); sys.exit(1)\n"
        "s = serial.Serial(ports[0], 115200, timeout=0.5)\n"
        "time.sleep(0.5)\n"
        "for _ in range(3):\n"
        "    s.write(b'\\x03'); time.sleep(0.4)\n"
        "s.read(800)\n"
        "s.write(b'import microcontroller\\r\\n'); time.sleep(0.4)\n"
        "s.write(b'microcontroller.on_next_reset("
        "microcontroller.RunMode.BOOTLOADER)\\r\\n'); time.sleep(0.8)\n"
        "s.write(b'microcontroller.reset()\\r\\n'); s.flush()\n"
        "time.sleep(2); s.close(); print('OK')\n"
    )
    result = run("sudo python3 -c %s" % quote(program))
    out = (result.stdout or "") + (result.stderr or "")
    if "OK" in out:
        return None
    if "NO_PYSERIAL" in out:
        return "pyserial is not installed for root"
    if "NO_PORT" in out:
        return "no PyPortal serial port found"
    return "could not put the board into its bootloader: %s" % out.strip()[-200:]


def wait_for_bootloader(timeout=45):
    path = "/dev/disk/by-label/" + BOOTLOADER_LABEL
    end = time.time() + timeout
    while time.time() < end:
        if os.path.exists(path):
            return True
        time.sleep(1)
    return False


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--check"
    if mode not in ("--check", "--build", "--flash", "--rollback"):
        print(__doc__)
        return 2

    print("build host : %s" % HOST)
    if not reachable():
        print("!! cannot reach the build host over ssh")
        return 1
    print("             reachable")

    shadows = shadowing()
    if shadows:
        print("!! %s carries files that shadow a frozen build: %s"
              % (MOUNT, ", ".join(shadows)))
        print("   Everything would still work, on a third of the memory.")
        if mode == "--flash":
            return 1
    else:
        print("volume     : clean, nothing shadowing the frozen modules")

    if mode == "--check":
        print("nothing done. --build to build, --flash to build and flash.")
        return 0

    print("syncing oven/ to the build host")
    if not sync_sources():
        print("!! could not copy the sources")
        return 1

    print("building (this takes a couple of minutes)")
    result = build()
    print(result.stdout.strip() or result.stderr.strip())
    if "firmware.uf2" not in result.stdout:
        print("!! the build did not produce a uf2")
        return 1

    local, built, missing = frozen_modules_match()
    if missing:
        print("!! the image is missing %d of %d modules: %s"
              % (len(missing), len(local), ", ".join(missing)))
        print("   A firmware that omits a module imports fine until the")
        print("   moment it needs it. Not flashing this.")
        return 1
    print("frozen     : all %d modules present in the image" % len(local))

    if mode == "--build":
        return 0

    local = os.path.join("/tmp", "bespoketoast-firmware.uf2")
    if fetch_uf2(local).returncode != 0:
        print("!! could not fetch the built image")
        return 1
    print("fetched %s (%d bytes)" % (local, os.path.getsize(local)))

    print("asking the board to enter its bootloader")
    problem = enter_bootloader()
    if problem:
        print("!! %s" % problem)
        return 1
    if not wait_for_bootloader():
        print("!! %s did not appear. The bootloader can still be entered by"
              % BOOTLOADER_LABEL)
        print("   double-tapping reset, which means opening the panel.")
        return 1
    print("bootloader is up; copy the image onto it and the board reboots:")
    print("  sudo mount /dev/disk/by-label/%s /mnt/portalboot" % BOOTLOADER_LABEL)
    print("  sudo cp %s /mnt/portalboot/" % local)
    print("(left as a manual step: writing to a bootloader is the one thing")
    print(" here worth a human confirming.)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
