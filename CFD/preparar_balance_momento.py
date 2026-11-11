"""Offline momentum-integral audit, kept separate from both live solvers."""
from pathlib import Path
import shutil,json
ROOT=Path(__file__).resolve().parent
source=ROOT/'comparacion_Euler_reinicio_h0.006'
target=ROOT/'auditoria_momento_Euler_0_0.0005'
if target.exists():raise FileExistsError(target)
target.mkdir()
for name in ('constant','system','0'):shutil.copytree(source/name,target/name)
functions=[]
patches=['vaneX0','vaneX1','vaneX2','vaneY0','vaneY1','vaneY2','walls','inlet','outlet']
for name,group in [('all_boundary',patches),('solids',patches[:-2]),('open_ends',patches[-2:])]:
 functions.append(f'traction_{name} {{type forces; libs ("libforces.so"); patches ({" ".join(group)}); rho rhoInf; rhoInf 1.225; CofR (0 0 0); writeControl timeStep; writeInterval 1;}}')
functions.append('volume_velocity {type volFieldValue; libs ("libfieldFunctionObjects.so"); cellZone all; operation volIntegrate; writeFields false; fields (U); writeControl timeStep; writeInterval 1;}')
for patch in ('inlet','outlet'):
 functions.append(f'momentum_flux_{patch} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch {patch}; operation sum; weightField phi; writeFields false; fields (U); writeControl timeStep; writeInterval 1;}}')
 functions.append(f'flow_{patch} {{type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); patch {patch}; operation sum; writeFields false; fields (phi); writeControl timeStep; writeInterval 1;}}')
(target/'system/controlDict').write_text('FoamFile\n{version 2.0; format ascii; class dictionary; object controlDict;}\napplication foamRun; solver incompressibleFluid; startFrom startTime; startTime 0; stopAt endTime; endTime 0.0005; deltaT 1e-6; writeControl timeStep; writeInterval 1;\nfunctions {\n'+'\n'.join(functions)+'\n}\n')
(target/'PURPOSE.json').write_text(json.dumps(dict(purpose='Saved-field integral momentum audit, not exact discrete residual or installed force calibration',rho_kg_m3=1.225,requested_times_s=[0,.00025,.0005],equation='d(rho*integral U dV)/dt + rho*sum_open(phi U) + boundary_force_opposite_fluid = 0',limits=['coarse snapshot temporal quadrature','boundary viscous traction from reconstructed model','no rotor or external body']),indent=2))
print(target)
