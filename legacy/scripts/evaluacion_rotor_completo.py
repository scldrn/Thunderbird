"""Complete desktop screening, NOT a validated rotor map or hardware approval.
Measured SD8020 CL/CD, endpoint clamping flagged, signed uniform induced flow.
"""
from pathlib import Path
import os,json,csv,math
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
os.environ['MPLCONFIGDIR']=str(OUT/'mpl-cache')
import numpy as np
from scipy.optimize import brentq,linprog,minimize
from scipy.linalg import null_space
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from itertools import product
from control import allocation,guaranteed_force
from calcular import geometry,G
blocks=[]
for block in (ROOT/'fuentes/uiuc/SD8020.DRG').read_text().split('Average Reynolds #:')[1:]:
 lines=block.strip().splitlines();arr=[]
 for line in lines:
  v=line.split()
  if len(v)>=7:
   try:arr.append([float(x) for x in v[:3]])
   except ValueError:pass
 blocks.append((float(lines[0]),np.array(arr)))
RES=np.array([b[0] for b in blocks]);rho=1.225;R=.2286;c=.03;r0=.04

def rotor(target,rpm,N=240):
 r=np.linspace(r0,R,N);w=rpm*2*np.pi/60
 vi=np.sign(target)*np.sqrt(abs(target)/(2*rho*np.pi*R**2));W=np.sqrt((w*r)**2+vi**2);phi=np.arctan2(vi,w*r);Re=W*c/1.46e-5
 hi=np.clip(np.searchsorted(RES,Re),1,3);lo=hi-1;weight=np.clip((Re-RES[lo])/(RES[hi]-RES[lo]),0,1)
 def loads(theta):
  alpha=np.degrees(theta-phi)
  table=np.array([[np.interp(alpha,b[:,0],b[:,1]),np.interp(alpha,b[:,0],b[:,2])] for _,b in blocks])
  idx=np.arange(N)
  CL=(1-weight)*table[lo,0,idx]+weight*table[hi,0,idx]
  CD=(1-weight)*table[lo,1,idx]+weight*table[hi,1,idx]
  valid=(Re>=RES[0])&(Re<=RES[-1])
  for k,(_,b) in enumerate(blocks):
   used=((lo==k)&(weight<1-1e-12))|((hi==k)&(weight>1e-12))
   valid&=~used|((alpha>=b[0,0])&(alpha<=b[-1,0]))
  lift=.5*rho*W**2*c*CL;drag=.5*rho*W**2*c*CD
  dt=2*(lift*np.cos(phi)-drag*np.sin(phi));dq=2*r*(lift*np.sin(phi)+drag*np.cos(phi))
  return np.trapezoid(dt,r),np.trapezoid(dq,r),valid,dq,alpha
 low,high=loads(np.radians(-40))[0],loads(np.radians(40))[0]
 if not low<=target<=high:return dict(target_N=target,rpm=rpm,solved=False)
 theta=brentq(lambda t:loads(t)[0]-target,np.radians(-40),np.radians(40));T,Q,valid,dq,alpha=loads(theta)
 P=Q*w
 assert abs(T-target)<1e-6 and P>=0
 return dict(target_N=target,rpm=rpm,solved=True,pitch_deg=float(np.degrees(theta)),shaft_W=float(P),electrical_W_assumed=float(P/.85),shaft_torque_Nm=float(Q),outside_span_fraction=float(1-valid.mean()),outside_torque_fraction=float(np.trapezoid(np.where(valid,0,abs(dq)),r)/np.trapezoid(abs(dq),r)),Re_min=float(min(Re)),Re_max=float(max(Re)),Mach_tip=float(W[-1]/340.3),thrust_residual=float(abs(T-target)))

rows=[rotor(float(t),rpm) for rpm in [5000,5500,6000,6500] for t in np.arange(-40,41,1)]
keys=sorted(set().union(*(r.keys() for r in rows)))
with (OUT/'mapa_rotor_bidireccional_CONDICIONAL.csv').open('w') as f:
 wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(rows)
