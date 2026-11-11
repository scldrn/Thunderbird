"""Run a separate, headless XFOIL smoke test on the identified SD8020 profile."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOCKER = '/Users/sam/.docker/bin/docker'
IMAGE = 'sha256:13cbe27aaddde9b40c9250256c4c1eaa5c15a61c03f746169a4357a606479b01'
CONTAINER = 'codex-aero-xfoil-sd8020-smoke-r1'
COMMANDS = '''PLOP
G

LOAD /tmp/sd8020.dat
PANE
OPER
VISC 61400
MACH 0
ITER 200
PACC
/tmp/polar.txt

ALFA 0
ALFA 2
ALFA 4
PACC

QUIT
'''


def call(*args, check=True, **kwargs):
    return subprocess.run([DOCKER, *args], text=True, capture_output=True, check=check, **kwargs)


def main():
    output = HERE/'smoke_r1'
    assert not output.exists()
    output.mkdir()
    geometry = ROOT/'fuentes/uiuc/sd8020.dat'
    (output/'comandos.txt').write_text(COMMANDS)
    container_id = None
    report = dict(scope='Headless smoke test, not a validation or accepted polar', image_id=IMAGE,
        source_geometry_sha256=hashlib.sha256(geometry.read_bytes()).hexdigest(),
        input_commands_sha256=hashlib.sha256(COMMANDS.encode()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        expected_package_version='6.99.dfsg+1-3', physical_acceptance=False,
        created_UTC=datetime.now(timezone.utc).isoformat())
    try:
        container_id = call('run','-d','--name',CONTAINER,'--network','none',
                            '--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=container_id
        info = call('exec',CONTAINER,'sh','-c',
            'dpkg-query -W -f="${Version}\\n" xfoil; sha256sum /usr/bin/xfoil; uname -m')
        report['binary_identification']=info.stdout.strip()
        call('cp',str(geometry),CONTAINER+':/tmp/sd8020.dat')
        result=call('exec','-i',CONTAINER,'sh','-c','cd /tmp && xfoil',
                    input=COMMANDS,timeout=120,check=False)
        (output/'xfoil.log').write_text(result.stdout+'\nSTDERR:\n'+result.stderr)
        report['solver_exit_code']=result.returncode
        copy=call('cp',CONTAINER+':/tmp/polar.txt',str(output/'polar.txt'),check=False)
        report['polar_copy_exit_code']=copy.returncode
        if copy.returncode == 0:
            report['polar_sha256']=hashlib.sha256((output/'polar.txt').read_bytes()).hexdigest()
        report['smoke_execution_complete']=result.returncode == 0 and copy.returncode == 0
    except Exception as exc:
        report['error']=repr(exc)
        raise
    finally:
        if container_id:
            stop=call('stop',CONTAINER,check=False)
            report['stop_exit_code']=stop.returncode
        (output/'EJECUCION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
