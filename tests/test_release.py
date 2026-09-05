# SPDX-License-Identifier: MIT
"""The build-and-flash tool's checks.

The only part worth testing without a build host is the one that prevents
the silent failure: a file on CIRCUITPY shadows the frozen copy of the same
module, and nothing reports it. The oven simply runs on a third of the
memory.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import release  # noqa: E402


def test_it_names_every_module_that_can_shadow_the_frozen_build(tmp_path,
                                                                monkeypatch):
    monkeypatch.setattr(release, "MOUNT", str(tmp_path))
    assert release.shadowing() == []
    (tmp_path / "oven").mkdir()
    assert release.shadowing() == ["oven"]
    (tmp_path / "neopixel.mpy").write_text("x")
    assert set(release.shadowing()) == {"oven", "neopixel.mpy"}


def test_the_shadow_list_covers_what_the_firmware_freezes(monkeypatch,
                                                          tmp_path):
    """It must agree with deploy.py, which enforces the same rule."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
    import deploy
    monkeypatch.setattr(release, "MOUNT", str(tmp_path))
    for name in deploy.FROZEN_IN_FIRMWARE:
        if name.endswith(".py"):
            continue          # release checks the .mpy spelling
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        if name.endswith(".mpy"):
            (tmp_path / name).write_text("x")
        else:
            (tmp_path / name).mkdir(exist_ok=True)
    found = set(release.shadowing())
    missing = {n for n in deploy.FROZEN_IN_FIRMWARE
               if not n.endswith(".py")} - found
    assert not missing, (
        "release.py would not notice these shadowing the frozen build: %s"
        % sorted(missing))


def test_quote_survives_a_hostile_path():
    assert release.quote("a b") == "'a b'"
    assert "'\\''" in release.quote("it's")


def test_the_modes_are_the_documented_ones():
    assert release.main(["release.py", "--nonsense"]) == 2


def _img(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_nothing_to_roll_back_to_until_an_image_has_been_replaced(tmp_path):
    """--rollback was in the usage text as "reflash the stock image" and did
    nothing but build and flash the current one, which is the opposite of a
    rollback. It has to be honest about having nothing, too."""
    images = str(tmp_path / "images")
    assert release.rollback_image(images) is None
    release.rotate_images(_img(tmp_path, "a.uf2", "A"), images)
    assert release.rollback_image(images) is None, (
        "the first image ever flashed has nothing behind it")


def test_the_image_being_replaced_is_what_rollback_returns_to(tmp_path):
    images = str(tmp_path / "images")
    release.rotate_images(_img(tmp_path, "a.uf2", "A"), images)
    release.rotate_images(_img(tmp_path, "b.uf2", "B"), images)
    assert open(release.rollback_image(images)).read() == "A"


def test_only_two_are_kept(tmp_path):
    """A ring of old firmware is a museum. What is wanted is the one that
    was working twenty minutes ago."""
    images = str(tmp_path / "images")
    for n in "ABC":
        release.rotate_images(_img(tmp_path, n + ".uf2", n), images)
    assert open(release.rollback_image(images)).read() == "B"
    assert sorted(n for n in os.listdir(images) if n.endswith(".uf2")) == [
        "current.uf2", "previous.uf2"]


def test_rolling_back_twice_returns_where_you_were(tmp_path):
    """Otherwise the second --rollback is a no-op that looks like it did
    something, which is worse than refusing."""
    images = str(tmp_path / "images")
    release.rotate_images(_img(tmp_path, "a.uf2", "A"), images)
    release.rotate_images(_img(tmp_path, "b.uf2", "B"), images)
    assert open(release.rollback_image(images)).read() == "A"
    release.swap_images(images)
    assert open(release.rollback_image(images)).read() == "B"


def test_swapping_with_nothing_to_swap_says_so(tmp_path):
    images = str(tmp_path / "images")
    assert release.swap_images(images) is False
    release.rotate_images(_img(tmp_path, "a.uf2", "A"), images)
    assert release.swap_images(images) is False


def test_the_staged_image_is_the_one_being_rolled_back_to(tmp_path):
    """The first version printed previous.uf2 and then swapped the two
    files, so the path in the message held the image being rolled back
    FROM by the time anyone read it. It flashed forward and looked like it
    had worked. Only flashing a real board showed it."""
    images = str(tmp_path / "images")
    release.rotate_images(_img(tmp_path, "old.uf2", "OLD"), images)
    release.rotate_images(_img(tmp_path, "new.uf2", "NEW"), images)
    staged = release.stage_rollback(images)
    assert open(staged).read() == "OLD", (
        "staged %r, which is not the image being rolled back to"
        % open(staged).read())


def test_staging_leaves_the_pair_swapped_so_a_second_rollback_returns(tmp_path):
    images = str(tmp_path / "images")
    release.rotate_images(_img(tmp_path, "old.uf2", "OLD"), images)
    release.rotate_images(_img(tmp_path, "new.uf2", "NEW"), images)
    assert open(release.stage_rollback(images)).read() == "OLD"
    assert open(release.stage_rollback(images)).read() == "NEW"


def test_staging_with_nothing_behind_you_returns_nothing(tmp_path):
    images = str(tmp_path / "images")
    assert release.stage_rollback(images) is None
    release.rotate_images(_img(tmp_path, "a.uf2", "A"), images)
    assert release.stage_rollback(images) is None


def test_rolling_back_carries_the_code_py_that_matches_the_image(tmp_path):
    """code.py is not frozen, so it does not travel with the image. Rolling
    the firmware back without it leaves code.py calling into a firmware
    that no longer has what it calls: the board boots and the page is
    dead. That is what happened on the real board."""
    images = str(tmp_path / "images")
    code = os.path.join(os.path.dirname(release.__file__), "..", "firmware",
                        "code.py")
    assert os.path.exists(code), "the archiver reads the real code.py"
    release.rotate_images(_img(tmp_path, "old.uf2", "OLD"), images)
    release.rotate_images(_img(tmp_path, "new.uf2", "NEW"), images)
    release.stage_rollback(images)
    staged_code = os.path.join(images, release.STAGED_CODE)
    assert os.path.exists(staged_code), (
        "rolled the image back and left the newer code.py in place")
