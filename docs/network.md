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

- ESP32 co-processor: NINA firmware 1.2.2. Its MAC is not recorded here;
  the Pi keeps it in `/var/lib/toaster/arp-known`.
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

### Nothing on this access point receives a broadcast

**This section is superseded. Read the correction that follows it before
acting on anything here.** It is kept because the measurements in it were
real and because the reasoning that turned them into a wrong conclusion is
worth being able to see.



Two devices with nothing in common -- a Raspberry Pi with a Broadcom radio
and the oven's Espressif co-processor -- receive no group-addressed frames
at all on the Voxelis network. Unicast is perfect in both directions. That
one fact accounts for every symptom.

Measured on taeronpi, `tcpdump` on wlan0:

    180 s, promiscuous and not, every broadcast and multicast frame
    not sent by this host                                   0 frames

Not one ARP, DHCP, mDNS or SSDP frame from any other station in three
minutes. Everything it did receive was unicast, chiefly the gateway
polling it every ten seconds.

Measured on the oven, a UDP listener on the co-processor:

    4 datagrams to 10.20.10.255           nothing arrived
    4 datagrams to 10.20.10.242           arrived

Repeated on a second socket and a second port with the same result. The
control is the point: the same host, the same instant, the same size of
datagram, differing only in the destination address.

A device that cannot receive a broadcast cannot answer a broadcast ARP.
So neither of these two can be found by anything that does not already
know its MAC address, and neither can find the other:

    ping 10.20.10.242 with an empty cache       0 of 3, entry FAILED
    ip neigh replace ... lladdr 34:ab:95:...    8 of 8, 49-140 ms
    delete the entry again                      0 of 3, entry FAILED

Once either side holds the other's address everything works and keeps
working -- 20 of 20 pings, the index page in 0.44 s, and the oven pinging
the Pi in 20 ms where minutes earlier it had timed out.

Both are associated to the same BSSID, on channel 11,
at -35 and -47 dBm. Neither is the odd one out.

**This is the access point, and it is not something the firmware can fix.**
The oven cannot answer a request it never receives. Worth looking at on the
AP: multicast-to-unicast conversion, broadcast and multicast rate limiting,
IGMP or ARP snooping, proxy ARP, and any "multicast enhancement" setting.

Until then, a host reaches the oven by being told its address once:

    sudo ip neigh replace 10.20.10.242 lladdr <the oven's MAC> dev wlan0 nud permanent

(The MAC is kept on the Pi in `/var/lib/toaster/arp-known`, not in this
repository.)

#### What this costs the product

An operator arriving with a phone has an empty ARP cache and no way to
fill it. On this network they cannot open the oven's page at all. The
browser plan is sound and the server works; it is the network underneath
it that does not carry the first packet.

**The oven runs on Taeron in production, not on Voxelis, and this has not
been tested there.** That test is worth doing before any more is built on
top of the web service, because it decides whether the whole approach
survives. It needs nothing but a phone, the oven, and the Taeron network.

#### It is worse than one unreachable machine

While this was being written, eridani -- wired, and the machine every
earlier test leaned on -- let its ARP entry expire and could not get it
back:

    eridani: 10.20.10.242 dev eno2 FAILED
    eridani: ping 10.20.10.242      3 sent, 0 received
    the Pi, handed the MAC by hand  4 of 4, and the page in 0.48 s

The oven was in perfect health the whole time. **Once its neighbours'
caches expire the oven is invisible to the entire network, wired included,
until somebody types its MAC address into a host by hand.** That is the
real severity of this, and it is not specific to wireless clients.

#### Why no firmware change can fix it

The obvious answer is to have the oven announce itself, so nothing ever
has to ask. Half of that works: the oven's outgoing broadcast does reach
the wired segment -- eridani's FAILED entry repaired itself, unprompted,
the moment the oven broadcast an ARP request of its own.

The other half does not. With the Pi's cache emptied and `tcpdump`
watching every ARP frame, the oven was made to broadcast ARP requests for
three addresses, one of them the Pi's own:

    oven asks who-has 10.20.10.99     Pi saw nothing
    oven asks who-has 10.20.10.201    Pi saw nothing
    oven asks who-has 10.20.10.237    Pi saw nothing   <- the Pi's address
    Pi's ARP entry for the oven       still absent

