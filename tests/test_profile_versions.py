# SPDX-License-Identifier: MIT
"""Versions, archiving and deleting, from the page.

An upload never overwrites: it adds a version, and the newest version is
the one the oven runs. Archiving hides a profile from the oven's own
button without touching it. Deleting goes one version at a time, or the
whole profile, and the page will not offer either until what would be
deleted has been downloaded from it.
"""

import json
import os

import pytest

from oven import profilestore
from oven.profile import (choose, for_operators, latest, offered, scan,
                          version_filename, version_of, versions_of)
from oven.webapp import index_page, index_parts, profile_entry, route


def write(directory, filename, name, peak=165, **extra):
    body = {"name": name, "liquidus_c": 138,
            "points": [[0, 25], [120, 150], [200, peak], [260, 100]]}
    body.update(extra)
    (directory / filename).write_text(json.dumps(body))


def catalogue(tmp_path):
    return scan(str(tmp_path), on_warning=lambda m: None)


@pytest.fixture
def shelf(tmp_path):
    write(tmp_path, "ts391lt.json", "TS391LT", peak=165, default=True)
    write(tmp_path, "ts391lt.v2.json", "TS391LT", peak=170)
    write(tmp_path, "bake.json", "Bake")
    write(tmp_path, "diag.json", "DIAG", diagnostic=True)
    return tmp_path


# -- what a version is -----------------------------------------------------

@pytest.mark.parametrize("filename,expect", [
    ("ts391lt.json", ("ts391lt", 1)),
    ("ts391lt.v2.json", ("ts391lt", 2)),
    ("ts391lt.v12.json", ("ts391lt", 12)),
    ("bake-msl-125c.json", ("bake-msl-125c", 1)),
    # Not a version suffix: a letter after the v, or nothing before it.
    ("a.vx.json", ("a.vx", 1)),
    (".v2.json", (".v2", 1)),
])
def test_a_version_is_read_from_the_filename(filename, expect):
    assert version_of(filename) == expect


def test_version_filenames_round_trip():
    for v in (1, 2, 9, 10):
        assert version_of(version_filename("x", v)) == ("x", v)
    assert version_filename("x", 1) == "x.json", (
        "version 1 keeps the name every shipped profile already has")


def test_the_newest_version_is_what_the_oven_offers(shelf):
    refs = catalogue(shelf)
    assert len(refs) == 4, "every version is catalogued"
    names = [(r.name, r.version) for r in for_operators(refs)]
    assert names == [("Bake", 1), ("TS391LT", 2)]


def test_an_archived_profile_is_not_offered_at_the_oven(shelf):
    refs = catalogue(shelf)
    assert profilestore.set_archived(str(shelf), refs, "bake", True) is None
    refs = catalogue(shelf)
    assert [r.name for r in for_operators(refs)] == ["TS391LT"]
    assert [r.name for r in offered(refs)] == ["TS391LT"]
    # Still catalogued, so the page can list it and unarchive it.
    assert [r.archived for r in refs if r.stem == "bake"] == [True]


def test_archiving_covers_every_version(shelf):
    refs = catalogue(shelf)
    profilestore.set_archived(str(shelf), refs, "ts391lt", True)
    refs = catalogue(shelf)
    assert all(r.archived for r in versions_of(refs, "ts391lt"))
    assert [r.name for r in for_operators(refs)] == ["Bake"]


def test_unarchiving_brings_it_back_and_twice_is_harmless(shelf):
    d = str(shelf)
    profilestore.set_archived(d, catalogue(shelf), "bake", True)
    assert profilestore.set_archived(d, catalogue(shelf), "bake", False) is None
    assert profilestore.set_archived(d, catalogue(shelf), "bake", False) is None
    assert "Bake" in [r.name for r in for_operators(catalogue(shelf))]


def test_archiving_does_not_touch_the_profile_itself(shelf):
    before = (shelf / "bake.json").read_bytes()
    profilestore.set_archived(str(shelf), catalogue(shelf), "bake", True)
    assert (shelf / "bake.json").read_bytes() == before


def test_a_board_with_only_diagnostics_still_offers_them_but_never_archived(
        tmp_path):
    write(tmp_path, "diag.json", "DIAG", diagnostic=True)
    assert [r.name for r in offered(catalogue(tmp_path))] == ["DIAG"]
    profilestore.set_archived(str(tmp_path), catalogue(tmp_path), "diag",
                              True)
    assert offered(catalogue(tmp_path)) == []


# -- what stays selected ---------------------------------------------------

def test_a_new_version_of_the_selected_profile_is_what_runs(shelf):
    refs = catalogue(shelf)
    selected = choose(refs)
    assert (selected.name, selected.version) == ("TS391LT", 2)
    write(shelf, "ts391lt.v3.json", "TS391LT", peak=168)
    now = choose(catalogue(shelf), selected)
    assert (now.name, now.version) == ("TS391LT", 3)


