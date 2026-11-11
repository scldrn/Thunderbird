"""Matched-mesh SST/SA sensitivity; model spread is not experimental uncertainty."""
from pathlib import Path
import argparse
import hashlib
import json
import re

import numpy as np
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy

from auditar_malla_su2 import read_mesh
from reconstruir_traccion_su2 import boundary_cycle


def config(case):
    return {k:v.strip() for k,v in re.findall(r'^\s*([A-Z0-9_]+)\s*=\s*([^%\n]+)',
                                             (case/'case.cfg').read_text(), re.M)}


def shock_indicator(case, chord):
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
    cp = vtk_to_numpy(grid.GetPointData().GetArray('Pressure_Coefficient'))[mapping]
    cycle = boundary_cycle(markers['AIRFOIL'], xy)
    le, te = np.argmin(xy[cycle, 0]), np.argmax(xy[cycle, 0])
    paths = []
    for step in (1, -1):
        path = [int(le)]
        while path[-1] != te:
            path.append((path[-1]+step) % len(cycle))
        paths.append(cycle[path])
    upper = max(paths, key=lambda p: np.mean(xy[p, 1]))
    order = np.argsort(xy[upper, 0])
    x, pressure = xy[upper[order], 0]/chord, cp[upper[order]]
    width = np.diff(x)
    midpoint = .5*(x[:-1]+x[1:])
    gradient = np.divide(np.diff(pressure), width, out=np.full_like(width, -np.inf), where=width>0)
    mask = (midpoint >= .2) & (midpoint <= .8)
    index = int(np.argmax(np.where(mask, gradient, -np.inf)))
    assert mask[index] and gradient[index] > 0
    return dict(definition='Midpoint of largest positive wall Cp slope on upper surface inside fixed0.2..0.8chord window; not exact shock position',
        x_over_c=float(midpoint[index]), bracket_x_over_c=x[index:index+2].tolist(),
        delta_Cp=float(pressure[index+1]-pressure[index]), slope_dCp_dxi=float(gradient[index]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sst', type=Path, required=True)
    parser.add_argument('--sa', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Preserve previous model-comparison snapshot'
    sst, sa = args.sst.resolve(), args.sa.resolve()
    inputs = [json.loads((p/'ENTRADAS.json').read_text()) for p in (sst, sa)]
    audits = [json.loads((p/'AUDITORIA_SU2.json').read_text()) for p in (sst, sa)]
    terminals = [json.loads((p/'EJECUCION.json').read_text()) for p in (sst, sa)]
    assert all(t['stage']=='solver_exited' and t['exit_code']==0 for t in terminals)
    assert audits[0]['actual_model'].startswith('SST-2003m')
    assert audits[1]['actual_model'].startswith('Spalart-Allmaras-noft2')
    assert terminals[0]['binary_sha256'] == terminals[1]['binary_sha256']
    mesh_hashes = [hashlib.sha256((p/'mesh_RAE2822_turb.su2').read_bytes()).hexdigest() for p in (sst, sa)]
    assert mesh_hashes[0] == mesh_hashes[1]
    cc, cf = config(sst), config(sa)
    differences = {k:[cc.get(k), cf.get(k)] for k in cc.keys() | cf.keys() if cc.get(k) != cf.get(k)}
    allowed = {'ITER','CONV_STARTITER','OUTPUT_WRT_FREQ','SCREEN_OUTPUT','KIND_TURB_MODEL','SA_OPTIONS','FREESTREAM_NU_FACTOR'}
    assert set(differences) <= allowed, differences
    conditions = [i['declared_conditions'] for i in inputs]
    keys = ['Mach','alpha_deg','Reynolds','chord','T_freestream_K','gas_model','gas_R_J_kg_K','gamma',
            'mu_reference_Pas','mu_reference_temperature_K','Sutherland_K','eddy_to_molecular_viscosity_ratio']
    for key in keys:
        assert conditions[0][key] == conditions[1][key], key
    factor = conditions[1]['freestream_nu_factor']
    achieved_ratio = factor**4/(factor**3+7.1**3)
    np.testing.assert_allclose(achieved_ratio, conditions[0]['eddy_to_molecular_viscosity_ratio'], rtol=1e-13)
    taps = [np.loadtxt(p/'Cp_CONTRASTE_PROVISIONAL.csv', delimiter=',', skiprows=1) for p in (sst, sa)]
    np.testing.assert_array_equal(taps[0][:, :2], taps[1][:, :2])
    coeff = {key:dict(SST=audits[0][key], SA_noft2=audits[1][key],
        difference=audits[1][key]-audits[0][key], relative_to_SST=(audits[1][key]-audits[0][key])/audits[0][key])
        for key in ('last_CL','last_CD')}
    report = dict(scope='Matched-condition model sensitivity; not model selection by experimental fit, not accepted uncertainty or vehicle performance',
        SST_case=sst.name, SA_case=sa.name, native_binary_identical=True, mesh_identical_sha256=mesh_hashes[0],
        mean_freestream_transport_and_reference_values_identical=True,
        matched_freestream_eddy_to_laminar_ratio=float(achieved_ratio),
        configuration_differences=differences, coefficients=coeff,
        Cp_error_RMS_all103=dict(SST=audits[0]['Cp_RMS_error_provisional'], SA_noft2=audits[1]['Cp_RMS_error_provisional']),
        Cp_model_difference_same103positions=dict(RMS=float(np.sqrt(np.mean((taps[1][:,2]-taps[0][:,2])**2))),
                                                max_abs=float(abs(taps[1][:,2]-taps[0][:,2]).max())),
        upper_midchord_pressure_rise_indicator={name:shock_indicator(p, conditions[0]['chord'])
                                              for name,p in (('SST',sst),('SA_noft2',sa))},
        yPlus_ranges=dict(SST=audits[0]['wall_reported_yPlus_range'], SA_noft2=audits[1]['wall_reported_yPlus_range']),
        limits=['Mean pressure preserved when removing SST rho*k from SA restart energy; models do not share transported turbulence variables.',
            'Single-mesh model comparison; model spread is not a confidence interval or total physical error.',
            'SA requires its own late full-state/force probe before settled model differences can be claimed.',
            'No identity to legacy WIND SA variant or experimental transition; all103 pressure taps retained.'],
        experimental_validation_accepted=False, vehicle_performance_accepted=False,
        source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for case in (sst,sa)
            for p in (case/'ENTRADAS.json',case/'AUDITORIA_SU2.json',case/'TRACCION_RECONSTRUIDA.json',
                      case/'EJECUCION.json',case/'case.cfg',case/'Cp_CONTRASTE_PROVISIONAL.csv')})
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('coefficients','Cp_error_RMS_all103','upper_midchord_pressure_rise_indicator')}, indent=2))


if __name__ == '__main__':
    main()
