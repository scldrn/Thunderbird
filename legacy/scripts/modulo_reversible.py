"""Requirements and voltage sensitivity. No validated motor/battery coupled model."""
import json,math,csv
import numpy as np
from control import allocation,facets
from calcular import geometry,G
from cierre_masa import OUT
geo=geometry(.025,4,'esferoide');L,D=geo['L_m'],geo['D_m']
a=json.loads((OUT/'configuracion_control_HIPOTESIS.json').read_text())['record']
B,pos,n=allocation(L,D,2,a['theta_rad'],a['phi_rad']);pos[:,0]*=1.25
B[3:]=np.cross(pos-np.array([.05,0,0]),n).T/L
ns,h=facets(B);ns=np.vstack([ns,-ns]);products=np.einsum("ij,jk->ik",ns,B);h=np.sum(abs(products),axis=1)
requirements=[]
for ag in [.5,1.]:
 for beta in [1.,.8,.6]:
  # Support of B[-beta*T,T]^8; include both facet directions.
  support=(1+beta)/2*h+(1-beta)/2*np.sum(products,axis=1)
  required=(5*G*(1+ag)*np.linalg.norm(ns[:,:3],axis=1)+1/L*np.linalg.norm(ns[:,3:],axis=1))
  T=float(np.max(required/support))
  requirements.append(dict(acceleration_g=ag,negative_positive_ratio=beta,required_positive_N=T,required_negative_N=beta*T))
old=json.loads((OUT/'potencia_5kg_resumen.json').read_text())['summary']
battery=[]
for level in [1,2]:
 power=old[level]['sample_max_W']
 for parallel in [1,2]:
  for voc in [3.4,3.7,4.1]:
   pcell=power/(12*parallel);R=.0128;disc=voc*voc-4*R*pcell
   if disc<0:continue
   current=(voc-math.sqrt(disc))/(2*R);voltage=voc-current*R
   battery.append(dict(acceleration_g=[.5,1][level-1],parallel=parallel,Voc_cell=voc,cell_A=current,pack_V=12*voltage,ohmic_heat_W=12*parallel*current**2*R,within_60A=current<=60,voltage_squared_thrust_sensitivity_N=4.1*G*(12*voltage/46.94)**2))
# Explicit allocation caps, not actual components.
fixed=dict(engine=1.08,motors=8*.128,fuel=.156,skin=.35,arms_locks=.25,avionics_wiring=.20,engine_installation=.15,contingency=.25)
allow=[]
for par in [1,2]:
 pack=12*par*.071*1.15;remain=5-sum(fixed.values())-pack
 allow.append(dict(parallel=par,pack_kg=pack,fixed_budget_kg=sum(fixed.values()),remaining_for_8_ESC_prop_hub_servo_kg=remain,per_module_g=remain/8*1000))
assert np.all(np.isfinite(products))
from scipy.optimize import linprog
rng=np.random.default_rng(73)
for rr in requirements:
 for _ in range(30):
  v=rng.normal(size=3);v/=np.linalg.norm(v);t=rng.normal(size=3);t/=np.linalg.norm(t)
  w=np.r_[5*G*(1+rr['acceleration_g'])*v,t/L]
  check=linprog(np.zeros(8),A_eq=B,b_eq=w,bounds=[(-rr['required_negative_N'],rr['required_positive_N'])]*8,method='highs')
  assert check.success
result=dict(requirements=requirements,battery_sensitivity=battery,budget_assumptions_kg=fixed,module_budget=allow,notes=['1Nm torque ball','power is sampled old model, not worst-case guarantee','R constant at nominal datasheet condition; no SOC or thermal dynamics','V squared thrust is hypothetical fixed-pitch rpm scaling; not a VP map'])
(OUT/'modulo_reversible_requisitos.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
