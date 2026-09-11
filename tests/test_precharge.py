# SPDX-License-Identifier: MIT
"""Heating the element before the run clock starts.

The state machine side: preheat hands to precharge, precharge hands to
running when the observer says so or when it runs out of time, and an oven
with no factory behaves exactly as it did before this existed. The model
side is tested against the PreCharge class directly.
"""
import os

import pytest

from oven import hal
from oven.app import (App, Event, STATE_IDLE, STATE_PREHEAT, STATE_PRECHARGE,
                      STATE_RUNNING, CONTROL_INTERVAL_S)
from oven.controller import Controller, FeedForward, PID
from oven.elementff import ElementModel, ElementObserver, PreCharge
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

    def read(self):
        return hal.Reading(self.temp, cold=30.0, faults=hal.FAULT_NONE)


class ScriptedPreCharge(object):
    """Says 'charge' for *steps* ticks, then 'go'. Records what it saw."""

    def __init__(self, steps, max_s=40.0):
        self.steps = steps
        self.max_s = max_s
        self.observer = self
        self.z = 0.0
        self.started_at = None
        self.fed = []
        self._last_t = None

    def update(self, t, temp, applied):
        self.fed.append((t, temp, applied))
        self._last_t = t
        return self.z

    def duty(self, t):
        if self.started_at is None:
            self.started_at = t
        if self.steps <= 0:
            return None
        self.steps -= 1
        return 1.0


def rig(temp=34.0, factory=None):
    profile = Profile.load(os.path.join(PROFILES, "ts391snl.json"))
    clock, relay, sensor = FakeClock(), FakeRelay(), FakeSensor(temp)
    events = []
    app = App(relay, sensor, clock,
              lambda p: Controller(p, coast_tau_s=1.2,
                                   feed_forward=FeedForward(), pid=PID()),
              supervisor=Supervisor(Limits(max_rate_c_per_s=1e6)),
              on_event=lambda n, p: events.append((n, p)))
    app.precharge_factory = factory
    return app, clock, relay, sensor, profile, events


def tick(app, clock, n=1):
    for _ in range(n):
        clock.advance(CONTROL_INTERVAL_S)
        app.tick()


# -- the state machine -----------------------------------------------------

def test_without_a_factory_a_run_starts_the_way_it_always_did():
    app, clock, relay, sensor, profile, events = rig(factory=None)
    app.tick()
    app.request_start(profile)
    tick(app, clock, 2)
    assert app.state == STATE_RUNNING
    assert STATE_PRECHARGE not in [e[1].get("stage") for e in events
                                  if e[0] == Event.STAGE_CHANGED]


def test_a_factory_that_returns_none_is_the_same_as_no_factory():
    app, clock, relay, sensor, profile, events = rig(
        factory=lambda p, t: None)
    app.tick()
    app.request_start(profile)
    tick(app, clock, 2)
    assert app.state == STATE_RUNNING


def test_preheat_hands_to_precharge_and_precharge_hands_to_running():
    pc = ScriptedPreCharge(steps=8)
    app, clock, relay, sensor, profile, events = rig(
        factory=lambda p, t: pc)
    app.tick()
    app.request_start(profile)
    tick(app, clock, 1)
    assert app.state == STATE_PRECHARGE
    stages = [e[1].get("stage") for e in events if e[0] == Event.STAGE_CHANGED]
    assert "precharge" in stages
    tick(app, clock, 12)
    assert app.state == STATE_RUNNING
    assert "precharge done" in stages or any(
        e[1].get("stage") == "precharge done" for e in events)


def test_the_relay_is_driven_while_charging_and_released_on_handover():
    pc = ScriptedPreCharge(steps=6)
    app, clock, relay, sensor, profile, events = rig(factory=lambda p, t: pc)
    app.tick()
    app.request_start(profile)
    tick(app, clock, 1)
    on_during = []
    while app.state == STATE_PRECHARGE:
        tick(app, clock, 1)
        on_during.append(relay.is_on())
    assert any(on_during), "the element was never driven during precharge"
    assert app.state == STATE_RUNNING


def test_the_observer_is_fed_every_step_with_what_the_relay_did():
    pc = ScriptedPreCharge(steps=5)
    app, clock, relay, sensor, profile, events = rig(factory=lambda p, t: pc)
    app.tick()
    app.request_start(profile)
    tick(app, clock, 8)
    assert len(pc.fed) >= 5
    for t, temp, applied in pc.fed:
        assert applied in (0.0, 1.0)
        assert temp == 34.0


