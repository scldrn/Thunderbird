"""Compare measured lift branches with drag-run lift and exploratory XFOIL."""
from pathlib import Path
from bisect import bisect_right
import csv
import hashlib
import json
import math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def interp(x,points):
    xs=[p[0] for p in points]
    assert all(a<b for a,b in zip(xs,xs[1:])) and xs[0]<=x<=xs[-1]
    k=min(max(bisect_right(xs,x)-1,0),len(xs)-2)
    a,b=points[k],points[k+1]
    return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])


def main():
    assert interp(.5,[(0.,0.),(1.,2.)])==1.
    lft=ROOT/'fuentes/uiuc/SD8020.LFT'
    blocks=lft.read_text().split('Average Reynolds #:')[1:]
    selected=[b.strip().splitlines() for b in blocks if float(b.strip().splitlines()[0])==60600]
    assert len(selected)==1
    rows=[]
    for line in selected[0][1:]:
        try:
            vals=[float(x) for x in line.split()[:3]]
            if len(vals)==3:rows.append(vals)
        except ValueError:pass
    assert len(rows)==97
    pivot=max(range(len(rows)),key=lambda i:rows[i][0])
    up=rows[:pivot+1];down=list(reversed(rows[pivot:]))
    original=HERE/'uiuc_61400_r1/RESULTADOS.json'; data=json.loads(original.read_text())
    assert len(data['points'])==10
    output=[]
    for p in data['points']:
        angle=p['alpha_deg']; lift_up=interp(angle,up);lift_down=interp(angle,down)
        output.append(dict(alpha_deg=angle,lift_ascending_Re60600=lift_up,
            lift_descending_Re60600=lift_down,drag_run_lift_Re61400=p['cl_experiment'],
            xfoil_lift_Re61400=p['cl_xfoil'],xfoil_minus_lift_ascending=p['cl_xfoil']-lift_up,
            xfoil_minus_lift_descending=p['cl_xfoil']-lift_down))
    report=dict(scope='Same-angle interpolation between separate UIUC lift/drag runs and exploratory XFOIL; not matched uncertainty or acceptance',
        lift_Re=60600,drag_run_Re=61400,relative_Re_difference=(60600-61400)/61400,
        source_revision_note='UIUC webpage reports Vols1-2 updates in 1998; local source files were not byte-compared online during this run',
        no_alpha_extrapolation=True,lift_branches_kept_separate=True,
        individual_runs_not_assumed_identical=True,physical_fan_acceptance=False,
        interpolation_test_pass=True,cl_RMSE_vs_lift_ascending=math.sqrt(sum(x['xfoil_minus_lift_ascending']**2 for x in output)/len(output)),
        cl_RMSE_vs_lift_descending=math.sqrt(sum(x['xfoil_minus_lift_descending']**2 for x in output)/len(output)),
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (lft,original,Path(__file__).resolve())},points=output)
    out=HERE/'uiuc_61400_r1'/'COMPARACION_RAMAS_LIFT.json';assert not out.exists();out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    for r in output:
        if r['alpha_deg'] in (-.29,1.17,2.72,5.89):print(r)
    print('RMS vs measured branches:',report['cl_RMSE_vs_lift_ascending'],report['cl_RMSE_vs_lift_descending'])


if __name__=='__main__':main()
