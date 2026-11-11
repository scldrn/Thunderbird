"""Minimum separation of ideal zero-thickness rotor disks; deployed state only."""
import json,numpy as np
from scipy.optimize import minimize
from control import allocation
from calcular import geometry
from cierre_masa import OUT
rec=json.loads((OUT/'configuracion_control_HIPOTESIS.json').read_text())['record'];g=geometry(.025,4,'esferoide');L,D=g['L_m'],g['D_m']
results=[]
for spacing in [.2,.25,.3]:
 B,pos,n=allocation(L,D,2,rec['theta_rad'],rec['phi_rad']);pos[:,0]*=spacing/.2
 bases=[]
 for v in n:
  u=np.cross(v,[1,0,0]);u/=np.linalg.norm(u);bases.append(np.column_stack([u,np.cross(v,u)])*.4572/2)
 pairs=[]
 for i in range(8):
  for j in range(i+1,8):
   C=np.column_stack([bases[i],-bases[j]]);delta=pos[i]-pos[j]
   s=minimize(lambda z:np.sum((delta+C@z)**2),np.zeros(4),jac=lambda z:2*C.T@(delta+C@z),constraints=[{'type':'ineq','fun':lambda z:1-z[:2]@z[:2]},{'type':'ineq','fun':lambda z:1-z[2:]@z[2:]}],method='SLSQP',options={'ftol':1e-10,'maxiter':300})
   assert s.success
   assert np.linalg.norm(s.x[:2])<=1+1e-6 and np.linalg.norm(s.x[2:])<=1+1e-6
   pairs.append(dict(i=i,j=j,distance_m=float(np.sqrt(max(0,s.fun)))))
 results.append(dict(station_fraction=spacing,station_separation_m=2*spacing*L,closest=min(pairs,key=lambda p:p['distance_m']),pairs=pairs))
(OUT/'separacion_discos_5kg.json').write_text(json.dumps(results,indent=2));print([(r['station_fraction'],r['closest']) for r in results])
