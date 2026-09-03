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
