"""Mass redistribution and conservative rotational-load sensitivity; assumed blades."""
from pathlib import Path
import json,csv,sys
import numpy as np
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'legacy'/'scripts'))
from control import facets
E=np.eye(3)
def shift(m,p):return m*((p@p)*E-np.outer(p,p))
def cyl(m,r,h,n):return m*(3*r*r+h*h)/12*(E-np.outer(n,n))+.5*m*r*r*np.outer(n,n)
records=[];summaries=[]
for m in [5,10]:
 folder=ROOT/'candidato_ejes'/f'{m}kg';d=json.loads((folder/'mediciones_DIGITALES.json').read_text());scale=(m/5)**(1/3);massscale=m/5
 p=np.array(d['rotor_centers_m']);n=np.array(d['rotor_axes']);cg=np.array(d['CG_geometric_components_only_m']);gm=d['geometric_mass_kg'];I0=np.array(d['inertia_geometric_components_only_kgm2']);J=I0+shift(gm,cg);first=gm*cg
 table={r['componente']:r for r in csv.DictReader((folder/'masas_y_centros_ESTIMADOS.csv').open())}
 R=d['rotor_diameter_m']/2;r0=.04*scale;c=.03*scale;blade_mass=.03*massscale
 bladeJ=blade_mass*((R*R+R*r0+r0*r0)/3+c*c/12)
 for j,(center,axis) in enumerate(zip(p,n)):
  row=table[f'modulo_{j+1}'];mount=np.array([float(row[k]) for k in ['x_m','y_m','z_m']]);old=.198*massscale
  J-=cyl(old,.0278*scale,.032*scale,axis)+shift(old,mount);first-=old*mount
  motor=.128*massscale;servo_esc=.04*massscale
  J+=cyl(motor,.0278*scale,.032*scale,axis)+shift(motor+servo_esc,mount)
  J+=bladeJ*(.5*E+.5*np.outer(axis,axis))+shift(blade_mass,center)
  first+=(motor+servo_esc)*mount+blade_mass*center
  assert abs(motor+servo_esc+blade_mass-old)<1e-12
 newcg=first/gm;I=J-shift(gm,newcg);eig=np.linalg.eigvalsh(I);assert min(eig)>0
 # preserve tip speed by geometrically scaling RPM; not a selected motor operating point
 rpm=6000/scale;H=bladeJ*rpm*2*np.pi/60;spin=np.r_[np.ones(4),-np.ones(4)]
 assert np.linalg.norm((spin*H)@n)<1e-10
 B=np.vstack([n.T,np.cross(p-newcg,n).T/d['L_m']]);ns,hs=facets(B);nf=np.linalg.norm(ns[:,:3],axis=1);nt=ns[:,3:];tn=np.linalg.norm(nt,axis=1)
 for omega in [0,2,5,10]:
  for mismatch in [0,.05,.1]:
   gyro=mismatch*H*omega*np.sum(np.linalg.norm(np.cross(nt[:,None,:],n[None,:,:]),axis=2),axis=1)
   euler=.5*(eig[-1]-eig[0])*omega**2*tn
   for accel in [0,.5,1]:
    angular=2.;force=d['total_budget_kg']*9.80665*(1+accel)
    demand=force*nf+(angular*np.linalg.norm(nt@I,axis=1)+euler+gyro)/d['L_m']
    required=float(np.max(demand/hs))
    records.append(dict(target_mass_kg=m,body_rate_rad_s=omega,independent_rpm_mismatch_fraction=mismatch,additional_acceleration_g=accel,angular_acceleration_rad_s2=angular,sufficient_symmetric_T_N=required,Euler_torque_ball_Nm=.5*(eig[-1]-eig[0])*omega**2,one_rotor_gyro_upper_Nm=H*omega*(1+mismatch)))
 out=ROOT/'masas_distribuidas'/f'{m}kg';out.mkdir(parents=True,exist_ok=True)
 d['CG_geometric_components_only_m']=newcg.tolist();d['inertia_geometric_components_only_kgm2']=I.tolist();d['mass_model_note']='Assumed two uniform rectangular blades, spin averaged; motor uniform cylinder; servo and ESC point masses at motor center. No hub or motor spinning inertia.'
 (out/'mediciones_DIGITALES.json').write_text(json.dumps(d,indent=2))
 summaries.append(dict(target_mass_kg=m,old_CG_m=cg.tolist(),new_CG_m=newcg.tolist(),old_inertia_kgm2=I0.tolist(),new_inertia_kgm2=I.tolist(),blade_spin_J_kgm2=bladeJ,assumed_rpm=rpm,blade_H_per_rotor_Nms=H,missing=['hub inertia','motor rotating inertia','pitch actuator dynamics','measured mass distribution']))
with (ROOT/'masas_distribuidas'/'cargas_giro.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(ROOT/'masas_distribuidas'/'RESUMEN.json').write_text(json.dumps(summaries,indent=2))
print(json.dumps(summaries,indent=2));print(json.dumps([r for r in records if r['independent_rpm_mismatch_fraction']==.05 and r['additional_acceleration_g']==1],indent=2))
