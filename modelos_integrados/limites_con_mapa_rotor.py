"""Continuous-direction conditional thrust bounds from existing 6000 RPM map.
Not installed actuator validation; rotor reaction torque still omitted here.
"""
from pathlib import Path
import csv,json,sys,numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'legacy'/'scripts'))
from control import facets
r=[a for a in csv.DictReader((ROOT.parent/'resultados'/'mapa_rotor_bidireccional_CONDICIONAL.csv').open()) if a['rpm']=='6000' and a['solved']=='True']
d=json.loads((ROOT/'masas_distribuidas'/'5kg'/'mediciones_DIGITALES.json').read_text());I=np.array(d['inertia_geometric_components_only_kgm2']);u=np.array(d['rotor_axes']);p=np.array(d['rotor_centers_m']);cg=np.array(d['CG_geometric_components_only_m']);L=d['L_m'];mg=d['total_budget_kg']*9.80665
H=json.loads((ROOT/'masas_distribuidas'/'RESUMEN.json').read_text())[0]['blade_H_per_rotor_Nms'];B=np.vstack([u.T,np.cross(p-cg,u).T/L]);ns,h=facets(B);ns=np.vstack([ns,-ns]);nf=np.linalg.norm(ns[:,:3],axis=1);nt=ns[:,3:];tn=np.linalg.norm(nt,axis=1);eig=np.linalg.eigvalsh(I)
records=[]
for tag,eligible in [('todo_mapa_condicional',r),('filtro_5pct_par_fuera_polar',[a for a in r if float(a['outside_torque_fraction'])<=.05])]:
 points=sorted(float(a['target_N']) for a in eligible);assert 0 in points
 # contiguous sampled component containing zero; linear intervals are a further model assumption
 start=end=points.index(0)
 while start>0 and points[start]-points[start-1]<=1.000001:start-=1
 while end<len(points)-1 and points[end+1]-points[end]<=1.000001:end+=1
 lo,hi=points[start],points[end];c=(lo+hi)/2;half=(hi-lo)/2
 support=c*(ns@B@np.ones(8))+half*np.sum(np.abs(ns@B),axis=1)
 for omega in [0,2,5,10]:
  for angular in [0,2,5]:
   mismatch=.05
   rotational=angular*np.linalg.norm(nt@I,axis=1)
   euler=.5*(eig[-1]-eig[0])*omega**2
   rotational+=euler*tn
   rotational+=mismatch*H*omega*np.sum(np.linalg.norm(np.cross(nt[:,None,:],u[None,:,:]),axis=2),axis=1)
   force_radius=float(np.min((support-rotational/L)[nf>1e-10]/nf[nf>1e-10]));j=np.flatnonzero(nf>1e-10)[np.argmin((support-rotational/L)[nf>1e-10]/nf[nf>1e-10])]
   # Verify limiting facet of the conservative demand set independently by LP when radius nonnegative.
   residual=None;checked=False
   if force_radius>=0:
    n=ns[j];z=I@n[3:];torque=angular*I@z/np.linalg.norm(z) if np.linalg.norm(z)>1e-12 else np.zeros(3)
    if np.linalg.norm(n[3:])>1e-12:torque+=euler*n[3:]/np.linalg.norm(n[3:])
    for axis in u:
     v=n[3:]-axis*np.dot(axis,n[3:])
     if np.linalg.norm(v)>1e-12:torque+=mismatch*H*omega*v/np.linalg.norm(v)
    target=np.r_[force_radius*n[:3]/np.linalg.norm(n[:3]),torque/L]
    lp=linprog(np.zeros(8),A_eq=B,b_eq=target,bounds=[(lo,hi)]*8,method='highs');assert lp.success
    beyond=target.copy();beyond[:3]*=1.00001
    fail=linprog(np.zeros(8),A_eq=B,b_eq=beyond,bounds=[(lo,hi)]*8,method='highs');assert not fail.success
    residual=float(np.max(np.abs(B@lp.x-target)));checked=True
   records.append(dict(map_filter=tag,lo_thrust_N=lo,hi_thrust_N=hi,body_rate_rad_s=omega,angular_acceleration_rad_s2=angular,independent_rpm_mismatch_fraction=mismatch,force_ball_radius_N=force_radius,additional_acceleration_guarantee_g=force_radius/mg-1,limiting_LP_verified=checked,residual=residual))
with (ROOT/'masas_distribuidas'/'limites_mapa_5kg.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
out=dict(mass_budget_kg=d['total_budget_kg'],rows=records,note='Negative guarantees mean this sufficient criterion does not cover all-attitude hover. At nonzero rate, conservative load enlargement may cause pessimism; not proof of physical infeasibility. Filter5percent is arbitrary screening, not an uncertainty bound. No transfer to10kg.')
(ROOT/'masas_distribuidas'/'limites_mapa_5kg.json').write_text(json.dumps(out,indent=2));print(json.dumps([a for a in records if a['angular_acceleration_rad_s2']==2],indent=2))
