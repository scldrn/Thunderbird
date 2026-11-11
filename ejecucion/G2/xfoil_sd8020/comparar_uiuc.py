"""Independent-angle SD8020 XFOIL/UIUC comparison; all failures retained."""
from pathlib import Path
from datetime import datetime,timezone
import csv
import hashlib
import json
import math
import re
import subprocess

from comparar_arranques import call

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
IMAGE='sha256:54f41a5d5e16486edb4c92ebce9bb9fc2ec8108dbd3fed9f9b917886c8b9bdf3'
BINARY='/opt/xfoil-source/Xfoil/bin/xfoil'
CONTAINER='codex-aero-xfoil-uiuc-61400-r1'


def data_block(path):
    block=path.read_text().split('Average Reynolds #:')[1].strip().splitlines()
    assert float(block[0])==61400
    rows=[]
    for line in block[1:]:
        try:
            values=[float(x) for x in line.split()[:3]]
            if len(values)==3:rows.append(values)
        except ValueError:pass
    assert len(rows)==10 and all(a[0]<b[0] for a,b in zip(rows,rows[1:]))
    return rows


def polar_rows(text):
    result=[]
    for line in text.splitlines():
        fields=line.split()
        if len(fields)!=9:continue
        try:
            values=[float(x) for x in fields]
        except ValueError:continue
        result.append(values)
    return result


def main():
    out=HERE/'uiuc_61400_r1';assert not out.exists();out.mkdir()
    geometry=ROOT/'fuentes/uiuc/sd8020.dat'; reference=ROOT/'fuentes/uiuc/SD8020.DRG'
    measured=data_block(reference)
    report=dict(scope='Independent-angle computational crosscheck against UIUC SD8020 DRG; not calibrated installed fan',
        image_id=IMAGE,source_geometry_sha256=hashlib.sha256(geometry.read_bytes()).hexdigest(),
        reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        conditions=dict(Re=61400,Mach=0.,Ncrit=9.,panel_nodes=240,forced_transition_x_over_c=1.,
                        experimental_Ncrit_and_test_Mach_matched=False),
        independent_zero_history_for_each_alpha=True,all_requested_points_retained=True,
        transition_header_order_not_trusted=True,FPE_traps_disabled_in_MIT_default_build=True,
        physical_fan_acceptance=False,created_UTC=datetime.now(timezone.utc).isoformat(),points=[])
    identifier=None
    try:
        identifier=call('run','-d','--name',CONTAINER,'--network','none','--user','1000:1000',IMAGE,'sleep','infinity').stdout.strip()
        report['container_id']=identifier
        call('cp',str(geometry),CONTAINER+':/tmp/sd8020.dat')
        for index,(angle,cl_exp,cd_exp) in enumerate(measured):
            polar=f'/tmp/uiuc_{index:02d}.txt'
            commands=f'PLOP\nG\n\nLOAD /tmp/sd8020.dat\nPANE\nOPER\nVISC 61400\nMACH 0\nITER 200\nPACC\n{polar}\n\nALFA {angle:.2f}\nPACC\n\nQUIT\n'
            (out/f'{index:02d}_input.txt').write_text(commands)
            row=dict(index=index,alpha_deg=angle,cl_experiment=cl_exp,cd_experiment=cd_exp,
                     accepted_numerical_point=False)
            try:
                proc=call('exec','-i',CONTAINER,'sh','-c','ulimit -c 0; cd /tmp; '+BINARY,
                          input=commands,timeout=120,check=False)
                (out/f'{index:02d}.log').write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr)
                row.update(exit_code=proc.returncode,reported_convergence_failure=('Convergence failed' in proc.stdout),
                           added_to_polar=('Point added to stored polar' in proc.stdout),
                           fpe_signal_reported=('Floating-point exception' in proc.stderr))
                copied=call('cp',CONTAINER+':'+polar,str(out/f'{index:02d}_polar.txt'),check=False)
                row['polar_copy_exit_code']=copied.returncode
                if copied.returncode==0:
                    polar_text=(out/f'{index:02d}_polar.txt').read_text()
                    data=polar_rows(polar_text)
                    row['polar_rows']=len(data)
                    if len(data)==1 and all(math.isfinite(x) for x in data[0]) and abs(data[0][0]-angle)<.001:
                        row.update(cl_xfoil=data[0][1],cd_xfoil=data[0][2],
                                   cl_error=data[0][1]-cl_exp,cd_error=data[0][2]-cd_exp)
                        row['accepted_numerical_point']=(proc.returncode==0 and row['added_to_polar'] and
                                                         not row['reported_convergence_failure'] and data[0][2]>0)
            except subprocess.TimeoutExpired as exc:
                row.update(timeout=True,error=repr(exc))
            report['points'].append(row)
    finally:
        if identifier:report['stop_exit_code']=call('stop',CONTAINER,check=False).returncode
        (out/'RESULTADOS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    fields=sorted({key for row in report['points'] for key in row})
    with (out/'RESULTADOS.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(report['points'])
    print(json.dumps(dict(requested=len(measured),recorded=len(report['points']),
        numerical_points=sum(p['accepted_numerical_point'] for p in report['points']),
        physical_fan_acceptance=False),indent=2))


if __name__=='__main__':main()
