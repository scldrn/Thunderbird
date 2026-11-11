"""Convex allocation at fixed 5kg. Sampled power, not continuous guarantee."""
import json,csv,math
import numpy as np
from scipy.optimize import linprog,minimize
from itertools import product
from cierre_masa import OUT
from control import allocation,guaranteed_force
from calcular import geometry,G,RHO
geo=geometry(.025,4,'esferoide');L,D=geo['L_m'],geo['D_m']
rec=json.loads((OUT/'configuracion_control_HIPOTESIS.json').read_text())['record']
B,pos,n=allocation(L,D,2.,rec['theta_rad'],rec['phi_rad'])
# Shift assumed CG toward reactor; sensitivity only, not a hardware mass closure.
pos[:,0]*=1.25 # stations moved to +/-0.25L after disk intersection check
cg=np.array([.05,0,0]);B[3:]=np.cross(pos-cg,n).T/L
P=np.linalg.pinv(B);T=4.1*G
rng=np.random.default_rng(42)
dirs=np.array([v for v in product([-1.,0.,1.],repeat=3) if any(v)],float)
dirs=np.vstack([dirs,rng.normal(size=(100,3))]);dirs/=np.linalg.norm(dirs,axis=1)[:,None]
rows=[];residual=0
for level in [1.,1.5,2.]:
 for k,(v,tau) in enumerate(product(dirs,[np.zeros(3),*np.eye(3),*-np.eye(3)])):
  w=np.r_[5*G*level*v,tau/L]
  lp=linprog(np.zeros(8),A_eq=B,b_eq=w,bounds=[(-T,T)]*8,method='highs')
  if not lp.success:
   rows.append(dict(level=level,direction=k,feasible=False,power_W=None,pseudoinverse_W=None));continue
  objective=lambda f:np.sum(abs(f)**1.5)
  s=minimize(objective,lp.x,jac=lambda f:1.5*np.sign(f)*np.sqrt(abs(f)),bounds=[(-T,T)]*8,constraints={'type':'eq','fun':lambda f:B@f-w,'jac':lambda f:B},method='SLSQP',options={'ftol':1e-8,'maxiter':500})
  assert s.success,s.message
  residual=max(residual,float(np.max(abs(B@s.x-w))));assert residual<1e-6
  factor=1/(math.sqrt(2*RHO*math.pi*.4572**2/4)*.65)
  rows.append(dict(level=level,direction=k,feasible=True,power_W=float(objective(s.x)*factor),pseudoinverse_W=float(objective(P@w)*factor)))
summary=[]
for level in [1.,1.5,2.]:
 r=[x for x in rows if x['level']==level and x['feasible']];peak=max(x['power_W'] for x in r)
 # 12S, 3V loaded scenario; 40/60A not thermal guarantee.
 packs=[]
 for amps in [40,60]:
  par=math.ceil(peak/(12*3*amps));mass=12*par*.071*1.15
  packs.append(dict(current_A=amps,parallel=par,pack_kg=mass,remaining_after_engine_motors_fuel_pack_kg=5-1.08-8*.128-.156-mass))
 summary.append(dict(force_weight_multiple=level,feasible_samples=len(r),sample_max_W=peak,pseudoinverse_sample_max_W=max(x['pseudoinverse_W'] for x in r),packs=packs))
# Exact force ball in this ideal bidirectional model for chosen torque ball.
forceballs={str(tau):guaranteed_force(B,L,T,tau) for tau in [0.,1.,2.]}
with (OUT/'potencia_5kg_muestreo.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
result=dict(summary=summary,forceballs_N=forceballs,max_residual=residual,assumptions=dict(mass=5,CGx=.05,diameter=.4572,effective_efficiency=.65,per_rotor_signed_limit_N=T,directions_per_level=len(dirs),torque_samples_Nm=[0,1],station_fraction=.25),not_verified=['bidirectional thrust','continuous worst-case power','interference','new mass closure','transition'])
(OUT/'potencia_5kg_resumen.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
