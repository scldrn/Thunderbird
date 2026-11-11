"""Integral control-volume momentum check from sparse saved fields.

The residual includes snapshot quadrature and spatial/iterative inconsistencies;
it must not be presented as an exact assembled finite-volume residual.
"""
from pathlib import Path
import json
import numpy as np
from analizar_series_transitorias import read_series,interval
ROOT=Path(__file__).resolve().parent
case=ROOT/'auditoria_momento_Euler_0_0.0005'; pp=case/'postProcessing';rho=1.225
data={}
for name in ('all_boundary','solids','open_ends'):
 a,_=read_series(pp,'traction_'+name,'forces.dat',13)
 data[name]=(a[:,0],a[:,1:4]+a[:,4:7])
a,_=read_series(pp,'volume_velocity','volFieldValue.dat',4);t=a[:,0];u=a[:,1:4]
flux=[]
for name in ('inlet','outlet'):
 a,_=read_series(pp,'momentum_flux_'+name,'surfaceFieldValue.dat',4)
 np.testing.assert_allclose(a[:,0],t,rtol=0,atol=1e-12)
 flux.append(rho*a[:,1:4])
for times,_ in data.values():np.testing.assert_allclose(times,t,rtol=0,atol=1e-12)
np.testing.assert_allclose(data['all_boundary'][1],data['solids'][1]+data['open_ends'][1],rtol=0,atol=1e-5)
duration=t[-1]-t[0]
accumulation=rho*(u[-1]-u[0])/duration
convective=np.array(interval(t,flux[0]+flux[1],t[0],t[-1])['time_weighted_mean'])
traction=np.array(interval(t,data['all_boundary'][1],t[0],t[-1])['time_weighted_mean'])
residual=accumulation+convective+traction
endpoint_net=((flux[0]+flux[1]+data['all_boundary'][1])[[0,-1]]).mean(axis=0)
quadrature_change=convective+traction-endpoint_net
scale=max(np.linalg.norm(convective),np.linalg.norm(traction),np.linalg.norm(accumulation))
qi,_=read_series(pp,'flow_inlet','surfaceFieldValue.dat',2);qo,_=read_series(pp,'flow_outlet','surfaceFieldValue.dat',2)
mass_error=float(max(abs(qi[:,1]+qo[:,1])/abs(qi[:,1])))
out=dict(time_interval_s=[float(t[0]),float(t[-1])],snapshot_count=len(t),rho_kg_m3=rho,
 accumulation_mean_N=accumulation.tolist(),convective_outward_mean_N=convective.tolist(),
 opposite_fluid_boundary_traction_mean_N=traction.tolist(),integral_residual_mean_N=residual.tolist(),
 residual_norm_N=float(np.linalg.norm(residual)),normalization_scale_N=float(scale),
 normalized_residual=float(np.linalg.norm(residual)/scale),
 quadrature_three_vs_two_points_change_N=quadrature_change.tolist(),
 maximum_relative_volume_flux_imbalance=mass_error,
 physical_loads_accepted=False,exact_discrete_momentum_residual=False,
 interpretation='Sparse-time integral audit; nonzero closure error requires diagnosis, not force calibration.',
 limitations=['temporal quadrature not converged','reconstructed model tractions may differ from assembled discrete operators','PIMPLE iterations and pressure/velocity consistency not verified','domain excludes rotor and exterior','all snapshots remain within initial physical transient'])
(case/'MOMENTUM_AUDIT.json').write_text(json.dumps(out,indent=2,allow_nan=False))
print(json.dumps(out,indent=2))
