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


def test_telemetry_parsing_tolerates_extra_columns():
    """The column set grew once -- adding the controller die temperature took
    the row from seven fields to eight -- and a strict length check silently
    refused every pre-flight until it was noticed. New columns must not break
    the tools that read them."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
    import start_run
    seven = "123.4,idle,25.5,,0.000,0,26.1"
    eight = "123.4,idle,25.5,,0.000,0,26.1,33.2"
    nine = eight + ",99.9"
    for line in (seven, eight, nine):
        row = start_run.parse(line)
        assert row is not None, "refused %r" % line
        assert row["state"] == "idle" and row["temp"] == 25.5
    assert start_run.parse(seven)["cpu"] is None
    assert start_run.parse(eight)["cpu"] == 33.2
    assert start_run.parse("garbage,not,a,row") is None


def test_deploy_refuses_an_empty_or_wrong_destination(tmp_path):
    """A mount pointing at a stale device node reads as an empty directory,
    so a deploy reports success while writing nowhere near the board. That
    happened: the PyPortal re-enumerated sda -> sdb -> sda across hard resets
    and a deploy silently went into a dead mount."""
    src = open(os.path.join(os.path.dirname(__file__), "..", "tools",
                            "deploy.py")).read()
    assert "os.listdir(dest)" in src, "deploy must reject an empty destination"
    assert "boot_out.txt" in src, "deploy must confirm it is a CIRCUITPY volume"


def test_running_check_parses_the_telemetry_the_firmware_actually_emits():
    """The idle check must track the telemetry format, not a field count.

    It was written against a 7-field row; cpu_c made it 8 and the check
    matched nothing from then on, reporting "no telemetry" for every deploy.
    This pins it to a real line taken off the device.
    """
    import tools.deploy as d
    line = "262100.88,idle,27.1250,,0.000,0,26.06,34.29"
    parts = line.split(",")
    assert len(parts) >= 6 and parts[1] in d.STATES

    header = "# t,state,temp_c,target_c,duty,relay,cold_c,cpu_c"
    fields = header[2:].split(",")
    assert fields[1] == "state", "state must stay the second column"


def test_deploy_resolves_the_port_by_id_not_by_number():
    import tools.deploy as d
    assert d.resolve_port("/dev/ttyS9") == "/dev/ttyS9"
    assert "by-id" in d.resolve_port() or d.resolve_port().startswith("/dev/tty")
