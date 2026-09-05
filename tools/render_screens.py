#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Draw the firmware's screens to PNGs, on a host, from the real fonts.

Every automated check in this project proves that rendering did not raise.
None of them prove the screen is *right*: a label can be clipped, overlap
its neighbour, sit off the panel or come out blank, and every test still
passes. The only real check so far has been someone photographing the oven.

So this consumes the same command lists layout.py emits and rasterises them
with the same PCF files the device loads, glyph for glyph. It is not a
simulation of the display library -- it is the same geometry, drawn where
it can be looked at.

    python3 tools/render_screens.py [outdir]
"""

import os
import struct
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "firmware"))

from oven.profile import Profile                                   # noqa: E402
from oven.ui import layout as L                                    # noqa: E402
from oven.ui import theme as T                                     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIRMWARE = os.path.join(HERE, "..", "firmware")
SCALE = 2

PCF_METRICS = 1 << 2
PCF_BITMAPS = 1 << 3
PCF_BDF_ENCODINGS = 1 << 5


class Font(object):
    """Just enough PCF to draw with: metrics, encodings and bitmaps."""

    def __init__(self, path):
        with open(path, "rb") as fh:
            self.data = fh.read()
        n = struct.unpack("<i", self.data[4:8])[0]
        self.toc = {}
        for i in range(n):
            kind, _fmt, _size, off = struct.unpack(
                "<iiii", self.data[8 + 16 * i:24 + 16 * i])
            self.toc[kind] = off
        self.metrics = self._metrics(self.toc[PCF_METRICS])
        self.encodings = self._encodings(self.toc[PCF_BDF_ENCODINGS])
        self.offsets, self.bitmap_base, self.bitmap_format = \
            self._bitmaps(self.toc[PCF_BITMAPS])
        self.ascent = max(m[3] for m in self.metrics)
        self.descent = max(m[4] for m in self.metrics)

    def _metrics(self, off):
        fmt = struct.unpack("<i", self.data[off:off + 4])[0]
        big = ">" if fmt & 4 else "<"
        p = off + 4
        if fmt & 0x100:
            count = struct.unpack(big + "h", self.data[p:p + 2])[0]
            p += 2
            return [tuple(b - 0x80 for b in self.data[p + 5 * i:p + 5 * i + 5])
                    for i in range(count)]
        count = struct.unpack(big + "i", self.data[p:p + 4])[0]
        p += 4
        return [struct.unpack(big + "5hH",
                              self.data[p + 12 * i:p + 12 * i + 12])[:5]
                for i in range(count)]

    def _encodings(self, off):
        fmt = struct.unpack("<i", self.data[off:off + 4])[0]
        big = ">" if fmt & 4 else "<"
        lo0, lo1, hi0, hi1, _d = struct.unpack(big + "5h",
                                               self.data[off + 4:off + 14])
        p = off + 14
        out = {}
        for hi in range(hi0, hi1 + 1):
            for lo in range(lo0, lo1 + 1):
                g = struct.unpack(big + "H", self.data[p:p + 2])[0]
                p += 2
                if g != 0xFFFF:
                    out[(hi << 8) | lo] = g
        return out

    def _bitmaps(self, off):
        fmt = struct.unpack("<i", self.data[off:off + 4])[0]
        big = ">" if fmt & 4 else "<"
        count = struct.unpack(big + "i", self.data[off + 4:off + 8])[0]
        p = off + 8
        offsets = [struct.unpack(big + "i", self.data[p + 4 * i:p + 4 * i + 4])[0]
                   for i in range(count)]
        p += 4 * count
        sizes = [struct.unpack(big + "i", self.data[p + 4 * i:p + 4 * i + 4])[0]
                 for i in range(4)]
        p += 16
        return offsets, p, fmt

    def glyph(self, ch):
        g = self.encodings.get(ord(ch))
        if g is None:
            return None
        lsb, rsb, cw, asc, desc = self.metrics[g]
        w, h = rsb - lsb, asc + desc
        pad = 1 << (self.bitmap_format & 3)
        row = ((w + 7) // 8 + pad - 1) // pad * pad
        start = self.bitmap_base + self.offsets[g]
        msb_bit = bool(self.bitmap_format & 8)
        pixels = []
        for y in range(h):
            line = []
            for x in range(w):
                byte = self.data[start + y * row + x // 8]
                bit = (7 - x % 8) if msb_bit else (x % 8)
                line.append((byte >> bit) & 1)
            pixels.append(line)
        return {"w": w, "h": h, "lsb": lsb, "asc": asc, "cw": cw,
                "pixels": pixels}

    def width(self, text):
        total = 0
        for ch in text:
            g = self.encodings.get(ord(ch))
            total += self.metrics[g][2] if g is not None else 0
        return total


_FONTS = {}


def font(path):
    if path not in _FONTS:
        _FONTS[path] = Font(os.path.join(FIRMWARE, path.lstrip("/")))
    return _FONTS[path]


def rgb(value):
    return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)


def draw_text(img, x, y, text, colour, path):
    """y is the vertical centre of the line, as adafruit_display_text uses."""
    f = font(path)
    height = f.ascent + f.descent
    baseline = int(y + height / 2.0 - f.descent)
    pen = x
    px = img.load()
    col = rgb(colour)
    for ch in str(text):
        g = f.glyph(ch)
        if g is None:
            g = f.glyph("?")
            if g is None:
                pen += 10
                continue
        top = baseline - g["asc"]
        for row in range(g["h"]):
            for cx in range(g["w"]):
                if not g["pixels"][row][cx]:
                    continue
                ix, iy = pen + g["lsb"] + cx, top + row
                if 0 <= ix < img.width and 0 <= iy < img.height:
                    px[ix, iy] = col
        pen += g["cw"]


def render(commands, name, outdir):
    img = Image.new("RGB", (T.SCREEN_W, T.SCREEN_H), rgb(T.BG))
    d = ImageDraw.Draw(img)
    for cmd in commands:
        kind = cmd[0]
        if kind == "rect":
            _, x, y, w, h, colour, filled = cmd
            box = [x, y, x + w - 1, y + h - 1]
            if filled:
                d.rectangle(box, fill=rgb(colour))
            else:
                d.rectangle(box, outline=rgb(colour))
        elif kind == "text":
            _, x, y, text, colour, path = cmd
            draw_text(img, x, y, text, colour, path)
        elif kind == "plot":
            _, x, y, w, h, x_max, y_min, y_max, series, liquidus = cmd
            d.rectangle([x, y, x + w - 1, y + h - 1], outline=rgb(0x202020))

            def sx(v):
                return x + (0 if x_max <= 0 else
                            int(max(0, min(w - 1, v / x_max * (w - 1)))))

            def sy(v):
                span = y_max - y_min
                if span <= 0:
                    return y + h - 1
                return y + int(max(0, min(
                    h - 1, (h - 1) - (v - y_min) / span * (h - 1))))
            if liquidus is not None:
                ly = sy(liquidus)
                for seg in range(x, x + w, 8):
                    d.line([seg, ly, seg + 3, ly], fill=rgb(T.DANGER))
            for idx, (_label, pts) in enumerate(series):
                colour = rgb(T.DIM if idx == 0 else T.BRAND)
                last = None
                for t, v in pts:
                    here = (sx(t), sy(v))
                    if last is not None:
                        d.line([last, here], fill=colour)
                    last = here
        elif kind == "bitmap":
            _, x, y, path = cmd
            d.rectangle([x, y, x + 40, y + 20], outline=rgb(T.BRAND))
    big = img.resize((T.SCREEN_W * SCALE, T.SCREEN_H * SCALE), Image.NEAREST)
    path = os.path.join(outdir, "%s.png" % name)
    big.save(path)
    return path, img


def screens():
    profile = Profile.load(os.path.join(FIRMWARE, "profiles",
                                        "ts391snl.json"))
    trace = []
    t = 0.0
    while t <= 300:
        trace.append((t, profile.target_at(t) - 4.0))
        t += 4.0
    return [
        ("01-splash", L.splash("v2.0-dev")),
        ("02-self-test", L.self_test([("thermocouple", True),
                                      ("relay safe state", True),
                                      ("profiles", True),
                                      ("characterisation", True),
                                      ("run logging", False)])),
        ("03-home-ready", L.home(23.4, profile.name, True, None,
                                 address="10.20.10.242")),
        ("04-home-too-hot", L.home(88.0, profile.name, False,
                                   "oven too hot to start")),
        ("05-running-soak", L.running(151.2, 150.0, 150.0, 338.0, "soak",
                                      0.0, profile.liquidus_c, 0.42, True,
                                      history=trace[:38],
                                      profile_points=profile.points,
                                      duration_s=profile.duration)),
        ("06-running-peak", L.running(236.4, 235.0, 300.0, 188.0, "reflow",
                                      64.0, profile.liquidus_c, 0.18, False,
                                      history=trace,
                                      profile_points=profile.points,
                                      duration_s=profile.duration)),
        ("07-cooldown", L.open_the_door(214.0, -6.9)),
        ("08-report", L.report([
            ("peak", 236.4, True, "236 \u00b0C (want 230-245)"),
            ("time above liquidus", 97.0, True, "97 s (want 60-150)"),
            ("max ramp up", 3.4, False, "3.4 \u00b0C/s (want <3.0)"),
            ("soak", 92.0, True, "92 s (want 60-120)")],
            236.4, 97.0)),
        ("09-fault", L.fault("over temperature: 262.3 °C exceeds 260.0 °C")),
        ("10-fault-long", L.fault(
            "sensor reading not changing: 120.06 °C for 31 s during a run")),
    ]


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "screens"
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    made = []
    for name, cmds in screens():
        path, img = render(cmds, name, outdir)
        made.append((name, path, img))
        print("  %s" % path)
    sheet = Image.new("RGB", (T.SCREEN_W * 2 + 24, T.SCREEN_H * 5 + 60),
                      (24, 24, 28))
    for i, (_n, _p, img) in enumerate(made):
        sheet.paste(img, (8 + (i % 2) * (T.SCREEN_W + 8),
                          8 + (i // 2) * (T.SCREEN_H + 12)))
    sheet.save(os.path.join(outdir, "contact-sheet.png"))
    print("  %s" % os.path.join(outdir, "contact-sheet.png"))


if __name__ == "__main__":
    main()
