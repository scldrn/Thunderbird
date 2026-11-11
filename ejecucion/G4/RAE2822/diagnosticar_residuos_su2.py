"""Locate exported residuals and compare all experimental taps without trimming."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy

from auditar_malla_su2 import read_mesh
from verificar_convencion_cp import read_gen

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, required=True)
    args = parser.parse_args()
    case = args.case.resolve()
    audit = json.loads((case/'AUDITORIA_SU2.json').read_text())
    cond = json.loads((case/'ENTRADAS.json').read_text())['declared_conditions']
    xy, _, markers = read_mesh(case/'mesh_RAE2822_turb.su2')
    reader = vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(case/'flow.vtu'))
    reader.Update()
    grid = reader.GetOutput()
    coords = vtk_to_numpy(grid.GetPoints().GetData())[:, :2]
    a, b = np.lexsort((coords[:, 1], coords[:, 0])), np.lexsort((xy[:, 1], xy[:, 0]))
    np.testing.assert_allclose(coords[a], xy[b], atol=1e-12, rtol=0)
    mapping = np.empty(len(xy), dtype=int)
    mapping[b] = a
    wall = np.unique(markers['AIRFOIL'])
    residuals = {}
    for index in range(grid.GetPointData().GetNumberOfArrays()):
        name = grid.GetPointData().GetArrayName(index)
        if not name.startswith('Residual'):
            continue
        values = vtk_to_numpy(grid.GetPointData().GetArray(index))[mapping].reshape(len(xy), -1)
        assert np.isfinite(values).all()
        magnitude = np.linalg.norm(values, axis=1)
        at = int(np.argmax(magnitude))
        residuals[name] = dict(arithmetic_RMS_per_component=np.sqrt(np.mean(values**2, axis=0)).tolist(),
            maximum_vector_magnitude=float(magnitude[at]), values_at_maximum=values[at].tolist(),
            maximum_node_ID=at, xy_over_chord=(xy[at]/cond['chord']).tolist(),
            maximum_is_wall_node=bool(at in wall),
            nearest_wall_vertex_distance_chords=float(np.linalg.norm(xy[wall]-xy[at], axis=1).min()/cond['chord']))
    own = np.loadtxt(case/'Cp_CONTRASTE_PROVISIONAL.csv', delimiter=',', skiprows=1)
    source = HERE.parents[2]/'fuentes/benchmark_RAE2822'
    wind, exp = read_gen(source/'cp.wind.gen', 305), read_gen(source/'cp.exp.gen', 103)
    le, split = int(np.argmin(wind[:, 0])), int(np.argmin(exp[:, 0]))
    lower, upper = wind[:le+1][::-1], wind[le:]
    wind_predicted = -np.r_[np.interp(exp[:split+1, 0], upper[:, 0], upper[:, 1]),
                            np.interp(exp[split+1:, 0], lower[:, 0], lower[:, 1])]
    np.testing.assert_allclose(own[:, :2], np.column_stack((exp[:, 0], -exp[:, 1])))
    wind_error = wind_predicted-own[:, 1]
    # Fixed regions summarize the discrepancy, with no deletion of the full set.
    masks = {'all_103': np.ones(len(own), dtype=bool), 'leading_edge_x_lt_0p02': own[:, 0] < .02,
             'mid_chord_0p4_to_0p65': (own[:, 0] >= .4) & (own[:, 0] <= .65),
             'remaining_points': (own[:, 0] >= .02) & ((own[:, 0] < .4) | (own[:, 0] > .65))}
    regions = {name: dict(points=int(mask.sum()), own_RMS=float(np.sqrt(np.mean(own[mask, 3]**2))),
                          published_WIND_SA_RMS=float(np.sqrt(np.mean(wind_error[mask]**2))))
               for name, mask in masks.items()}
    at = int(np.argmax(abs(own[:, 3])))
    report = dict(scope='Residual location and complete-data diagnostic; not convergence/validation acceptance',
        residual_fields=residuals,
        residual_export_not_assumed_identical_to_history_stage_or_normalization=True,
        Cp_regions=regions, points_removed=0,
        worst_own_Cp_point=dict(index=at, x_over_c=float(own[at, 0]),
            branch='upper' if at <= split else 'lower', experimental=float(own[at, 1]),
            own=float(own[at, 2]), published_WIND_SA=float(wind_predicted[at])),
        published_WIND_is_SA_not_SST=True,
        interpretation='Similar error against the published computation is context, not an experimental acceptance test or proof of the cause.',
        experimental_Cp_error_reported_approximately=.0026,
        experimental_error_is_not_own_acceptance_tolerance=True,
        physical_validation_accepted=False,
        source_URL='https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (case/'flow.vtu', case/'Cp_CONTRASTE_PROVISIONAL.csv', source/'cp.wind.gen', source/'cp.exp.gen')})
    (case/'DIAGNOSTICO_RESIDUOS_CP.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(residuals={k:v['xy_over_chord'] for k,v in residuals.items()},
        Cp_regions=regions, worst=report['worst_own_Cp_point']), indent=2))


if __name__ == '__main__':
    main()
