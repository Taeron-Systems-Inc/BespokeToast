# SPDX-License-Identifier: MIT
"""Hardware interfaces.

Everything else in this package talks to the oven only through the shapes
described here. Nothing in this module imports ``board`` — the real
implementations live in ``hardware.py``, and the tests substitute simulated
ones. That separation is what lets the control and safety logic run under
CPython on a laptop.

These are documentation, not enforced base classes: CircuitPython has no
``abc``, and duck typing costs nothing here.

Clock
    ``monotonic()`` -> float seconds, monotonically increasing.

TempSensor
    ``read()`` -> ``Reading``. Must not raise for ordinary sensor faults;
    report them in the reading so the safety layer decides what they mean.

Relay
    ``set(on)`` and ``is_on()``. ``set(False)`` must be the safe direction.
"""

# Sensor fault flags, combined as a bitmask on Reading.faults.
FAULT_NONE = 0
FAULT_OPEN_CIRCUIT = 1 << 0    # thermocouple open / disconnected
FAULT_SHORT_CIRCUIT = 1 << 1   # thermocouple shorted
FAULT_BUS = 1 << 2             # I2C or device communication failure
FAULT_RANGE = 1 << 3           # reading outside the sensor's valid range

FAULT_NAMES = (
    (FAULT_OPEN_CIRCUIT, "thermocouple open circuit"),
    (FAULT_SHORT_CIRCUIT, "thermocouple short circuit"),
    (FAULT_BUS, "sensor bus failure"),
    (FAULT_RANGE, "reading out of range"),
)


def describe_faults(faults):
    """Human-readable list of the fault bits set in *faults*."""
    if not faults:
        return []
    return [name for bit, name in FAULT_NAMES if faults & bit]


class Reading(object):
    """One temperature sample.

    ``hot`` is the thermocouple junction in °C, or None if unavailable.
    ``cold`` is the sensor's own cold-junction temperature in °C, which
    doubles as a measure of how warm the enclosure is getting. ``faults`` is
    a bitmask of the FAULT_* constants above.

    A reading with faults set may still carry a value; it is the safety
    layer's job to refuse it, not the driver's job to hide it.
    """

    __slots__ = ("hot", "cold", "faults", "t", "cpu")

    def __init__(self, hot, cold=None, faults=FAULT_NONE, t=None, cpu=None):
        self.hot = hot
        self.cold = cold
        self.faults = faults
        self.t = t
        # Controller die temperature: a second thermometer in the same box on
        # a different chip. The difference between it and ``cold`` is what
        # shows whether the enclosure is warming or just the sensor.
        self.cpu = cpu

    @property
    def ok(self):
        return self.faults == FAULT_NONE and self.hot is not None

    def __repr__(self):
        return "Reading(hot=%r, cold=%r, faults=%d)" % (
            self.hot, self.cold, self.faults)
