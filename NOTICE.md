# Notice

`firmware/code.py` is a derivative work of **Adafruit's EZ Make Oven**
controller, written by Dan Cogliano for Adafruit Industries and released under
the MIT licence:

```
SPDX-FileCopyrightText: 2019 Dan Cogliano for Adafruit Industries
SPDX-License-Identifier: MIT
```

The controller was adapted for this oven in 2023. Over that work the original
SPDX header was dropped, which the MIT licence does not permit — it requires the
copyright and permission notice to travel with the code. The header has been
restored, and `LICENSE` carries the full text.

## The only edit to the firmware

Restoring those six header lines is the **sole** difference between
`firmware/code.py` here and the file on the device. The code itself is
unmodified and byte-identical below the header.

## Third-party components

The Adafruit CircuitPython libraries the firmware depends on are not committed
here; they are redistributable builds carried on the device. See
`docs/firmware.md` for the list.

Font and brand assets used by any future firmware carry their own licences and
are recorded alongside them when added.
