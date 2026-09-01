# SPDX-License-Identifier: MIT
"""Runs before code.py, on every reset.

Two jobs, in this order.

First: put the relay in a known state before anything else has a chance to
fail. CircuitPython releases pins on reset and this oven has a pulldown on
the relay line, so the hardware default is already de-energised -- this
makes it explicit rather than implicit, and covers the window before code.py
starts. Nothing below may get in the way of it.

Second: hand the filesystem to whoever should have it. See oven/bootmode.py
for why the decision is read out of non-volatile memory rather than taken
here: supervisor.runtime.usb_connected reads False inside boot.py even with
a cable attached, because CircuitPython starts USB after boot.py finishes.
"""

import board
import digitalio

# The relay first, unconditionally, before anything that could raise.
_relay = digitalio.DigitalInOut(board.D4)
_relay.direction = digitalio.Direction.OUTPUT
_relay.value = False
_relay.deinit()          # released; the pulldown holds it low

import microcontroller
import storage

from oven.bootmode import decode, name, owns_filesystem

_mode = decode(microcontroller.nvm)

# Said before the remount: boot.py's output goes to boot_out.txt, and once
# the filesystem is handed to the host CircuitPython can no longer write
# that file. Printing afterwards left the log empty and made a working
# change look like one that had never run.
print("# boot: filesystem to the %s%s" % (
    name(_mode),
    " (runs are recorded to /logs)" if owns_filesystem(_mode)
    else " (deploys work; runs are not recorded)"))

try:
    # readonly describes CircuitPython's own view: read-only for the oven
    # means writable for the host, and the other way round.
    storage.remount("/", readonly=not owns_filesystem(_mode))
except RuntimeError as e:
    # Not fatal. The oven runs fine without writing anything; it just
    # cannot keep its own record, and code.py reports that at boot.
    print("# boot: could not set filesystem ownership (%r); "
          "run logging will be unavailable" % e)
