"""Prepare NASA RAE2822 Study4 conditions, not the vehicle flow problem."""
from pathlib import Path
import argparse
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
CASE = HERE/'piloto_r1'


def foam(path, text, cls='dictionary'):
    p = CASE/path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('FoamFile { version 2.0; format ascii; class '+cls+'; object '+p.name+'; }\n'+text+'\n')


def main():
    global CASE
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, default=CASE)
    args = parser.parse_args()
    CASE = args.case.resolve()
    if (CASE/'ENTRADAS.json').exists():
        raise FileExistsError('Preserve existing case inputs')
    mesh = json.loads((CASE/'MALLA.json').read_text())
    R, gamma = 287.05287, 1.4
    T = 460*5/9
    p = 15.80734*6894.757293168
    c = mesh['chord_m']
    speed = .729*math.sqrt(gamma*R*T)
    alpha = math.radians(2.31)
    rho = p/(R*T)
    mu = rho*speed*c/6.5e6
    Ts = 110.4
    As = mu*(T+Ts)/T**1.5
    Cp = gamma*R/(gamma-1)
    U = [speed*math.cos(alpha), speed*math.sin(alpha), 0.]
    u_string = ' '.join(f'{v:.15g}' for v in U)
    # Freestream turbulence is not fully specified in the NASA input. It is a
    # declared model assumption, not inferred experimental turbulence intensity.
    intensity, nu_t_ratio = .001, 1.
    k = 1.5*(intensity*speed)**2
    omega = k/(nu_t_ratio*mu/rho)
    foam('constant/physicalProperties', f'''thermoType {{ type hePsiThermo; mixture pureMixture;
 transport sutherland; thermo hConst; equationOfState perfectGas; specie specie; energy sensibleEnthalpy; }}
mixture {{ specie {{ molWeight {8314.46261815324/R:.15g}; }}
 thermodynamics {{ Cp {Cp:.15g}; hf 0; }}
 transport {{ As {As:.15g}; Ts {Ts}; }} }}''')
    foam('constant/momentumTransport', 'simulationType RAS; RAS { model kOmegaSST; turbulence on; printCoeffs on; }')
    empty = 'frontAndBack { type empty; }'
    foam('0/U', f'''dimensions [0 1 -1 0 0 0 0]; internalField uniform ({u_string});
boundaryField {{
 farfield {{ type freestreamVelocity; freestreamValue uniform ({u_string}); value uniform ({u_string}); }}
 outlet {{ type pressureInletOutletVelocity; value uniform ({u_string}); }}
 airfoil {{ type noSlip; }} {empty} }}''', 'volVectorField')
    foam('0/p', f'''dimensions [1 -1 -2 0 0 0 0]; internalField uniform {p:.15g};
boundaryField {{
 farfield {{ type freestreamPressure; freestreamValue uniform {p:.15g}; }}
 outlet {{ type fixedValue; value uniform {p:.15g}; }}
 airfoil {{ type zeroGradient; }} {empty} }}''', 'volScalarField')
    foam('0/T', f'''dimensions [0 0 0 1 0 0 0]; internalField uniform {T:.15g};
boundaryField {{
 "(farfield|outlet)" {{ type inletOutlet; inletValue uniform {T:.15g}; value uniform {T:.15g}; }}
 airfoil {{ type zeroGradient; }} {empty} }}''', 'volScalarField')
    for name, dimensions, value, wall in [('k', '[0 2 -2 0 0 0 0]', k, 'kqRWallFunction'),
                                           ('omega', '[0 0 -1 0 0 0 0]', omega, 'omegaWallFunction')]:
        foam('0/'+name, f'''dimensions {dimensions}; internalField uniform {value:.15g};
boundaryField {{ "(farfield|outlet)" {{ type inletOutlet; inletValue uniform {value:.15g}; value uniform {value:.15g}; }}
 airfoil {{ type {wall}; value uniform {value:.15g}; }} {empty} }}''', 'volScalarField')
    foam('0/nut', f'''dimensions [0 2 -1 0 0 0 0]; internalField uniform {mu/rho*nu_t_ratio:.15g};
boundaryField {{ "(farfield|outlet)" {{ type calculated; value uniform {mu/rho*nu_t_ratio:.15g}; }}
 airfoil {{ type nutkWallFunction; value uniform 0; }} {empty} }}''', 'volScalarField')
    foam('0/alphat', f'''dimensions [1 -1 -1 0 0 0 0]; internalField uniform {mu*nu_t_ratio/.85:.15g};
boundaryField {{ "(farfield|outlet)" {{ type calculated; value uniform {mu*nu_t_ratio/.85:.15g}; }}
 airfoil {{ type compressible::alphatWallFunction; Prt 0.85; value uniform 0; }} {empty} }}''', 'volScalarField')
    functions = ['''force_airfoil { type forces; libs ("libforces.so"); patches (airfoil);
 rho rho; CofR (0.0762 0 0); writeControl timeStep; writeInterval 1; log false; }''',
        '''max_velocity { type volFieldValue; libs ("libfieldFunctionObjects.so"); cellZone all;
 operation maxMag; fields (U); writeFields false; writeControl timeStep; writeInterval 1; log true; }''',
        '''min_scalars { type volFieldValue; libs ("libfieldFunctionObjects.so"); cellZone all;
 operation min; fields (p T rho k omega); writeFields false; writeControl timeStep; writeInterval 1; log true; }''',
        '''max_scalars { type volFieldValue; libs ("libfieldFunctionObjects.so"); cellZone all;
 operation max; fields (p T rho k omega); writeFields false; writeControl timeStep; writeInterval 1; log false; }''',
        '''wall_resolution { type yPlus; libs ("libfieldFunctionObjects.so");
 writeControl timeStep; writeInterval 20; log false; }''']
    for patch in ('farfield', 'outlet'):
        functions.append(f'''mass_{patch} {{ type surfaceFieldValue; libs ("libfieldFunctionObjects.so");
 patch {patch}; operation sum; fields (phi); writeFields false; writeControl timeStep; writeInterval 1; log false; }}''')
    foam('system/controlDict', '''application foamRun; solver fluid;
startFrom startTime; startTime 0; stopAt endTime; endTime 100; deltaT 1;
writeControl timeStep; writeInterval 20; writeFormat ascii; writePrecision 12;
purgeWrite 0; runTimeModifiable true;
functions {\n'''+ '\n'.join(functions)+'\n}')
    foam('system/fvSchemes', '''ddtSchemes { default localEuler; }
gradSchemes { default cellLimited Gauss linear 1; }
divSchemes { default none; div(phi,U) Gauss upwind; div(phi,h) Gauss upwind;
 div(phi,K) Gauss upwind; div(phi,k) Gauss upwind; div(phi,omega) Gauss upwind;
 div(phid,p) Gauss upwind; div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear limited 0.5; }
interpolationSchemes { default linear; } snGradSchemes { default limited 0.5; }
wallDist { method meshWave; }''')
    foam('system/fvSolution', '''solvers {
 p { solver GAMG; smoother GaussSeidel; tolerance 1e-9; relTol 0.01; maxIter 500; }
 pFinal { $p; relTol 0; }
 rho { solver diagonal; } rhoFinal { $rho; }
 "(U|h|k|omega)" { solver PBiCGStab; preconditioner DILU; tolerance 1e-9; relTol 0.05; maxIter 500; }
 "(U|h|k|omega)Final" { solver PBiCGStab; preconditioner DILU; tolerance 1e-9; relTol 0; maxIter 500; }
}
PIMPLE { maxCo 0.2; maxDeltaT 0.001; rDeltaTSmoothingCoeff 0.1; rDeltaTDampingCoeff 0.2;
 transonic yes; nOuterCorrectors 2; nCorrectors 2; nNonOrthogonalCorrectors 1; }
relaxationFactors { equations { U 0.7; h 0.7; k 0.7; omega 0.7; } }''')
    (CASE/'benchmark.foam').touch()
    metadata = dict(scope='100-local-iteration compressible RANS startup/cost pilot, not accepted experimental validation',
                    source_NASA_study='https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html',
                    Mach_freestream=.729, alpha_deg=2.31, Reynolds_chord=6.5e6,
                    p_Pa=p, T_K=T, rho_kg_m3=rho, R_J_kg_K=R, gamma=gamma, Cp_J_kg_K=Cp,
                    speed_m_s=speed, velocity_m_s=U, chord_m=c, span_m=mesh['span_m'],
                    area_reference_m2=c*mesh['span_m'], mu_reference_Pas=mu,
                    Sutherland_As=As, Sutherland_Ts_K=Ts,
                    conductivity_law='OpenFOAM13 sutherlandTransport Eucken: kappa=mu*(1.32*Cv+1.77*R); no independent Pr keyword read',
                    molecular_Prandtl=Cp/(1.32*(Cp-R)+1.77*R),
                    viscosity_definition='Chosen to reproduce targetRe at the NASA referencep/T, with declared Sutherland temperature dependence; not a measured viscosity dataset.',
                    turbulence_I_ASSUMED=intensity, nu_t_over_nu_ASSUMED=nu_t_ratio,
                    k_freestream_m2_s2=k, omega_freestream_s_1=omega,
                    turbulence_model='OpenFOAM13 default kOmegaSST, fully turbulent; exact identity to legacy WIND SST/experiment transition not established',
                    wall_model='noSlip, adiabatic, kqRWallFunction/omegaWallFunction/nutkWallFunction; first point3.04micrometres, actual y+ pending',
                    iteration_target=100, counter_is_physical_time=False, own_loads_accepted=False,
                    Cp_experimental_points=103, experimental_Cp_error_reported_by_NASA=.0026,
                    physical_validation_accepted=False,
                    required_before_acceptance=['Mesh/topology verification, positivity/finiteness, actual localMach and wall resolution.',
                         'First-correction nonlinear residuals, lift/drag drift, mass/momentum closure, repeated field convergence.',
                         'Compare pressure at experimental taps and shock location; experimental precision alone is not a model acceptance tolerance.',
                         'Scheme, mesh, farfield, turbulence and transition sensitivity; no transfer of this benchmark to vehicle performance.'],
                    input_sha256={str(p.relative_to(CASE)):hashlib.sha256(p.read_bytes()).hexdigest()
                                  for folder in ('0', 'constant', 'system') for p in (CASE/folder).rglob('*') if p.is_file()})
    (CASE/'ENTRADAS.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps({k:metadata[k] for k in ('Mach_freestream','alpha_deg','Reynolds_chord','p_Pa','T_K','speed_m_s','mu_reference_Pas')}, indent=2))


if __name__ == '__main__':
    main()
