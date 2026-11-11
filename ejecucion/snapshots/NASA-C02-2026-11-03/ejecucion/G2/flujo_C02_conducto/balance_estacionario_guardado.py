"""Reconstruct CV momentum on saved fields, without solving or time claims."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'CFD'))
from analizar_series_transitorias import read_series

SOURCE = HERE/'neutro_r5_viscoso_exploratorio'
CASE = HERE/'balance_r5_80_100_r2_precision12'
DOCKER = '/Users/sam/.docker/bin/docker'
CONTAINER = 'codex-aero-c02-balance-r5-v2'


def run(*args, **kwargs):
    return subprocess.run([DOCKER, *args], check=True, text=True, **kwargs)


def main():
    global SOURCE, CASE, CONTAINER
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--case', type=Path, default=CASE)
    parser.add_argument('--container', default=CONTAINER)
    parser.add_argument('--times', nargs=2, type=int, default=[80,100])
    parser.add_argument('--saved-snapshot', action='store_true',
                        help='Require a separately recorded immutable saved-field snapshot, without claiming solver termination')
    args = parser.parse_args()
    SOURCE, CASE, CONTAINER = args.source.resolve(), args.case.resolve(), args.container
    assert 0 <= args.times[0] < args.times[1]
    times = tuple(map(str,args.times))
    if CASE.exists():
        raise FileExistsError('Preserve existing audit and inspect process before rerunning')
    snapshot = None
    if args.saved_snapshot:
        snapshot = json.loads((SOURCE/'INSTANTANEA_GUARDADA.json').read_text())
        assert snapshot['stage'] == 'saved_fields_snapshot'
        assert snapshot['saved_counters'] == list(args.times)
        assert snapshot['source_completed_counter_observed'] > args.times[-1]
        for name, digest in snapshot['saved_fields_sha256'].items():
            assert hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() == digest
    else:
        terminal = json.loads((SOURCE/'EJECUCION.json').read_text())
        assert terminal['stage'] == 'solver_exited' and terminal['target_reached']
        assert terminal['exit_code'] == 0
    CASE.mkdir()
    for name in ('constant', 'system', *times):
        shutil.copytree(SOURCE/name, CASE/name)
    geom = json.loads((SOURCE/'GEOMETRIA.json').read_text())
    solids = sorted(set(geom['patch_areas_m2'])-{'inlet', 'outlet'})
    groups = dict(all_boundary=solids+['inlet', 'outlet'], solids=solids, open_ends=['inlet', 'outlet'])
    functions = []
    for name, group in groups.items():
        functions.append(f'''traction_{name} {{ type forces; libs ("libforces.so");
 patches ({' '.join(group)}); rho rhoInf; rhoInf 1.225; CofR (0 0 0);
 writeControl timeStep; writeInterval 1; log false; }}''')
    for patch in ('inlet', 'outlet'):
        functions.append(f'''momentum_{patch} {{ type surfaceFieldValue; libs ("libfieldFunctionObjects.so");
 patch {patch}; operation sum; weightField phi; fields (U); writeFields false;
 writeControl timeStep; writeInterval 1; log false; }}''')
    (CASE/'system/controlDict').write_text('''FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application foamRun; solver incompressibleFluid; startFrom startTime; startTime 80;
stopAt endTime; endTime 100; deltaT 1; writeControl timeStep; writeInterval 1;
writeFormat ascii; writePrecision 12;
functions {\n'''+ '\n'.join(functions)+'\n}\n')
    control = CASE/'system/controlDict'
    control.write_text(control.read_text().replace('startTime 80;', 'startTime '+times[0]+';')
                       .replace('endTime 100;', 'endTime '+times[1]+';'))
    field_hashes = {f'{time}/{field}': hashlib.sha256((CASE/time/field).read_bytes()).hexdigest()
                    for time in times for field in ('U', 'p', 'k', 'omega', 'nut', 'phi')}
    existed = subprocess.run([DOCKER, 'inspect', CONTAINER], capture_output=True, text=True)
    assert existed.returncode != 0, 'Inspect existing audit container'
    identifier = run('create', '--name', CONTAINER, '--init', '--cpus', '2', '--memory', '2g',
                     '--network', 'none', 'codex-aero-openfoam:13', 'sleep', 'infinity',
                     capture_output=True).stdout.strip()
    (CASE/'CONTENEDOR.json').write_text(json.dumps(dict(container=CONTAINER, container_id=identifier,
         purpose='offline saved-field postprocessing only; no flow solver continuation'), indent=2)+'\n')
    run('cp', str(CASE), CONTAINER+':/case')
    run('start', CONTAINER, capture_output=True)
    result = subprocess.run([DOCKER, 'exec', '--workdir', '/case', CONTAINER, '/bin/bash', '-c',
        'source /opt/openfoam13/etc/bashrc && foamPostProcess -solver incompressibleFluid -time '+','.join(times)+' > log.postProcess 2>&1'], text=True)
    run('cp', CONTAINER+':/case/log.postProcess', str(CASE/'log.postProcess'))
    if result.returncode != 0:
        run('stop', CONTAINER, capture_output=True)
        raise RuntimeError('Preserve failed offline postprocessing and diagnose')
    run('cp', CONTAINER+':/case/postProcessing', str(CASE/'postProcessing'))
    run('stop', CONTAINER, capture_output=True)
    data = {}
    for name in groups:
        values, _ = read_series(CASE/'postProcessing', 'traction_'+name, 'forces.dat', 13)
        data[name] = values
    for name in ('solids', 'open_ends'):
        np.testing.assert_array_equal(data[name][:, 0], data['all_boundary'][:, 0])
    np.testing.assert_allclose(data['all_boundary'][:, 1:], data['solids'][:, 1:]+data['open_ends'][:, 1:], atol=1e-8, rtol=1e-8)
    convection = np.zeros((2, 3))
    for patch in ('inlet', 'outlet'):
        values, _ = read_series(CASE/'postProcessing', 'momentum_'+patch, 'surfaceFieldValue.dat', 4)
        np.testing.assert_array_equal(values[:, 0], data['all_boundary'][:, 0])
        convection += 1.225*values[:, 1:]
    traction = data['all_boundary'][:, 1:4]+data['all_boundary'][:, 4:7]
    residual = convection+traction
    scale = 1.225*20**2*geom['patch_areas_m2']['inlet']
    report = dict(scope='Steady CV balance defect on saved iterative fields; not physical accumulation or exact assembled residual',
                  iterations=data['all_boundary'][:, 0].tolist(),
                  boundary_partitions_verified=True, pressure_and_viscous_traction_opposite_fluid_N=traction.tolist(),
                  outward_convective_flux_N=convection.tolist(), residual_N=residual.tolist(),
                  residual_norm_relative_rho_U2_A=(np.linalg.norm(residual, axis=1)/scale).tolist(),
                  normalization_N=scale, field_sha256=field_hashes,
                  source_saved_field_snapshot=snapshot,
                  physical_time_interpretation=False, physical_loads_accepted=False,
                  limits=['No derivative inferred from steady iteration counters.',
                          'Reconstructed stress/flux can differ from the assembled discrete equations.',
                          'Not angular-momentum or energy closure, nor mesh/physical validation.'])
    (CASE/'BALANCE.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    for name, digest in field_hashes.items():
        assert hashlib.sha256((CASE/name).read_bytes()).hexdigest() == digest, 'Postprocessing changed saved input fields'
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
