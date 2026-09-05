# BespokeToast

Firmware for a toaster oven converted to a reflow soldering oven, controlled by
an Adafruit PyPortal.

This repository holds the current state of the oven: the firmware running on it
today, and reference notes on the hardware it drives.

## Layout

```
firmware/    What ships to the device. Mirrors the CIRCUITPY volume.
  oven/      Control, safety, profiles, metrics, interface. Only
             hardware.py touches the board; everything else is plain
             stdlib and runs under CPython.
  profiles/  Reflow profiles as JSON.
  assets/    Fonts and logo.
tests/       pytest, off-hardware. Includes a simulated oven built from
             this oven's own measured response.
tools/       Host-side: deploy, release and rollback, model fitting,
             screen rendering, profile formatting. tools/device/ runs
             on the board over serial; tools/collector/ receives runs.
data/        Measured characterisation and the raw step-test logs.
docs/        Hardware reference and notes on the original firmware.
```

## Testing

```
python3 -m pytest tests/
```

Everything runs on a laptop. That is deliberate and enforced: a test parses
every module in `oven/` and fails if anything other than `hardware.py`
imports `board`. The previous firmware became untestable one import at a
time.

## Deploying

`firmware/` mirrors the root of the PyPortal's `CIRCUITPY` volume — deployment
is a copy, not a build. `code.py` goes to the volume root, `reflow_profiles/`
alongside it. The Adafruit libraries listed in `docs/firmware.md` must already
be present and must match the board's CircuitPython version.

Writing to `CIRCUITPY` triggers CircuitPython's auto-reload, which restarts the
controller immediately. Never deploy while a profile is running: the mains relay
would be left in an undefined state.

## Safety

This switches 120 VAC. Read the safety section of `docs/firmware.md` before
running the oven or deploying to it.

## History

Earlier commits in this repository hold the oven's first controller and its
development through 2023. Two artifacts from that history are still useful and
are not carried in the tree — see `docs/firmware.md`, *Recovering earlier work*.

## Tags

- `v1` — the oven's state as found, before the rewrite.
