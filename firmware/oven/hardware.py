# SPDX-License-Identifier: MIT
"""The only module that touches the board.

Everything else in this package is plain stdlib and runs under CPython, which
is what makes the control and safety logic testable. That property is only
worth anything if this file stays the single exception — so keep board,
digitalio, busio and their kin here.

A note on fault detection, because it shapes the safety design. The MCP9600
does **not** have the dedicated open-circuit and short-circuit detection bits
that the MCP9601 carries. A disconnected thermocouple on this part does not
announce itself; it produces a reading. So the checks below are the input
range flag, an I2C failure, and plausibility bounds — and the rest of the work
falls to the supervisor's stall and frozen-value guards, which catch a probe
that reads plausibly but is not measuring the oven.
"""

import board
import busio
import digitalio
import microcontroller
import time

import adafruit_touchscreen

from adafruit_mcp9600 import MCP9600

from . import hal

RELAY_PIN = board.D4
MCP9600_ADDRESS = 0x67
I2C_FREQUENCY = 100000
THERMOCOUPLE_TYPE = "K"

_STATUS_REGISTER = 0x04
_STATUS_INPUT_RANGE = 1 << 4

# Anything outside this is not a temperature this oven can be at.
PLAUSIBLE_MIN_C = -20.0
PLAUSIBLE_MAX_C = 400.0


class Relay(object):
    """The mains relay on D4.

    Measured on this oven: an external pulldown holds the relay de-energised
    whenever the pin is not driven, so releasing the pin — on reset, on an
    unhandled exception, on a watchdog reset — is a safe state rather than an
    undefined one.
    """

    def __init__(self, pin=RELAY_PIN):
        self._io = digitalio.DigitalInOut(pin)
        self._io.direction = digitalio.Direction.OUTPUT
        self._io.value = False
        self._on = False
        self.actuations = 0

    def set(self, on):
        on = bool(on)
        if on != self._on:
            self.actuations += 1
            self._on = on
        self._io.value = on

    def is_on(self):
        return self._on

    def off(self):
        self.set(False)

    def deinit(self):
        try:
            self._io.value = False
        finally:
            self._io.deinit()


class Thermocouple(object):
    """MCP9600 + type-K probe, reporting faults rather than hiding them."""

    def __init__(self, i2c=None, address=MCP9600_ADDRESS):
        self._i2c = i2c or busio.I2C(board.SCL, board.SDA,
                                     frequency=I2C_FREQUENCY)
        self._address = address
        self._sensor = MCP9600(self._i2c, address, THERMOCOUPLE_TYPE)

    def read(self):
        faults = hal.FAULT_NONE
        hot = cold = None
        try:
            hot = self._sensor.temperature
            cold = self._sensor.ambient_temperature
        except Exception:
            # Any I2C or device error is a bus fault. Deliberately broad:
            # the supervisor's job is to refuse heat, not to diagnose.
            return hal.Reading(None, None, hal.FAULT_BUS, time.monotonic())

        try:
            if self._status() & _STATUS_INPUT_RANGE:
                faults |= hal.FAULT_RANGE
        except Exception:
            faults |= hal.FAULT_BUS

        if hot is None or not (PLAUSIBLE_MIN_C <= hot <= PLAUSIBLE_MAX_C):
            faults |= hal.FAULT_RANGE

        return hal.Reading(hot, cold, faults, time.monotonic())

    def _status(self):
        buf = bytearray(1)
        while not self._i2c.try_lock():
            pass
        try:
            self._i2c.writeto_then_readfrom(
                self._address, bytes([_STATUS_REGISTER]), buf)
        finally:
            self._i2c.unlock()
        return buf[0]


class Touchscreen(object):
    """Resistive touch panel.

    Calibration carried over from the previous firmware, which is the only
    place it was ever recorded. It should be re-derived at some point, but
    it demonstrably worked on this panel.
    """

    CALIBRATION = ((5200, 59000), (5800, 57000))

    def __init__(self):
        self._ts = adafruit_touchscreen.Touchscreen(
            board.TOUCH_XL, board.TOUCH_XR, board.TOUCH_YD, board.TOUCH_YU,
            calibration=self.CALIBRATION,
            size=(board.DISPLAY.width, board.DISPLAY.height))
        self._was_down = False

    def press(self):
        """Return (x, y) once per touch, on the press edge.

        Edge-triggered deliberately: a held finger must not repeat an action,
        and START is not something to trigger twice.
        """
        point = self._ts.touch_point
        if point is None:
            self._was_down = False
            return None
        if self._was_down:
            return None
        self._was_down = True
        return (point[0], point[1])


class Clock(object):
    def monotonic(self):
        return time.monotonic()


def cpu_temperature():
    """SAMD51 die temperature — a second, independent read on how warm the
    enclosure is getting, free of the thermocouple's cold junction."""
    try:
        return microcontroller.cpu.temperature
    except Exception:
        return None


class Hardware(object):
    """Everything the application needs, assembled and in a safe state."""

    def __init__(self):
        self.relay = Relay()          # first: the pin is claimed and driven low
        self.clock = Clock()
        self.sensor = Thermocouple()
        self.touch = Touchscreen()

    def safe(self):
        self.relay.off()
