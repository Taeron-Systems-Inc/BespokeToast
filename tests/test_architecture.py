"""The rule that makes everything else testable, enforced.

Only hardware.py may import board. If that slips, the control and safety
logic silently stops being runnable off-hardware and the whole test suite
becomes un-runnable on any machine that is not the oven — which is exactly
how the previous firmware ended up untestable.
"""

import ast
import os

import pytest

OVEN = os.path.join(os.path.dirname(__file__), "..", "firmware", "oven")
BOARD_ONLY = {"board", "digitalio", "busio", "microcontroller", "displayio",
              "audioio", "audiocore", "neopixel", "adafruit_mcp9600",
              "supervisor", "storage", "usb_cdc"}
ALLOWED = {"hardware.py"}


def modules():
    return sorted(f for f in os.listdir(OVEN) if f.endswith(".py"))


def imports_of(path):
    tree = ast.parse(open(path).read())
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return found


@pytest.mark.parametrize("name", modules())
def test_only_hardware_may_touch_the_board(name):
    if name in ALLOWED:
        return
    offending = imports_of(os.path.join(OVEN, name)) & BOARD_ONLY
    assert not offending, (
        "%s imports %s; that belongs behind hal.py so this module stays "
        "runnable under CPython" % (name, ", ".join(sorted(offending))))


@pytest.mark.parametrize("name", modules())
def test_pure_modules_actually_import_under_cpython(name):
    if name in ALLOWED:
        return
    __import__("oven." + name[:-3])


def test_hardware_module_exists_and_is_the_designated_exception():
    assert os.path.exists(os.path.join(OVEN, "hardware.py"))
    assert imports_of(os.path.join(OVEN, "hardware.py")) & BOARD_ONLY
