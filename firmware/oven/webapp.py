# SPDX-License-Identifier: MIT
"""The pages the oven serves, and nothing that needs a radio.

The oven is the only machine present in normal operation: USB is power-only
behind a panel, and the network it sits on does not reach the machine that
builds its firmware. So anything anyone wants off it has to come from the
oven itself, over a browser, while it is idle.

Routing, rendering and validation are decisions and live here, testable on
a host. The socket belongs to the co-processor's own server and is wired up
in code.py.

TWO THINGS THIS DELIBERATELY CANNOT DO. It cannot start a run, and it
cannot change a safety limit. Remote start was excluded when the network
features were agreed, and nothing here reopens it -- a run begins by a
person pressing START at the oven, having looked inside it.
"""

MAX_PROFILE_BYTES = 8192
CHUNK = 512


def _html_escape(text):
    out = str(text)
    for bad, good in (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"),
                      ('"', "&quot;")):
        out = out.replace(bad, good)
    return out


SENT = ".sent"


def display_name(name):
    """The filename with the uploader's bookkeeping taken off.

    A log that has been handed to an archive is renamed to end .sent so
    that the eviction order can prefer it. That is a fact about this
    oven's housekeeping and means nothing to whoever is fetching the run,
    so it does not belong on the page. The link still points at the real
    name.
    """
    return name[:-len(SENT)] if name.endswith(SENT) else name


def split_started_at(started_at):
    """(date, time) from an ISO stamp, or ("", "") if there is not one.

    The stored form uses dashes where a time would have colons, because it
    also has to be a filename on FAT. Undo that for reading.
    """
    if not started_at or "T" not in started_at:
        return ("", "")
    day, _, rest = started_at.partition("T")
    rest = rest.rstrip("Z")
    return (day, rest.replace("-", ":"))


def human_size(size):
    """Bytes as something a person reads at a glance."""
    if size is None:
        return ""
    if size < 1024:
        return "%d B" % size
    return "%.1f kB" % (size / 1024.0)


def run_label(name):
    """What to call a run whose start time cannot be read.

    Happens for real, not just to old files: the clock comes from the
    network, so the first run after a power cut is written by a board that
    does not yet know the date, and begin() records "monotonic+40" rather
    than inventing one. The sequence number is then the only honest handle
    on it, and it is still what the file is called.
    """
    digits = ""
    for ch in name:
        if not ch.isdigit():
            break
        digits += ch
    return ("run " + digits) if digits else display_name(name)


def _row(run):
    """One run. *run* is (name, size, started_at, profile)."""
    name, size, started_at, profile = run
    day, clock = split_started_at(started_at)
    return ("<tr><td><a href='/logs/%s'>%s</a></td><td>%s</td>"
            "<td>%s</td><td class='n'>%s</td></tr>"
            % (_html_escape(display_name(name)),
               _html_escape(day or run_label(name)),
               _html_escape(clock),
               _html_escape(profile or ""),
               _html_escape(human_size(size))))


def index_page(runs, profiles, warning=None):
    """The one page. Deliberately plain: it is read on a phone at a bench.

    No state and no selected profile at the top. Both were there and both
    were removed: this page only ever serves while the oven is idle, so
    "idle" told nobody anything, and the selected profile cannot be
    changed or started from here, so it was decoration.

    Built by concatenation rather than a format string -- the stylesheet is
    full of per-cent signs and every one of them is a formatting trap.
    """
    rows = "".join(_row(r) for r in runs) or \
        "<tr><td colspan=4 class='q'>no runs recorded yet</td></tr>"
    opts = "".join("<li>" + _html_escape(p) + "</li>" for p in profiles) \
        or "<li>none</li>"
    style = (
        "body{font:16px/1.5 system-ui,sans-serif;margin:0;padding:20px;"
        "background:#14161a;color:#eceae3}"
        "h1{font-size:20px;margin:0 0 20px}"
        "h2{font-size:13px;letter-spacing:.1em;text-transform:uppercase;"
        "color:#9aa1a9;margin:28px 0 8px}"
        "table{border-collapse:collapse;width:100%;max-width:640px}"
        "th{text-align:left;font:600 12px/1.5 system-ui,sans-serif;"
        "letter-spacing:.06em;text-transform:uppercase;color:#9aa1a9;"
        "padding:0 10px 6px 0;border-bottom:1px solid #2e333a}"
        "th.n{text-align:right}"
        "td{padding:8px 10px 8px 0;border-bottom:1px solid #2e333a}"
        "td.n{text-align:right;font-variant-numeric:tabular-nums;color:#9aa1a9}"
        ".q{color:#9aa1a9}a{color:#c1d72e}"
        "ul{margin:0;padding-left:18px;color:#9aa1a9}"
        ".s{color:#9aa1a9;font-size:14px}"
        ".w{color:#ffb000;font-size:14px;margin:0 0 16px}")
    return ("<!doctype html><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>Taeron Reflow Oven</title><style>" + style + "</style>"
            "<h1>Taeron Reflow Oven</h1>"
            + ("<div class=w>" + _html_escape(warning) + "</div>"
               if warning else "")
            + "<h2>Runs</h2><table>"
            "<tr><th>Date</th><th>Time</th><th>Profile</th>"
            "<th class=n>Size</th></tr>" + rows + "</table>"
            "<h2>Profiles</h2><ul>" + opts + "</ul>"
            "<h2>Note</h2><div class=s>A run is started at the oven, by "
            "someone who has looked inside it. This page cannot start "
            "one.</div>")


def route(method, path):
    """(kind, argument). Kept separate from doing so it can be tested."""
    if method not in ("GET", "HEAD", "POST"):
        return ("bad-method", method)
    if path in ("/", "/index.html"):
        return ("index", None)
    if path == "/logs":
        return ("index", None)
    if path.startswith("/logs/"):
        name = path[len("/logs/"):]
        if not name or "/" in name or ".." in name:
            return ("bad-name", name)
        return ("log", name)
    if path == "/profiles" and method == "POST":
        return ("put-profile", None)
    if path == "/status":
        return ("status", None)
    return ("not-found", path)


def safe_log_name(name, known):
    """The stored file a request is for, or None.

    Requests arrive under the name the page offered, which is the storage
    name with the uploader's .sent bookkeeping taken off, so this has to
    map back. Still matching against the real listing rather than
    sanitising a string: the set of legitimate names is known, so there is
    no reason to guess at what an attacker might have meant.
    """
    if name in known:
        return name
    for stored in known:
        if display_name(stored) == name:
            return stored
    return None
