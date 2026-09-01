# SPDX-License-Identifier: MIT
"""Who owns the filesystem on the next boot, recorded where boot.py can read it.

CircuitPython can only write to CIRCUITPY when the USB host is not writing
to it, and the two cannot share. USB is present here for programming and
absent in normal use, so the oven should own the filesystem when it is
standalone -- that is the only time it can keep a record of a run, and the
only time anything else would.

The obvious signal does not work. supervisor.runtime.usb_connected reads
False inside boot.py even with a cable attached, because CircuitPython
starts USB *after* boot.py finishes. Sampling it handed the filesystem to
the oven while it was plugged in and locked the host out of its own volume;
polling for five seconds did exactly the same thing, because the flag never
becomes true during boot at all. Both times the fix had to go in over the
serial REPL, which worked only because the oven happened to have write
access at that moment.

So the decision is made a boot late, by whoever knows the answer. code.py
runs seconds later, when USB is up and usb_connected is reliable, and
records what it saw in microcontroller.nvm -- eight kilobytes of storage
that does not care who owns the filesystem. boot.py reads that byte.

The lag means the first boot after the cable changes uses the previous
answer. Unset or corrupt reads as HOST, because being wrong that way costs
one unrecorded run, and being wrong the other way costs a board nobody can
program.
"""

# Deliberately not 0 or 255: both are what uninitialised or erased flash
# reads as, and neither should be mistaken for a decision.
HOST = 0xA5
STANDALONE = 0x5A

_MAGIC = 0x7E                            # says byte 1 was written on purpose


def decode(nvm):
    """Read the recorded mode. Anything unrecognised means HOST."""
    if nvm is None or len(nvm) < 2:
        return HOST
    if nvm[0] != _MAGIC:
        return HOST
    return nvm[1] if nvm[1] in (HOST, STANDALONE) else HOST


def encode(mode):
    """The two bytes to store for *mode*."""
    if mode not in (HOST, STANDALONE):
        raise ValueError("unknown boot mode %r" % (mode,))
    return bytearray((_MAGIC, mode))


def owns_filesystem(mode):
    """True when the OVEN should have write access."""
    return mode == STANDALONE


def name(mode):
    return "standalone" if mode == STANDALONE else "host"
