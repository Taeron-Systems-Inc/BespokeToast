# What runs on the bench host

None of this is needed for the oven to work. The oven runs standalone; this
is the machine that programs it and keeps the working copy. It is here
because it was previously untracked, living only on one SD card that was
92 % full and had already gone read-only once.

## toaster

The session launcher. Runs the assistant inside a detached tmux server so
the session survives an SSH disconnect, and falls back to resuming the
recorded conversation by id if tmux itself is gone.

    install -m 755 tools/host/toaster ~/bin/toaster

## wifi-no-powersave.service

WiFi power save left this host associated but asleep, so it missed broadcast
ARP requests: other machines got "Destination Host Unreachable" while it was
up and healthy. Turning it off also cut ping jitter from 3.16 ms mean
deviation to 0.83 ms.

    sudo cp tools/host/wifi-no-powersave.service /etc/systemd/system/
    sudo systemctl enable --now wifi-no-powersave.service

## arp-announce, arp-pin and the timer

Two halves of one problem, run together every three minutes by
`arp-announce.timer`. They are not symmetrical, because the fault is not.

Measured from this Pi on 2026-09-10, and **the second half of this was
wrong** -- see the correction in `docs/network.md`. A cold-cache ping of
wired eridani resolved 3 of 3 with the entry deleted first, and wireless
bench5 and the oven appeared not to resolve at all. They do: five broadcast
probes get five replies from both. The failing observations were one ping
check and a single `arping` with a two second timeout, against a link that
runs at 26 to 1115 ms.

Both halves are still worth having, for a different reason than the one they
were written for: the fault is intermittent and unexplained rather than a
standing property of the access point, which is exactly the case where
holding a mapping earns its keep.

**`arp-announce`** says "this address is at this MAC" without being asked, so
peers never have to ask -- on the wire and, on the evidence since, over the
air too.

It reads the address off the interface rather than having it written into the
unit. The version that hardcoded `10.20.10.237` would have gone on announcing
that after any DHCP change, and announcing the *wrong* mapping is worse than
announcing none, because peers cache that too.

**`arp-pin`** covers what announcing cannot: wireless peers this host must be
able to reach. It holds their entries from MACs the kernel has already
learned, never from one this file invents, verifies each pass with four
pings, and remembers what it learned in `/var/lib/toaster/arp-known`.

A peer that goes silent for three consecutive passes is **demoted to STALE,
not deleted**. That distinction cost two rounds to get right:

- Releasing after one failed check of two pings dropped the oven on the first
  production run. Its wireless link had already been measured at 95 to
  1115 ms with a third of packets lost -- a peer that is briefly slow is the
  normal case, not a departed one.
- Releasing by deleting is a one-way door here. A wireless peer that has been
  forgotten cannot be resolved again, because resolving is exactly what does
  not work. The oven went from pinned to permanently unreachable in one pass,
  and had to be seeded back by hand from its MAC, which the Pi now keeps in
  `/var/lib/toaster/arp-known`.

It also seeds the entry from what it remembers *before* it verifies. The
verification is a ping, and a ping cannot leave the host while the kernel's
entry is FAILED, which is the state an unresolvable peer leaves behind. Until
2026-09-15 the check could therefore never pass in the one case it existed
for, and the script reported that it was holding a mapping it had not
installed.

Demoting keeps the mapping usable -- the kernel sends to a stale entry
immediately -- while letting it be replaced the moment the peer says
anything, which is how a machine that changes its NIC recovers by itself.

Needs `iputils-arping`.

    sudo install -m 755 tools/host/arp-announce tools/host/arp-pin /usr/local/sbin/
    sudo install -d /etc/toaster
    sudo cp tools/host/arp-peers.example /etc/toaster/arp-peers   # then edit
    sudo cp tools/host/arp-announce.* /etc/systemd/system/
    sudo systemctl enable --now arp-announce.timer

`/etc/toaster/arp-peers` lists addresses only, one per line. No MAC addresses
live in this repository: the pin only ever holds one the kernel has learned,
so the peer list cannot make a host believe something untrue.

## arp-probe.py

Sends ARP requests with an Ethernet destination you choose, and counts the
replies. `arping` cannot do this job: it starts with broadcast and only
switches to unicast once a reply arrives, so against a peer that never
answers, every probe it sends is broadcast and the two cases look the same.

    sudo python3 tools/host/arp-probe.py 10.20.10.237 12 \
        "oven unicast,10.20.10.242,<mac>" "oven broadcast,10.20.10.242,"

Always include a peer that works as a control. That is what showed the
oven answering unicast 12 of 12 and broadcast 0 of 12 in the same minute.

## group-canary

Hourly check that the access point still delivers group-addressed frames,
installed as `group-canary.timer`. It probes the printer at 10.20.10.234 --
the reference client, which kept answering every probe even while the radio
was degraded -- and logs the total and the gap pattern to
`/var/lib/toaster/group-canary.log`. On the first hour it sees 4 or fewer of
12 it writes `/var/lib/toaster/group-canary-ALERT.txt` and sends the same
text to any logged-in session, once per episode rather than once per hour.
The alert carries the fix with it, because the fix is on the access point
and not here: `wifi down wifi0 && wifi up wifi0`, since `wifi reload` there
is a no-op that looks like a clean negative result.

    sudo install -m 755 tools/host/group-canary /usr/local/sbin/
    sudo cp tools/host/group-canary.* /etc/systemd/system/
    sudo systemctl enable --now group-canary.timer

A clean 1-in-N gap pattern is the signature of the 2026-09-16 fault, and the
fix for that is a radio restart on the access point, not anything here.

### What fixed it for everyone else

Since 2026-09-15 the router answers ARP for its wireless clients (bridge
proxy ARP), which fixes resolution for every device on the network, phones
included. See the last section of `docs/network.md`. An earlier version of
this README said nothing on the access point needed fixing; that was wrong.

These two units stay as insurance. `arp-announce` is more useful than it
was, because the router now accepts gratuitous ARP into its cache. Know
that `arp-pin` also hides the fault from this host: with the oven held as a
permanent entry, the Pi never has to ask for it, which is why a laptop could
fail while the Pi never did. Test resolution from some other machine.
