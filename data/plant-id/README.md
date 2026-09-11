# Captures for plant identification

Four real runs, off the serial console rather than out of the oven's own
logs, and decimated to 1 Hz.

The run logs the oven writes carry `elapsed_s, target_c, actual_c, relay,
cold_c, cpu_c` and **no duty**. Identification needs the input signal, and
the relay column sampled at 1 Hz is an aliased view of a 4 s
time-proportional window rather than the power actually applied. The console
prints the commanded duty every control step, which is what these hold.

1 Hz because the element time constant is about 14 s.

    python3 tools/identify_plant.py            cross-validate and score
    python3 tools/identify_plant.py --fit      fit on everything

| file | run | span |
|---|---|---|
| `run-0011-ts391snl-warm.csv` | 0011 | 34 C warm start, to 247 C |
| `run-0013-ts391snl-hot.csv` | 0013 | 59 C start, the hottest allowed, to 247 C |
| `run-0014-ts391lt.csv` | 0014 | 28 C cold start, to 168 C |
| `run-0015-bake-125c.csv` | 0015 | 30 C to 125 C and held |

All 2026-09-10, empty oven.
