"""Test Ubuntu's checked XFOIL binary with a virtual display, without source changes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json

from comparar_arranques import call

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IMAGE='sha256:cbf29dc7a179c4b20c46c90d9e54636912de665beb81cd8558c25bf6af33fbfe'
CONTAINER='codex-aero-xfoil-xvfb-smoke-r2'
CASES={
    'naca0012':'NACA 0012\nOPER\nPACC\n/tmp/naca_polar.txt\n\nALFA 2\nPACC\n\nQUIT\n',
    'sd8020_viscoso':'LOAD /tmp/sd8020.dat\nPANE\nOPER\nVISC 61400\nMACH 0\nITER 200\nPACC\n/tmp/sd_polar.txt\n\nALFA 0\nALFA 2\nALFA 4\nPACC\n\nQUIT\n',
}


def main():
    out=HERE/'xvfb_smoke_r2';assert not out.exists();out.mkdir()
    geometry=ROOT/'fuentes/uiuc/sd8020.dat'
    report=dict(scope='Virtual-display diagnostics, not physical validation',image_id=IMAGE,
        geometry_sha256=hashlib.sha256(geometry.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_or_binary_modified=False,packaged_FPE_checks_retained=True,physical_acceptance=False,
        created_UTC=datetime.now(timezone.utc).isoformat(),cases={})
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier
        report['binary_identification']=call('exec',CONTAINER,'sh','-c','dpkg-query -W xfoil; sha256sum /usr/bin/xfoil').stdout.strip()
        call('cp',str(geometry),CONTAINER+':/tmp/sd8020.dat')
        for name,commands in CASES.items():
            (out/(name+'_input.txt')).write_text(commands)
            proc=call('exec','-i',CONTAINER,'sh','-c','ulimit -c 0; cd /tmp; xvfb-run -a xfoil',input=commands,timeout=120,check=False)
            (out/(name+'.log')).write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr)
            target='/tmp/naca_polar.txt' if name=='naca0012' else '/tmp/sd_polar.txt'
            copy=call('cp',CONTAINER+':'+target,str(out/(name+'_polar.txt')),check=False)
            row=dict(exit_code=proc.returncode,polar_copy_exit_code=copy.returncode,
                fpe_signal_reported='Floating-point exception' in proc.stderr,
                convergence_warning_reported='Convergence failed' in proc.stdout)
            if copy.returncode==0:
                # Version 6.99 may have fewer than nine columns; preserve raw file first.
                row['polar_sha256']=hashlib.sha256((out/(name+'_polar.txt')).read_bytes()).hexdigest()
            report['cases'][name]=row
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'EJECUCION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
