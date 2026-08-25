import json
import os

import pytest

from oven.profile import Profile, ProfileError, CATEGORY_BAKE

HERE = os.path.dirname(__file__)
PROFILES = os.path.join(HERE, "..", "firmware", "profiles")


def make(points, **kw):
    d = {"name": "test", "points": points, "liquidus_c": 217}
    d.update(kw)
    return Profile.from_dict(d)


# -- the shipped profiles must all load -------------------------------------

def test_every_shipped_profile_loads():
    names = [f for f in os.listdir(PROFILES) if f.endswith(".json")]
    assert names, "no profiles shipped"
    for n in names:
        Profile.load(os.path.join(PROFILES, n))


def test_sac305_matches_the_curve_the_oven_has_been_running():
    p = Profile.load(os.path.join(PROFILES, "sac305.json"))
    assert p.peak == (300.0, 235.0)
    assert p.duration == 360.0
    assert p.liquidus_c == 217
    # the field fix: comfortably above liquidus, unlike the 225 C original
    assert p.peak[1] - p.liquidus_c >= 15


# -- validation is strict ---------------------------------------------------

def test_rejects_non_increasing_time():
    with pytest.raises(ProfileError, match="strictly increase"):
        make([[0, 25], [60, 100], [60, 120]])


def test_rejects_backwards_time():
    with pytest.raises(ProfileError, match="strictly increase"):
        make([[0, 25], [60, 100], [30, 120]])


def test_rejects_not_starting_at_zero():
    with pytest.raises(ProfileError, match="must start at t=0"):
        make([[1, 25], [60, 100]])


def test_rejects_single_point():
    with pytest.raises(ProfileError, match="at least two"):
        make([[0, 25]])


def test_rejects_absurd_temperature():
    with pytest.raises(ProfileError, match="outside the permitted range"):
        make([[0, 25], [60, 900]])


def test_rejects_negative_temperature():
    with pytest.raises(ProfileError, match="outside the permitted range"):
        make([[0, -5], [60, 100]])


def test_rejects_unknown_category():
    with pytest.raises(ProfileError, match="unknown category"):
        make([[0, 25], [60, 100]], category="incinerate")


def test_reflow_without_liquidus_is_refused():
    with pytest.raises(ProfileError, match="must declare liquidus_c"):
        Profile.from_dict({"name": "x", "points": [[0, 25], [60, 100]]})


def test_bake_without_liquidus_is_fine():
    p = Profile.from_dict({"name": "bake", "category": CATEGORY_BAKE,
                           "points": [[0, 25], [600, 125], [7200, 125]]})
    assert p.category == CATEGORY_BAKE


def test_malformed_point_is_reported_with_its_index():
    with pytest.raises(ProfileError, match="point 1"):
        make([[0, 25], [60]])


def test_non_numeric_point_is_reported():
    with pytest.raises(ProfileError, match="non-numeric"):
        make([[0, 25], [60, "hot"]])


def test_broken_json_names_the_file(tmp_path):
    # the profile in this project's history failed exactly this way: a
    # missing comma meant it never parsed, so nothing ever used it
    bad = tmp_path / "bad.json"
    bad.write_text('{"name": "x", "points": [[0,40] [60,100]]}')
    with pytest.raises(ProfileError, match="not valid JSON"):
        Profile.load(str(bad))


def test_missing_file_is_reported_not_raised_as_oserror():
    with pytest.raises(ProfileError, match="cannot read"):
        Profile.load("/nonexistent/nope.json")


# -- interpolation ----------------------------------------------------------

def test_target_at_exact_points():
    p = make([[0, 25], [60, 100], [120, 200]])
    assert p.target_at(0) == 25
    assert p.target_at(60) == 100
    assert p.target_at(120) == 200


def test_target_interpolates_midway():
    p = make([[0, 0], [100, 100]])
    assert p.target_at(50) == pytest.approx(50)
    assert p.target_at(25) == pytest.approx(25)


