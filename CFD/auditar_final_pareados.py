"""Terminal numerical audit of paired startup tests, not physical acceptance."""
from pathlib import Path
import json,hashlib,math,re
from analizar_series_transitorias import NUM
ROOT=Path(__file__).resolve().parent
cases=[ROOT/n for n in ('comparacion_Euler_reinicio_h0.006','comparacion_backward_reinicio_h0.006')]
out=dict(cases=[],initial_inputs_match=False,physical_loads_accepted=False,temporal_convergence_proven=False)
for case in cases:
 state=json.loads((case/'run_state.json').read_text());meta=json.loads((case/'transient_assumptions.json').read_text())
 assert state['stage']=='solver_process_exited' and state['exit_code']==0 and state['target_reached']
 assert abs(state['last_physical_time_s']-.0015)<1e-12
 assert not (case/'WATCHDOG_STOP.json').exists()
 checked=[]
 for name in ('U','p','k','omega','nut','phi'):
  path=case/'0.0015'/name;s=path.read_text()
  assert not re.search(r'\b(?:nan|inf)\b',s,re.I),(path,'nonfinite literal')
  assert all(math.isfinite(float(x)) for x in NUM.findall(s)),(path,'overflow')
  checked.append(dict(field=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 for name,digest in meta['initial_field_hashes'].items():assert hashlib.sha256((case/'0'/name).read_bytes()).hexdigest()==digest
 stats=json.loads((case/'force_statistics_audit.json').read_text())
 assert all(v['force_N']['statistics_withheld'] for v in stats['per_vane'].values())
 log=(case/'log.foamRun').read_text()
 assert '\nEnd\n' in log
 out['cases'].append(dict(case=case.name,requested_time_reached=True,finite_final_fields=checked,loads_withheld_initial_discard_not_reached=True))
for relative in ['system/fvSolution','constant/momentumTransport','constant/physicalProperties']+[f'0/{n}' for n in ('U','p','k','omega','nut','phi')]:
 assert (cases[0]/relative).read_bytes()==(cases[1]/relative).read_bytes(),relative
s0=(cases[0]/'system/fvSchemes').read_text();s1=(cases[1]/'system/fvSchemes').read_text()
assert s0.replace('default Euler','default backward')==s1
out['initial_inputs_match']=True
out['interpretation']='Both requested short numerical windows completed; same-grid scheme sensitivity only. Not temporal refinement, stationary loading or installed calibration.'
(ROOT/'AUDITORIA_PAREADA_FINAL.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(cases=len(cases),finite_final_fields_verified=True,initial_inputs_match=True,physical_loads_accepted=False)))
