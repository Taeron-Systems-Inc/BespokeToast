# SPDX-License-Identifier: MIT
"""On-device run logs, oldest discarded first.

The previous firmware kept no record of any run it ever performed. Serial
telemetry fixed that only while a host was attached, which is exactly when it
is least needed -- a run started from the touchscreen with nobody watching is
the one whose record you want afterwards.

Each run is one CSV file with a metadata header. The store keeps writing new
runs until free space would drop below a reserve, then deletes the oldest
runs until it fits. Nothing here is a ring buffer over a fixed region: files
vary in length with the profile, so "how many runs fit" is not a constant and
pretending otherwise would either waste most of the flash or truncate a long
run. The reserve is what is held constant.

Every filesystem call is injected. That is not ceremony -- it means the
eviction logic, which deletes files, is exercised entirely off the board.

Failure here must never disturb a run. A full or read-only filesystem makes
logging stop and say so once; it does not raise into the control loop.
"""

import os as _os

HEADER_FIELDS = ("t", "target_c", "actual_c", "relay", "cold_c", "cpu_c")

# 1 Hz. The control loop runs at 4 Hz, but a reflow profile has no feature
# that moves faster than a second, and quartering the row count quadruples
# the history the flash holds.
INTERVAL_S = 1.0

DEFAULT_RESERVE_BYTES = 1000000


