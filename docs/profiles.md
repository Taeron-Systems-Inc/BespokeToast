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

## TS391SNL -- Sn96.5/Ag3.0/Cu0.5, mp 217-220 C

Chip Quik TS391SNL rev 1.2. The curve is derived from measurement, not
from the datasheet chart, because the chart asks for ramps this oven does
not have:

    175 -> 217 C in 30 s     1.40 C/s asked, about 0.90 available
    217 -> 249 C in 30 s     1.07 C/s asked, about 0.70 available

Running it anyway would not fail loudly. It would miss both ramps and
produce a joint nobody characterised.

Peak is 235 C rather than 249 C. That was set when the step tests had only
reached 240 C. Run 0008 has since reached 252.8 C, so the temperature is
demonstrated and 235 is no longer the ceiling the evidence imposes.

Raising it is a decision nobody has made yet, and it is not the same
decision as reaching the temperature. The datasheet's *ramp* into peak,
1.07 C/s over 217-249 C, is still unachievable: run 0008 measured 0.63 C/s
in that band at full power. A profile peaking at 245-249 C would therefore
climb the last 30 C more slowly than the paste specifies, whatever its
peak says.

Rise segments run at 80% of the measured full-power rate so the controller
has headroom instead of saturating. The peak is held briefly to earn time
above liquidus, which the oven cannot earn on the way up.

Recorded: peak 236.4 C, TAL 96 s, mean tracking error 4.02 C.

## TS391LT -- Sn42/Bi57.6/Ag0.4, mp 138 C

Chip Quik TS391LT rev 1.3, datasheet curve unmodified, because this oven
can follow it: the steepest demand is 138 -> 165 C in 30 s, 0.90 C/s,
where capability is about 1.31.

The datasheet also gives a maximum operating temperature of 96 C after
assembly. A board built with this paste must not be baked or held above
that afterwards -- which is why there is no longer a Hold 150 C profile.

Run 0005, 2026-09-08: peak 169.8 C, TAL 83 s, max ramp 1.89 C/s, time to
peak 249 s. Every check passed on the first attempt, which no other reflow
profile here has done. The door prompt came at 282.2 s with 71.1 s of TAL
already banked, and the door was opened on it.

## NC191LTA10 -- Sn42 Bi57 Ag1, mp 137 C

Chip Quik's own curve. Process-interchangeable with TS391LT: the same
chart shape, one degree apart at liquidus.

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
which would have failed -- extrapolated from the DIAGNOSTIC profile
overshooting 8.5 C. It was wrong by 8 C, and pessimistically: the
simulation does not have the four hours of thermal mass the real oven
brings to a setpoint it is going to sit at. No profile change is needed.

Enclosure cold junction reached 48.3 C at t=11539 s and was still rising
slowly when the run ended, against a 70 C fault. Four hours is the longest
soak this oven has done and it has 21 C of headroom.

## DIAGNOSTIC fast

Not offered to whoever is choosing. It melts nothing, peaks at 95 C, and
exists to exercise preheat, soak, a liquidus crossing, peak, cooldown,
report, every screen and the console in 84 seconds. `liquidus_c` is 80 C
purely so the run crosses it; the number means nothing metallurgical.

Run 0004, 2026-09-08: peak 103.5 C, and one FAILED check -- max ramp up
3.20 C/s against a 2.5 limit. That is the profile asking for a ramp its
own limits forbid, not the oven misbehaving: the fixture is 84 s long and
gets from 25 to 104 C inside it, which is steeper than anything a real
paste asks for. Either the limit belongs to the profile or the fixture
should be gentler; until one of those is decided, a clean DIAGNOSTIC run
shows one red line and that is expected.

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
250 C, a minute at the top, then free cooling with the door SHUT --
the cooling curve is the measurement.

It exists because the measured heating table stops at 235 C and the
cooling table at 240, and every lead-free profile is built from both.
TS391SNL's peak sits at 235 C for exactly that reason: the datasheet
asks 249 and nothing here has ever been demonstrated above 240.

Ten minutes: about 3.5 to reach 250 from cold, one at the top, and the
rest falling. Simulated peak 248.4 C against a 260 C supervisor ceiling.
Run it empty, and do not open the door until the run ends.

Run 0008, 2026-09-08: peak 252.8 C, reached in 261 s, max ramp 2.03 C/s.
The door was kept shut for the whole 600 s and the log ran on past it, so
the free-fall curve is the longest and cleanest this oven has produced.

It also showed that chamber temperature alone does not predict cooling.
Between 180 and 224 C this run fell at 0.62-0.69 of the rate the existing
table gives for those temperatures, converging to 0.97 by 81 C. The oven
body was hotter than when the table was measured -- cold junction 53.4 C
against 41.8 -- and a hotter body radiates back into a cooling chamber.
The table was NOT rewritten from this run: one run cannot separate "the
table is wrong" from "the table is right for a cooler oven", and the
second is the more likely reading.

The check line "time above liquidus FAILED 1033 s" in this log is not a
result. STEP 250 C has no liquidus, and the guard that suppresses that
check was flashed after this run; run 0009 shows the check correctly
absent.
