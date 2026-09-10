# Profiles

One per paste, named the way the syringe is labelled. The qualifiers that
used to be in the names -- "(this oven)", "(datasheet)" -- only existed to
tell two curves for one paste apart, and after the review each paste has
one.

Long rationale lives here rather than in a profile's `notes` field,
because a profile has to fit through the oven's own upload: measured
ceiling 2700 bytes, limit set at 2560. A profile that cannot be sent back
to the oven it came from is a profile you can only change over USB, behind
two screws.

## The curves are generated

`data/profile-specs.json` says what each profile is metallurgically --
soak here, peak there, this much time above liquidus -- and
`tools/make_profile.py` turns that into points using the measured rate
tables in `data/oven-characterisation.json`.

    python3 tools/make_profile.py            # what would change
    python3 tools/make_profile.py --write    # regenerate
    python3 tools/make_profile.py --check    # CI: has anything drifted?

This is new, and it replaces three profiles that said they were derived
from the characterisation while nothing derived them. The points had been
worked out once, by hand; the characterisation was then measured twice
more and the curves never moved, because moving them meant somebody
redoing the arithmetic. A test asserts every shipped file is byte-identical
to what its spec generates, so that cannot happen again.

Two things follow from it that were previously somebody's job to remember.
`cooling_assumes_open_door` is now derived -- whether a curve outruns
door-shut cooling is arithmetic on the curve and the measurement, not a
flag. And points are placed by chord error rather than at a fixed
temperature spacing: the stored profile is read back by linear
interpolation, so what matters is how far the chord between two points
strays from the curve they came from. At 0.25 C of chord error TS391SNL
needs 25 points where even spacing needed 64, and the file went from 2717
bytes -- over the upload limit -- to 1954.

## TS391SNL -- Sn96.5/Ag3.0/Cu0.5, mp 217-220 C

Chip Quik TS391SNL rev 1.2. Generated from measurement rather than from
the datasheet chart, because the chart asks for ramps this oven does not
have:

    175 -> 217 C in 30 s     1.40 C/s asked, about 0.90 available
    217 -> 249 C in 30 s     1.07 C/s asked, about 0.63 measured

Running it anyway would not fail loudly. It would miss both ramps and
produce a joint nobody characterised.

**Peak is 245 C.** It was 235, set when the step tests had only reached
240; run 0008 then reached 252.8 C and 235 stopped being the ceiling the
evidence imposed. 235 C is 18 C above liquidus, and a SAC305 joint wants
20-40 -- so the old peak sat just under the bottom of the range that makes
the joint, and it was there for want of data rather than for a reason.
245 C is 28 C above, mid-range, and 8 C inside what this oven has been
shown to do.

The datasheet's 249 C is not adopted. Nothing here is 4 C better than
245 for the joint, and 245 leaves 15 C to the supervisor's ceiling on a
profile whose whole top segment is at 80% of capability.

What is still not met is the *ramp* into peak. 1.07 C/s over 217-249 C
against 0.63 measured; the last thirty degrees are climbed at roughly
three-fifths of the specified rate whatever the peak says. That is a
property of the oven and no profile can fix it.

The hold at peak is gone. At 235 C the climb and the fall earned 56 s
above liquidus and a 32 s dwell had to be added to clear the 60 s floor.
At 245 C they earn 88 s unaided, which is nearer the middle of the 60-150
window and puts only 17 s within 5 C of peak -- J-STD-020 caps that at 30.

Simulated against the measured plant, before and after:

    peak      238.5 C  ->  246.2 C      (asking 235 -> 245)
    TAL        95.5 s  ->   90.6 s
    mean error  2.63 C ->    1.86 C

Recorded on the old curve, run 0003: peak 236.4 C, TAL 96 s, mean
tracking error 4.02 C.

### Run 0011, 2026-09-10: the new curve, on hardware

    peak                    246.69 C   (asked 245, simulated 246.2)
    time above liquidus        97.7 s  (window 60-150)
    max ramp up                2.00 C/s (limit 2.5)
    time to peak                305 s  (limit 480)
    cold junction max         48.06 C  (fault at 70)

Every check passed. The peak sits 29.7 C above liquidus, inside the 20-40
the alloy wants; run 0003 on the old curve sat 19.4 above, below it.

It was also the first **warm start** on hardware -- the oven was at 34.1 C
and the run entered the profile 33.9 s in -- and that turned up the one
blemish.

