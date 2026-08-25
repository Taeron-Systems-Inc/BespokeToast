# SPDX-License-Identifier: MIT
"""An oven built from what this oven actually does.

The parametric fit failed on real data: heating rate rises to a peak near
80 C instead of decaying from the start, heating and cooling time constants
differ by about 2.5x, and a fitted 20 s dead time predicted roughly 17 C of
coast where 1.1 C was measured. Rather than force a first-order model onto a
process that plainly is not one, this interpolates the measured curves.

    dT/dt = c(T) + u * (h(T) - c(T))

``h(T)`` is the measured rate at full power and ``c(T)`` the measured rate
with the relay open, so u=1 and u=0 reproduce the step test by construction
and everything between is a linear blend. Valid over the measured range; it
extrapolates flat beyond it, which is honest but not informative.
"""

import json
import os

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data",
                    "oven-characterisation.json")


def _interp(table, x):
    if x <= table[0][0]:
        return table[0][1]
    if x >= table[-1][0]:
        return table[-1][1]
    for i in range(1, len(table)):
        if table[i][0] >= x:
            x0, y0 = table[i - 1]
            x1, y1 = table[i]
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return table[-1][1]


class MeasuredOven(object):
    def __init__(self, path=None, dt=0.25, start_c=None, lag_s=3.0,
                 scale_heat=1.0, scale_cool=1.0):
        d = json.load(open(path or DATA))
        self.heat = sorted(d["heating_rate_c_per_s"])
        self.cool = sorted(d["cooling_rate_c_per_s"])
        self.ambient_c = d["ambient_c"]
        self.dt = dt
        self.temp_c = self.ambient_c if start_c is None else start_c
        self.scale_heat = scale_heat
        self.scale_cool = scale_cool
        # the measured 3 s coast, as transport lag on the drive
        self._pipe = [0.0] * max(1, int(round(lag_s / dt)))
        self.t = 0.0

    def rates(self, temp_c):
        return (_interp(self.heat, temp_c) * self.scale_heat,
                _interp(self.cool, temp_c) * self.scale_cool)

    def step(self, relay_on):
        self._pipe.append(1.0 if relay_on else 0.0)
        u = self._pipe.pop(0)
        h, c = self.rates(self.temp_c)
        self.temp_c += (c + u * (h - c)) * self.dt
        self.t += self.dt
        return self.temp_c

    def read(self):
        return self.temp_c


def hold_duty_table(path=None):
    """The feed-forward table: duty required to hold a temperature."""
    d = json.load(open(path or DATA))
    return [(T, u) for T, u in d["hold_duty"]]


def capability(path=None):
    d = json.load(open(path or DATA))
    return {"max_ramp_up": max(r for _, r in d["heating_rate_c_per_s"]),
            "max_ramp_down": -min(r for _, r in d["cooling_rate_c_per_s"]),
            "coast_tau_s": d["coast_tau_s"]}