Not as a broadcast, and not converted to unicast either. In the same
capture the only ARP the Pi received was the gateway polling it, unicast,
every ten seconds.

So an announcement reaches wired hosts and never reaches wireless ones,
and an operator's phone is a wireless one. There is nothing the oven can
say that a phone can hear. **This is fixed at the access point or it is
not fixed.**

Worth trying there, in rough order of likelihood: proxy ARP, so the AP
answers for its own clients; whatever the vendor calls multicast
enhancement or broadcast filtering; and client isolation. Failing that,
a routed path works -- a phone can always reach its gateway, and the
gateway can always reach the oven, so the oven on its own subnet behind a
port forward sidesteps the whole problem.

#### What the firmware does about it

It puts the address on the screen.

That is not a fix and is not meant to be one. It is what makes the
question answerable: the address comes from whatever DHCP server the oven
meets, it is different on every network, and on a network like this one
nothing can discover it by asking. An operator standing at the oven can
read it off the front and type it into a phone, and that either works or
it does not -- which is the test, and it now costs five seconds instead of
an afternoon.

A keepalive that has the oven broadcast periodically would very likely
stop wired hosts ever losing it again, on the evidence of eridani
repairing itself. It is not implemented, because that evidence is one
unplanned observation rather than a controlled test, and the last change
written here on an untested mechanism had to be reverted the same day.

#### Two theories tested and discarded

*ESP32 power saving.* The co-processor idles in WIFI_PS_MIN_MODEM, waking
on each DTIM to collect what the AP buffered, and the documented weak spot
of that mode is group-addressed traffic. NINA implements the Arduino
`setPowerMode` command at 0x17; sending it a zero byte selects
WIFI_PS_NONE. It was accepted -- the co-processor replied `01` -- and
changed nothing: three more rounds of broadcast ARP, still unanswered.
A firmware change was written for this, and reverted when it did not work.
Retested properly on 2026-09-15, on one live association with a control --
see the last section. Same answer.

Its one measurable effect, 20 pings each way over a warm entry, was not a
clean win either:

    WIFI_PS_NONE        min 8.3   mean 34.6   max 346.9   mdev 75.4 ms
    WIFI_PS_MIN_MODEM   min 20.9  mean 80.9   max 126.0   mdev 33.0 ms

Lower mean, worse tail, one sample of each. Not enough to keep.

*The Pi.* Its stack was audited and is clean: no rules in nftables,
iptables, arptables or ebtables; `arp_ignore`, `arp_announce` and
`arp_filter` all zero; power save off; associated for two days without a
deauth; `tcpdump` shows its requests leaving the radio and the kernel
dropping nothing. It is a victim of this, not a cause -- but so is the
oven, and neither is special.

#### A measurement error worth recording

For most of this investigation the "wireless host that works" was
10.20.10.162, which is **eridani, on the wire**. bench5 is 10.20.10.145.
Every conclusion drawn from "a wireless client can reach the oven" was
drawn from a wired one, and the mistake survived because the address was
never checked against the name.

It matters because it is what made the fault look like it singled out one
pair of machines, which sent the search after differences between those two
machines -- their drivers, their radios, their power saving -- when the
common factor was in front of it the whole time. The question that broke it
open was not about either device: it was whether *anything* broadcast ever
arrives, which took one `tcpdump` and had been available from the start.

Three explanations were published before this one -- a dying radio, client
isolation, and an unexplained mutual failure -- and a fourth, power saving,
was built into firmware before being tested. Test the mechanism before
writing the fix.

Note that `arp-announce.service` under `tools/host/` was added as a hedge
for a symptom of this same fault, before the fault was understood.

## The correction: it is not the access point

Written 2026-09-10, after the access point was audited by someone with
access to it, and after re-testing here.

**The fault above is not reproducible.** From this Pi, forcing every probe
to be a broadcast rather than letting arping fall back to unicast:

    arping -b -c 5      oven    10.20.10.242 (wireless)    5/5
                      bench5    10.20.10.145 (wireless)    5/5
                     eridani    10.20.10.162 (wired)       5/5
                     gateway    10.20.10.1                 5/5

