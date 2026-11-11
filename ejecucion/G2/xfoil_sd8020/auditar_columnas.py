"""Cross-check XFOIL 6.996 polar transition column labels with its own logs."""
from pathlib import Path
import hashlib
import json
import re

from comparar_uiuc import polar_rows

HERE=Path(__file__).resolve().parent


def main():
    case=HERE/'uiuc_61400_r1'; original=json.loads((case/'RESULTADOS.json').read_text())
    source=HERE/'iopol_mit_6.996.f'; text=source.read_text()
    assert '((CPOLSD(IA,IS,JPOL(J)), J=1, NJPOL), IS=1, 2*NBL)' in text
    rows=[]
    for point in original['points']:
        index=point['index'];log=case/f'{index:02d}.log';polar=case/f'{index:02d}_polar.txt'
        t=log.read_text();data=polar_rows(polar.read_text());assert len(data)==1
        sides=[]
        for side in (1,2):
            found=re.findall(r'Side\s+'+str(side)+r'\s+(?:free|forced)\s+transition at x/c\s*=\s*([0-9.Ee+-]+)',t)
            assert found;sides.append(float(found[-1]))
        values=data[0]
        assert abs(values[5]-sides[0])<.00011 and abs(values[7]-sides[1])<.00011
        rows.append(dict(index=index,alpha_deg=point['alpha_deg'],logged_side1_x=sides[0],logged_side2_x=sides[1],
            polar_col6=values[5],polar_col7=values[6],polar_col8=values[7],polar_col9=values[8],
            log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),polar_sha256=hashlib.sha256(polar.read_bytes()).hexdigest()))
    report=dict(scope='Observed single-element polar layout for this MIT6.996 build; not generalized to other builds',
        header_columns_6_to_9=['Top_Xtr','Bot_Xtr','Top_Itr','Bot_Itr'],
        observed_data_order_6_to_9=['Top_Xtr','Top_Itr','Bot_Xtr','Bot_Itr'],
        all_10_side_transition_coordinates_match_log=True,
        first_five_numeric_columns_not_tested_by_this_audit=True,
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows)
    out=case/'AUDITORIA_ORDEN_COLUMNAS.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n')
    print('10/10: log side 1 matches column 6, side 2 matches column 8; header order differs')


if __name__=='__main__':main()
