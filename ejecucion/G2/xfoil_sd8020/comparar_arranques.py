"""Isolate XFOIL start-up failures using separate inviscid reference runs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DOCKER='/Users/sam/.docker/bin/docker'
IMAGE='sha256:13cbe27aaddde9b40c9250256c4c1eaa5c15a61c03f746169a4357a606479b01'
CONTAINER='codex-aero-xfoil-startup-r2'
PREFACE='PLOP\nG\n\n'
SUFFIX='OPER\nALFA 2\n\nQUIT\n'
CASES={
    'naca0012':PREFACE+'NACA 0012\n'+SUFFIX,
    'sd8020_original':PREFACE+'LOAD /tmp/sd8020.dat\n'+SUFFIX,
    'sd8020_pane':PREFACE+'LOAD /tmp/sd8020.dat\nPANE\n'+SUFFIX,
}


def call(*args,check=True,**kwargs):
    return subprocess.run([DOCKER,*args],text=True,capture_output=True,check=check,**kwargs)


def main():
    out=HERE/'arranque_r2'; assert not out.exists();out.mkdir()
    geometry=ROOT/'fuentes/uiuc/sd8020.dat'
    report=dict(scope='Independent inviscid startup diagnostics, not validation',image_id=IMAGE,
        geometry_sha256=hashlib.sha256(geometry.read_bytes()).hexdigest(),cases={},physical_acceptance=False,
        started_UTC=datetime.now(timezone.utc).isoformat(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier
        report['binary_identification']=call('exec',CONTAINER,'sh','-c','dpkg-query -W xfoil; sha256sum /usr/bin/xfoil; uname -m').stdout.strip()
        call('cp',str(geometry),CONTAINER+':/tmp/sd8020.dat')
        for name, commands in CASES.items():
            (out/(name+'_comandos.txt')).write_text(commands)
            process=call('exec','-i',CONTAINER,'sh','-c','ulimit -c 0; cd /tmp; xfoil',input=commands,timeout=60,check=False)
            (out/(name+'.log')).write_text(process.stdout+'\nSTDERR:\n'+process.stderr)
            report['cases'][name]=dict(exit_code=process.returncode,alpha_command_in_stdout=('a =  2.000' in process.stdout),
                fpe_signal_reported='Floating-point exception' in process.stderr,
                commands_sha256=hashlib.sha256(commands.encode()).hexdigest())
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'EJECUCION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
