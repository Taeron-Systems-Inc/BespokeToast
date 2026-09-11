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

## The identification run, 2026-09-11

`run-ident-2026-09-11.csv` is the first schedule from
`tools/device/heat_step_test.py`: plateaux at 60, 100, 150, 195 and 235 C,
each held and then square-waved in duty. `run-ident-2026-09-11-console-4hz.txt`
is the raw console capture it was decimated from, kept because the
per-plateau analysis (`tools/plateau_dynamics.py`) reads the step markers
that decimation drops.

Stopped by hand at step 35 of 41 with the cold junction at 65 C and the top
plateau clamping on its 250 C ceiling; the 235 C excitation and the
scheduled cooling are not in it. Peak 250.8 C, no faults.

What it found, per plateau:

    plateau   mean C   gain C/s   tau s    determined?
    60C        42.2      --        --      no: flat, excitation too gentle
    100C       82.9      --        --      weakly, prefers longer tau
    150C      146.1     1.71      ~15-18   yes
    195C      212.3     1.46      ~9       yes

The element time constant FALLS with temperature. The fitted gains at 150
and 212 C agree with the heating table's h - c to within 8%, so the table
is right there; the 235 C plateau climbed 14 C above its setpoint at the
table's own hold duty, so the table is wrong at the top. That locates the
30% dispute between the linear two-state model and the table: it is a
high-temperature effect, and it is the table's.

A single-tau linear model fitted to all five captures is worse than one
fitted to the four profile runs -- rms 11.3 against 5.3 -- because this run
spans a tau that is not constant. The observer in oven/elementff.py uses
the four-run beta, fitted on the warm-start regime it is used in.