#### A warm start enters past the oven's own dead time

The generated opening encodes this oven's cold-start transport lag: the
curve barely moves for its first thirty seconds, because the measured rates
below 85 C describe an element that has not woken up yet. Entering at 33.9 s
skips that, and asks the oven to be already accelerating while its element
is stone cold:

    elapsed   target   actual     lag
       40       39.4     34.0     -5.4      the probe has not moved at all
       60       64.1     41.5    -22.6
       70       78.4     54.4    -24.0      worst
       90      106.8     90.3    -16.5
      110      131.9    124.8     -7.1
      130      151.4    153.0     +1.6      ahead, and level from here

Twenty-four degrees, closed by elapsed 130 s and gone before the soak. The
run passed every check and the joint would not know. But it is a real
interaction between two features that were each tested alone: the profile
generator shapes an opening around measured dead time, and entry_time_for
credits the oven for time it has not thermally done.

#### And it does not need fixing, which was measured rather than argued

The warmest start the supervisor allows is 60 C. Run 0013 took it: oven at
59.4 C, entered 56.9 s in, where the curve is 55% steeper than at run 0011's
entry. That is the worst case this oven can produce, and the two runs put
the whole range on record:

    start      entry     worst lag     peak       TAL
    34.1 C     33.9 s      -24.3 C    246.69 C    97.7 s
    59.4 C     56.9 s      -32.2 C    246.75 C    99.5 s
    cold        0.0 s        -5 C     (simulated) --

Eight more degrees of transient for twenty-five more degrees of start
temperature, and the outcome does not move: the peaks are 0.06 C apart and
the time above liquidus 1.8 s apart. The joint sees the same process.

The lag is also self-limiting for a reason worth writing down. A warmer
oven enters at a steeper part of the curve, which should make the lag worse
-- but a warmer oven has just come off a run, so its element is warmer too
and the transport lag is shorter. The two effects push opposite ways.

So it stays. It is a transient in the display, below 90 C, gone before the
soak, and the alternatives all make things worse: entering earlier puts the
target below the oven and stops the controller driving at exactly the moment
the element needs waking, and the real remedy -- pre-charging the element
before the run clock starts -- is a controller feature, not a profile tweak,
and would be an untested change to something that passes every check.

## TS391LT -- Sn42/Bi57.6/Ag0.4, mp 138 C

Chip Quik TS391LT rev 1.3, at every point the datasheet actually states:
90 C at 90 s, 130 C at 180 s, liquidus at 210 s, peak 165 C at 240 s, back
through liquidus at 270 s. This oven can follow all of it -- the steepest
demand is 138 -> 165 C in 30 s, 0.90 C/s, where capability is about 1.31.

### The opening is this oven's, and it is the one change

Between 0 and 90 s the datasheet chart has no gridlines, and the points
that used to be there were somebody's reading of the line: 45 C at 15 s,
60 C at 30 s, 72 C at 45 s. The first of those asks 1.33 C/s from cold and
this oven does about 0.58 there, transport lag included. So both trial
runs opened the same way:

    45 C    curve  15 s    actual  34.5 s    21 s behind
    60 C           30 s            43.3 s    13 s behind
    80 C           60 s            55.5 s     5 s ahead
    90 C           90 s            74.5 s    15 s ahead

Behind, then ahead: the controller saturates against a target it cannot
reach, the integrator winds up, and the oven overshoots when the curve
finally slackens. Worth 23 C of tracking error, all of it before the paste
has done anything, and it is why these two profiles had the worst tracking
of the set.

The opening now follows the measured rate curve, scaled to land exactly on
90 C at 90 s -- which the datasheet does specify. Simulated, over the
first two minutes:

    worst error   24.3 C  ->  7.1 C
    mean error    11.1 C  ->  under 4 C (asserted by a test)

Nothing above 90 s changed, so every number the manufacturer gives is
still hit at the second they give it.

#### Run 0014, 2026-09-10: on hardware

    worst error, first 120 s     -6.6 C     (old curve: -23 to +15)
    mean |error|, first 120 s     2.69 C    (simulated under 4)
    peak                        168.4 C     (window 155-175)
    max ramp up                   1.80 C/s  (limit 2.5)

The opening is the single biggest tracking improvement in this firmware, and
it is now measured rather than simulated. The old curve had the oven 21 s
behind the line at 45 C and 15 s ahead of it at 90 C -- saturating against an
impossible target, winding up, then overshooting when the curve slackened.
It now sits within seven degrees of the line the whole way up.

