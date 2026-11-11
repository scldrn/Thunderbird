"""Compare alpha, total lift and total drag in polar files against final logs."""
from pathlib import Path
import hashlib
import json
import re

from comparar_uiuc import polar_rows

HERE=Path(__file__).resolve().parent


def main():
    case=HERE/'uiuc_61400_r1'
    source=json.loads((case/'RESULTADOS.json').read_text())
    rows=[]
    for p in source['points']:
        index=p['index'];log=case/f'{index:02d}.log';polar=case/f'{index:02d}_polar.txt'
        text=log.read_text()
        cl=re.findall(r'a\s*=\s*([-\d.]+)\s+CL\s*=\s*([-\d.]+)',text)
        cd=re.findall(r'Cm\s*=\s*([-\d.]+)\s+CD\s*=\s*([-\d.]+)',text)
        data=polar_rows(polar.read_text());assert cl and cd and len(data)==1
        last_alpha,last_cl=map(float,cl[-1]);last_cm,last_cd=map(float,cd[-1]);values=data[0]
        for actual,expected,tolerance in zip([values[0],values[1],values[2],values[4]],
            [last_alpha,last_cl,last_cd,last_cm],[.00051,.000051,.0000051,.000051]):
            assert abs(actual-expected)<tolerance,(index,actual,expected)
        rows.append(dict(index=index,alpha_deg=last_alpha,cl=last_cl,cd=last_cd,cm=last_cm,
            log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),polar_sha256=hashlib.sha256(polar.read_bytes()).hexdigest()))
    out=case/'AUDITORIA_CL_CD.json';assert not out.exists()
    out.write_text(json.dumps(dict(scope='10 final alpha/CL/CD/CM log-to-file consistency checks; not physical validation',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        all_agree_within_print_rounding=True,pressure_drag_component_not_assessed=True,
        physical_acceptance=False,points=rows),indent=2)+'\n')
    print('10/10: alpha, CL, total CD, CM match final solver log within rounding')


if __name__=='__main__':main()
