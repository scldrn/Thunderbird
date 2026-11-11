"""Low-speed rigid 6DOF conditional simulation. Not CFD or validated hardware.
Plant: p,v,R,omega,8 signed thrust states; first-order actuator + saturation.
Reference: 1m out/back quintic, then 30deg rotation. Controller not optimized.
"""
from pathlib import Path
import os,json,csv
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
os.environ['MPLCONFIGDIR']=str(OUT/'mpl-cache')
import numpy as np
from scipy.spatial.transform import Rotation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from calcular import G
DATA=json.loads((OUT/'candidato_dinamica_CONDICIONAL.json').read_text())
MODEL=DATA['model'];B=np.array(MODEL['B']);P=np.array(MODEL['allocator']);J=np.array(MODEL['J']);JI=np.linalg.inv(J);M=MODEL['mass'];L=MODEL['L'];LIMIT=np.array(MODEL['limits'])

def profile(t,t0,duration):
    z=(t-t0)/duration
    if z<=0:return 0.,0.,0.
    if z>=1:return 1.,0.,0.
    return 10*z**3-15*z**4+6*z**5,(30*z*z-60*z**3+30*z**4)/duration,(60*z-180*z*z+120*z**3)/duration**2

def reference(t,R0,duration):
    s,v,a=profile(t,.25,duration);s2,v2,a2=profile(t,1.65,duration)
    pos=np.array([s-s2,0.,0.]);vel=np.array([v-v2,0.,0.]);acc=np.array([a-a2,0.,0.])
    z,dz,ddz=profile(t,2.85,.8);axis=np.array([0.,0.,1.]);angle=np.pi/6
    Rd=R0@Rotation.from_rotvec(axis*z*angle).as_matrix()
    return pos,vel,acc,Rd,axis*dz*angle,axis*ddz*angle

def simulate(tau,compensate,tilt,dt=.002,duration=.8,hover_only=False,estimated_tau=None):
    R0=Rotation.from_euler('y',tilt,degrees=True).as_matrix();R=R0.copy();p=np.zeros(3);v=p.copy();omega=p.copy()
    f=P@np.r_[R.T@np.array([0,0,M*G]),np.zeros(3)];previous=f.copy();history=[]
    count=0;worst_saturation=0.
    for i in range(round(4.1/dt)):
        t=i*dt
        if hover_only:pd=vd=ad=np.zeros(3);Rd=R0;wd=alphad=np.zeros(3)
        else:pd,vd,ad,Rd,wd,alphad=reference(t,R0,duration)
        Fworld=M*(ad+9*(pd-p)+6*(vd-v)+np.array([0,0,G]))
        err=Rotation.from_matrix(R.T@Rd).as_rotvec()
        wd_body=R.T@Rd@wd
        torque=J@(16*err+8*(wd_body-omega)+R.T@Rd@alphad)+np.cross(omega,J@omega)
        desired=P@np.r_[R.T@Fworld,torque/L]
        # Inverse lag feedforward applies only to the declared first-order model.
        command=desired+(tau if estimated_tau is None else estimated_tau)*(desired-previous)/dt if compensate else desired
        previous=desired
        ratio=np.max(abs(command)/LIMIT);worst_saturation=max(worst_saturation,float(ratio))
        if ratio>1:count+=1
        command=np.clip(command,-LIMIT,LIMIT)
        nextf=command+(f-command)*np.exp(-dt/tau)
        meanf=command+(f-command)*tau/dt*(1-np.exp(-dt/tau))
        wrench=B@meanf;force=wrench[:3];torque=wrench[3:]*L
        # Midpoint rigid-body angular integration; exact exponential orientation update.
        alpha=JI@(torque-np.cross(omega,J@omega));whalf=omega+.5*dt*alpha
        alpha_mid=JI@(torque-np.cross(whalf,J@whalf));wnext=omega+dt*alpha_mid
        Rmid=R@Rotation.from_rotvec(.5*dt*whalf).as_matrix()
        accel=Rmid@force/M-np.array([0,0,G]);p=p+v*dt+.5*accel*dt*dt;v=v+accel*dt
        R=R@Rotation.from_rotvec(dt*whalf).as_matrix();omega=wnext;f=nextf
        pdt,_,_,Rdt,_,_=reference(t+dt,R0,duration) if not hover_only else (np.zeros(3),None,None,R0,None,None)
        attitude=np.linalg.norm(Rotation.from_matrix(R.T@Rdt).as_rotvec())*180/np.pi
        history.append([t+dt,*p,*pdt,*v,*accel,float(np.linalg.norm(p-pdt)),attitude,float(ratio)])
    ar=np.array(history)
    result=dict(estimated_tau_s=tau if estimated_tau is None else estimated_tau,tau_s=tau,lag_compensation=compensate,initial_pitch_deg=tilt,dt_s=dt,reference_duration_s=duration,position_RMSE_m=float(np.sqrt(np.mean(ar[:,13]**2))),position_max_error_m=float(np.max(ar[:,13])),attitude_max_error_deg=float(np.max(ar[:,14])),command_saturated_fraction=count/len(ar),max_unclipped_command_ratio=worst_saturation,max_translational_accel_g=float(np.max(np.linalg.norm(ar[:,10:13],axis=1))/G),final_error_m=float(ar[-1,13]),status='ideal_first_order_plant_not_actuator_validation')
    return result,ar