def test_the_run_clock_does_not_advance_while_charging():
    """The whole point: the profile does not start until the element can
    follow it."""
    pc = ScriptedPreCharge(steps=10)
    app, clock, relay, sensor, profile, events = rig(factory=lambda p, t: pc)
    app.tick()
    app.request_start(profile)
    tick(app, clock, 1)
    assert app.state == STATE_PRECHARGE
    t_wall_start = clock.t
    tick(app, clock, 6)
    assert app.state == STATE_PRECHARGE
    # elapsed is only meaningful once running; the run has not started
    assert app._run_started is None
    assert clock.t - t_wall_start > 1.0


def test_a_factory_that_raises_does_not_take_the_run_with_it():
    def bad(p, t):
        raise RuntimeError("model on fire")
    app, clock, relay, sensor, profile, events = rig(factory=bad)
    app.tick()
    app.request_start(profile)
    tick(app, clock, 2)
    assert app.state == STATE_RUNNING


def test_abort_works_during_precharge():
    pc = ScriptedPreCharge(steps=100)
    app, clock, relay, sensor, profile, events = rig(factory=lambda p, t: pc)
    app.tick()
    app.request_start(profile)
    tick(app, clock, 3)
    assert app.state == STATE_PRECHARGE
    app.abort()
    tick(app, clock, 1)
    assert app.state != STATE_PRECHARGE
    assert not relay.is_on()


# -- the model side --------------------------------------------------------

def model():
    return ElementModel(g=0.12047, beta=0.07635, gamma=1.07e-05,
                        d=0.003680, ambient_c=23.5)


class TinyPlant(object):
    """The identified two-state plant, so the chamber answers the element.

    A first version of the test below fed the observer a fixed 34.0 C, and
    the observer -- correctly -- concluded the element was delivering
    nothing: a chamber that never moves is exactly what a dead element
    looks like, and the correction step dragged the estimate down against
    the prediction. That is not a bug in the observer. It is a test that
    lied to it.
    """

    def __init__(self, m, start_c):
        self.m = m
        self.tc = start_c
        self.z = 0.0

    def step(self, u, dt=0.25):
        m = self.m
        self.z += (m.g * u - m.beta * self.z + m.gamma * (self.tc - m.ambient_c)) * dt
        self.tc += (self.z - m.d * (self.tc - m.ambient_c)) * dt
        return self.tc


def test_precharge_says_go_once_the_element_has_charged():
    m = model()
    plant = TinyPlant(m, 34.0)
    obs = ElementObserver(m)
    pc = PreCharge(obs, needed_z=0.6, max_s=40.0, margin=1.0)
    t = 0.0
    seen_charging = False
    while pc.duty(t) is not None:
        seen_charging = True
        obs.update(t, plant.tc, 1.0)
        plant.step(1.0)
        t += 0.25
        assert t < 40.0, "never charged"
    assert seen_charging
    assert obs.z >= 0.6 * 0.95


def test_precharge_gives_up_at_its_bound():
    obs = ElementObserver(model())
    pc = PreCharge(obs, needed_z=100.0, max_s=10.0, margin=1.0)
    t = 0.0
    while pc.duty(t) is not None:
        obs.update(t, 34.0, 1.0)
        t += 0.25
    assert 9.5 <= t <= 10.5


def test_a_cold_start_needs_almost_nothing():
    """The curve's opening from cold is slow, so the contribution it needs
    is small and the observer reaches it in a second or two. Simulation
    says cold starts are unaffected by pre-charge; this is why."""
    p = Profile.load(os.path.join(PROFILES, "ts391snl.json"))
    m = model()
    need = m.z_for(p.slope_at(0.0), 25.0)
    obs = ElementObserver(m)
    pc = PreCharge(obs, need, max_s=40.0, margin=1.0)
    t = 0.0
    while pc.duty(t) is not None:
        obs.update(t, 25.0, 1.0)
        t += 0.25
    assert t < 5.0, "a cold start pre-charged for %.1f s" % t


def test_the_hottest_legal_start_needs_the_most():
    p = Profile.load(os.path.join(PROFILES, "ts391snl.json"))
    m = model()
    need_cold = m.z_for(p.slope_at(p.entry_time_for(25.0)), 25.0)
    need_hot = m.z_for(p.slope_at(p.entry_time_for(59.4)), 59.4)
    assert need_hot > need_cold