Wireless client to wireless client, which is the exact path claimed broken.
The audit found client isolation off on both interfaces, no broadcast or
multicast filtering, multicast-to-unicast off, IGMP snooping off, Qualcomm
Multicast Enhancement at 0, no ebtables, and intra-BSS forwarding enabled.
A broadcast ARP from the router was answered by all twelve associated
wireless clients on both bands, this Pi and the oven included.

So the conclusion in the section above is withdrawn. Proxy ARP was
requested and the request was retracted. **The retraction was itself wrong:
proxy ARP was enabled on 2026-09-15 and fixed the fault. See the last
section of this file.**

### What was actually measured, and what was inferred

The measurements on 2026-09-04 stand as measurements. What was wrong was
the step from them to "the access point does not deliver broadcasts":

* Two devices seeing no group frames is consistent with an access point
  that does not send them, and equally consistent with an intermittent
  fault, or with two clients that were individually unwell at the time.
  Nothing was done to tell those apart -- no capture from a third device,
  and no repeat on another day.
* The oven is a genuinely marginal client: 26 to 1115 ms round trip, up to
  a third of packets lost. That was known and was treated as a nuisance
  rather than as a candidate explanation for the very thing being
  investigated.
* Today's own evidence for the fault turned out to be one ping check of
  four packets and a single `arping` probe with a two second timeout. Both
  were read as "cannot resolve". Five broadcast probes get five replies.

The obvious alternative on this side was checked and does not explain it
either: the Pi's WiFi power save was already off on 2026-09-04, disabled on
09-02 and not rebooted since 08-24, so it was not asleep during the capture.

The gap between 2026-09-04 and 2026-09-10 is unexplained. It may have been
intermittent, and it may have been a mistake. Either way it is not a
standing property of the network, and the earlier text asserted that it was.

### What this changes about the firmware

Nothing, which is the useful part. Everything built while the fault was
believed is either correct anyway or independently worth having:

* **The address on the idle screen** stays. It costs nothing and it is the
  only channel that works when the network is misbehaving for any reason.
* **`arp-pin` on the Pi** stays. Holding a neighbour entry for the two
  wireless peers that matter is cheap insurance against an intermittent
  fault whose cause is unknown, and it demotes rather than deletes, so it
  cannot outlive its usefulness.
* **No firmware change was ever made for this**, because none was possible.
  The one that was attempted -- ESP32 power save -- was reverted the same
  day when testing showed it did nothing.

The standing lesson is the one already written at the end of this file and
apparently not yet learned: *test the mechanism before writing the fix*, and
one unrepeated observation is not a property of a network.

## Proxy ARP on the router (2026-09-15)

A laptop could not reach the oven. An agent with access to the router
diagnosed a client missing broadcast ARP requests and changed the router.
The change is recorded in the router's own repository (design doc section
5.1, and the installed files under `router-config/proxyarp/`); this is what
it means for the oven.

### What changed

The router's Linux bridge now answers ARP requests for its wireless
clients, on both radios, from the router's own ARP cache. Requests for
addresses the router does not know are still broadcast as before, so no
other client's behaviour changes. This is the kernel mechanism behind
hostapd's `proxy_arp` option, set directly because the vendor scripts do
not expose it, and persisted by a script, two hotplug hooks and a boot-time
line so it survives reboots, WiFi reloads and bridge rebuilds.

Two supporting changes: the ARP cache garbage-collection thresholds were
raised, because the cache stood at 118 entries against a limit of 128 and
the proxy answers from that cache; and the router now accepts gratuitous
ARP into it, so entries come back quickly after a router reboot.

**A trap worth knowing.** The Qualcomm WiFi driver has its own proxy ARP
setting, and it is the one a search for "proxy ARP" leads to. It was tried
first and broke things: it intercepted every ARP request and answered none
until its table filled from DHCP, and the printer and the smart plug dropped
off the network. It was on for about twenty seconds and is reverted.

### What this corrects

The correction above was right that nothing on the router was
misconfigured, and wrong to conclude that nothing should change. The
fault is a client that misses some broadcasts some of the time --
intermittent, which is how five probes got five replies on 2026-09-10 and a
laptop failed on 2026-09-15. The router is the one device that always
knows every client's address and never sleeps, so it is the right place to
answer for them. This was what the original section said: *fixed at the
access point or not fixed.*

