# Putting the oven on the network

## Credentials

The oven reads `/wifi.json` from its own filesystem. `wifi.json.example` at
the top of this repository is the template: copy it onto the CIRCUITPY
volume as `wifi.json` and fill it in.

```json
{
  "networks": [
    {"ssid": "YourNetwork", "password": "..."},
    {"ssid": "AnotherNetwork", "password": "..."}
  ]
}
```

It is **device-only**. The filled-in file is not in this repository, the
name is in `.gitignore`, and `tools/deploy.py` never writes it — deploy
copies `firmware/` wholesale and would otherwise replace the credentials
every time. The example lives at the top level and not under `firmware/`
for the same reason: an example config landing beside the real one is a
trap, and a test holds it there.

The oven scans and joins whichever listed network it hears most strongly,
rather than taking the first in the file.

Take a passphrase from the supplicant config that is actually
authenticating (on netplan hosts, `/run/netplan/wpa-wlan0.conf`), not from
the source file that generates it. Parsing the latter is how a passphrase
came out two characters too long and cost three failed connection attempts
to notice.

### One caveat worth knowing

`CIRCUITPY` is USB mass storage. Anyone who plugs a cable into the PyPortal
can read `wifi.json`. That is inherent to the platform, not to this choice
of file. If the oven ever moves somewhere less trusted, put it on an
isolated SSID rather than trying to hide the file.

## What the radio costs

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

`tools/deploy.py` refuses to deploy if any of them reappear, because the
failure is silent — everything works, just with 20 kB less to work in.

A connected session costs 1872 bytes against roughly 22 kB free during a
run, so **memory is not what keeps the network out of the loop. Timing
is.** The control loop holds a 250 ms deadline and one SPI call to the
co-processor can block for 227 ms. Anything that talks to the network
*during* a run puts that latency inside the loop that decides when the
heater switches off. A live view has to solve that on its own terms before
it is worth building.

## Measured facts

- ESP32 co-processor: NINA firmware 1.2.2. No MAC addresses are recorded in
  this repository.
- The bench network reads −36 to −48 dBm from inside the oven's enclosure.
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

The page cannot start a run, and a test walks the routes to check that none
of them resolves to starting or aborting one. A run begins with a person
pressing START at the oven, having looked inside it.

It can take a profile. POST /profiles accepts a JSON profile under 2560
bytes, validates it, and writes it where the catalogue can see it — which
reloads, so an uploaded profile appears without a restart. It still cannot
select one: an upload has `default` and `diagnostic` stripped before it is
kept, so it can neither make itself the selection nor hide from the list it
just joined, and its filename comes from the profile's own name rather than
from the request.

That size limit is measured, not chosen. 2700 bytes is served in 1.5 s,
3000 arrives truncated, and 3200 gets no reply at all and leaves the server
holding a half-read request until the firmware restarts. Nothing in the
application can prevent that, because the server reads the request before
the application is called — so the limit sits under the cliff and the form
refuses to send more.

### The radio stays up; only the polling stops

The server runs only while the oven is idle, but the *radio* stays
associated through a run and the listening socket stays bound. What must
not happen during a run is `update_poll()` — the call that costs up to
227 ms — and the guard on the poll is what prevents it. Associating costs
nothing per loop, because the driver touches SPI only when it is called.

Staying up costs 1472 bytes, measured on the board: 1200 to associate and
272 more for the listening socket. The imports are another 5792 and are not
returned by closing anyway, because CircuitPython keeps them in
`sys.modules`. **Closing the socket and the radio at the start of a run and
reopening them at the end costs 24.22 s of frozen main loop** — no
telemetry, no touch, no console, and the previous screen still up because
the render never gets a turn. It lands on exactly one transition, back to
idle, which is the DONE button at the end of every run. That is what "the
DONE button doesn't work" was, and it is why the radio stays up.

