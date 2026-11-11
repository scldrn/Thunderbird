"""MILP minimum maximum endpoint pitch change, not a dynamic flight simulation."""
from pathlib import Path
import json,csv,numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'masas_distribuidas'
d=json.loads((OUT/'5kg/mediciones_DIGITALES.json').read_text());n=np.array(d['rotor_axes']);p=np.array(d['rotor_centers_m']);cg=np.array(d['CG_geometric_components_only_m']);L=d['L_m'];mg=d['total_budget_kg']*9.80665;B=np.vstack([n.T,np.cross(p-cg,n).T/L]);spin=np.r_[np.ones(4),-np.ones(4)]
r=sorted([a for a in csv.DictReader((ROOT.parent/'resultados/mapa_rotor_bidireccional_CONDICIONAL.csv').open()) if a['rpm']=='6000' and a['solved']=='True' and -28<=float(a['target_N'])<=38],key=lambda a:float(a['target_N']))
x=np.array([float(a['target_N']) for a in r]);q=np.array([float(a['shaft_torque_Nm']) for a in r]);theta=np.array([float(a['pitch_deg']) for a in r]);K=len(x)-1;N=8*K;NV=4*N+1;NR=2*(8+N+6)+16
A=lil_matrix((NR,NV));lb=np.full(NR,-np.inf);ub=np.zeros(NR);integ=np.zeros(NV);rowoffset=0
for e in range(2):
 off=e*2*N;ro=e*(8+N+6);integ[off:off+N]=1;lb[ro:ro+8]=1;ub[ro:ro+8]=1
 for i in range(8):
  for k in range(K):
   j=i*K+k;A[ro+i,off+j]=1;A[ro+8+j,off+j]=-1;A[ro+8+j,off+N+j]=1
   a=B[:,i]*x[k]+np.r_[np.zeros(3),-spin[i]*q[k]*n[i]/L];b=B[:,i]*np.diff(x)[k]+np.r_[np.zeros(3),-spin[i]*np.diff(q)[k]*n[i]/L]
   A[ro+8+N:ro+14+N,off+j]=a[:,None];A[ro+8+N:ro+14+N,off+N+j]=b[:,None]
   for sgn in [-1,1]:
    rr=2*(8+N+6)+2*i+(sgn==1);fac=sgn*(1 if e==1 else -1)
    A[rr,off+j]=fac*theta[k];A[rr,off+N+j]=fac*np.diff(theta)[k];A[rr,-1]=-1
A=A.tocsr();cost=np.zeros(NV);cost[-1]=1;low=np.zeros(NV);high=np.ones(NV);high[-1]=60
rows=[]
for axis in range(3):
 for accel in [.5,1]:
  targets=[]
  for e,sgn in enumerate([-1,1]):
   force=mg*np.array([0.,0.,1.]);force[axis]+=sgn*accel*mg;target=np.r_[force,np.zeros(3)];targets.append(target)
   ro=e*(8+N+6)+8+N;lb[ro:ro+6]=target;ub[ro:ro+6]=target
  sol=milp(cost,integrality=integ,bounds=Bounds(low,high),constraints=LinearConstraint(A,lb,ub),options={'time_limit':20,'mip_rel_gap':1e-5})
  row=dict(axis='xyz'[axis],acceleration_g=accel,status=int(sol.status),message=sol.message)
  if sol.x is not None:
   pitches=[];forces=[];errors=[]
   for e in range(2):
    off=e*2*N;z=sol.x[off:off+N].reshape(8,K);t=sol.x[off+N:off+2*N].reshape(8,K);f=z@x[:-1]+t@np.diff(x);qq=np.interp(f,x,q);tt=np.interp(f,x,theta);w=B@f+np.r_[np.zeros(3),-(spin*qq)@n/L];err=float(np.max(np.abs(w-targets[e])));assert err<1e-5;pitches.append(tt);forces.append(f.tolist());errors.append(err)
   delta=float(np.max(abs(pitches[1]-pitches[0])));assert delta<=sol.x[-1]+1e-5
   row.update(max_pitch_change_deg=delta,objective_bound_deg=float(sol.mip_dual_bound),mip_gap=float(sol.mip_gap),endpoint_thrusts_N=forces,endpoint_pitches_deg=[t.tolist() for t in pitches],max_endpoint_residual=max(errors),ideal_travel_seconds_at_pitch_rates={str(rate):delta/rate for rate in [100,300,600]})
  rows.append(row);(OUT/'inversion_paso_REQUISITOS.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
