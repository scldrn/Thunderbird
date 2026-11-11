from pathlib import Path
import json,csv,sys,numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'legacy'/'scripts'))
from control import facets
rng=np.random.default_rng(30102026);rows=list(csv.DictReader((ROOT/'masas_distribuidas'/'cargas_giro.csv').open()));summary=json.loads((ROOT/'masas_distribuidas'/'RESUMEN.json').read_text());count=0;residual=0
for m in [5,10]:
 d=json.loads((ROOT/'masas_distribuidas'/f'{m}kg'/'mediciones_DIGITALES.json').read_text());I=np.array(d['inertia_geometric_components_only_kgm2']);n=np.array(d['rotor_axes']);p=np.array(d['rotor_centers_m']);cg=np.array(d['CG_geometric_components_only_m']);L=d['L_m'];H=next(x['blade_H_per_rotor_Nms'] for x in summary if x['target_mass_kg']==m);spin=np.r_[np.ones(4),-np.ones(4)];B=np.vstack([n.T,np.cross(p-cg,n).T/L]);eig=np.linalg.eigvalsh(I)
 for row in rows:
  if int(row['target_mass_kg'])!=m:continue
  wmag=float(row['body_rate_rad_s']);eps=float(row['independent_rpm_mismatch_fraction']);ag=float(row['additional_acceleration_g']);T=float(row['sufficient_symmetric_T_N'])
  for _ in range(12):
   v=rng.normal(size=(3,3));v/=np.linalg.norm(v,axis=1)[:,None];omega=wmag*v[0];alpha=2*v[1];force=d['total_budget_kg']*9.80665*(1+ag)*v[2]
   hn=(spin*H*(1+rng.uniform(-eps,eps,8)))@n;euler=np.cross(omega,I@omega);gyro=np.cross(omega,hn)
   assert np.linalg.norm(euler)<=.5*(eig[-1]-eig[0])*wmag*wmag+1e-10
   w=np.r_[force,(I@alpha+euler+gyro)/L];sol=linprog(np.zeros(8),A_eq=B,b_eq=w,bounds=[(-T,T)]*8,method='highs');assert sol.success
   residual=max(residual,float(np.max(np.abs(B@sol.x-w))));count+=1
out=dict(sampled_wrench_checks=count,max_normalized_residual=residual,note='Numerical spot checks supplement analytical conservative support bounds, not physical validation.')
(ROOT/'masas_distribuidas'/'VERIFICACION.json').write_text(json.dumps(out,indent=2));print(out)
