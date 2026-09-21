# BespokeToast

Firmware for a toaster oven converted to a reflow soldering oven, controlled
by an Adafruit PyPortal.

This repository holds the current state of the oven: the firmware running on
it today, the measurements that firmware is built from, the runs that back
the numbers, and reference notes on the hardware it drives.

## What you need

| | |
|---|---|
| The oven | a PyPortal wired to a mains relay and an MCP9600 thermocouple amplifier — `docs/hardware.md` describes the one this was built for |
| A host | anything running Python 3 that can mount USB mass storage and open a serial port. A Raspberry Pi is enough |
| A build host | only to change anything under `firmware/oven/`: ~3 GB of disk and an ARM toolchain. It does not have to be the machine attached to the oven |

## Putting the firmware on a board for the first time

The oven's own package is **frozen into the CircuitPython image**, so an
install is two halves: an image to flash, and a set of files to copy.

**1. Get an image.** Either build one — `docs/frozen-build.md` has the
toolchain, the source version and the one patch that is required — or use
an image that was built and tested earlier, if you have one. Images are not
in this repository: a `.uf2` is a build artefact, and the one that matters
is always paired with a `code.py`, which is not frozen and does not travel
inside it. Keep the pair together.

**2. Flash it.** The board must be in its UF2 bootloader, which shows up as
a volume named `PORTALBOOT`. On a board already running this firmware, ask
for it over the serial console:

```python
import microcontroller
microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
microcontroller.reset()
```

On a board that will not boot, or has never run this, double-tap the reset
button instead — which on this oven means opening the panel. Copy the
`.uf2` onto `PORTALBOOT`; the board reboots itself and comes back as
`CIRCUITPY`.

**3. Copy the files that are not frozen.** Mount the volume writable and
deploy:

```
sudo mount -o rw,uid=$(id -u) /dev/disk/by-label/CIRCUITPY /mnt/circuitpy
python3 tools/deploy.py /mnt/circuitpy --dry-run    # what it would write
python3 tools/deploy.py /mnt/circuitpy
```

That copies `boot.py`, `code.py`, `settings.toml`, `profiles/` and
`assets/`, plus `data/oven-characterisation.json` as `characterisation.json`,
then verifies every file by digest. It skips `oven/` when it sees the board
is running a frozen build, refuses to run while a profile is running, and
refuses if the Adafruit libraries have reappeared on the volume — a copy
there shadows the frozen one and silently costs about 20 kB of RAM.

**4. Give it the network, if you want the web page.** Copy
`wifi.json.example` to `wifi.json` **on the volume** — not into this
repository — and fill in the SSIDs and passwords:

```
cp wifi.json.example /mnt/circuitpy/wifi.json
$EDITOR /mnt/circuitpy/wifi.json
```

The oven scans and joins whichever listed network it hears most strongly.
Without the file it runs perfectly well, with logs stamped from boot
instead of wall clock and no page. `wifi.json` is in `.gitignore`, deploy
never writes it, and anyone who can plug a cable into the board can read
it — `docs/network.md` covers that and the rest.

**5. Hand the volume back to the oven.**

```
sudo umount /mnt/circuitpy
python3 tools/deploy.py --standalone
```

A deploy needs the **host** to own `CIRCUITPY`; the oven needs to own it to
record a run. Only one direction is automatic, so an oven left in host mode
runs perfectly and keeps no record of it. The power-on screen says which
mode it is in, next to *run logging*.

**6. Check it came up.** The splash and self-test panel, then the home
screen within about 15 seconds; the network line fills in behind it. Press
nothing until the home screen shows a temperature that looks like the room.

## Getting changes onto an oven that already runs it

Which path you need depends on the file:

| Changed | How it ships |
|---|---|
| `code.py`, `profiles/`, `assets/`, `characterisation.json` | `tools/deploy.py`, as above |
| anything under `firmware/oven/` | rebuild and reflash |

```
export TOASTER_BUILD_HOST=user@host    # the machine with the toolchain
python3 tools/release.py --check       # what would happen, touching nothing
python3 tools/release.py --flash       # build, flash, verify
python3 tools/release.py --rollback    # the image before the last one
```

Writing to `CIRCUITPY` triggers CircuitPython's auto-reload, which restarts
the controller immediately. Never deploy while a profile is running; deploy
refuses unless forced.

## Testing

```
python3 -m pytest tests/
python3 tools/score_runs.py      # recompute the figures the docs quote
```

Everything runs on a laptop. That is deliberate and enforced: a test parses
every module in `oven/` and fails if anything other than `hardware.py`
imports `board`. The previous firmware became untestable one import at a
time. `code.py` is never imported by the suite — it needs a board — so it
is checked by parsing instead.

`tools/onboard_test.py` is the other half: it drives the new code on a real
board from the REPL without replacing what the board boots, which is the
right first step on a board that has never run this firmware.

## Safety

This switches 120 VAC into a heating element.

The relay fails safe: `D4` has an external pulldown, so the relay is
de-energised whenever the pin is not driven — which includes every reset,
every Ctrl-C and every auto-reload. A supervisor independent of the control
loop holds a 260 C ceiling, an enclosure limit, rate and stall guards, and
ABORT is always available. The web page cannot start or abort a run, and a
test walks the routes to keep it that way.

Read `docs/hardware.md` before working on the oven, and
`docs/control-loop.md` before changing how it heats. Every run behind the
numbers in those documents was made with an **empty oven**.

## Layout

```
firmware/    What ships to the device.
  code.py    Entry point: screens, console, web service, wiring.
  oven/      Control, safety, profiles, metrics, interface. Only
             hardware.py touches the board; everything else is plain
             stdlib and runs under CPython.
  profiles/  Reflow and bake profiles as JSON.
  assets/    Fonts and logo.
tests/       pytest, off-hardware. Includes a simulated oven built from
             this oven's own measured response.
tools/       Host-side: deploy, release and rollback, profile generation,
             plant identification, run scoring, screen rendering.
  device/    Runs on the board over the serial console.
  host/      Runs on the bench machine.
  collector/ Receives finished runs.
  design/    Simulation harnesses used to choose the control loop.
data/        Measured characterisation, step tests, and the runs the
             documentation cites. See data/README.md.
docs/        Hardware, network, control loop, profiles, build, validation.
```

## Documentation

| | |
|---|---|
| `docs/hardware.md` | the oven, the controller, what is measured and what is assumed |
| `docs/control-loop.md` | how it heats, what it achieves, and the rules a replacement must keep |
| `docs/profiles.md` | each paste's profile and why its numbers are what they are |
| `docs/network.md` | credentials, the web page, what the radio costs |
| `docs/frozen-build.md` | building, flashing, rolling back, who owns the volume |
| `docs/on-device-validation.md` | what has actually been run |
| `data/README.md` | which runs are in the repository, and how to fetch one that is not |

## Tags

| | |
|---|---|
| `v1` | the oven's state as found, before the rewrite |
| `known-good-loop-2026-09-10` | the last loop before pre-charge |
| `known-good-loop-2026-09-16` | the loop in production |

A tag records the source. The image and `code.py` that were tested together
are kept outside the repository, because a `.uf2` is a build artefact; see
*Rolling back* in `docs/control-loop.md`.
