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


def _row(name, size):
    return ("<tr><td><a href='/logs/%s'>%s</a></td>"
            "<td class='n'>%s</td></tr>"
            % (_html_escape(name), _html_escape(name),
               "" if size is None else "%d" % size))


def index_page(status, runs, profiles):
    """The one page. Deliberately plain: it is read on a phone at a bench.

    Built by concatenation rather than a format string -- the stylesheet is
    full of per-cent signs and every one of them is a formatting trap.
    """
    rows = "".join(_row(n, s) for n, s in runs) or \
        "<tr><td colspan=2 class='q'>no runs recorded yet</td></tr>"
    opts = "".join("<li>" + _html_escape(p) +
                   (" &mdash; selected" if sel else "") + "</li>"
                   for p, sel in profiles) or "<li>none</li>"
    style = (
        "body{font:16px/1.5 system-ui,sans-serif;margin:0;padding:20px;"
        "background:#14161a;color:#eceae3}"
        "h1{font-size:20px;margin:0 0 4px}"
        "h2{font-size:13px;letter-spacing:.1em;text-transform:uppercase;"
        "color:#9aa1a9;margin:28px 0 8px}"
        "table{border-collapse:collapse;width:100%;max-width:640px}"
        "td{padding:8px 10px 8px 0;border-bottom:1px solid #2e333a}"
        "td.n{text-align:right;font-variant-numeric:tabular-nums;color:#9aa1a9}"
        ".q{color:#9aa1a9}a{color:#c1d72e}"
        "ul{margin:0;padding-left:18px;color:#9aa1a9}"
        ".s{color:#9aa1a9;font-size:14px}")
    return ("<!doctype html><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>BespokeToast</title><style>" + style + "</style>"
            "<h1>BespokeToast</h1>"
            "<div class=s>" + _html_escape(status) + "</div>"
            "<h2>Runs</h2><table>" + rows + "</table>"
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
