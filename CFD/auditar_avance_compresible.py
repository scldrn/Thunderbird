"""Audit a completed short compressible startup; no stationary-drag acceptance."""
from pathlib import Path
import argparse,json,re,math,hashlib
import numpy as np
from analizar_series_transitorias import read_series
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--case',default='avance_A_compresible_600kmh_Euler_diag_v3');a=p.parse_args();case=ROOT/a.case
meta=json.loads((case/'compressible_assumptions.json').read_text());state=json.loads((case/'run_state.json').read_text())
assert meta['time_counter_is_physical_seconds']
assert state['stage']=='diagnostic_exited' and state['exit_code']==0 and state['target_reached']
assert not state['health_stop_requested']
log=(case/'log.foamRun').read_text();assert '\nEnd\n' in log
blocks=re.split(r'\nTime = ',log)[1:]
complete=[float(re.match(r'([\deE.+-]+)',s)[1]) for s in blocks if 'ClockTime =' in s]
assert complete and complete[-1]>=meta['target_physical_time_s']*(1-1e-8)
folders=[]
for q in case.iterdir():
 try:
  if q.is_dir() and float(q.name)>0:folders.append(q)
 except ValueError:pass
latest=max(folders,key=lambda q:float(q.name));assert float(latest.name)>=meta['target_physical_time_s']*(1-1e-8)
mesh_meta=json.loads((Path(meta['source_mesh_case'])/'mesh_metadata.json').read_text())
expected_cells=mesh_meta['cells']
def field(name,vector=False):
 s=(latest/name).read_text();match=re.search(r'internalField\s+nonuniform\s+List<(?:scalar|vector)>\s+(\d+)\s*\(\s*\n',s)
 if match:
  end=s.index('\n)',match.end());values=np.fromstring(s[match.end():end].replace('(',' ').replace(')',' '),sep=' ')
  values=values.reshape(-1,3) if vector else values
  assert len(values)==int(match[1])==expected_cells
 else:
  match=re.search(r'internalField\s+uniform\s+([^;]+);',s);assert match
  x=np.fromstring(match[1].replace('(',' ').replace(')',' '),sep=' ')
  assert len(x)==(3 if vector else 1)
  values=np.tile(x,(expected_cells,1)) if vector else np.full(expected_cells,x[0])
 assert np.isfinite(values).all(),name
 return values
U=field('U',True);T=field('T');P=field('p');assert T.min()>0 and P.min()>0
speed=np.linalg.norm(U,axis=1);Mach=speed/np.sqrt(meta['gamma']*meta['R_J_kgK']*T)
forces,_=read_series(case/'postProcessing','force_hull','forces.dat',13)
assert abs(forces[-1,0]-complete[-1])<1e-10
pressure_force=forces[-1,1:4];viscous_force=forces[-1,4:7]
q=.5*meta['rho_kg_m3']*meta['velocity_m_s']**2;area=meta['reference_area_m2']
out=dict(case=case.name,target_time_reached=True,completed_timesteps=len(complete),final_physical_time_s=complete[-1],
 cells_checked=expected_cells,all_U_p_T_finite=True,all_p_T_positive=True,min_T_K=float(T.min()),max_T_K=float(T.max()),min_p_Pa=float(P.min()),max_p_Pa=float(P.max()),
 maximum_internal_speed_m_s=float(speed.max()),maximum_internal_Mach_with_declared_constants=float(Mach.max()),cells_internal_Mach_above_one=int((Mach>1).sum()),
 instantaneous_final_pressure_force_N=pressure_force.tolist(),instantaneous_final_viscous_force_N=viscous_force.tolist(),
 instantaneous_pressure_force_coefficients=(pressure_force/(q*area)).tolist(),reference_dynamic_pressure_Pa=q,reference_area_m2=area,
 body_flow_through_times=complete[-1]/(mesh_meta['body_length_m']/meta['velocity_m_s']),
 stationary_drag_accepted=False,critical_Mach_determined=False,drag_divergence_determined=False,physical_loads_accepted=False,
 field_sha256={name:hashlib.sha256((latest/name).read_bytes()).hexdigest() for name in ('U','p','T')},
 limitations=['Short startup only, not developed flight','Slip wall without turbulent skin-friction model','No scheme, mesh or domain independence','No installed ports, doors, propulsion or trim','Internal cell Mach does not resolve all surface extrema','Declared constant gas parameters used for derived Mach; no isentropic inference from pressure'])
(case/'FINAL_STARTUP_AUDIT.json').write_text(json.dumps(out,indent=2,allow_nan=False))
state.update(results_audited=True,audit_scope='Startup target, finite positive fields and derived instantaneous values only',physical_loads_accepted=False)
(case/'run_state.json').write_text(json.dumps(state,indent=2));print(json.dumps(out,indent=2))
