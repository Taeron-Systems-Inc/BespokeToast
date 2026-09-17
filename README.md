# BespokeToast

Firmware for a toaster oven converted to a reflow soldering oven, controlled
by an Adafruit PyPortal.

This repository holds the current state of the oven: the firmware running on
it today, the measurements that firmware is built from, and reference notes
on the hardware it drives.

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
             plant identification, screen rendering.
  device/    Runs on the board over the serial console.
  host/      Runs on the bench machine.
  collector/ Receives finished runs.
  design/    Simulation harnesses used to choose the control loop.
data/        Measured characterisation, step-test logs, run captures.
docs/        Hardware, network, control loop, profiles, build, validation.
```

## Testing

```
python3 -m pytest tests/
```

Everything runs on a laptop. That is deliberate and enforced: a test parses
every module in `oven/` and fails if anything other than `hardware.py`
imports `board`. The previous firmware became untestable one import at a
time.

`code.py` is never imported by the suite -- it needs a board -- so it is
checked by parsing instead, which is how board-only code still gets
verified.

## Getting changes onto the oven

Two paths, and which one you need depends on the file:

| Changed | How it ships |
|---|---|
| `code.py`, `profiles/`, `assets/`, `characterisation.json` | `tools/deploy.py` |
| anything under `firmware/oven/` | rebuild and reflash |

`oven/` is **frozen into the CircuitPython image**, which is what makes it
fit in the board's memory -- a copy of it on the volume would shadow the
frozen one and silently cost about two thirds of the available RAM. See
`docs/frozen-build.md`, which also covers building, flashing and rolling
back.

    export TOASTER_BUILD_HOST=user@host    # the machine with the toolchain
    python3 tools/release.py --check       # what would happen
    python3 tools/release.py --flash       # build, then flash

Writing to `CIRCUITPY` triggers CircuitPython's auto-reload, which restarts
the controller immediately. Never deploy while a profile is running.

## Safety

This switches 120 VAC into a heating element.

The relay fails safe: `D4` has an external pulldown, so the relay is
de-energised whenever the pin is not driven -- which includes every reset,
every Ctrl-C and every auto-reload. A supervisor independent of the control
loop holds a 260 C ceiling, an enclosure limit, rate and stall guards, and
ABORT is always available.

Read `docs/hardware.md` before working on the oven, and
`docs/control-loop.md` before changing how it heats.

## Documentation

| | |
|---|---|
| `docs/hardware.md` | the oven, the controller, what is measured and what is assumed |
| `docs/control-loop.md` | how it heats, what it achieves, and the rules a replacement must keep |
| `docs/profiles.md` | each paste's profile and why its numbers are what they are |
| `docs/network.md` | credentials, the web page, what the radio costs |
| `docs/frozen-build.md` | building, flashing, rolling back, who owns the volume |
| `docs/on-device-validation.md` | what has actually been run |
| `docs/original-firmware.md` | what this replaced, and why |

## Tags

| | |
|---|---|
| `v1` | the oven's state as found, before the rewrite |
| `known-good-loop-2026-09-10` | the last loop before pre-charge |
| `known-good-loop-2026-09-16` | current |

Each `known-good-*` tag has a matching firmware image and `code.py` kept
outside the repository; see *Rolling back* in `docs/control-loop.md`.
