"""Ideal bounded-vector actuator study for approved A styling geometry.
Convex inner approximation of an UPWARD cone and magnitude limit per fan.
No reverse-flow convexification, measured vane map or installed performance.
"""
from pathlib import Path
import json,csv,itertools,math
import numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'vectorizacion_A';OUT.mkdir(exist_ok=True)
p=np.array([[x,y,.058] for x in [-.280,.285] for y in [-.065,.065]])
# CG fixed at origin only for this ideal geometry study; no current mass closure.
L=1.345;mass=5.;G=9.80665;mg=mass*G
dirs=np.array([v for v in itertools.product([-1.,0.,1.],repeat=3) if any(v)]);dirs/=np.linalg.norm(dirs,axis=1)[:,None];taus=np.vstack([np.zeros(3),.5*np.eye(3),-.5*np.eye(3)])
rows=[];validation=[]
for delta in [0,15,30,45]:
 ang=math.radians(delta);vectors=np.array([[0,0,1]]+([[math.sin(ang)*math.cos(phi),math.sin(ang)*math.sin(phi),math.cos(ang)] for phi in np.arange(32)*2*np.pi/32] if delta else []));K=len(vectors)
 Aeq=np.zeros((6,4*K+1));Aub=np.zeros((4,4*K+1))
 for i in range(4):Aeq[:,i*K:(i+1)*K]=np.vstack([vectors.T,np.cross(p[i],vectors).T/L]);Aub[i,i*K:(i+1)*K]=1;Aub[i,-1]=-1
 for accel in [0,.5,1]:
  for j,v in enumerate(dirs if accel else np.array([[0.,0.,1.]])):
   for k,tau in enumerate(taus):
    force=mg*(np.array([0,0,1.])+accel*v);target=np.r_[force,tau/L]
    cost=np.zeros(4*K+1);cost[-1]=1
    sol=linprog(cost,A_ub=Aub,b_ub=np.zeros(4),A_eq=Aeq,b_eq=target,bounds=[(0,None)]*(4*K+1),method='highs')
    row=dict(delta_effective_deg=delta,additional_acceleration_g=accel,direction_index=j,torque_case=k,force_N=force.tolist(),torque_Nm=tau.tolist(),feasible=bool(sol.success),status=int(sol.status))
    if sol.success:
     f=sol.x[:-1].reshape(4,K)@vectors;T=float(sol.x[-1]);res=float(max(abs(np.r_[f.sum(axis=0),np.cross(p,f).sum(axis=0)/L]-target)))
     assert res<1e-7 and max(np.linalg.norm(f,axis=1))<=T+1e-7
     for fi in f:
      assert np.linalg.norm(fi[:2])<=max(0,fi[2])*math.tan(ang)+1e-7
     row.update(required_T_per_fan_N=T,force_vectors_N=f.tolist(),residual=res)
    rows.append(row)
summary=[]
for delta in [0,15,30,45]:
 for accel in [0,.5,1]:
  r=[a for a in rows if a['delta_effective_deg']==delta and a['additional_acceleration_g']==accel];good=[a for a in r if a['feasible']];summary.append(dict(delta_deg=delta,acceleration_g=accel,solved=len(good),cases=len(r),largest_T_N=max((a['required_T_per_fan_N'] for a in good),default=None)))
(OUT/'CASOS.json').write_text(json.dumps(rows,indent=2));(OUT/'RESUMEN.json').write_text(json.dumps(dict(summary=summary,position_m=p.tolist(),mass_assumed_kg=mass,CG_assumed_m=[0,0,0],phi_vertices=32,note='Sampled force and torque directions. Unidirectional ideal vector cone; calculated T is for inner polytope, not a measured motor capacity. Effective jet angle is not mechanical vane angle.'),indent=2));print(json.dumps(summary,indent=2))
