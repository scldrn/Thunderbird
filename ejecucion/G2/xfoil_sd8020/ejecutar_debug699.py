"""Capture symbolized stack traces from the Ubuntu 6.99 source build."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json

from comparar_arranques import CASES,call

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IMAGE='sha256:41c3413d7d962c8b6e1d09072539e99561ecbc2413a3365d65ba3298e300e0e3'
BINARY='/opt/xfoil-ubuntu-source/xfoil-6.99.dfsg+1/bin/xfoil'
CONTAINER='codex-aero-xfoil-debug699-r1'


def main():
    out=HERE/'debug699_r1';assert not out.exists();out.mkdir()
    report=dict(scope='Debug build failure localization, not numerical or physical validation',
        image_id=IMAGE,optimization='O0 instead of packaged build optimization',
        fpe_and_initialization_flags='-fbounds-check -finit-real=inf -ffpe-trap=invalid,zero -fdefault-real-8',
        source_archive_sha256='f5ece350981f35f7b5b4cef540c921ffad877b0942591efb88bad76cc08b597a',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        created_UTC=datetime.now(timezone.utc).isoformat(),physical_acceptance=False,cases={})
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier
        call('cp',str(ROOT/'fuentes/uiuc/sd8020.dat'),CONTAINER+':/tmp/sd8020.dat')
        report['binary_sha256']=call('exec',CONTAINER,'sha256sum',BINARY).stdout.split()[0]
        for name in ('naca0012','sd8020_original'):
            commands=CASES[name];(out/(name+'_comandos.txt')).write_text(commands)
            proc=call('exec','-i',CONTAINER,'sh','-c','ulimit -c 0; cd /tmp; '+BINARY,
                      input=commands,timeout=90,check=False)
            (out/(name+'.log')).write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr)
            report['cases'][name]=dict(exit_code=proc.returncode,
                fpe_reported='Floating-point exception' in proc.stderr,
                source_lines_in_backtrace=('../src/' in proc.stderr),
                log_sha256=hashlib.sha256((out/(name+'.log')).read_bytes()).hexdigest())
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'EJECUCION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
