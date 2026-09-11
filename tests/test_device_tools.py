# SPDX-License-Identifier: MIT
"""The on-device test harnesses must not be able to switch the oven on.

soak.py and simulate.py run on the board, unattended, often with nobody in
the building. They exist to exercise the display and the state machine
without heat, and that property should be enforced rather than remembered:
neither may claim the relay pin, directly or through oven.hardware.
"""

import ast
import os

import pytest

TOOLS = os.path.join(os.path.dirname(__file__), "..", "tools", "device")

# One harness heats the oven on purpose, because identifying a plant needs
# the plant. It is named here rather than pattern-matched so that adding a
# second one is a decision somebody makes in this file, not something that
# happens by choosing a filename. Its own interlocks are tested below.
HEATS = "heat_step_test.py"

HARNESSES = sorted(n for n in os.listdir(TOOLS)
                   if n.endswith(".py") and n != HEATS)


def _tree(name):
    return ast.parse(open(os.path.join(TOOLS, name)).read())


def _imports(tree):
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            out.add(node.module or "")
    return out


def test_there_are_harnesses_to_check():
    assert HARNESSES, "no device harnesses found; this test would pass vacuously"


@pytest.mark.parametrize("name", HARNESSES)
def test_no_harness_imports_the_hardware_layer(name):
    imported = _imports(_tree(name))
    assert "oven.hardware" not in imported, (
        "%s imports oven.hardware, which claims the relay pin" % name)
    assert "digitalio" not in imported, (
        "%s imports digitalio and could drive a pin directly" % name)


@pytest.mark.parametrize("name", HARNESSES)
def test_no_harness_names_the_relay_pin(name):
    """board.D4 is the relay. Nothing here may reference it."""
    for node in ast.walk(_tree(name)):
        if isinstance(node, ast.Attribute) and node.attr == "D4":
            pytest.fail("%s references board.D4, the relay pin" % name)


@pytest.mark.parametrize("name", HARNESSES)
def test_a_harness_that_fakes_a_relay_says_so(name):
    """A fake relay is fine -- an unlabelled one invites confusion.

    Matched on any class with Relay in its name, not one exact spelling:
    the check quietly stopped applying the moment a harness called its
    stand-in Relay instead of FakeRelay.
    """
    source = open(os.path.join(TOOLS, name)).read()
    relays = [n.name for n in ast.walk(_tree(name))
              if isinstance(n, ast.ClassDef) and "relay" in n.name.lower()]
    if not relays:
        return
    lowered = source.lower()
    assert ("no heat" in lowered or "cannot energise" in lowered
            or "owns no pin" in lowered), (
        "%s defines %s without stating that it drives nothing"
        % (name, ", ".join(relays)))


def test_the_touch_harness_calibration_matches_the_firmware():
    """The harness duplicates the calibration; it must not drift from it.

    It cannot import oven.hardware -- that is the module which claims the
    relay pin -- so the constant is repeated, and repeated constants are
    exactly the kind that quietly diverge. Testing the calibration with a
    stale copy would prove nothing about the oven.
    """
    import re
    hw = open(os.path.join(os.path.dirname(__file__), "..", "firmware",
                           "oven", "hardware.py")).read()
    harness = open(os.path.join(TOOLS, "touchtest.py")).read()

    def calibration(source):
        m = re.search(r"CALIBRATION\s*=\s*(\(\(.*?\)\))", source, re.S)
        assert m, "no CALIBRATION found"
        return eval(m.group(1))

    assert calibration(hw) == calibration(harness), (
        "touchtest.py tests a calibration the firmware does not use")


# -- the one harness that does heat ----------------------------------------

def test_exactly_one_harness_is_allowed_to_heat():
    """If this fails, somebody added a second. That is a decision, not an
    accident, and it should be made deliberately in this file."""
    heaters = []
    for name in sorted(os.listdir(TOOLS)):
        if not name.endswith(".py"):
            continue
        if "oven.hardware" in _imports(_tree(name)):
            heaters.append(name)
    assert heaters == [HEATS], heaters


def test_the_heating_harness_says_so_in_its_first_line():
    """Whoever opens this file should know inside one line. Every other
    tool here is safe to run blind; this one is not."""
    first = open(os.path.join(TOOLS, HEATS)).readline() + \
        open(os.path.join(TOOLS, HEATS)).readlines()[1]
    assert "HEATS" in first.upper()


def test_the_heating_harness_does_not_run_on_import():
    """`import heat_step_test` on the board must not start anything. The
    module is read on a device that is sitting in a workshop."""
    tree = _tree(HEATS)
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            pytest.fail("%s calls something at module scope" % HEATS)
        if isinstance(node, ast.If):
            pytest.fail("%s has a top-level if; keep it declarative" % HEATS)


def test_the_heating_harness_refuses_without_the_token():
    """A typo, a half-remembered call, a paste that lost an argument: all of
    them must end in a refusal rather than in heat."""
    src = open(os.path.join(TOOLS, HEATS)).read()
    tree = ast.parse(src)
    main = [n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "main"]
    assert main, "no main()"
    # the first thing main does is compare confirm against the token
    first = main[0].body[1] if len(main[0].body) > 1 else main[0].body[0]
    assert isinstance(first, ast.If), "main does not start with a guard"
    assert "confirm" in ast.dump(first.test)
    # and the token is not something anyone types by accident
    assert "CONFIRM = " in src
    token = src.split("CONFIRM = ", 1)[1].split("\n", 1)[0].strip().strip('"')
    assert len(token) > 8, token


def test_the_heating_harness_drives_the_relay_low_whatever_happens():
    tree = _tree(HEATS)
    main = [n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "main"][0]
    tries = [n for n in ast.walk(main) if isinstance(n, ast.Try) and n.finalbody]
    assert tries, "main has no try/finally"
    off = False
    for t in tries:
        for node in ast.walk(ast.Module(body=t.finalbody, type_ignores=[])):
            if isinstance(node, ast.Call) and \
                    isinstance(node.func, ast.Attribute) and \
                    node.func.attr in ("off", "set"):
                off = True
    assert off, "nothing in the finally block de-energises the relay"


def test_a_step_cannot_be_given_a_ceiling_above_the_characterised_range():
    src = open(os.path.join(TOOLS, HEATS)).read()
    assert "250.0" in src and "ceiling" in src, (
        "Step no longer bounds its ceiling; an open-loop schedule could be "
        "pointed anywhere and only the supervisor would object")


def test_the_schedule_is_bounded_in_wall_clock_time():
    src = open(os.path.join(TOOLS, HEATS)).read()
    assert "max_total_s" in src
    assert "wall clock limit" in src, (
        "nothing stops a schedule that overruns its own arithmetic")
