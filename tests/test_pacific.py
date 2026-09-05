# SPDX-License-Identifier: MIT
"""Pacific time, which is what the oven is read in.

The rule is written out rather than looked up -- CircuitPython has no
timezone database -- so it has to be checked against one that is real.
"""

import pytest

from oven import pacific as P


def test_the_ordinary_cases():
    assert P.local("2026-01-15T12-00-00Z") == ("2026-01-15", "04:00:00", "PST")
    assert P.local("2026-07-15T12-00-00Z") == ("2026-07-15", "05:00:00", "PDT")


def test_the_offset_can_move_the_date():
    """01:19 UTC is the previous evening here. A run listed under the
    wrong day is the whole reason this module exists."""
    assert P.local("2026-09-03T01-19-09Z") == ("2026-09-02", "18:19:09", "PDT")


def test_spring_forward_skips_an_hour():
    """02:00 local never happens on that day."""
    assert P.local("2026-03-08T09-59-59Z")[1] == "01:59:59"
    assert P.local("2026-03-08T10-00-00Z")[1] == "03:00:00"


def test_fall_back_repeats_an_hour():
    assert P.local("2026-11-01T08-59-59Z") == ("2026-11-01", "01:59:59", "PDT")
    assert P.local("2026-11-01T09-00-00Z") == ("2026-11-01", "01:00:00", "PST")


def test_a_stamp_that_is_not_one_is_refused_rather_than_guessed():
    """The first run after every power cut has "monotonic+40" here,
    because the clock comes off the network and is not set yet."""
    for junk in ("monotonic+40", "", None, "2026-09-03", "banana"):
        assert P.local(junk) is None


def test_transition_dates_are_the_us_rule():
    """Second Sunday in March, first Sunday in November."""
    assert P._nth_sunday(2026, 3, 2) == 8
    assert P._nth_sunday(2026, 11, 1) == 1
    assert P._nth_sunday(2027, 3, 2) == 14
    assert P._nth_sunday(2027, 11, 1) == 7


def test_it_agrees_with_a_real_timezone_database():
    """Written-out rules drift from reality. This is the check that the
    arithmetic is not merely self-consistent."""
    zoneinfo = pytest.importorskip("zoneinfo")
    from datetime import datetime, timezone
    import random
    try:
        LA = zoneinfo.ZoneInfo("America/Los_Angeles")
    except Exception:
        pytest.skip("no tzdata on this host")
    random.seed(7)
    for _ in range(2000):
        ts = random.randint(1546300800, 2019686400)     # 2019..2034
        dt = datetime.fromtimestamp(ts, timezone.utc)
        truth = dt.astimezone(LA)
        assert P.local(dt.strftime("%Y-%m-%dT%H-%M-%SZ")) == (
            truth.strftime("%Y-%m-%d"), truth.strftime("%H:%M:%S"),
            truth.tzname())
