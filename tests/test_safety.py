"""The supervisor is the only thing that may permit heat, so these are the
tests that matter most. Every fault is injected the way the hardware would
actually produce it, and each one must both deny heat and stay denied."""

import pytest

from oven import hal
from oven.hal import Reading
from oven.safety import (Supervisor, Limits, FAULT_OVER_TEMP, FAULT_RATE,
                         FAULT_SENSOR, FAULT_SENSOR_STALE,
                         FAULT_SENSOR_FROZEN, FAULT_STALL, FAULT_ENCLOSURE,
                         FAULT_RUN_TIMEOUT, FAULT_IMPLAUSIBLE_START)


@pytest.fixture
def sup():
    s = Supervisor(Limits())
    s.begin_run(0.0)
    return s


def run(sup, temps, relay_on=True, step=0.25, start=0.0, cold=25.0):
    """Feed a series of temperatures at a fixed cadence."""
    t = start
    last = None
    for temp in temps:
        t += step
        last = sup.update(t, Reading(temp, cold=cold), relay_on)
    return last


# -- the baseline: a healthy run is not interfered with ---------------------

def test_a_normal_heating_run_never_trips(sup):
    temps = [25 + i * 0.2 for i in range(400)]     # 0.8 C/s, unremarkable
    assert run(sup, temps) is None
    assert sup.allow_heat()


def test_heat_is_permitted_before_anything_happens():
    assert Supervisor().allow_heat()


# -- over temperature -------------------------------------------------------

def test_absolute_ceiling_trips(sup):
    # climb at a rate the oven could actually produce, straight through it
    f = run(sup, [240 + i * 1.0 for i in range(25)], step=1.0)
    assert f.code == FAULT_OVER_TEMP
    assert not sup.allow_heat()


def test_ceiling_is_inclusive(sup):
    assert run(sup, [255.0, 257.0, 259.9], step=1.0) is None
    assert run(sup, [260.0], step=1.0, start=3.0).code == FAULT_OVER_TEMP


# -- the failure direction that actually hurts ------------------------------

def test_thermocouple_open_circuit_denies_heat(sup):
    f = sup.update(1.0, Reading(25.0, faults=hal.FAULT_OPEN_CIRCUIT), True)
    assert f.code == FAULT_SENSOR
    assert not sup.allow_heat()
    assert "open circuit" in f.message


def test_bus_failure_denies_heat(sup):
    f = sup.update(1.0, Reading(None, faults=hal.FAULT_BUS), True)
    assert not sup.allow_heat()


def test_a_reading_of_none_denies_heat(sup):
    f = sup.update(1.0, None, True)
    assert f.code == FAULT_SENSOR_STALE
    assert not sup.allow_heat()


def test_a_sensor_reading_low_is_caught_by_the_stall_guard(sup):
    """The dangerous case: a probe that reads cold makes the controller ask
    for more heat. Nothing about the number itself looks wrong, so the guard
    that has to catch it is 'heat in, nothing out'."""
    f = run(sup, [30.0] * 500, relay_on=True)
    assert f is not None
    assert f.code in (FAULT_STALL, FAULT_SENSOR_FROZEN)
    assert not sup.allow_heat()


def test_frozen_reading_while_heating_trips(sup):
    f = run(sup, [42.0] * 200, relay_on=True)
    assert f.code in (FAULT_SENSOR_FROZEN, FAULT_STALL)


def test_a_steady_reading_with_the_relay_off_is_fine(sup):
    assert run(sup, [42.0] * 500, relay_on=False) is None
    assert sup.allow_heat()


# -- rate of rise -----------------------------------------------------------

def test_implausible_rate_trips(sup):
    f = run(sup, [25, 30, 90], step=1.0)          # 60 C in one second
    assert f.code == FAULT_RATE


def test_a_brisk_but_real_ramp_does_not_trip(sup):
    f = run(sup, [25 + i * 2.0 for i in range(50)], step=1.0)   # 2 C/s
    assert f is None


# -- stall ------------------------------------------------------------------

def test_heating_with_no_rise_trips(sup):
    f = run(sup, [50.0 + i * 0.001 for i in range(600)], relay_on=True)
    assert f.code in (FAULT_STALL, FAULT_SENSOR_FROZEN)


