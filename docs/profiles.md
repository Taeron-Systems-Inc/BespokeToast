# Profiles

One per paste, named the way the syringe is labelled.

Long rationale lives here rather than in a profile's `notes` field, because
a profile has to fit through the oven's own upload: measured ceiling 2700
bytes, limit set at 2560. A profile that cannot be sent back to the oven it
came from is one you can only change over USB, behind two screws.

## The curves are generated

`data/profile-specs.json` says what each profile is metallurgically -- soak
here, peak there, this much time above liquidus -- and
`tools/make_profile.py` turns that into points using the measured rate
tables in `data/oven-characterisation.json`.

    python3 tools/make_profile.py            # what would change
    python3 tools/make_profile.py --write    # regenerate
    python3 tools/make_profile.py --check    # CI: has anything drifted?

A test asserts every shipped file is byte-identical to what its spec
generates. Before that, three profiles claimed to be derived from the
characterisation while nothing derived them: the points had been worked out
once by hand, the characterisation was measured twice more, and the curves
never moved because moving them meant somebody redoing the arithmetic.

Two consequences worth knowing. `cooling_assumes_open_door` is derived --
whether a curve outruns door-shut cooling is arithmetic, not a flag. And
points are placed by chord error rather than at fixed temperature spacing,
because the stored profile is read back by linear interpolation: at 0.25 C
of chord error TS391SNL needs 25 points where even spacing needed 64, and
the file went from 2717 bytes -- over the upload limit -- to 1954.

## TS391SNL -- Sn96.5/Ag3.0/Cu0.5, mp 217-220 C

Chip Quik TS391SNL rev 1.2, generated from measurement rather than from the
datasheet chart, because the chart asks for ramps this oven does not have:
175 -> 217 C wants 1.40 C/s against about 0.90 available, and 217 -> 249 C
wants 1.07 against about 0.63 measured. Running it anyway would not fail
loudly; it would miss both ramps and produce a joint nobody characterised.

**Peak is 245 C**, 28 C above liquidus and mid-range for what a SAC305
joint wants (20-40), with 8 C of margin against what this oven has been
shown to reach. The datasheet's 249 C is not adopted: nothing there is
better for the joint, and 245 leaves 15 C to the supervisor's ceiling on a
profile whose whole top segment is at 80% of capability.

**The ramp into peak is not met and no profile can fix it.** 1.07 C/s asked
over 217-249 C against 0.63 measured; the last thirty degrees are climbed
at roughly three-fifths of the specified rate. That is the oven.

There is no hold at peak. The climb and fall earn 88 s above liquidus
unaided, near the middle of the 60-150 window, and put only 17 s within 5 C
of peak where J-STD-020 caps 30.

## TS391LT -- Sn42/Bi57.6/Ag0.4, mp 138 C

Chip Quik TS391LT rev 1.3, at every point the datasheet states: 90 C at
90 s, 130 C at 180 s, liquidus at 210 s, peak 165 C at 240 s, back through
liquidus at 270 s. This oven can follow all of it -- the steepest demand is
138 -> 165 C in 30 s, 0.90 C/s, against about 1.31 available.

**The opening is this oven's, and it is the one departure.** Between 0 and
90 s the datasheet chart has no gridlines, and the points that used to be
there were somebody's reading of the line -- 45 C at 15 s asks 1.33 C/s
from cold where this oven does about 0.58. The controller saturated against
a target it could not reach, wound up, and overshot when the curve
slackened: 23 C of tracking error before the paste had done anything. The
opening now follows the measured rate curve, scaled to land exactly on 90 C
at 90 s, which the datasheet does specify. Nothing above 90 s changed.

The datasheet gives a maximum operating temperature of 96 C after assembly.
A board built with this paste must not be baked or held above that
afterwards, which is why there is no Hold 150 C profile.

## NC191LTA10 -- Sn42 Bi57 Ag1, mp 137 C

Chip Quik's own curve. Process-interchangeable with TS391LT: the same chart
shape, one degree apart at liquidus, and the same generated opening for the
same reason. Not separately validated on hardware, because it would test
the same code against the same measurement.

