# SPDX-License-Identifier: MIT
"""The shipped curves, against the specs and the standards they claim.

Three profiles said "derived from data/oven-characterisation.json" and no
code derived them. The characterisation has since been measured three times
and the curves never moved, because moving them meant somebody redoing the
arithmetic by hand. These tests exist so that cannot happen again: the spec
plus the measurement is the source, and a shipped file that has drifted from
it is a failure, not a discovery someone makes months later.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.append(os.path.join(ROOT, "tools"))

import make_profile as M                                    # noqa: E402

from oven.controller import Controller, FeedForward, PID     # noqa: E402
from oven.metrics import Limits as MetricLimits              # noqa: E402
from oven.metrics import RunMetrics                          # noqa: E402
from oven.profile import Profile                             # noqa: E402

from sim.measured import MeasuredOven                        # noqa: E402

DATA = json.load(open(os.path.join(ROOT, "data",
                                   "oven-characterisation.json")))
SPECS = M.load_specs()
PROFILES = os.path.join(ROOT, "firmware", "profiles")
NAMES = sorted(SPECS)

# Reflow profiles judged against J-STD-020. The bake, the step test and the
# diagnostic fixture are not reflow and the classification profile does not
# apply to them.
REFLOW = [n for n in NAMES if SPECS[n].get("category") == "reflow"
          and not SPECS[n].get("diagnostic")]


@pytest.fixture(scope="module")
def oven():
    return M.Oven()


def built(name, oven):
    return M.profile_from_spec(SPECS[name], oven)


# -- the shipped files are the generated ones ------------------------------

@pytest.mark.parametrize("name", NAMES)
def test_the_shipped_profile_is_what_the_spec_generates(name, oven):
    profile, _measured, _warnings = built(name, oven)
    expected = M.render(profile)
    path = os.path.join(PROFILES, name + ".json")
    assert os.path.exists(path), "%s is specified but not shipped" % name
    assert open(path).read() == expected, (
        "firmware/profiles/%s.json has drifted from its spec. Regenerate:\n"
        "    python3 tools/make_profile.py --write %s" % (name, name))


@pytest.mark.parametrize("name", NAMES)
def test_every_generated_profile_loads(name, oven):
    profile, _m, _w = built(name, oven)
    p = Profile.from_dict(profile)
    assert p.points
    assert p.duration > 0


def test_every_shipped_profile_has_a_spec():
    """Otherwise the generator quietly stops covering one of them."""
    shipped = {f[:-5] for f in os.listdir(PROFILES) if f.endswith(".json")}
    assert shipped == set(NAMES), (
        "shipped but unspecified: %s; specified but not shipped: %s"
        % (sorted(shipped - set(NAMES)), sorted(set(NAMES) - shipped)))


# -- the curve is faithful to the measurement it came from -----------------

@pytest.mark.parametrize("name", NAMES)
def test_the_points_represent_the_curve_they_came_from(name, oven):
    """A profile is stored as points and read back by straight lines between
    them, so the question is not how far apart they are but how far the
    chords stray from the integrated curve."""
    _p, measured, _w = built(name, oven)
    tolerance = SPECS[name].get("tolerance_c", 1.0)
    assert measured["worst_chord_error_c"] <= tolerance + 0.01


@pytest.mark.parametrize("name", NAMES)
def test_a_profile_fits_through_the_ovens_own_upload_route(name, oven):
    """Measured ceiling 2700 bytes, limit set at 2560. A profile too big to
    send back to the oven it came from can only be changed over USB, behind
    two screws."""
    profile, _m, _w = built(name, oven)
    size = len(M.render(profile))
    assert size <= 2560, "%s is %d bytes" % (name, size)


@pytest.mark.parametrize("name", NAMES)
def test_needing_the_door_is_derived_not_declared(name, oven):
    """Whether a curve outruns door-shut cooling is arithmetic on the curve
    and the measurement. It was a flag someone had to remember to set."""
    profile, measured, _w = built(name, oven)
    shut = min(oven.cooling_rate(c) for _, c in profile["points"])
    outruns = measured["max_ramp_down_c_per_s"] < shut - 0.05
    assert profile.get("cooling_assumes_open_door", False) == outruns


# -- what the standards ask for --------------------------------------------

@pytest.mark.parametrize("name", REFLOW)
def test_the_peak_sits_where_the_alloy_wants_it(name, oven):
    """20-40 C above liquidus is the general rule for a solder peak: below
    it the joint may not wet, above it the components take heat they do not
    need. TS391SNL sat 18 C above liquidus at its old 235 C peak."""
    profile, measured, _w = built(name, oven)
    liquidus = profile["liquidus_c"]
    over = measured["peak_c"] - liquidus
    assert 20.0 <= over <= 40.0, (
        "%s peaks %.0f C above liquidus" % (name, over))


@pytest.mark.parametrize("name", REFLOW)
def test_the_peak_is_a_temperature_this_oven_has_reached(name, oven):
    profile, measured, _w = built(name, oven)
    assert measured["peak_c"] <= oven.hottest_measured_c, (
        "%s peaks at %g C and the step tests reached %g"
        % (name, measured["peak_c"], oven.hottest_measured_c))


@pytest.mark.parametrize("name", REFLOW)
def test_the_curve_earns_its_own_time_above_liquidus(name, oven):
    """The nominal figure, from the curve alone. What the oven then does is
    tested below; this catches a curve that could not pass even if the oven
    followed it perfectly."""
    profile, measured, _w = built(name, oven)
    tal = measured["time_above_liquidus_s"]
    assert profile["tal_min_s"] <= tal <= profile["tal_max_s"], (
        "%s asks for %.0f s above liquidus against a %g-%g window"
        % (name, tal, profile["tal_min_s"], profile["tal_max_s"]))


@pytest.mark.parametrize("name", REFLOW)
def test_the_dwell_at_peak_is_inside_j_std_020(name, oven):
    """Time within 5 C of peak, capped at 30 s. A profile that earns its
    time above liquidus by sitting at the top is exactly how this gets
    exceeded without anyone looking at it."""
    _p, measured, _w = built(name, oven)
    assert measured["time_within_5c_of_peak_s"] <= 30.0


@pytest.mark.parametrize("name", REFLOW)
def test_time_to_peak_is_inside_j_std_020(name, oven):
    _p, measured, _w = built(name, oven)
    assert measured["time_to_peak_s"] <= 480.0


def test_the_lead_free_soak_is_inside_j_std_020(oven):
    """150-200 C for 60-120 s. Only the lead-free profile goes through that
    band at all -- the low-temperature alloys peak at 165 C."""
    _p, measured, _w = built("ts391snl", oven)
    assert 60.0 <= measured["soak_150_to_200_s"] <= 120.0


@pytest.mark.parametrize("name", NAMES)
def test_no_curve_asks_for_more_than_the_oven_has(name, oven):
    """Except STEP 250 C, which asks for more on purpose: the controller
    saturating is what makes it a step response."""
    if name == "step-250c":
        return
    profile, _m, _w = built(name, oven)
    for (t0, c0), (t1, c1) in zip(profile["points"], profile["points"][1:]):
        if t1 <= t0 or c1 <= c0:
            continue
        asked = (c1 - c0) / (t1 - t0)
        have = oven.heating_rate((c0 + c1) / 2.0)
        assert asked <= have, (
            "%s asks %.2f C/s at %.0f C and this oven has %.2f"
            % (name, asked, c0, have))


# -- and what the oven actually does with them -----------------------------

def _simulate(profile_dict, scale_heat=1.0, door_latency_s=1.0):
    """A run, including the door for the profiles that need one.

    The two low-temperature pastes fall faster than this oven does shut, so
    their runs are not defined without the door: leaving it closed put run
    0001 at 132 s above liquidus against a 90 s ceiling. The rule for WHEN
    is the firmware's own -- open when the accumulated time plus the descent
    lands mid-window -- restated here rather than driven through App, so
    that a profile can be judged without standing up the state machine.
    Runs 0005 and 0007 are what says the rule works on real hardware.
    """
    p = Profile.from_dict(profile_dict)
    ff = FeedForward(heating_rates=DATA["heating_rate_c_per_s"],
                     cooling_rates=DATA["cooling_rate_c_per_s"])
    ctl = Controller(p, coast_tau_s=DATA["coast_tau_s"], feed_forward=ff,
                     pid=PID(kp=0.22, ki=0.004, kd=0.5, i_max=0.6, i_min=-0.6))
    ctl.reset(0.0)
    o = MeasuredOven(dt=0.25, start_c=p.points[0][1], scale_heat=scale_heat)
    m = RunMetrics(p.liquidus_c or 0.0)

    wants_door = bool(profile_dict.get("cooling_assumes_open_door"))
    mid = ((p.tal_min_s or 0.0) + (p.tal_max_s or p.tal_min_s or 0.0)) / 2.0
    opens_at = None

    t = 0.0
    err = 0.0
    n = 0
    while t <= p.duration:
        temp = o.read()
        m.add(t, temp)
        err += abs(temp - p.target_at(t))
        n += 1

        if wants_door and opens_at is None and mid:
            descent = max(0.0, (temp - p.liquidus_c) / M.DOOR_C_PER_S)
            if m.time_above_liquidus + descent >= mid:
                opens_at = t + door_latency_s

        if opens_at is not None and t >= opens_at:
            frac = min(1.0, (t - opens_at) / 3.0)      # measured 3 s onset
            _h, c = o.rates(o.temp_c)
            o.temp_c += (c + frac * (-M.DOOR_C_PER_S - c)) * 0.25
        else:
            o.step(ctl.relay_state(t, ctl.duty_for(t, temp, t)))
        t += 0.25
    return p, m, err / max(1, n)


@pytest.mark.parametrize("name", REFLOW)
def test_the_oven_passes_every_check_on_the_generated_curve(name, oven):
    profile, _m, _w = built(name, oven)
    p, m, _mean = _simulate(profile)
    failures = [c[0] for c in m.check(MetricLimits.for_profile(p)) if not c[2]]
    assert not failures, "%s failed: %s" % (name, failures)


@pytest.mark.parametrize("name", REFLOW)
@pytest.mark.parametrize("scale", [0.85, 1.0, 1.15])
def test_the_curves_survive_the_plant_being_wrong(name, scale, oven):
    """The measured model is one oven on one day, and the profile is built
    from it. A curve that only works when the model is exactly right is a
    curve that works once."""
    profile, _m, _w = built(name, oven)
    p, m, _mean = _simulate(profile, scale_heat=scale)
    lim = MetricLimits.for_profile(p)
    assert lim.peak_min_c <= m.peak_c <= lim.peak_max_c, (
        "%s at plant scale %g peaked at %.1f C" % (name, scale, m.peak_c))


def test_the_low_temperature_opening_tracks_now(oven):
    """The digitised chart asked 1.33 C/s from cold where measurement gives
    about 0.58, and runs 0005 and 0007 both lagged it by 21 s at 45 C and
    then overtook it by 15 s at 90 C. Simulated mean error over the first
    two minutes was 12 C; the generated opening brings it under 4.
    """
    for name in ("ts391lt", "nc191lta10-datasheet"):
        profile, _m, _w = built(name, oven)
        p = Profile.from_dict(profile)
        ff = FeedForward(heating_rates=DATA["heating_rate_c_per_s"],
                         cooling_rates=DATA["cooling_rate_c_per_s"])
        ctl = Controller(p, coast_tau_s=DATA["coast_tau_s"], feed_forward=ff,
                         pid=PID(kp=0.22, ki=0.004, kd=0.5,
                                 i_max=0.6, i_min=-0.6))
        ctl.reset(0.0)
        o = MeasuredOven(dt=0.25)
        t = 0.0
        errs = []
        while t <= 120.0:
            temp = o.read()
            errs.append(abs(temp - p.target_at(t)))
            o.step(ctl.relay_state(t, ctl.duty_for(t, temp, t)))
            t += 0.25
        mean = sum(errs) / len(errs)
        assert mean < 4.0, "%s opens with %.1f C of mean error" % (name, mean)
        assert max(errs) < 10.0, "%s peaks at %.1f C of error" % (name,
                                                                 max(errs))


def test_the_step_test_stops_heating_near_the_top(oven):
    """The characterisation run only measures what it stops driving.

    Run 0008's relay was still firing at 333 s with the oven down to 232 C,
    so the highest clean free-cooling sample was 224 C -- below where the
    cooling table already reached, and the run extended nothing. The cause
    was a straight-line descent of -0.57 C/s against a -0.72 C/s oven: the
    oven outran its own target downwards and the controller kept topping it
    back up. Following the measured curve down is what fixes it, and this
    is the assertion that says so.
    """
    profile, _m, _w = built("step-250c", oven)
    p = Profile.from_dict(profile)
    ff = FeedForward(heating_rates=DATA["heating_rate_c_per_s"],
                     cooling_rates=DATA["cooling_rate_c_per_s"])
    ctl = Controller(p, coast_tau_s=DATA["coast_tau_s"], feed_forward=ff,
                     pid=PID(kp=0.22, ki=0.004, kd=0.5, i_max=0.6, i_min=-0.6))
    ctl.reset(0.0)
    o = MeasuredOven(dt=0.25, start_c=p.points[0][1])

    t = 0.0
    peak = 0.0
    last_on_c = None
    while t <= p.duration:
        temp = o.read()
        peak = max(peak, temp)
        on = ctl.relay_state(t, ctl.duty_for(t, temp, t))
        if on:
            last_on_c = temp
        o.step(on)
        t += 0.25

    assert peak >= 245.0, "only reached %.1f C" % peak
    assert last_on_c is not None
    assert last_on_c >= 245.0, (
        "the heater was last on at %.1f C, so everything above that is not "
        "free cooling and the run extends the table no further than %.0f"
        % (last_on_c, last_on_c))


def test_the_step_tests_hold_is_worth_its_thirty_seconds(oven):
    """Guards the other direction, and corrects a wrong guess.

    Removing the hold looked like a tidy-up, and the first attempt at it
    made the run peak at 212 C -- but that was a ramp asking twice the
    oven's capability, not the missing hold. With the ramp matched to
    capability the hold is worth 5 C of peak and, more to the point, 5 C of
    where the relay stops firing, which is where the useful part of the
    cooling curve begins.
    """
    import copy
    spec = copy.deepcopy(SPECS["step-250c"])
    spec["segments"] = [s for s in spec["segments"] if "hold_s" not in s]
    profile, _m, _w = M.profile_from_spec(spec, oven)
    _p, without, _mean = _simulate(profile)
    profile, _m, _w = built("step-250c", oven)
    _p, with_hold, _mean = _simulate(profile)
    assert with_hold.peak_c > without.peak_c + 2.0, (
        "the hold buys %.1f C; if that has fallen to nothing it can go"
        % (with_hold.peak_c - without.peak_c))