reference=[r for r in rows if r['rpm']==6000 and r['solved']]
forces=np.array([r['target_N'] for r in reference]);powers=np.array([r['electrical_W_assumed'] for r in reference]);lower=float(forces[0]);upper=float(forces[-1])
# Fixed RPM; use published asymmetric measured polar as-is, no artificial reflection.
# Direct objective interpolation; minimum found is numerical local result, no convexity claim.
g=geometry(.025,4,'esferoide');L,D=g['L_m'],g['D_m'];angles=json.loads((OUT/'configuracion_control_HIPOTESIS.json').read_text())['record']
B,pos,n=allocation(L,D,2,angles['theta_rad'],angles['phi_rad']);pos[:,0]*=1.25
B[3:]=np.cross(pos-np.array([.05,0,0]),n).T/L
Z=null_space(B);dirs=np.array([v for v in product([-1.,0.,1.],repeat=3) if any(v)],float);dirs/=np.linalg.norm(dirs,axis=1)[:,None]
allocations=[]
for level in [1.,1.5,2.]:
 for di,v in enumerate(dirs):
  for ti,tau in enumerate([np.zeros(3),*np.eye(3),*-np.eye(3)]):
   demand=np.r_[5*G*level*v,tau/L]
   lp=linprog(np.zeros(8),A_eq=B,b_eq=demand,bounds=[(lower,upper)]*8,method='highs')
   if not lp.success:
    allocations.append(dict(level=level,direction=di,torque_case=ti,feasible=False));continue
   f0=lp.x
   obj=lambda z:float(np.sum(np.interp(f0+Z@z,forces,powers)))
   con={'type':'ineq','fun':lambda z:np.r_[upper-f0-Z@z,f0+Z@z-lower]}
   sol=minimize(obj,np.zeros(Z.shape[1]),constraints=con,method='SLSQP',options={'ftol':1e-6,'maxiter':300})
   f=f0+Z@sol.x
   feasible=np.max(f)<=upper+1e-6 and np.min(f)>=lower-1e-6 and np.max(abs(B@f-demand))<1e-7
   # Fallback feasible starting point is explicitly flagged, not called optimum.
   if not feasible or obj(sol.x)>obj(np.zeros(Z.shape[1])):f=f0
   p=float(np.sum(np.interp(f,forces,powers)))
   outside=float(max(np.interp(f,forces,[r['outside_torque_fraction'] for r in reference])))
   allocations.append(dict(level=level,direction=di,torque_case=ti,feasible=True,power_W=p,optimizer_success=bool(sol.success and feasible),max_rotor_outside_torque_fraction=outside,thrusts=f.tolist()))
summary=[]
for lev in [1.,1.5,2.]:
 rr=[a for a in allocations if a['level']==lev and a['feasible']];worst=max(rr,key=lambda a:a['power_W']);summary.append(dict(level=lev,infeasible_samples=sum(a['level']==lev and not a['feasible'] for a in allocations),max_sample_power_W=worst['power_W'],min_sample_power_W=min(a['power_W'] for a in rr),worst=worst,optimizer_failures=sum(not a['optimizer_success'] for a in rr)))
# Independent refinement and physical accounting consistency.
checks=[]
for t in [-30,0,30,39]:
 a=rotor(t,6000);b=rotor(t,6000,480)
 diff=abs(a['shaft_W']/b['shaft_W']-1);assert diff<.005;checks.append(dict(thrust=t,relative_power_difference=diff))
