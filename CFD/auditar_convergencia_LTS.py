"""First-outer residuals, block drift and body-normalized mass balance for LTS.

Iteration means diagnose numerical drift, never physical time statistics.
"""
from pathlib import Path
import argparse,json,re
import numpy as np
from analizar_series_transitorias import read_series
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--case',default='avance_A_compresible_600kmh_LTS_diag');p.add_argument('--post-processing',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
case=ROOT/a.case;pp=a.post_processing or case/'postProcessing';meta=json.loads((case/'compressible_assumptions.json').read_text());criteria=json.loads((ROOT/'CRITERIOS-CONVERGENCIA-LTS.json').read_text())
assert meta.get('counter_kind')=='local_pseudo_iterations'
log=(case/'log.foamRun').read_text();residuals={}
for chunk in re.split(r'\nTime = ',log)[1:]:
 t=re.match(r'([\deE.+-]+)',chunk)
 if not t or 'ClockTime =' not in chunk:continue
 first={};last={}
 for name,initial,final in re.findall(r'Solving for (\w+), Initial residual = ([\deE.+-]+), Final residual = ([\deE.+-]+)',chunk):
  first.setdefault(name,float(initial));last[name]=float(final)
 residuals[float(t[1])]=dict(first_outer_initial=first,last_linear_final=last)
f,parsing=read_series(pp,'force_hull','forces.dat',13)
flux=[];parsers={'force_hull':parsing}
for name in ('inlet','outlet','farfield'):
 x,pa=read_series(pp,'mass_flux_'+name,'surfaceFieldValue.dat',2);flux.append(x);parsers[name]=pa
start=max(1.,f[0,0],*(x[0,0] for x in flux));end=min(f[-1,0],*(x[-1,0] for x in flux),max(residuals))
t=f[(f[:,0]>=start)&(f[:,0]<=end),0]
assert len(t)>=2 and np.all(abs(t-np.round(t))<1e-9) and np.all(np.diff(t)==1)
mask=(f[:,0]>=t[0])&(f[:,0]<=t[-1]);f=f[mask]
mass=[]
for x in flux:
 selected=x[(x[:,0]>=t[0])&(x[:,0]<=t[-1])]
 np.testing.assert_allclose(selected[:,0],t,rtol=0,atol=1e-12);mass.append(selected[:,1])
rho=meta['rho_kg_m3'];speed=meta['velocity_m_s'];area=meta['reference_area_m2'];q=.5*rho*speed**2
mesh=json.loads((Path(meta['source_mesh_case'])/'mesh_metadata.json').read_text());L=mesh['body_length_m']
cpforce=f[:,1:4]/(q*area);cpmoment=f[:,7:10]/(q*area*L)
n=criteria['tail_iterations'];blocks=[]
for i in range(len(t)//n):
 ix=slice(i*n,(i+1)*n)
 blocks.append(dict(first_iteration=float(t[ix][0]),last_iteration=float(t[ix][-1]),pressure_force_Cmean=cpforce[ix].mean(0).tolist(),pressure_moment_Cmean=cpmoment[ix].mean(0).tolist()))
force_delta=moment_delta=None
if len(blocks)>=2:
 force_delta=float(np.max(abs(np.array(blocks[-1]['pressure_force_Cmean'])-blocks[-2]['pressure_force_Cmean'])))
 moment_delta=float(np.max(abs(np.array(blocks[-1]['pressure_moment_Cmean'])-blocks[-2]['pressure_moment_Cmean'])))
# Use the last complete block for all screens, excluding the unfinished block.
last_index=(len(t)//n)*n;last=t[max(0,last_index-n):last_index]
has_tail=len(last)==n
first_max={}
for field in criteria['first_outer_initial_residual_max']:
 vals=[residuals[float(ti)]['first_outer_initial'].get(field) for ti in last]
 first_max[field]=max(vals) if vals and all(v is not None for v in vals) else None
net=np.sum(mass,axis=0);body_scale=rho*speed*area
mass_body=float(max(abs(net[max(0,last_index-n):last_index]))/body_scale) if has_tail else None
domain_scale=np.maximum(abs(mass[0]),1e-30)
force_p2p=float(np.ptp(cpforce[max(0,last_index-n):last_index],axis=0).max()) if has_tail else None
moment_p2p=float(np.ptp(cpmoment[max(0,last_index-n):last_index],axis=0).max()) if has_tail else None
screens=dict(enough_complete_blocks=len(blocks)>=criteria['required_complete_blocks'],
 first_outer_initial_residuals=has_tail and all(first_max[k] is not None and first_max[k]<=v for k,v in criteria['first_outer_initial_residual_max'].items()),
 force_mean_drift=force_delta is not None and force_delta<=criteria['force_coefficient_adjacent_block_mean_change_max'],
 moment_mean_drift=moment_delta is not None and moment_delta<=criteria['moment_coefficient_adjacent_block_mean_change_max'],
 force_last_block_range=force_p2p is not None and force_p2p<=criteria['force_coefficient_last_block_peak_to_peak_max'],
 moment_last_block_range=moment_p2p is not None and moment_p2p<=criteria['moment_coefficient_last_block_peak_to_peak_max'],
 mass_body_scale=mass_body is not None and mass_body<=criteria['mass_imbalance_relative_to_rho_U_body_area_max'])
out=dict(case=case.name,source_post_processing=str(pp.resolve()),counter_kind='local_pseudo_iterations',common_iterations=[float(t[0]),float(t[-1])],iteration_count=len(t),parsing=parsers,
 complete_blocks=blocks,screen_tail_iterations=last.tolist(),last_block_first_outer_initial_residual_max=first_max,
 last_two_complete_block_force_Cmean_change_max=force_delta,last_two_complete_block_moment_Cmean_change_max=moment_delta,
 last_complete_block_force_Cpeak_to_peak_max=force_p2p,last_complete_block_moment_Cpeak_to_peak_max=moment_p2p,
 max_mass_imbalance_relative_domain_inlet=float(max(abs(net)/domain_scale)),last_complete_block_mass_imbalance_relative_body=mass_body,
 body_mass_flow_reference_kg_s=body_scale,criteria=criteria,screens=screens,all_chosen_screens_passed=all(screens.values()),
 steady_convergence_proven=False,physical_drag_accepted=False,physical_time_statistics=False,
 note='First-outer initial residuals are screened; tiny final linear residuals alone do not prove convergence. LTS counters are algorithmic. Field changes and sensitivities remain required.')
output=a.output or case/'CONVERGENCE_AUDIT.json';output.write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps({k:out[k] for k in ('common_iterations','last_block_first_outer_initial_residual_max','last_two_complete_block_force_Cmean_change_max','last_two_complete_block_moment_Cmean_change_max','last_complete_block_mass_imbalance_relative_body','screens','all_chosen_screens_passed','physical_drag_accepted')},indent=2))
