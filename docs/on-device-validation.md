# On-device validation

Run 2026-08-25 against the oven's PyPortal, CircuitPython 8.0.5, with no heat
applied at any point. `tools/onboard_test.py` reproduces it.

The method matters: `oven/`, `profiles/` and `assets/` were copied to the
`CIRCUITPY` volume but **`code.py` and `boot.py` were left alone**, so the
board still boots the firmware it has always booted. Everything new was then
imported and driven from the REPL. That tests whether the code runs on this
hardware at all without committing the oven to it, and it is reversible by
deleting three directories.

## Results

| | |
|---|---|
| All modules import | yes, 29 KB of RAM |
| Free RAM after import | 182 KB |
| Free RAM after app + UI | **155 KB** |
| Control cadence | 33 ticks in 8.0 s = **4.1 Hz**, the intended 250 ms |
| Sensor through the new HAL | hot 25.31 °C, cold 25.50 °C, faults 0 |
| CPU die | 34.9 °C |
| Relay energised at any point | **no** |
| All three profiles parse | yes, including the 60-point derived one |
| UI screens build | 1776 bytes for home, running and fault together |

## What this does and does not establish

Established: the code compiles under CircuitPython 8.0.5, every import
resolves, the profile parser and the interpolation work on-device, the real
MCP9600 reads through the new HAL, the scheduler holds its cadence on actual
hardware, and the state machine sits in idle without ever requesting heat.

Not established: `displayio` was not initialised during this run, so the
fonts and the display adapter are still unexercised, and their RAM cost is
unmeasured. 155 KB of headroom makes it very unlikely to be a problem, but
"unlikely" is not "measured". Nothing here has driven the relay under
control, and no profile has been run.
