"""Feasible endpoint search plus quasi-static linear pitch path diagnostic."""
from pathlib import Path
import json,csv,numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'masas_distribuidas'
d=json.loads((OUT/'5kg/mediciones_DIGITALES.json').read_text());n=np.array(d['rotor_axes']);p=np.array(d['rotor_centers_m']);cg=np.array(d['CG_geometric_components_only_m']);L=d['L_m'];mg=d['total_budget_kg']*9.80665;B=np.vstack([n.T,np.cross(p-cg,n).T/L]);spin=np.r_[np.ones(4),-np.ones(4)]
r=sorted([a for a in csv.DictReader((ROOT.parent/'resultados/mapa_rotor_bidireccional_CONDICIONAL.csv').open()) if a['rpm']=='6000' and a['solved']=='True' and -28<=float(a['target_N'])<=38],key=lambda a:float(a['target_N']))
x=np.array([float(a['target_N']) for a in r]);q=np.array([float(a['shaft_torque_Nm']) for a in r]);theta=np.array([float(a['pitch_deg']) for a in r])
def wrench(f):return B@f+np.r_[np.zeros(3),-(spin*np.interp(f,x,q))@n/L]
results=[]
for axis in range(3):
 for accel in [.5,1]:
  targets=[];fs=[]
  for sign in [-1,1]:
   force=np.array([0.,0.,mg]);force[axis]+=sign*accel*mg;target=np.r_[force,np.zeros(3)];targets.append(target)
   sol=minimize(lambda f:float(f@f),np.clip(np.linalg.lstsq(B,target,rcond=None)[0],-28,38),bounds=[(-28,38)]*8,constraints={'type':'eq','fun':lambda f:wrench(f)-target},method='SLSQP',options={'ftol':1e-9,'maxiter':300});assert max(abs(wrench(sol.x)-target))<1e-6;fs.append(sol.x)
  delta=max(abs(np.interp(fs[1],x,theta)-np.interp(fs[0],x,theta)));start=np.r_[fs[0],fs[1],delta+1e-6]
  eq=lambda z:np.r_[wrench(z[:8])-targets[0],wrench(z[8:16])-targets[1]]
  iq=lambda z:z[-1]-abs(np.interp(z[8:16],x,theta)-np.interp(z[:8],x,theta))
  sol=minimize(lambda z:z[-1],start,bounds=[(-28,38)]*16+[(0,60)],constraints=[{'type':'eq','fun':eq},{'type':'ineq','fun':iq}],method='SLSQP',options={'ftol':1e-8,'maxiter':400})
  z=sol.x if max(abs(eq(sol.x)))<1e-6 and min(iq(sol.x))>-1e-6 else start
  angles=np.interp(z[:16],x,theta).reshape(2,8);delta=float(max(abs(angles[1]-angles[0])));force_error=[];torque_error=[]
  for s in np.linspace(0,1,101):
   step=(1-s)*angles[0]+s*angles[1];f=np.interp(step,theta,x);w=wrench(f);target=(1-s)*targets[0]+s*targets[1]
   force_error.append(float(np.linalg.norm(w[:3]-target[:3])));torque_error.append(float(np.linalg.norm(w[3:])*L))
  results.append(dict(axis='xyz'[axis],acceleration_g=accel,max_pitch_change_deg_feasible=delta,endpoint_residual=float(max(abs(eq(z)))),endpoint_thrusts_N=z[:16].reshape(2,8).tolist(),endpoint_pitches_deg=angles.tolist(),linear_pitch_path_max_force_error_N=max(force_error),linear_pitch_path_max_torque_Nm=max(torque_error),ideal_pitch_travel_seconds_300deg_s=delta/300,status='Feasible local solution; no global optimality or dynamic tracking claim'))
(OUT/'transicion_paso_LOCAL.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
