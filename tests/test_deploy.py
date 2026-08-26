"""Deployment must not be able to abort a run.

Writing to CIRCUITPY soft-reboots the board. Doing that during a profile
aborts it, and relying on remembering not to is what failed: a deploy went
out into a run already at 160 °C. The check is mechanical now, and it fails
closed -- a device that says nothing is unknown, not idle.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import deploy


def test_an_unreadable_port_refuses_rather_than_assuming_idle():
    reason = deploy.running_check("/mnt/circuitpy",
                                  port="/dev/definitely-not-a-port",
                                  listen_s=0.1)
    assert reason is not None
    assert "cannot confirm" in reason


def test_the_busy_states_are_the_ones_that_matter():
    """preheat and cooldown count as busy as well as running: preheat is
    already applying heat, and a reboot during cooldown loses the run report
    and the metrics with it."""
    src = open(os.path.join(os.path.dirname(__file__), "..", "tools",
                            "deploy.py")).read()
    body = src[src.index("def running_check"):src.index("def main")]
    for state in ("running", "preheat", "cooldown"):
        assert '"%s"' % state in body


def test_force_is_available_but_shouts():
    src = open(os.path.join(os.path.dirname(__file__), "..", "tools",
                            "deploy.py")).read()
    assert "--force" in src
    assert "WARNING deploying anyway" in src
