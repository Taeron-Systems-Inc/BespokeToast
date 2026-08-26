# SPDX-License-Identifier: MIT
"""Screen layouts, as data.

Each builder returns a list of drawing primitives rather than touching
displayio, so layout can be tested without a board: that the abort target is
big enough to hit, that nothing runs off the edge, that the readout is where
the eye expects it. The displayio adapter walks the same list.

Primitives are tuples so they are cheap on a SAMD51:

    ("text", x, y, string, colour, font)
    ("rect", x, y, w, h, colour, filled)
    ("bitmap", x, y, path)
    ("touch", x, y, w, h, name)      -- a hit target, drawn by whatever is
                                        under it
"""

from . import theme as T


DEG = "\u00b0"


def _t(value, unit=True):
    """A temperature, written the way anyone would write it: "234 °C".

    Whole degrees -- a tenth is below what the probe means and below what
    anyone acts on -- and the unit spelled out rather than a bare degree
    sign, so a number on screen never has to be guessed at.
    """
    if value is None:
        return "-- °C" if unit else "--"
    return "%d %sC" % (round(value), DEG) if unit else "%d" % round(value)


def _rate(value):
    if value is None:
        return "-- °C/s"
    return "%+.1f %sC/s" % (value, DEG)


def splash(version):
    y = (T.SCREEN_H - 37) // 2 - 20
    return [
        ("bitmap", 0, y, T.LOGO_LARGE),
        ("text", 10, y + 60, "reflow oven", T.DIM, T.FONT_BODY),
        ("text", 10, y + 80, version, T.DIM, T.FONT_SMALL),
    ]


def self_test(results):
    """Power-on self test, shown while it runs. Not decoration: a failure
    stops here rather than at 200 C."""
    out = [("bitmap", 0, 8, T.LOGO_LARGE)]
    y = 70
    for name, ok in results:
        out.append(("text", 20, y, name, T.TEXT, T.FONT_BODY))
        out.append(("text", 250, y, "OK" if ok else "FAIL",
                    T.BRAND if ok else T.DANGER, T.FONT_BODY))
        y += 26
    return out


def home(temp_c, profile_name, ready, reason=None):
    out = [
        ("bitmap", 6, 6, T.LOGO_SMALL),
        ("text", 6, 76, _t(temp_c), T.BRAND, T.FONT_READOUT),
        ("text", 6, 132, profile_name or "no profile", T.TEXT, T.FONT_BODY),
    ]
    if ready:
        out += [("rect", 6, 176, 150, T.ABORT_TOUCH_PX, T.BRAND, False),
                ("text", 42, 206, "START", T.BRAND, T.FONT_LARGE),
                ("touch", 6, 176, 150, T.ABORT_TOUCH_PX, "start")]
    else:
        out += [("text", 6, 176, reason or "not ready", T.CAUTION, T.FONT_BODY)]
    out += [("rect", 176, 176, 138, T.MIN_TOUCH_PX, T.DIM, False),
            ("text", 198, 198, "PROFILES", T.TEXT, T.FONT_BODY),
            ("touch", 176, 176, 138, T.MIN_TOUCH_PX, "profiles")]
    return out


# Label.y in displayio is the vertical CENTRE of the text, not its top. A
# 64 px readout placed at y=4 is half off the screen; these are centres.
CHART = (6, 84, 308, 104)          # x, y, w, h

ROW_READOUT = 36
ROW_INFO = 72
ROW_FOOT = 206


