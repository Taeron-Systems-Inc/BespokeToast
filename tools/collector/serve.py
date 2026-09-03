#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Receive run logs from the oven, and say something when a run finishes.

Deliberately small and dependency-free. It runs wherever is always on --
this project uses eridani -- and it does two of the things the oven cannot
do for itself: keep the archive somewhere that is backed up, and tell
someone a run has finished.

    python3 tools/collector/serve.py --dir ~/bespoketoast-runs

The oven POSTs a CSV with the filename in an X-Run-Log header. Anything
that is not a 2xx leaves the oven's copy in place, so a receiver that is
down or full costs nothing but a retry.
"""

import argparse
import datetime
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

SAFE = re.compile(r"[^A-Za-z0-9._-]")
MAX_BYTES = 4 * 1024 * 1024


def summarise(text):
    """Pull the header and trailer the oven writes into a one-line summary."""
    profile = started = summary = rows = None
    for line in text.splitlines():
        if line.startswith("# profile,"):
            profile = line.split(",", 1)[1]
        elif line.startswith("# started_at,"):
            started = line.split(",", 1)[1]
        elif line.startswith("# summary,"):
            summary = line.split(",", 1)[1]
        elif line.startswith("# rows,"):
            rows = line.split(",", 1)[1]
    parts = [p for p in (profile, started, summary,
                         ("%s rows" % rows) if rows else None) if p]
    return " | ".join(parts) if parts else "(no header)"


class Handler(BaseHTTPRequestHandler):
    directory = "."
    notify = None

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BYTES:
            self.send_error(413, "bad length")
            return
        name = self.headers.get("X-Run-Log") or "run.csv"
        name = SAFE.sub("_", os.path.basename(name))[:80]
        body = self.rfile.read(length)

        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(self.directory, "%s-%s" % (stamp, name))
        try:
            with open(path, "wb") as fh:
                fh.write(body)
        except OSError as e:
            # Refuse rather than pretend: a 2xx here would let the oven
            # mark the log sent and eventually evict its only copy.
            self.send_error(507, "cannot store: %s" % e)
            return

        text = body.decode("utf-8", "replace")
        line = summarise(text)
        faults = [l.split(",", 3)[-1] for l in text.splitlines()
                  if l.startswith("# event,") and
                  (",fault," in l or ",aborted," in l)]
        failed = [l.split(",", 3)[-1] for l in text.splitlines()
                  if l.startswith("# event,") and ",check," in l
                  and "FAILED" in l]
        if faults:
            line += " | FAULTED: " + "; ".join(faults[:2])
        if failed:
            line += " | checks FAILED: " + "; ".join(failed[:3])
        print("[%s] %s  <- %s" % (stamp, name, line), flush=True)
        if self.notify:
            try:
                subprocess.run([self.notify, name, line], timeout=30)
            except Exception as e:
                print("  notify failed: %r" % e, flush=True)

        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        try:
            names = sorted(os.listdir(self.directory))
        except OSError:
            names = []
        body = ("bespoketoast collector\n%d run(s) stored in %s\n\n%s\n"
                % (len(names), self.directory, "\n".join(names[-40:])))
        raw = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args):
        pass          # the POST handler already says what happened


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=os.path.expanduser("~/bespoketoast-runs"))
    ap.add_argument("--port", type=int, default=8788)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--notify", help="program run as: NOTIFY <name> <summary>")
    args = ap.parse_args()

    os.makedirs(args.dir, exist_ok=True)
    Handler.directory = args.dir
    Handler.notify = args.notify
    print("collecting runs into %s, listening on %s:%d"
          % (args.dir, args.host, args.port), flush=True)
    HTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    sys.exit(main())
