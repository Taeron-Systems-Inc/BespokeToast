# SPDX-License-Identifier: MIT
"""A simulated oven, so control changes can be judged without heating metal.

First order plus dead time — the standard model for a lag-dominant thermal
process:

    dT/dt = (K * u(t - L) - (T - T_ambient)) / tau

``L`` is transport lag between element and probe, and it is where coast comes
from: when ``u`` drops to zero the heat already in the pipe keeps arriving for
``L`` seconds and the oven keeps climbing.

**This oven's parameters are not known.** No step test has been run on it. So
there is no single model here to tune against — there is a *family*, bounded
below from first principles, and the controller is required to behave across
all of it. A controller that only works at the centre of the family is not
tuned, it is fitted.

The bounds come from what a domestic toaster oven physically is:

``K``    steady-state rise at full power. Element around 1200-1500 W against a
         loss coefficient of a few W/K puts the unloaded ceiling somewhere in
         250-450 C above ambient.
``tau``  thermal mass over loss coefficient. A few kg of steel at ~500 J/kg/K
         against those same losses gives 150-500 s.
``L``    element to probe transport. Anywhere from a few seconds if the probe
         sits in the airflow to the better part of a minute if it is clamped
         to a cool surface. **The probe's placement in this oven is not
         known**, which is why this bound is the widest of the three and why
         it dominates the difficulty.

Experiment E2 collapses this family to a fitted model. Until then, breadth is
the honest representation of what we know.
"""

import itertools


class Oven(object):
    def __init__(self, ambient_c=22.0, gain_c=340.0, tau_s=300.0,
                 dead_time_s=25.0, dt=0.25, noise=None, sensor_offset_c=0.0):
        self.ambient_c = ambient_c
        self.gain_c = gain_c
        self.tau_s = tau_s
        self.dead_time_s = dead_time_s
        self.dt = dt
        self.noise = noise
        self.sensor_offset_c = sensor_offset_c
        self.t = 0.0
        self.temp_c = ambient_c
        self._pipe = [0.0] * max(1, int(round(dead_time_s / dt)))

    def step(self, relay_on):
        self._pipe.append(1.0 if relay_on else 0.0)
        u = self._pipe.pop(0)
        drive = self.gain_c * u - (self.temp_c - self.ambient_c)
        self.temp_c += drive / self.tau_s * self.dt
        self.t += self.dt
        return self.temp_c

    def read(self):
        v = self.temp_c + self.sensor_offset_c
        if self.noise is not None:
            v += self.noise(self.t)
        return v


# The bounds argued for above.
GAIN_RANGE = (250.0, 450.0)
TAU_RANGE = (150.0, 500.0)
DEAD_TIME_RANGE = (5.0, 60.0)


def family(include_centre=True):
    """Corners of the plausible parameter space, plus its centre.

    Corners, not a random sample: for a monotone plant like this the extremes
    are where a controller breaks, and eight cases run in well under a second.
    """
    out = []
    for g, t, l in itertools.product(GAIN_RANGE, TAU_RANGE, DEAD_TIME_RANGE):
        out.append({"gain_c": g, "tau_s": t, "dead_time_s": l})
    if include_centre:
        out.append({"gain_c": sum(GAIN_RANGE) / 2,
                    "tau_s": sum(TAU_RANGE) / 2,
                    "dead_time_s": sum(DEAD_TIME_RANGE) / 2})
    return out


def describe(params):
    return "K=%.0f tau=%.0f L=%.0f" % (
        params["gain_c"], params["tau_s"], params["dead_time_s"])


def measure_coast(oven_factory, setpoint_c=100.0, dt=0.25, timeout_s=3000.0):
    """Heat to a setpoint, cut power, and see how far and how long the oven
    keeps climbing. This is what experiment E2 performs on the real oven;
    running it against a simulated one is how the two get compared.

    Returns ``(overshoot_c, seconds_to_peak)``.
    """
    o = oven_factory()
    t = 0.0
    while o.temp_c < setpoint_c and t < timeout_s:
        o.step(True)
        t += dt
    cut_temp = o.temp_c
    cut_t = t
    peak = cut_temp
    peak_t = cut_t
    while t - cut_t < timeout_s:
        o.step(False)
        t += dt
        if o.temp_c > peak:
            peak = o.temp_c
            peak_t = t
        elif o.temp_c < peak - 0.05:
            break
    return peak - cut_temp, peak_t - cut_t