Two consequences worth knowing. A browser that hits the oven mid-run
connects and waits rather than being refused, and is answered when the run
ends; the backlog is 1, so a second attempt is refused rather than queued.
And `web.start()` runs after the frame is drawn, so a cold boot puts the
screen up first and brings the radio up behind it.

### Boot: one bring-up, and nothing waits for it

Bringing the radio up is `oven/bringup.py`: a state machine that does at
most **one command to the co-processor per call** and returns. The loop
calls it once per pass while idle, so the screen renders, the touchscreen
is read and the control cadence is kept throughout.

Measured on the board, a cold boot with the clock unset:

    t = 9.9 s    first telemetry row -- imports, fonts, hardware done
    t = 11.4 s   3.00 s gap: the splash and the self-test panel, deliberate
    t = 14.4 s   home screen up, oven usable, START works
    t = 41.4 s   joined, clock set, page serving
                 -- and not one gap in the telemetry between those two

The oven is usable at 14 s and the network arrives behind it. Three rules
hold that, each of which cost about fifty seconds of dead screen when it
was not held:

1. **The radio comes up once.** The clock is read on the connection the
   page is already making, not on one of its own. Two connections mean two
   co-processor resets, two scans, two joins.
2. **Nothing restarts to reclaim memory.** `supervisor.reload()` after
   setting the clock freed the WiFi imports and then re-spent them seconds
   later, charging a second cold boot for it.
3. **Nothing blocks.** The waiting was never one long call — the library
   polls, a scan sleeps between tries, a join reads a status register. The
   longest indivisible thing is one SPI transaction at 227 ms, so the
   waiting can always be somebody else's turn.

The idle screen says which stage it is in where the address goes: *looking
for a network*, *joining <ssid>*, *setting the clock*, then the address.
There is no abort button, because there is no lock-out left to escape.

If the network is not there, the bring-up gives up on deadlines — 20 s for
a scan that finds nothing, three join attempts of 10 s — and the line reads
"no network". The oven runs regardless, with logs stamped from boot instead
of wall clock.

## A fixed address, supported and switched off

`netconfig` reads optional `ip` and `gateway` (and `mask`, `dns`) for a
network in `wifi.json`. When both are present, bring-up sets them before
joining, so DHCP never runs. Measured on the device: joined in 4.5 s, took
its address, pinged the bench host at 40 ms, held.

**Nothing configures it, and it is not the production answer.** A fixed
address is a second place for the network's layout to be recorded and to go
stale. It exists for testing, and for reaching the oven while something
upstream is being fixed. A co-processor that will not take the command
falls back to DHCP, and a configuration missing either half is refused
rather than half applied.

`wifi.json.example` carries a filled-in network entry showing the four
fields:

    "ip": "10.0.0.42", "gateway": "10.0.0.1",
    "mask": "255.255.255.0", "dns": "10.0.0.1"

`mask` defaults to 255.255.255.0 and `dns` to the gateway, so in practice
only the first two are typed.

## Sending finished runs somewhere

Optional, and off on this oven. An `archive` block at the top level of
`wifi.json`, beside `networks`, names a receiver:

```json
{"archive": {"host": "10.0.0.5", "port": 8788, "path": "/runs"}}
```

Only `host` is required; `port` defaults to 80 and `path` to `/runs`. A
non-numeric port is refused rather than guessed, and an archive with no
host is reported — in both cases nothing is uploaded. `wifi.json.example`
carries the same block under an underscored key, which is how it stays
switched off: rename it to `archive` to turn it on.

Each finished log is POSTed as `text/csv` with its filename in an
`X-Run-Log` header. A 2xx marks it sent; anything else leaves it unsent so
it is offered again next time, up to three attempts — losing a run's only
record to a receiver that answered 500 would be a poor trade for one less
retry. `tools/collector/serve.py` is a receiver that works with this and
listens on 8788.

