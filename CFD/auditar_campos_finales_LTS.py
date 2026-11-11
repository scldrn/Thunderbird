"""Final field/target audit for local-pseudotime pressure cases, not convergence."""
from pathlib import Path
import argparse,json,re,hashlib
import numpy as np
from foam_fields import read_internal
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--case',default='avance_A_compresible_600kmh_LTS_diag');a=p.parse_args();case=ROOT/a.case
m=json.loads((case/'compressible_assumptions.json').read_text());state=json.loads((case/'run_state.json').read_text());assert m['counter_kind']=='local_pseudo_iterations'
assert state['stage']=='diagnostic_exited' and state['exit_code']==0 and state['target_reached'] and not state['health_stop_requested']
log=(case/'log.foamRun').read_text();assert '\nEnd\n' in log
complete=[float(re.match(r'([\deE.+-]+)',chunk)[1]) for chunk in re.split(r'\nTime = ',log)[1:] if 'ClockTime =' in chunk]
assert complete[-1]>=m['target_steady_iterations']
folders=[]
for q in case.iterdir():
 try:
  if q.is_dir() and float(q.name)>0:folders.append(q)
 except ValueError:pass
latest=max(folders,key=lambda q:float(q.name));assert float(latest.name)>=m['target_steady_iterations']
mesh=json.loads((Path(m['source_mesh_case'])/'mesh_metadata.json').read_text());N=mesh['cells']
U=read_internal(latest/'U',N,3);P=read_internal(latest/'p',N);T=read_internal(latest/'T',N)
assert P.min()>0 and T.min()>0
Mach=np.linalg.norm(U,axis=1)/np.sqrt(m['gamma']*m['R_J_kgK']*T)
out=dict(case=case.name,counter_kind=m['counter_kind'],target_reached=True,last_pseudo_iteration=complete[-1],completed_iterations=len(complete),cells=N,finite_U_p_T=True,positive_p_T=True,
 min_p_Pa=float(P.min()),max_p_Pa=float(P.max()),min_T_K=float(T.min()),max_T_K=float(T.max()),max_internal_speed_m_s=float(np.linalg.norm(U,axis=1).max()),max_internal_Mach_declared_constants=float(Mach.max()),internal_cells_above_Mach_one=int((Mach>1).sum()),
 field_sha256={name:hashlib.sha256((latest/name).read_bytes()).hexdigest() for name in ('U','p','T')},
 numerical_steady_convergence_proven=False,physical_drag_accepted=False,scope='Finite positive final fields and requested pseudocounter completion only; residual, drift, field-change and sensitivity audits remain separate.')
if (latest/'rho').exists():
 rho=read_internal(latest/'rho',N);assert rho.min()>0
 ideal=P/(m['R_J_kgK']*T)
 out['max_density_EOS_relative_difference_declared_R']=float(np.max(abs(rho-ideal)/ideal))
 out['EOS_note']='Declared nominal R may differ slightly from library constants; not a closure/accuracy gate.'
(case/'FINAL_FIELDS_AUDIT.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2))
