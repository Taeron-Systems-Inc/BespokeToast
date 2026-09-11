# SPDX-License-Identifier: MIT
"""An observer for the state the plant model was missing: the element.

The loop this sits beside -- docs/control-loop.md, tag
known-good-loop-2026-09-10 -- inverts a plant with no element state. On a
warm start the oven lagged its curve by 24-32 C for the first ninety
seconds with duty pinned at 1.0 the whole time. No gain fixes an actuator
that is already flat out, and this file does not try to: the first version
of it added a state-feedback term to the feed-forward and moved the
worst-case lag from -11.5 to -11.5. Asking harder for what the plant cannot
give is what the old loop already did.

What an element observer buys is knowing WHEN the element is ready. The fix
for a saturated start is not more duty during the run, it is heat before
the run clock starts, stopped at the moment the element can carry the
curve's first segment -- see PreCharge. That is a timing decision, and this
is the state it is made on.

## The plant, in the form that can be identified

    z       the element's contribution to chamber rate, C/s
    dz/dt   = g*u - beta*z + gamma*(Tc - Ta)
    dTc/dt  = z - d*(Tc - Ta)

It is the two-state model from tools/identify_plant.py with the element
temperature eliminated. That model's a and c trade off -- only their product
reaches the chamber, and four runs spread them 202% and 150% -- so this uses
the combinations the chamber can see: g = c*a, beta = b + c, gamma = c*d.
beta (the element time constant, 10-14 s in every fit) and d (chamber loss)
are pinned down. Leave-one-out over four real runs, it predicts the held-out
run two to five times better than the one-state model.

## What is not settled, deliberately

Its steady state disagrees with the measured heating table by up to 30% at
the ends of the range. Forcing it onto the table -- table steady state,
two-state dynamics -- made prediction WORSE on every fold (7.8-17.5 C rms
against 4.6-6.5). One reading is that the table is not steady state: it came
from a cold-start step test, so its entries are trajectory rates on a
charging element, and the fitted model is recovering the true gain. The
other is that the model is linear where the oven radiates. The plateaux held
in the 2026-09-11 identification run decide it, and until they do the
steady-state duty is taken from whichever source the caller passes in. That
is not indecision; it is not choosing on a coin toss.
"""

from oven.controller import clamp


class ElementModel(object):
    """The identified plant, in chamber-observable parameters."""

    __slots__ = ("g", "beta", "gamma", "d", "ambient_c")

    def __init__(self, g, beta, gamma, d, ambient_c):
        self.g = float(g)
        self.beta = float(beta)
        self.gamma = float(gamma)
        self.d = float(d)
        self.ambient_c = float(ambient_c)

    @classmethod
    def from_two_state(cls, a, b, c, d, ambient_c):
        """From the a,b,c,d that tools/identify_plant.py fits."""
        return cls(g=c * a, beta=b + c, gamma=c * d, d=d, ambient_c=ambient_c)

    def z_for(self, rate_c_per_s, temp_c):
        """Element contribution needed for *rate* at *temp*."""
        return rate_c_per_s + self.d * (temp_c - self.ambient_c)

    def hold_duty(self, z, temp_c):
        """Duty that keeps the element contribution at *z*, per the linear
        model. One of two candidate steady-state sources; see the module
        docstring for why it is not the only one."""
        return (self.beta * z - self.gamma * (temp_c - self.ambient_c)) / self.g

    def full_power_rate(self, temp_c):
        """Steady-state chamber rate at duty 1, per the linear model."""
        loss = self.d * (temp_c - self.ambient_c)
        z_ss = (self.g + self.gamma * (temp_c - self.ambient_c)) / self.beta
        return z_ss - loss