def running(temp_c, target_c, elapsed_s, remaining_s, stage, tal_s,
            liquidus_c, duty, relay_on, history=None, profile_points=None,
            duration_s=None, y_max=250.0):
    """The screen that matters.

    A chart carries the run: the target curve, what the oven has actually
    done, and the liquidus as a dashed line. Two numbers say where you are;
    the shape says whether it is going right, which is what an operator is
    really watching for.

    Abort sits top right, clear of everything else, because it is the one
    control that gets pressed in a hurry. The four-stage strip is gone -- the
    chart shows progress better than a row of words, so only the current
    stage is named.
    """
    delta = None if (temp_c is None or target_c is None) else temp_c - target_c
    out = [
        ("text", 6, ROW_READOUT, _t(temp_c), T.BRAND, T.FONT_READOUT),
        ("rect", 206, 6, 108, T.ABORT_TOUCH_PX, T.DANGER, False),
        ("text", 232, 36, "ABORT", T.DANGER, T.FONT_LARGE),
        ("touch", 206, 6, 108, T.ABORT_TOUCH_PX, "abort"),
        ("text", 6, ROW_INFO, _t(delta) + " off",
         T.delta_colour(delta), T.FONT_BODY),
        ("text", 108, ROW_INFO, (stage or "").upper(), T.BRAND, T.FONT_BODY),
        ("text", 196, ROW_INFO, "target " + _t(target_c), T.TEXT, T.FONT_BODY),
    ]

    cx, cy, cw, ch = CHART
    series = []
    if profile_points and duration_s:
        series.append((T.DIM, list(profile_points)))
    if history:
        series.append((T.BRAND, list(history)))
    out.append(("plot", cx, cy, cw, ch,
                float(duration_s or 1.0), 0.0, float(y_max),
                series, liquidus_c))

    out += [
        ("text", 6, ROW_FOOT, "%02d:%02d" % (int(elapsed_s) // 60,
                                             int(elapsed_s) % 60),
         T.TEXT, T.FONT_BODY),
        ("text", 76, ROW_FOOT, "-%02d:%02d" % (int(max(0, remaining_s)) // 60,
                                               int(max(0, remaining_s)) % 60),
         T.DIM, T.FONT_BODY),
        ("text", 158, ROW_FOOT, "HEAT ON" if relay_on else "heat off",
         T.BRAND if relay_on else T.DIM, T.FONT_BODY),
    ]
    if tal_s is not None and tal_s > 0:
        out.append(("text", 248, ROW_FOOT, "%ds liq" % int(tal_s),
                    T.CAUTION if tal_s > 130 else T.DANGER, T.FONT_BODY))
    return out


def open_the_door(temp_c, cooling_rate=None, target_rate=None):
    """The door prompt.

    The rate is shown because it is the one number that tells you the door is
    actually doing something: this oven cools at about -0.7 C/s shut and
    around -5 to -7 C/s open.
    """
    out = [
        ("text", 6, 28, "OPEN", T.COOL, T.FONT_LARGE),
        ("text", 6, 60, "THE DOOR", T.COOL, T.FONT_LARGE),
        ("text", 6, 130, _t(temp_c), T.TEXT, T.FONT_READOUT),
        ("text", 196, 120, _rate(cooling_rate), T.TEXT, T.FONT_LARGE),
        ("text", 196, 148, "cooling", T.DIM, T.FONT_BODY),
    ]
    if cooling_rate is not None and cooling_rate > -1.5:
        out.append(("text", 6, 196, "still shut? open it to cool faster",
                    T.CAUTION, T.FONT_BODY))
    return out


def fault(message):
    return [
        ("rect", 0, 0, T.SCREEN_W, T.SCREEN_H, T.DANGER, False),
        ("text", 6, 40, "FAULT", T.DANGER, T.FONT_LARGE),
        ("text", 6, 110, message[:38], T.TEXT, T.FONT_BODY),
        ("text", 6, 134, message[38:76], T.TEXT, T.FONT_BODY),
        ("text", 6, 168, "heat is off and stays off until acknowledged",
         T.DIM, T.FONT_SMALL),
        ("rect", 6, 190, 200, T.MIN_TOUCH_PX, T.DANGER, False),
        ("text", 30, 208, "ACKNOWLEDGE", T.DANGER, T.FONT_BODY),
        ("touch", 6, 190, 200, T.MIN_TOUCH_PX, "acknowledge"),
    ]


def report(checks, peak_c, tal_s):
    out = [("text", 6, 16, "RUN REPORT", T.TEXT, T.FONT_LARGE)]
    y = 48
    for name, _value, ok, text in checks:
        out.append(("text", 6, y, name[:22], T.TEXT, T.FONT_SMALL))
        # 20 characters cut "(want 225-245)" down to "(want 225-24", which
        # read as a typo rather than as a limit.
        out.append(("text", 150, y, text[:30],
                    T.BRAND if ok else T.DANGER, T.FONT_SMALL))
        y += 22
    out.append(("rect", 6, 186, 140, T.MIN_TOUCH_PX, T.BRAND, False))
    out.append(("text", 46, 208, "DONE", T.BRAND, T.FONT_BODY))
    out.append(("touch", 6, 186, 140, T.MIN_TOUCH_PX, "done"))
    return out


def hit(commands, x, y):
    """Which touch target, if any, is at (x, y). Last match wins so later
    elements sit on top."""
    found = None
    for c in commands:
        if c[0] == "touch":
            _, tx, ty, tw, th, name = c
            if tx <= x < tx + tw and ty <= y < ty + th:
                found = name
    return found
