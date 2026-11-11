"""Convert/check a new Gmsh mesh in an isolated container; never run flow."""
from pathlib import Path
import argparse,subprocess,re,json
p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('--container',required=True);p.add_argument('--wall-pattern',default=r'walls|vane\w+');a=p.parse_args()
case=a.case.resolve();container=a.container
if (case/'log.gmshToFoam').exists():raise FileExistsError('Preserve previous conversion logs')
(case/'system').mkdir(exist_ok=True)
(case/'system/controlDict').write_text('FoamFile\n{version 2.0; format ascii; class dictionary; object controlDict;}\napplication foamRun; solver incompressibleFluid; startFrom startTime; startTime 0; stopAt endTime; endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;\n')
subprocess.run(['docker','create','--name',container,'--cpus=1','--memory=3g','--network=none','--workdir','/case','codex-aero-openfoam:13','sleep','infinity'],check=True)
subprocess.run(['docker','start',container],check=True)
subprocess.run(['docker','cp',str(case)+'/.',container+':/case'],check=True)
def run(command,log):
 with (case/log).open('w') as f:
  result=subprocess.run(['docker','exec','--workdir','/case',container,'bash','-c','source /opt/openfoam13/etc/bashrc\n'+command],stdout=f,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError(f'{command} failed: see {log}')
try:
 run('gmshToFoam fluid.msh','log.gmshToFoam')
 subprocess.run(['docker','cp',container+':/case/constant',str(case)],check=True)
 path=case/'constant/polyMesh/boundary';s=path.read_text()
 s=re.sub(r'(\b(?:'+a.wall_pattern+r')\s*\{\s*type\s+)patch;',r'\1wall;',s);path.write_text(s)
 subprocess.run(['docker','cp',str(path),container+':/case/constant/polyMesh/boundary'],check=True)
 run('checkMesh -allGeometry -allTopology','log.checkMesh')
 log=(case/'log.checkMesh').read_text()
 result=dict(mesh_ok='Mesh OK.' in log,flow_started=False,physical_loads_accepted=False,container=container,
             note='Mesh quality gate only; no wall resolution, mesh/domain sensitivity or flow validation.')
 (case/'OPENFOAM_MESH_AUDIT.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result))
finally:
 subprocess.run(['docker','stop','-t','1',container],check=False)
