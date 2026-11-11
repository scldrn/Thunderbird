"""Compare two native meshes at identical physical conditions, without a GCI claim."""
from pathlib import Path
import argparse
import hashlib
import json
import re

import numpy as np

from auditar_malla_su2 import read_mesh
from reconstruir_traccion_su2 import boundary_cycle


def load(case):
    inputs = json.loads((case/'ENTRADAS.json').read_text())
    audit = json.loads((case/'AUDITORIA_SU2.json').read_text())
    traction = json.loads((case/'TRACCION_RECONSTRUIDA.json').read_text())
    xy, cells, markers = read_mesh(case/'mesh_RAE2822_turb.su2')
    poly = xy[boundary_cycle(markers['AIRFOIL'], xy)]
    domain_area = sum(.5*abs(np.sum(xy[c, 0]*np.roll(xy[c, 1], -1)
                                   - xy[c, 1]*np.roll(xy[c, 0], -1))) for c in cells)
    taps = np.loadtxt(case/'Cp_CONTRASTE_PROVISIONAL.csv', delimiter=',', skiprows=1)
    return inputs, audit, traction, poly, domain_area, taps, len(cells)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--coarse', type=Path, required=True)
    parser.add_argument('--fine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Keep previous mesh comparison evidence'
    coarse, fine = args.coarse.resolve(), args.fine.resolve()
    ic, ac, tc, pc, dc, taps_c, nc = load(coarse)
    iff, af, tf, pf, df, taps_f, nf = load(fine)
    assert ic['declared_conditions'] == iff['declared_conditions']
    def config(case):
        return {k:v.strip() for k,v in re.findall(r'^\s*([A-Z0-9_]+)\s*=\s*([^%\n]+)',
                                                 (case/'case.cfg').read_text(), re.M)}
    cc, cf = config(coarse), config(fine)
    differences = {k:[cc.get(k), cf.get(k)] for k in cc.keys() | cf.keys() if cc.get(k) != cf.get(k)}
    allowed = {'ITER', 'CONV_STARTITER', 'OUTPUT_WRT_FREQ', 'RESTART_SOL', 'READ_BINARY_RESTART'}
    assert set(differences) <= allowed, differences
    ec, ef = [json.loads((case/'EJECUCION.json').read_text()) for case in (coarse, fine)]
    assert ec['binary_sha256'] == ef['binary_sha256']
    np.testing.assert_allclose(dc, df, rtol=1e-12, atol=1e-10)
    # Every refined wall vertex lies on the same original polygon segments.
    edge = np.roll(pc, -1, axis=0)-pc
    t = np.clip(np.einsum('nmi,mi->nm', pf[:, None, :]-pc, edge)/np.sum(edge**2, axis=1), 0, 1)
    distance = np.linalg.norm(pf[:, None, :]-(pc+t[..., None]*edge), axis=2).min(axis=1)
    np.testing.assert_allclose(distance, 0, atol=1e-12, rtol=0)
    np.testing.assert_allclose(taps_c[:, :2], taps_f[:, :2], atol=0, rtol=0)
    report = dict(scope='Two-grid sensitivity with same polygon and conditions; not a grid-independence/GCI or experimental acceptance claim',
        coarse_case=coarse.name, fine_case=fine.name, cell_counts=[nc, nf],
        physical_conditions_identical=True, domain_area_m2=[dc, df],
        same_native_binary_verified=True, configuration_differences=differences,
        explicit_model_and_scheme_options_identical=True,
        maximum_refined_wall_distance_to_coarse_polygon_m=float(distance.max()),
        same_polygon_verified=True,
        calculated_coefficients={k:dict(coarse=ac[k], fine=af[k], difference=af[k]-ac[k],
            relative_difference_to_coarse=(af[k]-ac[k])/ac[k]) for k in ('last_CL', 'last_CD')},
        calculated_yPlus_ranges=dict(coarse=ac['wall_reported_yPlus_range'], fine=af['wall_reported_yPlus_range']),
        Cp_difference_same103positions=dict(RMS=float(np.sqrt(np.mean((taps_f[:, 2]-taps_c[:, 2])**2))),
            max_abs=float(abs(taps_f[:, 2]-taps_c[:, 2]).max())),
        momentum_defect_coeff={name:t['exterior_physical_CV_diagnostic']['Roe_characteristic_reconstruction']['momentum_defect_coeff']
            for name,t in (('coarse', tc), ('fine', tf))},
        caution='Fine branch must pass a further full-state probe before treating this difference as settled discretization sensitivity; effective MG levels and initialization differ.',
        formal_Richardson_GCI_not_computed=True,
        physical_validation_accepted=False, vehicle_performance_accepted=False,
        source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for case in (coarse, fine)
            for p in (case/'AUDITORIA_SU2.json', case/'TRACCION_RECONSTRUIDA.json', case/'ENTRADAS.json',
                      case/'mesh_RAE2822_turb.su2', case/'Cp_CONTRASTE_PROVISIONAL.csv')})
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('same_polygon_verified', 'maximum_refined_wall_distance_to_coarse_polygon_m',
        'calculated_coefficients', 'calculated_yPlus_ranges', 'Cp_difference_same103positions')}, indent=2))


if __name__ == '__main__':
    main()
