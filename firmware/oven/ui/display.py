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
        except Exception as e:
            # Keep going without the nice type, but do not do it quietly.
            print("# font %s failed to load (%r); using terminalio" % (path, e))
            _fonts[path] = terminalio.FONT
    return _fonts[path]


class Display(object):
    def __init__(self, board_display):
        self.display = board_display
        self.group = displayio.Group()
        self._set_root(self.group)
        self._current = None
        # The chart buffer is allocated once and redrawn in place. Building a
        # fresh Bitmap every frame at 4 Hz fragments the heap until a
        # contiguous block is no longer available: measured on hardware as
        # MemoryError on a 7360-byte allocation, a hundred-odd times in a
        # single run, each one a frame where the chart simply vanished.
        self._chart = None
        self._chart_key = None
        self._chart_palette = None

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
                except Exception as e:
                    print("# note %s has no transparent index (%r)"
                          % (path, e))
                grid = displayio.TileGrid(bmp, pixel_shader=pal, x=x, y=y)
                return grid
            except Exception as e:
                print("# WARNING bitmap %s failed to load (%r)" % (path, e))
                return None
        return None            # "touch" is a hit target, nothing to draw

    def _plot(self, cmd):
        """Draw the chart into a reused indexed bitmap.

        One bitmap rather than a Group of Line shapes: a run is hundreds of
        segments, and hundreds of displayio objects would cost far more RAM
        and redraw time than 308x92 at 4 bits per pixel. And one bitmap for
        the life of the program rather than one per frame, because the latter
        runs the heap out of contiguous space within a couple of minutes.
        """
        _, x, y, w, h, x_max, y_min, y_max, series, liquidus = cmd
        if self._chart_key != (w, h):
            self._chart = displayio.Bitmap(w, h, 4)
            palette = displayio.Palette(4)
            palette[0] = T.BG
            palette[1] = T.DIM
            palette[2] = T.BRAND
            # A saturated red rule straight across the chart reads as an
            # alarm rather than a reference: muted tone, sparser dash.
            palette[3] = T.DANGER
            palette.make_transparent(0)
            self._chart_palette = palette
            self._chart_key = (w, h)
        bitmap = self._chart
        palette = self._chart_palette
        bitmap.fill(0)

        def sx(v):
            if x_max <= 0:
                return 0
            return int(max(0, min(w - 1, v / x_max * (w - 1))))

        def sy(v):
            span = y_max - y_min
            if span <= 0:
                return h - 1
            return int(max(0, min(h - 1, (h - 1) - (v - y_min) / span * (h - 1))))

        def line(x0, y0, x1, y1, idx, dash=0):
            dx = abs(x1 - x0)
            dy = -abs(y1 - y0)
            sxs = 1 if x0 < x1 else -1
            sys_ = 1 if y0 < y1 else -1
            err = dx + dy
            n = 0
            while True:
                on = True if not dash else (n % (dash * 2)) < dash
                if on and 0 <= x0 < w and 0 <= y0 < h:
                    bitmap[x0, y0] = idx
                n += 1
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x0 += sxs
                if e2 <= dx:
                    err += dx
                    y0 += sys_

        # No rule across the whole chart. A line spanning the display draws
        # the eye everywhere and says nothing about where it matters. Instead
        # the stretch of the TARGET curve that sits above liquidus is drawn
        # bright and dashed -- that is the part of the run being pointed at.
        for colour, points in series:
            idx = 2 if colour == T.BRAND else 1
            prev = None
            prev_v = None
            for t, v in points:
                cur = (sx(t), sy(v))
                if prev is not None:
                    hot = (liquidus is not None and idx == 1
                           and (v >= liquidus or prev_v >= liquidus))
                    line(prev[0], prev[1], cur[0], cur[1],
                         3 if hot else idx, dash=3 if hot else 0)
                prev = cur
                prev_v = v

        return displayio.TileGrid(bitmap, pixel_shader=palette, x=x, y=y)

    def _note_font_fallback(self, path, exc):
        """Say so out loud. A silent fallback to terminalio means a font that
        failed to load looks merely wrong rather than announcing itself."""
        print("# font %s failed to load (%r); falling back" % (path, exc))
