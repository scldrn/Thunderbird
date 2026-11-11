"""Read actual Docker state/process/log; a snapshot never proves future liveness."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import re
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--case',type=Path,required=True)
parser.add_argument('--container',required=True)
a=parser.parse_args();case=a.case.resolve();docker='/Users/sam/.docker/bin/docker'
def call(*args):
    return subprocess.run([docker,*args],capture_output=True,text=True)
r=call('inspect',a.container)
assert r.returncode==0,r.stderr
state=json.loads(r.stdout)[0]
top=call('top',a.container,'-eo','pid,etime,args')
processes=top.stdout.splitlines()[1:] if top.returncode==0 else []
live=any(re.match(r'^\s*\d+\s+\S+\s+(?:\S*/)?foamRun(?:\s+-parallel)?\s*$',line) for line in processes)
record=dict(observed_UTC=datetime.now(timezone.utc).isoformat(),container=a.container,
    container_id=state['Id'],container_status=state['State']['Status'],paused=state['State']['Paused'],
    foamRun_process_verified_live=live,observed_processes=processes,
    snapshot_does_not_prove_future_liveness=True,physical_validation_accepted=False)
if live:
    r=call('exec',a.container,'cat','/case/log.foamRun')
    assert r.returncode==0
    blocks=re.split(r'\nTime = ',r.stdout)[1:]
    complete=[float(re.match(r'([\deE.+-]+)',b)[1]) for b in blocks if re.match(r'([\deE.+-]+)',b) and 'ClockTime =' in b]
    record['last_completed_counter']=complete[-1] if complete else None
    speed=re.findall(r'maxMag\(all\) of U = ([\deE.+-]+)',r.stdout)
    record['last_reported_max_speed_m_s']=float(speed[-1]) if speed else None
else:
    record['runner_state_if_available']=json.loads((case/'EJECUCION.json').read_text()) if (case/'EJECUCION.json').exists() else None
(case/'OBSERVACION_PROCESO.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
