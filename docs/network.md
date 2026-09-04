# Putting the oven on the network

## Credentials

The oven reads `/wifi.json` from its own filesystem:

```json
{
  "networks": [
    {"ssid": "Voxelis", "password": "..."},
    {"ssid": "Taeron",  "password": "..."}
  ]
}
```

It is **device-only**. It is not in this repository, it is in `.gitignore`,
and `tools/deploy.py` never writes it — deploy copies `firmware/` wholesale
and would otherwise replace the credentials every time.

The oven scans and joins whichever listed network it hears most strongly,
rather than taking the first in the file. Both networks reach the bench.

Take the passphrase from the supplicant config that is actually
authenticating (`/run/netplan/wpa-wlan0.conf`), not from the netplan source
that generates it. Parsing the latter is how a passphrase came out two
characters too long and cost three failed connection attempts to notice.

### One caveat worth knowing

`CIRCUITPY` is USB mass storage. Anyone who plugs a cable into the PyPortal
can read `wifi.json`. That is inherent to the platform, not to this choice
of file. If the oven ever moves somewhere less trusted, put it on an
isolated SSID rather than trying to hide the file.

## What the radio costs

This was measured twice and the second answer is twenty times smaller than
the first. The first was right about the numbers and wrong about the cause.

The PyPortal firmware already carries `adafruit_esp32spi`,
`adafruit_display_text`, `adafruit_requests`, `neopixel`,
`adafruit_bus_device` and `adafruit_portalbase` **frozen into flash** —
`help("modules")` on the device lists them. A copy of any of those on
CIRCUITPY *shadows* the frozen one and is loaded into RAM instead, for no
benefit whatsoever. Installing the Adafruit bundle puts them there.

| | shadowed by a .mpy | frozen in flash |
|---|---|---|
| `import adafruit_esp32spi` | 16064 | **16** |
| `import ..._socket` | 2320 | 112 |
| create, scan, connect | ~1700 | 1312 |
| one HTTP exchange | ~2400 | 432 |
| **whole connected session** | **22592** | **1872** |

Moving those copies aside took idle free memory from 29376 to 36032 bytes
and cost nothing: the display renders 1454 frames across 20-260 °C with
zero failures, and the frozen socket API is the same one this code was
written against (`getaddrinfo`, `SOCK_STREAM`, `set_interface`, no
`TCP_MODE`).

`tools/deploy.py` refuses to deploy if any of them reappear, because the
failure is silent — everything works, just with 20 kB less to work in.

### What this means

The earlier conclusion here was that the radio fits while idle and is
6.3 kB short during a run, so live view and remote abort had to live on the
attached host. That was arithmetic on the shadowed figures. At 1872 bytes
against roughly 22 kB free during a run, the memory objection is gone.

What has not gone is the timing one: the control loop holds a 250 ms
deadline and an SPI call to the co-processor can block for longer. Anything
that talks to the network *during* a run puts that latency inside the loop
that decides when the heater switches off. That needs solving on its own
terms before a live view is worth building, and it is not a memory
problem.

## Measured facts

- ESP32 co-processor: NINA firmware 1.2.2, MAC `bc:c9:49:95:ab:34`
- `Voxelis` reads −36 to −48 dBm from inside the oven's enclosure
- Connecting takes about 9–18 s, and the **first attempt frequently fails**
  with `ConnectionError`; the second succeeds. Retry is not optional.
- The socket API here is the CPython-style one: `socket.getaddrinfo(host,
  port)[0][4]` then `connect(addr)`. There is no `TCP_MODE`, and `recv()`
  needs a size. Passing a `(host, port)` tuple straight to `connect` fails
  with `BrokenPipeError: Expected 01 but got 00`, which reads like a wiring
  fault and is not one.

## Getting logs off the oven

The oven serves its own page while idle. That is how a run log comes off it
in normal operation: USB is power-only behind a panel, and the network the
oven sits on does not reach the machine that builds its firmware.

    index page          200, 1565 bytes, 0.49 s
    a 26601-byte run    200,             2.74 s

Serving is about twenty times faster than pushing the same file out, which
takes 47 s. If both directions are ever available, prefer being fetched.

The page cannot start a run. Remote start was excluded when these features
were agreed, and a test walks the routes to check none of them resolves to
starting or aborting one. A run begins with a person pressing START at the
oven, having looked inside it.

### The oven does not answer a broadcast ARP

A host that has never spoken to the oven cannot reach it at all. A host that
already knows its MAC address reaches it perfectly. That is the whole fault.

From taeronpi, with the ARP cache empty:

    ping 10.20.10.242        3 sent, 0 received, entry goes to FAILED
    arping -c3               0 responses from 3 broadcasts
    tcpdump                  4 requests leave the radio, nothing comes back,
                             0 packets dropped by the kernel

Hand the same host the MAC address and everything works:

    ip neigh replace 10.20.10.242 lladdr 34:ab:95:49:c9:bc dev wlan0 nud stale

    ping        8 of 8, 49-140 ms          index page   200, 1565 B, 0.44 s

The kernel then refreshes that entry with a *unicast* ARP probe, and the entry
reaches REACHABLE — so the oven does answer ARP. It answers a request addressed
to it and ignores one addressed to the broadcast address. Deleting the entry
brings the fault straight back, every time.

This is almost certainly the ESP32 asleep between DTIM beacons: a station in
power save is signalled about buffered unicast individually, while
group-addressed frames go out after the beacon whether it is listening or not.
The 40-1084 ms ping spread is the same radio napping.

Why only this one machine, then:

| host | how it got the MAC |
|---|---|
| eridani | the oven opened the upload connection to it first |
| bench5 | the oven pinged it during the peer test |
| taeronpi | never — nothing on the oven has ever addressed it |

Every host that works was handed the address by the oven talking first. The Pi
is not special; it is just the only one that had to ask.

**The fix belongs in the firmware, not on the Pi.** An operator's phone on the
Taeron network will be in exactly the Pi's position — a cold cache and nothing
to fill it — so the oven should announce itself unprompted, either with a
gratuitous ARP every half minute or by advertising over mDNS, which does the
same job and gives it a name. Until then, a static entry on the host is the
workaround:

    sudo ip neigh replace 10.20.10.242 lladdr 34:ab:95:49:c9:bc dev wlan0 nud permanent

Note that `arp-announce.service` under `tools/host/` already does the announcing
half of this for the Pi's own address. The oven needs the same thing.

Three wrong explanations were published before this one. That the radio was
dying — it was not, 45 000 polls, zero errors, connected throughout. That the
network isolated wireless clients — it does not, the Pi and bench5 reach each
other fine. And that the failure was mutual and unexplained — it is neither.
The first two came from testing reachability only from the machine that cannot
reach it. The third came from stopping at "it fails" instead of asking which
layer failed; `tcpdump` and a hand-written ARP entry answered it in ten minutes.

One loose end: the peer test recorded the oven failing to ping taeronpi, and
that script addressed peers by name. It was never established whether the oven
failed to resolve the name or failed to reach the host, so that half of the
"mutual" claim rests on nothing. Redo it with a bare address.
