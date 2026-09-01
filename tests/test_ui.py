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
def test_text_does_not_run_off_the_right_edge(name):
    for cmd in SCREENS[name]():
        if cmd[0] != "text":
            continue
        _, x, _, text, _, font = cmd
        end = x + _width(text, font)
        assert end <= T.SCREEN_W, \
            "%s: %r ends at %d, past the %d px edge" % (name, text, end, T.SCREEN_W)


@pytest.mark.parametrize("name", sorted(SCREENS))
def test_touch_targets_are_big_enough_for_a_fingertip(name):
    for cmd in SCREENS[name]():
        if cmd[0] == "touch":
            _, _, _, w, h, target = cmd
            assert w >= T.MIN_TOUCH_PX and h >= T.MIN_TOUCH_PX, \
                "%s: target %r is %dx%d, too small for resistive touch" % (
                    name, target, w, h)


def test_abort_is_generous_and_in_a_corner():
    """Comfortably hittable and hard against a corner, because it is the one
    control pressed in a hurry. It moved from bottom-right to top-right when
    the chart took the middle of the screen, and was trimmed once it turned
    out to be larger than it needed to be."""
    cmds = SCREENS["running"]()
    abort = [c for c in cmds if c[0] == "touch" and c[5] == "abort"]
    assert abort, "the run screen must always offer abort"
    _, x, y, w, h, _ = abort[0]
    assert h >= T.ABORT_TOUCH_PX
    assert w >= T.ABORT_TOUCH_PX
    assert x + w >= T.SCREEN_W - 12, "abort must hug the right edge"
    assert y <= 20 or y + h >= T.SCREEN_H - 20, "and the top or bottom"
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

def _metrics():
    """Real per-glyph advance widths, taken from the BDF the fonts were built
    from. Estimating a single width per font is how the stage strip ended up
    drawn through the target reading."""
    import json
    root = os.path.join(os.path.dirname(__file__), "..", "firmware")
    return json.load(open(root + "/assets/fonts/metrics.json"))


def _width(text, font):
    m = _metrics().get(font)
    if m is None:
        return len(str(text)) * 9
    widths = m["widths"]
    return sum(widths.get(str(ord(c)), m["max_width"]) for c in str(text))


def _rows(cmds):
    rows = {}
    for c in cmds:
        if c[0] == "text":
            _, x, y, text, _, font = c
            rows.setdefault(y, []).append((x, x + _width(text, font), text))
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


@pytest.mark.parametrize("name", sorted(SCREENS))
def test_button_labels_stay_inside_their_boxes(name):
    """A label that overflows its outline reads as a rendering fault even
    when it is technically on screen."""
    cmds = SCREENS[name]()
    boxes = [(c[1], c[2], c[3], c[4]) for c in cmds if c[0] == "rect"
             and not c[6]]
    for c in cmds:
        if c[0] != "text":
            continue
        _, x, y, text, _, font = c
        end = x + _width(text, font)
        for bx, by, bw, bh in boxes:
            if bx <= x <= bx + bw and by <= y <= by + bh:
                assert end <= bx + bw + 1, \
                    "%s: %r overflows its box by %d px" % (
                        name, text, end - (bx + bw))


def test_the_run_screen_keeps_a_constant_shape():
    """Adding or removing an element forces the renderer to rebuild every
    object at once, and that burst is what fails on a fragmented heap. The
    first render failure of a run landed exactly as the oven crossed liquidus
    and the time-above-liquidus readout appeared, so elements are now always
    emitted and blanked instead."""
    def shape(cmds):
        return tuple((c[0], c[5] if c[0] == "text" else None) for c in cmds)
    variants = [
        L.running(25.0, 25.0, 0, 488, "preheat", 0, 217, 0.0, False),
        L.running(150.0, 152.0, 200, 288, "soak", 0, 217, 0.6, True),
        L.running(230.0, 232.0, 300, 188, "reflow", 45, 217, 0.4, True),
        L.running(220.0, 210.0, 400, 88, "cool", 140, 217, 0.0, False),
        L.running(None, None, 0, 0, None, None, 217, None, False),
    ]
    shapes = {shape(v) for v in variants}
    assert len(shapes) == 1, "the run screen changes shape between states"


def test_the_cooldown_screen_keeps_a_constant_shape():
    def shape(cmds):
        return tuple((c[0], c[5] if c[0] == "text" else None) for c in cmds)
    assert shape(L.open_the_door(200.0, -5.0)) == shape(L.open_the_door(80.0, -0.4))
    assert shape(L.open_the_door(200.0, None)) == shape(L.open_the_door(80.0, -0.4))