Time above liquidus came out at **125 s against a 60-90 window, and that is
the door, not the curve**. This run was deliberately left shut. The oven
asked for it at the right moment -- 71.4 s of time above liquidus banked at
157.8 C, aiming for the middle of the window -- and nobody opened it, which
is the same failure run 0001 recorded at 132 s. Run 0007 opened on the
prompt and landed 76 s. Nothing about the profile changed that.

NC191LTA10 is not separately re-run. Its opening is generated by the same
code from the same measurement and differs only in the one degree of
liquidus; running it would test the same thing twice.

The datasheet also gives a maximum operating temperature of 96 C after
assembly. A board built with this paste must not be baked or held above
that afterwards -- which is why there is no longer a Hold 150 C profile.

Run 0005, 2026-09-08: peak 169.8 C, TAL 83 s, max ramp 1.89 C/s, time to
peak 249 s. Every check passed on the first attempt, which no other reflow
profile here has done. The door prompt came at 282.2 s with 71.1 s of TAL
already banked, and the door was opened on it.

## NC191LTA10 -- Sn42 Bi57 Ag1, mp 137 C

Chip Quik's own curve. Process-interchangeable with TS391LT: the same
chart shape, one degree apart at liquidus, and the same generated opening
for the same reason.

| run | date | peak | TAL | verdict |
|---|---|---|---|---|
| 0001 | datasheet curve | 169.7 C | 132 s | FAILED, door never opened |
| 0006 | 2026-09-08 | 169.3 C | 98 s | FAILED by 8 s |
| 0007 | 2026-09-08 | 169.3 C | 76 s | passed |

The window is 60-90 s and the paste is the same in all three. What differs
is when the door opened, and the oven asked for it at the same instant
every time: 280.6 s in run 0006 and 281.7 s in run 0007, both with 71 s of
TAL banked and about 19 s of profile left. So the prompt is not the
variable -- the delay between the prompt and the hand is, and 26 s of it
was the whole difference between a failure and a pass.

That is what the countdown is for. A prompt that appears at the moment the
door is needed has already spent its margin; run 0007 was opened "within
less than 1 s" of it and still landed 16 s of the 30 s window away from
the middle.

## Bake 125 C

J-STD-033 high-temperature bake for moisture-sensitive devices. Not a
reflow profile and has no liquidus. 4 h 13 min.

Run 0009, 2026-09-09: peak 127.2 C against a 125 C target, and over the
four hours after the approach settled the chamber held 125.0 C mean with a
band of +/-1.0 C and a mean error of +0.001 C. J-STD-033 asks for 125 +/- 5,
so the overshoot spends 2.2 C of a 5 C allowance and the hold spends
almost none of it. Duty was 16.2%.

The prediction on record before the run was 135 C -- a 10 C overshoot,
which would have failed. It was wrong by 8 C. Simulating the same profile
through the real controller against the measured plant gives 127.15 C
against the 127.19 measured, so the plant model was never the problem and
the 135 came from somewhere that is not this harness.

### The ramp changed anyway, and not because of the overshoot

The old curve climbed at close to the oven's maximum. Rapid heating of a
part that is already wet is the failure this bake exists to prevent, so
that was the one thing a moisture bake should not do, and it cost nothing
to fix: the climb is now at 40% of capability and the last ten degrees at
0.15 C/s, reaching 125 C at 259 s instead of 239 s. Twenty seconds, on a
four-hour run.

The overshoot improves as a side effect, and by far more than simulated.
Run 0015, 2026-09-10, started from 30.3 C and aborted once it had settled:

    peak                 125.44 C     overshoot 0.44
    run 0009, old curve  127.19 C     overshoot 2.19
    simulated            126.70 C     overshoot 1.70

Five times less overshoot, where the model promised less than two. J-STD-033
allows plus or minus five, so the old curve was never failing -- but 0.44 C
of it leaves the whole allowance for a bake started on a warm oven, which is
the case this has to survive and the one nobody has run.

It reached 125 C at 256 s against the old curve's 239. Seventeen seconds,
for that, on a four-hour run.

The run was aborted deliberately at the setpoint rather than held: the
four-hour hold is what run 0009 validated, at 125.0 C mean with a band of
+/-1.0, and nothing about this change touches it. What changed is the
approach, and the approach is over by 260 s.

