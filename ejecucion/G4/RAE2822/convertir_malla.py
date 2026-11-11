"""Convert NASA-derived mesh, audit topology and keep a separate idle container."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
CASE = HERE/'piloto_r1'
CONTAINER = 'codex-aero-rae2822-r1'
DOCKER = '/Users/sam/.docker/bin/docker'


def run(*args, **kwargs):
    return subprocess.run([DOCKER, *args], check=True, text=True, **kwargs)


def main():
    global CASE, CONTAINER
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, default=CASE)
    parser.add_argument('--container', default=CONTAINER)
    args = parser.parse_args()
    CASE, CONTAINER = args.case.resolve(), args.container
    if (CASE/'CONTENEDOR.json').exists():
        raise FileExistsError('Inspect existing conversion/container rather than duplicate it')
    metadata = json.loads((CASE/'MALLA.json').read_text())
    assert hashlib.sha256((CASE/'fluid.msh').read_bytes()).hexdigest() == metadata['mesh_sha256']
    exists = subprocess.run([DOCKER, 'inspect', CONTAINER], capture_output=True, text=True)
    assert exists.returncode != 0
    identifier = run('create', '--name', CONTAINER, '--init', '--cpus', '2', '--memory', '2g',
                     '--network', 'none', 'codex-aero-openfoam:13', 'sleep', 'infinity', capture_output=True).stdout.strip()
    state = dict(container=CONTAINER, container_id=identifier, stage='mesh_conversion_running',
                 own_solver_started=False, historical_paused_solvers_resumed=False)
    (CASE/'CONTENEDOR.json').write_text(json.dumps(state, indent=2)+'\n')
    run('cp', str(CASE), CONTAINER+':/case')
    run('start', CONTAINER, capture_output=True)
    run('exec', '--workdir', '/case', CONTAINER, '/bin/bash', '-c',
         'source /opt/openfoam13/etc/bashrc && gmshToFoam fluid.msh > log.gmshToFoam 2>&1')
    run('cp', CONTAINER+':/case/log.gmshToFoam', str(CASE/'log.gmshToFoam'))
    run('cp', CONTAINER+':/case/constant/polyMesh', str(CASE/'constant/polyMesh'))
    boundary = CASE/'constant/polyMesh/boundary'
    original = boundary.read_text()
    (CASE/'boundary_original.txt').write_text(original)
    text, n = re.subn(r'(\bairfoil\s*\{\s*type\s+)patch;', r'\1wall;', original)
    assert n == 1
    text, n = re.subn(r'(\bfrontAndBack\s*\{\s*type\s+)patch;', r'\1empty;', text)
    assert n == 1
    boundary.write_text(text)
    for name, expected in metadata['boundary_faces'].items():
        block = re.search(r'\b'+name+r'\s*\{(.*?)\}', text, re.S)[1]
        assert int(re.search(r'nFaces\s+(\d+)', block)[1]) == expected
    if 'defaultFaces' in text:
        block = re.search(r'\bdefaultFaces\s*\{(.*?)\}', text, re.S)[1]
        assert int(re.search(r'nFaces\s+(\d+)', block)[1]) == 0
    owner = (CASE/'constant/polyMesh/owner').read_text()[:2000]
    cells = metadata.get('cells', metadata.get('hexahedra'))
    assert int(re.search(r'nCells:\s*(\d+)', owner)[1]) == cells
    assert int(re.search(r'nInternalFaces:\s*(\d+)', owner)[1]) == metadata['expected_internal_faces']
    assert int(re.search(r'nFaces:\s*(\d+)', owner)[1]) == metadata['expected_total_faces']
    run('cp', str(boundary), CONTAINER+':/case/constant/polyMesh/boundary')
    result = subprocess.run([DOCKER, 'exec', '--workdir', '/case', CONTAINER, '/bin/bash', '-c',
        'source /opt/openfoam13/etc/bashrc && checkMesh -allGeometry -allTopology > log.checkMesh 2>&1'], text=True)
    run('cp', CONTAINER+':/case/log.checkMesh', str(CASE/'log.checkMesh'))
    log = (CASE/'log.checkMesh').read_text()
    accepted = result.returncode == 0 and 'Mesh OK.' in log and 'Failed ' not in log
    report = dict(source_mesh_sha256=metadata['mesh_sha256'], cells=cells,
                  conformal_wake_verified_by_internal_face_count=True,
                  boundary_counts_verified=True, checkMesh_exit_code=result.returncode,
                  checkMesh_OK=accepted, physical_validation_accepted=False,
                  polyMesh_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in (CASE/'constant/polyMesh').iterdir() if p.is_file()})
    (CASE/'MALLA_OPENFOAM.json').write_text(json.dumps(report, indent=2)+'\n')
    state['stage'] = 'mesh_checked_no_solver' if accepted else 'mesh_rejected_no_solver'
    if not accepted:
        run('stop', CONTAINER, capture_output=True)
    (CASE/'CONTENEDOR.json').write_text(json.dumps(state, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    assert accepted, 'Inspect mesh quality before running flow'


if __name__ == '__main__':
    main()
