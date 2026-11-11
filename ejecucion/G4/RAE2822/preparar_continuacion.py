"""Identified continuation from terminal startup, not an automatic retry."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE/'piloto_r4_hibrido_resuelto'
CASE = HERE/'piloto_r5_continuacion_Co1'
CONTAINER = 'codex-aero-rae2822-r5'
DOCKER = '/Users/sam/.docker/bin/docker'


def main():
    assert not CASE.exists(), 'Preserve existing continuation'
    terminal = json.loads((SOURCE/'EJECUCION.json').read_text())
    audit = json.loads((SOURCE/'AUDITORIA_PILOTO.json').read_text())
    assert terminal['exit_code'] == 0 and terminal['target_reached']
    assert not audit['diagnostic_screens_all_pass']
    assert audit['final_fields']['T']['min'] > 0 and audit['final_fields']['p']['min'] > 0
    CASE.mkdir()
    for name in ('constant', 'system', '0', '100'):
        shutil.copytree(SOURCE/name, CASE/name)
    for name in ('MALLA.json','MALLA_OPENFOAM.json','Cp_experimental.csv'):
        shutil.copy2(SOURCE/name, CASE/name)
    (CASE/'benchmark.foam').touch()
    control = CASE/'system/controlDict'
    text = control.read_text()
    text, n1 = re.subn(r'\bstartTime 0;', 'startTime 100;', text)
    text, n2 = re.subn(r'\bendTime 100;', 'endTime 600;', text)
    assert n1 == n2 == 1
    control.write_text(text)
    solution = CASE/'system/fvSolution'
    text, count = re.subn(r'\bmaxCo 0\.2;', 'maxCo 1;', solution.read_text())
    assert count == 1
    solution.write_text(text)
    inputs = json.loads((SOURCE/'ENTRADAS.json').read_text())
    inputs.update(scope='Identified500-additional-iteration compressible startup continuation; not accepted validation',
        iteration_start=100, iteration_target=600, maxCo=1,
        source_terminal_case=SOURCE.name,
        continuation_reason='100-step fields finite/positive but residuals, coefficient drift and Cp not accepted; extend solution and increase local Courant limit from0.2 to1. Keep mesh/models/upwind unchanged.',
        physical_validation_accepted=False,
        input_sha256={str(p.relative_to(CASE)):hashlib.sha256(p.read_bytes()).hexdigest()
                      for folder in ('0','100','constant','system') for p in (CASE/folder).rglob('*') if p.is_file()})
    (CASE/'ENTRADAS.json').write_text(json.dumps(inputs,indent=2)+'\n')
    provenance = dict(source_case=SOURCE.name,
        source_audit_sha256=hashlib.sha256((SOURCE/'AUDITORIA_PILOTO.json').read_bytes()).hexdigest(),
        source_initial_fields_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE/'100').iterdir() if p.is_file()},
        changes=['start100/end600','maxCo0.2_to1'],
        original_case_unchanged=True, historical_solvers_resumed=False)
    (CASE/'DERIVACION.json').write_text(json.dumps(provenance,indent=2)+'\n')
    def run(*args):
        return subprocess.run([DOCKER,*args],check=True,capture_output=True,text=True)
    assert subprocess.run([DOCKER,'inspect',CONTAINER],capture_output=True).returncode != 0
    identifier = run('create','--name',CONTAINER,'--init','--cpus','2','--memory','2g','--network','none',
                     'codex-aero-openfoam:13','sleep','infinity').stdout.strip()
    (CASE/'CONTENEDOR.json').write_text(json.dumps(dict(container=CONTAINER,container_id=identifier,
        stage='derived_same_checked_mesh_no_solver',own_solver_started=False),indent=2)+'\n')
    run('cp',str(CASE),CONTAINER+':/case')
    run('start',CONTAINER)
    print(json.dumps(dict(case=str(CASE),container=CONTAINER,iteration_start=100,iteration_target=600),indent=2))


if __name__ == '__main__':
    main()
