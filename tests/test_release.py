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
    assert sorted(os.listdir(images)) == ["current.uf2", "previous.uf2"]


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
