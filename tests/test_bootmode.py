# SPDX-License-Identifier: MIT
"""Which way the filesystem ownership fails when it is unsure.

Getting this wrong in one direction costs an unrecorded run. Getting it
wrong in the other locks the host out of the volume, which happened twice
while working this out and both times needed rescuing over the serial REPL.
"""

import pytest

from oven.bootmode import (HOST, STANDALONE, decode, encode, name,
                           owns_filesystem)


def test_a_recorded_mode_round_trips():
    for mode in (HOST, STANDALONE):
        assert decode(encode(mode)) == mode


def test_the_oven_only_owns_the_filesystem_when_standalone():
    assert owns_filesystem(STANDALONE) is True
    assert owns_filesystem(HOST) is False


@pytest.mark.parametrize("nvm", [
    None,
    bytearray(),
    bytearray((0x00,)),
    bytearray((0x00, 0x00)),
    bytearray((0xFF, 0xFF)),
    bytearray((0x7E, 0x00)),
    bytearray((0x7E, 0xFF)),
    bytearray((0x00, 0x5A)),
    bytearray((0x12, 0x34)),
])
def test_anything_unrecognised_leaves_the_volume_with_the_host(nvm):
    """Erased flash, zeroed flash, a short buffer, a plausible-looking
    value without the magic -- none of them may be read as standalone."""
    assert decode(nvm) == HOST


def test_the_markers_are_not_values_erased_flash_produces():
    """0x00 and 0xFF are what uninitialised memory reads as."""
    for value in (HOST, STANDALONE):
        assert value not in (0x00, 0xFF)


def test_an_unknown_mode_cannot_be_encoded():
    with pytest.raises(ValueError):
        encode(0x01)


def test_modes_have_readable_names():
    assert name(STANDALONE) == "standalone"
    assert name(HOST) == "host"
