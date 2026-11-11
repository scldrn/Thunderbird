from pathlib import Path
import argparse,subprocess,json,re
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--case',default='transitorio_X35_Y-35_h0.006')
parser.add_argument('--container',default='codex-aero-transitorio-A-v2')
args=parser.parse_args();case=(ROOT/args.case).resolve();container=args.container
if (case/'log.foamRun').exists():
 raise RuntimeError('Existing solver log: preserve the run; use an explicit new case for a new experiment.')
meta=json.loads((case/'transient_assumptions.json').read_text())
subprocess.run(['docker','create','--name',container,'--cpus=2','--memory=4g','--network=none','--workdir','/case','codex-aero-openfoam:13','sleep','infinity'],check=True)
subprocess.run(['docker','start',container],check=True);subprocess.run(['docker','cp',str(case)+'/.',container+':/case'],check=True)
(case/'run_state.json').write_text(json.dumps(dict(stage='solver_starting',container=container,note='Use live handle/container for status, not this file alone.'),indent=2))
with (case/'log.foamRun').open('w') as log:
 sol=subprocess.run(['docker','exec','--workdir','/case',container,'bash','-c','source /opt/openfoam13/etc/bashrc\nfoamRun'],stdout=log,stderr=subprocess.STDOUT)
logtext=(case/'log.foamRun').read_text()
times=[float(x) for x in re.findall(r'\nTime = ([\deE.+-]+)s',logtext)]
advanced=bool(times and max(times)>0)
if advanced:subprocess.run(['docker','cp',container+':/case/postProcessing',str(case)],check=True)
# Preserve the most recent written field as well as force histories, including a
# deliberately stopped diagnostic run. Container copy also works when stopped.
listing=subprocess.run(['docker','exec',container,'ls','-1','/case'],capture_output=True,text=True,check=True)
fieldnames=[]
for name in listing.stdout.splitlines():
 try:
  if float(name)>0:fieldnames.append(name)
 except ValueError:pass
if fieldnames:
 latest=max(fieldnames,key=float)
 subprocess.run(['docker','cp',container+':/case/'+latest,str(case)],check=True)
subprocess.run(['docker','cp',container+':/case/system/controlDict',str(case/'controlDict.final')],check=True)
subprocess.run(['docker','stop','-t','1',container],check=False)
reached_target=bool(times and times[-1]>=meta['end_time_s']*(1-1e-7))
(case/'run_state.json').write_text(json.dumps(dict(stage='solver_process_exited',exit_code=sol.returncode,last_physical_time_s=times[-1] if times else 0,target_physical_time_s=meta['end_time_s'],target_reached=reached_target,results_audited=False,container=container),indent=2))
if not advanced:raise RuntimeError('Process did not advance physical time; no simulation result.')
if sol.returncode:raise RuntimeError('Solver failed: inspect log.foamRun')
if not reached_target:raise RuntimeError('Stopped before requested physical time: run is incomplete regardless of exit code.')
print('Process finished. Audit physical-time sampling and force statistics before accepting results.')
