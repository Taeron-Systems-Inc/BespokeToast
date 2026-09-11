# The control loop

## The fallback, first

Everything below describes the loop **as it stood on 2026-09-10**, before any
attempt to replace it. It works. It passed every check on every profile
across runs 0010-0015, and if a redesign turns out worse, this is what to go
back to.

    git checkout known-good-loop-2026-09-10

The flashed image and the `code.py` that belongs with it are kept outside the
repository, because `code.py` is not frozen and does not travel with a `.uf2`:

    ~/.bespoketoast/images/known-good/loop-2026-09-10.uf2
    ~/.bespoketoast/images/known-good/loop-2026-09-10-code.py

    md5  76e7370d62647ab372a1d76c4507e210   loop-2026-09-10.uf2
    md5  4d69581432b3d16c48998e0150d7f7c5   loop-2026-09-10-code.py

To put it back: enter the bootloader (`tools/release.py` does this, or
`microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)` over the
console), copy the `.uf2` onto `PORTALBOOT`, then deploy that `code.py`.
Rolling the firmware back without its `code.py` leaves a board that boots and
serves a dead page -- that was found by doing it.

## What it is

    duty = clamp( FF(target, slope) + PID(target - measured), 0, 1 )
    relay = time_proportional(duty)

**FeedForward** inverts the plant: given a temperature and a demanded rate,
it returns the duty that produces that rate, by interpolating the measured
heating and cooling tables in `data/oven-characterisation.json`.

    u = (rate - c(T)) / (h(T) - c(T))

It is evaluated at the *target* and the *target's* slope, not at the
measurement -- it is a function of the reference, not of the error.

**PID** is a trim on top, free to go negative.

    kp = 0.22   ki = 0.004   kd = 0.5   i in [-0.6, 0.6]

Derivative on measurement, negated, taken across a 3 s window rather than
between adjacent samples: at 4 Hz with a probe quantised to 0.0625 C, one
quantisation step between neighbours reads as 0.25 C/s of slope that is not
there, and with kd=0.5 that is a 0.125 swing in duty out of pure noise.
Measured on hardware, adjacent-sample derivative turned a smooth demand into
duty hopping between 0 and 1 several times a second and cost roughly three
times the expected relay actuations.

Anti-windup is conditional integration: the integral only accumulates when
doing so would not push an already-saturated output further into the rail,
and unwinding is always allowed.

**Predictive peak cutoff.** Once `predict_peak(temp, rate, coast_tau)`
reaches the profile's peak, duty goes to zero and latches. It releases when
the oven falls more than 1 C below the target, which is what lets a profile
HOLD at peak to earn time above liquidus -- an earlier version also required
the target to be below the peak, and silently coasted through the whole
dwell.

**TimeProportional** turns duty into relay states: a 4 s window, minimum 0.8 s
on and off. One window for every profile. A 30 s window would cut relay wear
on a four-hour bake from ~1080 actuations to ~136, but the oven climbs at
over a degree a second and a 30 s slug of heat overshoots by 35 C; 8 s still
costs 4.7 C. A bake exists to hold 125 C within a few degrees, and trading
that for relay life is the wrong way round.

## What it achieves, measured

Heating phase only -- the cooling tail is the door's error, not the loop's.

    run 0014  TS391LT, 28 C cold start        2.47 C rms
    run 0011  TS391SNL, 34 C warm start       9.14 C rms, worst lag -24.3 C
    run 0013  TS391SNL, 59 C warm start      13.17 C rms, worst lag -32.2 C

Every run 0010-0015 passed every check: peak, time above liquidus, both ramp
limits, time to peak.

## Where it is weak, and why it is not a tuning problem

A cold start on a generated curve is at 2.47 C rms, which is near what the
probe and the switching window can resolve. The weakness is warm starts.

The residual is dead-time shaped. Shifting the measurement earlier in time by
8-13 s minimises the error, against 9-10 s of transport dead time measured
directly from relay-close to probe-movement, and that accounts for 18-41% of
it.

But **whenever the oven was more than 8 C behind, duty was 1.00, for 100% of
that time.** The actuator was flat out. There is no gain you can give a
controller that is already asking for everything the plant has, so no amount
of tuning addresses this.

The cause is upstream of the controller. `FeedForward` inverts a plant model
that has no element state: it returns the *steady-state* duty for the
demanded rate, which is correct once the element is hot and far too little at
the start of a run. From a cold start that is hidden, because the rate
table's low-temperature entries encode the same delay and a generated
profile's opening is slow anyway -- the two errors cancel. A warm start
enters past that opening and exposes it.

See `tools/identify_plant.py`: a two-state model predicts held-out runs two
to five times better than the one this inverts.

## What replaced the start: pre-charge (2026-09-11)

The loop above is unchanged. What changed is when its clock starts.

    PREHEAT  ->  PRECHARGE  ->  RUNNING

In PRECHARGE the element is driven at full duty with the profile clock held.
An observer -- `oven/elementff.py`, the two-state model from
`tools/identify_plant.py` in the parameters the chamber can see --
estimates the element's contribution to chamber rate, and the run starts
the moment that reaches what the curve's opening needs, or at a 40 s bound.
The oven then enters the profile wherever it is, exactly as before, but with
an element that can follow.

Why timing and not gain: whenever the old loop was more than 8 C behind on a
warm start, duty was 1.00 for 100% of that time. A state-feedback
feed-forward was built first and moved the worst-case lag from -11.5 to
-11.5. The plant does not care how hard it is asked; it cares when.

Simulated through the real App on the identified plant, old feed-forward and
old PID throughout:

                            without              with            charge
    TS391SNL 59 C start    rms 12.51 lag -25.2  rms 4.10 lag -8.5   40 s
    TS391SNL 34 C start    rms  8.59 lag -16.6  rms 5.77 lag -11.8  11 s
    TS391LT  45 C start    rms  6.47 lag -15.0  rms 3.25 lag -7.5   15 s
    cold starts            unchanged; 2-4 s of charge, then stands aside

Peaks and time above liquidus do not move. Holds up at g*0.8 and g*1.2.

What it is not: a change to the feed-forward, the PID, the cutoff or the
output stage. The measured rate tables remain what the steady state comes
from. The two-state model is used for one decision -- when -- and its
30% steady-state disagreement with the table is recorded as open rather
than resolved either way.

The characterisation carries the parameters under `element_model` and the
bound under `precharge`. An oven whose characterisation lacks them starts
runs the way it always did; the factory returns None and PRECHARGE is never
entered.

## Rules any replacement has to keep

These are not style preferences. Each cost a run, a board, or a day.

1. **The relay fails safe and the supervisor is not part of the loop.**
   260 C hard ceiling, 70 C enclosure, rate and stall guards, ABORT always
   available. A controller may not assume the supervisor will catch it.
2. **One SPI call to the co-processor can block 227 ms against a 250 ms
   control deadline.** Nothing in the loop may talk to the network.
3. **Derivative over a window, never between adjacent samples.** 0.0625 C of
   quantisation at 4 Hz is 0.25 C/s of imaginary slope.
4. **Relay actuations are a cost.** A four-hour bake is where the wear is;
   the loop that replaces this one should count them.
5. **Composing a screen must not be able to kill a run**, and the loop must
   hold its cadence while it happens.
6. **The measured rate tables are right.** They carry the nonlinearity of a
   radiative oven -- a factor of three in process gain between 80 C and
   240 C -- and any replacement that throws them away is starting behind.