# Necessary no-load speed bound only, not motor loaded curve.
voltage=[dict(voltage=v,nominal_no_load_rpm=170*v,can_reach_6000_even_unloaded=170*v>=6000) for v in [32,34,36,38,40,42,44,46.94,50.4]]
# Rotor angular momentum and total reaction-torque omission are now quantified.
w=6000*2*np.pi/60;m=.015;Jrot=2*m*(R**3-r0**3)/(3*(R-r0));H=Jrot*w
# Peak spindle centrifugal load and illustrative servo sizing for new chord.
a=rotor(30,6000);b=rotor(-30,6000);maxangle=max(abs(a['pitch_deg']),abs(b['pitch_deg']));theta=np.radians(maxangle)
I=m*c*c*(1/12+.25**2);cp=w*w*I*abs(np.sin(theta)*np.cos(theta));cm=.5*rho*w*w*c*c*(R**3-r0**3)/3*.03
servo=2*(cp+cm+.02)*.5/.8
sweep=a['pitch_deg']-b['pitch_deg'];time0=sweep/.5/60*.07
# A hypothetical linear torque-speed law is sensitivity, NOT servo datasheet behavior.
loaded_time=time0/(1-servo/.62) if servo<.62 else None
result=dict(map_cases=len(rows),map_solved=sum(r['solved'] for r in rows),reference_points=[rotor(t,6000) for t in [-39,-30,0,30,39]],allocation_samples=len(allocations),allocation_summary=summary,refinement_checks=checks,voltage_necessary_conditions=voltage,rotor_momentum=dict(blade_only_J_kgm2=Jrot,angular_momentum_Nms=H,gyroscopic_torque_at_body_2rads_Nm=H*2),servo_sensitivity=dict(thrust_endpoints_N=[-30,30],required_Nm=servo,sweep_deg=sweep,kinematic_time_s=time0,linear_torque_speed_assumption_time_s=loaded_time),limitations=['not validated negative thrust','endpoint clamping','low-speed 2D polar at rotor Mach up to .46','constant85percent efficiency','no measured motor map','no profile Cm data','rotor reaction and gyro NOT included in allocation','fixed mass and CG','no structural sizing approval'])
(OUT/'evaluacion_rotor_completo.json').write_text(json.dumps(result,indent=2));(OUT/'asignacion_mapa_rotor.json').write_text(json.dumps(allocations,indent=2))
fig,axs=plt.subplots(2,2,figsize=(12,8))
for rpm in [5000,5500,6000,6500]:
 rr=[r for r in rows if r['rpm']==rpm and r['solved']]
 axs[0,0].plot([r['target_N'] for r in rr],[r['electrical_W_assumed'] for r in rr],label=str(rpm)+' rpm')
 axs[0,1].plot([r['target_N'] for r in rr],[r['pitch_deg'] for r in rr])
axs[1,0].plot(forces,[100*r['outside_torque_fraction'] for r in reference],color='#b04b3d')
axs[1,1].bar(['Peso + control','0,5 g + control','1 g + control'],[s['max_sample_power_W']/1000 for s in summary],color=['#406b83','#52878c','#ae7044'])
axs[0,0].set(ylabel='Potencia eléctrica estimada [W]',xlabel='Empuje por rotor [N]');axs[0,0].legend()
axs[0,1].set(ylabel='Paso [grados]',xlabel='Empuje por rotor [N]')
axs[1,0].set(ylabel='Contribución fuera de dominio [%]',xlabel='Empuje por rotor [N]',title='Cobertura experimental parcial · 6.000 rpm')
axs[1,1].set(ylabel='Potencia de 8 rotores [kW]',title='Máximo muestreado · 5 kg · 6.000 rpm')
for ax in axs.flat:ax.grid(alpha=.2)
fig.suptitle('Rotor SD8020 · mapa de escritorio condicionado',fontsize=16)
fig.text(.5,.015,'No son ensayos del rotor: extrapolación marcada, eficiencia supuesta y pares reactivos pendientes.',ha='center',fontsize=10)
fig.tight_layout(rect=[0,.04,1,.95]);fig.savefig(OUT/'evaluacion_rotor_completo.png',dpi=160)
print(json.dumps(result,indent=2))
