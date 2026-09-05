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


class FakeReader(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def read(self, size=None):
        if size is None:
            return self.text
        piece = self.text[self.pos:self.pos + size]
        self.pos += len(piece)
        return piece

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


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

    def open(self, path, mode="r"):
        if mode == "r":
            if path not in self.files:
                raise OSError(2, "No such file")
            return FakeReader(self.files[path])
        if self.readonly:
            raise OSError(30, "Read-only filesystem")
        self.files[path] = ""
        return FakeFile(self, path)

    def rename(self, old, new):
        if self.readonly:
            raise OSError(30, "Read-only filesystem")
        self.files[new] = self.files.pop(old)

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



def test_a_stored_run_can_be_read_back_for_upload():
    store, fs, _ = make()
    path = store.begin("p", "v", "t")
    store.write(0.0, 25.0, 24.9, False, 30.0, 34.0)
    store.end(summary="peak=100")
    body = store.read(path.rsplit("/", 1)[-1])
    assert body is not None
    assert "peak=100" in body
    assert "24.900" in body


def test_reading_a_missing_run_reports_rather_than_raises():
    store, fs, warnings = make()
    assert store.read("nope.csv") is None
    assert warnings


def test_marking_sent_removes_it_from_pending_without_touching_the_file():
    from oven.uploader import pending
    store, fs, _ = make()
    path = store.begin("p", "v", "t")
    store.write(0.0, 1.0, 1.0, False, 1.0, 1.0)
    store.end()
    name = path.rsplit("/", 1)[-1]
    assert pending(store.runs(), store.sent()) == [name]
    assert store.mark_sent(name) is True
    assert pending(store.runs(), store.sent()) == []
    assert name in store.runs(), "the file itself must not be renamed"
    assert store.sent() == set([name])


def test_an_index_that_cannot_be_written_leaves_the_log_pending():
    """Better uploaded twice than marked sent and later evicted."""
    from oven.uploader import pending
    store, fs, warnings = make()
    path = store.begin("p", "v", "t")
    store.write(0.0, 1.0, 1.0, False, 1.0, 1.0)
    store.end()
    name = path.rsplit("/", 1)[-1]
    fs.readonly = True
    assert store.mark_sent(name) is False
    assert pending(store.runs(), store.sent()) == [name]
    assert warnings



def test_eviction_is_oldest_first_and_nothing_cleverer():
    """Preferring already-uploaded runs coupled the store to the uploader
    for a preference that only differs when the disk is full AND an
    archive exists AND the oldest run is the unsent one."""
    fs = FakeFS(free=1000)
    store, fs, warnings = make(fs=fs, reserve_bytes=5000)
    fs.files["/logs/0001-old.csv"] = "x" * 2000
    fs.files["/logs/0002-old.csv"] = "x" * 2000
    fs.files["/logs/0003-old.csv"] = "x" * 2000
    store.begin("new", "v", "t")
    assert fs.removed[0] == "/logs/0001-old.csv", (
        "evicted %s, which is not the oldest" % fs.removed[0])


def test_the_sent_index_is_not_mistaken_for_a_run():
    """It lives in the same directory, so runs() has to step over it."""
    from oven.logstore import SENT_INDEX
    store, fs, _ = make()
    fs.files["/logs/0001-a.csv"] = "x"
    fs.files["/logs/0002-b.csv"] = "x"
    fs.files["/logs/" + SENT_INDEX] = "0002-b.csv\n"
    assert store.runs() == ["0001-a.csv", "0002-b.csv"]
    assert store.sent() == set(["0002-b.csv"])


def test_events_are_recorded_in_line_with_the_samples():
    """A log that stops without saying why looks like a power cut."""
    store, fs, _ = make()
    path = store.begin("p", "v", "t")
    store.write(0.0, 25.0, 24.9, False, 30.0, 34.0)
    store.event(1.5, "fault", "over temperature: 262.3 C exceeds 260.0 C")
    store.write(2.0, 26.0, 25.5, True, 30.0, 34.0)
    store.end()
    lines = fs.files[path].splitlines()
    idx = [i for i, l in enumerate(lines) if l.startswith("# event,")]
    assert len(idx) == 1
    assert "over temperature" in lines[idx[0]]
    # in time order, between the samples either side of it
    assert lines[idx[0] - 1].startswith("0.0,")
    assert lines[idx[0] + 1].startswith("2.0,")


def test_an_event_is_a_comment_so_csv_readers_skip_it():
    store, fs, _ = make()
    path = store.begin("p", "v", "t")
    store.event(1.0, "aborted", "")
    body = fs.files[path]
    data = [l for l in body.splitlines()
            if l and not l.startswith("#") and not l.startswith("t,")]
    assert data == []


def test_newlines_in_a_detail_cannot_break_the_format():
    store, fs, _ = make()
    path = store.begin("p", "v", "t")
    store.event(1.0, "fault", "line one\nline two\rline three")
    events = [l for l in fs.files[path].splitlines() if l.startswith("# event")]
    assert len(events) == 1
    assert "line one line two line three" in events[0]


def test_an_event_before_a_run_is_ignored_not_raised():
    store, fs, _ = make()
    assert store.event(0.0, "fault", "no run open") is False


def test_a_run_is_streamed_in_pieces_not_read_whole():
    """Reading a 26 kB log into memory failed with MemoryError.

    The heap has a few thousand bytes in its largest hole once the radio is
    up, so the file has to go to the socket in pieces and never exist as a
    single object.
    """
    store, fs, _ = make()
    path = store.begin("p", "v", "t")
    for i in range(200):
        store.write(float(i), 25.0 + i, 24.0 + i, i % 2 == 0, 30.0, 34.0)
    store.end()
    name = path.rsplit("/", 1)[-1]

    size = store.size(name)
    assert size == len(fs.files[path])

    pieces = list(store.chunks(name, size=64))
    assert len(pieces) > 20, "should have been split into many pieces"
    assert max(len(p) for p in pieces) <= 64
    assert "".join(pieces) == fs.files[path], "streaming lost or reordered data"


def test_streaming_a_missing_run_yields_nothing_and_reports():
    store, fs, warnings = make()
    assert list(store.chunks("nope.csv")) == []
    assert warnings


def test_the_streamed_length_matches_what_the_header_will_claim():
    """A Content-Length that disagrees with the body hangs the receiver."""
    from oven.uploader import request_head
    store, fs, _ = make()
    path = store.begin("p", "v", "t")
    for i in range(50):
        store.write(float(i), 25.0, 24.0, False, 30.0, 34.0)
    store.end()
    name = path.rsplit("/", 1)[-1]
    length = store.size(name)
    streamed = sum(len(p) for p in store.chunks(name, size=100))
    assert streamed == length
    head = request_head("h", "/runs", name, length, 8788).decode()
    assert "Content-Length: %d\r\n" % streamed in head
