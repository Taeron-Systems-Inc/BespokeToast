# SPDX-License-Identifier: MIT
"""Run a whole profile in simulation: controller, oven, and supervisor
together, at the cadence the firmware will actually use."""

from oven.hal import Reading
from oven.controller import Controller
from oven.metrics import RunMetrics
from oven.safety import Supervisor

from .thermal import Oven

CONTROL_DT = 0.25


class Result(object):
    def __init__(self):
        self.trace = []          # (t, temp, target, duty, relay)
        self.metrics = None
        self.fault = None
        self.actuations = 0
        self.max_abs_error = 0.0
        self.rms_error = 0.0


def simulate(profile, oven=None, controller=None, supervisor=None,
             dt=CONTROL_DT, tail_s=0.0):
    """Run *profile* to completion. Returns a :class:`Result`."""
    oven = oven or Oven(dt=dt)
    ctl = controller or Controller(profile)
    sup = supervisor if supervisor is not None else Supervisor()
    ctl.reset(0.0)
    sup.begin_run(0.0)

    res = Result()
    m = RunMetrics(profile.liquidus_c or 0.0)
    t = 0.0
    relay = False
    total = profile.duration + tail_s
    err_sq = 0.0
    n = 0

    while t <= total:
        temp = oven.read()
        f = sup.update(t, Reading(temp, cold=25.0), relay)
        if f is not None:
            res.fault = f
            break

        duty = ctl.duty_for(t, temp, t)
        if not sup.allow_heat():
            duty = 0.0
        relay = ctl.relay_state(t, duty)

        m.add(t, temp)
        target = profile.target_at(t)
        err = temp - target
        if abs(err) > res.max_abs_error:
            res.max_abs_error = abs(err)
        err_sq += err * err
        n += 1
        res.trace.append((t, temp, target, duty, relay))

        oven.step(relay)
        t += dt

    res.metrics = m
    res.actuations = ctl.tpo.actuations
    res.rms_error = (err_sq / n) ** 0.5 if n else 0.0
    return res
