"""Two-state DYNAMICS, measured-table STEADY STATE.

    dz/dt  = g(T)*u - beta*z
    dTc/dt = z - d*(Tc - Ta)

with g(T) chosen so that at duty 1 the steady state equals the measured
full-power rate h(T):  g(T) = beta * (h(T) + d*(T - Ta)).  beta and d are
the two parameters the data pinned down; the radiative nonlinearity rides in
g(T) from the table. The pure linear two-state model was 30% off the table
at the ends of the range.
"""
import json, os, sys
sys.path.insert(0, __import__("os").path.join(ROOT, "tools"))
from identify_plant import load, _interp, rms, two_state, one_state, nelder_mead, cost as cost2, X0, STEP
ROOT=__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))))
D=json.load(open(ROOT+"/data/oven-characterisation.json"))
HEAT=sorted(D["heating_rate_c_per_s"]); TA=23.5

def hybrid(par, rows):
    beta, d = par
    tc=rows[0][2]; z=0.0; out=[tc]
    for i in range(1,len(rows)):
        dt=rows[i][0]-rows[i-1][0]
        if dt<=0 or dt>5: out.append(tc); continue
        u=rows[i-1][1]; n=max(1,int(dt/0.25)); h=dt/n
        for _ in range(n):
            g=beta*(_interp(HEAT,tc)+d*(tc-TA))
            z+=(g*u-beta*z)*h
            tc+=(z-d*(tc-TA))*h
        out.append(tc)
    return out

def costh(par, sets):
    if par[0]<=0.005 or par[1]<=0: return 1e9
    tot=n=0.0
    for rw in sets:
        m=hybrid(par,rw)
        for i,r in enumerate(rw): e=m[i]-r[2]; tot+=e*e; n+=1
    return (tot/n)**0.5

S=ROOT+"/data/plant-id/"
runs={f[:-4]:load(S+f) for f in sorted(os.listdir(S)) if f.endswith(".csv")}
runs={k:v for k,v in runs.items() if len(v)>50}
print("%-26s %8s %9s %8s %7s %8s" % ("held out","hybrid","two-state","current","beta","tau s"))
for held in runs:
    train=[v for k,v in runs.items() if k!=held]
    ph,_=nelder_mead(lambda p: costh(p,train), [0.07,0.0037],[0.02,0.001], iters=300)
    p2,_=nelder_mead(lambda p: cost2(p,train), X0, STEP, iters=300)
    print("%-26s %8.2f %9.2f %8.2f %7.4f %7.1f" % (held, rms(hybrid(ph,runs[held]),runs[held]),
          rms(two_state(p2,runs[held]),runs[held]), rms(one_state(runs[held]),runs[held]), ph[0], 1/ph[0]))
pa,ea=nelder_mead(lambda p: costh(p,list(runs.values())), [0.07,0.0037],[0.02,0.001], iters=400)
print("\nall four: beta=%.5f (tau %.1f s) d=%.5f  rms %.2f" % (pa[0],1/pa[0],pa[1],ea))
open("hybrid.txt","w").write(repr(pa))
