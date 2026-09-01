# SPDX-License-Identifier: MIT
"""NTP parsing, including replies that should be refused.

A clock set from a bad reply is worse than one that is admittedly unset:
every log written afterwards carries a wrong date and says nothing about
it. So the failure mode here is an exception, never a plausible number.
"""

import struct
import time as _time

import pytest

from oven.timesync import (EARLIEST, LATEST, NTP_TO_UNIX, PACKET_SIZE,
                           TimeError, iso, looks_set, parse, request)


def reply(unix=1756700000, mode=4, stratum=2, leap=0, size=PACKET_SIZE):
    data = bytearray(size)
    data[0] = (leap << 6) | (4 << 3) | mode
    data[1] = stratum
    if size >= 44:
        struct.pack_into(">I", data, 40, unix + NTP_TO_UNIX)
    return bytes(data)


def test_a_request_is_a_client_packet():
    packet = request()
    assert len(packet) == PACKET_SIZE
    assert packet[0] & 0b111 == 3, "mode must be client"
    assert (packet[0] >> 3) & 0b111 == 4, "version 4"


def test_a_good_reply_gives_the_time():
    assert parse(reply(1756700000)) == 1756700000


def test_a_broadcast_reply_is_accepted():
    assert parse(reply(mode=5)) == 1756700000


@pytest.mark.parametrize("bad,why", [
    (None, "no reply at all"),
    (b"", "empty"),
    (b"\x1c" * 20, "truncated"),
    (reply(mode=3), "a client packet echoed back"),
    (reply(leap=3), "the server says it is not synchronised"),
    (reply(stratum=0), "kiss of death"),
    (reply(stratum=16), "unusable stratum"),
    (reply(unix=0 - NTP_TO_UNIX), "zero transmit timestamp"),
    (reply(unix=EARLIEST - 1), "before this project existed"),
    (b"\x24\x02" + b"\x00" * 38 + b"\x00\x00\x00\x01" + b"\x00" * 4,
     "a transmit timestamp of 1 second past 1900"),
])
def test_a_bad_reply_is_refused_not_guessed(bad, why):
    with pytest.raises(TimeError):
        parse(bad)


def test_the_bounds_bracket_now():
    """A guard set in the past would let a stale clock through."""
    now = int(_time.time())
    assert EARLIEST < now < LATEST


def test_the_upper_bound_is_the_end_of_ntp_era_zero():
    """Not a policy choice: the field is 32 bits of seconds since 1900.

    A bound beyond 2036-02-07 could never be reached, so it would be a
    guard that does nothing.
    """
    assert LATEST == 4294967295 - NTP_TO_UNIX
    assert iso(LATEST).startswith("2036-02-07")


def test_an_era_rollover_reads_as_1900_and_is_refused():
    """After 2036 a reply wraps. That must not set the clock back."""
    wrapped = reply(unix=EARLIEST)
    wrapped = bytearray(wrapped)
    struct.pack_into(">I", wrapped, 40, 5)      # 5 seconds past 1900
    with pytest.raises(TimeError):
        parse(bytes(wrapped))


def test_looks_set_rejects_seconds_since_boot():
    """Uptime is what the oven has instead of a clock, and it is small."""
    assert looks_set(1756700000) is True
    assert looks_set(None) is False
    assert looks_set(0) is False
    assert looks_set(263943) is False, "that is three days of uptime, not a date"


def test_iso_is_sortable_and_safe_for_a_fat_filesystem():
    stamp = iso(1756700000)
    assert stamp.startswith("2025-") or stamp.startswith("2026-")
    for ch in ":/\\?*<>|":
        assert ch not in stamp, "%r would be rejected by FAT" % ch
    assert iso(None) is None
    assert iso(50) is None


@pytest.mark.parametrize("unix,expected", [
    (0 + 1735689600, "2025-01-01T00-00-00Z"),
    (1735689600 + 86399, "2025-01-01T23-59-59Z"),
    (1735689600 + 86400, "2025-01-02T00-00-00Z"),
])
def test_iso_matches_known_dates(unix, expected):
    assert iso(unix) == expected


def test_iso_handles_a_leap_year_boundary():
    """2028-02-29 exists; getting it wrong shifts every later date."""
    import calendar
    target = calendar.timegm((2028, 2, 29, 12, 0, 0, 0, 0, 0))
    assert iso(target) == "2028-02-29T12-00-00Z"


def test_iso_agrees_with_the_standard_library_across_many_dates():
    import calendar
    for unix in range(EARLIEST, EARLIEST + 86400 * 900, 86400 * 37):
        expected = _time.strftime("%Y-%m-%dT%H-%M-%SZ", _time.gmtime(unix))
        assert iso(unix) == expected, "disagreed at %d" % unix
