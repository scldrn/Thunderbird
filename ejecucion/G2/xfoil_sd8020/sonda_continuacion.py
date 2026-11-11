"""Compare a warm-start angle sequence with independent XFOIL points."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import math

from comparar_arranques import call
from comparar_uiuc import polar_rows

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IMAGE='sha256:54f41a5d5e16486edb4c92ebce9bb9fc2ec8108dbd3fed9f9b917886c8b9bdf3'
BINARY='/opt/xfoil-source/Xfoil/bin/xfoil'
CONTAINER='codex-aero-xfoil-continuacion-r1'
COMMANDS='''PLOP
G

LOAD /tmp/sd8020.dat
PANE
OPER
VISC 61400
MACH 0
ITER 200
PACC
/tmp/secuencia.txt

ALFA 0
ALFA 1.17
ALFA 2.72
ALFA 5.89
PACC

QUIT
'''


def main():
    out=HERE/'continuacion_r1';assert not out.exists();out.mkdir()
    geometry=ROOT/'fuentes/uiuc/sd8020.dat';(out/'comandos.txt').write_text(COMMANDS)
    report=dict(scope='Warm-start history sensitivity diagnostic; no physical acceptance',image_id=IMAGE,
        geometry_sha256=hashlib.sha256(geometry.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        created_UTC=datetime.now(timezone.utc).isoformat(),physical_fan_acceptance=False,
        same_sequence_is_not_independent_cases=True,FPE_traps_disabled_in_MIT_default_build=True)
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier;call('cp',str(geometry),CONTAINER+':/tmp/sd8020.dat')
        proc=call('exec','-i',CONTAINER,'sh','-c','ulimit -c 0; cd /tmp; '+BINARY,
                  input=COMMANDS,timeout=120,check=False)
        (out/'xfoil.log').write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr)
        report['exit_code']=proc.returncode
        result=call('cp',CONTAINER+':/tmp/secuencia.txt',str(out/'polar.txt'),check=False)
        report['polar_copy_exit_code']=result.returncode
        if result.returncode==0:
            rows=polar_rows((out/'polar.txt').read_text())
            report['rows']=[dict(alpha_deg=r[0],cl=r[1],cd=r[2]) for r in rows if all(math.isfinite(v) for v in r)]
            report['polar_sha256']=hashlib.sha256((out/'polar.txt').read_bytes()).hexdigest()
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'RESULTADOS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
