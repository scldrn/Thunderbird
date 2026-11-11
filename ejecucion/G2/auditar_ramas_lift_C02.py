"""Audit the ordering and overlapping branches of measured SD8020 lift data."""
from pathlib import Path
import csv
import hashlib
import json

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def branch_difference(up, down, angle):
    assert np.all(np.diff(up[:, 0]) > 0) and np.all(np.diff(down[:, 0]) > 0)
    assert max(up[0, 0], down[0, 0]) <= angle <= min(up[-1, 0], down[-1, 0])
    return float(np.interp(angle, up[:, 0], up[:, 1])-np.interp(angle, down[:, 0], down[:, 1]))


def main():
    test = np.array([[0.,0.], [1.,1.]])
    np.testing.assert_allclose(branch_difference(test, test, .4), 0.)
    np.testing.assert_allclose(branch_difference(test, test+np.array([0., .2]), .4), -.2)
    path = ROOT/'fuentes/uiuc/SD8020.LFT'
    rows, meta = [], []
    for block in path.read_text().split('Average Reynolds #:')[1:]:
        lines = block.strip().splitlines(); values = []
        for line in lines[1:]:
            try:
                row = [float(x) for x in line.split()[:3]]
                if len(row) == 3:
                    values.append(row)
            except ValueError:
                continue
        data = np.array(values); pivot = int(np.argmax(data[:, 0]))
        up, down = data[:pivot+1], data[pivot:][::-1]
        assert np.all(np.diff(up[:, 0]) > 0) and np.all(np.diff(down[:, 0]) > 0)
        overlap = [max(up[0,0],down[0,0]), min(up[-1,0],down[-1,0])]
        re = float(lines[0])
        meta.append(dict(reynolds=re, samples=len(data), increasing_samples=len(up),
                         decreasing_samples=len(down), common_alpha_deg=[float(x) for x in overlap]))
        for angle in (0.,5.,10.,15.):
            delta = branch_difference(up, down, angle)
            rows.append(dict(reynolds=re, alpha_deg=angle,
                cl_increasing=float(np.interp(angle,up[:,0],up[:,1])),
                cl_decreasing=float(np.interp(angle,down[:,0],down[:,1])),
                cl_increasing_minus_decreasing=delta))
    assert len(meta) == 8 and len(rows) == 32
    out = HERE/'dominio_polar_C02_r2'
    target = out/'RAMAS_LIFT.json'
    assert out.is_dir() and not target.exists()
    with (out/'RAMAS_LIFT.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    result = dict(scope='Two order-preserving alpha branches in UIUC lift-only data; not cause identification or rotor validation',
        method='Linear interpolation within overlapping angle range, separately for increasing and decreasing recorded angles',
        analytic_interpolation_tests_pass=True, extrapolation_used=False,
        loops_do_not_establish_hysteresis_mechanism=True, drag_or_shaft_power_not_supplied=True,
        source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        blocks=meta, comparisons=rows)
    target.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for row in rows:
        if row['alpha_deg']==5:
            print(f"Re={row['reynolds']:.0f}, alpha=5°, Cl increase-decrease={row['cl_increasing_minus_decreasing']:.6f}")


if __name__ == '__main__':
    main()
