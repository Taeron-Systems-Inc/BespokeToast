"""Does heating BEFORE the run clock starts fix the warm-start lag?

Timing, not gain. The observer is re-implemented inline so this does not
depend on the module being rewritten alongside it. Old feed-forward and old
PID throughout -- the only thing that changes is whether the element is
charged before the profile's clock is allowed to run."""
import json, os, sys
ROOT=__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))))
sys.path.insert(0, ROOT+"/firmware"); sys.path.insert(0, ROOT+"/tests")
from oven.controller import FeedForward, PID, TimeProportional, clamp, predict_peak
from oven.metrics import RunMetrics
from oven.profile import Profile
D=json.load(open(ROOT+"/data/oven-characterisation.json"))
TA=23.5
a,b,c,d = 41.4411, 0.07344, 0.002907, 0.003680
G, BETA, GAMMA = c*a, b+c, c*d

class Plant(object):
    def __init__(self, start_c, scale=1.0): self.tc=start_c; self.z=0.0; self.scale=scale
    def read(self): return int(self.tc*16)/16.0
    def step(self, on):
        u=1.0 if on else 0.0
        self.z += (G*self.scale*u - BETA*self.z + GAMMA*(self.tc-TA))*0.25
        self.tc += (self.z - d*(self.tc-TA))*0.25

class Obs(object):
    def __init__(self): self.z=0.0; self.hist=[]; self.lt=None; self.lu=0.0
    def rate(self):
        h=self.hist
        if len(h)<2: return None
        t1,c1=h[-1]
        for t0,c0 in h:
            if t1-t0<=3.0: return None if t1-t0<1.5 else (c1-c0)/(t1-t0)
        return None
    def update(self,t,temp,u):
        self.hist.append((t,temp))
        while len(self.hist)>2 and self.hist[0][0]<t-6.0: self.hist.pop(0)
        if self.lt is not None:
            dt=t-self.lt
            self.z += (G*self.lu - BETA*self.z + GAMMA*(temp-TA))*dt
            r=self.rate()
            if r is not None: self.z += 0.15*((r + d*(temp-TA)) - self.z)
        self.lt=t; self.lu=u
        return self.z

def run(p, start_c, precharge, scale=1.0, max_pre=28.0):
    plant=Plant(start_c, scale); obs=Obs()
    ff=FeedForward(heating_rates=D["heating_rate_c_per_s"], cooling_rates=D["cooling_rate_c_per_s"])
    pid=PID(kp=0.22,ki=0.004,kd=0.5,i_max=0.6,i_min=-0.6); pid.reset()
    entry=p.entry_time_for(start_c)
    tpo=TimeProportional()
    # --- pre-charge phase: wall clock runs, profile clock does not ---
    wall=0.0; pre_s=0.0; applied=0.0
    if precharge:
        # what the opening needs: the element contribution for the curve's
        # slope at entry, at the current temperature
        need = p.slope_at(entry) + d*(start_c-TA)
        tpo.reset(wall)
        while pre_s < max_pre:
            temp=plant.read(); obs.update(wall,temp,applied)
            if obs.z >= 0.9*need: break
            on=tpo.update(wall,1.0); applied=1.0 if on else 0.0
            plant.step(on); wall+=0.25; pre_s+=0.25
        # re-enter wherever the oven now is
        entry=p.entry_time_for(plant.read())
    # --- the run ---
    t=entry; tpo.reset(t); m=RunMetrics(p.liquidus_c or 0.0)
    coasting=False; last=None; rate=0.0; errs=[]; peak_t=p.peak[0]
    while t<=p.duration:
        temp=plant.read()
        if last is not None: rate=(temp-last[1])/(t-last[0])
        last=(t,temp); target=p.target_at(t); m.add(t,temp)
        if t<=peak_t: errs.append(temp-target)
        obs.update(t,temp,applied)
        if not coasting and t<=peak_t and predict_peak(temp,rate,D["coast_tau_s"])>=p.peak[1]: coasting=True
        if coasting and temp<target-1.0: coasting=False; pid.reset()
        duty=0.0 if coasting else clamp(ff.duty_for(target,p.slope_at(t))+pid.update(t,target,temp),0.0,1.0)
        on=tpo.update(t,duty); applied=1.0 if on else 0.0
        plant.step(on); t+=0.25
    return dict(rms=(sum(e*e for e in errs)/len(errs))**0.5, worst=min(errs),
                peak=m.peak_c, tal=m.time_above_liquidus, pre=pre_s)

snl=Profile.load(ROOT+"/firmware/profiles/ts391snl.json")
lt=Profile.load(ROOT+"/firmware/profiles/ts391lt.json")
print("%-8s %-8s %5s | %8s %7s %6s %5s | %8s %7s %6s %5s %6s" % ("profile","plant","start","rms","worst","peak","tal","rms","worst","peak","tal","pre s"))
print("%-8s %-8s %5s | %-30s | %s" % ("","","","      -- no pre-charge --","      -- with pre-charge --"))
for scale,pn in ((1.0,"nominal"),(0.8,"g*0.8"),(1.2,"g*1.2")):
    for prof,start in ((snl,25.0),(snl,34.1),(snl,59.4),(lt,28.4),(lt,45.0)):
        o=run(prof,start,False,scale); n=run(prof,start,True,scale)
        print("%-8s %-8s %4.0fC | %8.2f %7.1f %6.1f %5.0f | %8.2f %7.1f %6.1f %5.0f %6.1f"
              % (prof.name[:8],pn,start,o["rms"],o["worst"],o["peak"],o["tal"],n["rms"],n["worst"],n["peak"],n["tal"],n["pre"]))
