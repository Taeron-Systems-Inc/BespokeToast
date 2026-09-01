# SPDX-License-Identifier: MIT
"""Check the touchscreen with a person present. No heat.

Nothing about touch has ever been verified on this oven. The calibration
was carried over from the previous firmware because it was the only place
it had been written down, and every button depends on it -- including
ABORT, which is the one control that has to work.

Two phases. First the calibration itself: a cross is drawn at five known
points and the error between where it was drawn and where the panel says
it was touched is reported. Then the real screens, one at a time, checking
that pressing where a button appears resolves to the action that button
claims -- which is a different question, because layout.hit() is what turns
a coordinate into an action.

Never imports oven.hardware, so the relay pin is not claimed and no heat is
possible. Everything here only reads the panel and draws.
"""

import gc
import time

import board
import adafruit_touchscreen

from oven.ui import layout as L
from oven.ui import theme as T
from oven.ui.display import Display, preload

# Must match oven.hardware.Touchscreen.CALIBRATION. Duplicated rather than
# imported because importing that module is how the relay pin gets claimed;
# a test in tests/test_device_tools.py holds the two together.
CALIBRATION = ((7184, 60984), (6995, 58195))

TARGETS = [(40, 40), (280, 40), (160, 120), (40, 200), (280, 200)]


def cross(x, y, label):
    return [
        ("rect", 0, 0, T.SCREEN_W, 3, T.BG, True),
        ("rect", x - 20, y - 1, 40, 3, T.BRAND, True),
        ("rect", x - 1, y - 20, 3, 40, T.BRAND, True),
        ("text", 10, 20, label, T.TEXT, T.FONT_BODY),
    ]


def wait_touch(ts, timeout=45.0):
    """One press, on the release edge, so a held finger reads once."""
    end = time.monotonic() + timeout
    seen = None
    while time.monotonic() < end:
        p = ts.touch_point
        if p is not None:
            seen = p
        elif seen is not None:
            return seen
        time.sleep(0.02)
    return None


def main():
    display = Display(board.DISPLAY)
    preload((T.FONT_READOUT, T.FONT_LARGE, T.FONT_BODY, T.FONT_SMALL))
    display.reserve_chart(L.CHART[2], L.CHART[3])
    ts = adafruit_touchscreen.Touchscreen(
        board.TOUCH_XL, board.TOUCH_XR, board.TOUCH_YD, board.TOUCH_YU,
        calibration=CALIBRATION,
        size=(board.DISPLAY.width, board.DISPLAY.height))

    print("TOUCH begin free=%d" % gc.mem_free())
    print("TOUCH phase 1: touch each cross as accurately as you can")

    errors = []
    for i, (tx, ty) in enumerate(TARGETS):
        display.render(cross(tx, ty, "touch the cross  %d of %d"
                             % (i + 1, len(TARGETS))))
        got = wait_touch(ts)
        if got is None:
            print("TOUCH   target %d (%3d,%3d): nothing registered" % (i + 1, tx, ty))
            continue
        dx, dy = got[0] - tx, got[1] - ty
        errors.append((dx, dy))
        print("TOUCH   target %d (%3d,%3d) -> (%3d,%3d)  error (%+d,%+d)"
              % (i + 1, tx, ty, got[0], got[1], dx, dy))

    if errors:
        ax = sum(abs(d[0]) for d in errors) / float(len(errors))
        ay = sum(abs(d[1]) for d in errors) / float(len(errors))
        bx = sum(d[0] for d in errors) / float(len(errors))
        by = sum(d[1] for d in errors) / float(len(errors))
        print("TOUCH mean absolute error  x=%.1f px  y=%.1f px" % (ax, ay))
        print("TOUCH mean bias            x=%+.1f px  y=%+.1f px" % (bx, by))
        worst = max(max(abs(d[0]), abs(d[1])) for d in errors)
        print("TOUCH worst single axis error = %d px" % worst)

    # Phase 2: the buttons themselves, on the screens they really appear on.
    profile_points = [[0, 25], [90, 150], [180, 217], [240, 235], [300, 150]]
    screens = [
        ("home", L.home(23.0, "SAC305 (this oven)", True, None),
         ["start", "profiles"]),
        ("running", L.running(150.0, 150.0, 150.0, 300.0, "soak", 0.0, 217,
                              0.5, True, history=[(0.0, 25.0), (150.0, 150.0)],
                              profile_points=profile_points, duration_s=450.0),
         ["abort"]),
        ("fault", L.fault("thermocouple fault: open circuit"), ["acknowledge"]),
    ]

    print("TOUCH phase 2: press the button named on screen")
    problems = 0
    for name, screen, wanted in screens:
        for action in wanted:
            prompt = list(screen)
            # The first run of this timed out because the instruction was
            # 12 px tall in the bottom margin. It is the only thing on
            # screen that matters here, so it is drawn like it.
            prompt.append(("rect", 0, 96, T.SCREEN_W, 52, T.BG, True))
            prompt.append(("text", 12, 122, "PRESS %s" % action.upper(),
                           T.BRAND, T.FONT_LARGE))
            display.render(prompt)
            got = wait_touch(ts)
            if got is None:
                print("TOUCH   %-8s %-12s nothing registered" % (name, action))
                problems += 1
                continue
            resolved = L.hit(screen, got[0], got[1])
            ok = resolved == action
            if not ok:
                problems += 1
            print("TOUCH   %-8s press at (%3d,%3d) -> %-12s %s"
                  % (name, got[0], got[1], resolved, "ok" if ok else
                     "WRONG, wanted %s" % action))

    display.render(L.home(23.0, "SAC305 (this oven)", True, None))
    print("TOUCH problems=%d" % problems)
    print("TOUCH done")


main()
