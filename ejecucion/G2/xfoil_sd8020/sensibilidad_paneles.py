"""Selected UIUC angles at two XFOIL panel counts; retain all failures."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import math
import re
import subprocess

from comparar_arranques import call
from comparar_uiuc import polar_rows

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IMAGE='sha256:54f41a5d5e16486edb4c92ebce9bb9fc2ec8108dbd3fed9f9b917886c8b9bdf3'
CONTAINER='codex-aero-xfoil-paneles-r1'
BINARY='/opt/xfoil-source/Xfoil/bin/xfoil'


def main():
    out=HERE/'paneles_r1';assert not out.exists();out.mkdir()
    geometry=ROOT/'fuentes/uiuc/sd8020.dat'
    report=dict(scope='Selected XFOIL panel-count sensitivity only, not uncertainty or physical acceptance',
        image_id=IMAGE,geometry_sha256=hashlib.sha256(geometry.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        Re=61400,Mach=0.,Ncrit=9.,FPE_traps_disabled_in_MIT_default_build=True,
        independent_zero_history_per_point=True,physical_fan_acceptance=False,
        created_UTC=datetime.now(timezone.utc).isoformat(),points=[])
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier;call('cp',str(geometry),CONTAINER+':/tmp/sd8020.dat')
        for panels in (160,320):
            for index,angle in enumerate((-.29,1.17,2.72,5.89)):
                name=f'n{panels}_{index:02d}';polar=f'/tmp/{name}.txt'
                commands=f'PLOP\nG\n\nLOAD /tmp/sd8020.dat\nPPAR\nN {panels}\n\n\nPANE\nOPER\nVISC 61400\nMACH 0\nITER 200\nPACC\n{polar}\n\nALFA {angle:.2f}\nPACC\n\nQUIT\n'
                (out/(name+'_input.txt')).write_text(commands)
                row=dict(requested_panels=panels,alpha_deg=angle,strict_accepted=False)
                try:
                    proc=call('exec','-i',CONTAINER,'sh','-c','ulimit -c 0; cd /tmp; '+BINARY,
                              input=commands,timeout=120,check=False)
                    (out/(name+'.log')).write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr)
                    matches=re.findall(r'Number of panel nodes\s+(\d+)',proc.stdout)
                    rms=re.findall(r'\brms:\s*([0-9.Ee+-]+)',proc.stdout)
                    row.update(exit_code=proc.returncode,observed_panel_nodes=list(map(int,matches)),
                        final_rms=float(rms[-1]) if rms else None,
                        marching_warning_count=len(re.findall(r'MRCH(?:UE|DU): Convergence failed',proc.stdout)),
                        final_viscal_failure=bool(re.search(r'VISCAL:\s+Convergence failed',proc.stdout)))
                    copied=call('cp',CONTAINER+':'+polar,str(out/(name+'_polar.txt')),check=False)
                    row['polar_copy_exit_code']=copied.returncode
                    if copied.returncode==0:
                        data=polar_rows((out/(name+'_polar.txt')).read_text());row['polar_rows']=len(data)
                        if len(data)==1 and all(math.isfinite(x) for x in data[0]) and abs(data[0][0]-angle)<.001:
                            row.update(cl=data[0][1],cd=data[0][2])
                            row['strict_accepted']=(proc.returncode==0 and panels in row['observed_panel_nodes'] and
                                row['marching_warning_count']==0 and not row['final_viscal_failure'] and
                                row['final_rms'] is not None and row['final_rms']<1e-4 and row['cd']>0)
                except subprocess.TimeoutExpired as exc:row.update(timeout=True,error=repr(exc))
                report['points'].append(row)
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'RESULTADOS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report['points'],indent=2))


if __name__=='__main__':main()
