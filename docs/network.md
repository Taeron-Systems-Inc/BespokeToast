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

### Nothing on this access point receives a broadcast

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

Both are associated to the same BSSID, 76:16:c1:0a:6d:54, on channel 11,
at -35 and -47 dBm. Neither is the odd one out.

**This is the access point, and it is not something the firmware can fix.**
The oven cannot answer a request it never receives. Worth looking at on the
AP: multicast-to-unicast conversion, broadcast and multicast rate limiting,
IGMP or ARP snooping, proxy ARP, and any "multicast enhancement" setting.

Until then, a host reaches the oven by being told its address once:

    sudo ip neigh replace 10.20.10.242 lladdr 34:ab:95:49:c9:bc dev wlan0 nud permanent

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
