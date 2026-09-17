# The control loop

## What is in production

Pre-charge and predictive tracking, described below. The image and the
`code.py` that belongs with it are kept together, because `code.py` is not
frozen and does not travel with a `.uf2`:

    git checkout known-good-loop-2026-09-16        # commit 7320298

    ~/.bespoketoast/images/known-good/loop-2026-09-16.uf2
    ~/.bespoketoast/images/known-good/loop-2026-09-16-code.py

    md5  b6fc67b32a057615132b5421a5b5ad3d   loop-2026-09-16.uf2
    md5  7c058d41a4374a1aee34295cfae18f55   loop-2026-09-16-code.py

Validated on hardware: runs 0020 to 0022 for the reflow profiles, and run
0024, a full four-hour bake at 0.240 C rms. Rolling the firmware back
without its `code.py` leaves a board that boots and serves a dead page --
that was found by doing it.

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
on a four-hour bake by roughly eight times, but the oven climbs at
over a degree a second and a 30 s slug of heat overshoots by 35 C; 8 s still
costs 4.7 C. (The ~1080 actuations per bake this once claimed was a
simulation figure. Measured at the hold on hardware, both loops sit near
2300-2550 per four-hour bake -- see the bake numbers below.) A bake exists to hold 125 C within a few degrees, and trading
that for relay life is the wrong way round.

## What it achieves, measured

Heating phase only -- the cooling tail is the door's error, not the loop's.

    run 0014  TS391LT, 28 C cold start        2.47 C rms
    run 0011  TS391SNL, 34 C warm start       9.14 C rms, worst lag -24.3 C
    run 0013  TS391SNL, 59 C warm start      13.17 C rms, worst lag -32.2 C

(Scored before the entry-sample correction; the sections below use
1.57/13.06 for the same two runs. The comparison is like for like
within each section.)

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

Measured on hardware, 2026-09-11, run 0016 -- the same 59 C start as run
0013, empty oven, heating phase only:

                          worst lag    rms    charge   entered at   peak
    run 0013, old start    -32.0 C   13.06     --        59.4 C    +1.9 C
    run 0016, pre-charge    -5.1 C    1.57    33 s       80.5 C    -0.2 C

That is the hottest start the supervisor allows, tracking as well as the
best cold start on record (run 0014, 2.47 C rms), and better. The simulation had said
4.10 rms and -8.5 C; the real element charged in 33 s against the 40 s
bound, so the model is conservative in the right direction. Time above
liquidus 94 s.

What it is not: a change to the feed-forward, the PID, the cutoff or the
output stage. The measured rate tables remain what the steady state comes
from. The two-state model is used for one decision -- when -- and its
30% steady-state disagreement with the table is recorded as open rather
than resolved either way.

The characterisation carries the parameters under `element_model` and the
bound under `precharge`. An oven whose characterisation lacks them starts
runs the way it always did; the factory returns None and PRECHARGE is never
entered.

## What replaced the error: predictive tracking (2026-09-11)

Run 0017 -- TS391LT from the same hot start, on pre-charge -- tracked the
ramp within 5 C and then coasted 14 C past the soak knee with the relay
open: at 90 C the element held that much heat the chamber had not seen.
The loop was acting on stale news. Whenever it drove full-on into a knee
it had already lost.

The same element state that decides when a run starts now tells the loop
where the chamber will be. `Controller.duty_for` takes the observer's
estimate z, and with a lead configured evaluates the feed-forward and the
PID on the curve `lead_s` ahead, against

    T_pred = T + z * (1 - exp(-beta * lead)) / beta - d * (T - Ta) * lead

The App owns one `ElementObserver` per run: pre-charge fills it, the run
keeps feeding it with what the relay did. The FF, the PID gains, the
cutoff and the output stage are the ones above; only what they are shown
has changed. With no model, or no element state, it is the old loop, and
`tests/test_predictive.py` holds it to that.

Swept through the firmware's own Controller on the identified plant
(`tools/design/predictive_sim.py`), heating phase rms:

                          lead 0    4 s     6 s     8 s    10 s
    TS391LT   28 C         2.70    1.52    1.47    2.24    3.29
    TS391LT   59 C         1.85    1.38    0.90    1.22    2.42
    TS391SNL  25 C         5.99    3.93    3.75    4.12    4.34
    TS391SNL  34 C         4.99    4.00    3.36    3.76    3.79
    TS391SNL  59 C         2.53    1.84    1.42    1.61    1.91

