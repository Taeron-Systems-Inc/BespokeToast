# SPDX-License-Identifier: MIT
"""On-device run logging, driven against a fake filesystem.

Eviction deletes files. That code should never have to be exercised for the
first time on the device with a run's record on the line, so the filesystem
is injected and every path here runs on the host.
"""

import pytest

from oven.logstore import LogStore, HEADER_FIELDS, _sequence_of


class FakeFile(object):
    def __init__(self, store, path):
        self.store = store
        self.path = path
        self.closed = False

    def write(self, text):
        if self.store.readonly:
            raise OSError(30, "Read-only filesystem")
        if self.store.full:
            raise OSError(28, "No space left on device")
        self.store.files[self.path] += text

    def flush(self):
        pass

    def close(self):
        self.closed = True


class FakeFS(object):
    def __init__(self, free=5000000, readonly=False, full=False):
        self.files = {}
        self.dirs = set()
        self.free = free
        self.readonly = readonly
        self.full = full
        self.removed = []

    def exists(self, path):
        return path in self.dirs or path in self.files

    def listdir(self, path):
        prefix = path.rstrip("/") + "/"
        if path not in self.dirs:
            raise OSError(2, "No such directory")
        return [p[len(prefix):] for p in self.files if p.startswith(prefix)]

    def mkdir(self, path):
        if self.readonly:
            raise OSError(30, "Read-only filesystem")
        if path in self.dirs:
            raise OSError(17, "exists")
        self.dirs.add(path)

    def remove(self, path):
        del self.files[path]
        self.removed.append(path)

    def size(self, path):
        return len(self.files[path])

    def open(self, path, mode):
        if self.readonly:
            raise OSError(30, "Read-only filesystem")
        self.files[path] = ""
        return FakeFile(self, path)

    def free_bytes(self):
        return self.free


def make(fs=None, **kw):
    fs = fs or FakeFS()
    fs.dirs.add("/logs")
    warnings = []
    store = LogStore(fs=fs, on_warning=warnings.append, **kw)
    return store, fs, warnings


def test_a_run_is_recorded_with_its_header_and_rows():
    store, fs, _ = make()
    path = store.begin("SAC305 (this oven)", "v2.0", "2026-08-31T10:00:00Z")
    assert path is not None
    store.write(0.0, 25.0, 25.4, False, 30.0, 34.0)
    store.write(1.0, 26.0, 25.9, True, 30.1, 34.1)
    store.end(summary="peak=236.7 tal=97")
    text = fs.files[path]
    assert ",".join(HEADER_FIELDS) in text
    assert "# profile,SAC305 (this oven)" in text
    assert "# firmware,v2.0" in text
    assert "0.0,25.00,25.400,0,30.00,34.00" in text
    assert "1.0,26.00,25.900,1,30.10,34.10" in text
    assert "# summary,peak=236.7 tal=97" in text
    assert "# rows,2" in text


def test_missing_values_are_left_empty_not_invented():
    store, fs, _ = make()
    path = store.begin("p", "v", "t")
    store.write(0.0, None, None, False, None, None)
    row = [l for l in fs.files[path].splitlines() if l.startswith("0.0")][0]
    assert row == "0.0,,,0,,"


def test_oldest_runs_are_discarded_to_hold_the_reserve():
    fs = FakeFS(free=1000)
    store, fs, warnings = make(fs=fs, reserve_bytes=5000)
    for i in range(4):
        fs.files["/logs/%04d-old.csv" % (i + 1)] = "x" * 2000
    store.begin("new", "v", "t")
    # 1000 free, needs 5000; each file returns 2000 -> two are enough.
    assert fs.removed == ["/logs/0001-old.csv", "/logs/0002-old.csv"]
    assert len(warnings) == 1
    assert "discarded 2 oldest" in warnings[0]


def test_nothing_is_discarded_when_there_is_room():
    fs = FakeFS(free=9000000)
    store, fs, warnings = make(fs=fs)
    fs.files["/logs/0001-old.csv"] = "x" * 2000
    store.begin("new", "v", "t")
    assert fs.removed == []
    assert warnings == []


def test_runs_are_ordered_by_sequence_not_alphabetically():
    """0010 sorts before 0002 as text, and that is the wrong file to delete."""
    store, fs, _ = make()
    for name in ("0002-a.csv", "0010-b.csv", "0001-c.csv"):
        fs.files["/logs/" + name] = "x"
    assert store.runs() == ["0001-c.csv", "0002-a.csv", "0010-b.csv"]
    assert _sequence_of("0010-b.csv") == 10


def test_the_sequence_continues_past_existing_runs():
    store, fs, _ = make()
    fs.files["/logs/0007-x.csv"] = "x"
    path = store.begin("SAC305 (this oven)", "v", "t")
    assert path == "/logs/0008-SAC305-this-oven.csv"


def test_a_read_only_filesystem_disables_logging_without_raising():
    """USB-writable is the normal state, and a run must not care.

    When the volume is mounted writable by a host, CircuitPython cannot
    write to it at all. Logging is a nice-to-have; the run is not.
    """
    fs = FakeFS(readonly=True)
    store, fs, warnings = make(fs=fs)
    assert store.begin("p", "v", "t") is None
    assert store.write(0.0, 1.0, 1.0, False, 1.0, 1.0) is False
    assert len(warnings) == 1
    assert "will not be recorded" in warnings[0]


def test_a_filesystem_that_fills_mid_run_complains_once_and_stops():
    store, fs, warnings = make()
    store.begin("p", "v", "t")
    store.write(0.0, 1.0, 1.0, False, 1.0, 1.0)
    fs.full = True
    for _ in range(50):
        assert store.write(1.0, 1.0, 1.0, False, 1.0, 1.0) is False
    assert len(warnings) == 1, "one warning, not one per sample"


def test_logging_failure_never_raises_into_the_control_loop():
    """Every public call must be safe when the filesystem is hostile."""
    fs = FakeFS(readonly=True)
    store, fs, _ = make(fs=fs)
    store.begin("p", "v", "t")
    store.write(0.0, 1.0, 1.0, True, 1.0, 1.0)
    store.end("summary")
    store.close()
    store.runs()
    store.free_bytes()


def test_rate_is_one_hertz_and_documented():
    from oven import logstore
    assert logstore.INTERVAL_S == 1.0
