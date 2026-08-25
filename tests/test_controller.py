"""Controller behaviour across the plausible plant family.

No step test has been run on this oven, so its gain, time constant and
transport lag are unknown. These tests therefore assert what must hold for
*every* plant in the family rather than performance figures for one — and
performance figures are deliberately absent, because there is nothing yet to
tune against. What is checked here is that the structure is sound and that
the failure modes go the safe way.
"""

import os

import pytest

from oven.controller import (PID, FeedForward, TimeProportional, Controller,
                             predict_peak, clamp)
from oven.profile import Profile
from oven.safety import Supervisor, Limits as SafetyLimits

from sim.runner import simulate
from sim.thermal import Oven, family, describe

PROFILES = os.path.join(os.path.dirname(__file__), "..", "firmware", "profiles")
AS_RUN = Profile.load(os.path.join(PROFILES, "4900p-as-run.json"))


# -- pieces -----------------------------------------------------------------

def test_time_proportional_holds_on_rather_than_chattering():
    """High duty must latch the relay through the window. This is what keeps
    a mechanical relay to tens of actuations per run instead of hundreds."""
    tpo = TimeProportional(window_s=2.0, min_on_s=0.4, min_off_s=0.4)
    tpo.reset(0.0)
    t = 0.0
    for _ in range(400):                 # 100 s at full demand
        tpo.update(t, 0.95)
        t += 0.25
    assert tpo.actuations <= 2


def test_time_proportional_ignores_a_sliver_of_demand():
    tpo = TimeProportional(window_s=2.0, min_on_s=0.4)
    tpo.reset(0.0)
    states = [tpo.update(t * 0.25, 0.05) for t in range(40)]
    assert not any(states)


def test_time_proportional_actually_modulates_in_between():
    tpo = TimeProportional(window_s=2.0)
    tpo.reset(0.0)
    on = sum(1 for i in range(400) if tpo.update(i * 0.25, 0.5))
    assert 0.4 < on / 400 < 0.6


def test_pid_derivative_does_not_kick_on_a_setpoint_step():
    pid = PID()
    pid.update(0.0, 100.0, 100.0)
    calm = pid.update(0.25, 100.0, 100.0)
    pid2 = PID()
    pid2.update(0.0, 100.0, 100.0)
    stepped = pid2.update(0.25, 200.0, 100.0)   # setpoint jumps 100 C
    # proportional responds; derivative must not add a spike on top
    assert stepped > calm
    assert stepped <= pid2.out_max


def test_pid_integral_does_not_wind_up_while_saturated():
    pid = PID()
    t = 0.0
    for _ in range(4000):                 # 1000 s of unreachable setpoint
        pid.update(t, 500.0, 25.0)
        t += 0.25
    assert pid._i <= pid.i_max
    # and it must come back promptly once the error reverses
    for _ in range(80):
        out = pid.update(t, 25.0, 30.0)
        t += 0.25
    assert out < 0.2


def test_feed_forward_uses_a_measured_table_when_there_is_one():
    ff = FeedForward(table=[(100, 0.25), (200, 0.55)])
    assert ff.duty_for(100) == pytest.approx(0.25)
    assert ff.duty_for(150) == pytest.approx(0.40)
    assert ff.duty_for(300) == pytest.approx(0.55)   # clamped, not extrapolated


def test_predict_peak_is_the_present_temperature_when_nothing_is_moving():
    assert predict_peak(150.0, 0.0, 30.0) == 150.0
    assert predict_peak(150.0, -1.0, 30.0) == 150.0


def test_predict_peak_grows_with_both_rate_and_lag():
    assert predict_peak(150, 1.0, 30) > predict_peak(150, 1.0, 10)
    assert predict_peak(150, 2.0, 30) > predict_peak(150, 1.0, 30)


def test_controller_refuses_to_be_built_without_a_measured_coast():
    with pytest.raises(ValueError, match="must be measured"):
        Controller(AS_RUN, coast_tau_s=None)


# -- across the whole family ------------------------------------------------

@pytest.mark.parametrize("params", family(), ids=describe)
def test_supervisor_is_never_violated_on_any_plant(params):
    """Whatever the oven turns out to be, the absolute ceiling holds."""
    r = simulate(AS_RUN,
                 oven=Oven(dt=0.25, **params),
                 controller=Controller(AS_RUN,
                                       coast_tau_s=params["dead_time_s"]))
    if r.fault is not None:
        # tripping is an acceptable outcome; running past the limit is not
        assert r.metrics.peak_c < SafetyLimits().max_temp_c + 5
    assert r.metrics.peak_c < SafetyLimits().max_temp_c + 5


@pytest.mark.parametrize("params", family(), ids=describe)
def test_relay_actuation_stays_modest_on_any_plant(params):
    r = simulate(AS_RUN,
                 oven=Oven(dt=0.25, **params),
                 controller=Controller(AS_RUN,
                                       coast_tau_s=params["dead_time_s"]))
    assert r.actuations < 120, "mechanical relay would wear quickly"


@pytest.mark.parametrize("params", family(), ids=describe)
def test_heat_is_never_requested_after_a_fault(params):
    sup = Supervisor()
    r = simulate(AS_RUN,
                 oven=Oven(dt=0.25, **params),
                 controller=Controller(AS_RUN,
                                       coast_tau_s=params["dead_time_s"]),
                 supervisor=sup)
    if r.fault is None:
        return
    fault_t = r.fault.t
    after = [row for row in r.trace if row[0] >= fault_t]
    assert not any(row[4] for row in after), "relay commanded on after a fault"


# -- the coast constant is the one nobody has measured ----------------------

@pytest.mark.parametrize("assumed", [5.0, 20.0, 40.0, 60.0])
def test_a_wrong_coast_constant_errs_towards_undershoot(assumed):
    """``coast_tau_s`` will be wrong until E2 measures it. Assuming too much
    lag stops heating early and undershoots — a re-run. Assuming too little
    overshoots — cooked parts. The predictive cutoff must not turn a bad
    estimate into a runaway, so the overshoot for an under-estimate is
    bounded here even on the worst plant in the family."""
    plant = {"gain_c": 450.0, "tau_s": 150.0, "dead_time_s": 60.0}
    r = simulate(AS_RUN, oven=Oven(dt=0.25, **plant),
                 controller=Controller(AS_RUN, coast_tau_s=assumed))
    assert r.metrics.peak_c < SafetyLimits().max_temp_c


def test_the_cutoff_latches_so_heat_is_not_put_back_in_flight():
    ctl = Controller(AS_RUN, coast_tau_s=30.0)
    ctl.reset(0.0)
    ctl.duty_for(250.0, 150.0, 250.0)
    ctl.duty_for(251.0, 190.0, 251.0)          # 40 C/s: predicted way past peak
    assert ctl.coasting
    d = ctl.duty_for(252.0, 191.0, 252.0)
    assert d == 0.0
