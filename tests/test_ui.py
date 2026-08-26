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
                                 217, 0.62, True),
    "running_early": lambda: L.running(25.0, 25.0, 0, 480, "preheat", 0,
                                       217, 0.0, False),
    "door": lambda: L.open_the_door(205.0, -0.7),
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


def test_abort_is_oversized_and_reachable():
    cmds = SCREENS["running"]()
    abort = [c for c in cmds if c[0] == "touch" and c[5] == "abort"]
    assert abort, "the run screen must always offer abort"
    _, x, y, w, h, _ = abort[0]
    assert h >= T.ABORT_TOUCH_PX
    assert w >= T.ABORT_TOUCH_PX * 2
    assert x + w >= T.SCREEN_W - 10 and y + h >= T.SCREEN_H - 20


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


def test_the_current_stage_is_the_only_one_highlighted():
    cmds = L.running(212.0, 215.0, 300, 180, "reflow", 42, 217, 0.6, True)
    lit = [c for c in cmds if c[0] == "text" and c[4] == T.BRAND
           and c[3] in [s.upper() for s in L.STAGES]]
    assert len(lit) == 1 and lit[0][3] == "REFLOW"


def test_missing_values_render_as_dashes_not_crashes():
    for cmd in L.running(None, None, 0, 0, None, None, 217, None, False):
        assert bounds_ok(cmd)


def test_assets_referenced_by_the_theme_exist():
    root = os.path.join(os.path.dirname(__file__), "..", "firmware")
    for path in (T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL,
                 T.LOGO_LARGE, T.LOGO_SMALL):
        assert os.path.exists(root + path), "%s is referenced but not shipped" % path


def test_font_budget_stays_small():
    """A full charset at 64 px is 329 KB; subsetting is what makes this fit."""
    root = os.path.join(os.path.dirname(__file__), "..", "firmware")
    total = sum(os.path.getsize(root + p) for p in
                (T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL))
    assert total < 60000, "fonts total %d bytes" % total
