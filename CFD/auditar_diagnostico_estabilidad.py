"""Audit completion and gross numerical behavior; never accept physical loads."""
from pathlib import Path
import json,re
import numpy as np
from analizar_series_transitorias import analyze

ROOT=Path(__file__).resolve().parent
case=ROOT/'diagnostico_Euler_upwind_X35_Y-35_h0.006'
state=json.loads((case/'run_state.json').read_text())
if state['stage'] not in ['solver_process_exited','diagnostic_audited']:raise RuntimeError('Diagnostic still running: audit after process exits.')
log=(case/'log.foamRun').read_text();names=re.findall(r'\nTime = ([\deE.+-]+)s',log)
dt=[float(x) for x in re.findall(r'deltaT = ([\deE.+-]+)',log)]
fields={}
for name in ['U','p','k','omega']:
    p=case/names[-1]/name
    if not p.exists():raise RuntimeError('Final field not recovered; do not infer field validity from process exit.')
    s=p.read_text();m=re.search(r'internalField\s+nonuniform\s+List<\w+>\s+(\d+)\s*\((.*?)\)\s*;',s,re.S)
    a=np.fromstring(re.sub(r'[()]',' ',m[2]),sep=' ')
    fields[name]=dict(all_finite=bool(np.isfinite(a).all()),min_component=float(a.min()),max_component=float(a.max()))
    if name=='U':fields[name]['max_magnitude_ms']=float(np.linalg.norm(a.reshape(-1,3),axis=1).max())
    if name=='p':fields[name]['units']='kinematic pressure, m^2/s^2, not Pa'
stats=analyze(case,case/'postProcessing')
(case/'force_statistics_audit.json').write_text(json.dumps(stats,indent=2,allow_nan=False))
rejection=json.loads((ROOT/'transitorio_X35_Y-35_h0.006/REJECTION_AUDIT.json').read_text())
report=dict(process_exit_code=state['exit_code'],target_reached=state['target_reached'],last_physical_time_s=float(names[-1]),all_internal_fields_finite=all(v['all_finite'] for v in fields.values()),fields_at_final_write=fields,dt_initial_s=dt[0],dt_final_s=dt[-1],initial_to_final_dt_ratio=dt[0]/dt[-1],dt_collapsed_by_factor_1000=dt[-1]<dt[0]/1000,exceeded_previous_run_failure_time=float(names[-1])>rejection['last_physical_time_s'],force_statistics_withheld=all(v['force_N']['statistics_withheld'] for v in stats['per_vane'].values()),max_abs_relative_flux_imbalance=stats['mass_balance']['max_abs_relative_imbalance_recorded'],physical_loads_accepted=False,scope='Short first-order stability diagnostic; cannot establish root cause, numerical accuracy, physical stationarity, installed performance or grid/time-step independence.')
(case/'STABILITY_AUDIT.json').write_text(json.dumps(report,indent=2,allow_nan=False))
state.update(stage='diagnostic_audited',results_audited=True,physical_loads_accepted=False,force_statistics_withheld=report['force_statistics_withheld'])
(case/'run_state.json').write_text(json.dumps(state,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['fields_at_final_write','scope']}))