class ElementObserver(object):
    """Estimate of the element's contribution to chamber rate.

    Integrates the model forward with the duty actually applied, then
    corrects toward what the chamber rate says the contribution must have
    been. The measured rate is taken over a window for the same reason the
    PID's derivative is: 0.0625 C of quantisation at 4 Hz is 0.25 C/s of
    slope that is not there.

    The correction gain is modest on purpose. The prediction step carries
    the element's dynamics, which is the thing the chamber cannot see
    directly; the correction only keeps it from drifting. A gain near 1
    would turn this into a filtered derivative of the chamber and throw the
    prediction away.
    """

    def __init__(self, model, gain=0.15, window_s=3.0):
        self.model = model
        self.gain = gain
        self.window_s = window_s
        self.reset()

    def reset(self, z=0.0):
        self.z = float(z)
        self._history = []
        self._last_t = None
        self._last_u = 0.0

    def measured_rate(self):
        h = self._history
        if len(h) < 2:
            return None
        t1, c1 = h[-1]
        for t0, c0 in h:
            if t1 - t0 <= self.window_s:
                if t1 - t0 < self.window_s * 0.5:
                    return None
                return (c1 - c0) / (t1 - t0)
        return None

    def update(self, t, temp_c, applied_duty):
        m = self.model
        self._history.append((t, temp_c))
        cutoff = t - self.window_s * 2
        while len(self._history) > 2 and self._history[0][0] < cutoff:
            self._history.pop(0)

        if self._last_t is not None:
            dt = t - self._last_t
            if 0 < dt < 5.0:
                dz = (m.g * self._last_u - m.beta * self.z
                      + m.gamma * (temp_c - m.ambient_c))
                self.z += dz * dt
                r = self.measured_rate()
                if r is not None:
                    z_from_chamber = r + m.d * (temp_c - m.ambient_c)
                    self.z += self.gain * (z_from_chamber - self.z)
        self._last_t = t
        self._last_u = float(applied_duty)
        return self.z


class PreCharge(object):
    """Heat the element before the run clock starts, and say when to start.

    The warm-start lag is a saturated actuator: the curve asks for a rate
    the moment the clock starts, the element is stone cold, and for the
    next ten to fourteen seconds nothing the controller asks for arrives.
    The old loop and the first version of this file both responded by
    asking harder. The plant does not care how hard it is asked.

    So instead: full duty with the clock held, until the observer says the
    element's contribution has reached what the curve's opening needs, or
    until a bound is hit. Then start. The oven enters the profile where it
    already is -- entry_time_for is unchanged -- but it enters it with an
    element that can follow.

    Bounded at about two time constants. An element that has not charged
    in that long is not going to, and holding a hot oven still while
    waiting for a model is the wrong failure.
    """

    def __init__(self, observer, needed_z, max_s=28.0, margin=0.9):
        self.observer = observer
        self.needed_z = float(needed_z)
        self.max_s = float(max_s)
        self.margin = float(margin)
        self.started_at = None
        self.done = False

    def duty(self, t):
        """1.0 while charging; None once the run may start."""
        if self.done:
            return None
        if self.started_at is None:
            self.started_at = t
        if self.observer.z >= self.needed_z * self.margin:
            self.done = True
            return None
        if t - self.started_at >= self.max_s:
            self.done = True
            return None
        return 1.0

    @property
    def elapsed(self):
        return 0.0 if self.started_at is None else (self.observer._last_t or self.started_at) - self.started_at


class ElementFeedForward(object):
    """Feed-forward with the observer behind it, steady state pluggable.

    duty_for(temp, rate) keeps the FeedForward signature. `steady_state` is
    a callable (temp, rate) -> duty; pass the old FeedForward.duty_for to
    take it from the measured tables, or model.hold_duty-based to take it
    from the linear model. Which is right is what the plateau data decides.
    """

    def __init__(self, model, steady_state, observer=None):
        self.model = model
        self.steady_state = steady_state
        self.observer = observer or ElementObserver(model)

    def reset(self):
        self.observer.reset()

    def observe(self, t, temp_c, applied_duty):
        return self.observer.update(t, temp_c, applied_duty)

    def duty_for(self, temp_c, rate_c_per_s=0.0):
        return clamp(self.steady_state(temp_c, rate_c_per_s), 0.0, 1.0)

    def achievable_rate(self, temp_c, duty=1.0):
        loss = self.model.d * (temp_c - self.model.ambient_c)
        z_ss = (self.model.g * duty
                + self.model.gamma * (temp_c - self.model.ambient_c)) \
            / self.model.beta
        return z_ss - loss