def test_stall_window_resets_when_the_oven_does_rise(sup):
    # rises 3 C every stall window: never a stall
    temps = []
    for block in range(6):
        temps += [50.0 + block * 3.0 + i * 0.01 for i in range(360)]
    assert run(sup, temps, relay_on=True) is None


# -- enclosure --------------------------------------------------------------

def test_hot_enclosure_trips(sup):
    f = sup.update(1.0, Reading(120.0, cold=61.0), True)
    assert f.code == FAULT_ENCLOSURE
    assert "enclosure" in f.message


def test_warm_enclosure_is_tolerated(sup):
    assert sup.update(1.0, Reading(120.0, cold=45.0), True) is None


def test_absent_enclosure_reading_does_not_trip(sup):
    assert sup.update(1.0, Reading(120.0, cold=None), True) is None


# -- watchdog-ish: gaps in supervision --------------------------------------

def test_a_long_gap_while_heating_trips(sup):
    sup.update(1.0, Reading(100.0), True)
    f = sup.update(20.0, Reading(105.0), True)     # 19 s unwatched, relay on
    assert f.code == FAULT_SENSOR_STALE


def test_a_long_gap_with_the_relay_off_is_not_a_fault(sup):
    sup.update(1.0, Reading(100.0), False)
    assert sup.update(20.0, Reading(99.0), False) is None


# -- run duration -----------------------------------------------------------

def test_run_timeout_trips(sup):
    f = sup.update(3601.0, Reading(100.0), True)
    assert f.code == FAULT_RUN_TIMEOUT


# -- latching ---------------------------------------------------------------

def test_a_fault_latches_even_once_conditions_are_good_again(sup):
    run(sup, [240 + i * 1.0 for i in range(25)], step=1.0)
    assert not sup.allow_heat()
    for _ in range(100):
        sup.update(999.0, Reading(25.0), False)    # perfectly healthy now
    assert not sup.allow_heat(), "fault cleared itself"


def test_the_first_cause_is_kept_not_the_last(sup):
    run(sup, [240 + i * 1.0 for i in range(25)], step=1.0)   # over temp
    first = sup.fault
    sup.update(500.0, Reading(None), True)         # then a sensor failure
    assert sup.fault is first
    assert sup.fault.code == FAULT_OVER_TEMP


def test_acknowledgement_clears_it(sup):
    run(sup, [240 + i * 1.0 for i in range(25)], step=1.0)
    sup.acknowledge()
    assert sup.allow_heat()


def test_acknowledgement_does_not_resurrect_stale_history(sup):
    run(sup, [25 + i for i in range(50)], step=1.0)
    sup.acknowledge()
    # a big jump straight after ack must not be read as a huge rate
    assert sup.update(1000.0, Reading(200.0), True) is None


# -- pre-flight -------------------------------------------------------------

def test_start_refused_when_the_oven_is_still_hot():
    s = Supervisor()
    f = s.check_start(Reading(84.0))
    assert f.code == FAULT_IMPLAUSIBLE_START
    assert "84.0" in f.message


def test_start_refused_with_a_faulty_probe():
    s = Supervisor()
    assert s.check_start(
        Reading(25.0, faults=hal.FAULT_OPEN_CIRCUIT)).code == FAULT_SENSOR


def test_start_refused_with_no_reading():
    assert Supervisor().check_start(None).code == FAULT_SENSOR_STALE


def test_start_allowed_from_ambient():
    assert Supervisor().check_start(Reading(22.0)) is None


def test_refusing_to_start_does_not_latch():
    s = Supervisor()
    s.check_start(Reading(84.0))
    assert s.allow_heat(), "a refused start should not need acknowledgement"


def test_a_step_change_too_large_to_be_real_trips_the_rate_guard(sup):
    """Writing the ceiling test naively surfaced this: a jump of 100 C
    between samples is not an over-temperature event, it is a broken
    measurement, and the rate guard is the one that should say so."""
    f = run(sup, [100.0, 200.0], step=0.25)
    assert f.code == FAULT_RATE
    assert not sup.allow_heat()
