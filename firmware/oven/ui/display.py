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


def preload(paths):
    """Load fonts before anything nests inside a render.

    PCF glyph loading recurses, and at boot the first load happens deep in
    main -> render -> _rebuild -> _build -> Label -> load_font. That was
    enough to exhaust the Python stack: "RuntimeError: pystack exhausted",
    after which the half-built font reports every glyph as missing. Loading
    them here, at the top of main where the stack is shallow, costs nothing
    and removes the depth.
    """
    for path in paths:
        _font(path)


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
    """Renders a command list, reusing the objects it already has.

    The naive version rebuilt every Label, Rect and Group on each frame. At
    2 Hz that is a few hundred allocations a minute, and the SAMD51 heap
    fragments: measured on hardware, 155 render failures in one run, all
    MemoryError on 1848- and 2156-byte requests while roughly 100 KB was
    nominally free. Free memory was never the problem; contiguous space was.

    So the display group persists, and so do the objects in it. A frame whose
    *shape* matches the last one -- same sequence of kinds, same fonts, same
    bitmap paths -- updates text, colour and position in place and allocates
    nothing. A frame with a different shape (a change of screen) rebuilds
    once. That also matters for what comes next: the WiFi stack allocates
    socket and TLS buffers at unpredictable moments, and it cannot share a
    heap with something churning it every frame.
    """

    def __init__(self, board_display):
        self.display = board_display
        self.group = displayio.Group()
        self._set_root(self.group)
        self._sig = None
        self._slots = []
        # The chart buffer is allocated once and drawn incrementally.
        self._chart = None
        self._chart_key = None
        self._chart_palette = None
        self._chart_drawn = None
        self._chart_tile = None

    def _set_root(self, group):
        # display.show() was removed in CircuitPython 9.
        try:
            self.display.root_group = group
        except AttributeError:
            self.display.show(group)

    @staticmethod
    def _signature(commands):
        """What distinguishes one screen layout from another.

        Values that change every frame -- the temperature, a colour, a
        coordinate -- are deliberately excluded, so a screen holding still
        keeps its objects.
        """
        out = []
        for c in commands:
            if c[0] == "text":
                out.append(("text", c[5]))
            elif c[0] == "rect":
                out.append(("rect", c[6]))
            elif c[0] == "bitmap":
                out.append(("bitmap", c[3]))
            elif c[0] == "plot":
                out.append(("plot",))
            else:
                out.append((c[0],))
        return tuple(out)

    def render(self, commands):
        """Put *commands* on screen.

        Wrapped whole. A failure inside one element used to be caught per
        element, which is right, but a failure in the Group itself or in the
        renderer escaped and killed the firmware -- which is how a run died
        silently in cooldown with only the host watchdog noticing.
        """
        try:
            self._render(commands)
        except Exception as e:
            print("# WARNING render failed entirely (%r); screen left as-is" % e)

    def _render(self, commands):
        sig = self._signature(commands)
        if sig != self._sig:
            self._rebuild(commands, sig)
            return
        for slot, cmd in zip(self._slots, commands):
            try:
                self._update(slot, cmd)
            except Exception as e:
                # Name the string and the font. A bare "update failed for
                # text" is not enough to act on: the same TypeError is what a
                # glyph missing from a subsetted font raises, and without the
                # text you cannot tell which character or which face.
                print("# WARNING update failed: %r in %s (%r)"
                      % (cmd[3] if len(cmd) > 3 else "?",
                         cmd[5].rsplit("/", 1)[-1] if len(cmd) > 5 else "?", e))

    def _rebuild(self, commands, sig):
        # Any retained layer belongs to the OUTGOING group, and displayio
        # will not have one layer in two. Release it so this rebuild makes a
        # fresh wrapper.
        self._chart_tile = None

        # Release the chart bitmap too when the new screen has no chart.
        # Every remaining render failure in run 7 came in one burst, on the
        # first frame of the cooldown screen: a full rebuild while a 26 KB
        # chart bitmap was still resident, with nothing left to allocate the
        # new labels from. The cooldown screen does not plot anything, so
        # holding its buffer costs a screen.
        if not any(c[0] == "plot" for c in commands):
            self._chart = None
            self._chart_key = None
            self._chart_palette = None
            self._chart_drawn = None

        # Drop the outgoing group before building the new one, so the two are
        # never resident together.
        self._slots = []
        self.group = displayio.Group()
        self._set_root(self.group)

        group = displayio.Group()
        slots = []
        for cmd in commands:
            try:
                item = self._build(cmd)
            except Exception as e:
                print("# WARNING build failed: %r in %s (%r)"
                      % (cmd[3] if len(cmd) > 3 else "?",
                         cmd[5].rsplit("/", 1)[-1] if len(cmd) > 5 else "?", e))
                item = None
            slots.append(item)
            if item is not None:
                group.append(item)
        self.group = group
        self._slots = slots
        self._sig = sig
        self._set_root(group)

    def _update(self, item, cmd):
        """Change an existing object rather than making a new one."""
        if item is None:
            return
        kind = cmd[0]
        if kind == "text":
            _, x, y, text, colour, _font = cmd
            text = str(text)
            if item.text != text:
                item.text = text
            if item.color != colour:
                item.color = colour
            if item.x != x:
                item.x = x
            if item.y != y:
                item.y = y
        elif kind == "rect":
            _, x, y, w, h, colour, filled = cmd
            item.x = x
            item.y = y
            if filled:
                if item.fill != colour:
                    item.fill = colour
            elif item.outline != colour:
                item.outline = colour
        elif kind == "plot":
            self._plot(cmd)          # draws into the retained bitmap in place

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
        # Scales and the target curve do not change within a run, and the
        # measured trace only ever grows. So the chart is drawn INCREMENTALLY:
        # a full clear-and-redraw every frame meant displayio could refresh
        # while the buffer was blank, which is the flicker. Clearing only
        # happens when the geometry changes or a series gets shorter, which
        # means a new run.
        shape = (w, h, x_max, y_max, liquidus, len(series))
        counts = [len(pts) for _, pts in series]
        full = (self._chart_drawn is None
                or self._chart_drawn[0] != shape
                or len(self._chart_drawn[1]) != len(counts)
                or any(new < old for new, old in
                       zip(counts, self._chart_drawn[1])))
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
            full = True
        bitmap = self._chart
        palette = self._chart_palette
        if full:
            bitmap.fill(0)
            start_at = [0] * len(series)
        else:
            # resume one point back so the joining segment is not left out
            start_at = [max(0, n - 1) for n in self._chart_drawn[1]]

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
        for i, (colour, points) in enumerate(series):
            idx = 2 if colour == T.BRAND else 1
            begin = start_at[i]
            if begin >= len(points):
                continue
            prev = None
            prev_v = None
            for t, v in points[begin:]:
                cur = (sx(t), sy(v))
                if prev is not None:
                    hot = (liquidus is not None and idx == 1
                           and (v >= liquidus or prev_v >= liquidus))
                    colour_idx = 3 if hot else idx
                    # The target curve is drawn two pixels thick so it reads
                    # clearly against the measured trace; solid rather than
                    # dashed above liquidus, since a broken line is harder to
                    # follow exactly where it matters most.
                    line(prev[0], prev[1], cur[0], cur[1], colour_idx)
                    if idx == 1:
                        line(prev[0], prev[1] + 1, cur[0], cur[1] + 1,
                             colour_idx)
                prev = cur
                prev_v = v
        self._chart_drawn = (shape, counts)

        # The group persists now, so the TileGrid can persist with it. It is
        # rebuilt only when the bitmap itself is replaced -- a layer cannot
        # belong to two groups, which is what broke when the group was
        # rebuilt every frame.
        if self._chart_tile is None or self._chart_tile.bitmap is not bitmap:
            self._chart_tile = displayio.TileGrid(bitmap, pixel_shader=palette,
                                                  x=x, y=y)
        return self._chart_tile

    def _note_font_fallback(self, path, exc):
        """Say so out loud. A silent fallback to terminalio means a font that
        failed to load looks merely wrong rather than announcing itself."""
        print("# font %s failed to load (%r); falling back" % (path, exc))
