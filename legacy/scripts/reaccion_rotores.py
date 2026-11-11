"""Sensitivity of fixed RPM control to rotor reaction torque using conditional map."""
import csv,json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from itertools import product
from control import allocation
from calcular import geometry,G
OUT=Path(__file__).resolve().parents[2]/'resultados'
r=[r for r in csv.DictReader((OUT/'mapa_rotor_bidireccional_CONDICIONAL.csv').open()) if r['rpm']=='6000' and r['solved']=='True']
fgrid=np.array([float(x['target_N']) for x in r]);qgrid=np.array([float(x['shaft_torque_Nm']) for x in r]);pgrid=np.array([float(x['electrical_W_assumed']) for x in r]);og=np.array([float(x['outside_torque_fraction']) for x in r])
previous=json.loads((OUT/'asignacion_mapa_rotor.json').read_text());assert all(a['feasible'] for a in previous)
g=geometry(.025,4,'esferoide');L,D=g['L_m'],g['D_m'];a=json.loads((OUT/'configuracion_control_HIPOTESIS.json').read_text())['record']
B,pos,n=allocation(L,D,2,a['theta_rad'],a['phi_rad']);pos[:,0]*=1.25;B[3:]=np.cross(pos-np.array([.05,0,0]),n).T/L
F=np.array([a['thrusts'] for a in previous]);Q=np.interp(F,fgrid,qgrid)
spins=[]
for tail in product([-1.,1.],repeat=7):
 s=np.r_[1.,tail];Hnet=np.linalg.norm(np.sum(s[:,None]*n,axis=0))*.3958529894
 if Hnet>1e-8:continue
 reactions=-np.einsum("ij,jk->ik",Q*s,n)
 spins.append((float(np.max(np.linalg.norm(reactions,axis=1))),s))
assert spins
worst,spin=min(spins,key=lambda p:p[0])
dirs=np.array([v for v in product([-1.,0.,1.],repeat=3) if any(v)],float);dirs/=np.linalg.norm(dirs,axis=1)[:,None];taus=[np.zeros(3),*np.eye(3),*-np.eye(3)]
def wrench(f):return B@f+np.r_[np.zeros(3),-(np.interp(f,fgrid,qgrid)*spin)@n/L]
rows=[]
for old in previous:
 demand=np.r_[5*G*old['level']*dirs[old['direction']],taus[old['torque_case']]/L]
 sol=minimize(lambda f:float(np.sum(np.interp(f,fgrid,pgrid))),np.array(old['thrusts']),bounds=[(fgrid[0],fgrid[-1])]*8,constraints={'type':'eq','fun':lambda f:wrench(f)-demand},method='SLSQP',options={'ftol':1e-6,'maxiter':400})
 error=float(max(abs(wrench(sol.x)-demand)));ok=bool(sol.success and error<1e-5)
 rows.append(dict(level=old['level'],direction=old['direction'],torque_case=old['torque_case'],solver_feasible=ok,residual=error,power_W=float(sum(np.interp(sol.x,fgrid,pgrid))),outside_max=float(max(np.interp(sol.x,fgrid,og)))))
summary=[]
for lev in [1,1.5,2]:
 rr=[x for x in rows if x['level']==lev];good=[x for x in rr if x['solver_feasible']]
 summary.append(dict(level=lev,solved=len(good),total=len(rr),max_power_W=max(x['power_W'] for x in good),outside_max=max(x['outside_max'] for x in good),worst=max(good,key=lambda x:x['power_W'])))
result=dict(balanced_spin_patterns=len(spins),chosen_spin_directions=spin.tolist(),max_reaction_without_compensation_Nm=worst,summary=summary,notes=['gyro cancellation assumes equal rotor inertia and constant RPM','signed thrust asymmetry partly due to limited experimental domain','solver failure is not proof of physical infeasibility','fixed5kg not full hardware closure'])
(OUT/'reaccion_rotores_resumen.json').write_text(json.dumps(result,indent=2));(OUT/'reaccion_rotores_casos.json').write_text(json.dumps(rows,indent=2));print(json.dumps(result,indent=2))
