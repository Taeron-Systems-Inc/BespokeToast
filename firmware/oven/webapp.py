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
from oven import timesync

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

    Takes either form the header has ever used: seconds since the epoch,
    which is what it writes now, or the ISO stamp it wrote before
    2026-09-08. Reading only the older one is how ten of the fifteen runs
    on this oven came to show "?" for their date -- the header was improved
    and the page was not told, and nothing failed, it just quietly stopped
    knowing when anything happened.

    A question mark rather than a blank or a guess: a run written before
    the oven had been told the date carries "monotonic+40" in its header,
    which happens to the first run after every power cut, and pretending to
    know is worse than saying it does not.
    """
    if started_at is None:
        return (UNKNOWN, UNKNOWN)
    got = None
    text = str(started_at).strip()
    # Range-checked rather than wrapped in a try: timesync.looks_set is the
    # same test the radio puts a fetched time through, so a number that is
    # seconds-since-boot rather than a date is rejected here for the same
    # reason and by the same rule.
    if text.isdigit() and timesync.looks_set(int(text)):
        got = pacific.local_from_epoch(int(text))
    if got is None:
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


# Split in two for the same reason the page is served in pieces at all:
# every piece is encoded to bytes on the way out, so a piece is a contiguous
# allocation. The stylesheet grew past 1.5 kB when the profile format table
# was added, on a board measured at 1760 bytes largest free block after a
# day of runs. Two pieces of 800 always fit where one of 1500 sometimes
# does not.
_STYLE_A = (
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
    ".q{color:#9aa1a9}a{color:#c1d72e}")

_STYLE_B = (
    # The field table is reference, not results: smaller, quieter, and the
    # first column is the JSON key so it is set like one.
    "table.f{font-size:14px;margin:8px 0 12px}"
    "table.f td{padding:6px 12px 6px 0;vertical-align:top;color:#9aa1a9}"
    "table.f td:first-child{color:#eceae3;font-family:ui-monospace,monospace;"
    "white-space:nowrap}"
    "code{font-family:ui-monospace,monospace;font-size:13px;color:#c1d72e}"
    "button.alt{background:0;color:#c1d72e;border:1px solid #2e333a;"
    "font-weight:400}"
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

# The profile list's own rules, a third piece rather than growing the second.
_STYLE_C = (
    ".p{max-width:640px;margin:0 0 18px;padding:10px 12px;"
    "border:1px solid #2e333a;border-radius:3px}"
    ".p.ar{opacity:.7}"
    ".a{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;"
    "margin:8px 0 0;font-size:14px}"
    ".a button,.p td button{padding:5px 10px;font-size:14px}"
    "button.del{background:#8a2b22;color:#eceae3}"
    ".tag{color:#ffb000;font-size:13px;margin-left:8px}")


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
            "<title>Taeron Reflow Oven</title><style>" + _STYLE_A + _STYLE_B
            + _STYLE_C + "</style>"
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


def index_parts(runs, profiles, warning=None):
    """The page in pieces, smallest allocation first.

    Returned as a list rather than one string because one string is what
    broke it: with the upload form the page reached 3.4 kB, and building
    it asked the heap for a single 3304-byte block it could not always
    find. The service caught the MemoryError, stopped, restarted, and the
    page answered one request in four. The log download has streamed in
    512-byte pieces since it hit the same wall; this is the same fix.

    No state and no selected profile at the top. Both were there and both
    were removed: this page only ever serves while the oven is idle, so
    "idle" told nobody anything, and the selected profile cannot be
    changed or started from here, so it was decoration.
    """
    out = ["<!doctype html><meta charset=utf-8>"
           "<meta name=viewport content='width=device-width,initial-scale=1'>"
           "<title>Taeron Reflow Oven</title><style>", _STYLE_A, _STYLE_B,
           _STYLE_C, "</style><h1>Taeron Reflow Oven</h1>"]
    if warning:
        out.append("<div class=w>" + _html_escape(warning) + "</div>")
    out.append("<h2>Runs</h2><table>"
               "<tr><th>Run</th><th>Date</th><th>Time (PT)</th>"
               "<th>Profile</th><th class=n>Size</th></tr>")
    if runs:
        for r in runs:
            out.append(_row(r))
    else:
        out.append("<tr><td colspan=5 class='q'>no runs recorded yet</td></tr>")
    out.append("</table><h2>Profiles</h2>"
               "<div class=s>Open one to see exactly what a profile looks "
               "like -- it is the same format the box below takes. The "
               "newest version of each is the one the oven runs. Archived "
               "profiles are kept here but not offered at the oven. Delete "
               "stays greyed out until you have downloaded, from this page, "
               "what it would delete.</div>")
    managed = False
    plain = []
    for entry in profiles:
        # A bare name, (name, filename), or a full entry from
        # profile_entry(). The filename is what makes the entry a link to
        # the real thing, which is the only format documentation that
        # cannot go stale.
        if isinstance(entry, (tuple, list)) and len(entry) >= 4:
            managed = True
            out.extend(_profile_block(*entry))
            continue
        if isinstance(entry, (tuple, list)):
            name, filename = entry[0], (entry[1] if len(entry) > 1 else None)
        else:
            name, filename = entry, None
        if filename:
            plain.append("<li><a href='/profiles/%s'>%s</a></li>"
                         % (_html_escape(filename), _html_escape(name)))
        else:
            plain.append("<li>" + _html_escape(name) + "</li>")
    if plain or not profiles:
        out.append("<ul>")
        out.extend(plain or ["<li>none</li>"])
        out.append("</ul>")
    if managed:
        out.extend(_MANAGE)
    out.extend(_UPLOAD)
    return out


def profile_entry(name, stem, archived, versions):
    """What index_parts takes for one managed profile.

    *versions* is [(version, filename), ...], oldest first; the last one
    is the newest, which is the one the oven runs.
    """
    return (name, stem, bool(archived), list(versions))


def _profile_block(name, stem, archived, versions):
    """One profile, in pieces: a heading and then one piece per version,
    so a profile with many versions never becomes one large string."""
    st = _html_escape(stem)
    nm = _html_escape(name)
    yield ("<div class='p%s'><b>%s</b>%s<div class=a>"
           "<button type=button class=alt data-x=%s data-s='%s'>%s</button>"
           "<a download href='/bundles/%s.json' data-g='%s'>Download all "
           "versions</a>"
           "<button type=button class=del disabled data-x=delete-profile "
           "data-s='%s' data-k='%s' data-n='%s, every version,'>Delete "
           "profile</button></div>"
           "<table class=f><tr><th>version</th><th></th><th></th></tr>"
           % (" ar" if archived else "", nm,
              "<span class=tag>archived -- not offered at the oven</span>"
              if archived else "",
              "unarchive" if archived else "archive", st,
              "Unarchive" if archived else "Archive",
              st, st, st, st, nm))
    newest = versions[-1][0] if versions else None
    for version, filename in versions:
        fn = _html_escape(filename)
        yield ("<tr><td><a href='/profiles/%s'>v%d</a>%s</td>"
               "<td><a download href='/profiles/%s' data-g='%s' "
               "data-v='%s'>download</a></td>"
               "<td><button type=button class=del disabled "
               "data-x=delete-version data-s='%s' data-k='%s' data-v='%s' "
               "data-n='%s v%d'>delete</button></td></tr>"
               % (fn, version,
                  (" <span class=q>newest%s</span>"
                   % ("" if archived else ", runs at the oven"))
                  if version == newest else "",
                  fn, st, fn, fn, st, fn, nm, version))
    yield "</table></div>"


# Downloading is what unlocks a delete. A version's own download unlocks
# that version; the bundle holds every version, so it unlocks all of them
# and the profile as a whole. Enforced by the page only, as agreed: the
# routes behind the buttons do not check, and like every other change this
# page makes they are only served while the oven is idle.
_MANAGE = (
    "<script>"
    "document.addEventListener('click',function(e){"
    "var x=e.target,d=x.dataset||{},i,bs;"
    "if(d.g!==undefined){"
    "bs=document.querySelectorAll('button.del');"
    "for(i=0;i<bs.length;i++){var b=bs[i].dataset;"
    "if(d.v?b.v===d.v:b.k===d.g)bs[i].disabled=false}"
    "return}"
    "if(!d.x)return;",

    "if(d.x.indexOf('delete')===0&&!confirm('Delete '+d.n+' from the oven?"
    " This cannot be undone.'))return;"
    "x.disabled=true;"
    "fetch('/'+d.x+'/'+encodeURIComponent(d.s),{method:'POST'})"
    ".then(function(r){return r.text()})"
    ".then(function(h){document.open();document.write(h);document.close()})"
    ".catch(function(e){x.disabled=false;alert('Did not reach the oven: '+e)"
    "})});"
    "</script>")


def index_page(runs, profiles, warning=None):
    """The whole page as one string. For tests and for anything with room."""
    return "".join(index_parts(runs, profiles, warning))


# Three pieces, not one literal: this is the biggest single thing on the
# page, and one string of it is what the heap could not always find room
# for.
_UPLOAD = (
    "<h2>Add or replace a profile</h2>"
    "<div class=s>JSON, under 2.5 kB. It is checked before it is kept: if "
    "anything is wrong you are told which field and nothing on the oven "
    "changes. Sending one with a name already in the list adds a new "
    "version of it rather than replacing it: the newest version is the one "
    "the oven runs, and the older ones stay listed above until you delete "
    "them.</div>",

    "<table class=f>"
    "<tr><th>field</th><th>what it is</th></tr>"
    "<tr><td>name</td><td>required. Shown at the oven, and decides the "
    "filename.</td></tr>"
    "<tr><td>points</td><td>required. <code>[[seconds, celsius], ...]</code>"
    " &mdash; two or more, the first at t=0, times increasing, 0-300 C."
    "</td></tr>"
    "<tr><td>category</td><td><code>reflow</code> (the default), "
    "<code>bake</code> or <code>hold</code>.</td></tr>",

    "<tr><td>liquidus_c</td><td>required for a reflow profile: where the "
    "alloy melts. The stages and the time above liquidus are worked out "
    "from it.</td></tr>"
    "<tr><td>tal_min_s<br>tal_max_s</td><td>the time-above-liquidus window "
    "the run report judges against.</td></tr>"
    "<tr><td>max_ramp_up_c_per_s</td><td>the ramp the report treats as too "
    "steep.</td></tr>",

    "<tr><td>cooling_assumes_open_door</td><td><code>true</code> if the tail "
    "falls faster than this oven does shut, so the run needs somebody to "
    "open the door when it asks.</td></tr>"
    "<tr><td>alloy<br>reference<br>notes</td><td>free text. Kept with the "
    "profile so a run can be traced back to where its curve came "
    "from.</td></tr></table>"
    "<div class=s><code>default</code> and <code>diagnostic</code> are "
    "removed if you send them: a profile that arrives this way can neither "
    "make itself the selected one nor hide from the list it just joined. "
    "Somebody chooses the profile at the oven.</div>",

    "<div class=up>"
    "<div><button id=tpl type=button class=alt>Start from a template</button>"
    "</div>"
    "<input type=file id=f accept='.json,application/json'>"
    "<textarea id=t rows=10 placeholder='or paste the profile here'>"
    "</textarea>"
    "<button id=b type=button>Send to the oven</button>"
    "<div id=m class=s></div>"
    "</div>",

    "<script>"
    "var f=document.getElementById('f'),t=document.getElementById('t'),"
    "b=document.getElementById('b'),m=document.getElementById('m'),"
    "tpl=document.getElementById('tpl');"
    "tpl.addEventListener('click',function(){"
    "t.value=JSON.stringify({name:'My paste',category:'reflow',"
    "liquidus_c:138,tal_min_s:60,tal_max_s:90,max_ramp_up_c_per_s:2.5,"
    "cooling_assumes_open_door:true,"
    "points:[[0,25],[90,90],[180,130],[210,138],[240,165],[270,138],"
    "[300,95]]},null,1);"
    "m.textContent='A working low-temperature curve. Edit it, then send.'});",

    "f.addEventListener('change',function(){"
    "var r=new FileReader();r.onload=function(){t.value=r.result};"
    "if(f.files[0])r.readAsText(f.files[0])});",

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


_CHANGES = (("/archive/", "archive"), ("/unarchive/", "unarchive"),
            ("/delete-version/", "delete-version"),
            ("/delete-profile/", "delete-profile"))


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
    # Changes are POST only, so nothing a browser prefetches or a crawler
    # follows can archive or delete anything.
    for prefix, kind in _CHANGES:
        if path.startswith(prefix):
            name = path[len(prefix):]
            if not name or "/" in name or ".." in name:
                return ("bad-name", name)
            if method != "POST":
                return ("not-found", path)
            return (kind, name)
    if path.startswith("/bundles/"):
        name = path[len("/bundles/"):]
        if (not name.endswith(".json") or len(name) <= 5 or "/" in name
                or ".." in name):
            return ("bad-name", name)
        return ("get-bundle", name[:-5])
    if path.startswith("/profiles/"):
        name = path[len("/profiles/"):]
        if not name or "/" in name or ".." in name:
            return ("bad-name", name)
        return ("get-profile", name)
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
