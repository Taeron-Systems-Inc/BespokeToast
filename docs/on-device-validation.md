# On-device validation

The firmware is validated by running the oven, not by a bench harness. What
each profile achieves, measured on hardware, is in `profiles.md`; what the
control loop achieves is in `control-loop.md`.

## What has actually been run

Twenty-six logged runs, every one recorded to the oven's own storage with
every control step. Two of those are a no-heat fixture used to test the
run-to-idle transition and prove nothing about heating. The ones that
matter:

    reflow, cold and warm starts    runs 0020-0022   0.78-1.13 C rms
    a full four-hour bake           run 0024         0.240 C rms hold
    the step test that measures
      the cooling table             run 0010         245 -> 58 C, relay open

Every run passes its checks: peak, time above liquidus where there is one,
both ramp limits, and time to peak where it applies.

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
