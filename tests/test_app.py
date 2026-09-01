"""The run state machine, driven against fakes.

The point of the HAL split is that this whole file runs without a board.
Every fake here is deliberately dumb: the interesting behaviour belongs to
the code under test, not the scaffolding.
"""

import os

import pytest

from oven import hal
from oven.app import (App, Event, STATE_IDLE, STATE_PREHEAT, STATE_RUNNING,
                      STATE_COOLDOWN, STATE_REPORT, STATE_FAULT,
                      CONTROL_INTERVAL_S)
from oven.controller import Controller, FeedForward, PID
from oven.profile import Profile
from oven.safety import Supervisor, Limits

PROFILES = os.path.join(os.path.dirname(__file__), "..", "firmware", "profiles")


class FakeClock(object):
    def __init__(self, t=0.0):
        self.t = t

    def monotonic(self):
        return self.t

    def advance(self, dt):
        self.t += dt


class FakeRelay(object):
    def __init__(self):
        self._on = False
        self.history = []

    def set(self, on):
        self._on = bool(on)
        self.history.append(bool(on))

    def is_on(self):
        return self._on


class FakeSensor(object):
    def __init__(self, temp=25.0):
        self.temp = temp
        self.faults = hal.FAULT_NONE
        self.raise_on_read = False

    def read(self):
        if self.raise_on_read:
            raise RuntimeError("bus exploded")
        return hal.Reading(self.temp, cold=30.0, faults=self.faults)


@pytest.fixture
def rig():
    """State-machine rig.

    The supervisor here is given a permissive rate limit on purpose. These
    tests move the fake thermocouple in instant steps to reach an interesting
    state quickly, which a real oven cannot do and the real guard correctly
    rejects. Rate limiting has its own tests in test_safety.py; mixing the two
    concerns just means every state test has to simulate a plausible ramp.
    """
    profile = Profile.load(os.path.join(PROFILES, "sac305-this-oven.json"))
    clock, relay, sensor = FakeClock(), FakeRelay(), FakeSensor()
    events = []
    app = App(relay, sensor, clock,
              lambda p: Controller(p, coast_tau_s=1.2,
                                   feed_forward=FeedForward(),
                                   pid=PID()),
              supervisor=Supervisor(Limits(max_rate_c_per_s=1e6)),
              on_event=lambda n, p: events.append((n, p)))
    return app, clock, relay, sensor, profile, events


def warm_start_profile():
    """A profile that begins well above ambient, so preheat has work to do.

    The shipped profiles start at room temperature, where preheat is correctly
    a no-op -- which makes them useless for testing it.
    """
    return Profile.from_dict({
        "name": "warm start", "category": "reflow", "liquidus_c": 217,
        "points": [[0, 100], [60, 150], [120, 220], [180, 150]]})


def run_for(app, clock, seconds, dt=CONTROL_INTERVAL_S):
    steps = int(seconds / dt)
    for _ in range(steps):
        clock.advance(dt)
        app.tick()


# -- cadence ---------------------------------------------------------------

def test_control_step_fires_on_schedule_not_on_every_call(rig):
    app, clock, _, _, _, _ = rig
    assert app.tick() is True                  # first call establishes it
    assert app.tick() is False                 # no time has passed
    clock.advance(CONTROL_INTERVAL_S)
    assert app.tick() is True


def test_cadence_does_not_drift_permanently_late_after_one_slow_render(rig):
    app, clock, _, _, _, _ = rig
    app.tick()
    clock.advance(CONTROL_INTERVAL_S * 0.9)    # a render overran a little
    app.tick()
    clock.advance(CONTROL_INTERVAL_S * 0.1)
    assert app.tick() is True, "next step should still land on the original grid"


def test_a_very_long_stall_resets_the_schedule_rather_than_catching_up(rig):
    app, clock, _, _, _, _ = rig
    app.tick()
    clock.advance(60.0)
    app.tick()
    clock.advance(CONTROL_INTERVAL_S * 0.5)
    assert app.tick() is False, "must not fire a burst of catch-up steps"


# -- starting ---------------------------------------------------------------

def test_start_is_refused_when_the_oven_is_too_hot(rig):
    app, _, _, sensor, profile, _ = rig
    sensor.temp = 95.0
    problem = app.request_start(profile)
    assert problem is not None
    assert app.state == STATE_IDLE


def test_start_goes_to_preheat_not_straight_to_running(rig):
    app, _, _, _, profile, _ = rig
    assert app.request_start(profile) is None
    assert app.state == STATE_PREHEAT


def test_the_clock_only_starts_once_the_oven_reaches_the_profile_start(rig):
    """Beginning from an arbitrary temperature is the biggest avoidable
    source of run-to-run variation, so preheat holds the clock at zero."""
    app, clock, _, sensor, _, events = rig
    profile = warm_start_profile()
    sensor.temp = 25.0
    app.request_start(profile)
    run_for(app, clock, 5.0)
    assert app.state == STATE_PREHEAT
    assert app.elapsed == 0.0
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 1.0)
    assert app.state == STATE_RUNNING
    assert any(n == Event.RUN_STARTED for n, _ in events)