Enclosure cold junction reached 48.3 C at t=11539 s and was still rising
slowly when the run ended, against a 70 C fault. Four hours is the longest
soak this oven has done and it has 21 C of headroom.

## DIAGNOSTIC fast

Not offered to whoever is choosing. It melts nothing, peaks at 95 C, and
exists to exercise preheat, soak, a liquidus crossing, peak, cooldown,
report, every screen and the console in 84 seconds. `liquidus_c` is 80 C
purely so the run crosses it; the number means nothing metallurgical.

Run 0004, 2026-09-08: peak 103.5 C against a 95 C target, and one FAILED
check -- max ramp up 3.20 C/s against a 2.5 limit.

Both were the fixture being too abrupt, and both are addressed.

The 8.5 C overshoot came from the climb running at the oven's maximum on a
curve too short to settle. At 55% of capability the simulated peak is
96.8 C.

The 3.20 C/s is more interesting, because this oven cannot do it. The step
tests peak at 1.85 C/s near 80 C; the run's own log gives 1.58; simulating
the profile end to end gives 1.84; and every other run that day reported
1.87 to 2.03. What could produce it is that the rate window had an upper
bound of 5 s and no lower bound at all, so for the first seconds of a run
it was measuring over a fraction of a second, where a degree of
thermocouple noise is several degrees per second. There is now a 3 s
floor. The 4 Hz samples that produced 3.20 were never captured, so that is
the mechanism and not a proof about that run -- but a rate measured over a
third of a second is not a ramp rate either way, and the floor changes
nothing on any run logged at 1 Hz or slower, which is all of them.

Its time-above-liquidus window is 10-400 s rather than 10-200. What that
number actually measures on this fixture is how long the room takes to
cool the oven back through 80 C after the run ends, which is not a
property of the profile, and 187 s of it was already most of the old
ceiling.

Run 0012, 2026-09-10, on the gentler curve: **peak 102.5 C**, inside the
85-105 window and barely better than the 103.5 C the old curve produced.
Dropping the climb to 55% of capability was worth one degree. The fixture is
84 s long and simply does not run long enough for the oven to settle before
it ends -- its overshoot happens in cooldown, coasting on stored element
heat, and the ramp is not what puts the heat there.

Worth recording against the simulator rather than the profile: the host
harness predicted 96.8 C, out by 5.7. It reproduces every reflow profile to
within 1-3 C and the bake to 0.05, and it is worst on the one profile that
is shortest and the only one with a preheat. Trust it for a curve the oven
has time to follow; do not trust it for this fixture.

It does exercise preheat, which is the point: run 0012 held 45.00 C at half
power from a 26 C start before the run clock began, which no other profile
does.

## What the door actually does, measured

Run 0007, NC191LTA10, 8 September 2026. The first time this has been
measured against a known door-open instant: the firmware asked at
elapsed 281.7 s and the operator reports opening it inside a second, so
the door was open by about 282.2.

    281.7   158.00 C   -0.25 C/s    "now"
    282.7   157.38     -0.62        first departure from baseline
    283.9   155.88     -1.25        unambiguous
    285.2   148.69     -5.53        full effect
    286.2   140.38     -8.31        peak rate

The ten seconds before it are flat at -0.44 C/s, so the departure is not
in doubt.

    onset          1-2 s
    full effect    about 3 s
    peak rate      -8.31 C/s at about 4 s
    shut, same temperature   -0.44 C/s

A nineteenfold change in cooling rate, showing at the probe inside two
seconds. Uncertainty is about a second either way: the log samples at
1 Hz and "inside a second" is the other half of it.

The peak rate is well above the -5.2 C/s this project has been quoting.
Both numbers are right about different things -- the rate decays as the
gap to ambient closes, through -4.8 and -3.2 and -2.2, so the average
over a whole descent lands near 5.

That average is what `DOOR_COOLING_C_PER_S = 5.2` is used for, and this
run is the first evidence for it:

    predicted descent   4.0 s     (158 -> 137 C at 5.2 C/s)
    actual              4.3 s

which is why the countdown lands where it does. That run aimed at the
middle of the profile's window, (60 + 90) / 2 = 75 s, and measured 75 s.

Two earlier figures published for this were wrong -- a "slow operator"
and a "60 s thermal lag" -- both from inferring the door time rather
than knowing it. The difference here is that the oven timestamped the
request and the operator reported against it.

