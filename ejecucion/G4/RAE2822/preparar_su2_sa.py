"""Prepare SA-noft2 sensitivity with matched geometry/mean flow and eddy viscosity.

The SST rho*k contribution is removed from total energy when changing models;
otherwise the restart itself would spuriously alter thermodynamic pressure.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil

import numpy as np
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy

from auditar_su2 import table
from auditar_malla_su2 import read_mesh

HERE = Path(__file__).resolve().parent
SOURCE = HERE/'su2_nasa_fina_r3_sonda'
CASE = HERE/'su2_nasa_sa_r1'


def inverse_fv1(eddy_to_laminar):
    """Invert r=chi^4/(chi^3+7.1^3), the nonnegative SA branch."""
    ratio = np.asarray(eddy_to_laminar, dtype=float)
    assert np.isfinite(ratio).all() and (ratio >= 0).all()
    lower, upper = np.zeros_like(ratio), ratio+7.1
    for _ in range(80):
        mid = .5*(lower+upper)
        recovered = mid**4/(mid**3+7.1**3)
        lower = np.where(recovered < ratio, mid, lower)
        upper = np.where(recovered >= ratio, mid, upper)
    chi = np.where(ratio == 0, 0., .5*(lower+upper))
    np.testing.assert_allclose(chi**4/(chi**3+7.1**3), ratio, rtol=2e-13, atol=1e-14)
    return chi


def main():
    assert not CASE.exists(), 'Preserve existing model-sensitivity case'
    terminal = json.loads((SOURCE/'EJECUCION.json').read_text())
    audit = json.loads((SOURCE/'AUDITORIA_SU2.json').read_text())
    inputs = json.loads((SOURCE/'ENTRADAS.json').read_text())
    gamma = inputs['declared_conditions'].get('gamma', 1.4)
    assert terminal['stage'] == 'solver_exited' and terminal['exit_code'] == 0
    assert audit['rho_range_kg_m3'][0] > 0 and audit['pressure_range_Pa'][0] > 0
    fields = table(SOURCE/'restart_flow.csv')
    order = np.argsort(fields['PointID'])
    fields = {k:v[order] for k,v in fields.items()}
    xy, _, _ = read_mesh(SOURCE/'mesh_RAE2822_turb.su2')
    np.testing.assert_allclose(np.column_stack((fields['x'], fields['y'])), xy, atol=1e-12, rtol=0)
    reader = vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(SOURCE/'flow.vtu'))
    reader.Update()
    grid = reader.GetOutput()
    xyz = vtk_to_numpy(grid.GetPoints().GetData())[:, :2]
    a, b = np.lexsort((xyz[:, 1], xyz[:, 0])), np.lexsort((xy[:, 1], xy[:, 0]))
    np.testing.assert_allclose(xyz[a], xy[b], atol=1e-12, rtol=0)
    mapping = np.empty(len(xy), dtype=int)
    mapping[b] = a
    mu = vtk_to_numpy(grid.GetPointData().GetArray('Laminar_Viscosity'))[mapping]
    mut = vtk_to_numpy(grid.GetPointData().GetArray('Eddy_Viscosity'))[mapping]
    rho = fields['Density']
    assert (mu > 0).all() and (mut >= 0).all()
    nu_tilde = inverse_fv1(mut/mu)*mu/rho
    chi = rho*nu_tilde/mu
    recovered_mut = rho*nu_tilde*chi**3/(chi**3+7.1**3)
    np.testing.assert_allclose(recovered_mut, mut, rtol=3e-13, atol=1e-15)
    energy = fields['Energy']-rho*fields['Turb_Kin_Energy']
    kinetic_density = .5*(fields['Momentum_x']**2+fields['Momentum_y']**2)/rho
    p_SST = (gamma-1)*(fields['Energy']-kinetic_density-rho*fields['Turb_Kin_Energy'])
    p_SA = (gamma-1)*(energy-kinetic_density)
    np.testing.assert_allclose(p_SST, p_SA, rtol=1e-14, atol=1e-9)
    assert p_SA.min() > 0 and np.isfinite(nu_tilde).all() and (nu_tilde >= 0).all()
    ratio_inf = inputs['declared_conditions']['eddy_to_molecular_viscosity_ratio']
    nu_factor = float(inverse_fv1(ratio_inf))
    CASE.mkdir()
    for name in ('mesh_RAE2822_turb.su2', 'ORIGINAL_turb_SST_RAE2822.cfg'):
        shutil.copy2(SOURCE/name, CASE/name)
    columns = ['PointID', 'x', 'y', 'Density', 'Momentum_x', 'Momentum_y', 'Energy', 'Nu_Tilde']
    with (CASE/'solution_flow.csv').open('w') as f:
        f.write(','.join('"'+name+'"' for name in columns)+'\n')
        for i in range(len(xy)):
            row = [i, *xy[i], rho[i], fields['Momentum_x'][i], fields['Momentum_y'][i], energy[i], nu_tilde[i]]
            f.write(str(i)+', '+', '.join(f'{v:.16e}' for v in row[1:])+'\n')
    text = (SOURCE/'case.cfg').read_text()
    for key, value in {'KIND_TURB_MODEL':'SA', 'ITER':'1800', 'CONV_STARTITER':'1801',
                       'OUTPUT_WRT_FREQ':'1800',
                       'SCREEN_OUTPUT':'(INNER_ITER, RMS_DENSITY, RMS_NU_TILDE, LIFT, DRAG, AVG_CFL)'}.items():
        text, count = re.subn(r'^'+key+r'\s*=.*$', f'{key}= {value}', text, flags=re.M)
        assert count == 1, key
    text += f'\nSA_OPTIONS= NONE\nFREESTREAM_NU_FACTOR= {nu_factor:.17g}\n'
    (CASE/'case.cfg').write_text(text)
    inputs.update(scope='Matched-eddy-viscosity SA-noft2 model sensitivity; not experimental or vehicle validation',
        parent=SOURCE.name, iteration_limit=1800,
        turbulence_model='SA', actual_model_expected='Spalart-Allmaras-noft2; no corrections, fully turbulent',
        geometry_and_mean_conditions_unchanged=True,
        physical_models_geometry_freestream_and_schemes_unchanged=False,
        model_change='SST2003m to SA-noft2; preserve mean pressure and initial eddy viscosity, not the SST transported variables',
        numerical_note='JST/implicitEuler/MG3/FGMRES-LUSGS/CFLadaptive1..50 retained;1800 forced SA steps; original SST config kept as parameter provenance only.',
        restart_seed=dict(source=SOURCE.name, energy_formula='rhoE_SA=rhoE_SST-rho*k_SST',
            initial_mu_t_preserved_by_inverse_fv1=True,
            maximum_pressure_conversion_difference_Pa=float(abs(p_SA-p_SST).max()),
            maximum_mut_conversion_difference_Pas=float(abs(recovered_mut-mut).max()),
            native_primitive_stage_lag_from_SST_preserved_in_report=audit['retained_vs_recomputed_thermodynamics']),
        changes_from_parent=['SA-noft2 model', 'Mean energy excludes SST rho*k contribution',
            'Nu_Tilde from inversion of source eddy viscosity', f'FREESTREAM_NU_FACTOR={nu_factor:.12g} for mu_t/mu={ratio_inf}',
            '1800 forced additional iterations; SA residual output'],
        source_inputs_sha256={name:hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()
                             for name in ('restart_flow.csv', 'flow.vtu', 'AUDITORIA_SU2.json', 'case.cfg')},
        physical_validation_accepted=False, vehicle_performance_accepted=False,
        inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CASE.iterdir() if p.is_file()})
    inputs['declared_conditions'].update(turbulence_model='SA', SA_options='NONE',
        freestream_nu_factor=nu_factor, turbulence_intensity_not_transported_by_SA=True)
    inputs['distinctions_from_NASA_WIND'] = [
        'SA-noft2 fully turbulent; no identity to the legacy WIND SA variant or experiment transition asserted.'
        if item.startswith('SST2003m') else item for item in inputs['distinctions_from_NASA_WIND']]
    (CASE/'ENTRADAS.json').write_text(json.dumps(inputs, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(case=str(CASE), freestream_nu_factor=nu_factor,
        matched_mu_t_over_mu=ratio_inf, max_pressure_conversion_Pa=float(abs(p_SA-p_SST).max()),
        max_mu_t_conversion_Pas=float(abs(recovered_mut-mut).max())), indent=2))


if __name__ == '__main__':
    main()
