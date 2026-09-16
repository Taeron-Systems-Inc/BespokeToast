"""Send ARP requests with an Ethernet destination we choose, and count replies.

`arping` cannot do this job: it starts with broadcast and only switches to
unicast once a reply arrives, so against a peer that never answers, every
probe it sends is a broadcast and the two cases look identical.

    sudo python3 arp-probe.py 10.20.10.237 12 \
        "oven unicast,10.20.10.242,34:ab:..." "oven broadcast,10.20.10.242,"

Set VERBOSE=1 for the per-probe pattern, and GAP for the spacing in seconds.

The gaps matter more than the total. On 2026-09-16 this access point's
2.4 GHz radio was delivering group-addressed frames exactly one time in ten,
with no spread at all -- random loss cannot do that, and the totals alone
hid it. The clean 1-in-N is the signature.

Always include a peer known to work as a control, and write its band and
BSSID next to the number: a 5 GHz peer says nothing about a 2.4 GHz fault.
"""
import binascii
import os
import select
import socket
import struct
import sys
import time

ETH_P_ARP = 0x0806


def mac_bytes(text):
    return binascii.unhexlify(text.replace(":", "").replace("-", ""))


def probe(iface, src_ip, target_ip, dst_mac, count, gap):
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ARP))
    s.bind((iface, ETH_P_ARP))
    src_mac = s.getsockname()[4]
    src = socket.inet_aton(src_ip)
    tpa = socket.inet_aton(target_ip)
    dst = mac_bytes(dst_mac) if dst_mac else b"\xff" * 6
    frame = (dst + src_mac + struct.pack("!H", ETH_P_ARP)
             + struct.pack("!HHBBH", 1, 0x0800, 6, 4, 1)
             + src_mac + src + b"\x00" * 6 + tpa)
    hits = []
    started = time.monotonic()
    for i in range(count):
        s.send(frame)
        deadline = time.monotonic() + gap
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                break
            ready, _, _ = select.select([s], [], [], left)
            if not ready:
                break
            pkt = s.recv(2048)
            if len(pkt) < 42:
                continue
            if struct.unpack("!H", pkt[20:22])[0] == 2 and pkt[28:32] == tpa:
                hits.append((i + 1, round(time.monotonic() - started, 2)))
                break
    s.close()
    return hits


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    iface = os.environ.get("IFACE", "wlan0")
    gap = float(os.environ.get("GAP", "1.0"))
    src_ip, count = argv[0], int(argv[1])
    for spec in argv[2:]:
        label, ip, mac = spec.split(",")
        hits = probe(iface, src_ip, ip, mac or None, count, gap)
        print("  %-28s %2d of %2d" % (label, len(hits), count))
        if os.environ.get("VERBOSE") and hits:
            idx = [h[0] for h in hits]
            gaps = [b - a for a, b in zip(idx, idx[1:])]
            print("       replied on probes: %s"
                  % ", ".join(str(i) for i in idx))
            if gaps:
                clean = len(set(gaps)) == 1 and gaps[0] > 1
                print("       gaps: %s%s"
                      % (", ".join(str(g) for g in gaps),
                         "   <- CLEAN 1-in-%d, the degraded-radio signature"
                         % gaps[0] if clean else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
