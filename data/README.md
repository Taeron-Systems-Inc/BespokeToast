# What is in here, and which runs the documentation can point at

Two things live in `data/`: the measurements the firmware is built from,
and the runs that back the numbers quoted in `docs/`.

    python3 tools/score_runs.py

recomputes every tracking figure the documentation quotes, from the files
below. A number that has drifted from its data shows up as a difference
rather than as a sentence nobody can check.

## The measurements the firmware uses

| file | what it is |
|---|---|
| `oven-characterisation.json` | the heating and cooling rate tables, the coast figures, the element model and the pre-charge and predictive constants. Deployed to the board as `characterisation.json`; every profile is generated from it. |
| `profile-specs.json` | what each profile is metallurgically. `tools/make_profile.py` turns these into the shipped curves. |
| `e2-step-test-2026-08-25.csv`, `e2-step-test-240c-2026-08-25.csv` | the two original step tests, 2 Hz, empty oven: 26 → 200 °C and 53 → 240 °C. Columns `stage,t_s,hot_c,cold_c,cpu_c`. |
| `plant-id/run-ident-2026-09-11.csv` | the plateau identification schedule, and the 4 Hz console capture it was decimated from. See `plant-id/README.md`. |

## The runs

The oven numbers its runs and records every control step to its own
storage. Only the runs the documentation actually cites are copied here.
Anything else stays on the oven.

**Getting a run that is not here:** the oven serves its own logs while it
is idle. Open its page — the address is on the home screen — and the run
list is the first thing on it; a log downloads as CSV from
`/logs/<number>-<profile>.csv`. That is the normal way a run comes off the
oven, because USB is power-only behind a panel.

Two formats, because they carry different things:

* **Run logs** (`data/*run-00*.csv`) are the oven's own records, about
  4 Hz, complete: `elapsed_s, target_c, actual_c, relay, cold_c, cpu_c`.
  They carry the relay state but no duty.
* **Console captures** (`data/plant-id/*.csv`) are decimated to 1 Hz and
  carry the **commanded duty**, which the run logs do not. Plant
  identification needs the input signal, and a 1 Hz sample of the relay is
  an aliased view of a 4 s time-proportional window rather than the power
  applied.

| run | date | what it is | file |
|---|---|---|---|
| 0009 | 2026-09-09 | four-hour bake on the loop before pre-charge — the only other four-hour bake on record | `bake-125c-run-0009-2026-09-09.csv` |
| 0010 | 2026-09-10 | STEP 250 °C. One free-cooling descent, relay open throughout: this is where the cooling table comes from | `step-250c-run-0010-2026-09-10.csv` |
| 0011 | 2026-09-10 | TS391SNL, 34 °C warm start, old loop | `ts391snl-run-0011-2026-09-10.csv`, `plant-id/run-0011-ts391snl-warm.csv` |
| 0013 | 2026-09-10 | TS391SNL, 59 °C start, old loop — the warm-start failure the rebuild was aimed at | `ts391snl-warm-start-run-0013-2026-09-10.csv`, `plant-id/run-0013-ts391snl-hot.csv` |
| 0014 | 2026-09-10 | TS391LT, 28 °C cold start, old loop | `ts391lt-run-0014-2026-09-10.csv`, `plant-id/run-0014-ts391lt.csv` |
| 0015 | 2026-09-10 | bake on the old loop. Stopped after 3.2 minutes of hold, so it bounds the old loop's hold but is not a four-hour comparison | `bake-125c-run-0015-2026-09-10.csv`, `plant-id/run-0015-bake-125c.csv` |
| 0016, 0017 | 2026-09-11 | the first two runs with pre-charge | `plant-id/run-001[67]-*.csv` |
| 0018, 0019 | 2026-09-11 | predictive tracking, decay-form prediction | `plant-id/run-001[89]-*.csv` |
| 0020, 0021, 0022 | 2026-09-11 | predictive tracking, driven-form prediction: the loop in production | `plant-id/run-002[012]-*.csv` |
| 0024 | 2026-09-16 | four-hour bake on the production loop, empty oven — the release validation run | `bake-125c-run-0024-2026-09-16.csv` |

`tests/data/` holds two more, used as test fixtures rather than as
evidence: run 0006 (NC191LTA10) and a 1 Hz capture of a datasheet-profile
run with the door opened at the end.

## What none of these establish

Every run here was made with an **empty oven**. They show what the oven
did with the chamber it was measured in, and nothing about a loaded board,
a different thermocouple position, or how far the reading is from the
truth. `docs/hardware.md` lists what is still unquantified.
