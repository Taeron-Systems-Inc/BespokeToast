# SPDX-License-Identifier: MIT
"""Ask the network what time it is.

The oven has no battery-backed clock. Until it is told, every run it
records is stamped with seconds-since-boot, which is enough to plot a run
against itself and useless for saying which run it was. A reflow log that
cannot be placed in time cannot be matched to a board.

The wire format is handled here, away from the radio, because it is the
part worth testing: a malformed or hostile reply must not be able to set
the clock to something absurd. It is 48 bytes of UDP, which is also why
this does not need an HTTP client -- see docs/network.md for what that
saved.
"""

import struct

# NTP counts from 1900, POSIX from 1970.
NTP_TO_UNIX = 2208988800

PACKET_SIZE = 48
NTP_PORT = 123

# Anything outside this is not a clock error, it is a wrong answer.
#
# The lower bound is after this project started. The upper one is not a
# policy choice: NTP's transmit timestamp is 32 bits of seconds since 1900,
# so era 0 runs out on 2036-02-07 and 4294967295 is the largest value the
# field can hold. A bound beyond that could never be reached and would be
# a guard that does nothing.
#
# When era 1 arrives this needs an era offset, and a reply will otherwise
# read as 1900. The lower bound catches that rather than letting it set
# the clock back 126 years.
EARLIEST = 1735689600      # 2025-01-01
LATEST = 4294967295 - NTP_TO_UNIX      # 2036-02-07, the end of NTP era 0


class TimeError(Exception):
    pass


def request():
    """A client request packet: mode 3, version 4."""
    packet = bytearray(PACKET_SIZE)
    # LI = 0, VN = 4, Mode = 3
    packet[0] = 0b00100011
    return packet


def parse(data):
    """The POSIX timestamp in an NTP reply.

    Raises TimeError rather than returning something plausible: a clock set
    from a bad reply is worse than a clock that is admittedly unset, because
    every log written afterwards carries the wrong date without saying so.
    """
    if data is None:
        raise TimeError("no reply")
    if len(data) < PACKET_SIZE:
        raise TimeError("reply is %d bytes, expected at least %d"
                        % (len(data), PACKET_SIZE))

    mode = data[0] & 0b111
    if mode not in (4, 5):               # server, broadcast
        raise TimeError("reply mode is %d, not a server reply" % mode)

    leap = (data[0] >> 6) & 0b11
    if leap == 3:
        raise TimeError("server says its own clock is not synchronised")

    stratum = data[1]
    if stratum == 0:
        raise TimeError("stratum 0: a kiss-of-death packet, not a time")
    if stratum > 15:
        raise TimeError("stratum %d is not usable" % stratum)

    # Transmit timestamp, seconds part, at offset 40.
    seconds = struct.unpack_from(">I", data, 40)[0]
    if seconds == 0:
        raise TimeError("transmit timestamp is zero")

    unix = seconds - NTP_TO_UNIX
    if not EARLIEST <= unix <= LATEST:
        raise TimeError("time %d is outside anything believable" % unix)
    return unix


def looks_set(timestamp):
    """Whether a timestamp is a real date rather than seconds since boot."""
    return timestamp is not None and EARLIEST <= timestamp <= LATEST


def iso(timestamp):
    """A sortable UTC stamp, without importing anything to format it.

    Used in log filenames and headers, so it avoids characters a FAT
    filesystem would object to.
    """
    if not looks_set(timestamp):
        return None
    days, rem = divmod(int(timestamp), 86400)
    hh, rem = divmod(rem, 3600)
    mm, ss = divmod(rem, 60)

    year = 1970
    while True:
        length = 366 if _leap(year) else 365
        if days < length:
            break
        days -= length
        year += 1
    month = 1
    for count in _months(year):
        if days < count:
            break
        days -= count
        month += 1
    return "%04d-%02d-%02dT%02d-%02d-%02dZ" % (year, month, days + 1,
                                               hh, mm, ss)


def _leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _months(year):
    return (31, 29 if _leap(year) else 28, 31, 30, 31, 30,
            31, 31, 30, 31, 30, 31)
