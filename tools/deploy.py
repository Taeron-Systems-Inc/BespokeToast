#!/usr/bin/env python3
"""Deploy firmware/ to the PyPortal's CIRCUITPY volume.

Refuses to deploy while the oven is running. Writing any file to CIRCUITPY
triggers CircuitPython's auto-reload, which restarts the controller
mid-profile -- with a relay that fails safe, that means the heat stops and
the board is half-soldered, which is a wasted board rather than a fire, but
it is still not something to do by accident.

  python3 tools/deploy.py /mnt/circuitpy            # copy, then verify
  python3 tools/deploy.py /mnt/circuitpy --dry-run
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "firmware")
CHARACTERISATION = os.path.join(ROOT, "data", "oven-characterisation.json")

SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIX = (".pyc",)


def digest(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def files():
    for base, dirs, names in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in sorted(names):
            if n.endswith(SKIP_SUFFIX):
                continue
            full = os.path.join(base, n)
            yield full, os.path.relpath(full, SRC)


def running_check(dest):
    """A best-effort look at whether a run is in progress."""
    marker = os.path.join(dest, "RUNNING")
    if os.path.exists(marker):
        return "the device reports a run in progress (%s exists)" % marker
    return None


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    dest = argv[1]
    dry = "--dry-run" in argv

    if not os.path.isdir(dest):
        print("!! %s is not mounted" % dest)
        return 1
    if not dry and not os.access(dest, os.W_OK):
        print("!! %s is read-only. Remount it writable to deploy." % dest)
        return 1

    blocked = running_check(dest)
    if blocked:
        print("!! refusing to deploy: %s" % blocked)
        return 1

    planned = list(files())
    if os.path.exists(CHARACTERISATION):
        planned.append((CHARACTERISATION, "characterisation.json"))

    changed = []
    for src, rel in planned:
        dst = os.path.join(dest, rel)
        if not os.path.exists(dst) or digest(src) != digest(dst):
            changed.append((src, rel))

    print("  %d files, %d changed" % (len(planned), len(changed)))
    for _, rel in changed:
        print("    %s" % rel)
    if dry:
        print("  (dry run, nothing written)")
        return 0
    if not changed:
        print("  nothing to do")
        return 0

    for src, rel in changed:
        dst = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    bad = [rel for src, rel in changed
           if digest(src) != digest(os.path.join(dest, rel))]
    if bad:
        print("!! verification failed for: %s" % ", ".join(bad))
        return 1
    print("  deployed and verified; the board will auto-reload")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
