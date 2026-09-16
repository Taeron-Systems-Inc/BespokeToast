"""Send ARP requests with an Ethernet destination we choose, and count replies.

iputils-arping only switches to unicast after a reply arrives, so on a peer
that never answers, every probe it sends is a broadcast. This builds the
frame itself: the only difference between the two modes here is the
destination MAC in the Ethernet header.
"""
import binascii, select, socket, struct, sys, time

IFACE = "wlan0"
ETH_P_ARP = 0x0806


def mac_bytes(text):
    return binascii.unhexlify(text.replace(":", "").replace("-", ""))


def probe(target_ip, dst_mac, count, gap=1.0):
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ARP))
    s.bind((IFACE, ETH_P_ARP))
    src_mac = s.getsockname()[4]
    src_ip = socket.inet_aton(SRC_IP)
    tpa = socket.inet_aton(target_ip)
    dst = mac_bytes(dst_mac) if dst_mac else b"\xff" * 6
    frame = (dst + src_mac + struct.pack("!H", ETH_P_ARP)
             + struct.pack("!HHBBH", 1, 0x0800, 6, 4, 1)
             + src_mac + src_ip + b"\x00" * 6 + tpa)
    replies = 0
    for _ in range(count):
        s.send(frame)
        deadline = time.monotonic() + gap
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                break
            r, _, _ = select.select([s], [], [], left)
            if not r:
                break
            pkt = s.recv(2048)
            if len(pkt) < 42:
                continue
            op = struct.unpack("!H", pkt[20:22])[0]
            if op == 2 and pkt[28:32] == tpa:
                replies += 1
                break
    s.close()
    return replies


if __name__ == "__main__":
    SRC_IP = sys.argv[1]
    count = int(sys.argv[2])
    for label, ip, mac in [tuple(a.split(",")) for a in sys.argv[3:]]:
        got = probe(ip, mac or None, count)
        print("  %-28s %2d of %2d" % (label, got, count), flush=True)
