# SPDX-License-Identifier: MIT
"""The chart's trace, bounded.

This existed as a bare list in code.py that was appended to every two seconds
and never trimmed. A run died at 90 C, mid-profile with the relay at full
duty, because growing that list wanted 256 contiguous bytes and the heap --
~22 kB free, no hole above ~900 bytes -- could not provide them. The relay
was driven low by the exit handler, so the failure was safe, but the run was
lost and the oven stopped responding to the console.

An unbounded buffer was also wrong on its own terms: the longest shipped
profile is an MSL bake measured in hours, and the chart is 308 pixels wide.
There was never any point holding more points than the chart can draw.

When the buffer fills, every second point is dropped and the sampling
interval doubles. The trace keeps the shape of the whole run at half the
resolution rather than losing either its beginning or its end, and the
allocation ceiling is fixed from then on.
"""


class History(object):
    def __init__(self, max_points=150, interval_s=2.0):
        if max_points < 4:
            raise ValueError("max_points must leave room to decimate")
        self.max_points = max_points
        self.base_interval_s = interval_s
        self.interval_s = interval_s
        # One list of (t, value) tuples, kept live. Rebuilding this per frame
        # to hand to the chart would allocate 150 tuples and a list at 2 Hz,
        # which is the same churn that killed a run.
        self._points = []
        self._last_t = None
        self.decimations = 0

    def __len__(self):
        return len(self._points)

    @property
    def points(self):
        """(t, value) pairs, oldest first.

        The live list, not a copy: the caller reads it and must not hold on
        to it across a clear().
        """
        return self._points

    def add(self, t, value):
        """Record a sample if one is due. Returns True if it was stored."""
        if value is None:
            return False
        if self._last_t is not None and t - self._last_t < self.interval_s:
            return False
        self._last_t = t
        self._points.append((t, value))
        if len(self._points) > self.max_points:
            self._decimate()
        return True

    def clear(self):
        # del l[:] rather than rebinding: the list object is reused, so a
        # cleared history costs no allocation at all.
        del self._points[:]
        self._last_t = None
        self.interval_s = self.base_interval_s
        self.decimations = 0

    def _decimate(self):
        """Halve the resolution, in place, keeping the first and last points.

        Slice deletion (del l[::2]) raises NotImplementedError on this
        firmware, so the copy is explicit.
        """
        n = len(self._points)
        keep = []
        for i in range(0, n, 2):
            keep.append(self._points[i])
        # The most recent sample is the one being watched; never drop it.
        if keep[-1] is not self._points[n - 1]:
            keep.append(self._points[n - 1])
        del self._points[:]
        for p in keep:
            self._points.append(p)
        self.interval_s *= 2.0
        self.decimations += 1
