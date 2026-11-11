"""Reproduce evidence for rejecting the v2 transient; not a physical load model."""
from pathlib import Path
import json,re
import numpy as np
from analizar_series_transitorias import read_series

ROOT=Path(__file__).resolve().parent
case=ROOT/'transitorio_X35_Y-35_h0.006'
log=(case/'log.foamRun').read_text()
times=re.findall(r'\nTime = ([\deE.+-]+)s',log)
dt=[float(x) for x in re.findall(r'deltaT = ([\deE.+-]+)',log)]
meta=json.loads((case/'transient_assumptions.json').read_text())
field_summary={}
for name in ['U','p','k','omega']:
    s=(case/times[-1]/name).read_text()
    m=re.search(r'internalField\s+nonuniform\s+List<\w+>\s+(\d+)\s*\((.*?)\)\s*;',s,re.S)
    a=np.fromstring(re.sub(r'[()]',' ',m[2]),sep=' ')
    field_summary[name]=dict(min_component=float(a.min()),max_component=float(a.max()))
    if name=='U':field_summary[name]['max_magnitude_ms']=float(np.linalg.norm(a.reshape(-1,3),axis=1).max())
    if name=='p':field_summary[name]['units']='kinematic pressure, m^2/s^2, not Pa'
a,parsing=read_series(case/'postProcessing','force_vaneX0','forces.dat',13)
f=a[:,1:4]+a[:,4:7]
audit=dict(physical_loads_accepted=False,classification='Rejected numerical run',termination='Requested orderly stopAt writeNow after observed timestep collapse and force blow-up; process returned 0.',last_physical_time_s=float(times[-1]),requested_end_time_s=meta['end_time_s'],target_reached=False,completed_time_fraction=float(times[-1])/meta['end_time_s'],initial_dt_s=dt[0],final_dt_s=dt[-1],dt_collapse_factor=dt[0]/dt[-1],fields_at_final_write=field_summary,vaneX0_force_norm_first_N=float(np.linalg.norm(f[0])),vaneX0_force_norm_final_N=float(np.linalg.norm(f[-1])),force_parsing=parsing,root_cause='Not isolated. Subsequent first-order/upwind/more-corrector diagnostic changes multiple controls and cannot attribute causation to one setting.',acceptance_note='Small continuity errors and exit code zero do not validate this run. No means, effectiveness, servo loads or thrust maps accepted.')
(case/'REJECTION_AUDIT.json').write_text(json.dumps(audit,indent=2))
state=json.loads((case/'run_state.json').read_text())
state.update(stage='rejected_after_audit',results_audited=True,physical_loads_accepted=False,target_reached=False,last_physical_time_s=float(times[-1]),reason='Numerical runaway; deliberately stopped before target physical time.')
(case/'run_state.json').write_text(json.dumps(state,indent=2))
print(json.dumps({k:audit[k] for k in ['last_physical_time_s','dt_collapse_factor','vaneX0_force_norm_final_N','physical_loads_accepted']}))
