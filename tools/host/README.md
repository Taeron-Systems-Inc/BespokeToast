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

## The ARP workarounds are gone

`arp-announce` and `arp-pin` used to run here every three minutes, holding
neighbour entries for peers this host could not resolve by asking. They were
built for a fault that turned out to be the access point's radio delivering
one group frame in ten, fixed on 2026-09-16 by restarting it. Resolution
works normally now, so they were removed.

They were also wrong to keep for a second reason: the peer list and the
remembered MACs were specific to one network, and on any other network this
host joins they would pin entries that mean nothing.

## arp-probe.py

Sends ARP requests with an Ethernet destination you choose, and counts the
replies. `arping` cannot do this job: it starts with broadcast and only
switches to unicast once a reply arrives, so against a peer that never
answers, every probe it sends is broadcast and the two cases look the same.

    sudo python3 tools/host/arp-probe.py 10.20.10.237 12 \
        "oven unicast,10.20.10.242,<mac>" "oven broadcast,10.20.10.242,"

Always include a peer that works as a control. That is what showed the
oven answering unicast 12 of 12 and broadcast 0 of 12 in the same minute.

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
