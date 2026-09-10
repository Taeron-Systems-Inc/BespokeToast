# SPDX-License-Identifier: MIT
"""Bringing the radio up a step at a time.

The thing under test is that no step waits. Every assertion here is really
the same one: after N calls the state is X, and each call did one command --
so a caller that renders between calls renders N times, where the blocking
version rendered once in 24 seconds.
"""
import pytest

from oven import bringup
from oven.bringup import Bringup, SCANNING, JOINING, TIMING, READY, FAILED
from oven.netconfig import Network


class Clock(object):
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


class FakeESP(object):
    """The co-processor, as a small state machine.

    Deliberately unhelpful in the same ways the real one is: the scan comes
    back empty for a while, and is_connected stays False for most of a join
    that is going to succeed.
    """

    def __init__(self, aps=(("Voxelis", -40),), scan_after=3,
                 connect_after=8, time_after=4, epoch=1788973181):
        self.aps = list(aps)
        self.scan_after = scan_after
        self.connect_after = connect_after
        self.time_after = time_after
        self.epoch = epoch
        self.commands = []
        self._scans = 0
        self._status_reads = 0
        self._time_reads = 0
        self.passphrases = []

    def start_scan_networks(self):
        self.commands.append("start_scan")

    def get_scan_networks(self):
        self.commands.append("get_scan")
        self._scans += 1
        if self._scans < self.scan_after:
            return None
        return [{"ssid": bytes(s, "utf-8"), "rssi": r} for s, r in self.aps]

    def wifi_set_passphrase(self, ssid, password):
        self.commands.append("passphrase")
        self.passphrases.append((ssid, password))
        self._status_reads = 0

    @property
    def is_connected(self):
        self.commands.append("status")
        self._status_reads += 1
        return self._status_reads >= self.connect_after

    def get_time(self):
        self.commands.append("get_time")
        self._time_reads += 1
        if self._time_reads < self.time_after:
            raise RuntimeError("_GET_TIME returned 0")
        return self.epoch


class FakeRadio(object):
    def __init__(self, esp, ip="10.20.10.242"):
        self.esp = esp
        self._ip = ip

    def _hardware(self):
        return self.esp

    @property
    def ip(self):
        return self._ip


def networks():
    return [Network("Voxelis", "secret"), Network("Taeron", "other")]


def drive(b, clock, limit=400, dt=0.25):
    """Step the way the loop will: one call, a quarter second, repeat."""
    steps = 0
    while not b.finished and steps < limit:
        b.step()
        clock.advance(dt)
        steps += 1
    return steps


# -- the happy path --------------------------------------------------------

def test_it_gets_there():
    clock = Clock()
    esp = FakeESP()
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock)
    assert b.state == READY
    assert b.ip == "10.20.10.242"
    assert b.epoch == 1788973181
    assert b.connected


def test_no_step_does_more_than_one_command():
    """The whole point. If any step issued two commands to the
    co-processor, the worst case for a single pass would double."""
    clock = Clock()
    esp = FakeESP()
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    while not b.finished:
        before = len(esp.commands)
        b.step()
        clock.advance(0.25)
        assert len(esp.commands) - before <= 1, esp.commands[before:]


def test_it_passes_through_every_stage_in_order():
    clock = Clock()
    b = Bringup(networks(), FakeRadio(FakeESP()), monotonic=clock)
    seen = []
    while not b.finished:
        state = b.step()
        clock.advance(0.25)
        if not seen or seen[-1] != state:
            seen.append(state)
    assert seen == [SCANNING, JOINING, TIMING, READY]


def test_it_joins_the_strongest_known_network():
    clock = Clock()
    esp = FakeESP(aps=(("Taeron", -30), ("Voxelis", -70), ("Guest", -20)))
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock)
    assert b.network.ssid == "Taeron"
    assert esp.passphrases[0][0] == b"Taeron"


