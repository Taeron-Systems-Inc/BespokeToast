# The control loop

## What is in production

Pre-charge and predictive tracking, described below. The image and the
`code.py` that belongs with it are kept together, because `code.py` is not
frozen and does not travel with a `.uf2`:

    git checkout known-good-loop-2026-09-16        # commit 0395111

    ~/.bespoketoast/images/known-good/loop-2026-09-16.uf2
    ~/.bespoketoast/images/known-good/loop-2026-09-16-code.py

    md5  b6fc67b32a057615132b5421a5b5ad3d   loop-2026-09-16.uf2
    md5  094bf903cdacc90b66ac516a41cfb64e   loop-2026-09-16-code.py

Validated on hardware: runs 0020 to 0022 for the reflow profiles, and run
0024, a full four-hour bake at 0.240 C rms. Rolling the firmware back
without its `code.py` leaves a board that boots and serves a dead page --
that was found by doing it.

## What it is

    duty  = clamp( FF(target, slope) + PID(target - predicted), 0, 1 )
    relay = time_proportional(duty)

with the element's stored heat carried as a state, because the chamber
cannot see it and the loop is wrong without it.

**FeedForward** inverts the plant: given a temperature and a demanded rate,
it returns the duty that produces that rate, interpolating the measured
heating and cooling tables in `data/oven-characterisation.json`.

    u = (rate - c(T)) / (h(T) - c(T))

Evaluated at the *target* and the target's slope, not at the measurement --
a function of the reference, not of the error.

**PID** is a trim on top, free to go negative.

    kp = 0.22   ki = 0.004   kd = 0.5   i in [-0.6, 0.6]

Derivative on measurement, negated, taken across a 3 s window rather than
between adjacent samples. At 4 Hz with a probe quantised to 0.0625 C, one
quantisation step between neighbours reads as 0.25 C/s of slope that is not
there, and with kd=0.5 that is a 0.125 swing in duty out of pure noise. On
hardware, adjacent-sample derivative turned a smooth demand into duty
hopping between 0 and 1 several times a second and cost roughly three times
the relay actuations.

Anti-windup is conditional integration: the integral accumulates only when
doing so would not push an already-saturated output further into the rail,
and unwinding is always allowed.

**Pre-charge** runs before the profile clock starts.

    PREHEAT  ->  PRECHARGE  ->  RUNNING

The element is driven at full duty with the clock held, while an observer
(`oven/elementff.py`) estimates its contribution to chamber rate. The run
starts when that reaches what the curve's opening needs, or at a 40 s
bound, and the oven then enters the profile wherever it has got to.

This exists because a warm start is a saturated-actuator problem, not a
gain problem: whenever the loop without it was more than 8 C behind, duty
was 1.00 for 100% of that time. A state-feedback feed-forward was tried
first and moved the worst-case lag from -11.5 C to -11.5 C. The plant does
not care how hard it is asked; it cares when.

It only runs where the curve is actually asking for a rise. The guard is on
the slope for a reason: the natural-looking test, `rate + d*(T - Ta) > 0`,
collapses on a flat opening to *is the room warm*, and fired full duty for
0.6 s on a profile whose target was 14 C below ambient.

**Predictive tracking** acts on where the chamber will be, not where it is.
`Controller.duty_for` takes the observer's estimate `z` and evaluates the
feed-forward and the PID on the curve `lead_s` ahead, against

    z_ss  = (g*u_last + gamma*(T - Ta)) / beta
    T_pred = T + z_ss*lead + (z - z_ss)*(1 - exp(-beta*lead))/beta
             - d*(T - Ta)*lead

The prediction assumes the loop keeps applying its last duty. Assuming
instead that the element decays over the lead ran the oven 0.85 C hot on
average, because the loop was driving it; this form is unbiased to 0.05 C
with half the spread.

`lead_s` is 6 s, from `predictive.lead_s` in the characterisation. Swept on
the identified plant, 4-6 s roughly halves heating-phase rms on every
profile and start temperature; 10 s and beyond overshoots, because the
prediction trusts the observer more than it deserves.

