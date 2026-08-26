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


def _fmt(value, suffix="", places=0):
    if value is None:
        return "--" + suffix
    return ("%." + str(places) + "f") % value + suffix


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
        ("text", 6, 60, _fmt(temp_c, "", 1), T.BRAND, T.FONT_READOUT),
        ("text", 240, 96, "C", T.BRAND, T.FONT_LARGE),
        ("text", 6, 140, profile_name or "no profile", T.TEXT, T.FONT_BODY),
    ]
    if ready:
        out += [("rect", 6, 176, 150, T.ABORT_TOUCH_PX, T.BRAND, False),
                ("text", 40, 196, "START", T.BRAND, T.FONT_LARGE),
                ("touch", 6, 176, 150, T.ABORT_TOUCH_PX, "start")]
    else:
        out += [("text", 6, 176, reason or "not ready", T.CAUTION, T.FONT_BODY)]
    out += [("rect", 176, 176, 138, T.MIN_TOUCH_PX, T.DIM, False),
            ("text", 196, 192, "PROFILES", T.TEXT, T.FONT_BODY),
            ("touch", 176, 176, 138, T.MIN_TOUCH_PX, "profiles")]
    return out


STAGES = ("preheat", "soak", "reflow", "cool")


def running(temp_c, target_c, elapsed_s, remaining_s, stage, tal_s,
            liquidus_c, duty, relay_on):
    delta = None if (temp_c is None or target_c is None) else temp_c - target_c
    out = []
    x = 6
    for name in STAGES:
        out.append(("text", x, 6, name.upper(),
                    T.stage_colour(name, stage), T.FONT_SMALL))
        x += 78
    out += [
        ("text", 6, 30, _fmt(temp_c, "", 1), T.BRAND, T.FONT_READOUT),
        ("text", 6, 104, "target " + _fmt(target_c, " C", 0), T.TEXT, T.FONT_BODY),
        ("text", 170, 104, _fmt(delta, " C", 1), T.delta_colour(delta), T.FONT_BODY),
        ("text", 6, 128, "%02d:%02d elapsed" % (int(elapsed_s) // 60,
                                                int(elapsed_s) % 60),
         T.TEXT, T.FONT_SMALL),
        ("text", 170, 128, "%02d:%02d left" % (int(max(0, remaining_s)) // 60,
                                               int(max(0, remaining_s)) % 60),
         T.TEXT, T.FONT_SMALL),
    ]
    if tal_s is not None and tal_s > 0:
        colour = T.CAUTION if tal_s > 130 else T.DANGER
        out.append(("text", 6, 150, "above liquidus %ds" % int(tal_s),
                    colour, T.FONT_BODY))
    out += [
        ("rect", 6, 176, 120, 12, T.DIM, False),
        ("rect", 7, 177, int(118 * max(0.0, min(1.0, duty or 0.0))), 10,
         T.BRAND if relay_on else T.DIM, True),
        ("rect", 314 - T.ABORT_TOUCH_PX * 2, 240 - T.ABORT_TOUCH_PX - 6,
         T.ABORT_TOUCH_PX * 2, T.ABORT_TOUCH_PX, T.DANGER, False),
        ("text", 314 - T.ABORT_TOUCH_PX * 2 + 26, 240 - T.ABORT_TOUCH_PX + 16,
         "ABORT", T.DANGER, T.FONT_LARGE),
        ("touch", 314 - T.ABORT_TOUCH_PX * 2, 240 - T.ABORT_TOUCH_PX - 6,
         T.ABORT_TOUCH_PX * 2, T.ABORT_TOUCH_PX, "abort"),
    ]
    return out


def open_the_door(temp_c, cooling_rate):
    return [
        ("text", 6, 40, "OPEN", T.COOL, T.FONT_READOUT),
        ("text", 6, 110, "THE DOOR", T.COOL, T.FONT_LARGE),
        ("text", 6, 150, _fmt(temp_c, " C", 0), T.TEXT, T.FONT_BODY),
        ("text", 140, 150, _fmt(cooling_rate, " C/s", 2), T.TEXT, T.FONT_BODY),
        ("text", 6, 180, "cooling faster than this needs the door open",
         T.DIM, T.FONT_SMALL),
    ]


def fault(message):
    return [
        ("rect", 0, 0, T.SCREEN_W, T.SCREEN_H, T.DANGER, False),
        ("text", 6, 30, "FAULT", T.DANGER, T.FONT_READOUT),
        ("text", 6, 110, message[:38], T.TEXT, T.FONT_BODY),
        ("text", 6, 134, message[38:76], T.TEXT, T.FONT_BODY),
        ("text", 6, 168, "heat is off and stays off until acknowledged",
         T.DIM, T.FONT_SMALL),
        ("rect", 6, 190, 200, T.MIN_TOUCH_PX, T.DANGER, False),
        ("text", 30, 208, "ACKNOWLEDGE", T.DANGER, T.FONT_BODY),
        ("touch", 6, 190, 200, T.MIN_TOUCH_PX, "acknowledge"),
    ]


def report(checks, peak_c, tal_s):
    out = [("text", 6, 8, "RUN REPORT", T.TEXT, T.FONT_LARGE)]
    y = 40
    for name, _value, ok, text in checks:
        out.append(("text", 6, y, name[:22], T.TEXT, T.FONT_SMALL))
        out.append(("text", 150, y, text[:20],
                    T.BRAND if ok else T.DANGER, T.FONT_SMALL))
        y += 22
    out.append(("rect", 6, 190, 140, T.MIN_TOUCH_PX, T.BRAND, False))
    out.append(("text", 40, 208, "DONE", T.BRAND, T.FONT_BODY))
    out.append(("touch", 6, 190, 140, T.MIN_TOUCH_PX, "done"))
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
