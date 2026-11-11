"""Exact static wrench feasibility for an IDEAL signed-thrust candidate family.
Numerically optimize only the declared family; not an aircraft hardware design.
"""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
os.environ['MPLCONFIGDIR']=str(ROOT/'resultados'/'mpl-cache')
import numpy as np
from scipy.optimize import linprog, differential_evolution
from itertools import product, combinations
import json,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from calcular import geometry,G
OUT=ROOT/'resultados'
SIGNS=np.array(list(product([-1.,1.],repeat=3)))
COMB=list(combinations(range(8),5))

def allocation(L,D,radial_D,theta,phi,kappa=0.):
    a=.2*L;b=radial_D*D/np.sqrt(2)
    positions=SIGNS*np.array([a,b,b])
    c=np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
    sx,sy,sz=SIGNS.T
    normals=np.array([c[0]*sy*sz,c[1]*sx*sz,c[2]*sx*sy]).T
    # Reaction torque assumed proportional to signed thrust; must be measured for VP.
    moments=np.cross(positions,normals)+kappa*(sx*sy*sz)[:,None]*normals
    B=np.vstack([normals.T,moments.T/L])
    return B,positions,normals

def facets(B):
    if np.linalg.matrix_rank(B,tol=1e-9)<6:return None,None
    ns=[]
    for ids in COMB:
        _,s,v=np.linalg.svd(B[:,ids].T,full_matrices=True)
        if s[-1]<1e-9:continue
        n=v[-1];ns.append(n)
    ns=np.array(ns)
    return ns,np.sum(np.abs(ns@B),axis=1)

def guaranteed_force(B,L,T,tau):
    n,h=facets(B)
    if n is None:return -1e6
    nf=np.linalg.norm(n[:,:3],axis=1);nt=np.linalg.norm(n[:,3:],axis=1)
    margin=T*h-tau/L*nt
    if np.any(margin[nf<1e-8]<-1e-8):return -1e6
    return float(np.min(margin[nf>=1e-8]/nf[nf>=1e-8]))

def directional(B,L,T,force_base,force_direction,torque):
    # maximize acceleration force amplitude along direction, prescribed torque.
    A=np.column_stack([B,-np.r_[force_direction,[0.,0.,0.]]])
    target=np.r_[force_base,np.array(torque)/L]
    result=linprog(np.r_[np.zeros(8),-1.],A_eq=A,b_eq=target,bounds=[(-T,T)]*8+[(None,None)],method='highs')
    return result