def main():
    cases=[];plots=[]
    h,ha=simulate(.07,False,90,hover_only=True)
    assert h['position_max_error_m']<1e-8 and h['attitude_max_error_deg']<1e-7
    for tau in [.03,.07,.15]:
     for comp in [False,True]:
      for tilt in [0,90]:
       r,a=simulate(tau,comp,tilt);cases.append(r)
       if tilt==0:plots.append((r,a))
    r1,a=simulate(.07,True,90,dt=.002);r2,b=simulate(.07,True,90,dt=.001)
    difference=float(np.max(np.linalg.norm(a[:,1:4]-b[1::2,1:4],axis=1)))
    assert difference<.01
    with (OUT/'dinamica_6DOF_CONDICIONAL.csv').open('w') as f:
      w=csv.DictWriter(f,fieldnames=cases[0]);w.writeheader();w.writerows(cases)
    with (OUT/'trayectoria_6DOF_ejemplo.csv').open('w') as f:
      w=csv.writer(f);w.writerow(['t','x','y','z','xd','yd','zd','vx','vy','vz','ax','ay','az','position_error','attitude_error_deg','command_ratio']);w.writerows(a)
    (OUT/'verificacion_dinamica.json').write_text(json.dumps(dict(hover_test=h,max_position_difference_dt_halving_m=difference,not_verified=['rotor_reversal','variable_pitch_dynamics','rotor_gyro','aerodynamics','flexibility','sensing','retraction']),indent=2))
    fig,axs=plt.subplots(2,1,figsize=(9,6),sharex=True)
    for r,a in plots:
      label=f"τ={r['tau_s']*1000:.0f} ms, "+('compensado' if r['lag_compensation'] else 'sin compensar')
      axs[0].plot(a[:,0],a[:,1],label=label,lw=1.3);axs[1].plot(a[:,0],a[:,13],lw=1.3)
    axs[0].plot(a[:,0],a[:,4],'k--',label='Referencia',lw=1)
    axs[0].set_ylabel('Posición x [m]');axs[1].set_ylabel('Error de posición [m]');axs[1].set_xlabel('Tiempo [s]')
    axs[0].legend(fontsize=8,ncol=2);[ax.grid(alpha=.2) for ax in axs]
    fig.suptitle('Simulación 6DOF ideal · actuadores de primer orden · inversión de trayectoria')
    fig.text(.5,.01,'Candidato optimista no validado; compensación conoce exactamente el retardo dinámico.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.03,1,.95]);fig.savefig(OUT/'dinamica_6DOF.png',dpi=160)
    print(json.dumps(dict(verification=difference,cases=cases),indent=2))
if __name__=='__main__':main()
