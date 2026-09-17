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

- ESP32 co-processor: NINA firmware 1.2.2. No MAC addresses are recorded in
  this repository.
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

It can take a profile. POST /profiles accepts a JSON profile under 2560
bytes, validates it, and writes it where the catalogue can see it -- which
reloads, so an uploaded profile appears without a restart. It still cannot
select one: an upload has `default` and `diagnostic` stripped before it is
kept, so it can neither make itself the selection nor hide from the list it
just joined, and its filename comes from the profile's own name rather than
from the request.

That size limit is measured, not chosen. 2700 bytes is served in 1.5 s,
3000 arrives truncated, and 3200 gets no reply at all and leaves the server
holding a half-read request until the firmware restarts. Nothing in the
application can prevent that, because the server reads the request before
the application is called -- so the limit sits under the cliff and the form
refuses to send more.

### The radio stays up; only the polling stops

The server is up only while the oven is idle, but the *radio* now stays
associated through a run, and the listening socket stays bound. What must
not happen during a run is `update_poll()` -- that is the call that costs
up to 227 ms against a 250 ms control deadline -- and the guard on the poll
is what prevents it. Associating costs nothing per loop, because the driver
touches SPI only when it is called.

Closing both and reopening them afterwards was measured at **24.22 s of
frozen main loop**: no telemetry, no touch, no console, and the previous
screen still up because the render never got a turn. It happened on exactly
one transition -- back to idle -- which is the DONE button at the end of
every run, and it is what "the DONE button doesn't work" was.

    telemetry, 4 Hz, across a boot
    85419.25  last row before web.start()
    85443.47  first row after            24.22 s

Staying up costs 1472 bytes, measured on the board: 1200 to associate and
272 more for the listening socket. The imports are another 5792 and are not
returned by closing anyway, because CircuitPython keeps them in
`sys.modules`. Against a screen that freezes for 24 s after every run, that
is not a difficult trade.

Two consequences worth knowing. A browser that hits the oven mid-run
connects and waits, rather than being refused, and is answered when the run
ends; the backlog is 1, so a second attempt is refused rather than queued.
And `web.start()` now runs after the frame is drawn, not before, so a cold
boot puts the screen up first and brings the radio up behind it -- ahead of
the render it meant a fresh boot showed nothing at all for as long as the
network took.

### Boot: one bring-up, and nothing waits for it

Bringing the radio up is now `oven/bringup.py`: a state machine that does at
most **one command to the co-processor per call** and returns. The loop calls
it once per pass while idle, so the screen renders, the touchscreen is read
and the control cadence is kept throughout.

Measured on the board, a cold boot with the clock unset:

    t = 9.9 s    first telemetry row -- imports, fonts, hardware done
    t = 11.4 s   3.00 s gap: the splash and the self-test panel, deliberate
    t = 14.4 s   home screen up, oven usable, START works
    t = 41.4 s   joined, clock set, page serving
                 -- and not one gap in the telemetry between those two

Before, boot did this:

    splash, self-test, then 24.22 s of FROZEN LOOP for the clock's own
    connection, then supervisor.reload(), then splash and self-test again,
    then another 24.22 s of frozen loop for the page's connection

About fifty seconds, most of it with the oven answering nothing at all --
no telemetry, no touch, no console -- while the self-test panel sat on
screen with every line reading OK. It was reported as a hang twice, and it
was indistinguishable from one.

Three things were wrong and all three are fixed:

**The radio came up twice.** The clock made its own connection and the page
made another: two co-processor resets, two scans, two joins.  The clock is
now read on the connection the page is already making.

**It restarted in between.** `set_rtc` called `supervisor.reload()` to give
back the 7280 bytes the WiFi imports leave in `sys.modules`. That reason had
expired twice over: the radio now stays associated for the whole session, so
those modules are resident whatever happens, and the frozen build leaves
60368 free with the server up. The restart freed memory that was re-spent
seconds later, and charged a second cold boot for it.