It also explains why this Pi never showed the fault in everyday use:
`arp-pin` holds the oven as a PERMANENT neighbour entry, so the Pi never
has to ask for it. A fault the Pi has been told to route around cannot be
seen from the Pi.

### Verified

From the Pi, broadcast ARP requests for the oven are answered in 4 to 35 ms,
about as fast as the router answers for itself, while pinging the oven
directly takes 24 to 122 ms. Something much closer than the oven is
answering, one reply per request.

The concern going in was idleness: the kernel appears to answer only for a
client it has recently seen traffic from, roughly the last five minutes by
default, so a quiet oven might drop out and the old failure return. Tested:

    12:44:19 PDT   last contact from the Pi (arp-pin)
    12:46:31       Pi's periodic check paused
    12:51          laptop's ARP entry for the oven deleted
    13:10:46       laptop, entry deleted again, then:
                     ping             4 of 4, 60-79 ms
                     arp -a           entry present
                     GET /            HTTP 200 in 2.5 s
    13:12:01       Pi's periodic check resumed

Twenty-six minutes of silence, and a laptop with no cached entry reached
the oven first time. A capture on the Pi was running at 13:10:46 and never
saw the laptop's request for the oven, which is what the router answering
and not passing the request on to wireless clients would look like -- but
broadcasts reaching this Pi have been unreliable before, so that is
consistent rather than proven. The capture was killed twice for memory, so
roughly 12:52 to 13:07 is unobserved; nothing this host controls touched
the oven in that time.

The page takes 2.5 s from the laptop and 2.6 s from the Pi. The same over
both paths, so that is the oven serving it, not the network.

### Not taken: ESP32 power save

The router agent also suggested disabling power save on the ESP32
(`WiFi.setSleep(false)` or `esp_wifi_set_ps(WIFI_PS_NONE)`). That form does
not apply: the PyPortal's ESP32 runs Adafruit's prebuilt NINA firmware
(1.2.2), not a sketch or an ESP-IDF build of ours. The equivalent is NINA's
`setPowerMode` command, and it was tried on 2026-09-04 and did nothing --
though that test proves less than it looks, because at the time the Pi was
not receiving broadcasts either, so it could not have shown a benefit.

It is not needed now. The benefit it offers beyond ARP is multicast and
broadcast discovery -- mDNS, SSDP -- and the oven uses none of it: its
address is on its idle screen. Revisit only if resolution fails again.

### What stays on the Pi

`arp-pin` and `arp-announce` stay, as insurance that costs nothing.
`arp-announce` is if anything more useful now: the router accepts
gratuitous ARP into its cache, so the Pi's announcements land there.

## The oven could not join, and why (2026-09-15)

After the host processor was reflashed at 14:17 the oven stopped joining
Voxelis. Every attempt failed for hours. The cause is the proxy ARP change
above, and the mechanism is worth knowing because it will do the same to any
device with this network stack.

The access point answers ARP on behalf of its own clients. Before taking an
address DHCP has offered it, this stack broadcasts an ARP request for that
address to check nobody else has it. The access point answered on the oven's
behalf, carrying the oven's own MAC, and the oven refused the address it had
just been given.

The stack was right to. RFC 5227 2.1.1 says that during the probe phase
*any* ARP packet whose sender address is the address being probed means the
address is in use, with no MAC comparison -- the sender-MAC test belongs to
the later phases. This was written here the other way round, claiming lwIP
was the lax one; the router's owner corrected it.

What made the oven the visible casualty is that the poisoned answer needs
the router to hold both an ARP cache entry for the address and a forwarding
entry for that MAC behind a wireless port, a window open only on a quick
rejoin -- and that when a client declines an offer, dnsmasq goes on offering
the same lease to the oven rather than a different address.

From the router's own logs, over the first 37 attempts: 37 authentications,
37 completed WPA2 handshakes, 37 addresses handed out, zero denials -- and
the oven reporting itself unconnected every time. Nothing was refusing it.

Two things this cost, both mine:

