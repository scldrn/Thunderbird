"""MILP feasibility for the EXACT piecewise-linear interpolated rotor map.
Global statement is about this surrogate only, not rotor physics.
"""
from pathlib import Path
import json,csv,numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix,vstack
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'masas_distribuidas'
d=json.loads((OUT/'5kg/mediciones_DIGITALES.json').read_text());I=np.array(d['inertia_geometric_components_only_kgm2']);n=np.array(d['rotor_axes']);p=np.array(d['rotor_centers_m']);cg=np.array(d['CG_geometric_components_only_m']);L=d['L_m'];B=np.vstack([n.T,np.cross(p-cg,n).T/L]);spin=np.r_[np.ones(4),-np.ones(4)]
r=sorted([a for a in csv.DictReader((ROOT.parent/'resultados/mapa_rotor_bidireccional_CONDICIONAL.csv').open()) if a['rpm']=='6000' and a['solved']=='True' and -28<=float(a['target_N'])<=38],key=lambda a:float(a['target_N']))
x=np.array([float(a['target_N']) for a in r]);q=np.array([float(a['shaft_torque_Nm']) for a in r]);pw=np.array([float(a['electrical_W_assumed']) for a in r]);K=len(x)-1;N=8*K;NV=2*N
# z chooses exactly one segment per rotor; 0<=t<=z interpolates within it.
A=lil_matrix((8+N+6,NV));lb=np.r_[np.ones(8),np.full(N,-np.inf),np.zeros(6)];ub=np.r_[np.ones(8),np.zeros(N),np.zeros(6)]
for i in range(8):
 for k in range(K):
  j=i*K+k;A[i,j]=1;A[8+j,j]=-1;A[8+j,N+j]=1
  w0=B[:,i]*x[k]+np.r_[np.zeros(3),-spin[i]*q[k]*n[i]/L]
  dw=B[:,i]*(x[k+1]-x[k])+np.r_[np.zeros(3),-spin[i]*(q[k+1]-q[k])*n[i]/L]
  A[-6:,j]=w0[:,None];A[-6:,N+j]=dw[:,None]
A=A.tocsr();integrality=np.r_[np.ones(N),np.zeros(N)];bounds=Bounds(np.zeros(NV),np.ones(NV));objective=np.zeros(NV)
old=json.loads((OUT/'asignacion_reaccion_potencia_CASOS.json').read_text());failed=[a for a in old if not a['feasible_numerically']];assert len(failed)==60 and all(a['domain']=='coverage5percent' for a in failed)
rows=[]
for idx,a in enumerate(failed):
 target=np.r_[d['total_budget_kg']*9.80665*a['force_level_weight']*np.array(a['force_direction']),I@a['alpha_rad_s2']/L];lb[-6:]=target;ub[-6:]=target
 sol=milp(objective,integrality=integrality,bounds=bounds,constraints=LinearConstraint(A,lb,ub),options={'time_limit':10,'mip_rel_gap':0})
 entry=dict(direction_index=a['direction_index'],angular_case=a['angular_case'],status=int(sol.status),message=sol.message)
 if sol.x is not None:
  z=sol.x[:N].reshape(8,K);t=sol.x[N:].reshape(8,K);f=z@x[:-1]+t@np.diff(x);qq=z@q[:-1]+t@np.diff(q);w=B@f+np.r_[np.zeros(3),-(spin*qq)@n/L]
  err=float(np.max(np.abs(w-target)));interp_err=float(np.max(np.abs(np.interp(f,x,q)-qq)))
  assert err<1e-5 and interp_err<1e-5
  entry.update(thrusts_N=f.tolist(),residual=err,interpolation_error=interp_err,power_W=float(np.sum(z@pw[:-1]+t@np.diff(pw))))
 rows.append(entry);(OUT/'asignacion_global_CASOS.json').write_text(json.dumps(rows,indent=2))
 if (idx+1)%10==0:print(idx+1,'/',len(failed),{s:sum(r['status']==s for r in rows) for s in range(5)},flush=True)
summary=dict(cases=len(rows),globally_feasible=sum(r['status']==0 for r in rows),globally_infeasible_in_interpolated_model=sum(r['status']==2 for r in rows),unresolved=sum(r['status'] not in [0,2] for r in rows),scope='Exact segment disjunction for the conditional interpolated aerodynamic map. Numerical MILP solver tolerances apply. Does not prove physical impossibility. Feasible solutions minimize zero, not power.')
(OUT/'asignacion_global_RESUMEN.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
# Positive controls: every previous feasible filtered-map point must embed exactly.
controls=[a for a in old if a['domain']=='coverage5percent' and a['feasible_numerically']]
max_error=0.
for a in controls:
 f=np.array(a['thrusts_N']);v=np.zeros(NV)
 for i,fi in enumerate(f):
  k=int(np.clip(np.searchsorted(x,fi,side='right')-1,0,K-1));j=i*K+k;v[j]=1;v[N+j]=(fi-x[k])/(x[k+1]-x[k])
 av=A@v;target=np.r_[d['total_budget_kg']*9.80665*a['force_level_weight']*np.array(a['force_direction']),I@a['alpha_rad_s2']/L]
 assert np.max(np.abs(av[:8]-1))<1e-12 and np.max(av[8:8+N])<1e-10
 assert min(v)>-1e-8 and max(v)<1+1e-8
 error=float(np.max(np.abs(av[-6:]-target)));assert error<1e-6;max_error=max(max_error,error)
validation=dict(known_feasible_points_embedded=len(controls),max_equilibrium_residual=max_error)
(OUT/'asignacion_global_VERIFICACION.json').write_text(json.dumps(validation,indent=2));print(validation)
