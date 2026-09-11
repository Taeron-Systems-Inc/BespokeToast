"""Old feed-forward vs element feed-forward, same PID, same TPO, same
profile, on two plants: the two-state model the new FF was fitted to, and
the one-state model the old FF was fitted to. A design that only wins on
its own plant has not won."""
import json, os, sys
ROOT=__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))))
sys.path.insert(0, ROOT+"/firmware"); sys.path.insert(0, ROOT+"/tests")
from oven.controller import FeedForward, PID, TimeProportional, clamp, predict_peak
from oven.elementff import ElementModel, ElementFeedForward
from oven.metrics import RunMetrics
from oven.profile import Profile
from sim.measured import MeasuredOven
D=json.load(open(ROOT+"/data/oven-characterisation.json"))
TA=23.5
MODEL=ElementModel.from_two_state(41.4411, 0.07344, 0.002907, 0.003680, TA)

class TwoStateOven(object):
    """The identified plant, integrated at 0.25 s. scale perturbs g."""
    def __init__(self, start_c, scale=1.0, dt=0.25):
        self.tc=start_c; self.z=0.0; self.dt=dt; self.scale=scale
    def read(self): return int(self.tc*16)/16.0
    def step(self, relay_on):
        m=MODEL; u=1.0 if relay_on else 0.0
        dz=(m.g*self.scale*u - m.beta*self.z + m.gamma*(self.tc-TA))
        self.z+=dz*self.dt
        self.tc+=(self.z - m.d*(self.tc-TA))*self.dt

def run(profile, plant, use_element, start_c, gains):
    p=profile
    entry=p.entry_time_for(start_c)
    if use_element:
        ff=ElementFeedForward(MODEL, k_z=gains["k_z"]); ff.reset()
    else:
        ff=FeedForward(heating_rates=D["heating_rate_c_per_s"], cooling_rates=D["cooling_rate_c_per_s"])
    pid=PID(kp=gains["kp"],ki=gains["ki"],kd=gains["kd"],i_max=0.6,i_min=-0.6); pid.reset()
    tpo=TimeProportional(); tpo.reset(entry)
    m=RunMetrics(p.liquidus_c or 0.0)
    t=entry; coasting=False; last=None; rate=0.0; applied=0.0
    errs=[]; peak_t=p.peak[0]
    while t<=p.duration:
        temp=plant.read()
        if last is not None: rate=(temp-last[1])/(t-last[0])
        last=(t,temp)
        target=p.target_at(t)
        m.add(t,temp)
        if t<=peak_t: errs.append(temp-target)
        if use_element:
            ff.observe(t, temp, applied)
        # replicate Controller.duty_for
        if not coasting and t<=peak_t:
            if predict_peak(temp, rate, D["coast_tau_s"]) >= p.peak[1]: coasting=True
        if coasting:
            if temp < target-1.0: coasting=False; pid.reset()
            else: duty=0.0
        if not coasting:
            duty=clamp(ff.duty_for(target, p.slope_at(t)) + pid.update(t, target, temp), 0.0, 1.0)
        on=tpo.update(t, duty)
        applied=1.0 if on else 0.0
        plant.step(on); t+=0.25
    rms=(sum(e*e for e in errs)/len(errs))**0.5
    return dict(rms=rms, worst=min(errs), peak=m.peak_c, tal=m.time_above_liquidus)

OLD=dict(kp=0.22,ki=0.004,kd=0.5,k_z=0.0)
NEW=dict(kp=0.22,ki=0.004,kd=0.5,k_z=float(os.environ.get("KZ","2.0")))
snl=Profile.load(ROOT+"/firmware/profiles/ts391snl.json")
lt=Profile.load(ROOT+"/firmware/profiles/ts391lt.json")
print("k_z=%.2f    %-9s %-6s | %7s %7s %7s %6s | %7s %7s %7s %6s" % (NEW["k_z"],"plant","start","old rms","worst","peak","tal","new rms","worst","peak","tal"))
for pname, mk in (("two-state", lambda s: TwoStateOven(s)),
                  ("2s g*0.8",  lambda s: TwoStateOven(s, 0.8)),
                  ("2s g*1.2",  lambda s: TwoStateOven(s, 1.2)),
                  ("one-state", lambda s: MeasuredOven(dt=0.25, start_c=s))):
    for prof, start in ((snl,25.0),(snl,34.1),(snl,59.4),(lt,28.4)):
        o=run(prof, mk(start), False, start, OLD)
        n=run(prof, mk(start), True,  start, NEW)
        print("%-16s %-4s %4.0fC | %7.2f %7.1f %7.1f %6.0f | %7.2f %7.1f %7.1f %6.0f"
              % (prof.name[:7], pname, start, o["rms"],o["worst"],o["peak"],o["tal"], n["rms"],n["worst"],n["peak"],n["tal"]))
