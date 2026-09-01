# SPDX-License-Identifier: MIT
"""Drive every screen through the full temperature range, without heating.

Runs ON the PyPortal, and deliberately does NOT import oven.hardware: the
relay pin is never claimed, so this cannot energise the oven no matter what
it does. That is the whole point -- the display bugs that have cost the most
time here are heap bugs, and they reproduce from the render path alone.

It matters that this builds the same objects code.py does, in the same order
(fonts preloaded, chart buffer reserved, profiles loaded, a chart history
that grows), because the failures only appear once the heap is fragmented,
and MicroPython's collector never compacts. Synthetic fragmentation does not
reproduce it -- adjacent frees coalesce and the heap comes back whole.

A sweep to 260 C takes seconds here against roughly twenty minutes of real
heating, and it covers the reflow range that a low-temperature test profile
never reaches.
"""

import gc
import json
import os
import time

import board

from oven.profile import Profile
from oven.ui import layout as L
from oven.ui import theme as T
from oven.ui.display import Display, preload, largest_free_block

PROFILE_DIR = "/profiles"


def heap():
    gc.collect()
    return gc.mem_free(), largest_free_block()


def main():
    display = Display(board.DISPLAY)
    preload((T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL))
    display.reserve_chart(L.CHART[2], L.CHART[3])

    profiles = []
    for name in sorted(os.listdir(PROFILE_DIR)):
        if name.endswith(".json"):
            try:
                profiles.append(Profile.load(PROFILE_DIR + "/" + name))
            except Exception as e:
                print("SOAK profile %s rejected: %r" % (name, e))
    profile = profiles[0]
    for p in profiles:
        if getattr(p, "is_default", False):
            profile = p
    free0, big0 = heap()
    print("SOAK start free=%d largest=%d profile=%s"
          % (free0, big0, profile.name))

    history = []
    frames = 0
    t0 = time.monotonic()
    passes = 3

    # Up through the whole reflow range and back down, at every whole degree,
    # so each digit-count boundary is crossed in both directions. Repeated,
    # because a one-time cost and a slow leak look identical after one pass:
    # the first sweep retains the persistent display objects, and every sweep
    # after it should cost nothing.
    for sweep in range(passes):
      before = heap()
      for temp in list(range(20, 261)) + list(range(260, 19, -1)):
        elapsed = float(len(history) * 2)
        history.append((elapsed, float(temp)))
        if len(history) > 160:
            del history[0]
        target = profile.target_at(min(elapsed, profile.duration))
        display.render(L.running(
            float(temp), target, elapsed,
            max(0.0, profile.duration - elapsed), "reflow",
            float(len(history)), profile.liquidus_c, 0.5, temp % 2 == 0,
            history=history, profile_points=profile.points,
            duration_s=profile.duration))
        frames += 1
      after = heap()
      print("SOAK sweep %d free=%d (%+d) largest=%d"
            % (sweep + 1, after[0], after[0] - before[0], after[1]))

    # The screens a run passes through on the way out, each drawn from a
    # state the heap has already been worked into.
    for temp in (250.0, 180.0, 90.0, 40.0):
        display.render(L.open_the_door(temp, -6.9))
        frames += 1
    display.render(L.home(28.0, profile.name, True, None))
    display.render(L.home(None, profile.name, False, "oven too hot to start"))
    display.render(L.fault("thermocouple open circuit"))
    display.render(L.self_test([("thermocouple", True), ("relay safe", True)]))
    frames += 4

    free1, big1 = heap()
    dt = time.monotonic() - t0
    print("SOAK end free=%d largest=%d frames=%d seconds=%.1f"
          % (free1, big1, frames, dt))
    print("SOAK drift free=%+d largest=%+d" % (free1 - free0, big1 - big0))
    print("SOAK done")


main()
