"""Audit startup fields and compare Cp without accepting an unconverged pilot."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'CFD'))
from foam_fields import read_internal
from analizar_series_transitorias import read_series


def list_body(path):
    text = path.read_text()
    match = re.search(r'\n(\d+)\s*\(\s*\n', text)
    assert match, path
    end = text.find('\n)', match.end())
    assert end > match.end()
    return int(match[1]), text[match.end():end]


def wall_geometry(case, expected):
    mesh = case/'constant/polyMesh'
    count, body = list_body(mesh/'points')
    points = np.fromstring(body.replace('(', ' ').replace(')', ' '), sep=' ').reshape(-1, 3)
    assert len(points) == count
    boundary = (mesh/'boundary').read_text()
    block = re.search(r'\bairfoil\s*\{(.*?)\}', boundary, re.S)[1]
    assert re.search(r'type\s+wall;', block)
    start = int(re.search(r'startFace\s+(\d+)', block)[1])
    size = int(re.search(r'nFaces\s+(\d+)', block)[1])
    assert size == expected
    count, body = list_body(mesh/'faces')
    rows = body.splitlines()
    assert len(rows) == count
    selected = rows[start:start+size]
    assert all(row.startswith('4(') for row in selected)
    faces = np.fromstring('\n'.join(selected).replace('4(', ' ').replace(')', ' '), sep=' ', dtype=int).reshape(-1, 4)
    p = points[faces]
    centres = p.mean(axis=1)
    areas = .5*np.sum(np.cross(p, np.roll(p, -1, axis=1)), axis=1)
    assert np.linalg.norm(areas.sum(axis=0)) < 1e-12
    count, body = list_body(mesh/'owner')
    owner = np.fromstring(body, sep=' ', dtype=int)
    assert len(owner) == count == len(rows)
    return centres, areas, owner[start:start+size]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, required=True)
    args = parser.parse_args()
    case = args.case.resolve()
    state = json.loads((case/'EJECUCION.json').read_text())
    assert state['stage'] == 'solver_exited' and state['exit_code'] == 0 and state['target_reached']
    inputs = json.loads((case/'ENTRADAS.json').read_text())
    mesh = json.loads((case/'MALLA.json').read_text())
    target = inputs['iteration_target']
    start_counter = inputs.get('iteration_start', 0)
    log = (case/'log.foamRun').read_text()
    assert '\nEnd\n' in log and 'FOAM FATAL' not in log
    first = {}
    zero_corrections = {}
    for block in re.split(r'\nTime = ', log)[1:]:
        match = re.match(r'([\deE.+-]+)', block)
        if not match or 'ClockTime =' not in block:
            continue
        values = {}
        for name, value in re.findall(r'Solving for (\w+), Initial residual = ([\deE.+-]+)', block):
            values.setdefault(name, float(value))
        first[float(match[1])] = values
        counts = re.findall(r'Solving for (\w+),[^\n]*No Iterations (\d+)', block)
        zero_corrections[float(match[1])] = dict(total=len(counts), zero=sum(int(v) == 0 for _, v in counts))
    assert max(first) == target
    n = mesh['cells']
    fields, summary = {}, {}
    for name in ('U', 'p', 'T', 'rho', 'k', 'omega', 'nut'):
        path = case/str(target)/name
        a = read_internal(path, n, 3 if name == 'U' else 1)
        fields[name] = a
        v = np.linalg.norm(a, axis=1) if name == 'U' else a
        if name != 'U':
            assert np.min(a) >= 0, name
        summary[name] = dict(min=float(v.min()), max=float(v.max()), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    assert fields['T'].min() > 0 and fields['rho'].min() > 0 and fields['p'].min() > 0
    # Local sound speed, not a freestream proxy.
    speed = np.linalg.norm(fields['U'], axis=1)
    mach = speed/np.sqrt(inputs['gamma']*inputs['R_J_kg_K']*fields['T'])
    gas_defect = np.max(abs(fields['p']-fields['rho']*inputs['R_J_kg_K']*fields['T'])/fields['p'])
    pp = case/'postProcessing'
    forces, parse = read_series(pp, 'force_airfoil', 'forces.dat', 13)
    times = forces[:, 0]
    # foamRun also evaluates these function objects on its initial state.
    assert times[-1] == target and np.array_equal(times, np.arange(start_counter, target+1))
    force = forces[:, 1:4]+forces[:, 4:7]
    alpha = np.deg2rad(inputs['alpha_deg'])
    drag_axis, lift_axis = np.array([np.cos(alpha), np.sin(alpha), 0]), np.array([-np.sin(alpha), np.cos(alpha), 0])
    q = .5*inputs['rho_kg_m3']*inputs['speed_m_s']**2
    scale = q*inputs['area_reference_m2']
    cd, cl = force@drag_axis/scale, force@lift_axis/scale
    mass = []
    for patch in ('farfield', 'outlet'):
        a, _ = read_series(pp, 'mass_'+patch, 'surfaceFieldValue.dat', 2)
        np.testing.assert_array_equal(a[:, 0], times)
        mass.append(a[:, 1])
    # This is an outer net-flux diagnostic. Under local time stepping it is
    # neither an exact global physical accumulation nor a discrete residual.
    boundary_net_mass = mass[0]+mass[1]
    mass_scale = inputs['rho_kg_m3']*inputs['speed_m_s']*inputs['area_reference_m2']
    thresholds = dict(p=1e-5, Ux=1e-5, Uy=1e-5, h=1e-5, k=1e-5, omega=1e-5)
    tail = times[-20:]
    residuals = {name:max(first[t][name] for t in tail) for name in thresholds}
    drift = dict(CL=float(abs(cl[-20:].mean()-cl[-40:-20].mean())),
                 CD=float(abs(cd[-20:].mean()-cd[-40:-20].mean())))
    changes = {}
    scales = dict(U=inputs['speed_m_s'], p=q, T=inputs['T_K'], rho=inputs['rho_kg_m3'],
                  k=inputs['k_freestream_m2_s2'], omega=inputs['omega_freestream_s_1'],
                  nut=inputs['mu_reference_Pas']/inputs['rho_kg_m3'])
    for name, value in fields.items():
        a = read_internal(case/str(target-20)/name, n, 3 if name == 'U' else 1)
        delta = np.linalg.norm(value-a, axis=1) if name == 'U' else abs(value-a)
        changes[name] = dict(maximum=float(delta.max()), cell_arithmetic_RMS=float(np.sqrt(np.mean(delta**2))),
                             reference_scale=scales[name], maximum_normalized=float(delta.max()/scales[name]))
    centres, areas, owner = wall_geometry(case, mesh['boundary_faces']['airfoil'])
    ptext = (case/str(target)/'p').read_text()
    pwall = re.search(r'\bairfoil\s*\{(.*?)\}', ptext, re.S)[1]
    assert re.search(r'type\s+zeroGradient;', pwall), 'Owner pressure only for this explicit BC'
    pressure = fields['p'][owner]
    independent_force = np.sum((pressure-inputs['p_Pa'])[:, None]*areas, axis=0)
    np.testing.assert_allclose(independent_force, forces[-1, 1:4], rtol=2e-7, atol=2e-7)
    cpwall = (pressure-inputs['p_Pa'])/q
    # Project wall-face centres onto the NASA polygon. Its full surface arc
    # resolves the two branches and the leading-edge tap without extrapolation.
    raw = np.fromstring((ROOT/'fuentes/benchmark_RAE2822/raetaf.x.fmt').read_text(), sep=' ')
    surface = raw[2:].reshape(2, 65, 369).transpose(1, 2, 0)[0, 32:337]
    ds = np.linalg.norm(np.diff(surface, axis=0), axis=1)
    arc = np.r_[0, np.cumsum(ds)]
    a, d = surface[:-1], np.diff(surface, axis=0)
    xy = centres[:, :2]/inputs['chord_m']
    t = np.clip(np.einsum('ijk,jk->ij', xy[:, None, :]-a, d)/ds**2, 0, 1)
    proj = a+t[..., None]*d
    distance = np.linalg.norm(xy[:, None, :]-proj, axis=2)
    segment = distance.argmin(axis=1)
    assert np.max(distance[np.arange(len(xy)), segment]) < 1e-10
    s = arc[segment]+t[np.arange(len(xy)), segment]*ds[segment]
    exp = np.loadtxt(case/'Cp_experimental.csv', delimiter=',', skiprows=1)
    convention = json.loads((HERE/'CONVENCION_CP_VERIFICADA.json').read_text())
    assert convention['physical_Cp_multiplier'] == -1
    assert convention['experimental_trace'] == 'upper_TE_to_LE_then_lower_LE_to_TE'
    exp[:, 1] *= -1
    leading = int(np.argmin(exp[:, 0]))
    le = int(np.argmin(surface[:, 0]))
    upper_s = np.interp(exp[:leading+1, 0], surface[le:, 0], arc[le:])
    lower_s = np.interp(exp[leading+1:, 0], surface[:le+1, 0][::-1], arc[:le+1][::-1])
    tap_s = np.r_[upper_s, lower_s]
    assert tap_s.min() >= s.min() and tap_s.max() <= s.max()
    order = np.argsort(s)
    own_cp = np.interp(tap_s, s[order], cpwall[order])
    error = own_cp-exp[:, 1]
    np.savetxt(case/'Cp_CONTRASTE_ARRANQUE.csv', np.column_stack((exp[:, 0], tap_s, exp[:, 1], own_cp, error)),
               delimiter=',', header='x_over_c,s_over_c,Cp_exp,Cp_startup,error', comments='')
    yplus = []
    for path in (pp/'wall_resolution').glob('*/yPlus.dat'):
        for line in path.read_text().splitlines():
            v = line.split()
            if len(v) == 5 and v[1] == 'airfoil':
                yplus.append(dict(counter=float(v[0]), minimum=float(v[2]), maximum=float(v[3]), reported_average=float(v[4])))
    screens = dict(first_residuals=all(residuals[k] < thresholds[k] for k in thresholds),
                   adjacent20_force_coeff_drift=max(drift.values()) < 1e-4,
                   outer_net_mass_last20=float(np.max(abs(boundary_net_mass[-20:]))/mass_scale) < 1e-5,
                   primary_field_changes=max(changes[k]['maximum_normalized'] for k in ('U','p','T','rho')) < 1e-4,
                   no_near_vacuum_sentinel=min(summary['p']['min']/inputs['p_Pa'],
                                               summary['rho']['min']/inputs['rho_kg_m3']) > .05)
    frozen_thermo = all(changes[k]['maximum'] == 0 for k in ('p','T','rho'))
    zero_fraction = sum(zero_corrections[t]['zero'] for t in tail)/sum(zero_corrections[t]['total'] for t in tail)
    dt_range = None
    if (case/str(target)/'rDeltaT').exists():
        inverse_dt = read_internal(case/str(target)/'rDeltaT', n)
        assert inverse_dt.min() > 0
        dt_range = [float(1/inverse_dt.max()),float(1/inverse_dt.min())]
    cpu = re.findall(r'ExecutionTime = ([\deE.+-]+) s\s+ClockTime = ([\deE.+-]+) s', log)
    report = dict(scope='Transonic startup diagnostic and provisional Cp comparison, not accepted validation',
        iteration_start=start_counter, iteration_target=target, counter_is_physical_time=False, final_fields=summary,
        maximum_local_Mach=float(mach.max()), perfect_gas_relative_defect_max=float(gas_defect),
        last_force_N=force[-1].tolist(), last_CL=float(cl[-1]), last_CD=float(cd[-1]),
        pressure_force_independently_reconstructed_verified=True,
        force_series_parsing=parse, last20_first_residual_max=residuals,
        declared_screen_thresholds=thresholds, adjacent20_coefficient_drift=drift,
        last20_outer_net_mass_relative_max=float(np.max(abs(boundary_net_mass[-20:]))/mass_scale),
        comparison_counters=[target-20,target], field_changes=changes, yPlus_reported=yplus,
        last20_zero_linear_correction_fraction=zero_fraction,
        frozen_thermo_with_changing_velocity=bool(frozen_thermo and changes['U']['maximum_normalized'] > 1e-4),
        local_pseudo_time_step_range_s=dt_range,
        numerical_sentinels=dict(min_p_over_pInf=summary['p']['min']/inputs['p_Pa'],
            min_rho_over_rhoInf=summary['rho']['min']/inputs['rho_kg_m3'],near_vacuum_ratio_floor=.05,
            note='Broad numerical degeneracy sentinel for this transonic benchmark, not a physical acceptance envelope.'),
        Cp_points=len(exp), Cp_interpolation='Full surface arc on actual NASA polygon; lower/upper trace joined at LE; no tap extrapolation',
        experimental_Cp_convention='Raw NASA file stores -Cp, upper trace first; corrected to (p-pInf)/qInf with independently verified branch order',
        experimental_convention_sha256=hashlib.sha256((HERE/'CONVENCION_CP_VERIFICADA.json').read_bytes()).hexdigest(),
        Cp_startup_RMS_error=float(np.sqrt(np.mean(error**2))), Cp_startup_max_abs_error=float(abs(error).max()),
        diagnostic_screens=screens, diagnostic_screens_all_pass=all(screens.values()),
        solver_CPU_s=float(cpu[-1][0]), solver_wall_s=float(cpu[-1][1]),
        physical_validation_accepted=False, vehicle_performance_accepted=False,
        pending='Develop and converge fields; confirm budgets, wall treatment, turbulence/transition and mesh/scheme/domain sensitivity before accepting Cp or loads.')
    (case/'AUDITORIA_PILOTO.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('maximum_local_Mach', 'last_CL','last_CD','Cp_startup_RMS_error','diagnostic_screens')}, indent=2))


if __name__ == '__main__':
    main()
