# SPDX-License-Identifier: MIT
"""Text the firmware builds at runtime, checked against the fonts it has.

The existing coverage test walks a fixed set of screens, so it only ever
sees the strings those fixtures happen to contain. Two kinds of text never
appear there and both reach the screen:

  * fault messages, assembled from a supervisor detail string with measured
    numbers and units in it;
  * profile names, which come from JSON files that anyone can drop in
    /profiles.

A character with no glyph does not fall back to a placeholder. It raises
TypeError deep inside adafruit_display_text and takes the screen with it.
That shipped once already -- the word OPEN drawn in a digits-only font
killed the firmware on entering cooldown, and the fault screen carried the
same bug, so the one screen that has to survive was the one that could not.
"""

import ast
import json
import os

import pytest

from oven import safety
from oven.profile import Profile
from oven.ui import layout as L
from oven.ui import theme as T

HERE = os.path.dirname(__file__)
FIRMWARE = os.path.join(HERE, "..", "firmware")
PROFILES = os.path.join(FIRMWARE, "profiles")


def _coverage():
    with open(os.path.join(FIRMWARE, "assets", "fonts", "coverage.json")) as f:
        return json.load(f)


def _renderable(text, font, cov):
    if font not in cov:
        return []
    return sorted(set(str(text)) - set(cov[font]))


# -- fault messages ---------------------------------------------------------

def _fault_detail_formats():
    """Every format string handed to a Fault, taken from the source.

    Read out of safety.py rather than listed here, so a new fault cannot be
    added without this test seeing it.
    """
    path = os.path.join(FIRMWARE, "oven", "safety.py")
    with open(path) as f:
        tree = ast.parse(f.read())
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name not in ("_trip", "Fault"):
            continue
        for arg in node.args[1:]:
            for sub in ast.walk(arg):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    out.append(sub.value)
    return sorted(set(out))


def test_there_are_fault_formats_to_check():
    assert len(_fault_detail_formats()) >= 8, (
        "found only %d fault detail strings; the extraction has probably "
        "stopped matching" % len(_fault_detail_formats()))


@pytest.mark.parametrize("fmt", _fault_detail_formats())
def test_every_fault_detail_renders_in_the_body_font(fmt):
    """Fill each format with plausible values and check every character."""
    count = fmt.count("%")- 2 * fmt.count("%%")
    filled = fmt
    if count > 0:
        try:
            filled = fmt % tuple([260.0] * count)
        except (TypeError, ValueError):
            try:
                filled = fmt % tuple(["260.0"] * count)
            except (TypeError, ValueError):
                filled = fmt
    cov = _coverage()
    missing = _renderable(filled, T.FONT_BODY, cov)
    assert not missing, (
        "fault text %r needs %r, which %s does not have"
        % (filled, "".join(missing), T.FONT_BODY.rsplit("/", 1)[-1]))


@pytest.mark.parametrize("code", sorted(safety._FAULT_TEXT))
def test_every_fault_screen_renders(code):
    """The whole screen, not just the message: wrapping and the border too."""
    cov = _coverage()
    fault = safety.Fault(code, "260.0 °C exceeds 260.0 °C", 0.0)
    for cmd in L.fault(fault.message):
        if cmd[0] != "text":
            continue
        missing = _renderable(cmd[3], cmd[5], cov)
        assert not missing, (
            "fault %d draws %r in %s, missing %r"
            % (code, cmd[3], cmd[5].rsplit("/", 1)[-1], "".join(missing)))


# -- profile names ----------------------------------------------------------

@pytest.mark.parametrize("name", sorted(
    n for n in os.listdir(PROFILES) if n.endswith(".json")))
def test_every_shipped_profile_name_renders(name):
    cov = _coverage()
    profile = Profile.load(os.path.join(PROFILES, name))
    for screen in (L.home(25.0, profile.name, True, None),
                   L.home(25.0, profile.name, False, "oven too hot to start")):
        for cmd in screen:
            if cmd[0] != "text":
                continue
            missing = _renderable(cmd[3], cmd[5], cov)
            assert not missing, (
                "%s: %r needs %r" % (name, cmd[3], "".join(missing)))


def test_text_is_sanitised_against_the_font_before_it_reaches_a_label():
    """A name the font cannot render must not be handed to the display.

    Profile names come from JSON files anyone can drop in /profiles, and a
    character with no glyph does not fall back -- get_glyph returns None and
    the layout maths inside adafruit_display_text raises, taking the screen
    with it. Layout cannot check this: it emits font *paths*, and only the
    display holds the loaded face. So the guard lives there, and this
    asserts it is on both paths that put text into a label.

    Checked by parsing, because display.py imports board and cannot be
    imported on the host. tools/device/glyphs.py proves it actually works.
    """
    path = os.path.join(FIRMWARE, "oven", "ui", "display.py")
    with open(path) as f:
        tree = ast.parse(f.read())

    assert any(isinstance(n, ast.FunctionDef) and n.name == "renderable"
               for n in ast.walk(tree)), "display.renderable() is missing"

    guarded = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name not in ("_build", "_update"):
            continue
        calls = [getattr(c.func, "id", None) for c in ast.walk(node)
                 if isinstance(c, ast.Call)]
        if "renderable" in calls:
            guarded.append(node.name)
    assert sorted(guarded) == ["_build", "_update"], (
        "text reaches a label unsanitised in: %s"
        % sorted({"_build", "_update"} - set(guarded)))


def test_a_hostile_profile_name_is_still_reported_somewhere():
    """Substituting glyphs must not be the only trace of a bad name.

    A name that renders as "Sn42Bi58 ? low?temp ?" on the oven is confusing
    if nothing else ever mentions it, so the loader keeps the original and
    the substitution happens only at the point of drawing.
    """
    hostile = "Sn42Bi58 \u2014 low\u2011temp \u00ae"
    profile = Profile.from_dict({
        "name": hostile, "category": "reflow", "liquidus_c": 138,
        "points": [[0, 25], [60, 100], [120, 170], [180, 100]]})
    assert profile.name == hostile, (
        "the profile should keep its real name; only the screen substitutes")
