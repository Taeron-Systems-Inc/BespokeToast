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

_METRICS = None


def _metrics():
    """Per-glyph advance widths for the shipped fonts.

    Loaded once. Centring a label by eye is what left START, PROFILES and
    ACKNOWLEDGE each sitting at a different offset inside their boxes.
    """
    global _METRICS
    if _METRICS is None:
        import json
        # "/assets/..." is where it lives on the device; the second path is
        # the same file in the source tree, so the layout tests measure with
        # the same numbers the firmware does. Falling back silently to an
        # estimate meant the tests passed while the device mis-centred every
        # button.
        for path in ("/assets/fonts/metrics.json",
                     __file__.rsplit("/", 3)[0] + "/assets/fonts/metrics.json"):
            try:
                with open(path) as f:
                    _METRICS = json.load(f)
                    break
            except Exception:
                continue
        if _METRICS is None:
            _METRICS = {}
    return _METRICS


def text_width(text, font):
    m = _metrics().get(font)
    if not m:
        return len(str(text)) * 9
    widths = m["widths"]
    return sum(widths.get(str(ord(c)), m["max_width"]) for c in str(text))


def button(x, y, w, h, label, colour, name, font=None):
    """A box with its label centred in it, and a matching touch target.

    Every button on every screen goes through here so they cannot drift apart
    in font, alignment or size.
    """
    font = font or T.FONT_BODY
    tx = x + max(0, (w - text_width(label, font)) // 2)
    return [("rect", x, y, w, h, colour, False),
            ("text", tx, y + h // 2, label, colour, font),
            ("touch", x, y, w, h, name)]


def wrap(text, font, width_px, max_lines=3):
    """Break on spaces, not mid-word.

    Slicing at a fixed character count split "exceeds" into "e" and "xceeds"
    on the fault screen, which is where legibility matters most.
    """
    words = str(text).split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if current and text_width(candidate, font) > width_px:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
        else:
            current = candidate
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines


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
        ("text", 6, 134, profile_name or "no profile", T.TEXT, T.FONT_BODY),
    ]
    if ready:
        out += button(6, 176, 150, T.ABORT_TOUCH_PX, "START", T.BRAND,
                      "start", T.FONT_LARGE)
    else:
        out += [("text", 6, 176, reason or "not ready", T.CAUTION,
                 T.FONT_BODY)]
    out += button(176, 176, 138, T.ABORT_TOUCH_PX, "PROFILES", T.TEXT,
                  "profiles", T.FONT_LARGE)
    return out


# Label.y in displayio is the vertical CENTRE of the text, not its top. A
# 64 px readout placed at y=4 is half off the screen; these are centres.
CHART = (6, 100, 308, 92)          # x, y, w, h

ROW_READOUT = 36        # 64 px type, so it occupies y = 4..68
ROW_INFO = 84           # clear of it: 16 px type occupies y = 76..92
ROW_FOOT = 208


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
    out = button(220, 12, 94, T.ABORT_TOUCH_PX, "ABORT", T.DANGER, "abort",
                 T.FONT_LARGE)
    out += [
        ("text", 6, ROW_READOUT, _t(temp_c), T.BRAND, T.FONT_READOUT),
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
        ("text", 6, 30, "OPEN", T.COOL, T.FONT_LARGE),
        ("text", 6, 62, "THE DOOR", T.COOL, T.FONT_LARGE),
        ("text", 6, 132, _t(temp_c), T.TEXT, T.FONT_READOUT),
        ("text", 6, 186, _rate(cooling_rate) + " cooling", T.TEXT,
         T.FONT_LARGE),
    ]
    if cooling_rate is not None and cooling_rate > -1.5:
        out.append(("text", 6, 218, "still shut? open it to cool faster",
                    T.CAUTION, T.FONT_BODY))
    return out


def fault(message):
    """The one screen that has to work.

    The message is wrapped on word boundaries: slicing at a fixed character
    count split "exceeds" across two lines as "e" and "xceeds", which is not
    what you want to be reading while an oven cools down.
    """
    lines = wrap(message, T.FONT_BODY, 296, max_lines=3)
    out = [
        ("rect", 0, 0, T.SCREEN_W, T.SCREEN_H, T.DANGER, False),
        ("text", 12, 34, "FAULT", T.DANGER, T.FONT_LARGE),
    ]
    y = 84
    for line in lines:
        out.append(("text", 12, y, line, T.TEXT, T.FONT_BODY))
        y += 24
    out.append(("text", 12, 160, "heat is off until acknowledged",
                T.DIM, T.FONT_BODY))
    out += button(12, 180, 200, T.ABORT_TOUCH_PX, "ACKNOWLEDGE", T.DANGER,
                  "acknowledge", T.FONT_LARGE)
    return out


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
    out += button(6, 186, 140, T.ABORT_TOUCH_PX, "DONE", T.BRAND, "done",
                  T.FONT_LARGE)
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
