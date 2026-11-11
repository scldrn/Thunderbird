"""Contrast Ubuntu XFOIL6.99/Xvfb with the saved MIT6.996 UIUC cases."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import math
import re
import subprocess

from comparar_arranques import call
from comparar_uiuc import data_block,polar_rows

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IMAGE='sha256:cbf29dc7a179c4b20c46c90d9e54636912de665beb81cd8558c25bf6af33fbfe'
CONTAINER='codex-aero-xfoil-uiuc-xvfb699-r1'


def main():
    out=HERE/'uiuc_xvfb699_r1';assert not out.exists();out.mkdir()
    geometry=ROOT/'fuentes/uiuc/sd8020.dat';reference=ROOT/'fuentes/uiuc/SD8020.DRG'
    previous=HERE/'uiuc_61400_r1/RESULTADOS.json'; prev=json.loads(previous.read_text())
    measured=data_block(reference);assert len(measured)==len(prev['points'])==10
    report=dict(scope='Paired XFOIL versions at selected UIUC angles; not physical validation',
        image_id=IMAGE,geometry_sha256=hashlib.sha256(geometry.read_bytes()).hexdigest(),
        previous_result_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(),
        source_data_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        created_UTC=datetime.now(timezone.utc).isoformat(),physical_acceptance=False,
        conditions=dict(Re=61400,Mach=0.,Ncrit=9.,panels=240,independent_initialization=True),
        same_inputs_do_not_prove_identical_algorithms=True,packaged_FPE_checks_retained=True,points=[])
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier;call('cp',str(geometry),CONTAINER+':/tmp/sd8020.dat')
        report['binary_sha256']=call('exec',CONTAINER,'sha256sum','/usr/bin/xfoil').stdout.split()[0]
        for index,(angle,cl_exp,cd_exp) in enumerate(measured):
            prior=prev['points'][index];assert prior['alpha_deg']==angle
            name=f'{index:02d}';polar=f'/tmp/v699_{name}.txt'
            commands=f'LOAD /tmp/sd8020.dat\nPPAR\nN 240\n\n\nPANE\nOPER\nVISC 61400\nMACH 0\nITER 200\nPACC\n{polar}\n\nALFA {angle:.2f}\nPACC\n\nQUIT\n'
            (out/(name+'_input.txt')).write_text(commands)
            row=dict(index=index,alpha_deg=angle,cl_exp=cl_exp,cd_exp=cd_exp,
                previous_6996_cl=prior.get('cl_xfoil'),previous_6996_cd=prior.get('cd_xfoil'),strict_screen_pass=False)
            try:
                proc=call('exec','-i',CONTAINER,'sh','-c','ulimit -c 0; cd /tmp; xvfb-run -a xfoil',
                          input=commands,timeout=120,check=False)
                (out/(name+'.log')).write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr)
                panels=re.findall(r'Number of panel nodes\s+(\d+)',proc.stdout)
                rms=re.findall(r'\brms:\s*([0-9.Ee+-]+)',proc.stdout)
                row.update(exit_code=proc.returncode,observed_panel_nodes=list(map(int,panels)),
                    fpe_signal_reported='Floating-point exception' in proc.stderr,
                    marching_warnings=len(re.findall(r'MRCH(?:UE|DU): Convergence failed',proc.stdout)),
                    final_viscal_failure=bool(re.search(r'VISCAL:\s+Convergence failed',proc.stdout)),
                    final_rms=float(rms[-1]) if rms else None)
                copied=call('cp',CONTAINER+':'+polar,str(out/(name+'_polar.txt')),check=False)
                row['polar_copy_exit_code']=copied.returncode
                if copied.returncode==0:
                    data=polar_rows((out/(name+'_polar.txt')).read_text());row['polar_rows']=len(data)
                    if len(data)==1 and all(math.isfinite(x) for x in data[0]) and abs(data[0][0]-angle)<.001:
                        row.update(cl_699=data[0][1],cd_699=data[0][2],
                            delta_cl_699_vs_6996=data[0][1]-prior['cl_xfoil'],
                            delta_cd_699_vs_6996=data[0][2]-prior['cd_xfoil'])
                        row['strict_screen_pass']=(proc.returncode==0 and bool(panels) and int(panels[-1])==240 and
                            row['marching_warnings']==0 and not row['final_viscal_failure'] and
                            row['final_rms'] is not None and row['final_rms']<1e-4 and row['cd_699']>0)
            except subprocess.TimeoutExpired as exc:row.update(timeout=True,error=repr(exc))
            report['points'].append(row)
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'RESULTADOS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report['points'],indent=2))


if __name__=='__main__':main()