**Its window is 60-90 s and the door is what decides it.** Across three
runs the oven asked for the door at the same instant every time -- within a
second of each other, both with 71 s banked -- and the outcome ranged from
a pass at 76 s to a failure at 98 s to a failure at 132 s. The variable is
the delay between the prompt and the hand, and 26 s of it was the whole
difference between a pass and a failure. That is what the countdown is for:
a prompt that appears at the moment the door is needed has already spent
its margin.

## Bake 125 C

J-STD-033 high-temperature bake for moisture-sensitive devices. Not a
reflow profile, no liquidus, 4 h 13 min.

The climb runs at 40% of capability with the last ten degrees at 0.15 C/s.
Rapid heating of a part that is already wet is the failure this bake exists
to prevent, so climbing at the oven's maximum was the one thing it should
not do, and slowing it costs twenty seconds on a four-hour run. Overshoot
is 0.44 C against a J-STD-033 allowance of 5.

Validated over a full run: 0.240 C rms across four hours of hold, mean
+0.141 C, no drift, peak 125.9 C. The enclosure's cold junction reaches
about 48 C against a 70 C fault -- this is the longest soak the oven does
and it has around 20 C of headroom.

## DIAGNOSTIC fast

Not offered to whoever is choosing. It melts nothing, peaks at 95 C, and
exists to exercise preheat, soak, a liquidus crossing, peak, cooldown,
report, every screen and the console in 84 seconds. `liquidus_c` is 80 C
purely so the run crosses it; the number means nothing metallurgical, and
its 10-400 s window measures how long the room takes to cool the oven back
through 80 C, which is not a property of the profile.

It peaks around 102 C against the 95 asked, and that does not improve with
a gentler climb -- the fixture is too short for the oven to settle before
it ends, so the overshoot happens in cooldown on stored element heat.

Worth recording against the simulator rather than the profile: the host
harness predicts this one 5.7 C low, while reproducing every reflow profile
to within 1-3 C and the bake to 0.05. Trust it for a curve the oven has
time to follow; do not trust it for this fixture.

**It is also the only profile that exercises preheat**, holding 45 C at
half power before the run clock starts.

## STEP 250 C

Not a soldering profile and not offered at the oven. Full power to 250 C,
half a minute at the top, then free cooling with the door SHUT -- the
cooling curve is the measurement, and it is where the cooling table comes
from. Run it empty, and do not open the door until the run ends.

The descent follows the measured passive curve rather than a straight line,
because a curve steeper than free cooling makes the controller top the oven
back up on the way down: the first version stopped driving at 232 C, below
where the table already reached, and so extended nothing. It now hands over
187 degrees of clean free fall from 245 C.

**The table stops at 245 C, not 250.** For the first ten seconds after the
relay opens the rate is still settling as the element sheds its own heat --
+0.09 C/s at the instant of opening, -0.36 at four seconds, -0.75 by ten --
so anything above 245 would be element decay recorded as free cooling.

One caution for whoever measures it next. Chamber temperature alone does
not fully predict cooling: a run that held a minute at the top cools 5-20%
slower than the table at every temperature, with a cold junction 6 C hotter.
A hotter body radiates back into a cooling chamber. The table is right for
an oven in the state it was measured in.

## What the door does, measured

Timed against a known door-open instant -- the firmware asked at 281.7 s
and the operator opened within a second:

    onset                    1-2 s
    full effect              about 3 s
    peak rate                -8.31 C/s at about 4 s
    door shut, same temp     -0.44 C/s

A nineteenfold change in cooling rate, showing at the probe inside two
seconds.

`DOOR_COOLING_C_PER_S = 5.2` is the average over a whole descent, not the
peak: the rate decays as the gap to ambient closes, through -4.8, -3.2,
-2.2. That average is what the countdown uses, and it predicted a 158 ->
137 C descent in 4.0 s against 4.3 s measured, landing that run's time
above liquidus on 75 s against the 75 s it aimed for.