Holds at g*0.8 and g*1.2. Ten seconds and beyond overshoots: the
prediction trusts the observer more than it deserves. Peaks and time
above liquidus do not move; a reflow run costs about ten more relay
actuations, and the four-hour bake costs fewer (2895 to 2440) because the
hold no longer hunts. The lead is `predictive.lead_s` in the
characterisation; 6 s.

Not taken: charging the element to the need six or twelve seconds past
entry instead of at entry. Simulated, it moves nothing -- the residual
lag on a 34 C start is the oven at full power below 60 C, which is the
table's low end and not a control problem.

Measured on hardware, heating phase only:

    run 0018  TS391SNL  34 C start   rms 1.87   worst lag -5.3   (run 0011, old loop: 9.16, -24.1)
    run 0019  TS391SNL  59 C start   rms 1.91   worst lag -5.0   (run 0016, pre-charge only: 1.57, -5.1)
    run 0020  TS391LT   59 C start   rms 0.78   worst lag -2.5   (run 0017, pre-charge only: 2.24, -5.4)
    run 0021  TS391SNL  25 C cold     rms 0.95   worst lag -2.6   (run 0014, TS391LT cold, old loop: 2.46, -6.6)
    run 0022  TS391SNL  59 C start   rms 1.13   worst lag -4.2   (run 0019, decay form, same start: 1.91, -5.0)

0022 answers 0019 directly: same profile, same start temperature, same
29 s of charge, only the prediction changed. The bias 0019 carried from
160 C to the peak is gone.

    mean error, C      run 0016     run 0019     run 0022
    by target band    pre-charge   decay form   driven form
     80-120 C            -3.35        -3.25       -2.44
    120-160 C            -0.06        +0.66       +0.00
    160-200 C            -0.14        +1.67       +0.48
    200-240 C            +0.47        +1.50       -0.06
    240-260 C            +0.55        +1.77       -0.50

What is left is the opening: 2.4 C behind between 80 and 120 C, with the
relay closed. That is the oven at full power on the low end of the
heating table, and no controller reaches it.

Run 0020 is the case the lead was built for, on the corrected
prediction. The soak knee that cost run 0017 +4.1 C of overshoot cost
0.8 C; the peak landed at 164.6 against a 164.9 target where 0017 sailed
to 168.1; duty was saturated for 6% of the heating phase against 21%;
time above liquidus went 86.8 s to 90.5 s. Relay actuations rose from 42
to 64, which is the trade: the loop is modulating where it used to sit
on the rail.

Run 0019 against 0016 is the honest comparison, and the first lead did
not win it: better through the early ramp (100-140 C rms 3.9 to 2.8),
then +1.2 to +1.8 C hot from 160 C to the peak. Replaying the observer
over the captures found why. The prediction assumed the element would
be left to decay over the lead, and the loop was driving it: the chamber
landed +0.85 C above the prediction on average across three runs, and
the PID chased that. Predicting with the element on its way to the
steady state of the loop's own last duty is unbiased to 0.05 C with half
the spread (commit 183543e). What is in the simulation table above is
that form.

### The bake, where the relay wear is

Measured over a full four-hour run, 2026-09-16, empty oven, from the oven's
own log (run 0024):

                        rms      mean       closures/min   hold measured
    old loop (0015)     0.552              8.8            3.2 min
    predictive (0024)   0.240   +0.141 C   8.2            240 min

Better on both counts, and the earlier reading that suggested 12% more
relay wear came from a 23-minute probe that was mostly the settle. There is
no drift across the four hours:

    hour 0   rms 0.266        hour 2   rms 0.224
    hour 1   rms 0.238        hour 3   rms 0.234

Peak 125.9 C, both ramp limits passed, no faults, 14868 rows.

## Where the loop still loses

Every hardware run above is 2 to 3 C behind between 80 and 120 C with the
relay closed the whole time. That is not the controller: it is the oven at
full power on the low end of the heating table, where the table's own
entries below 85 C are an extrapolation and the first 37 s of the step
test they came from were transport dead time. Pre-charge shortens it; it
cannot remove it. Anything further has to come from the plant -- a longer
charge, or a curve whose opening does not ask for what the oven cannot
give there.

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
6. **The element is a state, not a delay to tune around.** Pre-charge and
   the predictive lead both come from the same two-state model and the
   same observer. A loop that sees only the chamber is guessing about
   half the plant.
7. **The measured rate tables are right.** They carry the nonlinearity of a
   radiative oven -- a factor of three in process gain between 80 C and
   240 C -- and any replacement that throws them away is starting behind.