def test_every_string_a_run_can_produce_is_covered_by_its_font():
    """The screen-level test checks one sample of each screen. This walks the
    values a real run actually passes through -- negative deltas, blanked
    fields, every stage name, three-digit and two-digit temperatures -- because
    a glyph missing from a subsetted font does not fall back, it raises, and
    it will do so only on the frame that first needs the character."""
    cov = _coverage()
    seen = set()
    stages = [None, "preheat", "soak", "reflow", "cool"]
    for stage in stages:
        for temp, target in ((25.0, 25.0), (154.0, 155.8), (99.5, 101.0),
                             (236.5, 235.0), (-5.0, 0.0), (None, None)):
            for tal in (None, 0, 1, 42, 140):
                for relay in (True, False):
                    for cmd in L.running(temp, target, 300, 188, stage, tal,
                                         217, 0.5, relay):
                        if cmd[0] == "text":
                            seen.add((str(cmd[3]), cmd[5]))
    for text, font in sorted(seen):
        if font not in cov:
            continue
        missing = sorted(set(text) - set(cov[font]))
        assert not missing, "%r needs %r, absent from %s" % (
            text, "".join(missing), font.rsplit("/", 1)[-1])


def test_no_screen_ever_emits_an_empty_string():
    """adafruit_display_text raises TypeError out of _place_text on an empty
    string -- the same signature a missing glyph produces, which made it look
    like a font problem. Blank fields use a space.

    The first version of this test checked a couple of hand-picked variants
    and missed stage=None, which is what a run passes through before its
    first stage is known. It now sweeps the same space the glyph test does.
    """
    offenders = []
    for stage in (None, "", "preheat", "soak", "reflow", "cool"):
        for tal in (None, 0, 42):
            for temp, target in ((None, None), (25.0, 25.0), (230.0, 232.0)):
                for cmd in L.running(temp, target, 100, 300, stage, tal,
                                     217, 0.4, True):
                    if cmd[0] == "text" and str(cmd[3]) == "":
                        offenders.append("running(stage=%r,tal=%r)" % (stage, tal))
    for name, build in SCREENS.items():
        for cmd in build():
            if cmd[0] == "text" and str(cmd[3]) == "":
                offenders.append(name)
    for tal in (None, 0):
        for cmd in L.running(150.0, 152.0, 200, 288, "soak", tal, 217, 0.5, True):
            if cmd[0] == "text" and str(cmd[3]) == "":
                offenders.append("running(tal=%r)" % tal)
    for rate in (None, -0.4):
        for cmd in L.open_the_door(120.0, rate):
            if cmd[0] == "text" and str(cmd[3]) == "":
                offenders.append("open_the_door(rate=%r)" % rate)
    assert not offenders, "empty strings on: %s" % sorted(set(offenders))


def test_the_live_readout_is_not_the_largest_face():
    """The live readout stays at 48 px; 64 px is for the splash only.

    Glyph tiles are allocations, and the heap during a run has ~22 kB free
    with no contiguous hole above ~900 bytes (measured, not estimated). The
    larger face buys nothing at that cost -- "234 °C" is 153 px wide at 48 px
    against 205 at 64, and both read across a bench."""
    assert T.FONT_READOUT.endswith("48.pcf")
    assert T.FONT_READOUT_XL.endswith("64.pcf")
    live = {c[5] for c in L.running(230.0, 232.0, 300, 188, "reflow", 45,
                                    217, 0.5, True) if c[0] == "text"}
    assert T.FONT_READOUT_XL not in live, \
        "the largest face must not appear on a screen that updates"
    for cmds in (L.open_the_door(180.0, -2.0),
                 L.fault("x"),
                 L.report([("peak", 1, True, "ok")], 1, 1)):
        assert T.FONT_READOUT_XL not in {c[5] for c in cmds if c[0] == "text"}


def test_the_error_describer_never_raises():
    """A diagnostic that can fail destroys the information it exists to
    provide. This one read cmd[5] as a font path, which is true for text
    commands and false for every other kind -- on a plot it is a float, so
    reporting an error raised AttributeError, escaped the per-element catch
    and took down the entire screen."""
    _describe = L.describe_command
    samples = [
        ("text", 1, 2, "hello", 0xFFFFFF, "/assets/fonts/B612-12s.pcf"),
        ("plot", 6, 100, 278, 82, 480.0, 0.0, 250.0, [], 217),
        ("rect", 1, 2, 3, 4, 0xFFFFFF, True),
        ("bitmap", 0, 0, "/assets/taeron-logo-320.bmp"),
        ("touch", 1, 2, 3, 4, "start"),
        ("text",), (), ("weird", None), ("text", 1, 2, 3, 4, 5.0),
    ]
    for cmd in samples:
        out = _describe(cmd)
        assert isinstance(out, str) and out


def test_no_layout_asks_for_a_large_contiguous_allocation():
    """Every rect must fit in a hole a fragmented heap can still offer.

    adafruit_display_shapes.Rect allocates width x height at one bit per
    pixel whether it is filled or an outline. Measured mid-run, the heap has
    around 22 kB free but no contiguous block above ~900 bytes, so anything
    above that will fail -- and it failed on the fault screen, whose
    full-screen border wanted 9600 bytes in one piece. 900 bytes is 7200
    pixels; this holds every layout under that.
    """
    limit_px = 7200
    offenders = []
    for name in sorted(SCREENS):
        for cmd in SCREENS[name]():
            if cmd[0] != "rect":
                continue
            _, _x, _y, w, h, _colour, _filled = cmd
            if w * h > limit_px:
                offenders.append("%s: %dx%d = %d px (%d bytes)"
                                 % (name, w, h, w * h, w * h // 8))
    assert not offenders, "oversized rects: %s" % offenders
