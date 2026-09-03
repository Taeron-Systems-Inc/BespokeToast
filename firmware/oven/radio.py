# SPDX-License-Identifier: MIT
"""The WiFi hardware, and nothing that can be decided without it.

Deliberately thin. Which network to join, whether the radio may come up at
all, and whether a returned time is believable are decided in netconfig and
timesync, which have no hardware in them and are tested on a host. What is
left here is the part that can only be checked by running it.

Two things worth knowing about this stack, both measured:

  * It costs about 18 kB resident, which fits while the oven is idle and
    does not fit during a run. netconfig.may_connect enforces that.
  * The first connect_AP attempt usually fails and the second succeeds, so
    retrying is not optional.

The time comes from the ESP32's own SNTP client rather than a hand-rolled
NTP exchange. The co-processor already does it, and UDP over this SPI
protocol is the least trodden path in the library -- but the answer is
still run past timesync before anyone believes it, because an unsynced
NINA returns something small rather than an error.
"""

import time

import board
import busio
from digitalio import DigitalInOut

from adafruit_esp32spi import adafruit_esp32spi

from oven import timesync

CONNECT_ATTEMPTS = 3
CONNECT_SETTLE_S = 2.0


class Radio(object):
    def __init__(self, on_warning=None):
        self._warn = on_warning or (lambda msg: print("# WARNING %s" % msg))
        self._esp = None
        self._spi = None
        self._pins = []

    def _hardware(self):
        if self._esp is None:
            self._spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
            self._pins = [DigitalInOut(board.ESP_CS),
                          DigitalInOut(board.ESP_BUSY),
                          DigitalInOut(board.ESP_RESET)]
            self._esp = adafruit_esp32spi.ESP_SPIcontrol(
                self._spi, self._pins[0], self._pins[1], self._pins[2])
        return self._esp

    def scan(self):
        """(ssid, rssi) for everything in range. Empty on failure."""
        try:
            esp = self._hardware()
            return [(str(ap["ssid"], "utf-8"), ap["rssi"])
                    for ap in esp.scan_networks()]
        except Exception as e:
            self._warn("wifi scan failed (%r)" % e)
            return []

    def connect(self, network):
        """Join *network*. Returns True if it worked.

        The first attempt fails often enough that a single try reads as "no
        network here" when the network is fine.
        """
        try:
            esp = self._hardware()
        except Exception as e:
            self._warn("wifi hardware not available (%r)" % e)
            return False
        for attempt in range(CONNECT_ATTEMPTS):
            try:
                esp.connect_AP(network.ssid, network.password)
                if esp.is_connected:
                    return True
            except Exception as e:
                if attempt == CONNECT_ATTEMPTS - 1:
                    self._warn("could not join %s after %d attempts (%r)"
                               % (network.ssid, CONNECT_ATTEMPTS, e))
                time.sleep(CONNECT_SETTLE_S)
        return False

    @property
    def ip(self):
        try:
            esp = self._esp
            return esp.pretty_ip(esp.ip_address) if esp else None
        except Exception:
            return None

    def utc_now(self, wait_s=20.0):
        """Seconds since the epoch, or None if the answer is not believable.

        The co-processor runs its own SNTP client and is not ready the
        instant the network is joined -- asking straight away raises
        "_GET_TIME returned 0", which is what it does instead of saying
        "not yet". So this polls until it answers or the time runs out.

        It also returns something small rather than an error when SNTP has
        failed outright, which is what the bounds check in timesync is for:
        without it a log fills with 1970.
        """
        deadline = time.monotonic() + wait_s
        seconds = None
        last = None
        while time.monotonic() < deadline:
            try:
                seconds = self._hardware().get_time()
                if seconds:
                    break
            except Exception as e:
                last = e
            time.sleep(1.0)
        if not seconds:
            self._warn("the radio never produced a time in %.0f s (%r)"
                       % (wait_s, last))
            return None
        if isinstance(seconds, (tuple, list)):
            seconds = seconds[0] if seconds else 0
        try:
            seconds = int(seconds)
        except (TypeError, ValueError):
            self._warn("the radio returned %r for the time" % (seconds,))
            return None
        if not timesync.looks_set(seconds):
            self._warn("the radio's clock reads %d, which is not a "
                       "believable date; leaving the clock unset" % seconds)
            return None
        return seconds

    def post(self, host, port, path, filename, body, timeout_s=20):
        """Send one run log. Returns the raw reply, or None.

        Raw sockets rather than an HTTP client: adafruit_requests costs
        9.7 kB and this is a POST with a known length. The reply is read
        only as far as the status line matters -- uploader.succeeded()
        decides, and anything short of a 2xx leaves the log pending.
        """
        from adafruit_esp32spi import adafruit_esp32spi_socket as socket

        from oven import uploader
        try:
            esp = self._hardware()
            socket.set_interface(esp)
            addr = socket.getaddrinfo(host, port)[0][4]
        except Exception as e:
            self._warn("cannot resolve %s:%s (%r)" % (host, port, e))
            return None

        sock = None
        try:
            sock = socket.socket()
            sock.settimeout(timeout_s)
            sock.connect(addr)
            # Sent in pieces. The co-processor's socket buffer is 4000
            # bytes and a run log is tens of kilobytes; handing send() the
            # whole thing does not fail, it simply never returns. A ten
            # minute run is about 26 kB, so this is roughly 26 calls at a
            # few milliseconds each -- fine, because the oven is idle.
            payload = uploader.request(host, path, filename, body, port)
            step = 1024
            for start in range(0, len(payload), step):
                sock.send(payload[start:start + step])
            reply = b""
            deadline = time.monotonic() + timeout_s
            while time.monotonic() < deadline and len(reply) < 512:
                chunk = sock.recv(256)
                if not chunk:
                    break
                reply += chunk
                if b"\r\n\r\n" in reply:
                    break
            return reply
        except Exception as e:
            self._warn("upload of %s failed (%r)" % (filename, e))
            return None
        finally:
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass

    def close(self):
        """Drop the connection AND release the bus.

        Releasing matters more than it sounds. busio.SPI stays claimed for
        the life of the object, so a Radio that is finished with but not
        released makes every later one fail with "SCK in use" -- which is
        exactly what happened: one failed upload at boot left the bus held,
        and every subsequent attempt died before it reached the network.
        """
        ok = True
        try:
            if self._esp is not None and self._esp.is_connected:
                self._esp.disconnect()
        except Exception as e:
            self._warn("could not drop the wifi connection (%r)" % e)
            ok = False
        self._esp = None
        for pin in self._pins:
            try:
                pin.deinit()
            except Exception:
                ok = False
                self._warn("a radio pin would not release")
        self._pins = []
        try:
            if self._spi is not None:
                self._spi.deinit()
        except Exception as e:
            self._warn("the SPI bus would not release (%r); further radio "
                       "use will fail with 'SCK in use'" % e)
            ok = False
        self._spi = None
        return ok
