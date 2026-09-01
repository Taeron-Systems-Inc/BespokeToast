# SPDX-License-Identifier: MIT
"""The measured rate curves, stored compactly.

The characterisation arrives as JSON lists of [temperature, rate] pairs and
was kept that way, which costs 7.2 kB of SRAM on a board with about 30 kB
free. Almost none of that is the numbers: a Python float is a heap object,
a two-element list is another, and sixty of those come to roughly a hundred
bytes apiece before any of them holds a value.

Two array('f') hold the same curve in 4 bytes per number, contiguous, with
no per-element object at all. The interpolation is unchanged; only the
storage is.

Kept separate from the controller so it can be tested against the lists it
replaces, value for value, rather than trusted.
"""

from array import array


class RateTable(object):
    """Temperature -> rate, linearly interpolated, clamped at both ends."""

    __slots__ = ("_t", "_r")

    def __init__(self, pairs):
        ordered = sorted(pairs)
        if not ordered:
            raise ValueError("a rate table needs at least one point")
        self._t = array("f", [float(p[0]) for p in ordered])
        self._r = array("f", [float(p[1]) for p in ordered])

    def __len__(self):
        return len(self._t)

    @property
    def span(self):
        return self._t[0], self._t[-1]

    def at(self, temp_c):
        t, r = self._t, self._r
        n = len(t)
        if temp_c <= t[0]:
            return r[0]
        if temp_c >= t[n - 1]:
            return r[n - 1]
        lo, hi = 0, n - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if t[mid] <= temp_c:
                lo = mid
            else:
                hi = mid
        span = t[hi] - t[lo]
        if span <= 0:
            return r[lo]
        return r[lo] + (r[hi] - r[lo]) * (temp_c - t[lo]) / span

    def pairs(self):
        """Back to plain pairs, for anything that still wants them."""
        return [(self._t[i], self._r[i]) for i in range(len(self._t))]


def as_table(value):
    """Accept a RateTable, a list of pairs, or None."""
    if value is None or isinstance(value, RateTable):
        return value
    return RateTable(value)
