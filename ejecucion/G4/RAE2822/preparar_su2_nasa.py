"""Convert the supplied NASA grid directly to native 2D SU2, preserving its wake.

This is a separate, bounded comparison. It does not repair or overwrite any
previous case, nor claim identical turbulence/boundary implementations to WIND.
"""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil

import numpy as np

from auditar_malla_su2 import read_mesh
from auditar_su2 import table

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASE = HERE / 'su2_nasa_r1'


def main():
    global CASE
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, default=CASE)
    parser.add_argument('--refined', action='store_true')
    parser.add_argument('--seed', type=Path)
    args = parser.parse_args()
    CASE = args.case.resolve()
    assert not CASE.exists(), 'Inspect existing NASA native case before changing it'
    source = ROOT / 'fuentes/benchmark_RAE2822/raetaf.x.fmt'
    raw = np.fromstring(source.read_text(), sep=' ')
    ni, nj = map(int, raw[:2])
    assert (ni, nj) == (369, 65) and len(raw) == 2 + 2*ni*nj
    grid = raw[2:].reshape(2, nj, ni).transpose(1, 2, 0)
    np.testing.assert_array_equal(grid[0, :33], grid[0, -1:-34:-1])
    original_grid = grid.copy()
    si = 2 if args.refined else 1
    icoord = np.linspace(0, ni-1, (ni-1)*si+1)
    jcoord = np.r_[np.concatenate([j+np.arange(4 if j < 2 else 2)/(4 if j < 2 else 2)
                         for j in range(nj-1)]), nj-1] if args.refined else np.arange(nj)
    jlower = np.minimum(jcoord.astype(int), nj-2)
    ilower = np.minimum(icoord.astype(int), ni-2)
    jf, it = jcoord-jlower, icoord-ilower
    def interpolate(values):
        bottom = ((1-it)[None, :, None]*values[jlower[:, None], ilower[None, :]]
                  + it[None, :, None]*values[jlower[:, None], ilower[None, :]+1])
        top = ((1-it)[None, :, None]*values[jlower[:, None]+1, ilower[None, :]]
               + it[None, :, None]*values[jlower[:, None]+1, ilower[None, :]+1])
        return (1-jf)[:, None, None]*bottom+jf[:, None, None]*top
    grid = interpolate(grid)
    ni, nj = len(icoord), len(jcoord)
    xy, first, inverse = np.unique(grid.reshape(-1, 2), axis=0, return_index=True, return_inverse=True)
    index = inverse.reshape(nj, ni)
    chord = .3048
    xy *= chord
    cells = np.array([[index[j, i], index[j, i+1], index[j+1, i+1], index[j+1, i]]
                      for j in range(nj-1) for i in range(ni-1)])
    polygon = xy[cells]
    edges = np.roll(polygon, -1, axis=1) - polygon
    crosses = (edges[:, :, 0]*np.roll(edges[:, :, 1], -1, axis=1)
               - edges[:, :, 1]*np.roll(edges[:, :, 0], -1, axis=1))
    assert (crosses > 0).all()
    areas = .5*np.sum(polygon[:, :, 0]*np.roll(polygon[:, :, 1], -1, axis=1)
                         - polygon[:, :, 1]*np.roll(polygon[:, :, 0], -1, axis=1), axis=1)
    markers = {
        'AIRFOIL': [[index[0, i], index[0, i+1]] for i in range(32*si, 336*si)],
        'FARFIELD': [[index[-1, i+1], index[-1, i]] for i in range(ni-1)],
        'OUTFLOW': ([[index[j+1, 0], index[j, 0]] for j in range(nj-1)]
                    + [[index[j, -1], index[j+1, -1]] for j in range(nj-1)])}
    counts = Counter(tuple(sorted((int(c[i]), int(c[(i+1) % 4]))))
                     for c in cells for i in range(4))
    assert set(counts.values()) == {1, 2}
    assert {e for e, count in counts.items() if count == 1} == {
        tuple(sorted(e)) for values in markers.values() for e in values}
    assert len(xy) == ni*nj-(32*si+1)
    assert len(cells) == (97152 if args.refined else 23552)
    CASE.mkdir()
    mesh = CASE / 'mesh_RAE2822_turb.su2'
    with mesh.open('w') as f:
        f.write(f'NDIME= 2\nNELEM= {len(cells)}\n')
        for i, c in enumerate(cells):
            f.write('9 ' + ' '.join(map(str, c)) + f' {i}\n')
        f.write(f'NPOIN= {len(xy)}\n')
        for i, (x, y) in enumerate(xy):
            f.write(f'{x:.17g} {y:.17g} {i}\n')
        f.write(f'NMARK= {len(markers)}\n')
        for name, values in markers.items():
            f.write(f'MARKER_TAG= {name}\nMARKER_ELEMS= {len(values)}\n')
            for a, b in values:
                f.write(f'3 {a} {b}\n')
    restored, restored_cells, restored_markers = read_mesh(mesh)
    np.testing.assert_array_equal(restored, xy)
    np.testing.assert_array_equal(restored_cells, cells)
    assert restored_markers == markers
    # Every source surface vertex is retained, including the sharp trailing edge.
    np.testing.assert_array_equal(xy[index[0, 32*si:336*si+1:si]], original_grid[0, 32:337]*chord)
    p_inf, T_inf, gas_r, gamma = 15.80734*6894.757293168, 460*5/9, 287.05287, 1.4
    speed = .729*np.sqrt(gamma*gas_r*T_inf)
    rho = p_inf/(gas_r*T_inf)
    mu_target = rho*speed*chord/6.5e6
    mu_ref = mu_target/((T_inf/273.15)**1.5*(273.15+110.4)/(T_inf+110.4))
    original = HERE/'su2_r1_oficial/ORIGINAL_turb_SST_RAE2822.cfg'
    shutil.copy2(original, CASE/original.name)
    text = original.read_text()
    replacements = {
        'ITER': '1200', 'OUTPUT_WRT_FREQ': '400',
        'FREESTREAM_TEMPERATURE': f'{T_inf:.17g}', 'REYNOLDS_LENGTH': str(chord),
        'FREESTREAM_TURB2LAMVISCRATIO': '1.0',
        'REF_ORIGIN_MOMENT_X': str(.25*chord), 'REF_LENGTH': str(chord),
        'REF_AREA': str(chord), 'CFL_NUMBER': '5.0', 'CFL_ADAPT': 'YES',
        'CFL_ADAPT_PARAM': '( 0.9, 1.1, 1.0, 50.0, 0.1 )',
        'CONV_STARTITER': '1201'}
    for name, value in replacements.items():
        text, count = re.subn(r'^'+name+r'\s*=.*$', f'{name}= {value}', text, flags=re.M)
        assert count == 1, name
    text += f'''\n% Native conversion of NASA Study4 grid. No fitted aerodynamic parameters.
FLUID_MODEL= IDEAL_GAS
GAMMA_VALUE= {gamma}
GAS_CONSTANT= {gas_r}
VISCOSITY_MODEL= SUTHERLAND
MU_REF= {mu_ref:.17g}
MU_T_REF= 273.15
SUTHERLAND_CONSTANT= 110.4
MARKER_OUTLET= ( OUTFLOW, {p_inf:.17g} )
OUTPUT_FILES= (RESTART_ASCII, SURFACE_CSV, PARAVIEW)
HISTORY_OUTPUT= (ITER, RMS_RES, MAX_RES, AERO_COEFF)
VOLUME_OUTPUT= (COORDINATES, SOLUTION, PRIMITIVE, RESIDUAL)
VOLUME_OUTPUT_PRECISION= DOUBLE
'''
    (CASE/'case.cfg').write_text(text)
    seed_metadata = None
    if args.seed:
        seed = args.seed.resolve()
        terminal = json.loads((seed/'EJECUCION.json').read_text())
        audit = json.loads((seed/'AUDITORIA_SU2.json').read_text())
        assert terminal['stage'] == 'solver_exited' and terminal['exit_code'] == 0
        assert audit['pressure_range_Pa'][0] > 0 and audit['rho_range_kg_m3'][0] > 0
        source_xy, _, _ = read_mesh(seed/'mesh_RAE2822_turb.su2')
        coarse_unique, coarse_inverse = np.unique(original_grid.reshape(-1, 2), axis=0, return_inverse=True)
        np.testing.assert_array_equal(source_xy, coarse_unique*chord)
        fields = table(seed/'restart_flow.csv')
        order = np.argsort(fields['PointID'])
        fields = {k:v[order] for k,v in fields.items()}
        # Native ASCII restart rounds coordinates to ~15 significant digits.
        np.testing.assert_allclose(fields['x'], source_xy[:, 0], atol=1e-12, rtol=0)
        np.testing.assert_allclose(fields['y'], source_xy[:, 1], atol=1e-12, rtol=0)
        names = ['Density', 'Momentum_x', 'Momentum_y', 'Energy', 'Turb_Kin_Energy', 'Omega']
        conserved = np.column_stack([fields[k] for k in names])
        conserved[:, 4] *= conserved[:, 0]  # Interpolate rho*k to retain admissible energy.
        coarse_values = conserved[coarse_inverse].reshape(*original_grid.shape[:2], len(names))
        refined = interpolate(coarse_values).reshape(-1, len(names))[first]
        refined[:, 4] /= refined[:, 0]
        rho_f = refined[:, 0]
        pressure_f = (gamma-1)*(refined[:, 3]-.5*np.sum(refined[:, 1:3]**2, axis=1)/rho_f-rho_f*refined[:, 4])
        assert np.isfinite(refined).all() and rho_f.min() > 0 and pressure_f.min() > 0
        assert refined[:, 4].min() >= 0 and refined[:, 5].min() > 0
        with (CASE/'solution_flow.csv').open('w') as f:
            f.write(','.join('"'+k+'"' for k in ['PointID', 'x', 'y', *names])+'\n')
            for at, (pos, values) in enumerate(zip(xy, refined)):
                f.write(str(at)+', '+', '.join(f'{v:.16e}' for v in [*pos, *values])+'\n')
        text = re.sub(r'^RESTART_SOL\s*=.*$', 'RESTART_SOL= YES', text, flags=re.M)
        text += '\nREAD_BINARY_RESTART= NO\n'
        (CASE/'case.cfg').write_text(text)
        seed_metadata = dict(parent=seed.name, scheme='Bilinear native structured-parametric interpolation of rho,momentum,rhoE,rho*k,omega; divide rho*k by refinedrho.',
            source_restart_sha256=hashlib.sha256((seed/'restart_flow.csv').read_bytes()).hexdigest(),
            minimum_initial_p_Pa=float(pressure_f.min()), minimum_initial_rho_kg_m3=float(rho_f.min()),
            wall_omega_note='Native SST will reset wallomega for the smaller first-cell spacing; interpolated seed is not a solution.')
    inputs = dict(
        scope='Native SU2 comparison on directly converted NASA grid, not accepted validation',
        source_SU2_version='8.6.0', iteration_limit=1200, counter_is_physical_time=False,
        declared_conditions=dict(Mach=.729, alpha_deg=2.31, Reynolds=6.5e6, chord=chord,
            T_freestream_K=T_inf, turbulence_intensity=.001, eddy_to_molecular_viscosity_ratio=1.,
            gas_model='IDEAL_GAS', gas_R_J_kg_K=gas_r, gamma=gamma,
            mu_reference_Pas=mu_ref, mu_reference_temperature_K=273.15, Sutherland_K=110.4),
        target_reference=dict(p_Pa=p_inf, rho_kg_m3=rho, U_m_s=speed, mu_Pas=mu_target),
        geometry=dict(points=len(xy), quadrilaterals=len(cells), positive_convex_cells=True,
            minimum_area_m2=float(areas.min()), boundary_edges={k:len(v) for k,v in markers.items()},
            identical_source_vertices_verified=True, conformal_wake_merged_nodes=32*si+1,
            refinement='i2; first2 jintervals4, remaining jintervals2' if args.refined else 'none',
            planar_geometry_unchanged_by_bilinear_subdivision=True,
            sharp_TE=True, quality_not_accepted_from_other_solver=True),
        source_grid_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_URL='https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html',
        numerical_note='Official SU2 JST/implicit/MG3; startCFL5/adaptive1..50; all1200steps forced; residual export added.',
        distinctions_from_NASA_WIND=[
            'Same supplied vertices/connectivity and freestream M/alpha/Re/T/chord; native node-centred scheme differs.',
            'Transport reference chosen to reproduce stated p/Re simultaneously; not measured viscosity.',
            'SST2003m fully turbulent versus legacy WIND/experiment transition, not identical.',
            'I0.001 and viscosityRatio1 are assumptions, not stated NASA experimental values.',
            'Native characteristic farfield/static-pressure outlet may differ from WIND implementation.',
            'Single highly stretched source C-grid; no mesh independence or full force budget accepted.'],
        physical_validation_accepted=False, vehicle_performance_accepted=False,
        restart_seed=seed_metadata,
        inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CASE.iterdir() if p.is_file()})
    (CASE/'ENTRADAS.json').write_text(json.dumps(inputs, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(case=str(CASE), points=len(xy), cells=len(cells), target_p_Pa=p_inf,
                          mu_ref_Pas=mu_ref), indent=2))


if __name__ == '__main__':
    main()