def test_target_clamps_outside_the_profile():
    p = make([[0, 25], [60, 100]])
    assert p.target_at(-10) == 25
    assert p.target_at(1e6) == 100


def test_binary_search_agrees_with_linear_scan():
    pts = [[i * 10, 20 + i * 7] for i in range(40)]
    p = make(pts)
    for t in range(0, 400):
        expected = _linear_lookup(pts, t)
        assert p.target_at(t) == pytest.approx(expected)


def _linear_lookup(pts, t):
    for i in range(1, len(pts)):
        if pts[i][0] >= t:
            t0, c0 = pts[i - 1]
            t1, c1 = pts[i]
            return c0 + (c1 - c0) * (t - t0) / (t1 - t0)
    return pts[-1][1]


def test_slope_matches_the_segment():
    p = make([[0, 0], [100, 100], [200, 100]])
    assert p.slope_at(50) == pytest.approx(1.0)
    assert p.slope_at(150) == pytest.approx(0.0)
    assert p.slope_at(1000) == 0.0


# -- derived quantities -----------------------------------------------------

def test_time_above_interpolates_the_crossings():
    # crosses 50 at t=50 going up and t=150 coming down
    p = make([[0, 0], [100, 100], [200, 0]])
    assert p.time_above(50) == pytest.approx(100)


def test_time_above_a_level_never_reached_is_zero():
    p = make([[0, 0], [100, 100]])
    assert p.time_above(500) == 0


def test_time_above_counts_a_flat_top():
    p = make([[0, 0], [50, 100], [150, 100], [200, 0]])
    assert p.time_above(100) == pytest.approx(100)


def test_ramp_rates():
    p = make([[0, 0], [100, 100], [200, 50]])
    assert p.max_ramp_up == pytest.approx(1.0)
    assert p.max_ramp_down == pytest.approx(-0.5)


# -- warnings, not errors ---------------------------------------------------

def test_warns_when_peak_barely_clears_liquidus():
    # the 225 C profile this oven used to run: 8 C over a 217 C liquidus
    p = make([[0, 25], [280, 219], [300, 225], [320, 219], [360, 100]])
    w = " ".join(p.warnings())
    assert "above liquidus" in w


def test_no_peak_warning_for_a_healthy_profile():
    p = Profile.load(os.path.join(PROFILES, "sac305.json"))
    assert not any("above liquidus" in x for x in p.warnings())


def test_warns_when_the_oven_cannot_meet_the_ramp():
    p = make([[0, 25], [10, 125]])          # 10 C/s, no toaster does this
    w = " ".join(p.warnings(max_ramp_up=2.1))
    assert "this oven has managed" in w


def test_no_ramp_warning_when_the_oven_is_capable():
    p = Profile.load(os.path.join(PROFILES, "sac305.json"))
    assert not any("has managed" in x for x in p.warnings(max_ramp_up=99))


# -- stages are derived, never read from the file ---------------------------

def test_stages_are_derived_from_the_curve():
    p = Profile.load(os.path.join(PROFILES, "sac305.json"))
    names = [s[0] for s in p.stages]
    assert names == ["preheat", "soak", "reflow", "cool"]
    reflow = [s for s in p.stages if s[0] == "reflow"][0]
    # the reflow window must actually bracket the peak
    assert reflow[1] < p.peak[0] < reflow[2]


def test_a_lying_melting_point_in_the_file_cannot_move_the_stages():
    # the historical profile declared 183 C for a SAC305 curve. Stages come
    # from liquidus_c and the curve, and an unknown key is simply ignored.
    d = json.load(open(os.path.join(PROFILES, "sac305.json")))
    d["melting_point"] = 183
    d["stages"] = {"reflow": [330, 183]}
    p = Profile.from_dict(d)
    good = Profile.load(os.path.join(PROFILES, "sac305.json"))
    assert p.stages == good.stages
