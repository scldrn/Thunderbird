"""Couple existing geometric mass, new rotor CAD, and power/energy constraints.

5-kg target only. Partial budget, not a physical mass closure or battery choice.
"""
from pathlib import Path
import csv
import json
import math

HERE = Path(__file__).resolve().parent


def main():
    rows = list(csv.DictReader((HERE.parent/'G1/MASA_SENSIBILIDAD.csv').open()))
    reference = next(r for r in rows if r['mass_target_kg']=='5' and r['material_hypothesis']=='envolvente_1600' and r['axial_pipe_as_aluminium']=='False')
    fixed = float(reference['nominal_geometry_mass_sensitivity_kg'])
    reserve = float(reference['provisional_mass_reserve_kg'])
    ops = list(csv.DictReader((HERE/'modulo_preliminar/OPERACION_CONDICIONAL.csv').open()))
    geometry = json.loads((HERE/'modulo_preliminar/CAD/GEOMETRIA.json').read_text())
    results = []
    for factor, cad in zip((1.,1.25), geometry['candidates']):
        def point(name):
            return next(r for r in ops if r['mass_target_kg']=='5' and float(r['diameter_factor'])==factor and float(r['force_transfer_ASSUMED'])==.85 and r['maneuver']==name)
        hover = float(point('hover')['electrical_W_eta_0_9_ASSUMED'])
        # Increment only: simple four cylindrical walls H=.18m, t=.002m,
        # rho=1600. Original non-cylindrical A07 duct mass remains in fixed.
        original_wall = math.pi*((.042+.002)**2-.042**2)*.18*4*1600
        enlarged_wall = math.pi*((.042*factor+.002)**2-(.042*factor)**2)*.18*4*1600
        delta_duct = enlarged_wall-original_wall
        for total_s in (30,120,300):
            for peak_name, peak_s in (('hover',0),('lateral_0_5g_fixed_attitude',3),('vertical_up_1g',3)):
                peak = float(point(peak_name)['electrical_W_eta_0_9_ASSUMED'])
                energy = (hover*(total_s-peak_s)+peak*peak_s)/3600
                for specific_power in (2000,5000,10000):
                    usable_energy = 150.0
                    energy_mass = energy/usable_energy
                    power_mass = max(hover,peak)/specific_power
                    battery_mass = max(energy_mass,power_mass)
                    rotors_mass = 4*cad['nominal_rotor_mass_sensitivity_kg']
                    partial_total = fixed+reserve+rotors_mass+delta_duct+battery_mass
                    results.append(dict(diameter_factor=factor, duration_total_s=total_s,
                        peak_maneuver=peak_name, peak_duration_s_ASSUMED=peak_s,
                        usable_energy_Wh_kg_ASSUMED=usable_energy,
                        pack_specific_power_W_kg_ASSUMED=specific_power,
                        original_geometry_mass_sensitivity_kg=fixed,
                        provisional_reserve_kg=reserve,
                        four_rotors_mass_sensitivity_kg=rotors_mass,
                        cylindrical_duct_increment_sensitivity_kg=delta_duct,
                        hover_electrical_model_W=hover, peak_electrical_model_W=peak,
                        required_energy_model_Wh=energy,
                        battery_energy_constraint_kg=energy_mass,
                        battery_power_constraint_kg=power_mass,
                        combined_battery_mass_reference_kg=battery_mass,
                        partial_accounted_mass_kg=partial_total,
                        remaining_for_other_hardware_and_changes_kg=5-partial_total,
                        physical_mass_closed=False))
    path = HERE/'modulo_preliminar/MASA_MISION_5kg.csv'
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    assert len(results)==54
    summary=dict(cases=len(results),scope='Partial conditional mass-energy-power comparison, 5 kg target',
        all_original_unknown_hardware_still_pending=True,
        no_real_battery_or_material_selected=True,
        large_rotor_and_duct_mass_not_a_complete_redesign=True,
        limitations=['The 3-s peak is an analysis scenario, not a user-fixed mission or demonstrated maneuver.',
                     'Specific energy and specific power are simultaneous hypothetical pack requirements, not independently selectable measured battery properties.',
                     'No battery qualification, temperature, voltage sag, discharge history, ESC, motor or axial propulsion mass.',
                     'Duct increment excludes door/support/actuator/body changes; fixed geometry contains unapproved density and nominal overlaps.',
                     'Negative remainder rejects only this combined hypothesis; positive remainder does not demonstrate feasibility.'])
    (HERE/'modulo_preliminar/MASA_MISION_RESUMEN.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps([r for r in results if r['pack_specific_power_W_kg_ASSUMED']==5000 and r['peak_maneuver']=='hover'],indent=2))


if __name__=='__main__':
    main()
