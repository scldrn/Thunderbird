"""Prepare an isolated saved-field postprocessing case; never alter live case."""
from pathlib import Path
import shutil,json

ROOT=Path(__file__).resolve().parent
source=ROOT/'comparacion_Euler_reinicio_h0.006'
target=ROOT/'auditoria_reaccion_Euler_t0.0005'
if target.exists():raise FileExistsError(target)
target.mkdir()
for name in ('constant','system','0'):
    shutil.copytree(source/name,target/name)
patches=['vaneX0','vaneX1','vaneX2','vaneY0','vaneY1','vaneY2','walls']
groups={name:[name] for name in patches}
groups.update(vanes=patches[:-1],all_solid=patches)
functions=[]
for name,group in groups.items():
    functions.append(f'load_{name} {{type forces; libs ("libforces.so"); patches ({" ".join(group)}); rho rhoInf; rhoInf 1.225; CofR (0 0 0); writeControl timeStep; writeInterval 1;}}')
(target/'system/controlDict').write_text('FoamFile\n{version 2.0; format ascii; class dictionary; object controlDict;}\napplication foamRun; solver incompressibleFluid; startFrom startTime; startTime 0; stopAt endTime; endTime 0.0005; deltaT 1e-6; writeControl timeStep; writeInterval 1;\nfunctions {\n'+'\n'.join(functions)+'\n}\n')
(target/'AUDIT_PURPOSE.json').write_text(json.dumps(dict(source_case=str(source),snapshot_time_s=.0005,source_initial_age_s=.001,purpose='Saved-field local solid reaction partition; not net thruster force or accepted physical loads.',origin_m=[0,0,0],rho_kg_m3=1.225,missing=['rotor','external body','inlet and outlet momentum/pressure control-volume audit','time development and numerical sensitivity']),indent=2))
print(target)
