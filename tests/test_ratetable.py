# SPDX-License-Identifier: MIT
"""The packed rate curves must agree with the lists they replace.

This exists to save memory, and a memory saving that changes the numbers is
not a saving, it is a different oven model. So the test is agreement, value
for value, against the measured data actually shipped.
"""

import json
import os

import pytest

from oven.ratetable import RateTable, as_table

DATA = os.path.join(os.path.dirname(__file__), "..", "data",
                    "oven-characterisation.json")


def reference(pairs, x):
    """The interpolation this replaces, written out plainly."""
    ordered = sorted(pairs)
    if x <= ordered[0][0]:
        return ordered[0][1]
    if x >= ordered[-1][0]:
        return ordered[-1][1]
    for i in range(1, len(ordered)):
        if ordered[i][0] >= x:
            (a, ya), (b, yb) = ordered[i - 1], ordered[i]
            return ya + (yb - ya) * (x - a) / (b - a)
    return ordered[-1][1]


@pytest.fixture(scope="module")
def measured():
    with open(DATA) as f:
        return json.load(f)


@pytest.mark.parametrize("key", ["heating_rate_c_per_s", "cooling_rate_c_per_s"])
def test_it_agrees_with_the_plain_interpolation_everywhere(measured, key):
    pairs = measured[key]
    table = RateTable(pairs)
    lo = min(p[0] for p in pairs) - 30
    hi = max(p[0] for p in pairs) + 30
    x = lo
    while x <= hi:
        assert table.at(x) == pytest.approx(reference(pairs, x), abs=1e-3), \
            "disagreed at %.1f C" % x
        x += 0.5


def test_it_clamps_outside_the_measured_span(measured):
    pairs = measured["heating_rate_c_per_s"]
    table = RateTable(pairs)
    first, last = sorted(pairs)[0], sorted(pairs)[-1]
    assert table.at(-100.0) == pytest.approx(first[1], abs=1e-3)
    assert table.at(9999.0) == pytest.approx(last[1], abs=1e-3)


def test_the_endpoints_are_exact(measured):
    for key in ("heating_rate_c_per_s", "cooling_rate_c_per_s"):
        pairs = sorted(measured[key])
        table = RateTable(pairs)
        for temp, rate in pairs:
            assert table.at(temp) == pytest.approx(rate, abs=1e-3)


def test_unsorted_input_is_ordered_not_trusted():
    table = RateTable([(200, 0.8), (25, 2.0), (100, 1.5)])
    assert table.span == (pytest.approx(25.0), pytest.approx(200.0))
    assert table.at(25.0) == pytest.approx(2.0, abs=1e-3)


def test_a_single_point_table_is_flat():
    table = RateTable([(100, 1.25)])
    for x in (-5.0, 100.0, 500.0):
        assert table.at(x) == pytest.approx(1.25, abs=1e-3)


def test_an_empty_table_is_refused():
    with pytest.raises(ValueError):
        RateTable([])


def test_as_table_accepts_what_the_firmware_will_hand_it(measured):
    pairs = measured["heating_rate_c_per_s"]
    assert as_table(None) is None
    packed = as_table(pairs)
    assert isinstance(packed, RateTable)
    assert as_table(packed) is packed


def test_repeated_temperatures_do_not_divide_by_zero():
    table = RateTable([(100, 1.0), (100, 2.0), (200, 0.5)])
    assert table.at(100.0) in (pytest.approx(1.0), pytest.approx(2.0))
