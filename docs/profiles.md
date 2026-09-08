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

Peak is 235 C rather than 249 C. The step tests reached 240 C, so 249 C
has never been demonstrated on this oven and a profile that asks for it
would be extrapolating past the evidence. The 249 C step test on the trial
list settles whether that ceiling can move.

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

Never run. First trial pending.

## NC191LTA10 -- Sn42 Bi57 Ag1, mp 137 C

Chip Quik's own curve. Process-interchangeable with TS391LT: the same
chart shape, one degree apart at liquidus.

Recorded: peak 169.7 C, TAL 132 s against a 60-90 s window -- a failure,
and the cause is the door. It was not opened at peak, so the joints sat
molten 42 s past the window. Re-run pending.

## Bake 125 C

J-STD-033 high-temperature bake for moisture-sensitive devices. Not a
reflow profile and has no liquidus. Never run; 4 h 15 min.

## DIAGNOSTIC fast

Not offered to whoever is choosing. It melts nothing, peaks at 95 C, and
exists to exercise preheat, soak, a liquidus crossing, peak, cooldown,
report, every screen and the console in 84 seconds. `liquidus_c` is 80 C
purely so the run crosses it; the number means nothing metallurgical.

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
