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

## What the radio can and cannot do

Measured on the device, not estimated:

| | bytes |
|---|---|
| firmware free, idle | 30352 |
| the running screen costs | −14080 |
| **free during a run** | **16272** |
| `esp32spi` + socket, resident | 18192 |
| a connected session | 4400 |
| **WiFi needs** | **22592** |

So the radio **fits while the oven is idle**, with about 7.7 kB spare, and
is **6.3 kB short during a run**.

`adafruit_requests` was dropped for raw sockets, which saved 9.7 kB — an
HTTP POST is a dozen lines by hand and NTP is a 48-byte UDP packet. The only
remaining item of that size is 59 kB of fonts and their glyphs, which cannot
shrink without a font toolchain this repository does not have.

This splits the work by where it has to run:

**On the oven, while idle** — upload a finished run, sync the clock, fetch
profiles, send a notification once the run has ended.

**On the attached host** — watching a run live, and stopping one from
elsewhere. Both must work *during* a run, which the oven cannot do, and both
already work over the USB serial link that carries every telemetry row.

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
