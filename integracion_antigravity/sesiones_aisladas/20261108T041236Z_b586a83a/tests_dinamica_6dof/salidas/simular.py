from pathlib import Path
import numpy as np,json,csv
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as R
P=Path(__file__).resolve().parent;G=9.80665

def rigid_rhs(y,F,A,I,mass,ext,et):
 q=y[6:10];q=q/np.linalg.norm(q);om=y[10:13];rot=R.from_quat(q)
 acc=(rot.apply(F.sum(axis=0))+ext)/mass-np.array([0,0,G]);torque=(A@F.ravel())[3:]+et
 qdot=.5*np.r_[q[3]*om+np.cross(q[:3],om),-np.dot(q[:3],om)]
 return np.r_[y[3:6],acc,qdot,(torque-np.cross(om,I*om))/I]

def rk4_step(state,dt,F,A,I,mass,ext,et):
 def f(y):return rigid_rhs(y,F,A,I,mass,ext,et)
 a=f(state);b=f(state+dt*a/2);c=f(state+dt*b/2);d=f(state+dt*c)
 y=state+dt/6*(a+2*b+2*c+d);y[6:10]/=np.linalg.norm(y[6:10]);return y

def run(mass=5.,dt=.005,capacity=1.,save=True):
 scale=(mass/5)**(1/3);I=mass*np.array([.321821**2+.194110**2,1.341**2+.194110**2,1.341**2+.321821**2])/20*scale**2
 xy=np.array([[-.2,-.076],[-.2,.076],[.2,-.076],[.2,.076]])*scale
 A=np.zeros((6,12))
 for i,(x,y) in enumerate(xy):
  A[:3,3*i:3*i+3]=np.eye(3)
  A[3:,3*i:3*i+3]=np.array([[0,.021*scale,y],[-.039*scale,0,-x],[-y,x,0]])
 T=21*mass/5*capacity;cone=np.tan(np.deg2rad(35));rate=50*mass/5;tau=.08
 f=np.tile([0,0,mass*G/4],(4,1));previous=f.copy();state=np.r_[0.,0.,2.,0.,0.,0.,R.from_euler('xyz',[5,0,5],degrees=True).as_quat(),0.,0.,0.]
 W=np.array([1/mass]*3+[4/(mass/5)**(4/3)]*3);H=(W[:,None]*A);history=[];bad=0;optfail=0;maxviol=0;command=f.copy();resid=[]
 def ref(t):
  if t<4:return np.array([0.,0.,2.])
  if t<8:return np.array([2.,0.,2.])
  if t<12:return np.array([2.,2.,2.])
  if t<16:return np.array([2.,2.,3.5])
  if t<20:return np.array([-1.,-1.,2.])
  return np.array([0.,0.,2.])
 def con(v):
  z=v.reshape(4,3);return np.r_[T*T-np.sum(z*z,axis=1),(cone*z[:,2])**2-z[:,0]**2-z[:,1]**2]
 def jac(v):
  z=v.reshape(4,3);j=np.zeros((8,12))
  for i in range(4):
   j[i,3*i:3*i+3]=-2*z[i];j[4+i,3*i:3*i+3]=[-2*z[i,0],-2*z[i,1],2*cone**2*z[i,2]]
  return j
 def rhs(y,F,ext,et):return rigid_rhs(y,F,A,I,mass,ext,et)
 steps=int(round(24/dt));stride=round(.02/dt)
 for k in range(steps+1):
  t=k*dt;pos=state[:3];vel=state[3:6];rot=R.from_quat(state[6:10]);om=state[10:];reference=ref(t)
  ext=np.array([3.,-2.,0.])*mass/5 if 12<=t<13 else np.zeros(3);et=np.array([.03,.02,.01])*mass/5*scale if 12<=t<13 else np.zeros(3)
  if k%stride==0:
   ac=3*(reference-pos)-3*vel;n=np.linalg.norm(ac)
   if n>.5*G:ac*=.5*G/n
   force=rot.inv().apply(mass*(ac+np.array([0,0,G])))
   alpha=-8*rot.as_rotvec()-5*om;torque=I*alpha+np.cross(om,I*om);torque=np.clip(torque,-.4*mass/5*scale,.4*mass/5*scale)
   desired=np.r_[force,torque];b=W*desired;anchor=previous.ravel().copy()
   def obj(v):e=H@v-b;d=v-anchor;return .5*(e@e+1e-5*(d@d))
   def grad(v):return H.T@(H@v-b)+1e-5*(v-anchor)
   sol=minimize(obj,anchor,jac=grad,method='SLSQP',bounds=[(-T,T),(-T,T),(mass/5,T)]*4,constraints=[dict(type='ineq',fun=con,jac=jac)],options=dict(ftol=1e-9,maxiter=100))
   if not sol.success:optfail+=1
   if con(sol.x).min()<-1e-5:bad+=1
   command=sol.x.reshape(4,3);previous=command.copy();resid.append(float(np.linalg.norm(A@sol.x-desired)))
  norm=np.linalg.norm(f,axis=1);ang=np.rad2deg(np.arctan2(np.linalg.norm(f[:,:2],axis=1),f[:,2]));acc=rhs(state,f,ext,et)[3:6]
  history.append(np.r_[t,state,reference,f.ravel(),acc,ang,ext])
  if k==steps:break
  df=(command-f)*(1-np.exp(-dt/tau));dn=np.linalg.norm(df,axis=1);df*=np.minimum(1,rate*dt/np.maximum(dn,1e-12))[:,None];f=f+df
  state=rk4_step(state,dt,f,A,I,mass,ext,et)
 h=np.array(history);forces=h[:,17:29].reshape(-1,4,3)
 summary=dict(mass_assumed_kg=mass,inertia_assumed_kgm2=I.tolist(),dt_s=dt,capacity_factor=capacity,max_speed_ms=float(np.linalg.norm(h[:,4:7],axis=1).max()),max_acceleration_ms2=float(np.linalg.norm(h[:,29:32],axis=1).max()),min_altitude_m=float(h[:,3].min()),max_altitude_m=float(h[:,3].max()),final_position_error_m=float(np.linalg.norm(h[-1,1:4]-h[-1,14:17])),max_attitude_deg=float(np.rad2deg(R.from_quat(h[:,7:11]).magnitude()).max()),max_fan_force_N=float(np.linalg.norm(forces,axis=2).max()),max_force_rate_Ns=float(np.linalg.norm(np.diff(forces,axis=0)/dt,axis=2).max()),max_force_angle_deg=float(h[:,32:36].max()),solver_unsuccessful_steps=optfail,infeasible_allocation_steps=bad,final_speed_ms=float(np.linalg.norm(h[-1,4:7])),simulation_scope='Conditional low-speed rigid-body ideal-vector-thrust model; not validated installed plant')
 if save:
  stem=f'{mass:g}kg_'+('nominal' if capacity==1 else 'capacidad_reducida')
  np.savez_compressed(P/f'{stem}.npz',history=h,inertia=I,positions_xy=xy)
  (P/f'{stem}.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps(summary),flush=True)
 return h,summary

if __name__=='__main__':
 results=[]
 for mass in (2.,5.,10.):results.append(run(mass)[1])
 results.append(run(5.,capacity=.8)[1])
 (P/'RESULTADOS.json').write_text(json.dumps(results,indent=2))
