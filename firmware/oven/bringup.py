# SPDX-License-Identifier: MIT
"""Bringing the radio up without stopping the oven.

Nothing here waits, and nothing here imports a board. Every call to
:meth:`Bringup.step` does at most one command to the co-processor and
returns, so the caller keeps rendering, keeps reading the touchscreen and
keeps its control cadence.

That matters more than it sounds. The blocking version took a measured
24.22 s with the network healthy, and the oven answered nothing at all for
the whole of it -- no telemetry, no touch, no console -- while the screen
held whatever frame was last drawn. It looked like a hang, and twice it was
reported as one. Boot did it twice over, because the clock and the web page
each brought the radio up from scratch.

The waiting was never in one long call. The library polls: a scan sleeps 2 s
and retries ten times, a join reads a status register every 50 ms, the clock
is asked once a second. The longest indivisible thing is a single SPI
transaction, measured at 227 ms worst case. So the waiting could always have
been somebody else's turn.

An abort button was considered and is deliberately not here. It existed to
escape a lock-out, and there is no lock-out to escape: the oven is fully
usable while this runs, START included.

The co-processor is duck-typed -- ``start_scan_networks``, ``get_scan_networks``,
``wifi_set_passphrase``, ``is_connected``, ``get_time`` -- so this is tested
on a host against a fake, which is the whole reason it does not live in
radio.py.
"""

import time

from oven import netconfig
from oven import timesync

SCANNING = "scanning"
JOINING = "joining"
TIMING = "timing"
READY = "ready"
FAILED = "failed"

# One scan attempt in the library sleeps 2 s and retries ten times, so this
# is the same patience expressed as a deadline rather than a blocking loop.
SCAN_TIMEOUT_S = 20.0
# connect_AP's own default, per attempt. The first attempt fails often
# enough that a single try reads as "no network here" when the network is
# fine, which is why there is more than one.
JOIN_TIMEOUT_S = 10.0
JOIN_ATTEMPTS = 3
CLOCK_TIMEOUT_S = 20.0


class Bringup(object):
    """Scan, join and read the clock, one command per step."""

    def __init__(self, networks, radio, monotonic=None, want_clock=True):
        self.radio = radio
        self.networks = networks
        self.want_clock = want_clock
        self._now = monotonic or time.monotonic
        self.state = None
        self.network = None
        self.ip = None
        self.epoch = None
        self.detail = "starting"
        self._esp = None
        self._deadline = 0.0
        self._attempt = 0
        # A state change never also issues a command: the next pass does
        # that. It costs a quarter of a second per transition and it is what
        # makes "one command per step" true rather than nearly true, so the
        # worst a single pass can cost is one SPI transaction, 227 ms.
        self._pending_join = False
        self._pending_ip = False

    @property
    def finished(self):
        return self.state in (READY, FAILED)

    @property
    def connected(self):
        return self.ip is not None

    def status_text(self):
        """One short line for the screen. Not a log message."""
        if self.state == SCANNING:
            return "looking for a network"
        if self.state == JOINING:
            return "joining %s" % (self.network.ssid if self.network else "")
        if self.state == TIMING:
            return "setting the clock"
        if self.state == READY:
            return self.ip or "no network"
        if self.state == FAILED:
            return "no network"
        return "starting the radio"

    def _fail(self, detail):
        self.detail = detail
        self.state = FAILED
        return self.state

    def step(self):
        """Advance by one command. Returns the state after doing so."""
        try:
            return self._step()
        except Exception as e:
            # A radio that misbehaves must not take the oven with it.
            # Everything this does is optional work.
            return self._fail("%r" % (e,))

    def _step(self):
        if self.state is None:
            return self._begin()
        if self.state == SCANNING:
            return self._scan()
        if self.state == JOINING:
            return self._join()
        if self.state == TIMING:
            return self._clock()
        return self.state

    def _begin(self):
        if not self.networks:
            return self._fail("no networks configured")
        # Constructing the ESP object resets the co-processor. It is the one
        # step here that genuinely blocks, and it is short. The scan it
        # starts is a separate command, so it waits for the next pass.
        self._esp = self.radio._hardware()
        self._esp.start_scan_networks()
        self._deadline = self._now() + SCAN_TIMEOUT_S
        self.state = SCANNING
        return self.state

    def _scan(self):
        found = self._esp.get_scan_networks()
        if found:
            seen = [(_ssid(ap["ssid"]), ap["rssi"]) for ap in found]
            self.network = netconfig.choose(self.networks, seen)
            if self.network is None:
                return self._fail("none of the known networks are in range")
            self._pending_join = True
            self.state = JOINING
            return self.state
        if self._now() >= self._deadline:
            return self._fail("no networks found in %.0f s" % SCAN_TIMEOUT_S)
        return self.state

    def _start_join(self):
        """Issue the passphrase. One command, and nothing else."""
        self._attempt += 1
        self._esp.wifi_set_passphrase(_bytes(self.network.ssid),
                                      _bytes(self.network.password))
        self._deadline = self._now() + JOIN_TIMEOUT_S
        self.state = JOINING
        return self.state

    def _join(self):
        if self._pending_join:
            self._pending_join = False
            return self._start_join()
        if self._pending_ip:
            self._pending_ip = False
            self.ip = self.radio.ip
            if not self.want_clock:
                self.state = READY
                return self.state
            self._deadline = self._now() + CLOCK_TIMEOUT_S
            self.state = TIMING
            return self.state
        # Asked as a question rather than compared against the library's
        # status constants: is_connected already handles the OSError that a
        # busy co-processor raises, and not importing the constants is what
        # lets this module be tested without a board.
        if self._esp.is_connected:
            self._pending_ip = True
            return self.state
        # Only the deadline ends an attempt. The status reads "disconnected"
        # for most of a perfectly normal join -- which is why the library
        # waits out its whole timeout before looking at it, and why acting
        # on it early would break every connection.
        if self._now() >= self._deadline:
            if self._attempt >= JOIN_ATTEMPTS:
                return self._fail("could not join %s in %d attempts"
                                  % (self.network.ssid, self._attempt))
            self._pending_join = True
            return self.state
        return self.state

    def _clock(self):
        # The co-processor runs its own SNTP client and is not ready the
        # instant the network is joined: it raises rather than saying "not
        # yet", and returns something small rather than an error when SNTP
        # has failed outright. Hence the try, and hence timesync.
        try:
            seconds = self._esp.get_time()
        except Exception:
            seconds = None
        if isinstance(seconds, (tuple, list)):
            seconds = seconds[0] if seconds else 0
        if seconds:
            try:
                seconds = int(seconds)
            except (TypeError, ValueError):
                seconds = 0
        if seconds and timesync.looks_set(seconds):
            self.epoch = seconds
            self.detail = "clock set"
            self.state = READY
            return self.state
        if self._now() >= self._deadline:
            # The network is up and the clock is not. That is a working oven
            # with unstamped logs, not a failure to connect, so this is
            # READY: the page still needs serving.
            self.detail = "no time from the network in %.0f s" % CLOCK_TIMEOUT_S
            self.state = READY
            return self.state
        return self.state


def _ssid(raw):
    if isinstance(raw, str):
        return raw
    try:
        return str(raw, "utf-8")
    except Exception:
        return ""


def _bytes(text):
    if isinstance(text, bytes):
        return text
    return bytes(text, "utf-8")
