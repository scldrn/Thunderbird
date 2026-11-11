"""Adaptive quasi-static pitch path. Checks all interpolation-map breakpoints.
No aerodynamic transient or actuator inertia/acceleration model.
"""
from pathlib import Path
import csv,json,numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'masas_distribuidas'
d=json.loads((OUT/'5kg/mediciones_DIGITALES.json').read_text());n=np.array(d['rotor_axes']);p=np.array(d['rotor_centers_m']);cg=np.array(d['CG_geometric_components_only_m']);L=d['L_m'];mg=d['total_budget_kg']*9.80665;B=np.vstack([n.T,np.cross(p-cg,n).T/L]);spin=np.r_[np.ones(4),-np.ones(4)]
r=sorted([a for a in csv.DictReader((ROOT.parent/'resultados/mapa_rotor_bidireccional_CONDICIONAL.csv').open()) if a['rpm']=='6000' and a['solved']=='True' and -28<=float(a['target_N'])<=38],key=lambda a:float(a['target_N']))
x=np.array([float(a['target_N']) for a in r]);q=np.array([float(a['shaft_torque_Nm']) for a in r]);theta=np.array([float(a['pitch_deg']) for a in r])
def wrench(f):return B@f+np.r_[np.zeros(3),-(spin*np.interp(f,x,q))@n/L]
allresults=[]
for old in json.loads((OUT/'transicion_paso_LOCAL.json').read_text()):
 axis='xyz'.index(old['axis']);a=old['acceleration_g']
 def demand(s):
  force=np.array([0.,0.,mg]);force[axis]+=(2*s-1)*a*mg;return np.r_[force,np.zeros(3)]
 points={0.:np.array(old['endpoint_pitches_deg'][0]),1.:np.array(old['endpoint_pitches_deg'][1])}
 def solve(s,guess):
  f=np.interp(guess,theta,x)
  sol=minimize(lambda z:float(np.sum((np.interp(z,x,theta)-guess)**2)),f,bounds=[(-28,38)]*8,constraints={'type':'eq','fun':lambda z:wrench(z)-demand(s)},method='SLSQP',options={'ftol':1e-11,'maxiter':400})
  assert max(abs(wrench(sol.x)-demand(s)))<1e-6
  return np.interp(sol.x,x,theta)
 history=[]
 for iteration in range(14):
  ss=sorted(points);bad=[];maxf=maxt=0.;checked=0
  for s0,s1 in zip(ss[:-1],ss[1:]):
   th0=points[s0];delta=points[s1]-th0;ts=[0.,1.]
   for j in range(8):
    if abs(delta[j])>1e-12:
     ts.extend(float(v) for v in (theta-th0[j])/delta[j] if 1e-10<v<1-1e-10)
   worst=(0,None,None)
   for t in sorted(set(ts)):
    s=s0+t*(s1-s0);th=th0+t*delta;error=wrench(np.interp(th,theta,x))-demand(s);ef=float(np.linalg.norm(error[:3]));et=float(np.linalg.norm(error[3:])*L);maxf=max(maxf,ef);maxt=max(maxt,et);checked+=1;score=max(ef/.01,et/.001)
    if score>worst[0]:worst=(score,s,th)
   if worst[0]>1.00001:bad.append(worst)
  history.append(dict(iteration=iteration,nodes=len(points),checked_breakpoints=checked,max_force_error_N=maxf,max_torque_error_Nm=maxt))
  if not bad:break
  if iteration==13:break
  for score,s,th in bad:
   assert s not in points
   points[s]=solve(s,th)
 ss=np.array(sorted(points));angles=np.array([points[s] for s in ss]);maxslope=float(np.max(abs(np.diff(angles,axis=0)/np.diff(ss)[:,None])));travel=np.sum(abs(np.diff(angles,axis=0)),axis=0)
 result=dict(axis=old['axis'],acceleration_g=a,converged_to_arbitrary_tolerances=not bool(bad),history=history,max_pitch_slope_deg_per_unit_progress=maxslope,constant_progress_duration_at_300deg_s=maxslope/300,maximum_rotor_total_pitch_travel_deg=float(max(travel)),progress_nodes=ss.tolist(),pitch_nodes_deg=angles.tolist(),limits='Quasi-static interpolation model only; piecewise-linear pitch commands have velocity jumps. No actuator acceleration, loads, delay, dynamic inflow, RPM variation, power limits or flight simulation.')
 allresults.append(result);(OUT/'trayectorias_paso_COORDINADAS.json').write_text(json.dumps(allresults,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['progress_nodes','pitch_nodes_deg','history']}),history[-1],flush=True)
