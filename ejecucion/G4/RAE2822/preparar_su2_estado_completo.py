"""Force extra iterations to check all stored fields after density-only stop."""
from pathlib import Path
import hashlib
import json
import re
import shutil

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'su2_r2_adaptativo'
CASE=HERE/'su2_r3_estado_completo'


def main():
    assert not CASE.exists(), 'Preserve previous full-state probe'
    terminal=json.loads((SOURCE/'EJECUCION.json').read_text())
    audit_path=SOURCE/'AUDITORIA_SU2.json';audit=json.loads(audit_path.read_text())
    assert terminal['exit_code']==0 and audit['source_solver_convergence_message']
    assert audit['convergence_message_does_not_cover_all_equations']
    assert audit['rho_range_kg_m3'][0]>0 and audit['pressure_range_Pa'][0]>0
    CASE.mkdir()
    for name in ('mesh_RAE2822_turb.su2','ORIGINAL_turb_SST_RAE2822.cfg'):
        shutil.copy2(SOURCE/name,CASE/name)
    shutil.copy2(SOURCE/'restart_flow.csv',CASE/'solution_flow.csv')
    text=(SOURCE/'case.cfg').read_text()
    for pattern,replacement in [(r'^ITER\s*=\s*2000\s*$','ITER= 200'),
                                (r'^CONV_STARTITER\s*=\s*10\s*$','CONV_STARTITER= 201'),
                                (r'^OUTPUT_WRT_FREQ\s*=\s*500\s*$','OUTPUT_WRT_FREQ= 200')]:
        text,n=re.subn(pattern,replacement,text,flags=re.M);assert n==1
    (CASE/'case.cfg').write_text(text)
    inputs=json.loads((SOURCE/'ENTRADAS.json').read_text())
    inputs.update(scope='Forced200-additional-iteration full-state convergence probe, not physical validation',
        iteration_limit=200,parent=SOURCE.name,
        source_total_steps_observed=600+audit['last_inner_iteration_index']+1,
        convergence_monitor_delayed_until=201,
        purpose='Density-only convergence did not cover turbulence; compare all final fields and force drift without automatic early stop.',
        changes_from_parent=['200forced additional iterations','convergence start201 beyond limit200','terminal output interval200'],
        physical_models_geometry_freestream_and_numerical_schemes_unchanged=True,
        source_audit_sha256=hashlib.sha256(audit_path.read_bytes()).hexdigest(),
        inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CASE.iterdir() if p.is_file()})
    (CASE/'ENTRADAS.json').write_text(json.dumps(inputs,indent=2)+'\n')
    print(json.dumps(dict(case=str(CASE),purpose=inputs['purpose'],additional_iterations=200),indent=2))


if __name__=='__main__':
    main()
