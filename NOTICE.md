# Notice

## The firmware in this tree

`firmware/` is original work, released under the MIT licence. Every module
carries an SPDX header and `LICENSE` holds the full text.

It is **not** a derivative of the controller it replaced. That controller --
Adafruit's EZ Make Oven, written by Dan Cogliano for Adafruit Industries and
adapted for this oven in 2023 -- is in this repository's history at tag `v1`,
and `LICENSE` carries its copyright line because that history is part of the
repository.

For the avoidance of doubt, measured rather than asserted: the `v1`
controller is 416 lines and the current `code.py` is 1394, and they have no
line in common. The rewrite shares the hardware and the problem, not the
code.

An earlier version of this file claimed the opposite -- that `code.py` was
Adafruit's work with six restored header lines as its "sole" difference.
That was true when it was written and became false at the rewrite.

## Third-party components

**CircuitPython and the Adafruit libraries** the firmware depends on are not
committed here. They are redistributable builds carried on the device, and
the set the firmware expects is listed in `docs/frozen-build.md` -- which
also explains why a copy of any of them on the volume is actively harmful.

**Fonts.** `firmware/assets/fonts/` holds B612, released under the SIL Open
Font Licence. The licence travels with them in
`firmware/assets/fonts/OFL.txt`.

**Brand assets.** `firmware/assets/taeron-logo-*.bmp` are Taeron Systems'
own.
