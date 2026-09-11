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
