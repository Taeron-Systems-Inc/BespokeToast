# SPDX-License-Identifier: MIT
"""Rendered width of the big readout, measured from the shipped font file.

A run died at 100 C because the readout grew by a digit and the 48 px label
could not reallocate its bitmap on a fragmented heap. Asserting string length
would not have caught the general case -- what matters is the pixel width, so
this reads the advances out of the PCF itself.
"""

import os
import struct

import pytest

from oven.ui import layout as L

FONTS = os.path.join(os.path.dirname(__file__), "..", "firmware",
                     "assets", "fonts")
READOUT = os.path.join(FONTS, "B612-Bold-48.pcf")

PCF_METRICS = 1 << 2
PCF_BDF_ENCODINGS = 1 << 5


def _tables(path):
    with open(path, "rb") as fh:
        data = fh.read()
    count = struct.unpack("<i", data[4:8])[0]
    toc = {}
    for i in range(count):
        kind, _fmt, _size, off = struct.unpack("<iiii", data[8 + 16 * i:
                                                             24 + 16 * i])
        toc[kind] = off
    return data, toc


def _metrics(data, off):
    fmt = struct.unpack("<i", data[off:off + 4])[0]
    big = ">" if fmt & 4 else "<"
    p = off + 4
    if fmt & 0x100:                      # compressed: bytes biased by 0x80
        n = struct.unpack(big + "h", data[p:p + 2])[0]
        p += 2
        return [tuple(b - 0x80 for b in data[p + 5 * i:p + 5 * i + 5])
                for i in range(n)]
    n = struct.unpack(big + "i", data[p:p + 4])[0]
    p += 4
    return [struct.unpack(big + "5hH", data[p + 12 * i:p + 12 * i + 12])[:5]
            for i in range(n)]


def _encodings(data, off):
    fmt = struct.unpack("<i", data[off:off + 4])[0]
    big = ">" if fmt & 4 else "<"
    lo0, lo1, hi0, hi1, _default = struct.unpack(big + "5h",
                                                 data[off + 4:off + 14])
    p = off + 14
    out = {}
    for hi in range(hi0, hi1 + 1):
        for lo in range(lo0, lo1 + 1):
            g = struct.unpack(big + "H", data[p:p + 2])[0]
            p += 2
            if g != 0xFFFF:
                out[(hi << 8) | lo] = g
    return out


@pytest.fixture(scope="module")
def advance():
    data, toc = _tables(READOUT)
    metrics = _metrics(data, toc[PCF_METRICS])
    enc = _encodings(data, toc[PCF_BDF_ENCODINGS])

    def width(text):
        total = 0
        for ch in text:
            g = enc.get(ord(ch))
            assert g is not None, "%r is not in %s" % (ch, READOUT)
            total += metrics[g][2]
        return total
    return width


def test_readout_width_is_bounded(advance):
    """The readout must fit its 314 px column at every temperature.

    This used to assert a *constant* width, because bitmap_label sized one
    bitmap to the whole string and growing it mid-run failed on a fragmented
    heap. Text is drawn per-glyph now, so width may vary -- it just has to
    fit.
    """
    for value in list(range(-20, 301)) + [None]:
        assert advance(L._t(value)) <= 314, (
            "%r is too wide for the readout column" % L._t(value))


def test_the_font_has_tabular_digits(advance):
    """The padding above only works because every digit is the same width."""
    assert len({advance(d) for d in "0123456789"}) == 1


def test_readout_covers_every_character_it_can_emit(advance):
    for value in (-5, 0, 7, 99, 100, 260, None):
        advance(L._t(value))             # asserts coverage internally
