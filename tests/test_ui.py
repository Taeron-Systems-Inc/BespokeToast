"""Layout tests.

Screens are emitted as drawing primitives rather than pushed straight into
displayio, which makes the things that actually go wrong on a small resistive
touchscreen testable without a board: targets too small to hit, text running
off the edge, the abort button not being where a panicking hand expects it.
"""

import os

import pytest

from oven.ui import layout as L
from oven.ui import theme as T


def bounds_ok(cmd):
    kind = cmd[0]
    if kind == "text":
        _, x, y = cmd[0], cmd[1], cmd[2]
        return 0 <= x < T.SCREEN_W and 0 <= y < T.SCREEN_H
    if kind in ("rect", "touch"):
        _, x, y, w, h = cmd[0], cmd[1], cmd[2], cmd[3], cmd[4]
        return x >= 0 and y >= 0 and x + w <= T.SCREEN_W and y + h <= T.SCREEN_H
    return True


SCREENS = {
    "splash": lambda: L.splash("v2.0"),
    "home_ready": lambda: L.home(24.5, "SAC305 (this oven)", True),
    "home_hot": lambda: L.home(84.0, "SAC305 (this oven)", False, "oven too hot"),
    "running": lambda: L.running(212.4, 215.0, 300, 180, "reflow", 42,
                                 217, 0.62, True,
                                 history=[(i * 4.0, 25 + i * 2.0) for i in range(50)],
                                 profile_points=[(0, 25), (200, 180), (300, 235), (488, 150)],
                                 duration_s=488),
    "running_early": lambda: L.running(25.0, 25.0, 0, 480, "preheat", 0,
                                       217, 0.0, False),
    "door": lambda: L.open_the_door(205.0, -5.2),
    "fault": lambda: L.fault("thermocouple fault: open circuit"),
    "report": lambda: L.report([("peak", 237.0, True, "237 C (want 225-245)"),
                                ("time above liquidus", 94, True, "94 s")],
                               237.0, 94),
}


@pytest.mark.parametrize("name", sorted(SCREENS))
def test_everything_stays_on_screen(name):
    for cmd in SCREENS[name]():
        assert bounds_ok(cmd), "%s: %r runs off the display" % (name, cmd)


@pytest.mark.parametrize("name", sorted(SCREENS))
def test_touch_targets_are_big_enough_for_a_fingertip(name):
    for cmd in SCREENS[name]():
        if cmd[0] == "touch":
            _, _, _, w, h, target = cmd
            assert w >= T.MIN_TOUCH_PX and h >= T.MIN_TOUCH_PX, \
                "%s: target %r is %dx%d, too small for resistive touch" % (
                    name, target, w, h)


def test_abort_is_oversized_and_in_a_corner():
    """Bigger than any other target and hard against a corner, because it is
    the one control pressed in a hurry. It moved from bottom-right to
    top-right when the chart took the lower two thirds of the screen."""
    cmds = SCREENS["running"]()
    abort = [c for c in cmds if c[0] == "touch" and c[5] == "abort"]
    assert abort, "the run screen must always offer abort"
    _, x, y, w, h, _ = abort[0]
    assert h >= T.ABORT_TOUCH_PX
    assert w >= T.ABORT_TOUCH_PX
    assert x + w >= T.SCREEN_W - 10
    assert y <= 10 or y + h >= T.SCREEN_H - 10
    others = [c for c in cmds if c[0] == "touch" and c[5] != "abort"]
    for _, _, _, ow, oh, _ in others:
        assert w * h >= ow * oh, "abort must be the largest target"