Two constraints worth knowing. Uploading happens only while the oven is
idle, for the same reason nothing else talks to the radio during a run. And
it happens only when the oven owns its own filesystem — which is also the
only time it has logs of its own to send, because a run recorded with a
host attached is already on that host.

An oven with no archive configured loses nothing: it records every run to
its own storage and serves them from its page.

## When discovery fails: check the gaps, not the totals

On 2026-09-16 an access point's 2.4 GHz radio was found to have degraded
after 155 days of uptime. Group-addressed frames reached most of its
stations **exactly one time in ten**, with essentially no variance, while
unicast stayed perfect. So every client answered pings and served pages
normally, and no host with a cold cache could find any of them. Restarting
the radio fixed it in forty seconds; nothing was misconfigured.

    after the restart, 30 broadcast ARP probes at 1 s
    oven      30 of 30   gaps all 1      (0 of 172 before it)
    printer   30 of 30   gaps all 1      (reference client)

    passively on the bench Pi, 90 s
    548 group frames from 18 senders, 114 of them mDNS
    (the same test read 0 in 70 s and 0 in 600 s before the restart)

Multicast discovery had been dead on that radio for months, and nobody had
attributed it: ARP was the only symptom anyone happened to report.

**If it happens again**, probe a client known to work alongside the one
that does not, with `tools/host/arp-probe.py`, and compare the *gap
patterns* rather than the totals. A clean 1-in-N is this fault. The fix is
on the access point — `wifi down wifi0 && wifi up wifi0` — and note that
`wifi reload` there is a no-op that returns success, drops no client, and
looks exactly like a clean negative result.

### Four rules this cost

1. **A control is not a control until its band and BSSID are written next
   to the number.** A "wireless host that works" was twice something else:
   once a wired host, once a 5 GHz client on a different BSS. Neither ever
   tested the path under investigation.
2. **Totals hide a structured fault; gaps expose it.** Three parties argued
   for three days about whose rate was right — 5 of 48, 0 of 172, 1 of 10.
   The question that ended it was whether the successes were clustered or
   uniform, and it took ninety seconds to answer.
3. **Test the mechanism before writing the fix.** Proxy ARP was recommended
   on an idle test that never exercised a fresh join — the one path it
   broke, by answering the oven's own DHCP address probe and making lwIP
   refuse the address it had just been given.
4. **Never answer an ARP probe on someone's behalf.** If an ARP proxy is
   ever used here, it must not reply when the sender address is 0.0.0.0 or
   equal to the target: both are a device asking whether its own address is
   free, and RFC 5227 requires it to treat any answer as a conflict.

## Losing the network, and getting it back

The oven can be off the network while looking perfectly healthy from its
own console: idle, no fault, an address on the screen. Two mechanisms cover
the two directions that can fail.

**An association lost after the page is up** is noticed: the idle path asks
the co-processor once a minute whether it is still associated, and on a no,
tears the service down so the next pass runs a fresh bring-up.

**A bring-up that fails in the first place** backs off and retries every
120 s. This used to be terminal — the main loop calls `advance()` only
while it returns True, and the flag was set once at startup and never
restored, so a boot that lost a scan to a busy channel or met an access
point still coming up went off the network until somebody rebooted it:
healthy, idle, reporting no fault, retrying nothing.

The liveness check does not cover that case, because it sits behind an
established server, which is why both exist.

## Open: the web service dies on SPI errors while idle

Measured 2026-09-16 across two ten-minute idle windows: the service stopped
twice on its own and restarted itself 11 s and 40 s later.

    web: stopped serving (ConnectionError('Failed to send 88 bytes (sent 0)'))
    web: stopped serving (TimeoutError('ESP32 not responding'))

The association is untouched throughout — ping stays at 0% loss — so this
is the co-processor intermittently not answering over SPI, not a network
fault. It is self-healing, and the cost is a page that is unreachable for
tens of seconds at a time. Undiagnosed.
