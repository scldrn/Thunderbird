"""Inspect the first headless XFOIL6.99 exception with debugger symbols."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json

from comparar_arranques import call

HERE=Path(__file__).resolve().parent
IMAGE='sha256:41c3413d7d962c8b6e1d09072539e99561ecbc2413a3365d65ba3298e300e0e3'
BINARY='/opt/xfoil-ubuntu-source/xfoil-6.99.dfsg+1/bin/xfoil'
CONTAINER='codex-aero-xfoil-gdb-r1'


def main():
    out=HERE/'gdb_ventana_r1';assert not out.exists();out.mkdir()
    commands=HERE/'debug699_r1/naca0012_comandos.txt'
    report=dict(scope='Debugger inspection of first headless failure; not a scientific validation',
        image_id=IMAGE,input_sha256=hashlib.sha256(commands.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        created_UTC=datetime.now(timezone.utc).isoformat(),physical_acceptance=False)
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier;call('cp',str(commands),CONTAINER+':/tmp/commands.txt')
        proc=call('exec',CONTAINER,'gdb','--batch','-ex','set pagination off','-ex','run < /tmp/commands.txt',
            '-ex','bt','-ex','frame 0','-ex','print g_scale','-ex','print gx_siz','-ex','print gy_siz',
            '--args',BINARY,timeout=90,check=False)
        (out/'gdb.log').write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr)
        report.update(gdb_exit_code=proc.returncode,signal_observed='SIGFPE' in proc.stdout,
            ptrace_denied='ptrace: Operation not permitted' in proc.stderr,
            aslr_disable_denied='Error disabling address space randomization: Operation not permitted' in proc.stderr,
            log_sha256=hashlib.sha256((out/'gdb.log').read_bytes()).hexdigest())
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'EJECUCION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
