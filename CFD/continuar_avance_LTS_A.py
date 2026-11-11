"""Continue a completed, finite LTS case without overwriting its evidence."""
from pathlib import Path
import argparse,json,shutil,re,hashlib
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source',default='avance_A_compresible_600kmh_LTS_diag');p.add_argument('--case',default='avance_A_compresible_600kmh_LTS_cont_1000');p.add_argument('--iterations',type=int,default=1000);a=p.parse_args()
src=ROOT/a.source;dst=ROOT/a.case
if dst.exists():raise FileExistsError(dst)
state=json.loads((src/'run_state.json').read_text());audit=json.loads((src/'FINAL_FIELDS_AUDIT.json').read_text());convergence=json.loads((src/'CONVERGENCE_AUDIT.json').read_text())
assert state['stage']=='diagnostic_exited' and state['exit_code']==0 and state['target_reached']
assert audit['finite_U_p_T'] and audit['positive_p_T'] and a.iterations>0
counter=audit['last_pseudo_iteration'];field=src/f'{counter:g}';assert field.is_dir()
dst.mkdir()
for name in ('constant','system'):shutil.copytree(src/name,dst/name)
shutil.copytree(field,dst/'0')
q=dst/'0/uniform/time'
if q.exists():q.unlink()
q=dst/'system/controlDict';s=q.read_text();s=re.sub(r'endTime\s+[^;]+;',f'endTime {a.iterations};',s)
s=s.replace('writeControl timeStep; writeInterval 25;','writeControl timeStep; writeInterval 100;');q.write_text(s)
m=json.loads((src/'compressible_assumptions.json').read_text());m.update(target_steady_iterations=a.iterations,
 source_pseudotime_restart_case=str(src.resolve()),source_fields_counter=counter,
 cumulative_prior_pseudo_iterations=m.get('cumulative_prior_pseudo_iterations',0)+counter,
 restart_reason='Requested initial 200 iterations completed with finite fields, but residual/load/mass screens failed; continue pressure convergence, not accept coefficients.',
 inherited_numerical_screens_passed=convergence['all_chosen_screens_passed'],
 restart_scope='Same geometry, boundaries and LTS controls. Counter resets and first damping/history steps differ from an uninterrupted run; no physical-time interpretation.')
m['input_sha256']={str(q.relative_to(dst)):hashlib.sha256(q.read_bytes()).hexdigest() for folder in ('0','system','constant') for q in (dst/folder).iterdir() if q.is_file()}
(dst/'compressible_assumptions.json').write_text(json.dumps(m,indent=2));print(dst)
