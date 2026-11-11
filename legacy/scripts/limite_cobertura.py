import csv,json,numpy as np
from control import allocation,facets
from calcular import geometry,G
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'resultados'
rows=[r for r in csv.DictReader((p/'mapa_rotor_bidireccional_CONDICIONAL.csv').open()) if r['rpm']=='6000' and r['solved']=='True' and float(r['outside_torque_fraction'])<=.05]
a=min(float(r['target_N']) for r in rows);b=max(float(r['target_N']) for r in rows)
g=geometry(.025,4,'esferoide');L,D=g['L_m'],g['D_m'];ang=json.loads((p/'configuracion_control_HIPOTESIS.json').read_text())['record'];B,pos,n=allocation(L,D,2,ang['theta_rad'],ang['phi_rad']);pos[:,0]*=1.25;B[3:]=np.cross(pos-np.array([.05,0,0]),n).T/L
ns,_=facets(B);ns=np.vstack([ns,-ns]);pr=np.einsum('ij,jk->ik',ns,B);support=(b-a)/2*abs(pr).sum(axis=1)+(b+a)/2*pr.sum(axis=1)
nf=np.linalg.norm(ns[:,:3],axis=1);nt=np.linalg.norm(ns[:,3:],axis=1);force=min((support-nt/L)[nf>1e-9]/nf[nf>1e-9])
d=dict(arbitrary_coverage_threshold=.05,thrust_interval_N=[a,b],forceball_N=force,additional_accel_g=force/(5*G)-1,warning='Coverage screen only; excludes reaction torque and NOT evidence of physical maximum')
hfull=(40+37)/2*abs(pr).sum(axis=1)+(40-37)/2*pr.sum(axis=1)
fullforce=min((hfull-nt/L)[nf>1e-9]/nf[nf>1e-9])
d['full_clamped_map_forceball_N']=float(fullforce)
d['full_clamped_map_additional_accel_g']=float(fullforce/(5*G)-1)
(p/'limite_cobertura.json').write_text(json.dumps(d,indent=2));print(d)