With no element model, or no element state passed in, both pre-charge and
the lead switch themselves off and the loop is a plain FF+PID. An oven
whose characterisation lacks `element_model` runs that way, and
`tests/test_predictive.py` holds it to it.

**Predictive peak cutoff.** Once `predict_peak(temp, rate, coast_tau)`
reaches the profile's peak, duty goes to zero and latches. It releases when
the oven falls more than 1 C below target, which is what lets a profile
HOLD at peak to earn time above liquidus. An earlier version also required
the target to be below the peak and silently coasted through the whole
dwell.

**TimeProportional** turns duty into relay states: a 4 s window, minimum
0.8 s on and off, one window for every profile. A 30 s window would cut
relay wear on a four-hour bake by roughly eight times, but the oven climbs
at over a degree a second and a 30 s slug of heat overshoots by 35 C; 8 s
still costs 4.7 C. A bake exists to hold 125 C within a few degrees, and
trading that for relay life is the wrong way round.

## What it achieves, measured

Heating phase only -- the cooling tail is the door's error, not the loop's.

    run 0021  TS391SNL  25 C cold     0.95 C rms   worst lag -2.6
    run 0018  TS391SNL  34 C start    1.87 C rms   worst lag -5.3
    run 0022  TS391SNL  59 C start    1.13 C rms   worst lag -4.2
    run 0020  TS391LT   59 C start    0.78 C rms   worst lag -2.5

59 C is the hottest start the supervisor allows. For scale, the loop before
pre-charge and the lead managed 13.06 C rms with -32.0 C of lag from that
same start, and 2.47 C from its best cold start.

Peaks land within 0.9 C, time above liquidus is unmoved, and every run
passes its checks.

### The bake, where the relay wear is

A full four-hour run, 2026-09-16, empty oven, from the oven's own log:

                        rms      mean       closures/min   hold measured
    old loop (0015)     0.552              8.8            3.2 min
    current (0024)      0.240   +0.141 C   8.2            240 min

Better on both counts. No drift across the four hours -- 0.266, 0.238,
0.224, 0.234 rms by hour. Peak 125.9 C, both ramp limits passed, no faults.

## Where the loop still loses

Every run is 2 to 3 C behind between 80 and 120 C with the relay closed the
whole time. That is not the controller: it is the oven at full power on the
low end of the heating table, where the entries below 85 C are an
extrapolation and the first 37 s of the step test they came from were
transport dead time. Pre-charge shortens it and cannot remove it. Anything
further has to come from the plant -- a longer charge, or a curve whose
opening does not ask for what the oven cannot give there.

## Rolling back

Each baseline is an image plus the `code.py` that belongs with it, kept
outside the repository because `code.py` is not frozen and does not travel
with a `.uf2`. Rolling the firmware back without its `code.py` leaves a
board that boots and serves a dead page -- found by doing it.

    known-good-loop-2026-09-16   current
    known-good-loop-2026-09-10   the last loop before pre-charge

    ~/.bespoketoast/images/known-good/

To put one back: enter the bootloader (`tools/release.py`, or
`microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)` over
the console), copy the `.uf2` onto `PORTALBOOT`, then deploy its `code.py`.

## Rules any replacement has to keep

These are not style preferences. Each cost a run, a board, or a day.

1. **The relay fails safe and the supervisor is not part of the loop.**
   260 C hard ceiling, 70 C enclosure, rate and stall guards, ABORT always
   available. A controller may not assume the supervisor will catch it.
2. **One SPI call to the co-processor can block 227 ms against a 250 ms
   control deadline.** Nothing in the loop may talk to the network.
3. **Derivative over a window, never between adjacent samples.** 0.0625 C
   of quantisation at 4 Hz is 0.25 C/s of imaginary slope.
4. **Relay actuations are a cost.** A four-hour bake is where the wear is;
   the loop that replaces this one should count them.
5. **Composing a screen must not be able to kill a run**, and the loop must
   hold its cadence while it happens.
6. **The element is a state, not a delay to tune around.** A loop that sees
   only the chamber is guessing about half the plant.
7. **The measured rate tables are right.** They carry the nonlinearity of a
   radiative oven -- a factor of three in process gain between 80 C and
   240 C -- and any replacement that throws them away is starting behind.
