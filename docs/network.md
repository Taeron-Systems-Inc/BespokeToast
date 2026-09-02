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
