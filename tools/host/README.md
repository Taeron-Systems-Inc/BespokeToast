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

## arp-announce.service and .timer

A hedge against the same failure, whatever its cause. ARP is normally a
question: a machine that wants to reach you broadcasts "who has this
address?" and waits for a reply. If the reply is missed the asker concludes
there is no route. This announces the mapping unprompted every three
minutes, so peers' caches stay warm and never have to ask.

Needs `iputils-arping`. The address in the unit is this host's; change it if
the host changes.

    sudo cp tools/host/arp-announce.* /etc/systemd/system/
    sudo systemctl enable --now arp-announce.timer
