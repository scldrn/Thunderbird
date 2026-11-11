"""SD8020 experimental drag runs: CL/CD vs alpha. Out-of-domain values flagged, never called validated."""
import re,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
text=(ROOT/'fuentes/uiuc/SD8020.DRG').read_text()
blocks=[]
for block in text.split('Average Reynolds #:')[1:]:
 lines=block.strip().splitlines();Re=float(lines[0]);data=[]
 for line in lines:
  vals=line.split()
  if len(vals)>=7:
   try:data.append([float(v) for v in vals[:3]])
   except ValueError:pass
 a=np.array(data);assert len(a)>=10;blocks.append((Re,a))
res=np.array([b[0] for b in blocks]);assert len(blocks)==4

def interp(alpha,re):
 hi=int(np.clip(np.searchsorted(res,re),1,len(res)-1));lo=hi-1
 weight=np.clip((re-res[lo])/(res[hi]-res[lo]),0,1)
 vals=[];valid=res[0]<=re<=res[-1]
 for idx in [lo,hi]:
  data=blocks[idx][1];valid=valid and data[0,0]<=alpha<=data[-1,0]
  vals.append([np.interp(alpha,data[:,0],data[:,1]),np.interp(alpha,data[:,0],data[:,2])])
 return (1-weight)*np.array(vals[0])+weight*np.array(vals[1]),valid

def solve(target,rpm,c,N=300):
 R=.2286;r=np.linspace(.04,R,N);omega=rpm*2*np.pi/60;vi=np.sqrt(target/(2*1.225*np.pi*R**2));W=np.sqrt((omega*r)**2+vi**2);phi=np.arctan2(vi,omega*r);Re=W*c/1.46e-5
 def loads(theta):
  pairs=[interp(float(a),float(re)) for a,re in zip(np.degrees(theta-phi),Re)]
  pol=np.array([p[0] for p in pairs]);valid=np.array([p[1] for p in pairs]);lift=.5*1.225*W**2*c*pol[:,0];drag=.5*1.225*W**2*c*pol[:,1]
  dt=2*(lift*np.cos(phi)-drag*np.sin(phi));dq=2*r*(lift*np.sin(phi)+drag*np.cos(phi))
  return np.trapezoid(dt,r),np.trapezoid(dq,r)*omega,valid,dt,dq
 if loads(np.radians(25))[0]<target:return dict(target=target,rpm=rpm,chord_mm=c*1000,solution=False)
 theta=brentq(lambda t:loads(t)[0]-target,0,np.radians(25));T,P,valid,dt,dq=loads(theta)
 outside=np.where(valid,0,abs(dq))
 return dict(target=target,rpm=rpm,chord_mm=c*1000,solution=True,collective_deg=np.degrees(theta),shaft_W=P,electric_W_assumed85pct=P/.85,span_outside_fraction=1-valid.mean(),absolute_torque_integral_outside_fraction=np.trapezoid(outside,r)/np.trapezoid(abs(dq),r),Re_min=min(Re),Re_max=max(Re),status='endpoint_clamping_sensitivity_not_validated_full_rotor')
rows=[solve(t,r,c) for t in [29.68422678,38.9412701] for r in [5500,6000] for c in [.030,.035]]
# Reproduce tabulated knots at each Reynolds, bypassing two-Re domain issue for alpha coverage.
for re,data in blocks:
 for a,cl,cd in data:
  p,ok=interp(a,re);assert np.max(abs(p-[cl,cd]))<1e-12
(OUT/'polar_experimental_resumen.json').write_text(json.dumps(dict(profile='SD8020 NOT NACA0012',data_Re=res.tolist(),rows=rows,missing=['Mach corrections','Cm measured','full radial coverage','tip loss','motor voltage map']),indent=2))
print(json.dumps(rows,indent=2))
