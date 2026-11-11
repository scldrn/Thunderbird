"""Mass/inertia/actuator/power fixed point with an explicit linear allocator.
All technology envelopes are assumptions, except identified engine reference.
Power bound is conservative over force/torque balls, independent isolated disks.
"""
from pathlib import Path
import os,json,csv
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
os.environ['MPLCONFIGDIR']=str(OUT/'mpl-cache')
import numpy as np
from calcular import geometry,G,RHO
from control import allocation

TECH={
'referencia_extrapolada':dict(specific=50/.448,eff=.65,bpower=4000,energy=200,skin=1.7),
'optimista_no_verificada':dict(specific=200.,eff=.8,bpower=8000,energy=220,skin=1.0)}

def inertia(parts):
    mass=sum(p[0] for p in parts);cg=sum(m*r for m,r,I in parts)/mass
    J=sum(I+m*(np.dot(r-cg,r-cg)*np.eye(3)-np.outer(r-cg,r-cg)) for m,r,I in parts)
    return mass,cg,J

def calc(target,diam,radial,ag,hover_s,fuel_min,tech,engine=True,engine_spec=None,fineness=6,extra_mass=0.):
    geo=geometry(target/200,fineness,'esferoide',n=400)
    spec=engine_spec or dict(mass=2.155,fuel_kg_min=.656,diameter=.121,length=.323);L,D=geo['L_m'],geo['D_m']
    d=json.loads((OUT/'configuracion_control_HIPOTESIS.json').read_text())['record']
    _,positions,normals=allocation(L,D,radial,d['theta_rad'],d['phi_rad'])
    # Radius-only sufficient clearance conditions: conservative, not swept folding check.
    hull_clearance=radial*D-diam/2-D/2
    pair_clearance=min(np.linalg.norm(a-b) for i,a in enumerate(positions) for b in positions[i+1:])-diam
    fuel=spec['fuel_kg_min']*fuel_min if engine else 0.;motor_mass=np.ones(8)*target*.04;battery=.15*target
    skin=geo['wet_m2']*tech['skin'];arms=.04*target;avionics=.02*target+extra_mass
    engmass=spec['mass'] if engine else 0.
    history=[];converged=False
    for step in range(150):
        parts=[]
        parts.append((skin,np.zeros(3),skin*np.diag([geo['shell_Ix_per_kg'],geo['shell_Iy_per_kg'],geo['shell_Iy_per_kg']])))
        # Half of arms assigned to center, half to tips approximates rod moment poorly;
        # use exact uniform straight radial rods from surface to hub.
        for i,pos in enumerate(positions):
            start=np.array([pos[0],pos[1],pos[2]])
            start[1:]*=(D/2)/(radial*D)
            delta=pos-start;center=(pos+start)/2;ma=arms/8
            ji=ma/12*(delta@delta*np.eye(3)-np.outer(delta,delta))
            parts.append((ma,center,ji))
            # motor+prop as thin disk is an explicit conservative/simplified shape assumption.
            mm=motor_mass[i];n=normals[i];jdisc=mm*(diam/2)**2/4*(np.eye(3)+np.outer(n,n))
            parts.append((mm,pos,jdisc))
        for mm in [battery,avionics,fuel]:parts.append((mm,np.zeros(3),mm*.4*(.2*D)**2*np.eye(3)))
        if engine:
            # Engine measured reference external envelope; uniform cylinder inertia assumption.
            r=spec['diameter']/2;ell=spec['length']
            parts.append((engmass,np.array([.27*L,0,0]),np.diag([engmass*r*r/2,engmass*(3*r*r+ell*ell)/12,engmass*(3*r*r+ell*ell)/12])))
        nominal=sum(p[0] for p in parts)
        ballast=max(0.,2.-nominal)
        if ballast:parts.append((ballast,np.zeros(3),ballast*.4*(.2*D)**2*np.eye(3)))
        mass,cg,J=inertia(parts)
        moment=np.cross(positions-cg,normals)
        B=np.vstack([normals.T,moment.T/L]);P=np.linalg.pinv(B)
        rank=np.linalg.matrix_rank(B)
        if rank<6:break
        fn=np.linalg.norm(P[:,:3],axis=1);tn=np.linalg.norm(P[:,3:],axis=1)
        reserve=2*np.linalg.eigvalsh(J)[-1]
        limits=mass*G*(1+ag)*fn+reserve/L*tn
        hoverloads=mass*G*fn+reserve/L*tn
        factor=1/(np.sqrt(2*RHO*np.pi*diam**2/4)*tech['eff'])
        peak=float(np.sum(limits**1.5)*factor);hover=float(np.sum(hoverloads**1.5)*factor)
        required_motor=limits/tech['specific']
        required_battery=max(peak/tech['bpower'],(.9*hover+.1*peak)*hover_s/3600/tech['energy'])
        newmass=max(2.,skin+arms+avionics+engmass+fuel+required_motor.sum()+required_battery)
        history.append(float(newmass))
        if newmass>200 or not np.isfinite(newmass):break
        err=max(np.max(abs(required_motor-motor_mass)),abs(required_battery-battery))
        if err<1e-8:
            converged=True;break
        motor_mass=.5*(motor_mass+required_motor);battery=.5*(battery+required_battery)
    result=dict(target_kg=target,technology=next(k for k,v in TECH.items() if v==tech),reactor=engine,rotor_diameter_m=diam,radial_D=radial,requested_acceleration_g=ag,hover_seconds=hover_s,fuel_minutes_full_throttle=fuel_min if engine else 0,converged=converged,equilibrium_mass_kg=mass if converged else None,mass_within_target=bool(converged and mass<=target+1e-7),hull_clearance_sufficient_m=hull_clearance,pair_clearance_sufficient_m=pair_clearance,clearance_sufficient=bool(hull_clearance>=0 and pair_clearance>=0),cg_x_m=float(cg[0]),Ix=float(J[0,0]),Iy=float(J[1,1]),Iz=float(J[2,2]),ballast_kg=ballast,motors_mass_kg=float(motor_mass.sum()),battery_kg=float(battery),power_peak_upper_W=peak,power_hover_upper_W=hover,iteration_steps=len(history),last_iterate_mass_kg=history[-1] if history else mass,status='conditional_technology_and_linear_allocator_no_hardware_validation')
    return result,dict(B=B.tolist(),allocator=P.tolist(),J=J.tolist(),cg=cg.tolist(),positions=positions.tolist(),normals=normals.tolist(),limits=limits.tolist(),mass=float(mass),L=L,history=history)

