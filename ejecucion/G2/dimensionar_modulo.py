"""Size conditional isolated rotor candidates and keep all domain warnings.

Every diameter/mass hypothesis has its own inverse twist at the hover design
point. Maneuver points reuse that twist; they do not silently redesign blades.
"""
from pathlib import Path
import csv
import hashlib
import json
import sys

import numpy as np
from scipy.optimize import brentq

from bem_hover import Polar, solve_design

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'configuraciones'))
from base import load_baseline

OUT = HERE / 'modulo_preliminar'
OUT.mkdir(exist_ok=True)
(OUT/'operacion_annular').mkdir(exist_ok=True)


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    cfg = load_baseline(verify_geometry=True)
    rho = cfg['operating_reference']['rho_kg_m3']
    g = cfg['operating_reference']['g_m_s2']
    polar = Polar()
    studies, battery_rows, refinements = [], [], []
    n_cells = 64
    for mass in (2, 5, 10):
        s = cfg['geometry'][str(mass)]['scale_from_5kg']
        for diameter_factor in (1., 1.25, 1.5):
            radius = .041*s*diameter_factor
            for force_transfer in ((.7, .85, 1.) if diameter_factor == 1 else (.85,)):
                case_id = f'm{mass}_d{diameter_factor:g}_k{force_transfer:g}'
                target_hover = mass*g/4/force_transfer
                def inverse(speed):
                    return solve_design(radius, speed, cells=n_cells, rho=rho, polar=polar)
                speed = brentq(lambda x: inverse(x)['T_isolated_model_N']-target_hover,
                               60, 360, xtol=1e-4)
                design = inverse(speed)
                assert design['all_annular_balances_converged']
                beta = np.array([r['beta_rad'] for r in design['annuli']])
                detail = dict(case_id=case_id, config_id=cfg['id'], mass_target_kg=mass,
                              diameter_factor=diameter_factor, force_transfer_ASSUMED=force_transfer,
                              design=design, installed_map_validated=False)
                (OUT / f'{case_id}.json').write_text(json.dumps(detail, indent=2)+'\n')
                for name, multiplier, theta in (
                    ('hover', 1., 0.),
                    ('lateral_0_5g_fixed_attitude', np.sqrt(1.25), np.degrees(np.arctan(.5))),
                    ('vertical_up_1g', 2., 0.),
                ):
                    target = target_hover*multiplier
                    if name == 'hover':
                        op = design
                    else:
                        def fixed(v):
                            return solve_design(radius, v, cells=n_cells, rho=rho, polar=polar, fixed_beta_rad=beta)
                        lo, hi = speed, speed*np.sqrt(multiplier)*1.35
                        op_speed = brentq(lambda v: fixed(v)['T_isolated_model_N']-target, lo, hi, xtol=1e-4)
                        op = fixed(op_speed)
                    assert op['all_annular_balances_converged']
                    assert abs(op['T_isolated_model_N']-target)/target < 1e-5
                    assert op['energy_identity_relative_residual'] < 1e-12
                    (OUT/'operacion_annular'/f'{case_id}_{name}.json').write_text(json.dumps(dict(
                        case_id=case_id, maneuver=name, fixed_twist_source=f'{case_id}.json',
                        target_isolated_thrust_N=float(target), result=op,
                        installed_map_validated=False),indent=2)+'\n')
                    r = dict(case_id=case_id, mass_target_kg=mass, diameter_factor=diameter_factor,
                             force_transfer_ASSUMED=force_transfer, maneuver=name,
                             rotor_diameter_mm=2000*radius, bore_if_scaled_mm=84*s*diameter_factor,
                             fan_count=4, tilt_force_deg_REQUIRED=theta,
                             torque_or_CG_reserve_included=False,
                             target_net_module_force_N=mass*g/4*multiplier,
                             rotor_T_model_N=op['T_isolated_model_N'], rpm_model=op['rpm'],
                             tip_speed_m_s=op['tip_rotational_speed_m_s'], Mach_tip=op['Mach_tip_rotational'],
                             four_rotor_shaft_model_W=4*op['shaft_model_W'],
                             electrical_W_eta_0_9_ASSUMED=4*op['shaft_model_W']/.9,
                             Q_per_rotor_model_Nm=op['Q_isolated_model_Nm'],
                             FM_free_rotor_model=op['free_rotor_model_FM'],
                             outside_polar_thrust_fraction=op['outside_polar_thrust_fraction'],
                             outside_polar_torque_fraction=op['outside_polar_torque_fraction'],
                             Mach_gt_0_3_torque_fraction=op['Mach_gt_0_3_torque_fraction'],
                             max_local_solidity=op['max_local_solidity'],
                             projected_chord_over_pitch_max=op['projected_chord_over_pitch_max'],
                             installed_performance_validated=False)
                    studies.append(r)
                    power = r['electrical_W_eta_0_9_ASSUMED']
                    if name == 'hover' and force_transfer == .85:
                        for seconds in (30, 120, 300):
                            for energy_wh_kg in (100, 150, 200):
                                for specific_power_w_kg in (2000, 5000, 10000):
                                    energy_mass = power*seconds/3600/energy_wh_kg
                                    power_mass = power/specific_power_w_kg
                                    battery_rows.append(dict(case_id=case_id, mass_target_kg=mass,
                                        duration_s=seconds, usable_energy_Wh_kg_ASSUMED=energy_wh_kg,
                                        pack_specific_power_W_kg_ASSUMED=specific_power_w_kg,
                                        energy_required_Wh=power*seconds/3600,
                                        energy_constraint_mass_kg=energy_mass, power_constraint_mass_kg=power_mass,
                                        combined_pack_mass_reference_kg=max(energy_mass, power_mass),
                                        pack_qualified=False))
                print(case_id, 'design saved', flush=True)
                if mass == 5 and diameter_factor == 1 and force_transfer == .85:
                    refined = solve_design(radius, speed, cells=128, rho=rho, polar=polar)
                    refinements.append(dict(case_id=case_id,
                        relative_T_difference_64_to_128=abs(design['T_isolated_model_N']/refined['T_isolated_model_N']-1),
                        relative_P_difference_64_to_128=abs(design['shaft_model_W']/refined['shaft_model_W']-1)))
                    assert max(refinements[-1][k] for k in refinements[-1] if k != 'case_id') < .005
    write_csv(OUT/'OPERACION_CONDICIONAL.csv', studies)
    write_csv(OUT/'BATERIA_ENERGIA_Y_POTENCIA.csv', battery_rows)
    summary = dict(config_id=cfg['id'], design_cases=15, operating_cases=len(studies),
                   battery_sensitivities=len(battery_rows), radial_quadrature_checks=refinements,
                   source_polar_sha256=hashlib.sha256(polar.path.read_bytes()).hexdigest(),
                   algorithm_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'bem_hover.py',Path(__file__))},
                   installed_performance_validated=False, unknown_hardware_mass_is_not_zero=True,
                   assumptions=dict(blades=8, root_ratio=.30, inverse_design_alpha_deg=6,
                                    electrical_efficiency=.9, force_transfer_factors=[.7,.85,1.],
                                    nonphysical_hardware_approval=False),
                   limitations=[
                       'Each candidate is a theoretical isolated free rotor, not an installed fan map.',
                       'Mach >.3 contribution flagged; no compressible polar/cascade/rotating correction validated.',
                       'Endpoint polar extension is flagged, not accepted experimental coverage.',
                       'High local solidity requires cascade/interblade and 3D validation.',
                       'Force transfer factor is a sensitivity, not measured duct/vane efficiency or a universal upper bound.',
                       'No motor/ESC/battery/thermal/RPM/structure approval; no negative-thrust map.',
                       'Body forces/moments, CG offset, gyro, ground/crosswind effects and transition not included.',
                       'Enlarged rotors require new ducts, doors, support/axial-route CAD and mass/aero reanalysis.',
                   ])
    assert len(studies) == 45 and len(battery_rows) == 243
    (OUT/'RESUMEN.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
