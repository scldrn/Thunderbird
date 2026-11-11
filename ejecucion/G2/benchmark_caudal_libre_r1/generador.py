"""Analytic reservoir/duct boundary test with free Q and prescribed body force.

Uniform slip duct: U=sqrt(2*G*L), p_kin(x)=G*(x-L).
This verifies boundary/operator coupling, not hover thrust or a real fan.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import subprocess
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(ROOT/'CFD'))
from foam_fields import read_internal
from analizar_series_transitorias import read_series

OUT = HERE/'benchmark_caudal_libre_r1'
DOCKER = '/Users/sam/.docker/bin/docker'
CONTAINER = 'codex-aero-benchmark-caudal-libre-r1'
IMAGE = 'sha256:4ea55efc8f3c56c542acc2d525b9477a73d6a55b8f4d41a7587431fb719f92fb'


def call(*args, check=True):
    return subprocess.run([DOCKER,*args],capture_output=True,text=True,check=check)


def foam(case, name, content, cls='dictionary'):
    path = case/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(f'FoamFile {{ format ascii; class {cls}; object {path.name}; }}\n'+content+'\n')


def main():
    assert not OUT.exists(), 'Preserve previous benchmark and inspect actual process'
    assert call('inspect',CONTAINER,check=False).returncode != 0
    OUT.mkdir();shutil.copy2(__file__,OUT/'generador.py')
    specs = []
    for nx in (4,20):
        for initial in (.5,2.):
            name = f'nx{nx}_Uinicial{initial:g}'
            case = OUT/name;case.mkdir();specs.append((name,nx,initial))
            foam(case,'system/blockMeshDict',f'''convertToMeters 1;
vertices ((0 -.1 -.1) (.2 -.1 -.1) (.2 .1 -.1) (0 .1 -.1)
          (0 -.1 .1) (.2 -.1 .1) (.2 .1 .1) (0 .1 .1));
blocks (hex (0 1 2 3 4 5 6 7) ({nx} 1 1) simpleGrading (1 1 1));
edges ();
boundary (
 inlet {{ type patch; faces ((0 4 7 3)); }}
 outlet {{ type patch; faces ((1 2 6 5)); }}
 sides {{ type wall; faces ((0 1 5 4) (3 7 6 2) (0 3 2 1) (4 5 6 7)); }}
); mergePatchPairs ();''')
            foam(case,'constant/physicalProperties','viscosityModel constant; nu [0 2 -1 0 0 0 0] 0.1;')
            foam(case,'constant/momentumTransport','simulationType laminar; laminar { model Stokes; }')
            foam(case,'constant/fvModels','''acceleration { type semiImplicitSource; cellZone all;
volumeMode specific; sources { U { explicit (5 0 0); implicit 0; } } }''')
            foam(case,'0/U',f'''dimensions [0 1 -1 0 0 0 0]; internalField uniform ({initial} 0 0);
boundaryField {{ inlet {{ type pressureInletOutletVelocity; value uniform ({initial} 0 0); }}
outlet {{ type pressureInletOutletVelocity; value uniform ({initial} 0 0); }}
sides {{ type slip; }} }}''','volVectorField')
            foam(case,'0/p','''dimensions [0 2 -2 0 0 0 0]; internalField uniform 0;
boundaryField { inlet { type totalPressure; p0 uniform 0; U U; phi phi; value uniform 0; }
outlet { type fixedValue; value uniform 0; } sides { type zeroGradient; } }''','volScalarField')
            foam(case,'system/controlDict','''application foamRun; solver incompressibleFluid;
startFrom startTime; startTime 0; stopAt endTime; endTime 200; deltaT 1;
writeControl timeStep; writeInterval 200; writeFormat ascii; writePrecision 14;
functions {
flow_inlet { type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch inlet;
operation sum; fields (phi); writeFields false; log false; writeControl timeStep; writeInterval 1; }
flow_outlet { type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch outlet;
operation sum; fields (phi); writeFields false; log false; writeControl timeStep; writeInterval 1; }
}''')
            foam(case,'system/fvSchemes','''ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; }
divSchemes { default none; div(phi,U) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; } snGradSchemes { default corrected; }
wallDist { method meshWave; }''')
            foam(case,'system/fvSolution','''solvers {
p { solver PCG; preconditioner DIC; tolerance 1e-12; relTol 0; maxIter 500; }
U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-12; relTol 0; maxIter 500; }
} SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }
relaxationFactors { fields { p 0.3; } equations { U 0.5; } }''')
            (case/'ENTRADAS.json').write_text(json.dumps(dict(nx=nx,initial_U_m_s=initial,
                L_m=.2,area_m2=.04,acceleration_m_s2=5.,rho_kg_m3=1.225,
                U_expected_m_s=math.sqrt(2),volume_flow_expected_m3_s=.04*math.sqrt(2),
                predeclared_relative_U_p_Q_tolerance=2e-4,physical_time=False,
                imposed_volume_flow=False,input_sha256={str(p.relative_to(case)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in case.rglob('*') if p.is_file()}),indent=2)+'\n')
    identifier = call('create','--name',CONTAINER,'--init','--network','none','--cpus','1','--memory','1g',IMAGE,'sleep','infinity').stdout.strip()
    state = dict(container=CONTAINER,container_id=identifier,stage='prepared',cases=[],vehicle_solver_started=False)
    def save():
        (OUT/'EJECUCION.json').write_text(json.dumps(state,indent=2)+'\n')
    save();call('cp',str(OUT),CONTAINER+':/bench');call('start',CONTAINER)
    for name,nx,initial in specs:
        state.update(stage='running',active_case=name);save()
        command = [DOCKER,'exec','--workdir','/bench/'+name,CONTAINER,'/bin/bash','-c',
                   'source /opt/openfoam13/etc/bashrc && blockMesh > log.blockMesh 2>&1 && foamRun > log.foamRun 2>&1']
        try:
            code = subprocess.run(command,timeout=120).returncode
        except subprocess.TimeoutExpired:
            call('stop',CONTAINER);code=-1
        call('cp',CONTAINER+':/bench/'+name+'/.',str(OUT/name))
        state['cases'].append(dict(name=name,exit_code=code));save()
        if code != 0:
            call('stop',CONTAINER,check=False);state.update(stage='failed',container_stopped=True);save()
            raise RuntimeError('Preserve failed free-flow benchmark and inspect its logs')
    call('stop',CONTAINER);state.update(stage='solver_exited',container_stopped=True,exit_code=0);save()
    results = []
    for name,nx,initial in specs:
        case = OUT/name;U = read_internal(case/'200/U',nx,3);p = read_internal(case/'200/p',nx,1)
        expected = math.sqrt(2);x = (np.arange(nx)+.5)*.2/nx
        U_error = float(np.max(abs(U-np.array([expected,0,0])))/expected)
        p_error = float(np.max(abs(p-5*(x-.2))))
        inlet,_ = read_series(case/'postProcessing','flow_inlet','surfaceFieldValue.dat',2)
        outlet,_ = read_series(case/'postProcessing','flow_outlet','surfaceFieldValue.dat',2)
        Qin,Qout = inlet[-1,1],outlet[-1,1]
        Q_error = float(abs(Qout/(.04*expected)-1))
        assert U_error < 2e-4 and p_error < 2e-4 and Q_error < 2e-4
        assert abs(Qin+Qout)/(.04*expected) < 1e-9
        results.append(dict(case=name,nx=nx,initial_U_m_s=initial,final_U_mean_m_s=float(U[:,0].mean()),
                            U_relative_error=U_error,p_error_normalized_G_L=p_error,Q_relative_error=Q_error,
                            outward_inlet_Q_m3_s=float(Qin),outward_outlet_Q_m3_s=float(Qout)))
    report = dict(scope='Slip-duct total-pressure/free-Q boundary/operator verification only',
                  analytic_formula='U=sqrt(2*G*L); p_kin(x)=G*(x-L); Q=A*U',results=results,
                  all_cases_pass=True,volume_flow_prescribed=False,
                  vehicle_or_hover_thrust_validated=False,rotor_or_shaft_power_validated=False,
                  source_velocity_is_numerically_solved=True,
                  limitations=['Slip sides and uniform incompressible flow; no vanes, rotor, losses or exterior.',
                               'Reservoir/exit boundary surrogate is not actual vehicle inlet-lip/exterior flow.'])
    (OUT/'AUDITORIA.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
