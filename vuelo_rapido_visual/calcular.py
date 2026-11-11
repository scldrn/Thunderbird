from pathlib import Path
import numpy as np,json
from scipy.integrate import solve_ivp
from scipy.spatial.transform import Rotation as R
P=Path(__file__).resolve().parent;g=9.80665;rho=1.225;mass=5.;S=.04977;I=np.array([.035311862,.458989923,.475462439])
def pulse(t,a,b,k):return k*np.sin(np.pi*(t-a)/(b-a))**2 if a<t<b else 0.
def accelerations(t):return g*(pulse(t,1,4,3)-pulse(t,4.5,8,6)+pulse(t,8.5,11.5,10)),g*(pulse(t,3,5,2)-pulse(t,6,8,2)+pulse(t,9,11,1))
results=[]
for speed in (600,1000):
 V=speed/3.6;time=np.linspace(0,12,6001)
 def rhs(t,y):
  psi,gam=y[:2];ay,az=accelerations(t)
  return [ay/(V*np.cos(gam)),az/V,V*np.cos(gam)*np.cos(psi),V*np.cos(gam)*np.sin(psi),V*np.sin(gam)]
 sol=solve_ivp(rhs,(0,12),[0,0,0,0,150],t_eval=time,rtol=1e-10,atol=1e-11,max_step=.005);assert sol.success
 state=sol.y.T;psi=state[:,0];gam=state[:,1];pos=state[:,2:5]
 tangent=np.column_stack([np.cos(gam)*np.cos(psi),np.cos(gam)*np.sin(psi),np.sin(gam)])
 normalh=np.column_stack([-np.sin(psi),np.cos(psi),np.zeros(len(time))]);normalv=np.column_stack([-np.sin(gam)*np.cos(psi),-np.sin(gam)*np.sin(psi),np.cos(gam)])
 ayaz=np.array([accelerations(t) for t in time]);acc=ayaz[:,0,None]*normalh+ayaz[:,1,None]*normalv
 nongrav=mass*(acc+np.array([0,0,g]));axial=np.sum(nongrav*tangent,axis=1);normal=nongrav-axial[:,None]*tangent;N=np.linalg.norm(normal,axis=1)
 bz=normal/N[:,None];by=np.cross(bz,tangent);rot=np.stack([tangent,by,bz],axis=2);rotation=R.from_matrix(rot)
 q=rotation.as_quat();dq=rotation[:-1].inv()*rotation[1:];omega=dq.as_rotvec()/.002;omega=np.vstack([omega,omega[-1]]);alpha=np.gradient(omega,.002,axis=0);tau=alpha*I+np.cross(omega,omega*I)
 Cn=N/(.5*rho*V**2*S);D=.5*rho*V**2*S*(.06+.12*Cn**2);thrust=D+axial
 bank=np.rad2deg(np.arctan2(ayaz[:,0],g*np.cos(gam)+ayaz[:,1]));qbar=.5*rho*V**2
 np.savez_compressed(P/f'{speed}kmh.npz',time=time,position=pos,velocity=tangent*V,acceleration=acc,quaternion=q,rotation=rot,omega=omega,torque_required=tau,normal_force=N,drag_assumed=D,thrust_required_assumed=thrust,power_required_assumed=thrust*V,bank_deg=bank,lateral_g=ayaz[:,0]/g,vertical_g=ayaz[:,1]/g,load_factor=N/(mass*g),q_Pa=qbar)
 radius=V**2/(10*g)
 residual=np.max(np.linalg.norm(nongrav-(normal+axial[:,None]*tangent),axis=1))
 result=dict(speed_kmh=speed,Mach_assumed=V/340.3,dynamic_pressure_Pa=qbar,ten_g_lateral_radius_m=radius,max_required_normal_force_N=float(N.max()),max_assumed_drag_N=float(D.max()),max_assumed_thrust_N=float(thrust.max()),max_assumed_useful_power_kW=float((thrust*V).max()/1000),max_required_torque_Nm=float(np.linalg.norm(tau,axis=1).max()),max_bank_deg=float(np.abs(bank).max()),force_reconstruction_residual_N=float(residual),distance_m=V*12,minimum_height_m=float(pos[:,2].min()))
 results.append(result);print(result)
(P/'RESULTADOS.json').write_text(json.dumps(results,indent=2))
