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


def test_a_profile_deleted_from_the_repository_is_removed_from_the_board(tmp_path):
    """Deploy copies and used to never remove, so cutting the shipped set
    from ten profiles to five left all ten on the board. A stale profile is
    not inert -- it is offered to whoever is choosing one, and one of the
    ten sat above the liquidus of both low-temp pastes."""
    dest = tmp_path / "CIRCUITPY"
    (dest / "profiles").mkdir(parents=True)
    (dest / "profiles" / "hold-150c.json").write_text("{}")
    (dest / "profiles" / "ts391snl.json").write_text("{}")
    gone = deploy.stale(str(dest))
    assert "profiles/hold-150c.json" in gone
    assert "profiles/ts391snl.json" not in gone


def test_pruning_only_touches_directories_the_repository_owns(tmp_path):
    """wifi.json, the logs and boot_out.txt live on the board and must
    survive a deploy that has never heard of them."""
    dest = tmp_path / "CIRCUITPY"
    (dest / "logs").mkdir(parents=True)
    (dest / "logs" / "0001-a.csv").write_text("x")
    (dest / "wifi.json").write_text("{}")
    (dest / "boot_out.txt").write_text("x")
    assert deploy.stale(str(dest)) == []


def test_names_code_py_imports_from_frozen_modules_are_collected(tmp_path):
    """The check that was missing. Adding a function to oven/ and
    deploying only code.py leaves the board stopping at "ImportError:
    cannot import name ..." before it prints anything, which reads like a
    dead board rather than a mismatch. It happened."""
    src = tmp_path / "code.py"
    src.write_text(
        "from oven.profile import Profile, for_operators\n"
        "from oven.ui import layout as L\n"
        "from oven.logstore import LogStore\n"
        "import os\n"
        "from collections import OrderedDict\n")
    pairs = deploy.frozen_imports(str(src))
    assert ("oven.profile", "for_operators") in pairs
    assert ("oven.profile", "Profile") in pairs
    assert ("oven.logstore", "LogStore") in pairs
    assert not any(m == "collections" for m, _ in pairs), (
        "only oven/ is frozen; other imports are not this check's business")


def test_the_real_code_py_declares_the_name_that_broke_the_board():
    pairs = deploy.frozen_imports(
        os.path.join(os.path.dirname(deploy.__file__), "..", "firmware",
                     "code.py"))
    assert ("oven.profile", "for_operators") in pairs


def test_handing_the_volume_back_refuses_while_the_host_holds_it(tmp_path,
                                                                 monkeypatch):
    """Two writers on one FAT volume is how a filesystem gets corrupted.

    A deploy leaves the host owning CIRCUITPY, and the natural next step is
    to hand it straight back -- with the mount still up, because nothing
    made you unmount it.
    """
    import tools.deploy as d

    point = tmp_path / "circuitpy"
    point.mkdir()
    (point / "boot_out.txt").write_text("Adafruit CircuitPython 8.0.5\n")
    monkeypatch.setattr(d, "mounted_circuitpy", lambda: [str(point)])

    called = []
    monkeypatch.setattr(d, "set_boot_mode",
                        lambda *a, **k: called.append(a) or None)
    assert d.hand_volume_back_to_the_oven() == 1
    assert not called, "the boot mode was changed with the volume mounted"


def test_handing_the_volume_back_asks_for_standalone_not_host(monkeypatch):
    """--standalone once set the host byte, which quietly did nothing.

    The two modes differ by one byte and the reset looks identical either
    way, so the wrong one is invisible until a run keeps no log.
    """
    import tools.deploy as d

    monkeypatch.setattr(d, "mounted_circuitpy", lambda: [])
    seen = []
    monkeypatch.setattr(d, "set_boot_mode",
                        lambda mode, **k: seen.append(mode) or None)
    assert d.hand_volume_back_to_the_oven() == 0
    assert seen == [d.STANDALONE_MODE]
    assert d.STANDALONE_MODE != d.HOST_MODE


def test_mounted_circuitpy_identifies_the_volume_by_its_contents(tmp_path,
                                                                 monkeypatch):
    """By boot_out.txt, not by label: /proc/mounts records the source device
    and the mount point, and the label lives on the device."""
    import tools.deploy as d

    board = tmp_path / "board"
    board.mkdir()
    (board / "boot_out.txt").write_text("x")
    other = tmp_path / "camera"
    other.mkdir()
    mounts = tmp_path / "mounts"
    mounts.write_text("/dev/sda1 %s vfat rw 0 0\n"
                      "/dev/sdb1 %s vfat rw 0 0\n"
                      "/dev/mmcblk0p2 / ext4 rw 0 0\n" % (board, other))

    real_open = open
    monkeypatch.setattr("builtins.open",
                        lambda p, *a, **k: real_open(mounts, *a, **k)
                        if p == "/proc/mounts" else real_open(p, *a, **k))
    assert d.mounted_circuitpy() == [str(board)]


def test_the_reset_taking_the_port_with_it_is_not_a_failure(monkeypatch):
    """The last line of the mode script is microcontroller.reset().

    Writing it disconnects the USB device, so the write, the flush or the
    close raises EIO -- reliably, on this board. Reporting that as "could
    not set the boot mode" is a lie told at the exact moment it worked, and
    it sent someone round the loop three times.
    """
    import tools.deploy as d

    class Port(object):
        def __init__(self, *a, **k):
            self.written = []

        def write(self, data):
            text = data.decode("utf-8", "replace")
            if "reset()" in text:
                raise OSError(5, "Input/output error")
            self.written.append(text)

        def read(self, n=1):
            return b""

        def flush(self):
            pass

        def close(self):
            raise OSError(5, "Input/output error")

    port = Port()
    fake = type("m", (), {"Serial": lambda *a, **k: port})
    monkeypatch.setitem(__import__("sys").modules, "serial", fake)
    monkeypatch.setattr(d, "resolve_port", lambda p=None: "/dev/fake")
    monkeypatch.setattr(d.time, "sleep", lambda s: None)

    assert d.set_boot_mode(d.STANDALONE_MODE) is None
    assert any("0x5A" in w for w in port.written), \
        "the mode byte was never written"
