"""Prepare the open-duct diagnostic after passing the mesh-only quality gate."""
from pathlib import Path
import shutil,json,hashlib
ROOT=Path(__file__).resolve().parent
case=ROOT/'salida_exterior_X35_Y-35_h0.006';src=ROOT/'comparacion_Euler_reinicio_h0.006'
audit=json.loads((case/'OPENFOAM_MESH_AUDIT.json').read_text())
if not audit['mesh_ok']:raise ValueError('Mesh gate not passed')
if (case/'0').exists():raise FileExistsError('Preserve any prepared/initialized fields')
def foam(path,body,cls='dictionary'):
 p=case/path;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text('FoamFile\n{version 2.0; format ascii; class '+cls+'; object '+p.name+';}\n'+body+'\n')
wall='"(walls|vane.*)"'
for name in ('physicalProperties','momentumTransport'):shutil.copy2(src/'constant'/name,case/'constant'/name)
foam('0/U',f'dimensions [0 1 -1 0 0 0 0]; internalField uniform (0 0 0); boundaryField {{ inlet {{type fixedValue; value uniform (0 0 -40);}} farfield {{type pressureInletOutletVelocity; inletValue uniform (0 0 0); value uniform (0 0 0);}} {wall} {{type noSlip;}} }}','volVectorField')
foam('0/p',f'dimensions [0 2 -2 0 0 0 0]; internalField uniform 0; boundaryField {{inlet {{type zeroGradient;}} farfield {{type fixedValue; value uniform 0;}} {wall} {{type zeroGradient;}} }}','volScalarField')
for name,dim,inlet,ambient,walltype in [('k','[0 2 -2 0 0 0 0]',6,1e-6,'kqRWallFunction'),('omega','[0 0 -1 0 0 0 0]',894.4271909999,10,'omegaWallFunction'),('nut','[0 2 -1 0 0 0 0]',0,0,'nutkWallFunction')]:
 ib=f'type fixedValue; value uniform {inlet};' if name!='nut' else 'type calculated; value uniform 0;'
 fb=f'type inletOutlet; inletValue uniform {ambient}; value uniform {ambient};' if name!='nut' else 'type calculated; value uniform 0;'
 foam('0/'+name,f'dimensions {dim}; internalField uniform {ambient}; boundaryField {{inlet {{{ib}}} farfield {{{fb}}} {wall} {{type {walltype}; value uniform {ambient};}} }}','volScalarField')
shutil.copytree(case/'0',case/'uniform_initial_inputs')
shutil.copy2(src/'system/fvSchemes',case/'system/fvSchemes')
s=(src/'system/fvSolution').read_text().replace('solvers\n{','solvers\n{\n Phi {solver GAMG; tolerance 1e-10; relTol 0; smoother GaussSeidel;}')
s+='\npotentialFlow {nNonOrthogonalCorrectors 5;}\n'
(case/'system/fvSolution').write_text(s)
functions=[]
for row,z in [('X',-.012),('Y',-.040)]:
 for j,offset in enumerate([-.022,0,.022]):
  center=[0,offset,z] if row=='X' else [offset,0,z];name=f'vane{row}{j}'
  functions.append(f'force_{name} {{type forces; libs ("libforces.so"); patches ({name}); rho rhoInf; rhoInf 1.225; CofR ({" ".join(map(str,center))}); writeControl timeStep; writeInterval 1;}}')
for name,patches in [('walls','walls'),('all_solids','walls vane.*'),('all_boundary','walls vane.* inlet farfield')]:
 functions.append(f'force_{name} {{type forces; libs ("libforces.so"); patches ({patches.replace("vane.*",chr(34)+"vane.*"+chr(34))}); rho rhoInf; rhoInf 1.225; CofR (0 0 0); writeControl timeStep; writeInterval 1;}}')
for patch in ('inlet','farfield'):
 functions.append(f'flow_{patch} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch {patch}; operation sum; writeFields false; fields (phi); writeControl timeStep; writeInterval 1;}}')
 functions.append(f'momentum_flux_{patch} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch {patch}; operation sum; weightField phi; writeFields false; fields (U); writeControl timeStep; writeInterval 1;}}')
functions.extend([
 'volume_velocity {type volFieldValue; libs ("libfieldFunctionObjects.so"); cellZone all; operation volIntegrate; writeFields false; fields (U); writeControl timeStep; writeInterval 1;}',
 'maxVelocityDiagnostic {type volFieldValue; log true; libs ("libfieldFunctionObjects.so"); cellZone all; operation maxMag; writeFields false; fields (U); writeControl timeStep; writeInterval 10;}',
 'minScalarsDiagnostic {type volFieldValue; log true; libs ("libfieldFunctionObjects.so"); cellZone all; operation min; writeFields false; fields (p k omega); writeControl timeStep; writeInterval 10;}'])
foam('system/controlDict','application foamRun; solver incompressibleFluid; startFrom startTime; startTime 0; stopAt endTime; endTime 0.00025; deltaT 1e-7; writeControl adjustableRunTime; writeInterval 0.00005; purgeWrite 3; writeFormat ascii; writePrecision 10; timePrecision 12; runTimeModifiable true; adjustTimeStep yes; maxCo 0.3; maxDeltaT 1e-5;\nfunctions {\n'+'\n'.join(functions)+'\n}')
meta=dict(end_time_s=.00025,flow_through_time_s=.145/40,discard_before_s=.01,initial_physical_age_s=0,
          initial_dt=1e-7,maxCo=.3,maxDeltaT=1e-5,time_scheme='Euler',momentum_advection='Gauss upwind',outer_correctors=2,
          rho_kg_m3=1.225,inlet_velocity_m_s=[0,0,-40],inlet_k_m2_s2=6,inlet_omega_s1=894.4271909999,
          ambient_k_m2_s2=1e-6,ambient_omega_s1=10,initialization='Potential-flow initialization pending; not developed viscous flow',
          purpose='Short startup stability diagnostic with exterior air, not a statistical load run',
          comparison_isolated_parameter=False,
          changes_from_old_channel=['exterior air and farfield boundaries','4 mm sleeve with exterior surfaces and lip','different mesh','potential initial field instead of old underdeveloped viscous fields','ambient turbulence assumptions'],
          limits=['not selected full CAD','no rotor, motor, shafts, hull or external flight velocity','incompressible model','no demonstrated yPlus or prism layers','domain/mesh/timestep/turbulence sensitivity unverified','no physical loads accepted'])
meta['configuration_sha256']={str(p.relative_to(case)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (case/'system').iterdir() if p.is_file()}
(case/'transient_assumptions.json').write_text(json.dumps(meta,indent=2));print(case)
