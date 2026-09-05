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

# A transport limit, not a policy one, and measured rather than reasoned
# from the co-processor's 4000-byte socket buffer -- that guess was wrong
# twice. Against the real oven, one profile at a time:
#
#     up to 2700 bytes   200, about 1.5 s
#     3000 bytes         400: the body arrives truncated
#     3200 and above     no reply at all
#
# Past that the WSGI server holds a half-read request and keeps accepting
# connections it never answers; the page is dead until the firmware
# restarts. The oven itself is untouched by this -- idle, relay down,
# telemetry unbroken throughout every one of those attempts -- but the
# page does not come back on its own.
#
# Nothing here can prevent it, because the server reads the request before
# the application is called. So the limit sits under the measured cliff,
# the form refuses to send anything larger, and every profile that ships
# fits underneath.
MAX_PROFILE_BYTES = 2560
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


_STYLE = (
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
    ".w{color:#ffb000;font-size:14px;margin:0 0 16px}"
    ".up{display:flex;flex-direction:column;gap:10px;max-width:640px}"
    "textarea{width:100%;background:#101216;color:#eceae3;"
    "border:1px solid #2e333a;border-radius:3px;padding:8px;"
    "font:13px/1.5 ui-monospace,monospace}"
    "button{background:#c1d72e;color:#14161a;border:0;border-radius:3px;"
    "padding:10px 16px;font:600 15px system-ui,sans-serif;cursor:pointer}"
    "button:disabled{opacity:.5}"
    "input[type=file]{color:#9aa1a9;font-size:14px}")


PROFILE_DIR = "/profiles"
_SAFE = "abcdefghijklmnopqrstuvwxyz0123456789-"


def profile_filename(name):
    """A filename for an uploaded profile, or None if nothing survives.

    Built from the profile's own name rather than taken from the request,
    so there is no path in it to escape with. Anything outside the safe
    set becomes a hyphen, which also means two names that differ only in
    punctuation land on the same file -- that is a replace, and replacing
    is the point of being able to upload one.
    """
    out = []
    for ch in str(name).lower():
        c = ch if ch in _SAFE else "-"
        if c == "-" and (not out or out[-1] == "-"):
            continue
        out.append(c)
    slug = "".join(out).strip("-")
    if not slug:
        return None
    return slug[:40] + ".json"


def accept_profile(body, loader):
    """(filename, cleaned_dict, warnings) for an upload, or (None, None, why).

    *loader* parses and validates -- it is oven.profile.Profile.from_dict
    in the firmware and a fake in the tests, so this stays host-testable
    without dragging the profile machinery in.

    Two fields are stripped rather than honoured. A profile arriving over
    the network must not make itself the selection, because nobody at the
    oven asked it to; and it must not declare itself diagnostic, because
    that would hide it from the list it was just added to.
    """
    if body is None or not str(body).strip():
        return (None, None, "the request had no body")
    if len(body) > MAX_PROFILE_BYTES:
        return (None, None,
                "profile is %d bytes; the limit is %d"
                % (len(body), MAX_PROFILE_BYTES))
    try:
        import json
        data = json.loads(body)
    except Exception as e:
        return (None, None, "not valid JSON (%s)" % e)
    if not isinstance(data, dict):
        return (None, None, "a profile must be a JSON object")
    data.pop("default", None)
    data.pop("diagnostic", None)
    try:
        parsed = loader(data)
    except Exception as e:
        return (None, None, "rejected: %s" % e)
    filename = profile_filename(data.get("name", ""))
    if filename is None:
        return (None, None, "the profile needs a name with letters in it")
    try:
        warnings = list(parsed.warnings())
    except Exception as e:
        # The profile is valid -- it loaded. Only the advisory pass over it
        # failed, and saying so beats an empty list, which reads like a
        # clean bill of health.
        return (filename, data,
                ["could not check this profile for warnings (%s)" % e])
    return (filename, data, warnings)


def result_page(heading, detail, warnings=(), ok=True):
    """What the browser gets back after an upload."""
    items = "".join("<li>" + _html_escape(w) + "</li>" for w in warnings)
    return ("<!doctype html><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>Taeron Reflow Oven</title><style>" + _STYLE + "</style>"
            "<h1>Taeron Reflow Oven</h1>"
            "<h2>" + _html_escape(heading) + "</h2>"
            "<div class=" + ("s" if ok else "w") + ">"
            + _html_escape(detail) + "</div>"
            + ("<h2>Worth knowing</h2><ul>" + items + "</ul>" if items else "")
            + "<div class=s style='margin-top:24px'>"
            "<a href='/'>Back to the oven</a></div>")


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
    return ("<!doctype html><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>Taeron Reflow Oven</title><style>" + _STYLE + "</style>"
            "<h1>Taeron Reflow Oven</h1>"
            + ("<div class=w>" + _html_escape(warning) + "</div>"
               if warning else "")
            + "<h2>Runs</h2><table>"
            "<tr><th>Run</th><th>Date</th><th>Time (PT)</th><th>Profile</th>"
            "<th class=n>Size</th></tr>" + rows + "</table>"
            "<h2>Profiles</h2><ul>" + opts + "</ul>"
            + _UPLOAD
            + "<h2>Note</h2><div class=s>A run is started at the oven, by "
            "someone who has looked inside it. This page cannot start "
            "one.</div>")


_UPLOAD = (
    "<h2>Add or replace a profile</h2>"
    "<div class=s>A JSON profile, under 2.5 kB. It is checked before it is "
    "kept, and one that arrives this way never becomes the selected "
    "profile -- somebody picks that at the oven.</div>"
    "<div class=up>"
    "<input type=file id=f accept='.json,application/json'>"
    "<textarea id=t rows=6 placeholder='or paste the profile here'></textarea>"
    "<button id=b type=button>Send to the oven</button>"
    "<div id=m class=s></div>"
    "</div>"
    "<script>"
    "var f=document.getElementById('f'),t=document.getElementById('t'),"
    "b=document.getElementById('b'),m=document.getElementById('m');"
    "f.addEventListener('change',function(){"
    "var r=new FileReader();r.onload=function(){t.value=r.result};"
    "if(f.files[0])r.readAsText(f.files[0])});"
    "b.addEventListener('click',function(){"
    "var body=t.value.trim();"
    "if(!body){m.textContent='Nothing to send yet.';return}"
    "if(body.length>2560){m.textContent='That is '+body.length+' bytes. "
    "The oven can only take 2560, and sending more stops it answering "
    "until it is restarted.';return}"
    "b.disabled=true;m.textContent='Sending...';"
    "fetch('/profiles',{method:'POST',body:body})"
    ".then(function(r){return r.text()})"
    ".then(function(h){document.open();document.write(h);document.close()})"
    ".catch(function(e){b.disabled=false;m.textContent="
    "'Did not reach the oven: '+e})});"
    "</script>")


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
