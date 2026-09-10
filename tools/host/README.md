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

Measured from this Pi: a cold-cache ping of **wired** eridani resolves in one
go, 3 of 3, with the entry deleted first. **Wireless** bench5 and the oven do
not resolve at all. So a broadcast leaving this host reaches the wire and not
the air, which decides what each half can do.

**`arp-announce`** says "this address is at this MAC" without being asked, so
peers never have to ask. That reaches the wired segment -- it is what stopped
eridani, the build host, losing the oven. It will not reach another wireless
client, and is not pretending to.

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
  and had to be seeded back by hand from the MAC in `docs/network.md`.

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

### What this does not fix

The oven, and any other wireless client, is still unreachable from a machine
with a cold cache -- a phone, a laptop that has just woken. That is the
access point's to fix: proxy ARP, or whatever the vendor calls multicast
enhancement or broadcast filtering. See `docs/network.md`. This keeps the two
machines that do the work able to find each other; it is not a cure.
