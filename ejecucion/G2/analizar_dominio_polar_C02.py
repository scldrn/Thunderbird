"""Audit local polar-domain coverage and a geometry-only Reynolds/Mach bound.

The saved input points impose disk velocity; this does not solve fan operation.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def fraction_below_piecewise(x, y, threshold):
    """Exact radial-span and annular-area fractions of a linear radius profile."""
    assert len(x) == len(y) and np.all(np.diff(x) > 0) and x[0] >= 0
    intervals = []
    for x0, x1, y0, y1 in zip(x[:-1], x[1:], y[:-1], y[1:]):
        if y0 < threshold and y1 < threshold:
            intervals.append((x0, x1))
        elif (y0 < threshold) != (y1 < threshold):
            cross = x0+(x1-x0)*(threshold-y0)/(y1-y0)
            intervals.append((x0, cross) if y0 < threshold else (cross, x1))
    span = sum(b-a for a, b in intervals)/(x[-1]-x[0])
    area = sum(b*b-a*a for a, b in intervals)/(x[-1]**2-x[0]**2)
    return float(span), float(area), [[float(a), float(b)] for a, b in intervals]


def main():
    np.testing.assert_allclose(fraction_below_piecewise(np.array([0., 1.]), np.array([0., 2.]), 1.)[:2], [.5, .25])
    np.testing.assert_allclose(fraction_below_piecewise(np.array([.5, 1.]), np.array([0., 0.]), 1.)[:2], [1., 1.])
    np.testing.assert_allclose(fraction_below_piecewise(np.array([.5, 1.]), np.array([2., 2.]), 1.)[:2], [0., 0.])
    polar_path = ROOT/'fuentes/uiuc/SD8020.DRG'
    blocks = []
    for block in polar_path.read_text().split('Average Reynolds #:')[1:]:
        lines = block.strip().splitlines()
        values = []
        for line in lines[1:]:
            try:
                numbers = [float(x) for x in line.split()[:3]]
                if len(numbers) == 3:
                    values.append(numbers)
            except ValueError:
                continue
        data = np.asarray(values)
        assert len(data) and np.all(np.diff(data[:, 0]) > 0)
        blocks.append((float(lines[0]), data))
    reynolds = np.array([item[0] for item in blocks])
    assert len(blocks) == 4 and np.all(np.diff(reynolds) > 0)
    lift_path = ROOT/'fuentes/uiuc/SD8020.LFT'
    lift_blocks = []
    for block in lift_path.read_text().split('Average Reynolds #:')[1:]:
        lines = block.strip().splitlines()
        values = []
        for line in lines[1:]:
            try:
                numbers = [float(x) for x in line.split()[:3]]
                if len(numbers) == 3:
                    values.append(numbers)
            except ValueError:
                continue
        data = np.asarray(values)
        assert len(data)
        lift_blocks.append(dict(Re=float(lines[0]), samples=len(data),
            alpha_range_deg=[float(data[:,0].min()),float(data[:,0].max())],
            descending_alpha_steps=int(np.count_nonzero(np.diff(data[:,0]) < 0))))
    assert len(lift_blocks) == 8 and min(b['Re'] for b in lift_blocks) == 30500
    nu, sound, mach_limit = 1.46e-5, 340.3, .3
    chord_limit = reynolds[0]*nu/(mach_limit*sound)
    source = HERE/'modulo_preliminar/m5_d1_k0.85.json'
    design = json.loads(source.read_text())['design']
    radius = design['radius_m']
    assert math.isclose(radius, .041)
    annuli = design['annuli']
    x_data = np.array([a['r_m']/radius for a in annuli])
    c_data = np.array([a['chord_m'] for a in annuli])
    hub = .315
    x = np.r_[hub, x_data[(x_data > hub) & (x_data < 1.)], 1.]
    chord = np.interp(x, x_data, c_data)
    span, area, segments = fraction_below_piecewise(x, chord, chord_limit)
    saved_path = HERE/'cargas_locales_C02_r1/ANILLOS.json'
    saved = json.loads(saved_path.read_text())
    rows = []
    for point in saved:
        summary, sections = point['summary'], point['sections']
        if summary['hub_ratio'] != hub:
            continue
        assert len(sections) == 128 and summary['swirl_disk_velocity_m_s'] == 0
        weights = np.array([s['r_m'] for s in sections]); weights /= weights.sum()
        causes = {key: [] for key in ('below_re', 'above_re', 'outside_alpha', 'outside_polar', 'mach_above_limit')}
        for s in sections:
            W = math.hypot(s['axial_at_disk_m_s'], summary['rpm']*math.pi/30*s['r_m'])
            np.testing.assert_allclose([s['relative_speed_m_s'], s['Re'], s['Mach_relative']],
                [W, W*s['chord_m']/nu, W/sound], rtol=1e-12)
            hi = int(np.clip(np.searchsorted(reynolds, s['Re']), 1, len(reynolds)-1)); lo = hi-1
            weight = float(np.clip((s['Re']-reynolds[lo])/(reynolds[hi]-reynolds[lo]), 0, 1))
            alpha_ok = all(blocks[i][1][0, 0] <= s['alpha_deg'] <= blocks[i][1][-1, 0]
                           for i, w in ((lo, 1-weight), (hi, weight)) if w > 1e-12)
            low, high = s['Re'] < reynolds[0], s['Re'] > reynolds[-1]
            outside = low or high or not alpha_ok
            assert outside == (not s['polar_in_domain'])
            for key, value in [('below_re', low), ('above_re', high), ('outside_alpha', not alpha_ok),
                               ('outside_polar', outside), ('mach_above_limit', s['Mach_relative'] > mach_limit)]:
                causes[key].append(value)
        row = dict(rpm=summary['rpm'], axial_disk_velocity_m_s=summary['axial_disk_velocity_m_s'],
                   **{key+'_annular_area_fraction':float(weights[np.array(mask)].sum()) for key, mask in causes.items()},
                   polar_and_mach_joint_area_fraction=float(weights[~np.array(causes['outside_polar']) &
                                                              ~np.array(causes['mach_above_limit'])].sum()))
        rows.append(row)
    assert len(rows) == 21
    out = HERE/'dominio_polar_C02_r2'
    assert not out.exists(), 'Preserve existing screening'
    out.mkdir()
    with (out/'COBERTURA.csv').open('w', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    result = dict(scope='Kinematic/polar-domain diagnostic; not a fan operating map or rotor redesign',
        combined_lift_drag_reynolds_blocks=reynolds.tolist(),
        combined_lift_drag_alpha_domain_deg=[[float(a[0,0]),float(a[-1,0])] for _,a in blocks],
        separate_lift_only_blocks=lift_blocks,
        nu_m2_s=nu,sound_speed_m_s=sound,mach_screen=mach_limit, radius_m=radius, hub_ratio=hub,
        critical_chord_m=chord_limit,critical_chord_formula='Re_min*nu/(M_screen*a)',
        critical_chord_condition='Below this chord Re >= DRG minimum and M <= screen cannot both hold for any local speed',
        impossible_span_fraction=span,impossible_active_annular_area_fraction=area,
        below_chord_intervals_r_over_R=segments, theoretical_bound_tests_pass=True,
        polar_flags_reproduced_for_all_21x128_sections=True,
        angle_and_Re_area_fractions_can_overlap=True,
        midpoint_area_weighting_is_not_thrust_or_torque_weighting=True,
        prescribed_disk_velocity_and_zero_swirl_not_solved=True,
        no_compressibility_or_rotating_cascade_model=True, physical_fan_performance_accepted=False,
        actual_experiment_reynolds_are_not_assumed_continuous_measurements=True,
        lift_only_data_are_not_drag_data=True,
        lift_loop_samples_not_sorted_or_interpolated=True,
        chord_geometry='Interpolation of 64 saved C01 annuli with endpoint extension; not exact CAD section metrology',
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (source,polar_path,lift_path,saved_path,Path(__file__).resolve())}, rows=rows)
    (out/'RESULTADOS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('combined_lift_drag_reynolds_blocks','combined_lift_drag_alpha_domain_deg',
        'separate_lift_only_blocks','critical_chord_m',
        'impossible_span_fraction','impossible_active_annular_area_fraction','below_chord_intervals_r_over_R')},indent=2))
    for row in rows:
        if row['axial_disk_velocity_m_s']==20:
            print(row)


if __name__ == '__main__':
    main()