def test_hit_testing_finds_the_target():
    cmds = SCREENS["running"]()
    abort = [c for c in cmds if c[0] == "touch" and c[5] == "abort"][0]
    _, x, y, w, h, _ = abort
    assert L.hit(cmds, x + w // 2, y + h // 2) == "abort"
    assert L.hit(cmds, 2, 2) is None


def test_the_fault_screen_cannot_be_dismissed_by_accident():
    cmds = L.fault("over temperature: 261 C reached the 260 C limit")
    targets = [c[5] for c in cmds if c[0] == "touch"]
    assert targets == ["acknowledge"], "a fault screen offers one action only"


def test_the_delta_colour_escalates():
    assert T.delta_colour(1.0) == T.BRAND
    assert T.delta_colour(5.0) == T.CAUTION
    assert T.delta_colour(30.0) == T.DANGER
    assert T.delta_colour(-30.0) == T.DANGER
    assert T.delta_colour(None) == T.DIM


def test_the_current_stage_is_named():
    """The four-stage strip is gone -- the chart shows progress better than a
    row of words -- so only the stage actually in progress is named."""
    cmds = L.running(212.0, 215.0, 300, 180, "reflow", 42, 217, 0.6, True)
    named = [c[3] for c in cmds if c[0] == "text" and c[3] == "REFLOW"]
    assert named == ["REFLOW"]
    assert not [c for c in cmds if c[0] == "text" and c[3] == "PREHEAT"]


def test_the_run_screen_plots_target_against_actual():
    cmds = SCREENS["running"]()
    plots = [c for c in cmds if c[0] == "plot"]
    assert len(plots) == 1
    _, _, _, w, h, _, _, _, series, liquidus = plots[0]
    assert w > 200 and h > 80, "the chart should dominate the screen"
    assert len(series) == 2, "both the target curve and the actual trace"
    assert liquidus == 217, "the liquidus line is the reference that matters"


def test_missing_values_render_as_dashes_not_crashes():
    for cmd in L.running(None, None, 0, 0, None, None, 217, None, False):
        assert bounds_ok(cmd)


def test_assets_referenced_by_the_theme_exist():
    root = os.path.join(os.path.dirname(__file__), "..", "firmware")
    for path in (T.FONT_READOUT, T.FONT_READOUT_XL, T.FONT_LARGE,
                 T.FONT_BODY, T.FONT_SMALL,
                 T.LOGO_LARGE, T.LOGO_SMALL):
        assert os.path.exists(root + path), "%s is referenced but not shipped" % path


def test_font_budget_stays_small():
    """A full charset at 64 px is 329 KB; subsetting is what makes this fit."""
    root = os.path.join(os.path.dirname(__file__), "..", "firmware")
    total = sum(os.path.getsize(root + p) for p in
                (T.FONT_READOUT, T.FONT_READOUT_XL, T.FONT_LARGE,
                 T.FONT_BODY, T.FONT_SMALL))
    assert total < 60000, "fonts total %d bytes" % total


# -- font coverage ----------------------------------------------------------

def _coverage():
    import json
    root = os.path.join(os.path.dirname(__file__), "..", "firmware")
    return json.load(open(root + "/assets/fonts/coverage.json"))


@pytest.mark.parametrize("name", sorted(SCREENS))
def test_every_string_uses_glyphs_its_font_actually_has(name):
    """The readout font is subsetted to digits: a full charset at 64 px costs
    329 KB to draw ten numerals. Rendering a letter in it does not fall back,
    it raises TypeError deep inside adafruit_display_text.

    This shipped. The word OPEN was drawn in the digits-only font, so the
    firmware died the moment it entered cooldown -- and the fault screen had
    the same bug, which would have crashed the one screen that must survive.
    """
    cov = _coverage()
    for cmd in SCREENS[name]():
        if cmd[0] != "text":
            continue
        _, _, _, text, _, font = cmd
        if font not in cov:
            continue
        missing = sorted(set(str(text)) - set(cov[font]))
        assert not missing, (
            "%s: %r needs %r which is not in %s"
            % (name, text, "".join(missing), font.rsplit("/", 1)[-1]))


def test_the_readout_font_is_digits_only_and_stays_that_way():
    cov = _coverage()
    readout = set(cov["/assets/fonts/B612-Bold-64.pcf"])
    assert "O" not in readout and "A" not in readout
    assert set("0123456789.") <= readout


# -- geometry ---------------------------------------------------------------

CHAR_W = {"/assets/fonts/B612-Bold-64.pcf": 38,
          "/assets/fonts/B612-Bold-48.pcf": 28,
          "/assets/fonts/B612-24s.pcf": 14,
          "/assets/fonts/B612-Bold-16s.pcf": 9,
          "/assets/fonts/B612-12s.pcf": 7}


def _rows(cmds):
    rows = {}
    for c in cmds:
        if c[0] == "text":
            _, x, y, text, _, font = c
            rows.setdefault(y, []).append((x, x + len(str(text)) * CHAR_W.get(font, 9), text))
    return rows


@pytest.mark.parametrize("name", sorted(SCREENS))
def test_text_on_the_same_row_does_not_overlap(name):
    """displayio will happily draw one label over another. The first version
    of the chart screen put the stage strip straight through the target
    reading."""
    for y, items in _rows(SCREENS[name]()).items():
        items.sort()
        for (x0, x1, t0), (x2, _, t1) in zip(items, items[1:]):
            assert x1 <= x2 + 2, \
                "%s row y=%d: %r overlaps %r" % (name, y, t0, t1)


@pytest.mark.parametrize("name", sorted(SCREENS))
def test_large_text_fits_vertically(name):
    """Label.y is the vertical centre, not the top: a 64 px readout centred
    at y=4 is half off the display."""
    heights = {"/assets/fonts/B612-Bold-64.pcf": 64,
               "/assets/fonts/B612-Bold-48.pcf": 48,
               "/assets/fonts/B612-24s.pcf": 24}
    for c in SCREENS[name]():
        if c[0] != "text":
            continue
        _, _, y, text, _, font = c
        h = heights.get(font, 16)
        assert y - h // 2 >= 0, "%s: %r starts above the screen" % (name, text)
        assert y + h // 2 <= T.SCREEN_H, "%s: %r runs off the bottom" % (name, text)


def test_temperatures_carry_their_unit():
    """Written the way anyone writes it, so a number on screen is never
    ambiguous."""
    assert L._t(234.28) == "234 °C"
    assert L._t(-3.4) == "-3 °C"
    assert L._t(None) == "-- °C"
    assert "." not in L._t(212.55)
    assert L._rate(-5.2) == "-5.2 °C/s"
    assert L._rate(None) == "-- °C/s"


def test_report_text_is_not_truncated_mid_parenthesis():
    checks = [("peak", 237.0, True, "237° (want 225-245)")]
    for cmd in L.report(checks, 237.0, 94):
        if cmd[0] == "text" and "want" in str(cmd[3]):
            assert cmd[3].count("(") == cmd[3].count(")"), \
                "%r lost its closing bracket" % cmd[3]
