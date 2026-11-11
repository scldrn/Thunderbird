"""Watch the actual velocity diagnostic file, independently of log verbosity.

Companion to the timestep/log watchdog. Never restart the solver on failure to
observe it. A successful stop request is recorded; failed requests are retried.
"""
from pathlib import Path
import subprocess,json,time,math,os
ROOT=Path(__file__).resolve().parent
case=ROOT/'salida_exterior_X35_Y-35_h0.006';container='codex-aero-exterior-urans-v1'
(case/'WATCHDOG_FIELDS_PID.json').write_text(json.dumps(dict(pid=os.getpid(),container=container)))
while True:
 p=subprocess.run(['docker','inspect',container,'--format','{{json .State}}'],capture_output=True,text=True)
 if p.returncode:
  state=dict(observation_failed_retry_same_job=True,physical_loads_accepted=False)
 else:
  running=json.loads(p.stdout)['Running'];state=dict(container=container,running=running,physical_loads_accepted=False)
  if running:
   p=subprocess.run(['docker','exec',container,'tail','-n','1','/case/postProcessing/maxVelocityDiagnostic/0/volFieldValue.dat'],capture_output=True,text=True)
   values=p.stdout.split()
   if p.returncode==0 and len(values)==2 and not values[0].startswith('#'):
    try:t,u=map(float,values)
    except ValueError:state['diagnostic_parse_retry']=True
    else:
     state.update(diagnostic_time_s=t,max_velocity_m_s=u if math.isfinite(u) else None,nonfinite_velocity=not math.isfinite(u))
     if (not math.isfinite(u) or u>1000) and not (case/'WATCHDOG_STOP.json').exists():
      stop=subprocess.run(['docker','exec','--workdir','/case',container,'bash','-c','source /opt/openfoam13/etc/bashrc\nfoamDictionary system/controlDict -entry stopAt -set writeNow'],capture_output=True,text=True)
      report=dict(reason='Nonfinite or >1000 m/s velocity in diagnostic field file',stop_returncode=stop.returncode,stdout=stop.stdout,stderr=stop.stderr,physical_loads_accepted=False)
      (case/('WATCHDOG_STOP.json' if stop.returncode==0 else 'WATCHDOG_FIELDS_STOP_FAILED_RETRY.json')).write_text(json.dumps(report,indent=2))
   else:state['diagnostic_read_retry']=True
 (case/'WATCHDOG_FIELDS_STATE.json').write_text(json.dumps(state,indent=2,allow_nan=False));print(json.dumps(state),flush=True)
 if state.get('running') is False:break
 time.sleep(20)
