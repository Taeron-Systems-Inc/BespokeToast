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
