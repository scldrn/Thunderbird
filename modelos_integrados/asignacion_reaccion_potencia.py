"""Sampled nonlinear allocation at zero body rate; no dynamic/flight guarantee."""
from pathlib import Path
import json,csv,itertools,numpy as np
from scipy.optimize import linprog,minimize
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'masas_distribuidas'
d=json.loads((OUT/'5kg'/'mediciones_DIGITALES.json').read_text());I=np.array(d['inertia_geometric_components_only_kgm2']);n=np.array(d['rotor_axes']);L=d['L_m'];cg=np.array(d['CG_geometric_components_only_m']);p=np.array(d['rotor_centers_m']);B=np.vstack([n.T,np.cross(p-cg,n).T/L]);spin=np.r_[np.ones(4),-np.ones(4)]
assert np.linalg.norm(spin@n)<1e-12
r=sorted([a for a in csv.DictReader((ROOT.parent/'resultados'/'mapa_rotor_bidireccional_CONDICIONAL.csv').open()) if a['rpm']=='6000' and a['solved']=='True'],key=lambda a:float(a['target_N']))
x=np.array([float(a['target_N']) for a in r]);q=np.array([float(a['shaft_torque_Nm']) for a in r]);power=np.array([float(a['electrical_W_assumed']) for a in r]);outside=np.array([float(a['outside_torque_fraction']) for a in r])
assert np.all(np.diff(x)>0)
dirs=np.array([v for v in itertools.product([-1.,0.,1.],repeat=3) if any(v)]);dirs/=np.linalg.norm(dirs,axis=1)[:,None];alphas=np.vstack([np.zeros(3),2*np.eye(3),-2*np.eye(3)])
def wrench(f):return B@f+np.r_[np.zeros(3),-(spin*np.interp(f,x,q))@n/L]
def objective(f):return float(np.sum(np.interp(f,x,power)))
rows=[]
for tag,lo,hi in [('full',-37,40),('coverage5percent',-28,38)]:
 for level in [1,1.5,2]:
  for j,v in enumerate(dirs):
   for k,a in enumerate(alphas):
    target=np.r_[d['total_budget_kg']*9.80665*level*v,I@a/L]
    lp=linprog(np.zeros(8),A_eq=B,b_eq=target,bounds=[(lo,hi)]*8,method='highs');start=lp.x if lp.success else np.clip(np.linalg.lstsq(B,target,rcond=None)[0],lo,hi)
    sol=minimize(objective,start,bounds=[(lo,hi)]*8,constraints={'type':'eq','fun':lambda f:wrench(f)-target},method='SLSQP',options={'maxiter':220,'ftol':1e-8})
    err=float(np.max(np.abs(wrench(sol.x)-target)));ok=err<1e-6 and np.all(sol.x>=lo-1e-8) and np.all(sol.x<=hi+1e-8)
    if not ok:
     retry=minimize(objective,np.full(8,(lo+hi)/2),bounds=[(lo,hi)]*8,constraints={'type':'eq','fun':lambda f:wrench(f)-target},method='SLSQP',options={'maxiter':300,'ftol':1e-8})
     er=float(np.max(np.abs(wrench(retry.x)-target)))
     if er<err:sol=retry;err=er;ok=err<1e-6
    rows.append(dict(domain=tag,force_level_weight=level,direction_index=j,angular_case=k,force_direction=v.tolist(),alpha_rad_s2=a.tolist(),feasible_numerically=bool(ok),optimizer_success=bool(sol.success),residual=err,power_W=objective(sol.x) if ok else None,largest_rotor_W=float(np.max(np.interp(sol.x,x,power))) if ok else None,reaction_norm_Nm=float(np.linalg.norm((spin*np.interp(sol.x,x,q))@n)) if ok else None,max_outside_torque_fraction=float(np.max(np.interp(sol.x,x,outside))) if ok else None,thrusts_N=sol.x.tolist()))
  print(tag,level,'done',flush=True)
summary=[]
for tag in ['full','coverage5percent']:
 for lev in [1,1.5,2]:
  subset=[r for r in rows if r['domain']==tag and r['force_level_weight']==lev];good=[r for r in subset if r['feasible_numerically']]
  summary.append(dict(domain=tag,force_level_weight=lev,solved=len(good),total=len(subset),min_power_W=min(r['power_W'] for r in good) if good else None,max_power_W=max(r['power_W'] for r in good) if good else None,max_rotor_W=max(r['largest_rotor_W'] for r in good) if good else None,max_reaction_norm_Nm=max(r['reaction_norm_Nm'] for r in good) if good else None))
(OUT/'asignacion_reaccion_potencia_CASOS.json').write_text(json.dumps(rows,indent=2));(OUT/'asignacion_reaccion_potencia_RESUMEN.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
