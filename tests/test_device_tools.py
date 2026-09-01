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
HARNESSES = sorted(n for n in os.listdir(TOOLS) if n.endswith(".py"))


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
