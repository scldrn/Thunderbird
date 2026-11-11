"""Blade-element + uniform actuator-disk inflow screening. Assumed polars, not NACA data."""
import json,csv,math
import numpy as np
from scipy.optimize import brentq
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'resultados'
rho=1.225;R=.2286;r0=.04;A=np.pi*R**2

def solve(chord,rpm,target,slope=5.5,clmax=.9,cd0=.02,axis=.25,N=500):
 r=np.linspace(r0,R,N);omega=rpm*2*np.pi/60;vi=math.sqrt(target/(2*rho*A));phi=np.arctan2(vi,omega*r);w2=(omega*r)**2+vi**2
 def loads(theta):
  alpha=theta-phi;cl=np.clip(slope*alpha,-clmax,clmax);cd=cd0+.03*cl**2
  lift=.5*rho*w2*chord*cl;drag=.5*rho*w2*chord*cd
  dt=2*(lift*np.cos(phi)-drag*np.sin(phi));dq=2*r*(lift*np.sin(phi)+drag*np.cos(phi))
  return float(np.trapezoid(dt,r)),float(np.trapezoid(dq,r)),alpha,dt
 if loads(np.radians(40))[0]<target:return dict(feasible_model=False,chord_mm=1000*chord,rpm=rpm,target_N=target,clmax=clmax)
 theta=brentq(lambda x:loads(x)[0]-target,0,np.radians(40));T,Q,alpha,dt=loads(theta)
 m=.015;pitchI=m*chord**2*(1/12+(.5-axis)**2)
 cent=omega**2*pitchI*abs(np.sin(theta)*np.cos(theta))
 # Symmetric ideal profile zero quarter-chord Cm; uncertainty separately .03 absolute.
 aero=.5*rho*chord**2*np.trapezoid(w2,r)*.03
 offset=target/2*abs(.25-axis)*chord
 transient=pitchI*(4*2*theta/.07**2)
 total=2*(cent+aero+offset+transient+.02)
 mech=Q*omega;re=np.sqrt(w2)*chord/1.46e-5
 return dict(feasible_model=True,chord_mm=chord*1000,rpm=rpm,target_N=target,clmax=clmax,axis_fraction=axis,collective_deg=float(np.degrees(theta)),pitch_sweep_deg=float(np.degrees(2*theta)),shaft_power_W=mech,electric_W_at_85pct=mech/.85,torque_shaft_Nm=Q,section_clipped_span_fraction=float(np.mean(abs(slope*alpha)>=clmax)),Re_min=float(min(re)),Re_max=float(max(re)),tip_Mach=float(np.sqrt(w2[-1])/340.3),centrifugal_N=m*omega**2*(r0+R)/2,servo_Nm_at_ratio_half=total*.5/.8,servo_min_kinematic_ms_at_8_4V=float(np.degrees(2*theta)/.5/60*.07*1000),thrust_residual=abs(T-target))
rows=[]
for c in [.025,.035,.045]:
 for rpm in [6000,7000,8000]:
  for target in [29.68422678,38.9412701]:
   for limit in [.7,.9,1.1]:
    rows.append(solve(c,rpm,target,clmax=limit))
keys=sorted(set().union(*(r.keys() for r in rows)))
with (OUT/'pala_referencia_ESCENARIOS.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
base=[r for r in rows if r['feasible_model'] and r['clmax']==.9 and r['target_N']>38]
checks=[]
for r in base:
 b=solve(r['chord_mm']/1000,r['rpm'],r['target_N'],N=1000)
 checks.append(abs(b['shaft_power_W']/r['shaft_power_W']-1));assert checks[-1]<1e-3
(OUT/'pala_referencia_resumen.json').write_text(json.dumps(dict(cases=54,baseline_1g=base,max_power_refinement_difference=max(checks),note='No measured profile polar, tip loss, swirl, elastic deformation, negative-thrust experiment'),indent=2))
print(json.dumps(base,indent=2))
