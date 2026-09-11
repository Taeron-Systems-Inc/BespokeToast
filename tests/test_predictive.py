"""Predictive tracking: the controller acts on where the chamber will be,
given the element's stored heat, rather than on where it is."""
import json
import os

from oven.controller import Controller, FeedForward, PID
from oven.elementff import ElementModel
from oven.profile import Profile

ROOT = os.path.join(os.path.dirname(__file__), "..")
D = json.load(open(os.path.join(ROOT, "data", "oven-characterisation.json")))
LT = Profile.load(os.path.join(ROOT, "firmware", "profiles", "ts391lt.json"))
EM = D["element_model"]
MODEL = ElementModel(g=EM["g"], beta=EM["beta"], gamma=EM["gamma"],
                     d=EM["d"], ambient_c=EM["ambient_c"])


def make(lead_s=0.0, model=MODEL):
    ff = FeedForward(heating_rates=D["heating_rate_c_per_s"],
                     cooling_rates=D["cooling_rate_c_per_s"])
    c = Controller(LT, coast_tau_s=D["coast_tau_s"], feed_forward=ff,
                   pid=PID(kp=0.22, ki=0.004, kd=0.5, i_max=0.6, i_min=-0.6),
                   element_model=model, lead_s=lead_s)
    c.reset(0.0)
    return c


def knee():
    """The time the soak begins: the profile's first drop in slope."""
    t, last = 0.0, LT.slope_at(0.0)
    while t < LT.peak[0]:
        s = LT.slope_at(t)
        if s < last - 0.3:
            return t
        last = s
        t += 1.0
    raise AssertionError("no knee in the profile")


def test_without_element_state_it_is_the_old_loop():
    a, b = make(lead_s=6.0), make(lead_s=0.0)
    for t in range(0, 120):
        temp = LT.target_at(float(t)) - 2.0
        assert a.duty_for(float(t), temp) == b.duty_for(float(t), temp)


def test_without_a_model_the_lead_is_ignored():
    a = make(lead_s=6.0, model=None)
    b = make(lead_s=0.0)
    for t in range(0, 60):
        temp = LT.target_at(float(t))
        assert a.duty_for(float(t), temp, element_z=1.5) == \
            b.duty_for(float(t), temp)


def test_stored_heat_lowers_the_demand():
    """Two identical chambers; the one whose element is hotter is asked
    for less, because more is already on its way."""
    t = 30.0
    cold, hot = make(6.0), make(6.0)
    temp = LT.target_at(t)
    assert hot.duty_for(t, temp, element_z=1.6) < \
        cold.duty_for(t, temp, element_z=0.2)


def test_the_knee_is_seen_before_it_arrives():
    """Four seconds before the soak begins, the lead loop is already
    asking for the soak's rate; the old loop is still ramping."""
    k = knee()
    t = k - 4.0
    temp = LT.target_at(t)
    z = MODEL.z_for(LT.slope_at(t), temp)      # exactly what the ramp needs
    with_lead = make(6.0).duty_for(t, temp, element_z=z)
    without = make(0.0).duty_for(t, temp)
    assert with_lead < without - 0.2


class Spy(object):
    """Delegates to a profile and records every time it was asked about."""
    def __init__(self, profile):
        self._p = profile
        self.asked = []

    def target_at(self, t):
        self.asked.append(t)
        return self._p.target_at(t)

    def slope_at(self, t):
        self.asked.append(t)
        return self._p.slope_at(t)

    def __getattr__(self, name):
        return getattr(self._p, name)


def test_the_lead_never_looks_past_the_peak_on_the_way_up():
    peak_t = LT.peak[0]
    c = make(6.0)
    c.profile = Spy(LT)
    t = peak_t - 1.0
    c.duty_for(t, LT.target_at(t), element_z=0.5)
    assert c.profile.asked and max(c.profile.asked) <= peak_t + 1e-9


# -- through the App --------------------------------------------------------

from oven.app import App, STATE_RUNNING
from oven.safety import Supervisor, Limits
from test_precharge import FakeClock, FakeRelay, FakeSensor, tick


class RecordingObserver(object):
    def __init__(self):
        self.fed = []
        self.z = 0.7

    def update(self, t, temp, applied):
        self.fed.append((t, temp, applied))
        return self.z


class RecordingController(object):
    """Stands in for Controller; keeps what duty_for was told."""
    def __init__(self):
        self.seen = []

    def reset(self, t=0.0):
        pass

    def duty_for(self, elapsed_s, temp_c, t=None, element_z=None):
        self.seen.append(element_z)
        return 0.5

    def relay_state(self, t, duty):
        return True


def app_rig(observer_factory):
    clock, relay, sensor = FakeClock(), FakeRelay(), FakeSensor(34.0)
    ctl = RecordingController()
    app = App(relay, sensor, clock, lambda p: ctl,
              supervisor=Supervisor(Limits(max_rate_c_per_s=1e6)),
              on_event=lambda n, p: None)
    app.observer_factory = observer_factory
    return app, clock, ctl


def test_the_observer_is_fed_every_running_step_and_read_by_the_controller():
    obs = RecordingObserver()
    app, clock, ctl = app_rig(lambda p, t: obs)
    assert app.request_start(LT) is None
    tick(app, clock, 40)
    assert app.state == STATE_RUNNING
    assert len(obs.fed) >= 30
    assert all(a in (0.0, 1.0) for _, _, a in obs.fed)
    assert ctl.seen and all(z == 0.7 for z in ctl.seen[-10:])


def test_without_an_observer_factory_the_controller_is_told_nothing():
    app, clock, ctl = app_rig(None)
    assert app.request_start(LT) is None
    tick(app, clock, 40)
    assert ctl.seen and all(z is None for z in ctl.seen)


def test_an_observer_factory_that_raises_does_not_take_the_run_with_it():
    def bad(p, t):
        raise RuntimeError("no model today")
    app, clock, ctl = app_rig(bad)
    assert app.request_start(LT) is None
    tick(app, clock, 40)
    assert app.state == STATE_RUNNING
    assert all(z is None for z in ctl.seen)
