# SPDX-License-Identifier: MIT
"""Which network to join, and when it is safe to have a radio at all.

The decisions here are separated from the radio so they can be tested
without one. What the hardware costs was measured on the device rather than
assumed, and it decides the shape of everything built on top:

    firmware free, idle                      30352
    the running screen costs                -14080
    free during a run                        16272

    esp32spi + socket, resident              18192
    a connected session                       4400
    WiFi needs                               22592

So the radio fits while the oven is idle, with about 7.7 kB to spare, and
does NOT fit while a run is on screen -- it is 6.3 kB short. That is not a
tuning problem: adafruit_requests was already dropped for raw sockets to
save 9.7 kB, and the only remaining item of that size is 59 kB of fonts,
which cannot shrink without a font toolchain this repository does not have.

Hence the rule: never bring the radio up during a run. Uploading an
archive, asking for the time and fetching profiles all happen with the oven
idle and nothing on the line. Anything that must work *during* a run --
watching it live, stopping it from elsewhere -- belongs on the host that is
already attached by USB and already receives every telemetry row.
"""

import json

CONFIG_PATH = "/wifi.json"

# States in which bringing the radio up is allowed. Deliberately a whitelist:
# a state added later has to be considered rather than inherited.
SAFE_STATES = ("idle", "report")


class Network(object):
    __slots__ = ("ssid", "password")

    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password

    def __repr__(self):
        return "Network(%s)" % self.ssid


def load(path=CONFIG_PATH, opener=open, on_warning=None):
    """Read the known networks.

    The file is device-only: it is not in the repository and tools/deploy.py
    never writes it, because deploy copies firmware/ wholesale and would
    otherwise replace the credentials on every deploy.
    """
    warn = on_warning or (lambda msg: print("# WARNING %s" % msg))
    try:
        with opener(path) as f:
            data = json.load(f)
    except OSError:
        warn("no %s: the oven will stay off the network" % path)
        return []
    except ValueError as e:
        warn("%s is not valid JSON (%s): the oven will stay off the network"
             % (path, e))
        return []
    out = []
    for entry in data.get("networks", []):
        ssid = entry.get("ssid")
        password = entry.get("password")
        if not ssid or password is None:
            warn("ignoring a network with no ssid or password in %s" % path)
            continue
        out.append(Network(ssid, password))
    if not out:
        warn("%s lists no usable networks" % path)
    return out


def choose(networks, scan):
    """Pick the strongest known network from *scan*.

    Order in the file is not used: which network is strongest where the oven
    sits is a fact to measure. Both of the known networks reach the bench,
    and the oven does not move, but the shop might change around it.

    *scan* is a sequence of (ssid, rssi). Returns a Network, or None.
    """
    known = {}
    for n in networks:
        known[n.ssid] = n
    best = None
    best_rssi = None
    for ssid, rssi in scan:
        if ssid in known and (best_rssi is None or rssi > best_rssi):
            best, best_rssi = known[ssid], rssi
    return best


def may_connect(state, heating):
    """Whether the radio may be brought up right now.

    Two independent reasons to say no, and both are checked: the memory
    argument above, and the plain one that a run is not the time to be doing
    anything optional. `heating` is passed separately from `state` so that a
    relay energised in a state this does not know about still says no.
    """
    if heating:
        return False
    return state in SAFE_STATES
