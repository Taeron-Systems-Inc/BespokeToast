# The original firmware

What the controller was before the rewrite, kept because it explains why the
rewrite happened. The code is not in this tree: `git show v1:firmware/code.py`
produces it, and every line reference below is against that.

## What it was

A single file built around one `Oven` class. The oven idled showing the
target curve; touching START ran the profile, drawing measured temperature
over target as it went; touching again stopped the run.

Control was proportional on *squared* error, recomputed once a second
(lines 312-342):

```
if tempDiff > 0:  onTime = tempDiff**2 / 100   # clamped to 1.0 s
else:             onTime = 0
```

No integral, no derivative, no feed-forward for the oven's thermal lag. A
`skipOffTime` flag held the relay on across consecutive saturated windows
rather than dropping it out, which is why a session showed on the order of
20 actuations rather than one per second.

Profiles were `time_s temperature_C` pairs, one per line, in
`reflow_profiles/`. Run length came from `self.totalTime = 360`, set
independently of the profile file, so a longer profile was simply cut short.

There was no logging. `save_temp_log` was commented out and the log file on
the device was empty: no run data was recorded anywhere, ever.

## Why it was replaced

Its safety characteristics, as found:

- **No over-temperature limit.** Nothing bounded commanded or measured
  temperature against an absolute maximum.
- **No sensor-fault detection.** An open, shorted or disconnected
  thermocouple, or an I2C failure, was not checked -- and a fault reading
  low *enlarges* the error, which increases relay on-time.
- **No watchdog.** If execution stalled with the relay energised, nothing
  independently turned it off.
- **No explicit safe state on stop.** Breaking out of the run loop did not
  drive the relay pin false; the relay dropped out only via the pin being
  deinitialised on the next VM reset, which assumes a pulldown at the relay
  input.
- **Auto-reload was live during runs.** Writing any file to `CIRCUITPY`
  restarted `code.py` mid-run with the relay in an undefined state.

Each of those is a rule in the current firmware, and the first four are why
`oven/safety.py` exists as something the control loop cannot talk its way
past.

## Recovering earlier work

| What | Where |
|---|---|
| `config.json`, with the 2023 coast figures | `git show b23f1a4^:code/config.json` |
| The program that measured them | `git show b23f1a4^:code/codecalibrate/code.py` |
| The larger controller it was reduced from | `git show 3ad005f:code/code.py` |

The 2023 coast figures are in `hardware.md` and are wrong by a factor of 28
against direct measurement; they are recorded there only so nobody
re-derives anything from them.

## A version coupling worth knowing

The old code called `display.show(group)`, removed in CircuitPython 9, and
its bundled `.mpy` libraries were 8.x builds. That coupling is why the board
still runs 8.0.5 and why the frozen build is pinned to it -- see
`frozen-build.md`.