def test_the_default_is_chosen_at_any_version(shelf):
    """default is set in v1 here and absent from v2, which is what an
    upload of the default profile looks like: "default" is stripped from
    anything that arrives over the network. The profile stays the default,
    at its newest version."""
    refs = catalogue(shelf)
    got = choose(refs)
    assert (got.name, got.version) == ("TS391LT", 2)


def test_archiving_the_selected_profile_moves_the_selection(shelf):
    refs = catalogue(shelf)
    selected = choose(refs)
    profilestore.set_archived(str(shelf), refs, selected.stem, True)
    now = choose(catalogue(shelf), selected)
    assert now is not None and now.name == "Bake"


def test_archiving_every_real_profile_does_not_surface_diagnostic(shelf):
    d = str(shelf)
    profilestore.set_archived(d, catalogue(shelf), "ts391lt", True)
    profilestore.set_archived(d, catalogue(shelf), "bake", True)
    assert offered(catalogue(shelf)) == []
    assert choose(catalogue(shelf)) is None


def test_deleting_everything_offered_leaves_nothing_selected(shelf):
    d = str(shelf)
    profilestore.delete_profile(d, catalogue(shelf), "ts391lt")
    profilestore.delete_profile(d, catalogue(shelf), "bake")
    # DIAG is not offered while anything else is; with nothing else it is.
    assert choose(catalogue(shelf)).name == "DIAG"
    profilestore.set_archived(d, catalogue(shelf), "diag", True)
    assert choose(catalogue(shelf)) is None


# -- uploading adds a version ----------------------------------------------

def test_an_upload_with_a_known_name_is_the_next_version(shelf):
    refs = catalogue(shelf)
    assert profilestore.new_version_filename(refs, "TS391LT",
                                             "ts391lt.json") == (
        "ts391lt.v3.json", 3)


def test_the_name_finds_the_profile_even_when_the_slug_would_not(tmp_path):
    """Shipped files are not named by slug: Bake 125 C lives in
    bake-msl-125c.json. Uploading Bake 125 C has to add a version to that
    profile, not start a second one beside it with the same name."""
    write(tmp_path, "bake-msl-125c.json", "Bake 125 C")
    refs = catalogue(tmp_path)
    assert profilestore.new_version_filename(refs, "bake 125 c",
                                             "bake-125-c.json") == (
        "bake-msl-125c.v2.json", 2)


def test_a_new_name_starts_at_version_one(shelf):
    refs = catalogue(shelf)
    assert profilestore.new_version_filename(refs, "Brand new",
                                             "brand-new.json") == (
        "brand-new.json", 1)


def test_a_name_that_slugs_onto_a_profile_joins_it(shelf):
    """Two names that differ only in punctuation have always been the same
    file. They are now the same profile, as a new version."""
    refs = catalogue(shelf)
    assert profilestore.new_version_filename(refs, "TS391-LT!",
                                             "ts391-lt.json")[1] == 1
    assert profilestore.new_version_filename(refs, "Bake!",
                                             "bake.json") == ("bake.v2.json", 2)


def test_versions_count_on_past_a_deleted_one(shelf):
    d = str(shelf)
    profilestore.delete_version(d, catalogue(shelf), "ts391lt.json")
    refs = catalogue(shelf)
    assert profilestore.new_version_filename(refs, "TS391LT",
                                             "ts391lt.json")[0] == (
        "ts391lt.v3.json")


# -- deleting --------------------------------------------------------------

def test_one_version_can_be_deleted_and_the_rest_stay(shelf):
    d = str(shelf)
    assert profilestore.delete_version(d, catalogue(shelf),
                                       "ts391lt.v2.json") is None
    left = versions_of(catalogue(shelf), "ts391lt")
    assert [r.version for r in left] == [1]
    assert (shelf / "bake.json").exists()


def test_deleting_the_last_version_takes_the_archive_marker_with_it(shelf):
    d = str(shelf)
    profilestore.set_archived(d, catalogue(shelf), "bake", True)
    profilestore.delete_version(d, catalogue(shelf), "bake.json")
    assert not (shelf / "bake.archived").exists(), (
        "a marker left behind would archive the next upload of that name")


def test_a_whole_profile_can_be_deleted(shelf):
    d = str(shelf)
    profilestore.set_archived(d, catalogue(shelf), "ts391lt", True)
    assert profilestore.delete_profile(d, catalogue(shelf), "ts391lt") is None
    assert sorted(os.listdir(d)) == ["bake.json", "diag.json"]


