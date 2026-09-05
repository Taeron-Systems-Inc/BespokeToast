# SPDX-License-Identifier: MIT
"""Deciding what to send off the oven, and how to ask.

None of this touches a radio. What to upload, how to build the request and
what counts as a success are decisions, and decisions are testable; the
socket is not. That split is what lets the retry policy and the "have I
already sent this?" logic be exercised on a host, where getting them wrong
costs nothing.

Uploading only happens when the oven owns its own filesystem, which is when
USB is absent -- and that is also the only time it has logs of its own to
send. A run recorded while a host is attached is already on the host's
screen.
"""

MAX_ATTEMPTS = 3


def pending(names, sent=()):
    """Logs that still need sending, oldest first.

    Which ones are done is passed in rather than read off the filenames.
    It used to be a .sent suffix on the file itself, and the argument for
    that was sound as far as it went -- a rename is one atomic operation,
    where an index is a second thing to keep consistent with the directory
    and the thing that will be wrong after a power cut halfway through a
    write.

    What that argument missed is where the cost lands. The suffix followed
    the file out to whoever downloaded it, arriving as
    0003-SAC305-this-oven.csv.sent: a name that will not open in a
    spreadsheet and that says nothing to the person holding it. The index
    can only fail in one direction -- a torn write loses names, so a run
    gets offered again -- and being uploaded twice is the cheap mistake.
    Being marked sent when it was not is the expensive one, and neither
    scheme does that.
    """
    out = []
    for name in names:
        if not name.endswith(".csv"):
            continue
        if name in sent:
            continue
        out.append(name)
    return sorted(out)


def request_head(host, path, filename, length, port=80):
    """Just the headers, for a body that will be streamed after them.

    Reading a run log into memory to send it does not fit: a 26 kB file
    needs a 26 kB allocation on a heap whose largest hole is a few
    thousand bytes, and it failed with MemoryError while the radio was up.
    The length is known from the file size, so the body never has to exist
    as one object.
    """
    return (
        "POST %s HTTP/1.0\r\n"
        "Host: %s\r\n"
        "X-Run-Log: %s\r\n"
        "Content-Type: text/csv\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n" % (path, host if port == 80 else "%s:%d" % (host, port),
                  filename, length)
    ).encode("utf-8")


def request(host, path, filename, body, port=80):
    """The bytes of an HTTP POST. Written out rather than using a client.

    adafruit_requests costs 9.7 kB and this is a dozen lines. The body is
    sent as-is with an explicit length: no chunking, no multipart, nothing
    that needs a parser at either end.
    """
    if isinstance(body, str):
        body = body.encode("utf-8")
    head = (
        "POST %s HTTP/1.0\r\n"
        "Host: %s\r\n"
        "X-Run-Log: %s\r\n"
        "Content-Type: text/csv\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n" % (path, host if port == 80 else "%s:%d" % (host, port),
                  filename, len(body))
    )
    return head.encode("utf-8") + body


def status_of(response):
    """The HTTP status code in a reply, or None if it is not one.

    Anything that is not a 2xx leaves the log unmarked, so it is tried
    again next time. Losing a run's record to a receiver that answered 500
    would be a poor trade for one less retry.
    """
    if not response:
        return None
    try:
        first = response.split(b"\r\n", 1)[0].decode("ascii", "replace")
    except Exception:
        return None
    parts = first.split()
    if len(parts) < 2 or not parts[0].startswith("HTTP/"):
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def succeeded(response):
    code = status_of(response)
    return code is not None and 200 <= code < 300
