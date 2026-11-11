"""Manufactured Couette/Poiseuille stress and saved-field CV checks.

No flow solve. Includes a continuous parabola and the exact cell-centred
discrete parabola for the declared orthogonal two-point wall stencil.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np

from verificar_cv_uniforme import foam, list_body

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'CFD'))
from analizar_series_transitorias import read_series

CASE = HERE/'benchmark_cv_no_uniforme'
DOCKER = '/Users/sam/.docker/bin/docker'
CONTAINER = 'codex-aero-cv-no-uniforme-v1'
RHO, NU = 1.225, .1
PATCHES = ('inlet', 'outlet', 'bottom', 'top', 'side_min', 'side_max')


def run(*args, **kwargs):
    return subprocess.run([DOCKER, *args], check=True, text=True, **kwargs)


def values(a):
    a = np.asarray(a)
    if a.ndim == 2:
        lines = ['('+' '.join(f'{x:.16g}' for x in row)+')' for row in a]
        kind = 'vector'
    else:
        lines = [f'{x:.16g}' for x in a]
        kind = 'scalar'
    return f'nonuniform List<{kind}> {len(a)}\n(\n'+'\n'.join(lines)+'\n)'


def setup(case, ny):
    foam(case/'constant/physicalProperties', f'viscosityModel constant; nu [0 2 -1 0 0 0 0] {NU};')
    foam(case/'constant/momentumTransport', 'simulationType laminar;')
    foam(case/'system/blockMeshDict', f'''convertToMeters 1;
vertices ((0 0 0)(1 0 0)(1 1 0)(0 1 0)(0 0 1)(1 0 1)(1 1 1)(0 1 1));
blocks (hex (0 1 2 3 4 5 6 7) (4 {ny} 2) simpleGrading (1 1 1));
edges (); boundary (
inlet {{type patch; faces ((0 4 7 3));}}
outlet {{type patch; faces ((1 2 6 5));}}
bottom {{type wall; faces ((0 1 5 4));}}
top {{type wall; faces ((3 7 6 2));}}
side_min {{type patch; faces ((0 3 2 1));}}
side_max {{type patch; faces ((4 5 6 7));}}
); mergePatchPairs ();''')
    functions = []
    for name, group in [(p, p) for p in PATCHES]+[('all', ' '.join(PATCHES))]:
        functions.append(f'''force_{name} {{type forces; libs ("libforces.so"); patches ({group});
rho rhoInf; rhoInf {RHO}; CofR (0 0 0); writeControl timeStep; writeInterval 1;}}''')
    for patch in ('inlet', 'outlet'):
        for name, field, operation in [('momentum', 'U', 'sum; weightField phi'), ('flow', 'phi', 'sum')]:
            functions.append(f'''{name}_{patch} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so");
patch {patch}; operation {operation}; fields ({field}); writeFields false; writeControl timeStep; writeInterval 1;}}''')
    foam(case/'system/controlDict', '''application foamRun; solver incompressibleFluid;
startFrom startTime; startTime 0; stopAt endTime; endTime 3; deltaT 1;
writeControl timeStep; writeInterval 1; writeFormat ascii; writePrecision 14;
functions {\n'''+ '\n'.join(functions)+'\n}')
    foam(case/'system/fvSchemes', '''ddtSchemes {default steadyState;}
gradSchemes {default Gauss linear;}
divSchemes {default none; div(phi,U) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear;}
laplacianSchemes {default Gauss linear corrected;}
interpolationSchemes {default linear;} snGradSchemes {default corrected;}''')
    foam(case/'system/fvSolution', '''solvers {p {solver GAMG; tolerance 1e-10; relTol 0; smoother GaussSeidel;}
U {solver smoothSolver; smoother symGaussSeidel; tolerance 1e-10; relTol 0;}}
SIMPLE {nNonOrthogonalCorrectors 0;}''')


def geometry(case, ny):
    mesh = case/'constant/polyMesh'
    count, body = list_body(mesh/'points')
    points = np.fromstring(body.replace('(', ' ').replace(')', ' '), sep=' ').reshape(-1, 3)
    assert len(points) == count
    count, body = list_body(mesh/'faces')
    assert all(line.startswith('4(') for line in body.splitlines())
    faces = np.fromstring(body.replace('4(', ' ').replace(')', ' '), sep=' ', dtype=int).reshape(-1, 4)
    assert len(faces) == count
    xyz = points[faces]
    face_centres = xyz.mean(axis=1)
    sf = .5*np.cross(xyz, np.roll(xyz, -1, axis=1)).sum(axis=1)
    count, body = list_body(mesh/'owner')
    owner = np.fromstring(body, sep=' ', dtype=int)
    assert len(owner) == count == len(faces)
    nint, body = list_body(mesh/'neighbour')
    neighbour = np.fromstring(body, sep=' ', dtype=int)
    assert len(neighbour) == nint
    nc = 4*ny*2
    np.testing.assert_array_equal(np.bincount(owner, minlength=nc)+np.bincount(neighbour, minlength=nc), 6)
    sums = xyz.sum(axis=1)
    cc = np.column_stack([(np.bincount(owner, weights=sums[:, k], minlength=nc)
                          +np.bincount(neighbour, weights=sums[:nint, k], minlength=nc))/24 for k in range(3)])
    np.testing.assert_allclose(np.sort(np.unique(cc[:, 1])), (np.arange(ny)+.5)/ny, atol=1e-14)
    import re
    text = (mesh/'boundary').read_text()
    patches = {}
    for p in PATCHES:
        block = re.search(r'\b'+p+r'\s*\{(.*?)\}', text, re.S)[1]
        size = int(re.search(r'nFaces\s+(\d+)', block)[1])
        start = int(re.search(r'startFace\s+(\d+)', block)[1])
        patches[p] = slice(start, start+size)
    return cc, face_centres, sf, nint, patches


def write_fields(case, ny):
    cc, fc, sf, nint, patches = geometry(case, ny)
    for t in range(4):
        a = 3. if t == 0 else 6.
        offset = 6/(4*ny**2) if t == 3 else 0.
        g = 2*NU*6 if t >= 2 else 0.
        def u(xyz, boundary=None):
            y = xyz[:, 1]
            x = 2+a*y if t < 2 else 6*y*(1-y)+offset
            if t >= 2 and boundary in ('top', 'bottom'):
                x = np.zeros_like(x)
            return np.column_stack((x, np.zeros_like(x), np.zeros_like(x)))
        def p(xyz):
            return 5-g*xyz[:, 0]
        ub = ' '.join(name+' {type fixedValue; value '+values(u(fc[s], name))+';}' for name, s in patches.items())
        pb = ' '.join(name+' {type fixedValue; value '+values(p(fc[s]))+';}' for name, s in patches.items())
        phib = ' '.join(name+' {type calculated; value '+values(np.sum(u(fc[s], name)*sf[s], axis=1))+';}' for name, s in patches.items())
        foam(case/str(t)/'U', 'dimensions [0 1 -1 0 0 0 0]; internalField '+values(u(cc))+'; boundaryField {'+ub+'}', 'volVectorField')
        foam(case/str(t)/'p', 'dimensions [0 2 -2 0 0 0 0]; internalField '+values(p(cc))+'; boundaryField {'+pb+'}', 'volScalarField')
        internal_phi = np.sum(u(fc[:nint])*sf[:nint], axis=1)
        foam(case/str(t)/'phi', 'dimensions [0 3 -1 0 0 0 0]; internalField '+values(internal_phi)+'; boundaryField {'+phib+'}', 'surfaceScalarField')


def audit(case, ny):
    pp = case/'postProcessing'
    forces = {p:read_series(pp, 'force_'+p, 'forces.dat', 13)[0] for p in (*PATCHES, 'all')}
    for a in forces.values():
        np.testing.assert_array_equal(a[:, 0], [0, 1, 2, 3])
    records = []
    for t in range(4):
        a = 3. if t == 0 else 6.
        g = 1.2 if t >= 2 else 0.
        midp = RHO*(5-g/2)
        expected_p = dict(inlet=[-RHO*5, 0, 0], outlet=[RHO*(5-g), 0, 0],
                          bottom=[0, -midp, 0], top=[0, midp, 0],
                          side_min=[0, 0, -midp], side_max=[0, 0, midp])
        tau = RHO*NU*(a if t < 2 else 6*(1-.5/ny if t == 2 else 1))
        expected_v = dict(inlet=[0, tau if t < 2 else 0, 0], outlet=[0, -tau if t < 2 else 0, 0],
                          bottom=[tau, 0, 0], top=[-tau if t < 2 else tau, 0, 0],
                          side_min=[0, 0, 0], side_max=[0, 0, 0])
        for patch in PATCHES:
            np.testing.assert_allclose(forces[patch][t, 1:4], expected_p[patch], atol=1e-10)
            np.testing.assert_allclose(forces[patch][t, 4:7], expected_v[patch], atol=1e-10)
        np.testing.assert_allclose(sum(forces[p][t, 1:] for p in PATCHES), forces['all'][t, 1:], atol=1e-10)
        off = 6/(4*ny**2) if t == 3 else 0.
        mean = 2+a/2 if t < 2 else 6*(1/6+1/(12*ny**2))+off
        second = 4+2*a+a*a/3-a*a/(12*ny**2) if t < 2 else 36*(1/30+7/(240*ny**4))+12*off*(1/6+1/(12*ny**2))+off**2
        convective = np.zeros(3)
        for patch, sign in [('inlet', -1), ('outlet', 1)]:
            flow, _ = read_series(pp, 'flow_'+patch, 'surfaceFieldValue.dat', 2)
            momentum, _ = read_series(pp, 'momentum_'+patch, 'surfaceFieldValue.dat', 4)
            np.testing.assert_allclose(flow[t, 1], sign*mean, atol=1e-10)
            np.testing.assert_allclose(momentum[t, 1:], [sign*second, 0, 0], atol=1e-10)
            convective += RHO*momentum[t, 1:]
        defect = convective+forces['all'][t, 1:4]+forces['all'][t, 4:7]
        predicted = -RHO*NU*6/ny if t == 2 else 0.
        np.testing.assert_allclose(defect, [predicted, 0, 0], atol=1e-10)
        records.append(dict(saved_index=t, state=('Couette_a3','Couette_a6','Poiseuille_continuous','Poiseuille_discrete')[t],
            wall_viscous_force_per_wall_N=tau, CV_defect_N=defect.tolist(),
            predicted_CV_defect_N=[predicted, 0, 0],
            pressure_gradient_force_scale_N=2*RHO*NU*6 if t >= 2 else None,
            continuous_wall_force_relative_error=.5/ny if t == 2 else 0.))
    return dict(ny=ny,cells=4*ny*2,checks_passed=True,states=records)


def main():
    assert not CASE.exists(), 'Preserve earlier benchmark'
    assert subprocess.run([DOCKER,'inspect',CONTAINER],capture_output=True).returncode != 0
    CASE.mkdir()
    for ny in (8, 16, 32):
        setup(CASE/f'ny{ny}', ny)
    identifier = run('create','--name',CONTAINER,'--init','--cpus','1','--memory','1g','--network','none',
                     'codex-aero-openfoam:13','sleep','infinity',capture_output=True).stdout.strip()
    (CASE/'CONTENEDOR.json').write_text(json.dumps(dict(container=CONTAINER,id=identifier,flow_solver_started=False),indent=2)+'\n')
    run('cp',str(CASE),CONTAINER+':/case')
    run('start',CONTAINER,capture_output=True)
    results = []
    try:
        for ny in (8, 16, 32):
            case = CASE/f'ny{ny}'
            run('exec','--workdir',f'/case/ny{ny}',CONTAINER,'/bin/bash','-c',
                'source /opt/openfoam13/etc/bashrc && blockMesh > log.blockMesh 2>&1')
            run('cp',f'{CONTAINER}:/case/ny{ny}/constant/polyMesh',str(case/'constant/polyMesh'))
            write_fields(case, ny)
            for t in range(4):
                run('cp',str(case/str(t)),f'{CONTAINER}:/case/ny{ny}/{t}')
            process = subprocess.run([DOCKER,'exec','--workdir',f'/case/ny{ny}',CONTAINER,'/bin/bash','-c',
                'source /opt/openfoam13/etc/bashrc && foamPostProcess -solver incompressibleFluid -time 0,1,2,3 > log.postProcess 2>&1'],text=True)
            run('cp',f'{CONTAINER}:/case/ny{ny}/log.postProcess',str(case/'log.postProcess'))
            assert process.returncode == 0, 'Inspect preserved postprocessing failure'
            run('cp',f'{CONTAINER}:/case/ny{ny}/postProcessing',str(case/'postProcessing'))
            results.append(audit(case, ny))
    finally:
        run('stop',CONTAINER,capture_output=True)
    errors = np.array([row['states'][2]['continuous_wall_force_relative_error'] for row in results])
    np.testing.assert_allclose(errors[:-1]/errors[1:], 2., atol=1e-12)
    report = dict(scope='Manufactured nonuniform saved-field stress/CV verification, not physical rotor or vehicle validation',
        density_kg_m3=RHO,kinematic_viscosity_m2_s=NU,domain_m=[1,1,1],
        flow_solver_executed=False,counter_is_physical_time=False,
        pressure_and_viscous_partition_verified=True,expected_wall_stencil_order_verified=1,
        discrete_parabola_offset_m_s='6/(4*ny^2)',
        all_checks_passed=True,results=results,
        limits=['Orthogonal mesh, laminar fluid, Gauss linear gradients and two-point walls only.',
                'Imposed side profiles are manufactured mathematical boundaries, not a six-wall physical channel.',
                'Does not validate limited pressure gradient, turbulence, corners, nonorthogonality or installed C02 loads.'],
        input_sha256={str(p.relative_to(CASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in CASE.rglob('*')
                      if p.is_file() and ('system' in p.parts or p.name in ('U','p','phi','physicalProperties','momentumTransport'))})
    (CASE/'AUDITORIA.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='input_sha256'},indent=2))


if __name__ == '__main__':
    main()
