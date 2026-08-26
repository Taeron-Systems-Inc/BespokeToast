# SPDX-License-Identifier: MIT
"""displayio adapter.

Walks the primitives from layout.py and puts them on the screen. This is the
only part of the interface that needs a board, which is why the layouts
themselves are data: everything about where things go, how big the targets
are and what colour they turn is decided and tested elsewhere.

Fonts are cached on first use. Loading a PCF is slow enough that doing it
inside a redraw would show.
"""

import displayio
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label
from adafruit_display_shapes.rect import Rect

from . import theme as T

_fonts = {}


def _font(path):
    if path not in _fonts:
        try:
            _fonts[path] = bitmap_font.load_font(path)
        except Exception:
            _fonts[path] = terminalio.FONT      # keep going without the nice type
    return _fonts[path]


class Display(object):
    def __init__(self, board_display):
        self.display = board_display
        self.group = displayio.Group()
        self._set_root(self.group)
        self._current = None

    def _set_root(self, group):
        # display.show() was removed in CircuitPython 9.
        try:
            self.display.root_group = group
        except AttributeError:
            self.display.show(group)

    def render(self, commands):
        """Replace the screen with *commands*. Cheap enough at 4 Hz; the
        control loop is not waiting on it either way."""
        if commands == self._current:
            return
        self._current = commands
        group = displayio.Group()
        for cmd in commands:
            try:
                item = self._build(cmd)
            except Exception as e:
                # A single unrenderable element -- a glyph missing from a
                # subsetted font, say -- must not take the display down. It
                # took down the cooldown screen, and would have taken down
                # the fault screen, which is the one that has to work.
                print("# render failed for %r: %r" % (cmd[:1], e))
                item = None
            if item is not None:
                group.append(item)
        self.group = group
        self._set_root(group)

    def _build(self, cmd):
        kind = cmd[0]
        if kind == "text":
            _, x, y, text, colour, font = cmd
            label = bitmap_label.Label(_font(font), text=str(text),
                                       color=colour)
            label.x = x
            label.y = y
            return label
        if kind == "rect":
            _, x, y, w, h, colour, filled = cmd
            if filled:
                return Rect(x, y, max(1, w), max(1, h), fill=colour)
            return Rect(x, y, max(1, w), max(1, h), outline=colour)
        if kind == "bitmap":
            _, x, y, path = cmd
            try:
                bmp = displayio.OnDiskBitmap(path)
                pal = bmp.pixel_shader
                try:
                    pal.make_transparent(0)
                except Exception:
                    pass
                grid = displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)
                return grid
            except Exception:
                return None
        return None            # "touch" is a hit target, nothing to draw
