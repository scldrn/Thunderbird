"""Prepare a short steady-iteration compressible slip-wall pressure diagnostic.

No rotor, no installed doors; no turbulent skin-friction prediction. The steady
iteration counter is not elapsed physical flight time.
"""
from pathlib import Path
import argparse,json,math,shutil,hashlib
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--speed-kmh',type=float,default=600);p.add_argument('--iterations',type=int,default=30);a=p.parse_args()
if not 0<a.speed_kmh<=1000 or a.iterations<1:raise ValueError('Invalid diagnostic settings')
mesh=ROOT/'avance_A_cerrada_h0.008';case=ROOT/f'avance_A_compresible_{a.speed_kmh:g}kmh_diag'
if case.exists():raise FileExistsError(case)
assert json.loads((mesh/'OPENFOAM_MESH_AUDIT.json').read_text())['mesh_ok']
case.mkdir();shutil.copytree(mesh/'constant/polyMesh',case/'constant/polyMesh')
def foam(path,body,cls='dictionary'):
 q=case/path;q.parent.mkdir(parents=True,exist_ok=True)
 q.write_text('FoamFile\n{version 2.0; format ascii; class '+cls+'; object '+q.name+';}\n'+body+'\n')
U=a.speed_kmh/3.6;T=288.15;P=101325.;R=287.05287;gamma=1.4;Cp=gamma*R/(gamma-1);W=8314.46261815324/R
far='"(inlet|outlet|farfield)"'
foam('0/U',f'dimensions [0 1 -1 0 0 0 0]; internalField uniform ({U:.14g} 0 0); boundaryField {{ {far} {{type freestreamVelocity; freestreamValue uniform ({U:.14g} 0 0); value uniform ({U:.14g} 0 0);}} hull {{type slip;}} }}','volVectorField')
foam('0/p',f'dimensions [1 -1 -2 0 0 0 0]; internalField uniform {P}; boundaryField {{ {far} {{type freestreamPressure; freestreamValue uniform {P};}} hull {{type zeroGradient;}} }}','volScalarField')
foam('0/T',f'dimensions [0 0 0 1 0 0 0]; internalField uniform {T}; boundaryField {{ {far} {{type inletOutlet; inletValue uniform {T}; value uniform {T};}} hull {{type zeroGradient;}} }}','volScalarField')
foam('constant/physicalProperties',f'thermoType {{type hePsiThermo; mixture pureMixture; transport const; thermo hConst; equationOfState perfectGas; specie specie; energy sensibleEnthalpy;}}\nmixture {{specie {{molWeight {W:.14g};}} thermodynamics {{Cp {Cp:.14g}; hf 0;}} transport {{mu 1.7894e-5; Pr 0.72;}}}}')
foam('constant/momentumTransport','simulationType laminar;')
foam('system/fvSchemes','ddtSchemes {default steadyState;}\ngradSchemes {default Gauss linear; grad(U) cellLimited Gauss linear 1;}\ndivSchemes {default none; div(phi,U) bounded Gauss upwind; div(phi,h) bounded Gauss upwind; div(phi,K) bounded Gauss upwind; div(phid,p) Gauss upwind; div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;}\nlaplacianSchemes {default Gauss linear corrected;} interpolationSchemes {default linear;} snGradSchemes {default corrected;} wallDist {method meshWave;}')
foam('system/fvSolution','solvers {p {solver GAMG; smoother GaussSeidel; tolerance 1e-8; relTol 0.01;} "(U|h)" {solver PBiCGStab; preconditioner DILU; tolerance 1e-9; relTol 0.05;}}\nPIMPLE {transonic yes; nNonOrthogonalCorrectors 1;}\nrelaxationFactors {fields {p 0.2; rho 0.1;} equations {U 0.5; h 0.5;}}')
functions=[
 f'force_hull {{type forces; libs ("libforces.so"); patches (hull); rho rho; pRef {P}; CofR (0 0 0); writeControl timeStep; writeInterval 1;}}',
 'maxVelocityDiagnostic {type volFieldValue; log true; libs ("libfieldFunctionObjects.so"); cellZone all; operation maxMag; writeFields false; fields (U); writeControl timeStep; writeInterval 1;}',
 'minScalarsDiagnostic {type volFieldValue; log true; libs ("libfieldFunctionObjects.so"); cellZone all; operation min; writeFields false; fields (p T rho); writeControl timeStep; writeInterval 1;}',
 'maxScalarsDiagnostic {type volFieldValue; log true; libs ("libfieldFunctionObjects.so"); cellZone all; operation max; writeFields false; fields (p T rho); writeControl timeStep; writeInterval 1;}']
for patch in ('inlet','outlet','farfield'):
 functions.append(f'mass_flux_{patch} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch {patch}; operation sum; writeFields false; fields (phi); writeControl timeStep; writeInterval 1;}}')
for operation in ('min','max'):
 functions.append(f'hull_pressure_{operation} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch hull; operation {operation}; writeFields false; fields (p); writeControl timeStep; writeInterval 1;}}')
foam('system/controlDict',f'application foamRun; solver fluid; startFrom startTime; startTime 0; stopAt endTime; endTime {a.iterations}; deltaT 1; writeControl timeStep; writeInterval 10; purgeWrite 3; writeFormat ascii; writePrecision 10; timePrecision 8; runTimeModifiable true;\nfunctions {{\n'+ '\n'.join(functions)+'\n}')
meta=dict(purpose='Compressible pressure/startup diagnostic with slip body, not total drag validation',speed_kmh=a.speed_kmh,velocity_m_s=U,freestream_Mach=U/math.sqrt(gamma*R*T),p_Pa=P,T_K=T,rho_kg_m3=P/(R*T),R_J_kgK=R,gamma=gamma,Cp_J_kgK=Cp,molar_mass_kg_kmol=W,dynamic_viscosity_Pas=1.7894e-5,Pr=.72,
          target_steady_iterations=a.iterations,time_counter_is_physical_seconds=False,slip_wall=True,momentum_model='laminar default Stokes; slip boundary, no turbulent skin-friction model',
          source_mesh_case=str(mesh.resolve()),mesh_geometry_scope=json.loads((mesh/'mesh_metadata.json').read_text())['geometry_scope'],reference_area_m2=json.loads((mesh/'mesh_metadata.json').read_text())['reference_area_m2'],
          source_basis='OpenFOAM Foundation13 installed fluid/aerofoilNACA0012Steady tutorial and isothermalFluid/correctPressure.C transonic branch',
          limits=['not converged by setup or fixed iteration count','no total viscous drag','no rotor/ports/installed doors','no mesh/domain or scheme independence','no experimental solver validation yet','no critical-Mach or drag-divergence result from one speed'])
meta['input_sha256']={str(f.relative_to(case)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ('0','system','constant') for f in (case/folder).iterdir() if f.is_file()}
(case/'compressible_assumptions.json').write_text(json.dumps(meta,indent=2));print(case)
