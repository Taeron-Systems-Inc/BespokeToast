# SPDX-License-Identifier: MIT
"""Draw text the fonts cannot render, and survive it. No heat.

A character with no glyph does not fall back inside adafruit_display_text:
get_glyph returns None and the layout maths raises TypeError, killing the
screen. That shipped twice -- the word OPEN in the digits-only readout font,
and an empty string in a blanked field -- and both were fixed at the
callsite, which only covers text this firmware writes. Profile names come
out of JSON files anyone can add.

This puts genuinely unrenderable text through the real display and checks
that something appears instead of an exception.

Never imports oven.hardware: the relay pin is not claimed and no heat is
possible.
"""

import gc

import board

from oven.ui import layout as L
from oven.ui import theme as T
from oven.ui.display import Display, preload, renderable, _font

HOSTILE = (
    ("em dash and registered", "Sn42Bi58 — low‑temp ®"),
    ("cyrillic", "Профиль"),
    ("cjk", "鄴炉"),
    ("emoji", "reflow \U0001f525"),
    ("empty", ""),
    ("letters in the digits font", "OPEN"),
)


def main():
    display = Display(board.DISPLAY)
    preload((T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL))
    display.reserve_chart(L.CHART[2], L.CHART[3])
    gc.collect()
    print("GLYPH begin free=%d" % gc.mem_free())

    bad = 0

    # The substitution itself, against the real faces.
    for label, text in HOSTILE:
        for path in (T.FONT_BODY, T.FONT_READOUT):
            try:
                out = renderable(text, _font(path))
            except Exception as e:
                print("GLYPH %-26s renderable() raised: %r" % (label, e))
                bad += 1
                continue
            if len(out) != len(text):
                print("GLYPH %-26s changed length %d -> %d"
                      % (label, len(text), len(out)))
                bad += 1

    # And the whole screen, drawn for real.
    for label, text in HOSTILE:
        try:
            display.render(L.home(25.0, text, True, None))
            display.render(L.fault("thermocouple fault: %s" % text))
        except Exception as e:
            print("GLYPH %-26s SCREEN RAISED %r" % (label, e))
            bad += 1
            continue
        print("GLYPH %-26s ok -> %r" % (label,
                                        renderable(text, _font(T.FONT_BODY))))

    # A name in the digits-only readout font is the case that shipped.
    try:
        out = renderable("OPEN", _font(T.FONT_READOUT))
        print("GLYPH readout font 'OPEN' -> %r" % out)
        if "O" in out:
            print("GLYPH !! the readout font claims to have letters")
            bad += 1
    except Exception as e:
        print("GLYPH readout substitution raised %r" % e)
        bad += 1

    gc.collect()
    print("GLYPH end problems=%d free=%d" % (bad, gc.mem_free()))
    print("GLYPH done")


main()
