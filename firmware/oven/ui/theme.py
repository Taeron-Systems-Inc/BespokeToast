# SPDX-License-Identifier: MIT
"""Colours, type and spacing.

The accent is taken from the Taeron wordmark, which is a single flat colour,
so the brand and the interface accent are literally the same value.

Type is B612 (PolarSys/Eclipse, OFL-1.1), drawn for Airbus cockpit displays --
small emissive screens read at a glance under bad conditions, which is close
enough to a bench-top oven readout. Subsetted to PCF: the readout sizes carry
digits and a degree sign only, because a full charset at 64 px costs 329 KB to
render ten numerals.
"""

BG = 0x000000
BRAND = 0xC1D72E      # Taeron wordmark
TEXT = 0xFFFFFF
DIM = 0x8C8C96
CAUTION = 0xFFB000
DANGER = 0xFF3B30
COOL = 0x3AA0FF
FAINT = 0x4A4A52     # chart grid only, never type

SCREEN_W = 320
SCREEN_H = 240

# The live readout is 48 px, not 64.
#
# Measured on the device: setting .text on a bitmap_label reallocates its
# internal bitmap, and at 64 px that is a ~2156-byte block -- the exact
# allocation that failed 93 times during the low-temp run. In a direct test,
# a 48 px label survived 40 text changes with no net drift while the 64 px
# label could not even be constructed. "234 °C" measures 153 px at 48 px
# against 205 at 64, so it still reads across a bench and leaves more room.
#
# 64 px stays for the splash, which is drawn once and never updated.
FONT_READOUT = "/assets/fonts/B612-Bold-48.pcf"
FONT_READOUT_XL = "/assets/fonts/B612-Bold-64.pcf"
FONT_LARGE = "/assets/fonts/B612-24s.pcf"
FONT_BODY = "/assets/fonts/B612-Bold-16s.pcf"
FONT_SMALL = "/assets/fonts/B612-12s.pcf"

LOGO_LARGE = "/assets/taeron-logo-320.bmp"
LOGO_SMALL = "/assets/taeron-logo-120.bmp"

# Resistive touch with a fingertip is imprecise. Anything the operator has to
# hit under time pressure gets at least this, and ABORT gets more.
MIN_TOUCH_PX = 44
ABORT_TOUCH_PX = 48

# Colour for how far the oven is from where it should be.
DELTA_GOOD_C = 3.0
DELTA_WARN_C = 8.0


def delta_colour(delta_c):
    if delta_c is None:
        return DIM
    d = abs(delta_c)
    if d <= DELTA_GOOD_C:
        return BRAND
    if d <= DELTA_WARN_C:
        return CAUTION
    return DANGER


def stage_colour(stage, current):
    return BRAND if stage == current else DIM