# -- the supervisor holds the veto -----------------------------------------

def test_no_heat_is_ever_commanded_once_a_fault_latches(rig):
    app, clock, relay, sensor, profile, _ = rig
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 2.0)
    assert app.state == STATE_RUNNING
    sensor.faults = hal.FAULT_OPEN_CIRCUIT
    run_for(app, clock, 1.0)
    assert app.state == STATE_FAULT
    relay.history = []
    run_for(app, clock, 30.0)
    assert not any(relay.history), "relay commanded on after a latched fault"


def test_a_sensor_that_raises_is_treated_as_no_reading(rig):
    app, clock, relay, sensor, profile, _ = rig
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 2.0)
    sensor.raise_on_read = True
    run_for(app, clock, 2.0)
    assert app.state == STATE_FAULT
    assert not relay.is_on()


def test_faults_need_acknowledging_before_another_run(rig):
    app, clock, _, sensor, profile, _ = rig
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 2.0)
    sensor.faults = hal.FAULT_OPEN_CIRCUIT
    run_for(app, clock, 1.0)
    sensor.faults = hal.FAULT_NONE
    sensor.temp = 25.0
    run_for(app, clock, 10.0)
    assert app.state == STATE_FAULT
    app.acknowledge_fault()
    assert app.state == STATE_IDLE


# -- abort ------------------------------------------------------------------

def test_abort_cuts_heat_immediately_and_goes_to_cooldown(rig):
    app, clock, relay, sensor, profile, events = rig
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 2.0)
    app.abort()
    assert not relay.is_on()
    assert app.state == STATE_COOLDOWN
    assert any(n == Event.ABORTED for n, _ in events)


def test_abort_from_idle_does_nothing(rig):
    app, _, _, _, _, _ = rig
    app.abort()
    assert app.state == STATE_IDLE


# -- events the interface and the speaker depend on -------------------------

def test_crossing_the_liquidus_is_announced_once_in_each_direction(rig):
    app, clock, _, sensor, profile, events = rig
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 1.0)
    sensor.temp = 230.0
    run_for(app, clock, 2.0)
    sensor.temp = 200.0
    run_for(app, clock, 2.0)
    ups = [n for n, _ in events if n == Event.ABOVE_LIQUIDUS]
    downs = [n for n, _ in events if n == Event.BELOW_LIQUIDUS]
    assert len(ups) == 1 and len(downs) == 1


def test_a_broken_event_handler_cannot_stop_the_control_loop(rig):
    app, clock, _, sensor, profile, _ = rig

    def explode(name, payload):
        raise RuntimeError("the UI is on fire")

    app.on_event = explode
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 5.0)
    assert app.state == STATE_RUNNING


def test_the_door_prompt_fires_on_the_way_down(rig):
    app, clock, _, sensor, profile, events = rig
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 1.0)
    sensor.temp = 230.0
    run_for(app, clock, 1.0)
    app.abort()
    sensor.temp = 180.0
    run_for(app, clock, 2.0)
    assert any(n == Event.OPEN_THE_DOOR for n, _ in events)


def test_cooldown_finishes_at_a_temperature_safe_to_open(rig):
    app, clock, _, sensor, profile, _ = rig
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 1.0)
    app.abort()
    sensor.temp = 45.0
    run_for(app, clock, 2.0)
    assert app.state == STATE_REPORT


# -- sampling ---------------------------------------------------------------

def test_every_control_step_produces_a_sample_for_the_log(rig):
    app, clock, _, sensor, profile, _ = rig
    rows = []
    app.sample = rows.append
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 5.0)
    assert len(rows) >= 19
    assert all("temp" in r and "state" in r and "relay" in r for r in rows)


def test_command_dispatch_tolerates_no_command():
    """poll_command returns None on every pass with no complete line. The
    equality branches tolerated that; a prefix match did not, and .startswith
    on None crashed the firmware on its first loop."""
    import ast
    import os
    src = open(os.path.join(os.path.dirname(__file__), "..", "firmware",
                            "code.py")).read()
    ast.parse(src)
    body = src[src.index("cmd = poll_command()"):]
    body = body[:body.index("display.render") if "display.render" in body
                else 1500]
    guard = body.index("if not cmd:")
    first_prefix = body.find(".startswith(")
    assert first_prefix == -1 or guard < first_prefix, (
        "a prefix match on the command appears before the None guard")


def test_a_finished_run_can_be_restarted_without_being_dismissed(rig):
    """A completed run parks on its report until someone presses DONE. With
    nobody at the oven that state persists, so starting must work from it.
    The firmware always allowed this; the host pre-flight did not, and a
    watcher waited on a state that could never arrive."""
    app, clock, _, sensor, profile, _ = rig
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    run_for(app, clock, 1.0)
    app.abort()
    sensor.temp = 45.0
    run_for(app, clock, 2.0)
    assert app.state == STATE_REPORT
    sensor.temp = 25.0
    assert app.request_start(profile) is None
    assert app.state == STATE_PREHEAT


