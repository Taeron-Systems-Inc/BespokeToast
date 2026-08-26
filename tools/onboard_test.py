#!/usr/bin/env python3
"""Import and exercise the new firmware ON the device, without deploying it.

Copies oven/, profiles/ and assets/ to CIRCUITPY but deliberately leaves
code.py and boot.py alone, so the board still boots the firmware it has
always booted. Everything new is then imported and driven from the REPL.

What this is actually testing: whether the code runs on CircuitPython 8.0.5
at all -- syntax the compiler accepts, imports that resolve, and whether it
fits in a SAMD51's RAM with displayio already loaded. None of that is visible
from CPython.

The relay is driven low at the start and its state is asserted throughout.
No profile is started, so nothing can request heat.
"""
import os, shutil, subprocess, sys, time, serial

BASE="/tmp/claude-1001/-home-kaan/e3791a80-a239-41f2-9f58-11ee423d796e/scratchpad"
SRC="/srv/repo/BespokeToast-rebuild/firmware"
DATA="/srv/repo/BespokeToast-rebuild/data/oven-characterisation.json"
MNT="/mnt/circuitpy"
PORT="/dev/ttyACM0"
log=open(BASE+"/onboard.log","w")

def note(m):
    print(m, flush=True); log.write(m+"\n"); log.flush()

class Repl:
    def __init__(s_,port):
        s_.s=serial.Serial(port,115200,timeout=0.2); s_.s.reset_input_buffer()
    def _rd(s_,n=8192):
        d=s_.s.read(n).decode("utf-8","replace")
        if d: log.write(d); log.flush()
        return d
    def enter_raw(s_):
        for _ in range(3):
            s_.s.write(b"\x03"); s_.s.flush(); time.sleep(0.25); s_._rd()
        s_.s.write(b"\x01"); s_.s.flush(); time.sleep(0.8)
        return "raw REPL" in s_._rd()
    def run(s_,code,timeout=25):
        s_.s.write(code.encode()+b"\x04"); s_.s.flush(); time.sleep(0.4)
        ack=s_._rd()
        if "OK" not in ack: return False,"no ack: %r"%ack[:100]
        buf=ack.split("OK",1)[1]; t0=time.monotonic()
        while time.monotonic()-t0<timeout:
            if "\x04" in buf: break
            c=s_._rd()
            if c: buf+=c
            else: time.sleep(0.05)
        return True, buf.replace("\x04","").strip()
    def restore(s_):
        s_.s.write(b"\x02"); s_.s.flush(); time.sleep(0.4)
        s_.s.write(b"\x04"); s_.s.flush(); time.sleep(3.0); s_._rd(); s_.s.close()

r=Repl(PORT)
try:
    note("[repl] taking control so the copy cannot race auto-reload")
    if not r.enter_raw(): note("!! no raw REPL"); sys.exit(1)
    ok,out=r.run("import board,digitalio\n"
                 "p=digitalio.DigitalInOut(board.D4)\n"
                 "p.direction=digitalio.Direction.OUTPUT\n"
                 "p.value=False\n"
                 "p.deinit()\n"
                 "print('RELAY-LOW')")
    note("    "+out)

    note("[copy] remounting CIRCUITPY writable")
    subprocess.run(["mount","-o","remount,rw",MNT],check=True)
    # copyfile, not copy2 or copytree: FAT cannot take the ownership and
    # timestamp metadata those try to set, and copytree aborts on it after
    # having already written the files.
    def put(src, dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    n=0
    for sub in ("oven","profiles","assets"):
        base=os.path.join(SRC,sub)
        for root,dirs,names in os.walk(base):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in names:
                if f.endswith(".pyc"): continue
                rel=os.path.relpath(os.path.join(root,f), SRC)
                put(os.path.join(root,f), os.path.join(MNT,rel)); n+=1
    put(DATA, os.path.join(MNT,"characterisation.json"))
    subprocess.run(["sync"],check=True)
    note("    copied %d files; code.py and boot.py untouched" % (n+1))
    subprocess.run(["mount","-o","remount,ro",MNT],check=True)
    note("    remounted read-only")

    note("[import] loading every module on the device")
    ok,out=r.run("""
import gc, sys
gc.collect()
before = gc.mem_free()
import oven.hal, oven.profile, oven.safety, oven.controller, oven.metrics, oven.app
from oven.ui import theme, layout
gc.collect()
print("IMPORT-OK free_before=%d free_after=%d cost=%d" % (before, gc.mem_free(), before-gc.mem_free()))
""", 40)
    note("    "+out)

    note("[profiles] parsing the shipped profiles on the device")
    ok,out=r.run("""
import gc
from oven.profile import Profile
import os
names = [n for n in os.listdir("/profiles") if n.endswith(".json")]
for n in sorted(names):
    p = Profile.load("/profiles/" + n)
    print("PROFILE %-22s %3d pts  %4.0f s  peak %.0f C  TAL %.0f s" %
          (p.name, len(p.points), p.duration, p.peak[1], p.time_above(p.liquidus_c)))
gc.collect()
print("free=%d" % gc.mem_free())
""", 40)
    for line in out.split("\n"): note("    "+line.strip())

    note("[hardware] real sensor through the new HAL")
    ok,out=r.run("""
from oven.hardware import Hardware, cpu_temperature
hw = Hardware()
rd = hw.sensor.read()
print("READ hot=%s cold=%s faults=%d ok=%s relay_on=%s cpu=%s" %
      (rd.hot, rd.cold, rd.faults, rd.ok, hw.relay.is_on(), cpu_temperature()))
""", 30)
    note("    "+out)

    note("[app] running the state machine idle -- no profile, so no heat path")
    ok,out=r.run("""
import gc, time
from oven.app import App
from oven.controller import Controller, FeedForward, PID
import json
d = json.load(open("/characterisation.json"))
ff = FeedForward(heating_rates=d["heating_rate_c_per_s"], cooling_rates=d["cooling_rate_c_per_s"])
app = App(hw.relay, hw.sensor, hw.clock,
          lambda p: Controller(p, coast_tau_s=d["coast_tau_s"], feed_forward=ff, pid=PID()))
ticks = 0
energised = False
t0 = time.monotonic()
while time.monotonic() - t0 < 8.0:
    if app.tick(): ticks += 1
    if hw.relay.is_on(): energised = True
gc.collect()
print("APP state=%s ticks=%d relay_ever_on=%s temp=%.2f free=%d" %
      (app.state, ticks, energised, app.temperature, gc.mem_free()))
""", 45)
    note("    "+out)

    note("[ui] building screens on the device")
    ok,out=r.run("""
import gc
from oven.ui import layout as L
gc.collect(); b = gc.mem_free()
s1 = L.home(24.5, "SAC305 (this oven)", True)
s2 = L.running(212.0, 215.0, 300, 180, "reflow", 42, 217, 0.6, True)
s3 = L.fault("thermocouple fault: open circuit")
gc.collect()
print("UI home=%d running=%d fault=%d cost=%d free=%d" %
      (len(s1), len(s2), len(s3), b-gc.mem_free(), gc.mem_free()))
""", 30)
    note("    "+out)

    note("[final] relay state")
    ok,out=r.run("print('RELAY-ON=%s' % hw.relay.is_on())")
    note("    "+out)
finally:
    try:
        subprocess.run(["mount","-o","remount,ro",MNT])
    except Exception:
        pass
    try:
        r.restore(); note("[restore] original code.py running again")
    except Exception as e: note("!! restore: %r" % e)
    log.close()