@pytest.mark.parametrize("hostile", [
    "../wifi.json", "/wifi.json", "wifi.json", "", "ts391lt.v9.json",
    "settings.toml",
])
def test_only_what_the_catalogue_lists_can_be_deleted(shelf, hostile):
    d = str(shelf)
    before = sorted(os.listdir(d))
    refs = catalogue(shelf)
    assert profilestore.delete_version(d, refs, hostile) is not None
    assert profilestore.delete_profile(d, refs, hostile) is not None
    assert profilestore.set_archived(d, refs, hostile, True) is not None
    assert sorted(os.listdir(d)) == before


# -- downloading everything at once ----------------------------------------

def test_the_bundle_holds_every_version_byte_for_byte(shelf):
    refs = catalogue(shelf)
    text = "".join(profilestore.bundle_chunks(refs, "ts391lt", chunk=64))
    got = json.loads(text)
    assert got["profile"] == "TS391LT"
    assert [v["version"] for v in got["versions"]] == [1, 2]
    assert [v["file"] for v in got["versions"]] == ["ts391lt.json",
                                                   "ts391lt.v2.json"]
    for v in got["versions"]:
        on_flash = json.loads((shelf / v["file"]).read_text())
        assert v["profile"] == on_flash


def test_the_bundle_is_streamed_in_small_pieces(shelf):
    refs = catalogue(shelf)
    pieces = list(profilestore.bundle_chunks(refs, "ts391lt", chunk=512))
    assert max(len(p) for p in pieces) <= 512


# -- the page --------------------------------------------------------------

@pytest.mark.parametrize("path,kind", [
    ("/archive/bake", "archive"),
    ("/unarchive/bake", "unarchive"),
    ("/delete-version/bake.json", "delete-version"),
    ("/delete-profile/bake", "delete-profile"),
])
def test_changes_are_post_only(path, kind):
    assert route("POST", path) == (kind, path.rsplit("/", 1)[1])
    assert route("GET", path)[0] == "not-found", (
        "a prefetch or a crawler following a link must not change anything")
    assert route("HEAD", path)[0] == "not-found"


@pytest.mark.parametrize("path", [
    "/archive/", "/archive/../wifi.json", "/delete-version/a/b",
    "/delete-profile/..", "/bundles/../wifi.json", "/bundles/x",
    "/bundles/.json",
])
def test_a_change_cannot_name_something_outside_the_catalogue(path):
    assert route("POST", path)[0] in ("bad-name", "not-found")
    assert route("GET", path)[0] in ("bad-name", "not-found")


def test_the_bundle_is_a_download():
    assert route("GET", "/bundles/ts391lt.json") == ("get-bundle", "ts391lt")


ENTRIES = [
    profile_entry("TS391LT", "ts391lt", False,
                  [(1, "ts391lt.json"), (2, "ts391lt.v2.json")]),
    profile_entry("Bake", "bake", True, [(1, "bake.json")]),
]


def test_every_delete_starts_greyed_out():
    page = index_page([], ENTRIES)
    deletes = page.count("class=del")
    assert deletes == 5, "three versions and two profiles"
    assert page.count("class=del disabled") == deletes


def test_every_delete_has_a_download_that_unlocks_it():
    page = index_page([], ENTRIES)
    for f in ("ts391lt.json", "ts391lt.v2.json", "bake.json"):
        assert "<a download href='/profiles/%s' data-g=" % f in page
        assert "data-x=delete-version data-s='%s'" % f in page
    for stem in ("ts391lt", "bake"):
        assert "<a download href='/bundles/%s.json' data-g='%s'>" % (
            stem, stem) in page
        assert "data-x=delete-profile data-s='%s'" % stem in page


def test_the_newest_version_is_marked_as_the_one_that_runs():
    page = index_page([], ENTRIES)
    assert page.count("runs at the oven") == 1
    assert "v2</a> <span class=q>newest, runs at the oven" in page


def test_an_archived_profile_says_so_and_offers_to_come_back():
    page = index_page([], ENTRIES)
    assert "archived -- not offered at the oven" in page
    assert "data-x=unarchive data-s='bake'" in page
    assert "data-x=archive data-s='ts391lt'" in page


def test_a_hostile_profile_name_cannot_inject_markup_into_the_list():
    page = index_page([], [profile_entry("<img src=x onerror=y>", "x", False,
                                         [(1, "x.json")])])
    assert "<img" not in page


def test_the_managed_list_is_still_built_in_small_pieces():
    many = [profile_entry("Profile %d" % i, "p%d" % i, i % 2 == 0,
                          [(v, "p%d.v%d.json" % (i, v)) for v in range(1, 9)])
            for i in range(6)]
    parts = index_parts([], many)
    biggest = max(len(p) for p in parts)
    assert biggest < 1600, "largest piece is %d bytes" % biggest
    assert "".join(parts) == index_page([], many)


def test_the_upload_box_says_it_adds_a_version():
    page = index_page([], ENTRIES)
    assert "adds a new version" in page
    assert "replaces it" not in page