* The co-processor's status said `WL_NO_SSID_AVAIL`, which reads as "the
  network is not there". This firmware reports connected only once it has an
  address, so that status cannot tell "not found" from "joined and refused
  the address". It was read as the first.
* Proxy ARP was recommended here on the strength of an idle test that
  checked whether an *existing* client could be found. It never exercised a
  fresh join, which is the one path it breaks. The oven was stable for five
  hours after the change for exactly that reason: it joined at 09:20, the
  flag went on at 09:43, and lease renewals do not repeat the check.

### Reverted on the access point (2026-09-15)

Proxy ARP is off again on both radios, its persistence files removed and the
ARP cache thresholds back to kernel defaults, so nothing answers for the
oven any more. If it returns -- there are devices on this network that
cannot be reflashed -- it will carry a guard against answering address
probes, which is the rule any proxy has to keep: never answer a request
whose sender address is 0.0.0.0.

### What the firmware does about it: nothing, by default

`netconfig` will now read `ip` and `gateway` (and optionally `mask` and
`dns`) for a network in `wifi.json`, and bring-up sets them before joining,
so DHCP never runs and there is no address check to answer. Measured on the
device: joined in 4.5 s, took its address, pinged the host at 40 ms, held.

**It is not configured, and is not the production answer.** A fixed address
is a second place for the network's layout to be recorded and to go stale.
It is here for testing -- proving the diagnosis, and reaching the oven while
the access point is being fixed. A co-processor that will not take the
command falls back to DHCP, and a configuration missing either half is
refused rather than half applied.

### Power save is not the reason, measured (2026-09-15)

With proxy ARP reverted the original fault came straight back: a host with
an empty cache cannot find the oven. The standing suggestion for the device
side is to turn the co-processor's power saving off, on the grounds that
modem sleep is weakest at group-addressed traffic. It was tried on
2026-09-04 and did nothing, but that test was worthless -- nothing on the
network was receiving broadcasts that day, so there was nothing for it to
fix.

This one is not. One association, held open from the REPL for the whole
test, measured from this Pi with its re-pinning timer stopped and its
neighbour entry deleted before each round:

    joined 23:13:51, still connected 23:15:30

    power save default   arping -b 0 of 8     ping 100% loss
    power save off       arping -b 0 of 8     ping 100% loss

    control, same minutes:  bench5 5 of 5,  gateway 5 of 5

The command was accepted -- NINA's `setPowerMode` at 0x17 with a zero byte,
reply `01` -- and the association survived it. It changes nothing. The Pi
resolves every other wireless peer in the same minutes, so the path is not
the Pi's.

### Unicast is perfect, group-addressed is nil (2026-09-15, later)

The power-save rounds above are eight probes each, which can exclude a fix
that works but not a small change. So the question was put differently: is
the oven's receiving broken, or only its answering? `iputils-arping` cannot
answer that -- it sends broadcast until it gets a reply and only then
switches to unicast, so against a peer that never answers, every probe it
sends is a broadcast. `tools/host/arp-probe.py` builds the frame instead,
so the only difference between the two modes is the destination MAC.

    12 probes each, one minute, 2026-09-15 23:56

    bench5    unicast     12 of 12      gateway  unicast   12 of 12
    bench5    broadcast   12 of 12      <- NOT a control, see below
    OVEN      unicast     12 of 12      ICMP to the oven   0% loss
    OVEN      broadcast    0 of 12

Tonight the oven answered 0 of 172 broadcast probes and every unicast one.

So nothing is wrong with its ARP, and its receiver is not weak in general:
frames addressed to it arrive and are answered every time. What it does not
get is group-addressed frames. 802.11 retries a unicast frame until it is
acknowledged and never retries a group-addressed one, so a receiver that
loses frames at random looks perfect on unicast and hopeless on broadcast --
which is also why the access point reports kicking it for excessive
retries.

That reframes the earlier power-save test rather than restoring it: with
broadcast reception at zero, turning power save off did not raise it, and
eight probes are enough to exclude a fix, though not to measure a small
change.

So there is no device-side fix in reach. The oven can be *reached* by a host
that already knows its address, which is what `arp-pin` provides here, and
it can be found by anything if the access point answers for it. That is what
proxy ARP bought, and why it is worth having back with a guard against
answering address probes.