def test_the_status_line_says_what_it_is_doing():
    clock = Clock()
    b = Bringup(networks(), FakeRadio(FakeESP()), monotonic=clock)
    lines = []
    while not b.finished:
        b.step()
        clock.advance(0.25)
        text = b.status_text()
        if not lines or lines[-1] != text:
            lines.append(text)
    assert lines[0] == "looking for a network"
    assert "joining Voxelis" in lines
    assert "setting the clock" in lines
    assert lines[-1] == "10.20.10.242"


# -- and every way it goes wrong -------------------------------------------

def test_nothing_configured_fails_at_once_without_touching_the_radio():
    esp = FakeESP()
    b = Bringup([], FakeRadio(esp), monotonic=Clock())
    assert b.step() == FAILED
    assert esp.commands == []


def test_a_scan_that_never_returns_anything_gives_up_on_a_deadline():
    clock = Clock()
    esp = FakeESP(scan_after=10 ** 6)
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock, limit=1000)
    assert b.state == FAILED
    assert "no networks found" in b.detail
    # Bounded by the deadline, not by the number of polls.
    assert clock.t - 1000.0 <= bringup.SCAN_TIMEOUT_S + 1.0


def test_an_unknown_network_is_not_joined():
    clock = Clock()
    esp = FakeESP(aps=(("SomebodyElse", -30),))
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock)
    assert b.state == FAILED
    assert "none of the known networks" in b.detail
    assert esp.passphrases == []


def test_a_join_is_retried_before_it_is_given_up_on():
    """The first attempt fails often enough that one try reads as "no
    network here" when the network is fine."""
    clock = Clock()
    esp = FakeESP(connect_after=10 ** 6)
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock, limit=2000)
    assert b.state == FAILED
    assert len(esp.passphrases) == bringup.JOIN_ATTEMPTS


def test_a_slow_join_is_not_mistaken_for_a_failed_one():
    """is_connected reads False for most of a join that is going to work.
    Acting on that early would break every connection."""
    clock = Clock()
    # succeeds on the 30th status read, well inside one 10 s attempt at 4 Hz
    esp = FakeESP(connect_after=30)
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock)
    assert b.state == READY
    assert len(esp.passphrases) == 1


def test_a_network_without_a_clock_is_still_a_working_network():
    """The page still needs serving, and a run still needs to happen. An
    unstamped log is worse than a stamped one and much better than no
    oven."""
    clock = Clock()
    esp = FakeESP(time_after=10 ** 6)
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock, limit=2000)
    assert b.state == READY
    assert b.epoch is None
    assert b.connected
    assert "no time from the network" in b.detail


def test_an_unbelievable_time_is_refused():
    """An unsynced NINA returns something small rather than an error, and a
    log full of 1970 is how that shows up later."""
    clock = Clock()
    esp = FakeESP(epoch=42)
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock, limit=2000)
    assert b.state == READY
    assert b.epoch is None


def test_a_radio_that_raises_does_not_take_the_oven_with_it():
    class Exploding(object):
        def _hardware(self):
            raise RuntimeError("SPI is on fire")
        ip = None

    b = Bringup(networks(), Exploding(), monotonic=Clock())
    assert b.step() == FAILED
    assert "SPI is on fire" in b.detail
    assert b.step() == FAILED          # and stays there, without raising


def test_a_finished_bringup_stops_doing_commands():
    clock = Clock()
    esp = FakeESP()
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock)
    drive(b, clock)
    count = len(esp.commands)
    for _ in range(10):
        b.step()
    assert len(esp.commands) == count


def test_a_bringup_that_was_not_asked_for_a_clock_reports_none():
    """A warm boot keeps its RTC, so the bring-up is told not to bother.
    Reporting the bring-up's detail regardless printed "clock: starting" on
    every warm boot, which reads as a failure and is the opposite."""
    clock = Clock()
    esp = FakeESP()
    b = Bringup(networks(), FakeRadio(esp), monotonic=clock, want_clock=False)
    drive(b, clock)
    assert b.state == READY
    assert b.epoch is None
    assert b.want_clock is False
    assert b.connected
    assert "get_time" not in esp.commands