## STEP 250 C

Not a soldering profile and not offered at the oven. Full power to
250 C, half a minute at the top, then free cooling with the door SHUT --
the cooling curve is the measurement.

It exists because every lead-free profile is built from the measured
heating and cooling tables, and the cooling table still stops at 235 C.
The heating side is done: run 0008 took it to 248.

Run it empty, and do not open the door until the run ends.

Run 0008, 2026-09-08: peak 252.8 C, reached in 261 s, max ramp 2.03 C/s.
The door was kept shut for the whole 600 s and the log ran on past it, so
the free-fall curve is the longest and cleanest this oven has produced.

It also appeared to show that chamber temperature alone does not predict
cooling: between 180 and 224 C it fell at 0.62-0.69 of the rate the table
gave, converging to 0.97 by 81 C. The reading at the time was that the oven
body was hotter than when the table was measured -- cold junction 53.4 C
against 41.8 -- and a hotter body radiates back into a cooling chamber. The
table was not rewritten, on the grounds that one run cannot separate "the
table is wrong" from "the table is right for a cooler oven".

**Run 0010 separated them, and it was mostly the first.** See below.

The check line "time above liquidus FAILED 1033 s" in this log is not a
result. STEP 250 C has no liquidus, and the guard that suppresses that
check was flashed after this run; run 0009 shows the check correctly
absent.

### Why it extended nothing on the cooling side, and what changed

The profile's own note blamed the one-minute hold at the top. That was
wrong. The relay was still firing at 333 s with the oven down to 232 C, so
the highest clean free-cooling sample was 224 C -- below where the table
already reached -- and the cause was the descent, not the hold:

    the curve asked   250 -> 80 C over 300 s      -0.57 C/s
    the oven falls    at 235 C, relay open        -0.72 C/s

The oven outran its own target downwards, so the controller kept topping
it back up. The descent now follows the measured passive curve, which the
oven cannot outrun. Simulated against the measured plant, that moves the
last firing of the relay from 232 C to 251 C, which is the entire point of
running it again.

The hold stays, at 30 s rather than 60. Removing it was tried and the
first attempt made the run peak at 212 C -- but that was a climb asking
twice the oven's capability, not the missing hold. With the climb matched
to capability the hold is worth about 5 C of peak and 5 C of where the
relay stops firing, and 60 s buys nothing that 30 does not.

### Run 0010, 2026-09-10: what it was for

    peak                    252.94 C   (simulated 253.04)
    relay last fired at     250.94 C   (run 0008: 232 C)
    cold junction max        47.31 C   (fault at 70)
    free cooling            3762 samples, 245.1 C to 58.4 C, relay open

That second line is the entire point of rebuilding the profile. Run 0008
stopped driving at 232 C, below where the cooling table already reached, so
it extended nothing. This one hands over 187 degrees of clean free fall.

**The cooling table is now this run**, replacing the one stitched from the
two 2026-08-25 step tests. That table had two artifacts at its seams -- a
25% discontinuity at 190->195 C and 8.7% at 230->235 C where measurement
gave way to flat extrapolation -- and they made it non-monotonic: it had the
oven shedding heat *faster* at 190 C than at 225 C, which cannot be true of
loss to a fixed ambient. The new one has a single 0.9% inversion at the top,
in the two smallest bins.

Validated against run 0008, which it was not built from: mean absolute error
0.048 C/s against the old table's 0.151, over 225.9 to 134.7 C. 3.2 times
closer.

The residual is the real effect the artifact was hiding. Run 0008 still
cools 5-20% slower than this table at every temperature, consistently and
without a seam, and its body was hotter -- cold junction 53.4 C against
47.3, because it held a minute at the top where run 0010 held thirty
seconds. So the original observation was two things: a table artifact, and a
body-heat effect about a third its size. Only the first is fixed.

The table stops at 245 C, not 250. For the first ten seconds after the relay
opens the rate is still settling as the element sheds its own heat --
+0.09 C/s at the instant of opening, -0.36 at four seconds, -0.75 by ten --
so anything above 245 would be element decay recorded as free cooling.

Three profiles changed as a result, all of them the ones whose cooling tails
are generated: TS391SNL's run is 33 s longer, and the bake's and the step
test's tails follow the slower curve. The two low-temperature pastes are
untouched, because their tails are the manufacturer's straight lines rather
than this oven's measurement.
