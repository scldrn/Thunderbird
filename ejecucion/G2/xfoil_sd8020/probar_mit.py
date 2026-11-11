"""Contrast MIT 6.996 build against failed packaged-XFOIL startup tests."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json

from comparar_arranques import CASES, call
from prueba_inicial import COMMANDS

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IMAGE='sha256:54f41a5d5e16486edb4c92ebce9bb9fc2ec8108dbd3fed9f9b917886c8b9bdf3'
CONTAINER='codex-aero-xfoil-mit-smoke-r1'
BINARY='/opt/xfoil-source/Xfoil/bin/xfoil'


def main():
    out=HERE/'mit_smoke_r1';assert not out.exists();out.mkdir()
    geometry=ROOT/'fuentes/uiuc/sd8020.dat'
    cases=dict(CASES,sd8020_viscoso=COMMANDS)
    report=dict(scope='MIT source smoke test; compiler compatibility flag and no FPE traps, not a physically accepted polar',
        image_id=IMAGE,geometry_sha256=hashlib.sha256(geometry.read_bytes()).hexdigest(),
        source_sha256='0feb71b58070d8514d830fcb0b609a10a11399d362493d7b9bbfb7343dff3f23',
        compiler_flags='-O -g -fdefault-real-8 -fallow-argument-mismatch; CHK empty',
        packaged_fpe_traps_not_used=True, physical_acceptance=False, cases={},
        started_UTC=datetime.now(timezone.utc).isoformat(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier
        info=call('exec',CONTAINER,'sh','-c',f'sha256sum {BINARY}; gfortran --version | head -1; cat /opt/xfoil-source/SHA256SUMS')
        report['binary_and_source_identification']=info.stdout.strip()
        call('cp',str(geometry),CONTAINER+':/tmp/sd8020.dat')
        for name,commands in cases.items():
            (out/(name+'_comandos.txt')).write_text(commands)
            process=call('exec','-i',CONTAINER,'sh','-c','ulimit -c 0; cd /tmp; '+BINARY,
                         input=commands,timeout=120,check=False)
            (out/(name+'.log')).write_text(process.stdout+'\nSTDERR:\n'+process.stderr)
            report['cases'][name]=dict(exit_code=process.returncode,
                output_contains_CL=('CL =' in process.stdout),
                fpe_signal_reported='Floating-point exception' in process.stderr,
                commands_sha256=hashlib.sha256(commands.encode()).hexdigest())
        copied=call('cp',CONTAINER+':/tmp/polar.txt',str(out/'polar.txt'),check=False)
        report['viscous_polar_copied']=copied.returncode==0
        if copied.returncode==0:report['polar_sha256']=hashlib.sha256((out/'polar.txt').read_bytes()).hexdigest()
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'EJECUCION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
