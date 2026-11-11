"""Check annular equations against published CCBlade angles and UIUC data.

The tutorial airfoil is computational/corrected NACA4412, not the measured
section distribution of APC or the proposed SD8020 eight-blade rotor.
"""
from pathlib import Path
import csv
import hashlib
import json
import re

import numpy as np
from scipy.interpolate import Akima1DInterpolator

from bem_anular import solve_annulus
from bem_hover import Polar, solve_design

HERE = Path(__file__).resolve().parent
OUT = HERE/'benchmark_bem_publico'


class TutorialPolar:
    def __init__(self):
        self.table = np.loadtxt(OUT/'naca4412_CCBlade.dat', skiprows=3)
        self.cl = Akima1DInterpolator(self.table[:, 0], self.table[:, 1])
        self.cd = Akima1DInterpolator(self.table[:, 0], self.table[:, 2])

    def lookup(self, alpha_deg, reynolds):
        alpha = np.radians(alpha_deg)
        return float(self.cl(alpha)), float(self.cd(alpha)), bool(self.table[0, 0] <= alpha <= self.table[-1, 0])


def geometry():
    text = (OUT/'tutorial_reference.md').read_text()
    match = re.search(r'propgeom = \[(.*?)\]', text, re.S)
    return np.loadtxt(match[1].strip().splitlines())


def operate(rpm, inflow, geom, polar):
    R = .127
    omega = rpm*np.pi/30
    rows = [solve_annulus(rr*R, cr*R, np.radians(beta), R, .1*R, omega,
                          inflow, 2, 1.225, polar) for rr, cr, beta in geom if rr < 1]
    assert all(row['solve_success'] for row in rows), 'No silent exclusion of failed annuli'
    r = np.r_[.1*R, [row['r_m'] for row in rows], R]
    thrust = float(np.trapezoid(np.r_[0., [row['dT_dr_N_m'] for row in rows], 0.], r))
    torque = float(np.trapezoid(np.r_[0., [row['dQ_dr_Nm_m'] for row in rows], 0.], r))
    n, D = rpm/60, 2*R
    CT = thrust/(1.225*n*n*D**4)
    CQ = torque/(1.225*n*n*D**5)
    CP = omega*torque/(1.225*n**3*D**5)
    np.testing.assert_allclose(CP, 2*np.pi*CQ, rtol=1e-12)
    return dict(rpm=float(rpm), inflow_m_s=float(inflow), CT=float(CT), CP=float(CP),
                CQ=float(CQ), T_N=thrust, Q_Nm=torque, P_W=omega*torque, annuli=rows)


def main():
    geom, polar = geometry(), TutorialPolar()
    reference_alpha = np.array([
        2.0022243728484095, 8.829422477953987, 8.870590912749018,
        7.52560914549595, 6.426689255291592, 5.428909664912407,
        4.831836218455918, 4.416757366128305, 4.18459393032332,
        4.10240858383191, 3.948108963919129, 3.9579344372819785,
        3.994888320432903, 4.067782228382873, 4.045789972893049,
        3.6912584138275917, 3.0401847819021457])
    result = operate(5400, 5., geom, polar)
    own_alpha = np.array([row['alpha_deg'] for row in result['annuli']])
    delta = own_alpha-reference_alpha
    angle_check = dict(reference_source='https://flow.byu.edu/CCBlade.jl/stable/tutorial/',
                       interior_stations=17, reference_alpha_deg=reference_alpha.tolist(),
                       calculated_alpha_deg=own_alpha.tolist(), delta_alpha_deg=delta.tolist(),
                       max_absolute_difference_deg=float(abs(delta).max()),
                       chosen_verification_threshold_deg=.002,
                       passed=bool(abs(delta).max() < .002))
    # Bridge to the original C01 kernel at its own midpoint grid, unchanged.
    legacy = solve_design(.041, 190., cells=64)
    bridge = []
    for row in legacy['annuli']:
        new = solve_annulus(row['r_m'], row['chord_m'], row['beta_rad'], .041, .3*.041,
                            190/.041, 0., 8, 1.225, Polar())
        assert new['solve_success']
        bridge.append(new)
    dr = .041*.7/64
    bridge_T = sum(r['dT_dr_N_m'] for r in bridge)*dr
    bridge_Q = sum(r['dQ_dr_Nm_m'] for r in bridge)*dr
    bridge_result = dict(T_relative_change=bridge_T/legacy['T_isolated_model_N']-1,
                         Q_relative_change=bridge_Q/legacy['Q_isolated_model_Nm']-1,
                         max_alpha_difference_deg=float(max(abs(r['alpha_deg']-6) for r in bridge)))
    assert abs(bridge_result['T_relative_change']) < 1e-6
    assert abs(bridge_result['Q_relative_change']) < 1e-6
    static_data = np.loadtxt(HERE/'benchmark_apc/apce_10x5_static_pg0819.txt', skiprows=1)
    comparison = []
    full = []
    for rpm, measured_CT, measured_CP in static_data:
        value = operate(rpm, 0., geom, polar)
        full.append(value)
        comparison.append(dict(rpm=float(rpm), CT_measured=float(measured_CT), CP_measured=float(measured_CP),
                               CT_model=value['CT'], CP_model=value['CP'],
                               CT_relative_error=value['CT']/measured_CT-1,
                               CP_relative_error=value['CP']/measured_CP-1))
    with (OUT/'COMPARACION_ESTATICA.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=comparison[0].keys())
        writer.writeheader(); writer.writerows(comparison)
    report = dict(scope='Independent equation crosscheck plus approximate experimental contrast; not installed rotor validation',
                  published_angle_check=angle_check, original_C01_hover_bridge=bridge_result,
                  tutorial_operating_result=result, static_cases=len(comparison),
                  static_CT_mean_abs_relative_error=float(np.mean([abs(r['CT_relative_error']) for r in comparison])),
                  static_CP_mean_abs_relative_error=float(np.mean([abs(r['CP_relative_error']) for r in comparison])),
                  CP_definition='P/(rho*n^3*D^5) = 2*pi*CQ; prose formula in tutorial has the reciprocal typo; its source-code conversion uses multiplication.',
                  static_model_operation=full, physical_rotor_validation_accepted=False,
                  experimental_contrast_limitations=[
                      'Single corrected/computational NACA4412 polar; AlphaAF ignores actual Reynolds/Mach variation.',
                      'Vendor describes E63/Clark-Y-like blends, so the tutorial airfoil is an approximation, not verified specimen geometry.',
                      'UIUC digitised chord/twist, assumed hub radius0.1R, trapezoid endpoint closure; no complete 3D specimen.',
                      'No duct, high-solidity cascade, SD8020, reverse thrust, transonic tip or actuator dynamics validation.',
                      'Official APC 202602 geometry archive download again returned HTTP403; no complete geometry recovered.',
                  ], source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in OUT.iterdir() if p.suffix in ('.dat', '.jl', '.md')})
    (OUT/'CONTRASTE.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: report[k] for k in ('published_angle_check', 'original_C01_hover_bridge',
                     'static_cases', 'static_CT_mean_abs_relative_error', 'static_CP_mean_abs_relative_error',
                     'physical_rotor_validation_accepted')}, indent=2))
    assert angle_check['passed'], 'Preserve failed comparison and investigate, do not fit a correction'


if __name__ == '__main__':
    main()
