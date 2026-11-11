"""Static full-attitude wrench feasibility from exported CAD mass/axis configuration.
No aerodynamic loads, rotor reaction/gyro, delays or measured actuator maps.
"""
from pathlib import Path
import sys,json,csv,os
import numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'legacy'/'scripts'))
from control import facets
DATA=ROOT/os.environ.get('AERO_CAD_VARIANT','salida')
G=9.80665
rows=[];checks=[]
rng=np.random.default_rng(20261030)
for target in [5,10]:
 d=json.loads((DATA/f'{target}kg'/'mediciones_DIGITALES.json').read_text())
 p=np.array(d['rotor_centers_m']);u=np.array(d['rotor_axes']);cg=np.array(d['CG_geometric_components_only_m']);L=d['L_m']
 B=np.vstack([u.T,np.cross(p-cg,u).T/L]);ns,hs=facets(B);ns=np.vstack([ns,-ns]);hs=np.r_[hs,hs]
 I0=np.array(d['inertia_geometric_components_only_kgm2'])
 assert np.linalg.matrix_rank(B)==6
 for missing in [0,.1*target,.2*target]:
  mass=d['total_budget_kg']+missing
  for dist in ['en_CG','periferica_simetrica_respecto_CG']:
   # Additional point masses at +/- module-like offsets about fixed CG.
   dm=sum(d['allowances_kg'].values())+missing
   I=I0.copy()
   if dist.startswith('periferica'):
    for v in p:I+=dm/8*((v@v)*np.eye(3)-np.outer(v,v))
   for angular in [0,2,5]:
    for accel in [0,.5,1]:
     force=mass*G*(1+accel)
     support=force*np.linalg.norm(ns[:,:3],axis=1)+angular*np.linalg.norm(ns[:,3:]@I,axis=1)/L
     T=float(np.max(support/hs));j=int(np.argmax(support/hs));n=ns[j]
     # Independent LP at the facet maximizing required actuator limit.
     f=force*n[:3]/np.linalg.norm(n[:3]) if np.linalg.norm(n[:3])>1e-12 else np.zeros(3)
     z=I@n[3:];alpha=angular*z/np.linalg.norm(z) if np.linalg.norm(z)>1e-12 else np.zeros(3)
     w=np.r_[f,I@alpha/L]
     sol=linprog(np.zeros(8),A_eq=B,b_eq=w,bounds=[(-T,T)]*8,method='highs')
     outside=linprog(np.zeros(8),A_eq=B,b_eq=w,bounds=[(-T*.9999,T*.9999)]*8,method='highs')
     assert sol.success and not outside.success
     residual=float(np.max(np.abs(B@sol.x-w)))
     for _ in range(8):
      v=rng.normal(size=3);v/=np.linalg.norm(v);a=rng.normal(size=3);a*=angular/np.linalg.norm(a)
      w=np.r_[force*v,I@a/L];s=linprog(np.zeros(8),A_eq=B,b_eq=w,bounds=[(-T,T)]*8,method='highs');assert s.success
      residual=max(residual,float(np.max(np.abs(B@s.x-w))))
     rows.append(dict(target_mass_kg=target,mass_budget_scenario_kg=mass,additional_missing_mass_kg=missing,allowance_distribution=dist,angular_acceleration_rad_s2=angular,additional_translation_g=accel,min_symmetric_signed_thrust_per_rotor_N=T,max_principal_inertia_kgm2=float(np.linalg.eigvalsh(I)[-1]),validation_residual=residual))
 write=DATA/f'{target}kg'/'control_CAD_CONFIG.json'
 write.write_text(json.dumps(dict(B_normalized=B.tolist(),CG_assumed_m=cg.tolist(),note='CG remains fixed only under the explicitly symmetric mass-placement scenarios. This is a static feasibility calculation.'),indent=2))
with (DATA/'control_CAD_ESCENARIOS.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
selected=[r for r in rows if r['additional_missing_mass_kg']==0 and r['angular_acceleration_rad_s2']==2 and r['allowance_distribution']=='en_CG']
summary=dict(scenarios=len(rows),lp_checks=len(rows)*10,max_residual=max(r['validation_residual'] for r in rows),selected=selected,limits=['Signed symmetric thrust assumed, including reverse','Rotors have no reaction torque or delay in this model','No aerodynamic/gyroscopic loads or power/thermal limits','CAD inertia is provisional, not physically measured','10kg module hardware not selected','Missing mechanisms not designed; added mass is sensitivity only'])
(DATA/'control_CAD_RESUMEN.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
