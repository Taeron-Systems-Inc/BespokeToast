# On-device validation

The firmware is validated by running the oven, not by a bench harness. What
each profile achieves is in `profiles.md`; what the control loop achieves is
in `control-loop.md`. Every figure either document quotes comes out of

    python3 tools/score_runs.py

from files in this repository, so a number that has drifted from its data
shows up as a difference rather than as a sentence nobody can check.

## What has actually been run

Twenty-six logged runs, every one recorded to the oven's own storage with
every control step. Two of those are a no-heat fixture that exercises the
run-to-idle transition and proves nothing about heating. The runs the
documentation rests on, and where they are:

    reflow, cold and hot starts   0020-0022   0.77-1.12 C rms heating phase
                                              data/plant-id/run-002*.csv
    a full four-hour bake         0024        0.240 C rms across the hold
                                              data/bake-125c-run-0024-*.csv
    the same bake, old loop       0009        0.264 C rms, peak 127.2 C
                                              data/bake-125c-run-0009-*.csv
    the free-cooling descent
      the cooling table is from   0010        245 -> 58 C, relay open
                                              data/step-250c-run-0010-*.csv

`data/README.md` lists every run that is here and how to fetch one that is
not: the oven serves its own logs from its page while it is idle.

Every run passes its checks: peak, time above liquidus where there is one,
both ramp limits, and time to peak where it applies.

All of it was an **empty oven**. Nothing here was run with a board in it.

## The first bring-up, and why it was done that way

Before any of that, the new code was driven on the board with `code.py` and
`boot.py` left untouched, so the board still booted the firmware it had
always booted, and everything new was imported and driven from the REPL.
`tools/onboard_test.py` reproduces it.

That established the things worth establishing before trusting an untested
controller with a heating element: every import resolves on CircuitPython
8.0.5, the profile parser and interpolation work on-device, the real MCP9600
reads through the new HAL, the scheduler holds 4.1 Hz against its intended
250 ms, and the state machine sits in idle without ever requesting heat. The
relay was never energised.

It is reversible by deleting three directories, which is the property that
made it a safe first step, and it remains the right way to put this firmware
on a board that has never run it.

## What no test here establishes

Nothing in this repository proves a joint is sound. The checks confirm the
oven followed the curve it was asked to follow; whether that curve suits the
paste, the board and the parts is metallurgy, and the profile notes cite the
datasheets rather than settling it.

Nor does anything here bound the oven's **absolute** accuracy. The probe's
position in the cavity is unrecorded and the cold-junction error grows
through a run, peaking when the oven is hottest; `hardware.md` says what
that would take to measure.