def main():
    rows=[];examples=[]
    for target in [2.,5.,10.]:
     for t in TECH.values():
      for eng in [False,True]:
       for diam in [.2,.3,.4]:
        for ag in [.5,1.,2.]:
         r,data=calc(target,diam,2.,ag,30.,.5,t,eng)
         rows.append(r)
         if r['converged'] and r['mass_within_target'] and r['clearance_sufficient']:examples.append((r,data))
    with (OUT/'cierre_masa_iterativo_CONDICIONAL.csv').open('w') as f:
      wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
    # Validate independent random force/moment requests against explicit actuator limits.
    checks=[];rng=np.random.default_rng(21)
    for r,d in examples:
      B=np.array(d['B']);P=np.array(d['allocator']);J=np.array(d['J']);lim=np.array(d['limits']);L=d['L'];m=d['mass']
      error=0.;ratio=0.
      for _ in range(100):
        v=rng.normal(size=3);v/=np.linalg.norm(v);tau=rng.normal(size=3);tau/=np.linalg.norm(tau)
        wrench=np.r_[m*G*(1+r['requested_acceleration_g'])*v,2*np.linalg.eigvalsh(J)[-1]*tau/L]
        f=P@wrench;error=max(error,float(np.max(abs(B@f-wrench))));ratio=max(ratio,float(np.max(abs(f)/lim)))
      assert error<1e-7 and ratio<=1+1e-9
      checks.append(dict(target=r['target_kg'],engine=r['reactor'],a_g=r['requested_acceleration_g'],max_residual=error,max_actuator_ratio=ratio))
    (OUT/'verificacion_cierre_masa.json').write_text(json.dumps(dict(scenarios=len(rows),conditional_passes=len(examples),checks=checks),indent=2))
    if examples:
      preferred=sorted(examples,key=lambda p:(not p[0]['reactor'],abs(p[0]['requested_acceleration_g']-1),abs(p[0]['target_kg']-10)))[0]
      (OUT/'candidato_dinamica_CONDICIONAL.json').write_text(json.dumps(dict(result=preferred[0],model=preferred[1]),indent=2))
    print(json.dumps(dict(scenarios=len(rows),passes=len(examples),examples=[r for r,d in examples][:10]),indent=2))
if __name__=='__main__':main()
