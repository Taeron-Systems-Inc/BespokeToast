# SPDX-License-Identifier: MIT
"""US Pacific time, because that is where this oven is read.

Logs are stored in UTC and always will be: it is the only stamp that is
unambiguous, it sorts, and it does not repeat an hour every November. What
a person reads should be the time they were standing there, so the
conversion happens on the way out.

CircuitPython has no timezone database, so the rule is written out. It is
the US rule in force since 2007: forward on the second Sunday in March at
02:00 local standard, back on the first Sunday in November at 01:00 local
standard, which are 10:00 and 09:00 UTC. Congress has moved these dates
before and may again; if it does, this is the file to change.
"""

STANDARD_OFFSET_H = -8          # PST
DAYLIGHT_OFFSET_H = -7          # PDT


def _days_from_civil(y, m, d):
    """Days since 1970-01-01. Integer only, no library."""
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _civil_from_days(z):
    z += 719468
    era = (z if z >= 0 else z - 146096) // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + (3 if mp < 10 else -9)
    return (y + (m <= 2), m, d)


def _nth_sunday(year, month, n):
    """Day of month of the *n*th Sunday. 1970-01-01 was a Thursday."""
    first = _days_from_civil(year, month, 1)
    weekday = (first + 4) % 7          # 0 = Sunday
    return 1 + (7 - weekday) % 7 + (n - 1) * 7


def is_daylight(utc_seconds, year):
    start = (_days_from_civil(year, 3, _nth_sunday(year, 3, 2)) * 86400
             + 10 * 3600)
    end = (_days_from_civil(year, 11, _nth_sunday(year, 11, 1)) * 86400
           + 9 * 3600)
    return start <= utc_seconds < end


def parse(stamp):
    """Seconds since the epoch from the stored form, or None.

    The stored form is ISO with dashes where the time would have colons,
    because it also has to survive as a filename on FAT.
    """
    if not stamp or "T" not in stamp:
        return None
    day, _, rest = stamp.partition("T")
    rest = rest.rstrip("Z")
    try:
        y, mo, d = [int(p) for p in day.split("-")]
        parts = rest.replace(":", "-").split("-")
        h, mi = int(parts[0]), int(parts[1])
        sec = int(parts[2]) if len(parts) > 2 else 0
    except (ValueError, IndexError):
        return None
    return _days_from_civil(y, mo, d) * 86400 + h * 3600 + mi * 60 + sec


def local(stamp):
    """(date, time, zone) in Pacific, or None if there is no usable stamp.

    None rather than a guess: a run written before the oven had been told
    the date carries "monotonic+40", and inventing a date for it would be
    worse than admitting there is not one.
    """
    utc = parse(stamp)
    if utc is None:
        return None
    year = _civil_from_days(utc // 86400)[0]
    daylight = is_daylight(utc, year)
    shifted = utc + (DAYLIGHT_OFFSET_H if daylight else STANDARD_OFFSET_H) * 3600
    y, mo, d = _civil_from_days(shifted // 86400)
    rem = shifted % 86400
    return ("%04d-%02d-%02d" % (y, mo, d),
            "%02d:%02d:%02d" % (rem // 3600, rem % 3600 // 60, rem % 60),
            "PDT" if daylight else "PST")
