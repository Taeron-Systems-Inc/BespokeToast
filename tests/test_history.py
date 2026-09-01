# SPDX-License-Identifier: MIT
"""The chart trace must never grow without bound.

A run died mid-profile because this was a plain list that was appended to for
the length of the run. The oven was at 90 C with the relay at full duty.
"""

import pytest

from oven.history import History


def test_it_never_exceeds_its_bound_however_long_the_run():
    """An MSL bake runs for hours at one sample every two seconds."""
    h = History(max_points=150, interval_s=2.0)
    t = 0.0
    for _ in range(20000):               # ~11 hours of a two-second cadence
        h.add(t, 25.0 + (t % 200))
        t += 2.0
    assert len(h) <= 150


def test_samples_are_rate_limited_to_the_interval():
    h = History(max_points=150, interval_s=2.0)
    assert h.add(0.0, 25.0) is True
    assert h.add(0.5, 25.1) is False, "faster than the interval"
    assert h.add(1.9, 25.2) is False
    assert h.add(2.0, 25.3) is True
    assert len(h) == 2


def test_decimation_keeps_the_whole_run_not_just_one_end():
    """Dropping the oldest would lose the ramp; dropping the newest would
    lose what is happening now. Halving the resolution keeps both."""
    h = History(max_points=10, interval_s=1.0)
    for i in range(11):
        h.add(float(i), float(i))
    pts = h.points
    assert pts[0][0] == 0.0, "the start of the run is still there"
    assert pts[-1][0] == 10.0, "so is the most recent sample"
    assert len(pts) <= 10
    assert h.interval_s == 2.0, "the effective interval doubled"


def test_decimation_never_drops_the_newest_stored_sample():
    """Whatever was just recorded must still be there afterwards.

    Only samples that were actually stored count: once the interval has
    doubled, a sample offered at the old cadence is not due yet, and
    declining it is the point of the rate limit.
    """
    h = History(max_points=6, interval_s=1.0)
    for i in range(40):
        if h.add(float(i), float(i)):
            assert h.points[-1] == (float(i), float(i))


def test_decimation_is_repeatable_and_the_interval_keeps_doubling():
    h = History(max_points=8, interval_s=1.0)
    for i in range(200):
        h.add(float(i), float(i))
    assert h.decimations >= 4
    assert h.interval_s == 1.0 * (2 ** h.decimations)
    assert len(h) <= 8


def test_clear_resets_the_interval_so_the_next_run_is_full_resolution():
    h = History(max_points=8, interval_s=2.0)
    for i in range(100):
        h.add(float(i) * 2, float(i))
    assert h.interval_s > 2.0
    h.clear()
    assert len(h) == 0
    assert h.interval_s == 2.0
    assert h.add(0.0, 25.0) is True


def test_a_missing_reading_is_not_recorded():
    h = History()
    assert h.add(0.0, None) is False
    assert len(h) == 0


def test_points_are_in_order():
    h = History(max_points=12, interval_s=1.0)
    for i in range(60):
        h.add(float(i), float(i))
    ts = [t for t, _ in h.points]
    assert ts == sorted(ts)


def test_it_refuses_a_bound_too_small_to_decimate():
    with pytest.raises(ValueError):
        History(max_points=2)
