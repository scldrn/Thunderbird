"""Watch only the named paired jobs; stop orderly on gross numerical runaway.
Thresholds diagnose catastrophic invalid states; they do not accept accuracy.
An inspect failure is not a terminal state and never triggers a restart.
"""
from pathlib import Path
import json,re,time,subprocess,math,argparse
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--case');parser.add_argument('--container');args=parser.parse_args()
if bool(args.case)!=bool(args.container):parser.error('--case and --container must be specified together')
jobs=[(args.case,args.container)] if args.case else [('comparacion_Euler_reinicio_h0.006','codex-aero-pareado-euler-v1'),('comparacion_backward_reinicio_h0.006','codex-aero-pareado-backward-v1')]
output=ROOT/args.case/'WATCHDOG_STATE.json' if args.case else ROOT/'COMPARACION_TEMPORAL_VIGILANCIA.json'
def inspect(name):
    p=subprocess.run(['docker','inspect',name,'--format','{{json .State}}'],text=True,capture_output=True)
    return json.loads(p.stdout) if p.returncode==0 else None
while True:
    all_terminal=True;snapshot=[]
    for folder,container in jobs:
        c=ROOT/folder;state=inspect(container)
        if state is None:all_terminal=False;snapshot.append(dict(container=container,state='observation_failed_retry_same_job'));continue
        running=bool(state['Running']);all_terminal &= not running
        log=(c/'log.foamRun').read_text() if (c/'log.foamRun').exists() else ''
        dt=[float(x) for x in re.findall(r'deltaT = ([\deE.+-]+)',log)]
        velocity=[float(x) for x in re.findall(r'maxMag\(all\) of U = ([\deE.+-]+)',log)]
        reasons=[]
        if velocity and (not math.isfinite(velocity[-1]) or velocity[-1]>1000):reasons.append('max U exceeds 1000 m/s in incompressible 40 m/s inlet diagnostic')
        if dt and dt[-1]<1e-9 and dt[-1]<dt[0]/1000:reasons.append('timestep collapse below 1e-9 s and factor 1000')
        if re.search(r'maxMag\(all\) of U = (?:nan|inf)',log,re.I):reasons.append('non-finite velocity diagnostic')
        stopfile=c/'WATCHDOG_STOP.json'
        if reasons and running and not stopfile.exists():
            command=subprocess.run(['docker','exec','--workdir','/case',container,'bash','-c','source /opt/openfoam13/etc/bashrc; foamDictionary system/controlDict -entry stopAt -set writeNow'],capture_output=True,text=True)
            attempt=stopfile if command.returncode==0 else c/'WATCHDOG_STOP_FAILED_RETRY.json'
            attempt.write_text(json.dumps(dict(reasons=reasons,orderly_stop_request_returncode=command.returncode,stdout=command.stdout,stderr=command.stderr,physical_loads_accepted=False),indent=2))
        snapshot.append(dict(container=container,running=running,latest_deltaT_s=dt[-1] if dt else None,latest_max_velocity_ms=velocity[-1] if velocity else None,runaway_reasons=reasons))
    output.write_text(json.dumps(dict(jobs=snapshot,all_observed_terminal=all_terminal,not_an_accuracy_acceptance=True),indent=2))
    print(json.dumps(snapshot),flush=True)
    if all_terminal:break
    time.sleep(20)