Also worth recording: the first join attempt returned status 4 and the
second succeeded, five seconds apart. That is the behaviour `radio.py`
already documents and the reason `JOIN_ATTEMPTS` is 3. A single-attempt
probe reads it as a dead network.

### It is not the oven: nothing on this radio hears a broadcast (2026-09-16)

Every "wireless control" above is withdrawn. bench5 is on **5 GHz channel
36**, a different BSSID. Measuring it proved that the 5 GHz group path works
and that bench5 can send a unicast reply. It never tested the 2.4 GHz group
path the oven lives on.

This is the second time this file has recorded that mistake. The first was a
"wireless host that works" which turned out to be eridani, on the wire. The
rule that follows from doing it twice: **a control is not a control until
its band and BSSID are written down next to the number.**

What a real measurement says. The bench Pi -- Broadcom radio, Linux, power
save off, 2.4 GHz channel 11, the same BSS as the oven -- listening
promiscuously for 70 s:

    group-addressed frames received, any source, any protocol      0
    of which, 20 UDP broadcasts sent from WIRED eridani during it  0 of 20

Not one ARP, mDNS, DHCP or anything else. So two clients that share nothing
but this BSS, an ESP32 and a Broadcom radio with power save off, are both
blind to group-addressed frames.

That exonerates the oven and everything inside it -- the SPI link, NINA's
buffering, CircuitPython's polling, the antenna, the enclosure, the heater
-- and it retires the "impaired receive path" reading, which never fit the
arithmetic anyway: group frames go out at the most robust basic rate and
unicast at a high MCS, and the oven passes 100% of the fragile ones while
losing the robust ones.

#### But six other hosts hear broadcasts perfectly

Written twenty minutes after the section above, because it qualifies it.
Every host this bench has a MAC for, 8 broadcast and 8 unicast ARP probes
each:

    10.20.10.1     8/8 broadcast     10.20.10.148   8/8 broadcast
    10.20.10.4     8/8 broadcast     10.20.10.162   8/8 broadcast  (wired)
    10.20.10.145   8/8 broadcast     10.20.10.220   8/8 broadcast
                   (5 GHz ch 36)
    10.20.10.242   0/8 broadcast, 8/8 unicast                      (the oven)

So group delivery works for six hosts and fails only for the oven, which is
the opposite of what the previous section implies on its own.

What survives is narrower and still decides it. The bands of .4, .148 and
.220 are unknown; bench5 is 5 GHz, eridani is wired, .1 is the router. The
only two hosts *known* to be on 2.4 GHz channel 11 are the oven and this Pi,
and both are deaf to group-addressed frames. This Pi cannot resolve the rest
-- its radio is 2.4 GHz only, so it cannot scan 5 GHz or read another
client's band.

So the pivot is one command on the access point: list the 2.4 GHz stations
with their band, then probe a confirmed 2.4 GHz client that is not ours.

* If .4, .148 and .220 are all 5 GHz or wired, both 2.4 GHz clients are deaf
  and the fault is that radio's group delivery -- which also breaks mDNS,
  SSDP and broadcast DHCP for anything else that joins it, and no ARP proxy
  is the right answer to that.
* If any one of them is on 2.4 GHz and hears broadcasts, group delivery is
  fine, the reading above is dead, and it is per-station -- where the group
  key is the first suspect, since the GTK carries group frames and the PTK
  carries the unicast that works.

### It is the access point's 2.4 GHz radio (2026-09-16, from its operator)

The router's operator measured four clients on that radio, 10 broadcast ARP
probes each from `br-lan`, unicast perfect for all four:

    printer          11 of 10        (replies can exceed probes; it answers twice)
    bench Pi          1 of 10
    the oven          1 of 10
    Kasa smart plug   1 of 10

Three unrelated clients -- an ESP32, a mainstream Linux host and a smart
plug -- all receive about a tenth of group-addressed frames, and power save
does not predict which ones fail. So this is not the oven, and the
co-processor's beacon and DTIM handling is no longer worth investigating for
this fault.

Their lead: the radio is configured for 40 MHz but operating at 20 MHz
because eight associated stations advertise 40 MHz intolerance. Testing it
needs a radio reload.

