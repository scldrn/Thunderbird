"""Analytic test of saved-field force/flux postprocessing, not a flow solve.

Two independent uniform states on a unit cube, at U=3/6 m/s, pkin=5 m2/s2.
Checks signs, weights, rho conversion and reloading of the stored face flux.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'CFD'))
from analizar_series_transitorias import read_series

CASE = HERE/'benchmark_cv_uniforme'
CONTAINER = 'codex-aero-cv-uniforme-v1'
DOCKER = '/Users/sam/.docker/bin/docker'


def run(*args, **kwargs):
    return subprocess.run([DOCKER, *args], check=True, text=True, **kwargs)


def foam(path, text, cls='dictionary'):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('FoamFile { version 2.0; format ascii; class '+cls+'; object '+path.name+'; }\n'+text+'\n')


def list_body(path):
    text = path.read_text()
    match = re.search(r'\n(\d+)\s*\(\s*\n', text)
    assert match, path
    end = text.find('\n)', match.end())
    return int(match[1]), text[match.end():end]


def main():
    if CASE.exists():
        raise FileExistsError('Preserve existing benchmark; inspect state rather than duplicate it')
    CASE.mkdir()
    foam(CASE/'constant/physicalProperties', 'viscosityModel constant; nu [0 2 -1 0 0 0 0] 0.1;')
    foam(CASE/'constant/momentumTransport', 'simulationType laminar;')
    foam(CASE/'system/blockMeshDict', '''convertToMeters 1;
vertices ((0 0 0)(1 0 0)(1 1 0)(0 1 0)(0 0 1)(1 0 1)(1 1 1)(0 1 1));
blocks (hex (0 1 2 3 4 5 6 7) (4 4 4) simpleGrading (1 1 1));
edges (); boundary (
 inlet { type patch; faces ((0 4 7 3)); }
 outlet { type patch; faces ((1 2 6 5)); }
 walls { type wall; faces ((0 3 2 1)(4 5 6 7)(0 1 5 4)(3 7 6 2)); }
); mergePatchPairs ();''')
    functions = []
    for patch, patches in [('inlet', 'inlet'), ('outlet', 'outlet'), ('all', 'inlet outlet walls')]:
        functions.append(f'''force_{patch} {{ type forces; libs ("libforces.so"); patches ({patches});
 rho rhoInf; rhoInf 1.225; CofR (0 0 0); writeControl timeStep; writeInterval 1; }}''')
    for patch in ('inlet', 'outlet'):
        functions.append(f'''momentum_{patch} {{ type surfaceFieldValue; libs ("libfieldFunctionObjects.so");
 patch {patch}; operation sum; weightField phi; fields (U); writeFields false; writeControl timeStep; writeInterval 1; }}''')
        functions.append(f'''flow_{patch} {{ type surfaceFieldValue; libs ("libfieldFunctionObjects.so");
 patch {patch}; operation sum; fields (phi); writeFields false; writeControl timeStep; writeInterval 1; }}''')
    foam(CASE/'system/controlDict', '''application foamRun; solver incompressibleFluid;
startFrom startTime; startTime 0; stopAt endTime; endTime 1; deltaT 1;
writeControl timeStep; writeInterval 1; writeFormat ascii; writePrecision 14;
functions {\n'''+ '\n'.join(functions)+'\n}')
    foam(CASE/'system/fvSchemes', '''ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; }
divSchemes { default none; div(phi,U) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear corrected; } interpolationSchemes { default linear; }
snGradSchemes { default corrected; }''')
    foam(CASE/'system/fvSolution', '''solvers { p { solver GAMG; tolerance 1e-10; relTol 0; smoother GaussSeidel; }
 U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-10; relTol 0; } }
SIMPLE { nNonOrthogonalCorrectors 0; }''')
    for name, speed in [('0', 3.), ('1', 6.)]:
        boundaries = ' '.join(f'{p} {{ type fixedValue; value uniform ({speed} 0 0); }}' for p in ('inlet', 'outlet', 'walls'))
        foam(CASE/name/'U', f'dimensions [0 1 -1 0 0 0 0]; internalField uniform ({speed} 0 0); boundaryField {{ {boundaries} }}', 'volVectorField')
        boundaries = ' '.join(f'{p} {{ type fixedValue; value uniform 5; }}' for p in ('inlet', 'outlet', 'walls'))
        foam(CASE/name/'p', f'dimensions [0 2 -2 0 0 0 0]; internalField uniform 5; boundaryField {{ {boundaries} }}', 'volScalarField')
    existed = subprocess.run([DOCKER, 'inspect', CONTAINER], capture_output=True, text=True)
    assert existed.returncode != 0
    identifier = run('create', '--name', CONTAINER, '--init', '--cpus', '1', '--memory', '1g',
                     '--network', 'none', 'codex-aero-openfoam:13', 'sleep', 'infinity', capture_output=True).stdout.strip()
    (CASE/'CONTENEDOR.json').write_text(json.dumps(dict(container=CONTAINER, id=identifier,
         stage='benchmark_preparation', flow_solver_started=False), indent=2)+'\n')
    run('cp', str(CASE), CONTAINER+':/case')
    run('start', CONTAINER, capture_output=True)
    run('exec', '--workdir', '/case', CONTAINER, '/bin/bash', '-c',
         'source /opt/openfoam13/etc/bashrc && blockMesh > log.blockMesh 2>&1')
    run('cp', CONTAINER+':/case/constant/polyMesh', str(CASE/'constant/polyMesh'))
    mesh = CASE/'constant/polyMesh'
    _, text = list_body(mesh/'points')
    points = np.fromstring(text.replace('(', ' ').replace(')', ' '), sep=' ').reshape(-1, 3)
    count, text = list_body(mesh/'faces')
    assert all(line.startswith('4(') for line in text.splitlines())
    faces = np.fromstring(text.replace('4(', ' ').replace(')', ' '), sep=' ', dtype=int).reshape(-1, 4)
    assert len(faces) == count
    xyz = points[faces]
    Sf = .5*np.cross(xyz, np.roll(xyz, -1, axis=1)).sum(axis=1)
    n_internal, _ = list_body(mesh/'neighbour')
    for name, speed in [('0', 3.), ('1', 6.)]:
        values = '\n'.join(f'{v:.16g}' for v in speed*Sf[:n_internal, 0])
        bc = f'''inlet {{ type calculated; value uniform {-speed/16}; }}
outlet {{ type calculated; value uniform {speed/16}; }}
walls {{ type calculated; value uniform 0; }}'''
        foam(CASE/name/'phi', f'''dimensions [0 3 -1 0 0 0 0];
internalField nonuniform List<scalar> {n_internal}\n(\n{values}\n); boundaryField {{ {bc} }}''', 'surfaceScalarField')
        run('cp', str(CASE/name/'phi'), CONTAINER+':/case/'+name+'/phi')
    result = subprocess.run([DOCKER, 'exec', '--workdir', '/case', CONTAINER, '/bin/bash', '-c',
         'source /opt/openfoam13/etc/bashrc && foamPostProcess -solver incompressibleFluid -time 0,1 > log.postProcess 2>&1'], text=True)
    run('cp', CONTAINER+':/case/log.postProcess', str(CASE/'log.postProcess'))
    if result.returncode != 0:
        run('stop', CONTAINER, capture_output=True)
        raise RuntimeError('Benchmark preparation/postprocess failed; preserve logs')
    run('cp', CONTAINER+':/case/postProcessing', str(CASE/'postProcessing'))
    run('stop', CONTAINER, capture_output=True)
    checks = {}
    expected_speed = np.array([3., 6.])
    for patch, sign in [('inlet', -1), ('outlet', 1)]:
        flux, _ = read_series(CASE/'postProcessing', 'flow_'+patch, 'surfaceFieldValue.dat', 2)
        momentum, _ = read_series(CASE/'postProcessing', 'momentum_'+patch, 'surfaceFieldValue.dat', 4)
        force, _ = read_series(CASE/'postProcessing', 'force_'+patch, 'forces.dat', 13)
        np.testing.assert_array_equal(flux[:, 0], [0., 1.])
        np.testing.assert_allclose(flux[:, 1], sign*expected_speed, atol=1e-12)
        np.testing.assert_allclose(momentum[:, 1], sign*expected_speed**2, atol=1e-12)
        np.testing.assert_allclose(momentum[:, 2:], 0, atol=1e-12)
        np.testing.assert_allclose(force[:, 1:4], np.tile([sign*1.225*5, 0, 0], (2, 1)), atol=1e-12)
        np.testing.assert_allclose(force[:, 4:7], 0, atol=1e-12)
        checks[patch] = dict(flux_m3_s=flux[:, 1].tolist(), momentum_unscaled=momentum[:, 1:].tolist(), pressure_force_N=force[:, 1:4].tolist())
    all_force, _ = read_series(CASE/'postProcessing', 'force_all', 'forces.dat', 13)
    np.testing.assert_allclose(all_force[:, 1:], 0, atol=1e-12)
    report = dict(scope='Manufactured saved-field postprocessing operator test; not rotor or vehicle validation',
                  cells=64, independent_uniform_states_m_s=[3., 6.], pressure_kinematic_m2_s2=5.,
                  density_kg_m3=1.225, verified=True, force_and_flux_checks=checks,
                  field_reload_across_saved_states_verified=True, physical_acceleration_inferred=False,
                  all_boundary_force_and_moment_zero_verified=True,
                  case_sha256={str(p.relative_to(CASE)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for name in ('0', '1', 'constant', 'system') for p in (CASE/name).rglob('*') if p.is_file()})
    (CASE/'AUDITORIA.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'case_sha256'}, indent=2))


if __name__ == '__main__':
    main()
