"""Preflight and short steady compressible diagnostic; counters are iterations."""
from pathlib import Path
import argparse,subprocess,json,re,time,math
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--case',default='avance_A_compresible_600kmh_diag');p.add_argument('--container',default='codex-aero-avance-compresible-600-v1');a=p.parse_args()
case=ROOT/a.case;container=a.container;meta=json.loads((case/'compressible_assumptions.json').read_text())
if (case/'log.preflight').exists() or (case/'log.foamRun').exists():raise FileExistsError('Preserve existing execution')
def state(**kwargs):
 (case/'run_state.json').write_text(json.dumps(dict(container=container,physical_loads_accepted=False,**kwargs),indent=2))
def run(command,**kwargs):
 return subprocess.run(['docker','exec','--workdir','/case',container,'bash','-c','source /opt/openfoam13/etc/bashrc\n'+command],**kwargs)
subprocess.run(['docker','create','--name',container,'--cpus=2','--memory=4g','--network=none','--workdir','/case','codex-aero-openfoam:13','sleep','infinity'],check=True)
subprocess.run(['docker','start',container],check=True)
subprocess.run(['docker','cp',str(case.resolve())+'/.',container+':/case'],check=True)
try:
 state(stage='preflight_running')
 with (case/'log.dictionary_check').open('w') as log:
  dictionary_check=run('foamDictionary system/fvSolution',stdout=log,stderr=subprocess.STDOUT)
 if dictionary_check.returncode:
  state(stage='dictionary_check_failed',exit_code=dictionary_check.returncode);raise RuntimeError('Dictionary check failed; no flow launched')
 with (case/'log.preflight').open('w') as log:pre=run('foamPostProcess -solver fluid -time 0',stdout=log,stderr=subprocess.STDOUT)
 if pre.returncode or '\nEnd\n' not in (case/'log.preflight').read_text():
  state(stage='preflight_failed',exit_code=pre.returncode);raise RuntimeError('Preflight failed; flow was not launched')
 physical=meta['time_counter_is_physical_seconds']
 target=meta['target_physical_time_s'] if physical else meta['target_steady_iterations']
 counter_kind=meta.get('counter_kind','physical_seconds' if physical else 'steady_iterations')
 state(stage='diagnostic_running',counter_kind=counter_kind,target_counter_value=target)
 stop_requested=False
 with (case/'log.foamRun').open('w') as log:
  job=subprocess.Popen(['docker','exec','--workdir','/case',container,'bash','-c','source /opt/openfoam13/etc/bashrc\nfoamRun'],stdout=log,stderr=subprocess.STDOUT)
  while job.poll() is None:
   s=(case/'log.foamRun').read_text();reasons=[]
   for field in ('p','T','rho'):
    matches=re.findall(r'min\(all\) of '+field+r' = ([\deE.+-]+)',s)
    if matches and (not math.isfinite(float(matches[-1])) or float(matches[-1])<=0):reasons.append('nonpositive/nonfinite '+field)
   matches=re.findall(r'maxMag\(all\) of U = ([\deE.+-]+)',s)
   if matches and (not math.isfinite(float(matches[-1])) or float(matches[-1])>1000):reasons.append('catastrophic velocity')
   if re.search(r'(?:maxMag|min|max)\(all\) of \w+ = (?:nan|inf)',s,re.I):reasons.append('nonfinite diagnostic')
   if reasons and not stop_requested:
    stop=run('foamDictionary system/controlDict -entry stopAt -set writeNow',capture_output=True,text=True)
    (case/'HEALTH_STOP_ATTEMPT.json').write_text(json.dumps(dict(reasons=reasons,returncode=stop.returncode),indent=2))
    stop_requested=stop.returncode==0
   time.sleep(1)
  code=job.wait()
 s=(case/'log.foamRun').read_text();times=[float(x) for x in re.findall(r'\nTime = ([\deE.+-]+)s',s)]
 listing=subprocess.run(['docker','exec',container,'ls','-1','/case'],capture_output=True,text=True,check=True)
 names=[]
 for name in listing.stdout.splitlines():
  try:
   if float(name)>0:names.append(name)
  except ValueError:pass
 if names:subprocess.run(['docker','cp',container+':/case/'+max(names,key=float),str(case)],check=True)
 if 'postProcessing' in listing.stdout.splitlines():
  subprocess.run(['docker','cp',container+':/case/postProcessing',str(case)],check=True)
 subprocess.run(['docker','cp',container+':/case/system/controlDict',str(case/'controlDict.final')],check=True)
 reached=bool(times and times[-1]>=target*(1-1e-8))
 state(stage='diagnostic_exited',exit_code=code,counter_kind=counter_kind,last_counter_value=times[-1] if times else None,target_counter_value=target,target_reached=reached,health_stop_requested=stop_requested,results_audited=False)
 if code or not reached:raise RuntimeError('Diagnostic failed or ended early; inspect records')
 print('Requested diagnostic counter target reached. No convergence or drag acceptance implied.')
finally:
 subprocess.run(['docker','stop','-t','1',container],check=False)