def main():
    records=[];best_angles={}
    for mass in [2,5,10]:
      geo=geometry(mass/200,6,'esferoide');L,D=geo['L_m'],geo['D_m']
      # Scenario: scalar sum of maximum rotor forces = 6 weight.
      T=6*mass*G/8
      # Scenario: 20% mass point modules; remaining mass half skin half core.
      for radial in [.5,1.,1.5,2.,2.5]:
       a=.2*L;r=radial*D;mr=.2*mass;rest=mass-mr
       ix=.5*rest*geo['shell_Ix_per_kg']+.5*rest*.4*(.35*D)**2+mr*r*r
       iy=.5*rest*geo['shell_Iy_per_kg']+.5*rest*.4*(.35*D)**2+mr*(a*a+r*r/2)
       # Guarantee angular acceleration in ANY axis conservatively using largest inertia.
       reserve=2*max(ix,iy)  # 2 rad/s², arbitrary declared maneuver reserve.
       def objective(v):return -guaranteed_force(allocation(L,D,radial,*v)[0],L,T,reserve)
       opt=differential_evolution(objective,[(.06,np.pi-.06),(-np.pi,np.pi)],seed=42,popsize=7,maxiter=45,tol=1e-5,polish=False)
       B,pos,normals=allocation(L,D,radial,*opt.x)
       fg=-opt.fun
       noreserve=guaranteed_force(B,L,T,0)
       n,h=facets(B);nf=np.linalg.norm(n[:,:3],axis=1);nt=np.linalg.norm(n[:,3:],axis=1)
       # All attitudes hover + requested isotropic torque ball.
       tau_guaranteed=float(np.min((T*h-mass*G*nf)[nt>1e-8]/nt[nt>1e-8])*L)
       # actuator force required for acceleration ball 1g plus same moment reserve.
       t_req=float(np.max((2*mass*G*nf+reserve/L*nt)/h))
       rec=dict(mass_kg=mass,radial_D=radial,rotor_abs_limit_N=T,sum_abs_limits_over_weight=6,torque_reserve_Nm=reserve,Ix=ix,Iy=iy,theta_rad=opt.x[0],phi_rad=opt.x[1],force_ball_N=fg,guaranteed_acceleration_g=fg/(mass*G)-1,force_ball_no_moment_N=noreserve,torque_ball_at_hover_Nm=tau_guaranteed,angular_accel_bound_rad_s2=tau_guaranteed/max(ix,iy),per_rotor_limit_for_1g_N=t_req,sum_limit_weight_for_1g=8*t_req/(mass*G),status='ideal_axes_no_collision_or_mass_closure')
       records.append(rec)
       if mass==10 and radial==2:
        best_angles=dict(B_normalized=B.tolist(),positions_m=pos.tolist(),thrust_unit_vectors=normals.tolist(),record=rec)
    with (OUT/'control_estatico_ESCENARIOS.csv').open('w') as f:
      wr=csv.DictWriter(f,fieldnames=records[0]);wr.writeheader();wr.writerows(records)
    (OUT/'configuracion_control_HIPOTESIS.json').write_text(json.dumps(best_angles,indent=2))
    # Independent LP validation: random directions, gravity orientations, bounded torque.
    B=np.array(best_angles['B_normalized']);rec=best_angles['record'];L=geometry(.05,6,'esferoide')['L_m'];T=rec['rotor_abs_limit_N'];tau=rec['torque_reserve_Nm'];fg=rec['force_ball_N']
    rng=np.random.default_rng(17);violations=0;residual=0.
    for _ in range(150):
      v=rng.normal(size=3);v/=np.linalg.norm(v)
      t=rng.normal(size=3);t*=tau/np.linalg.norm(t)
      target=np.r_[fg*v,t/L]
      lp=linprog(np.zeros(8),A_eq=B,b_eq=target,bounds=[(-T,T)]*8,method='highs')
      if not lp.success:violations+=1
      else:residual=max(residual,float(np.max(np.abs(B@lp.x-target))))
    assert violations==0
    # Radial maximum on a limiting facet must be attainable and immediately beyond infeasible.
    ns,hs=facets(B);nf=np.linalg.norm(ns[:,:3],axis=1);nt=np.linalg.norm(ns[:,3:],axis=1)
    valid=nf>1e-8;indices=np.flatnonzero(valid);j=indices[np.argmin((T*hs[valid]-tau/L*nt[valid])/nf[valid])]
    v=ns[j,:3]/nf[j];t=tau*ns[j,3:]/nt[j] if nt[j]>1e-9 else np.zeros(3)
    lp=directional(B,L,T,np.zeros(3),v,t)
    assert lp.success and abs(lp.x[-1]-fg)<1e-6
    target=np.r_[(fg+1e-3)*v,t/L]
    outside=linprog(np.zeros(8),A_eq=B,b_eq=target,bounds=[(-T,T)]*8,method='highs')
    assert not outside.success
    verify=dict(random_feasibility_checks=150,violations=violations,max_equality_residual=residual,limiting_facet_force_N=fg,independent_LP_force_N=lp.x[-1],outside_point_rejected=not outside.success,optimization='bounded stochastic search, seed42; not proof of optimal axes',physical_validation=False)
    (OUT/'verificacion_control.json').write_text(json.dumps(verify,indent=2))
    plt.rcParams.update({'font.size':10})
    fig,ax=plt.subplots(1,2,figsize=(11,4.8))
    for mass in [2,5,10]:
      subset=[r for r in records if r['mass_kg']==mass]
      x=[r['radial_D'] for r in subset]
      ax[0].plot(x,[r['guaranteed_acceleration_g'] for r in subset],'o-',label=f'{mass} kg')
      ax[1].plot(x,[r['angular_accel_bound_rad_s2'] for r in subset],'o-',label=f'{mass} kg')
    for a in ax:a.set_xlabel('Radio de módulos / diámetro del fuselaje');a.grid(alpha=.2);a.legend()
    ax[0].set_ylabel('Aceleración traslacional garantizada por modelo [g]');ax[0].axhline(1,color='gray',ls='--')
    ax[1].set_ylabel('Aceleración angular conservadora en hover [rad/s²]')
    fig.suptitle('Hipótesis ideal: 8 propulsores bidireccionales · suma de límites = 6 pesos')
    fig.text(.5,.015,'Cada punto optimiza ejes por separado. Sin interferencias, límites eléctricos ni cierre de masa.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.04,1,.94]);fig.savefig(OUT/'control_despliegue.png',dpi=170);plt.close(fig)
    print(json.dumps(dict(example=rec,verification=verify),indent=2))
if __name__=='__main__':main()
