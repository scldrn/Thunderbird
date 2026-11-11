import numpy as np,json
from simular import *
y0=np.r_[0.,0.,10.,0.,0.,0.,0.,0.,0.,1.,0.,0.,0.];A=np.zeros((6,12));A[:3,:3]=np.eye(3);I=np.array([.1,.2,.3]);F=np.zeros((4,3));out={}
for case in ('caida_libre','estacionario','par_constante'):
 y=y0.copy();F[:]=0;ext=np.zeros(3);et=np.zeros(3)
 if case!='caida_libre':F[0,2]=5*G
 if case=='par_constante':et[2]=.03
 for k in range(1000):y=rk4_step(y,.001,F,A,I,5,ext,et)
 if case=='caida_libre':err=max(abs(y[2]-(10-G/2)),abs(y[5]+G))
 elif case=='estacionario':err=np.max(abs(y-y0))
 else:err=max(abs(y[12]-.1),abs(R.from_quat(y[6:10]).as_rotvec()[2]-.05))
 out[case+'_max_error']=float(err);assert err<1e-9
h,summary=run(5,dt=.0025,save=False);baseline=np.load(P/'5kg_nominal.npz')['history'];fine=h[::2]
out['half_step_max_position_difference_m']=float(np.linalg.norm(fine[:,1:4]-baseline[:,1:4],axis=1).max())
out['half_step_max_attitude_difference_deg']=float(np.rad2deg((R.from_quat(fine[:,7:11]).inv()*R.from_quat(baseline[:,7:11])).magnitude()).max())
assert out['half_step_max_position_difference_m']<.02
out['scope']='Numerical checks only, not physical validation or full NASA check-case suite.'
(P/'VERIFICACION.json').write_text(json.dumps(out,indent=2));print(out)
