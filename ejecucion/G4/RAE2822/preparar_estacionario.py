"""New steady algorithm baseline after the degenerate LTS pilot; no rollback loss."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE/'piloto_r4_hibrido_resuelto'
CASE = HERE/'piloto_r6_estacionario'
OFFICIAL = HERE.parents[2]/'fuentes/OpenFOAM13_aerofoilNACA0012Steady'
CONTAINER = 'codex-aero-rae2822-r6'
DOCKER = '/Users/sam/.docker/bin/docker'


def main():
    global CASE, CONTAINER
    parser = argparse.ArgumentParser()
    parser.add_argument('--case',type=Path,default=CASE)
    parser.add_argument('--container',default=CONTAINER)
    parser.add_argument('--pressure-smoother',choices=('GaussSeidel','DIC','DILUGaussSeidel'),default='GaussSeidel')
    parser.add_argument('--transonic',choices=('yes','no'),default='yes')
    args = parser.parse_args()
    CASE, CONTAINER = args.case.resolve(), args.container
    assert not CASE.exists(), 'Preserve existing steady baseline'
    failure = json.loads((HERE/'piloto_r5_continuacion_Co1/AUDITORIA_PILOTO.json').read_text())
    assert not failure['diagnostic_screens']['no_near_vacuum_sentinel']
    CASE.mkdir()
    for name in ('0','constant','system'):
        shutil.copytree(SOURCE/name,CASE/name)
    for name in ('MALLA.json','MALLA_OPENFOAM.json','Cp_experimental.csv'):
        shutil.copy2(SOURCE/name,CASE/name)
    inputs = json.loads((SOURCE/'ENTRADAS.json').read_text())
    velocity = ' '.join(f'{v:.15g}' for v in inputs['velocity_m_s'])
    p = inputs['p_Pa']
    for name, replacement in [('U',f'outlet {{type freestreamVelocity; freestreamValue uniform ({velocity}); value uniform ({velocity});}}'),
                              ('p',f'outlet {{type freestreamPressure; freestreamValue uniform {p:.15g}; value uniform {p:.15g};}}')]:
        path = CASE/'0'/name
        text, count = re.subn(r'\boutlet\s*\{[^{}]*\}',replacement,path.read_text())
        assert count == 1
        path.write_text(text)
    schemes = '''FoamFile {version 2.0; format ascii; class dictionary; object fvSchemes;}
ddtSchemes {default steadyState;}
gradSchemes {default Gauss linear; limited cellLimited Gauss linear 1;
 grad(U) $limited; grad(k) $limited; grad(omega) $limited;}
divSchemes {default none; div(phi,U) bounded Gauss upwind; div(phi,h) bounded Gauss upwind;
 div(phi,K) bounded Gauss upwind; div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind;
 div(phid,p) Gauss upwind; div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;}
laplacianSchemes {default Gauss linear corrected;}
interpolationSchemes {default linear;} snGradSchemes {default corrected;}
wallDist {method meshWave;}
'''
    (CASE/'system/fvSchemes').write_text(schemes)
    solution_text = '''FoamFile {version 2.0; format ascii; class dictionary; object fvSolution;}
solvers {
 p {solver GAMG; smoother DIC; tolerance 1e-9; relTol 0.01; maxIter 500;}
 pFinal {$p; relTol 0;}
 rho {solver diagonal;} rhoFinal {$rho;}
 "(U|h|k|omega)" {solver PBiCGStab; preconditioner DILU; tolerance 1e-9; relTol 0.05; maxIter 500;}
 "(U|h|k|omega)Final" {solver PBiCGStab; preconditioner DILU; tolerance 1e-9; relTol 0; maxIter 500;}
}
PIMPLE {transonic yes; nOuterCorrectors 1; nCorrectors 1; nNonOrthogonalCorrectors 1;}
relaxationFactors {fields {p 0.3; rho 0.01;} equations {U 0.7; h 0.7; k 0.7; omega 0.7;}}
'''
    solution_text = solution_text.replace('smoother DIC;', 'smoother '+args.pressure_smoother+';')
    solution_text = solution_text.replace('transonic yes;', 'transonic '+args.transonic+';')
    (CASE/'system/fvSolution').write_text(solution_text)
    control = CASE/'system/controlDict'
    text, count = re.subn(r'\bendTime 100;', 'endTime 500;',control.read_text())
    assert count == 1 and 'runTimeModifiable true;' in text
    control.write_text(text)
    inputs.update(scope='Steady compressible baseline500-iteration pilot after LTS degeneracy; not accepted validation',
        iteration_start=0,iteration_target=500,time_discretization='steadyState, not localEuler',
        initialization='Original uniform freestream fields, not degenerate r5 or its near-vacuum values',
        algorithm='Steady PIMPLE, pressure0.3 and density0.01 field relaxation, official tutorial baseline adapted to RAE',
        pressure_gradient='Gauss linear, conservative boundary/volume identity; only U/k/omega gradients limited',
        pressure_matrix='Asymmetric with transonic convection' if args.transonic == 'yes' else 'Symmetric pressure-Poisson correction, matching the official steady aerofoil tutorial default',
        pressure_correction_transonic_switch=args.transonic,
        pressure_smoother=args.pressure_smoother,
        outlet_model='freestreamVelocity/freestreamPressure as official aerofoil tutorial, reference p/U unchanged',
        scheme='First-order upwind startup; official tutorial higher-order convection deferred until stability/convergence',
        near_vacuum_runtime_guard=dict(p_min_over_pInf=.05,rho_min_over_rhoInf=.05,action='stopAt writeNow',
            scope='Numerical degeneracy sentinel only, not physical acceptance criteria'),
        input_sha256={str(path.relative_to(CASE)):hashlib.sha256(path.read_bytes()).hexdigest()
                      for folder in ('0','constant','system') for path in (CASE/folder).rglob('*') if path.is_file()})
    (CASE/'ENTRADAS.json').write_text(json.dumps(inputs,indent=2)+'\n')
    provenance=dict(source_geometry_and_uniform_fields=SOURCE.name,degenerate_r5_preserved=True,
        package_change_not_single_parameter_test=True,
        official_tutorial_sha256={str(path.relative_to(OFFICIAL)):hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in (OFFICIAL/'system').iterdir() if path.is_file()},
        changes=['LTS_to_steadyState','conservative pressure/default Gauss gradient','density and pressure field relaxation',
                 'freestream BC on downstream plane','one outer corrector','corrected nonorthogonal diffusion'],
        physical_validation_accepted=False,historical_solvers_resumed=False)
    provenance['pressure_smoother'] = args.pressure_smoother
    provenance['pressure_correction_transonic_switch'] = args.transonic
    provenance['physical_compressibility_retained'] = 'Perfect-gas rho(p,T), sensible enthalpy, viscosity, Mach0.729 andRe6.5million unchanged; this switch changes the pressure-correction algorithm, not the governing physical target.'
    provenance['startup_failure_preserved'] = 'piloto_r6_estacionario: DIC is symmetric-only and failed on the transonic asymmetric matrix before completing any iteration'
    provenance['asymmetric_failure_preserved'] = 'piloto_r7_estacionario_asimetrico: pressure matrix iteration diverged to nonfinite fields; guarded stop and subsequent SIGTERM recorded'
    (CASE/'DERIVACION.json').write_text(json.dumps(provenance,indent=2)+'\n')
    (CASE/'benchmark.foam').touch()
    def run(*args):
        return subprocess.run([DOCKER,*args],check=True,capture_output=True,text=True)
    assert subprocess.run([DOCKER,'inspect',CONTAINER],capture_output=True).returncode != 0
    identifier = run('create','--name',CONTAINER,'--init','--cpus','2','--memory','2g','--network','none',
                     'codex-aero-openfoam:13','sleep','infinity').stdout.strip()
    (CASE/'CONTENEDOR.json').write_text(json.dumps(dict(container=CONTAINER,container_id=identifier,
        stage='steady_baseline_same_checked_mesh_no_solver',own_solver_started=False),indent=2)+'\n')
    run('cp',str(CASE),CONTAINER+':/case')
    run('start',CONTAINER)
    print(json.dumps(dict(case=str(CASE),container=CONTAINER,iteration_target=500),indent=2))


if __name__ == '__main__':
    main()
