# SPDX-License-Identifier: MIT
"""Starting a run on an oven that is already warm.

The oven is asked to work from a warm start -- 35 C was named specifically.
Entering the profile where the oven already is, rather than at t=0, avoids
opening the run with the target below the oven and the heater off.

For the record: this is not repairing an observed failure. Two back-to-back
SAC305 runs from about 50 C both met their J-STD windows without it, at
236.7 C / 103 s and 236.9 C / 100 s. An earlier version of this file claimed
the second run failed; that reading came from a run still in progress.
"""

import os

import pytest

from oven.profile import Profile

PROFILES = os.path.join(os.path.dirname(__file__), "..", "firmware", "profiles")


@pytest.fixture
def sac305():
    return Profile.load(os.path.join(PROFILES, "ts391snl.json"))


def test_a_cold_oven_starts_at_the_beginning(sac305):
    assert sac305.entry_time_for(20.0) == 0.0
    assert sac305.entry_time_for(sac305.points[0][1]) == 0.0


def test_a_missing_reading_starts_at_the_beginning(sac305):
    assert sac305.entry_time_for(None) == 0.0


def test_a_warm_oven_skips_the_ramp_it_has_already_done(sac305):
    """35 C was the case asked for by name."""
    entry = sac305.entry_time_for(35.0)
    assert entry > 0.0
    assert sac305.target_at(entry) == pytest.approx(35.0, abs=1.0)


def test_the_entry_point_matches_the_oven_temperature(sac305):
    for temp in (30.0, 50.0, 90.0, 140.0, 180.0):
        entry = sac305.entry_time_for(temp)
        assert sac305.target_at(entry) == pytest.approx(temp, abs=1.5), (
            "entering at %.0f s for %.0f C lands on %.1f C"
            % (entry, temp, sac305.target_at(entry)))


def test_it_never_matches_on_the_cooling_side(sac305):
    """The same temperature occurs twice. Picking the second skips the peak.

    150 C appears on the way up and again on the way down; entering on the
    descent would run only the tail of the profile.
    """
    peak_t = sac305.peak[0]
    for temp in (150.0, 200.0, 217.0):
        assert sac305.entry_time_for(temp) <= peak_t


def test_the_skip_is_capped_so_a_hot_oven_cannot_run_a_stub(sac305):
    """An oven still at 200 C from the last run is not 'a little warm'."""
    capped = sac305.entry_time_for(200.0, max_skip_fraction=0.5)
    assert capped <= sac305.duration * 0.5 + 0.001


def test_entering_warm_leaves_enough_profile_to_be_worth_running(sac305):
    """The case that failed: 60 C, roughly where the oven sat between runs."""
    entry = sac305.entry_time_for(60.0)
    remaining = sac305.duration - entry
    assert remaining > sac305.duration * 0.5, (
        "entering at %.0f s leaves only %.0f s of a %.0f s profile"
        % (entry, remaining, sac305.duration))


@pytest.mark.parametrize("name", [
    n for n in sorted(os.listdir(PROFILES)) if n.endswith(".json")])
def test_every_profile_has_a_sane_entry_curve(name):
    p = Profile.load(os.path.join(PROFILES, name))
    previous = -1.0
    for temp in range(20, int(p.peak[1]), 5):
        entry = p.entry_time_for(float(temp))
        assert entry >= previous, (
            "%s: entry time went backwards at %d C" % (p.name, temp))
        assert 0.0 <= entry <= p.duration
        previous = entry
