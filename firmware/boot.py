# SPDX-License-Identifier: MIT
"""Runs before code.py, on every reset.

The single job here is to put the relay in a known state before anything else
has a chance to fail. CircuitPython releases pins on reset and this oven has a
pulldown on the relay line, so the hardware default is already de-energised —
this makes it explicit rather than implicit, and covers the window before
code.py starts.
"""

import board
import digitalio

_relay = digitalio.DigitalInOut(board.D4)
_relay.direction = digitalio.Direction.OUTPUT
_relay.value = False
_relay.deinit()          # released; the pulldown holds it low
