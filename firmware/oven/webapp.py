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


from oven import pacific

UNKNOWN = "?"


def run_id(name):
    """The leading sequence number, which is what a run is called.

    Short, unique, and already how the log store names its files, so it
    is what the page uses as the handle rather than a filename nobody
    needs to read.
    """
    digits = ""
    for ch in name:
        if not ch.isdigit():
            break
        digits += ch
    return digits or name


def when(started_at):
    """(date, time) in Pacific, or ("?", "?").

    A question mark rather than a blank or a guess: a run written before
    the oven had been told the date carries "monotonic+40" in its header,
    which happens to the first run after every power cut, and pretending
    to know is worse than saying it does not.
    """
    got = pacific.local(started_at)
    if got is None:
        return (UNKNOWN, UNKNOWN)
    return (got[0], got[1])


def human_size(size):
    """Bytes as something a person reads at a glance."""
    if size is None:
        return UNKNOWN
    if size < 1024:
        return "%d B" % size
    return "%.1f kB" % (size / 1024.0)


def _row(run):
    """One run. *run* is (name, size, started_at, profile)."""
    name, size, started_at, profile = run
    day, clock = when(started_at)
    return ("<tr><td><a href='/logs/%s'>%s</a></td><td>%s</td><td>%s</td>"
            "<td>%s</td><td class='n'>%s</td></tr>"
            % (_html_escape(name), _html_escape(run_id(name)),
               _html_escape(day), _html_escape(clock),
               _html_escape(profile or UNKNOWN),
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
        "<tr><td colspan=5 class='q'>no runs recorded yet</td></tr>"
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
            "<tr><th>Run</th><th>Date</th><th>Time (PT)</th><th>Profile</th>"
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
    """A name is only served if the store already lists it.

    Matching against the real listing rather than sanitising a string: the
    set of legitimate names is known, so there is no reason to guess at
    what an attacker might have meant.
    """
    return name if name in known else None