def test_preheat_actually_energises_the_relay(rig):
    """Preheat must heat, not merely report a duty.

    On hardware the oven sat in preheat at 26.5 C with a target of 45 C,
    reporting duty=0.500 every step while the relay stayed open and the
    temperature drifted *down*. It would have sat there until the 900 s
    timeout. The cause: preheat's only duty value is exactly 0.5, and the
    drive gated on `duty > 0.5`, which is false for 0.5. Nothing in the
    telemetry looked wrong -- duty read 0.5, as intended -- so this asserts
    the relay, which is the only thing that means heat.
    """
    app, clock, relay, sensor, _, _ = rig
    sensor.temp = 26.5
    assert app.request_start(warm_start_profile()) is None
    assert app.state == STATE_PREHEAT
    run_for(app, clock, 20.0)
    assert app.state == STATE_PREHEAT, "should still be climbing to the start"
    assert app.duty > 0.0, "preheat should be asking for heat"
    assert any(relay.history), (
        "preheat commanded duty=%.2f for 20 s and the relay never closed"
        % app.duty)


def test_a_duty_of_exactly_one_half_produces_on_time(rig):
    """No relay path may use a strict comparison against its own duty value.

    Generalises the bug above: 0.5 is the exact boundary, so it is the value
    a threshold is most likely to mishandle, and it is the one preheat asks
    for every single time.
    """
    app, clock, relay, sensor, profile, _ = rig
    sensor.temp = 25.0
    assert app.request_start(profile) is None
    run_for(app, clock, 2.0)
    relay.history[:] = []
    for _ in range(80):
        clock.advance(0.25)
        app._drive(clock.monotonic(), 0.5)
    assert any(relay.history), "duty of exactly 0.5 never closed the relay"
    assert not all(relay.history), "duty of exactly 0.5 held the relay closed"


def test_a_completed_run_is_not_faulted_while_it_cools(rig):
    """Cooling takes longer than the profile that caused it.

    The run timeout used to keep running through cooldown. Once it followed
    the profile's own duration, a completed 360 s run faulted at 1050 s while
    passively cooling from 224 C -- and because faults latch, every later run
    was refused until someone acknowledged it. Cooldown has its own clock.

    The profile is followed exactly here so that nothing except a timeout is
    able to fault, and the run reaches cooldown the way a real one does
    rather than by jumping the clock (which the supervision-gap guard
    correctly refuses).
    """
    app, clock, relay, sensor, profile, _ = rig
    sensor.temp = profile.target_at(0.0)
    assert app.request_start(profile) is None

    for _ in range(int((profile.duration + 30.0) / CONTROL_INTERVAL_S)):
        clock.advance(CONTROL_INTERVAL_S)
        sensor.temp = profile.target_at(min(app.elapsed, profile.duration))
        app.tick()
        if app.state not in (STATE_RUNNING, STATE_PREHEAT):
            break
    assert app.state == STATE_COOLDOWN, (
        "expected cooldown, got %s (%s)"
        % (app.state, app.fault.message if app.fault else ""))

    # Twenty minutes of cooling at the control cadence -- longer than the
    # profile itself, which is the whole point.
    temp = sensor.temp
    for i in range(int(1200.0 / CONTROL_INTERVAL_S)):
        clock.advance(CONTROL_INTERVAL_S)
        temp = max(30.0, temp - 0.04)
        sensor.temp = temp
        app.tick()
        assert app.state != STATE_FAULT, (
            "faulted %.0f s into cooling at %.0f C: %s"
            % (i * CONTROL_INTERVAL_S, temp,
               app.fault.message if app.fault else "?"))


def test_a_warm_start_enters_the_profile_where_the_oven_already_is(rig):
    """A warm oven should not be handed a target below itself.

    Not a repair: back-to-back SAC305 runs from ~50 C met their J-STD
    windows without this. It shortens a warm run and makes the target
    meaningful immediately.
    """
    app, clock, relay, sensor, profile, events = rig
    sensor.temp = 60.0
    assert app.request_start(profile) is None
    run_for(app, clock, 2.0)
    assert app.state == STATE_RUNNING
    assert app.elapsed > 0.0, "a warm oven started at the beginning"
    # The target it is handed must match the oven, not sit far below it.
    assert app.target == pytest.approx(60.0, abs=3.0), (
        "entered at %.0f s where the target is %.1f C, with the oven at 60"
        % (app.elapsed, app.target))
    started = [p for n, p in events if n == "run_started"]
    assert started and "entered_at_s" in started[0], (
        "a skipped entry must be reported, not silent")


def test_a_cold_start_still_begins_at_zero(rig):
    app, clock, relay, sensor, profile, events = rig
    sensor.temp = 22.0
    assert app.request_start(profile) is None
    run_for(app, clock, 2.0)
    assert app.elapsed < 3.0
    started = [p for n, p in events if n == "run_started"]
    assert started and "entered_at_s" not in started[0]


def test_a_warm_run_is_not_given_the_full_duration_to_finish(rig):
    """The timeout has to shrink with the run, or it stops guarding."""
    app, clock, relay, sensor, profile, _ = rig
    sensor.temp = 60.0
    assert app.request_start(profile) is None
    run_for(app, clock, 2.0)
    remaining = profile.duration - app.elapsed
    assert remaining < profile.duration
