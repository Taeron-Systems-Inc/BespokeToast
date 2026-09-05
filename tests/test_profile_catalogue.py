# SPDX-License-Identifier: MIT
"""Listing profiles must not mean holding them.

Measured on the device, the ten shipped profiles cost 24 kB resident out of
roughly 180 kB, and exactly one of them is ever in use. That is more than
the whole WiFi stack needs to exist, spent on nine profiles nobody picked --
and the firmware was already close enough to the edge that a running screen
failed to build with 7 kB free.
"""

import os

import pytest

from oven.profile import Profile, ProfileRef, scan

PROFILES = os.path.join(os.path.dirname(__file__), "..", "firmware", "profiles")


def test_scan_finds_every_shipped_profile():
    refs = scan(PROFILES)
    files = [n for n in os.listdir(PROFILES) if n.endswith(".json")]
    assert len(refs) == len(files)
    assert all(isinstance(r, ProfileRef) for r in refs)


def test_a_ref_carries_what_the_picker_needs_and_no_points():
    refs = scan(PROFILES)
    for ref in refs:
        assert ref.name and isinstance(ref.name, str)
        assert ref.category
        assert not hasattr(ref, "points"), (
            "a ref holds points, which is the memory this was meant to save")


def test_exactly_one_profile_declares_itself_the_default():
    refs = scan(PROFILES)
    defaults = [r for r in refs if r.is_default]
    assert len(defaults) == 1, (
        "expected one default, found %s" % [r.name for r in defaults])
    assert defaults[0].name == "TS391SNL"


def test_loading_a_ref_gives_the_whole_profile():
    ref = [r for r in scan(PROFILES) if r.is_default][0]
    profile = ref.load()
    assert isinstance(profile, Profile)
    assert profile.name == ref.name
    assert profile.points, "the loaded profile must have its points"
    assert profile.is_default == ref.is_default


def test_a_broken_profile_is_reported_and_skipped_not_fatal(tmp_path):
    """One bad file must not take the whole picker down.

    A profile that quietly fails to appear is worse than one that refuses
    loudly, so the warning is checked too.
    """
    good = tmp_path / "good.json"
    good.write_text('{"name": "Good", "category": "reflow", '
                    '"liquidus_c": 217, "points": [[0,25],[60,150],'
                    '[120,240],[180,150]]}')
    (tmp_path / "broken.json").write_text("{not json")
    warnings = []
    refs = scan(str(tmp_path), on_warning=warnings.append)
    assert [r.name for r in refs] == ["Good"]
    assert len(warnings) == 1
    assert "broken.json" in warnings[0]


def test_a_missing_directory_is_reported_not_raised():
    warnings = []
    refs = scan("/no/such/place", on_warning=warnings.append)
    assert refs == []
    assert len(warnings) == 1


def test_scan_validates_now_rather_than_at_selection_time():
    """A profile that cannot load must be caught at boot.

    Discovering it when someone presses START, with a board in the oven, is
    the wrong time.
    """
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "bad.json"), "w") as f:
            json.dump({"name": "Backwards", "category": "reflow",
                       "liquidus_c": 217,
                       "points": [[60, 150], [0, 25]]}, f)
        warnings = []
        refs = scan(d, on_warning=warnings.append)
        assert refs == [], "an invalid profile was listed as selectable"
        assert warnings


def test_the_diagnostic_profile_is_not_offered_to_whoever_is_choosing():
    """It melts nothing and exists to exercise the firmware. In the cycle
    it is a profile someone steps past looking for their paste, and one
    they could start by mistake on a real assembly."""
    from oven.profile import for_operators
    refs = scan(PROFILES)
    assert any(r.diagnostic for r in refs), "the fixture itself is missing"
    offered = for_operators(refs)
    assert offered, "everything was filtered out"
    assert not any(r.diagnostic for r in offered)
    assert "DIAGNOSTIC fast" not in [r.name for r in offered]


def test_every_shipped_profile_is_named_for_something_you_can_pick_up():
    """One profile per paste, named the way the syringe is labelled. The
    qualifiers went because they only existed to tell two curves for one
    paste apart, and there are no longer two."""
    names = sorted(r.name for r in scan(PROFILES))
    assert names == ["Bake 125 °C", "DIAGNOSTIC fast", "NC191LTA10",
                     "TS391LT", "TS391SNL"], names
    for n in names:
        assert "this oven" not in n and "datasheet" not in n