**It blocked.** The waiting was never one long call -- the library polls, a
scan sleeping 2 s between tries, a join reading a status register, the clock
asked once a second. The longest indivisible thing is one SPI transaction at
227 ms. So the waiting could always have been somebody else's turn, and now
it is.

The idle screen says which stage it is in on the line that used to read
either an address or "no network": *looking for a network*, *joining
Voxelis*, *setting the clock*, then the address.

There is no abort button. One was considered, and the reason to want it was
the lock-out; there is no lock-out left to escape.

If the network is not there, the bring-up gives up on deadlines -- 20 s for
a scan that finds nothing, three join attempts of 10 s -- and the line reads
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
upstream is being fixed. A co-processor that will not take the command falls
back to DHCP, and a configuration missing either half is refused rather than
half applied.

## When discovery fails: check the gaps, not the totals

On 2026-09-16 the access point's 2.4 GHz radio was found to have degraded
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

Multicast discovery had been dead on that radio, presumably for months, and
nobody had attributed it: ARP was the only symptom anyone happened to
report.

**If it happens again**, probe a client known to work alongside the one that
does not, with `tools/host/arp-probe.py`, and compare the *gap patterns*
rather than the totals. A clean 1-in-N is this fault. The fix is on the
access point -- `wifi down wifi0 && wifi up wifi0` -- and note that `wifi
reload` there is a no-op that returns success, drops no client, and looks
exactly like a clean negative result.

### Four rules this cost

1. **A control is not a control until its band and BSSID are written next to
   the number.** A "wireless host that works" was twice something else: once
   a wired host, once a 5 GHz client on a different BSS. Neither ever tested
   the path under investigation.
2. **Totals hide a structured fault; gaps expose it.** Three parties argued
   for three days about whose rate was right -- 5 of 48, 0 of 172, 1 of 10.
   The question that ended it was whether the successes were clustered or
   uniform, and it took ninety seconds to answer.
3. **Test the mechanism before writing the fix.** Proxy ARP was recommended
   on an idle test that never exercised a fresh join -- the one path it
   broke, by answering the oven's own DHCP address probe and making lwIP
   refuse the address it had just been given.
4. **Never answer an ARP probe on someone's behalf.** If an ARP proxy is
   ever used here, it must not reply when the sender address is 0.0.0.0 or
   equal to the target: both are a device asking whether its own address is
   free, and RFC 5227 requires it to treat any answer as a conflict.

## Open: the web service dies on SPI errors while idle

Measured 2026-09-16 across two ten-minute idle windows: the service stopped
twice on its own and restarted itself 11 s and 40 s later.

    web: stopped serving (ConnectionError('Failed to send 88 bytes (sent 0)'))
    web: stopped serving (TimeoutError('ESP32 not responding'))

The association is untouched throughout -- ping stays at 0% loss -- so this
is the co-processor intermittently not answering over SPI, not a network
fault. It is self-healing, and the cost is a page that is unreachable for
tens of seconds at a time. Undiagnosed.

## Losing the network, and getting it back

The oven can be off the network while looking perfectly healthy from its
own console: idle, no fault, an address on the screen. It happened for eight
hours on 2026-09-15 -- reporting `network=10.20.10.242` and a live web
service while answering nothing and absent from the access point's station
table -- and a reload rejoined it in seconds.

Two separate faults sat behind this, and the second was the worse one.

**An association lost after the page is up** is now noticed: the idle path
asks the co-processor once a minute whether it is still associated, and on a
no, tears the service down so the next pass runs a fresh bring-up.

**A bring-up that fails in the first place** used to be terminal. The main
loop calls `advance()` only while it returns True, and its flag is set once
at startup and never restored, so a boot that lost a scan to a busy channel
or met an access point still coming up went off the network until somebody
rebooted it -- healthy, idle, reporting no fault, retrying nothing. Observed
2026-09-16: four minutes unreachable across two liveness intervals with a
silent console, cleared instantly by a reload. A failed bring-up now backs
off and retries every 120 s instead.

The liveness check never covered that case, because it sits behind an
established server. Between them they cover both directions, and the
eight-hour outage of 2026-09-15 was most likely the latch rather than the
silent drop.
