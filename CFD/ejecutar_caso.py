"""Prepare/check/run one prototype case in task-scoped OpenFOAM container."""
from pathlib import Path
import sys,subprocess,re,json
ROOT=Path(__file__).resolve().parent;name=sys.argv[1] if len(sys.argv)>1 else 'conducto_X0_Y0_h0.006';case=ROOT/name;assert (case/'fluid.msh').exists()
container='codex-aero-'+re.sub('[^a-zA-Z0-9_.-]','-',name)
subprocess.run(['docker','create','--name',container,'--cpus=2','--memory=4g','--network=none','--workdir','/case','codex-aero-openfoam:13','sleep','infinity'],check=True)
subprocess.run(['docker','start',container],check=True)
subprocess.run(['docker','cp',str(case)+ '/.',container+':/case'],check=True)
base=['docker','exec','--workdir','/case',container,'bash','-c']
def run(command,log):
 with (case/log).open('w') as f:
  sol=subprocess.run(base+['source /opt/openfoam13/etc/bashrc\n'+command],stdout=f,stderr=subprocess.STDOUT)
 if sol.returncode:raise RuntimeError(f'{command}: exit {sol.returncode}; see {case/log}')
run('gmshToFoam fluid.msh','log.gmshToFoam')
subprocess.run(['docker','cp',container+':/case/constant',str(case)],check=True)
p=case/'constant/polyMesh/boundary';s=p.read_text();s=re.sub(r'(\b(?:walls|vane\w+)\s*\{\s*type\s+)patch;',r'\1wall;',s);p.write_text(s)
subprocess.run(['docker','cp',str(p),container+':/case/constant/polyMesh/boundary'],check=True)
run('checkMesh -allGeometry -allTopology','log.checkMesh')
log=(case/'log.checkMesh').read_text();assert 'Mesh OK.' in log,'Mesh quality gate failed; inspect log.checkMesh before running'
(case/'run_state.json').write_text(json.dumps(dict(stage='solver_starting',mesh_quality='Mesh OK',note='Use live process/container, not this file alone, to infer active execution.'),indent=2))
run('foamRun','log.foamRun')
subprocess.run(['docker','cp',container+':/case/.',str(case)],check=True)
subprocess.run(['docker','stop',container],check=True)
(case/'run_state.json').write_text(json.dumps(dict(stage='solver_process_exited_successfully',note='Convergence, mass balance, forces, yPlus and mesh/domain sensitivity not yet audited.'),indent=2));print('Solver process completed; audit results before interpreting physics.')
