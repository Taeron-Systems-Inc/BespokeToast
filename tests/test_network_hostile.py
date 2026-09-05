"""What must stay true when the network misbehaves.

The ESP32 co-processor is driven over SPI by adafruit_esp32spi, whose calls
BLOCK. A socket read that stalls for seconds inside the control path would
walk straight through the 250 ms control cadence. These tests encode the rule
that keeps that from mattering: no network I/O in the control path, ever.

Written before the radio is brought up rather than after, because the failure
they describe is one you cannot reproduce on demand once it is in.
"""

import os

import pytest

from oven import hal
from oven.app import App, CONTROL_INTERVAL_S, STATE_RUNNING, STATE_FAULT
from oven.controller import Controller, FeedForward, PID
from oven.profile import Profile
from oven.safety import Supervisor, Limits

PROFILES = os.path.join(os.path.dirname(__file__), "..", "firmware", "profiles")


class Clock(object):
    def __init__(self):
        self.t = 0.0

    def monotonic(self):
        return self.t


class Relay(object):
    def __init__(self):
        self._on = False
        self.on_samples = 0

    def set(self, on):
        self._on = bool(on)
        if self._on:
            self.on_samples += 1

    def is_on(self):
        return self._on


class Sensor(object):
    def __init__(self):
        self.temp = 25.0

    def read(self):
        return hal.Reading(self.temp, cold=30.0, cpu=34.0)


def rig(supervisor=None):
    profile = Profile.load(os.path.join(PROFILES, "ts391snl.json"))
    clock, relay, sensor = Clock(), Relay(), Sensor()
    app = App(relay, sensor, clock,
              lambda p: Controller(p, coast_tau_s=1.2,
                                   feed_forward=FeedForward(), pid=PID()),
              supervisor=supervisor or Supervisor(Limits(max_rate_c_per_s=1e6)))
    return app, clock, relay, sensor, profile


def test_a_blocking_network_call_in_the_loop_faults_the_run():
    """A stall does not silently pass. Nine seconds is long enough that the
    profile clock has moved on without anyone watching the oven, so the run
    ends rather than resuming against a timeline that no longer describes
    reality."""
    app, clock, relay, sensor, profile = rig()
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    for _ in range(8):
        clock.t += CONTROL_INTERVAL_S
        app.tick()
    assert app.state == STATE_RUNNING
    clock.t += 9.0                      # a socket read hangs for nine seconds
    app.tick()
    assert app.state == STATE_FAULT
    assert not relay.is_on()


def test_a_stall_while_heating_faults_rather_than_carrying_on():
    """A gap in supervision while the relay is on is not a step anyone can
    vouch for, so it trips instead of being ignored."""
    sup = Supervisor(Limits(max_rate_c_per_s=1e6, sensor_stale_s=3.0))
    app, clock, relay, sensor, profile = rig(sup)
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    for _ in range(20):
        clock.t += CONTROL_INTERVAL_S
        app.tick()
    relay.set(True)
    clock.t += 30.0                     # the network wedged for half a minute
    app.tick()
    assert app.state == STATE_FAULT
    assert not relay.is_on()


def test_heat_is_never_left_on_across_a_stall():
    app, clock, relay, sensor, profile = rig()
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    for _ in range(20):
        clock.t += CONTROL_INTERVAL_S
        app.tick()
    clock.t += 45.0
    app.tick()
    assert not relay.is_on(), "relay left energised through a network stall"


def test_the_control_loop_never_calls_out_to_a_network():
    """Structural, not behavioural: app.py must not import or reference a
    network module. The rule is easier to keep than to remember."""
    import ast
    src = open(os.path.join(os.path.dirname(__file__), "..", "firmware",
                            "oven", "app.py")).read()
    names = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    forbidden = {"net", "socket", "ssl", "adafruit_requests",
                 "adafruit_esp32spi", "wifi", "socketpool"}
    assert not (names & forbidden), (
        "app.py reaches the network: %s. Association, time sync and uploads "
        "belong outside the control path." % (names & forbidden))


@pytest.mark.parametrize("stall_s", [0.5, 2.0, 5.0, 20.0])
def test_cadence_recovers_after_a_stall_of_any_length(stall_s):
    """However long the network hangs, the loop must resume on its grid
    rather than firing a burst of catch-up steps."""
    app, clock, relay, sensor, profile = rig()
    app.request_start(profile)
    sensor.temp = profile.target_at(0.0)
    for _ in range(8):
        clock.t += CONTROL_INTERVAL_S
        app.tick()
    clock.t += stall_s
    app.tick()
    fired = 0
    for _ in range(4):
        clock.t += CONTROL_INTERVAL_S * 0.4
        if app.tick():
            fired += 1
    assert fired <= 2, "burst of catch-up steps after a %.1fs stall" % stall_s
