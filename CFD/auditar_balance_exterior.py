"""Dense recorded-time momentum check for a live-run snapshot, not validation."""
from pathlib import Path
import argparse,json
import numpy as np
from analizar_series_transitorias import read_series,interval
p=argparse.ArgumentParser();p.add_argument('snapshot',type=Path);p.add_argument('--start',type=float,default=5e-6);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
pp=a.snapshot;rho=1.225;series={};parse={}
for name in ('force_all_boundary','force_all_solids','force_walls'):
 row,details=read_series(pp,name,'forces.dat',13)
 series[name]=(row[:,0],row[:,1:4]+row[:,4:7]);parse[name]=details
for name in ('volume_velocity','momentum_flux_inlet','momentum_flux_farfield'):
 row,details=read_series(pp,name,'volFieldValue.dat' if name=='volume_velocity' else 'surfaceFieldValue.dat',4)
 series[name]=(row[:,0],row[:,1:4]);parse[name]=details
for name in ('flow_inlet','flow_farfield'):
 row,details=read_series(pp,name,'surfaceFieldValue.dat',2)
 series[name]=(row[:,0],row[:,1:2]);parse[name]=details
end=min(t[-1] for t,_ in series.values());start=max(a.start,max(t[0] for t,_ in series.values()))
t0=series['volume_velocity'][0];t=t0[(t0>=start)&(t0<=end)]
if len(t)<4:raise ValueError('Too few common recorded timesteps after startup exclusion')
values={}
for name,(ti,y) in series.items():
 mask=(ti>=t[0])&(ti<=t[-1]);tt=ti[mask]
 np.testing.assert_allclose(tt,t,rtol=0,atol=1e-15)
 values[name]=y[mask]
u=values['volume_velocity'];flux=rho*(values['momentum_flux_inlet']+values['momentum_flux_farfield']);traction=values['force_all_boundary'];duration=t[-1]-t[0]
accumulation=rho*(u[-1]-u[0])/duration
def mean(y,mode):
 return np.sum(np.diff(t)[:,None]*(y[1:] if mode=='right_endpoint' else (y[:-1]+y[1:])/2),axis=0)/duration
reports={}
for mode in ('right_endpoint','trapezoidal'):
 conv=mean(flux,mode);boundary=mean(traction,mode);res=accumulation+conv+boundary
 scale=max(np.linalg.norm(accumulation),np.linalg.norm(conv),np.linalg.norm(boundary))
 reports[mode]=dict(accumulation_N=accumulation.tolist(),convective_outward_N=conv.tolist(),opposite_fluid_boundary_traction_N=boundary.tolist(),residual_N=res.tolist(),residual_norm_N=float(np.linalg.norm(res)),normalization_scale_N=float(scale),normalized_residual=float(np.linalg.norm(res)/scale))
balance=np.abs(values['flow_inlet']+values['flow_farfield'])/np.abs(values['flow_inlet'])
out=dict(snapshot=str(pp.resolve()),start_s=float(t[0]),end_s=float(t[-1]),recorded_timesteps=len(t),rho_kg_m3=rho,parsing=parse,
 results=reports,max_relative_volume_flux_imbalance=float(balance.max()),
 quadrature_mean_net_difference_N=(mean(flux+traction,'trapezoidal')-mean(flux+traction,'right_endpoint')).tolist(),
 physical_loads_accepted=False,exact_assembled_discrete_residual=False,
 limitations=['initial viscous transient and high local speed','not full installed vehicle or rotor','same-grid startup only; no mesh/domain refinement','RANS reconstructed traction versus solver operators','right-endpoint rule follows Euler timing but is not an assembled equation residual'])
a.output.write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(dict(start_s=out['start_s'],end_s=out['end_s'],records=len(t),residuals=reports,physical_loads_accepted=False),indent=2))
