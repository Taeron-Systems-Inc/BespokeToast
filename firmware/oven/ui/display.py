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
        if kind == "plot":
            return self._plot(cmd)
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

    def _plot(self, cmd):
        """Draw the chart into a small indexed bitmap.

        One bitmap rather than a Group of Line shapes: a run is hundreds of
        segments, and hundreds of displayio objects would cost far more RAM
        and redraw time than 308x116 at 4 bits per pixel.
        """
        _, x, y, w, h, x_max, y_min, y_max, series, liquidus = cmd
        bitmap = displayio.Bitmap(w, h, 4)
        palette = displayio.Palette(4)
        palette[0] = T.BG
        palette[1] = T.DIM
        palette[2] = T.BRAND
        palette[3] = T.DANGER
        palette.make_transparent(0)

        def sx(v):
            if x_max <= 0:
                return 0
            return int(max(0, min(w - 1, v / x_max * (w - 1))))

        def sy(v):
            span = y_max - y_min
            if span <= 0:
                return h - 1
            return int(max(0, min(h - 1, (h - 1) - (v - y_min) / span * (h - 1))))

        def line(x0, y0, x1, y1, idx):
            dx = abs(x1 - x0)
            dy = -abs(y1 - y0)
            sxs = 1 if x0 < x1 else -1
            sys_ = 1 if y0 < y1 else -1
            err = dx + dy
            while True:
                if 0 <= x0 < w and 0 <= y0 < h:
                    bitmap[x0, y0] = idx
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x0 += sxs
                if e2 <= dx:
                    err += dx
                    y0 += sys_

        if liquidus is not None:
            ly = sy(liquidus)
            for px in range(0, w, 6):          # dashed
                for d in range(3):
                    if px + d < w:
                        bitmap[px + d, ly] = 3

        for colour, points in series:
            idx = 2 if colour == T.BRAND else 1
            prev = None
            for t, v in points:
                cur = (sx(t), sy(v))
                if prev is not None:
                    line(prev[0], prev[1], cur[0], cur[1], idx)
                prev = cur

        return displayio.TileGrid(bitmap, pixel_shader=palette, x=x, y=y)