**Both group-to-unicast escapes are closed.** Qualcomm's multicast
enhancement is compiled out of that firmware -- setting it returns success
while the value stays 0 and the kernel logs the parameter as unsupported --
and the oven advertises no 802.11v DMS support at every association, as do
two phones on the network. So there is no mechanism on this AP to deliver a
group frame as unicast, which was the one fix that would have covered ARP,
mDNS and SSDP together.

#### Ten minutes, zero group frames

Measured here to put a number on the same question from the receiving side:

    00:27:43 to 00:37:43 PDT, 600 s, every group-addressed frame from
    anyone but us, on 2.4 GHz channel 11, associated throughout, unicast
    to the gateway 3 of 3 immediately after

    received: 0

No ARP, mDNS, SSDP or DHCP, on a network carrying a printer, phones and a
plug. At the 10% the access point measured for this same host, dozens would
be expected. So the two measurements of one host disagree, which now matters
more than the oven does: theirs is responder-side (a probe that needs the
host to receive *and* answer), mine is receiver-side (every group frame the
driver accepts). Neither should be near zero at 10%.

What remains unreconciled: from this Pi, station-originated broadcast ARP to
the oven is 0 of 172, against their 1 of 10 from the bridge. The candidate
was origin -- theirs start on `br-lan`, mine start on a station inside the
same BSS -- but six other hosts answer my station-originated probes 8 of 8,
which weakens it. Their per-client IPs will settle whether the two methods
even agree about the same client.

## Resolved: the radio had been up 155 days (2026-09-16)

The access point's 2.4 GHz radio had quietly degraded. Group-addressed
frames reached most of its stations **exactly one time in ten**, with
essentially no variance, while unicast stayed perfect. `wifi down wifi0 &&
wifi up wifi0` fixed it in forty seconds. Nothing was misconfigured; every
setting was as it had been.

Confirmed here afterwards, 30 broadcast ARP probes at 1 s with the printer
probed in the same window as a reference:

    oven      30 of 30     gaps all 1     (0 of 172 before the restart)
    printer   30 of 30     gaps all 1
    oven unicast control 10 of 10

And on this Pi, 90 s passive: **548** group-addressed frames from 18
senders, 114 of them mDNS to 224.0.0.251 -- where the identical test read 0
in 70 s and 0 in 600 s the night before. Multicast discovery had been dead
on that radio, presumably for months, and nobody had attributed it.

### What found it, and what hid it

The totals hid this for three days. Every party measured a rate -- 5 of 48,
0 of 172, 1 of 10 -- and argued about whose number was right. The fault was
visible the moment anyone asked whether the successes were *clustered or
uniform*: gaps of 10, 10, 11, 10, 10 with near-zero variance cannot come
from random loss. That took ninety seconds to measure and no amount of
configuration review would have produced it.

`tools/host/arp-probe.py` prints the gaps for this reason. Expect a
recurrence as the radio's uptime grows: when discovery starts failing again,
probe a client known to work alongside the one that does not, and compare
the gap patterns rather than the totals. A clean 1-in-N is this fault, and
the fix is on the access point -- `wifi down wifi0 && wifi up wifi0`, since
`wifi reload` there is a no-op that looks like a clean negative result.

Wrong turns worth keeping, all ours:

* Proxy ARP was recommended on an idle test that never exercised a fresh
  join, which is the one path it broke.
* A 5 GHz host was used as a "wireless control" twice, after this same file
  had already recorded that error once with a wired host. A control is not a
  control until its band and BSSID are written next to the number.
* A BSS-wide conclusion was published here and corrected within the hour.

### Open: the oven does not notice when it falls off the network

When the radio restarted, the oven lost its association and **never came
back**. For eight hours it reported `network=10.20.10.242`, a live web
service and no fault, while answering nothing and being absent from the
access point's station table. Restarting `code.py` rejoined it in seconds.

Nothing in the firmware checks that the radio is still associated once
bring-up has succeeded. It needs a liveness check that re-runs bring-up when
the co-processor stops answering -- cheap to write, but it is frozen code,
so it needs a rebuild and a reflash. Until then, an oven that has silently
left the network is indistinguishable, from its own console, from one that
is on it.
