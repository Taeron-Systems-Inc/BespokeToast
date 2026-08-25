"""Tests against the oven's own measured behaviour.

These are regression tests on real data: if a change to the controller or the
feed-forward stops reproducing what the hardware did on 2026-08-25, that is a
bug in the model, not a new result.
"""

import json
import os

import pytest

from oven.controller import FeedForward, predict_peak
from oven.profile import Profile

from sim.measured import MeasuredOven, capability, hold_duty_table

HERE = os.path.dirname(__file__)
DATA = json.load(open(os.path.join(HERE, "..", "data",
                                   "oven-characterisation.json")))
PROFILES = os.path.join(HERE, "..", "firmware", "profiles")


def ff():
    return FeedForward(heating_rates=DATA["heating_rate_c_per_s"],
                       cooling_rates=DATA["cooling_rate_c_per_s"])


# -- the simulator must reproduce the step test it was built from -----------

def test_simulator_reaches_200c_in_about_the_measured_time():
    o = MeasuredOven(dt=0.25)
    t = 0.0
    while o.temp_c < 200.0 and t < 600:
        o.step(True); t += 0.25
    assert 130 < t < 160, "real oven took 143 s"


def test_simulator_reproduces_the_small_measured_coast():
    o = MeasuredOven(dt=0.25)
    while o.temp_c < 200.0:
        o.step(True)
    cut = o.temp_c
    peak = cut
    for _ in range(200):
        o.step(False)
        peak = max(peak, o.temp_c)
    overshoot = peak - cut
    assert overshoot < 5.0, "measured coast was 1.06 C, not the 29.6 C on file"


def test_coast_constant_is_the_measured_one_not_the_legacy_one():
    assert capability()["coast_tau_s"] < 5.0
    # the 2023 value would have implied something like this, 28x larger
    assert predict_peak(200.0, 0.9, 37.0) - 200.0 > 30


# -- capability, which is what makes profiles fail --------------------------

def test_the_oven_is_weakest_exactly_where_reflow_needs_it_strongest():
    f = ff()
    assert f.achievable_rate(80.0) > f.achievable_rate(200.0)
    assert f.achievable_rate(200.0) < 1.0


def test_door_shut_cooling_cannot_follow_any_reflow_profile():
    down = capability()["max_ramp_down"]
    assert down < 1.0
    for name in ("4900p-as-run", "4900p-datasheet"):
        p = Profile.load(os.path.join(PROFILES, name + ".json"))
        assert -p.max_ramp_down > down, "profile %s would be achievable" % name


@pytest.mark.parametrize("name", ["4900p-as-run", "4900p-datasheet"])
def test_shipped_reflow_profiles_are_flagged_as_beyond_this_oven(name):
    p = Profile.load(os.path.join(PROFILES, name + ".json"))
    cap = capability()
    w = " ".join(p.warnings(max_ramp_up=cap["max_ramp_up"],
                            max_ramp_down=cap["max_ramp_down"]))
    assert "this oven has managed" in w


# -- feed-forward inverts the plant ----------------------------------------

def test_feed_forward_asks_for_zero_duty_when_told_to_cool():
    assert ff().duty_for(180.0, -1.0) == 0.0


def test_feed_forward_asks_for_full_duty_beyond_capability():
    assert ff().duty_for(200.0, 5.0) == 1.0


def test_hold_duty_rises_with_temperature():
    tbl = hold_duty_table()
    assert tbl[0][1] < tbl[-1][1]
    for a, b in zip(tbl, tbl[1:]):
        assert b[0] > a[0]


def test_feed_forward_hold_duty_reproduces_a_standstill():
    """Commanding rate 0 should hold: apply that duty and the temperature
    should barely move."""
    f = ff()
    o = MeasuredOven(dt=0.25, start_c=150.0)
    duty = f.duty_for(150.0, 0.0)
    on_for = 0.0
    for i in range(1200):                      # 300 s
        on_for += duty
        on = on_for >= 1.0
        if on: on_for -= 1.0
        o.step(on)
    assert abs(o.temp_c - 150.0) < 12.0


def test_hold_duty_table_is_not_extrapolated_past_its_evidence():
    """The table must stay inside its declared range, and that range must be
    honest about what was measured.

    This originally asserted the range stopped BELOW the liquidus, because the
    first step test halted at 200 C and everything reflow needs was
    extrapolation. The second step test to 240 C closed that gap, so the
    assertion is inverted: the table must now cover the reflow region, and
    must not have grown beyond the data again.
    """
    lo, hi = DATA["hold_duty_valid_range_c"]
    assert all(lo <= T <= hi for T, _ in DATA["hold_duty"])
    assert hi >= 235, "the reflow peak must be inside the measured range"
    hottest = max(T for T, _ in DATA["heating_rate_c_per_s"])
    assert hi <= hottest + 5, "table extends past the step test that fed it"


# -- regressions ------------------------------------------------------------

def test_predictive_cutoff_releases_during_a_hold_at_peak():
    """The cutoff latched on reaching the peak and only released once the
    target had dropped well below it. A profile that HOLDS at peak to earn
    time above liquidus therefore coasted down through its entire dwell, and
    time above liquidus came out ~40% short. Release is now simply 'the oven
    has fallen below what is being asked for'."""
    from oven.controller import Controller, PID
    p = Profile.load(os.path.join(PROFILES, "sac305-this-oven.json"))
    ctl = Controller(p, coast_tau_s=DATA["coast_tau_s"], feed_forward=ff(),
                     pid=PID(kp=0.03, ki=0.0015, kd=0.5))
    ctl.reset(0.0)
    o = MeasuredOven(dt=0.25)
    from oven.metrics import RunMetrics
    m = RunMetrics(p.liquidus_c)
    t = 0.0
    while t <= p.duration:
        temp = o.read()
        relay = ctl.relay_state(t, ctl.duty_for(t, temp, t))
        m.add(t, temp)
        o.step(relay)
        t += 0.25
    assert m.time_above_liquidus >= 60.0


def test_the_derived_profile_passes_every_check_on_this_oven():
    from oven.controller import Controller, PID
    from oven.metrics import RunMetrics, Limits
    p = Profile.load(os.path.join(PROFILES, "sac305-this-oven.json"))
    ctl = Controller(p, coast_tau_s=DATA["coast_tau_s"], feed_forward=ff(),
                     pid=PID(kp=0.03, ki=0.0015, kd=0.5))
    ctl.reset(0.0)
    o = MeasuredOven(dt=0.25)
    m = RunMetrics(p.liquidus_c)
    t = 0.0
    while t <= p.duration:
        temp = o.read()
        relay = ctl.relay_state(t, ctl.duty_for(t, temp, t))
        m.add(t, temp)
        o.step(relay)
        t += 0.25
    failures = [n for n, _, ok, _ in m.check(Limits.for_profile(p)) if not ok]
    assert not failures, "failed: %s" % failures
    assert ctl.tpo.actuations < 120