class LogStore(object):
    def __init__(self, root="/logs", reserve_bytes=DEFAULT_RESERVE_BYTES,
                 fs=None, on_warning=None):
        self.root = root
        self.reserve_bytes = reserve_bytes
        self.fs = fs or _RealFS()
        self._warn = on_warning or (lambda msg: print("# WARNING %s" % msg))
        self._file = None
        self._path = None
        self._rows = 0
        self._disabled = False
        self._last_write = None

    # -- lifecycle ---------------------------------------------------------

    def begin(self, profile_name, version, started_at, limits=None):
        """Open a log for a run. Returns the path, or None if unavailable."""
        if self._disabled:
            return None
        self.close()
        try:
            if not self.fs.exists(self.root):
                self.fs.mkdir(self.root)
            self._make_room()
            self._path = "%s/%s.csv" % (self.root, self._next_name(profile_name))
            self._file = self.fs.open(self._path, "w")
            self._file.write("# bespoketoast run log\n")
            self._file.write("# firmware,%s\n" % version)
            self._file.write("# profile,%s\n" % profile_name)
            self._file.write("# started_at,%s\n" % started_at)
            if limits:
                self._file.write("# limits,%s\n" % limits)
            self._file.write(",".join(HEADER_FIELDS) + "\n")
            self._rows = 0
            return self._path
        except Exception as e:
            self._fail("cannot open a run log (%r); this run will not be "
                       "recorded on the device" % e)
            return None

    def write(self, t, target_c, actual_c, relay, cold_c, cpu_c):
        """Append one sample. Rate limiting is the caller's business."""
        if self._file is None:
            return False
        try:
            self._file.write("%.1f,%s,%s,%d,%s,%s\n" % (
                t,
                "" if target_c is None else "%.2f" % target_c,
                "" if actual_c is None else "%.3f" % actual_c,
                1 if relay else 0,
                "" if cold_c is None else "%.2f" % cold_c,
                "" if cpu_c is None else "%.2f" % cpu_c))
            self._rows += 1
            # Flushed every 16 rows rather than every row: a run that loses
            # power keeps all but the last few seconds, and the flash sees a
            # sixteenth of the write cycles.
            if self._rows % 16 == 0:
                self._file.flush()
            return True
        except Exception as e:
            self._fail("run log write failed (%r); the rest of this run will "
                       "not be recorded" % e)
            return False

    def end(self, summary=None):
        if self._file is None:
            return
        try:
            if summary:
                self._file.write("# summary,%s\n" % summary)
            self._file.write("# rows,%d\n" % self._rows)
        except Exception as e:
            # The samples are already on the flash; only the trailer is lost,
            # so this is worth a word rather than an abort.
            self._warn("could not write the run log trailer (%r)" % e)
        if not self.close():
            self._warn("the run log did not close cleanly; the last few "
                       "samples may be missing")

    def close(self):
        """Close the open log. Returns False if it did not close cleanly."""
        if self._file is None:
            return True
        handle, self._file = self._file, None
        try:
            handle.flush()
            handle.close()
        except Exception:
            return False
        return True

    # -- housekeeping ------------------------------------------------------

    def runs(self):
        """Existing logs, oldest first.

        Ordered by the sequence number in the name, not by mtime: the board
        has no clock until it has been told the time, so every file written
        before then shares one timestamp.
        """
        try:
            names = [n for n in self.fs.listdir(self.root)
                     if ".csv" in n]
        except Exception:
            return []
        return sorted(names, key=_sequence_of)

    def read(self, name):
        """A stored run's bytes, or None. Used by the uploader."""
        try:
            with self.fs.open("%s/%s" % (self.root, name), "r") as f:
                return f.read()
        except Exception as e:
            self._warn("cannot read run log %s (%r)" % (name, e))
            return None

    def mark_sent(self, name):
        """Rename a log to record that it has been handed over.

        A rename rather than an index: an index is a second thing to keep
        consistent with the directory, and it is what will be wrong after a
        power cut halfway through a write.
        """
        from oven.uploader import sent_name
        try:
            self.fs.rename("%s/%s" % (self.root, name),
                           "%s/%s" % (self.root, sent_name(name)))
            return True
        except Exception as e:
            self._warn("could not mark %s as sent (%r); it will be uploaded "
                       "again" % (name, e))
            return False

    def free_bytes(self):
        try:
            return self.fs.free_bytes()
        except Exception:
            return None

    def _make_room(self):
        """Delete oldest runs until the reserve is satisfied.

        The reserve exists because CircuitPython needs writable space for
        more than logs -- a filesystem with nothing spare is one that cannot
        take a firmware update.
        """
        free = self.free_bytes()
        if free is None:
            return
        removed = []
        # Already-uploaded runs first: they exist somewhere else, and one
        # that has not been handed over may be the only copy there is.
        # Oldest first within each group.
        from oven.uploader import SENT_SUFFIX
        ordered = ([n for n in self.runs() if n.endswith(SENT_SUFFIX)]
                   + [n for n in self.runs() if not n.endswith(SENT_SUFFIX)])
        for name in ordered:
            if free >= self.reserve_bytes:
                break
            path = "%s/%s" % (self.root, name)
            try:
                size = self.fs.size(path)
                self.fs.remove(path)
                removed.append(name)
                free += size
            except Exception as e:
                self._warn("could not discard old run log %s (%r); keeping "
                           "it and stopping here" % (name, e))
                break
        if removed:
            self._warn("run log full: discarded %d oldest run(s) to stay "
                       "above the %d-byte reserve (%s)"
                       % (len(removed), self.reserve_bytes,
                          ", ".join(removed)))

    def _next_name(self, profile_name):
        seq = 0
        for name in self.runs():
            seq = max(seq, _sequence_of(name))
        # Collapse runs of separators: "SAC305 (this oven)" should become
        # 0008-SAC305-this-oven.csv, not 0008-SAC305--this-oven-.csv.
        safe = ""
        for c in profile_name:
            if c.isalpha() or c.isdigit():
                safe += c
            elif not safe.endswith("-"):
                safe += "-"
        return "%04d-%s" % (seq + 1, safe.strip("-")[:24] or "run")

    def _fail(self, message):
        self.close()
        if not self._disabled:
            self._warn(message)
        self._disabled = True


def _sequence_of(name):
    head = name.split("-", 1)[0]
    try:
        return int(head)
    except ValueError:
        return 0


class _RealFS(object):
    def exists(self, path):
        try:
            _os.stat(path)
            return True
        except OSError:
            return False

    def listdir(self, path):
        return _os.listdir(path)

    def mkdir(self, path):
        _os.mkdir(path)

    def remove(self, path):
        _os.remove(path)

    def size(self, path):
        return _os.stat(path)[6]

    def open(self, path, mode):
        return open(path, mode)

    def rename(self, old, new):
        _os.rename(old, new)

    def free_bytes(self):
        st = _os.statvfs("/")
        return st[0] * st[3]             # f_bsize * f_bavail
