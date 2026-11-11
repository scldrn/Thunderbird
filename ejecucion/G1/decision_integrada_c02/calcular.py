"""Conditional electric-mission mass screen using C02 partial BOM only.

Rotor powers are inherited exploratory C01 values, not an installed fan map.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MASS=ROOT/'G3/C02/integracion_x160/MASA_INERCIA_PARCIAL.json'
OPS=ROOT/'G2/modulo_preliminar/OPERACION_CONDICIONAL.csv'
AIRCRAFT_KG=5.
HOVER_W=2968.8083465960835
LATERAL_W=3505.892708058721


def mission(mass_kg, speed_kmh, drag_final_N, acceleration_s, hover_s, fast_s,
            hover_W, maneuver_W, maneuver_s, efficiency, energy_Wh_kg, power_W_kg):
    assert mass_kg>0 and speed_kmh>0 and drag_final_N>=0 and acceleration_s>0
    assert hover_s>=maneuver_s>=0 and fast_s>=0 and 0<efficiency<=1
    assert energy_Wh_kg>0 and power_W_kg>0
    v=speed_kmh/3.6
    # Prescribed constant acceleration, D(v)=D_final*(v/V)^2; no ascent/turns.
    kinetic=.5*mass_kg*v*v
    accelerating_drag=drag_final_N*v*acceleration_s/4
    cruise_drag=drag_final_N*v*fast_s
    hover_energy=(hover_W*(hover_s-maneuver_s)+maneuver_W*maneuver_s)/3600
    fast_energy=(kinetic+accelerating_drag+cruise_drag)/(3600*efficiency)
    axial_peak=(mass_kg*v*v/acceleration_s+drag_final_N*v)/efficiency
    active_hover_peak = hover_W if hover_s > maneuver_s else 0.0
    active_maneuver_peak = maneuver_W if maneuver_s > 0 else 0.0
    pack_peak=max(active_hover_peak, active_maneuver_peak, axial_peak)
    pack_energy=hover_energy+fast_energy
    battery_energy_kg=pack_energy/energy_Wh_kg
    battery_power_kg=pack_peak/power_W_kg
    return dict(speed_kmh=speed_kmh,drag_final_N_assumed=drag_final_N,
        acceleration_s_assumed=acceleration_s,hover_s=hover_s,fast_cruise_s=fast_s,
        kinetic_Wh=kinetic/3600,acceleration_drag_Wh=accelerating_drag/3600,
        cruise_drag_Wh=cruise_drag/3600,hover_electric_Wh=hover_energy,
        forward_electric_Wh=fast_energy,total_electric_Wh=pack_energy,
        axial_electric_peak_W=axial_peak,pack_electric_peak_W=pack_peak,
        battery_energy_constraint_kg=battery_energy_kg,battery_power_constraint_kg=battery_power_kg,
        battery_min_for_assumed_limits_kg=max(battery_energy_kg,battery_power_kg))


def main():
    # Independent exact special cases catch energy/power and unit mistakes.
    q=mission(5.,360.,0.,10.,0.,0.,0.,0.,0.,1.,100.,1000.)
    assert math.isclose(q['kinetic_Wh'],.5*5*100**2/3600)
    assert math.isclose(q['axial_electric_peak_W'],5*100**2/10)
    q=mission(5.,360.,40.,10.,0.,20.,0.,0.,0.,1.,100.,1000.)
    assert math.isclose(q['acceleration_drag_Wh'],40*100*10/4/3600)
    assert math.isclose(q['cruise_drag_Wh'],40*100*20/3600)
    assert math.isclose(q['battery_min_for_assumed_limits_kg'],max(q['battery_energy_constraint_kg'],q['battery_power_constraint_kg']))
    data=json.loads(MASS.read_text())
    hypotheses=[h for h in data['hypotheses'] if h['hypothesis'] in ('ligera_1200','mixta_1600')]
    assert len(hypotheses)==2 and all(h['unidentified_part_records']==54 for h in hypotheses)
    ops=list(csv.DictReader(OPS.open()))
    # Guard against unintended change in the frozen C01 source data.
    for label,expected in [('hover',HOVER_W),('lateral_0_5g_fixed_attitude',LATERAL_W)]:
        matches=[r for r in ops if r['case_id']=='m5_d1_k0.85' and r['maneuver']==label]
        assert len(matches)==1 and math.isclose(float(matches[0]['electrical_W_eta_0_9_ASSUMED']),expected,rel_tol=1e-12)
    cases=[]
    for h in hypotheses:
        for speed in (600.,1000.):
            for drag in (25.,50.,100.):
                for accel in (10.,30.,60.):
                    for hover in (30.,120.):
                        for cruise in (30.,120.):
                            row=mission(AIRCRAFT_KG,speed,drag,accel,hover,cruise,HOVER_W,LATERAL_W,3.,.7,150.,5000.)
                            row.update(mass_hypothesis=h['hypothesis'],partial_geometry_kg=h['partial_assigned_mass_kg'],
                                reserve_kg=h['provisional_reserve_kg'],battery_specific_energy_Wh_kg_assumed=150.,
                                battery_specific_power_W_kg_assumed=5000.,axial_electric_efficiency_assumed=.7,
                                remaining_for_unidentified_hardware_kg=AIRCRAFT_KG-h['partial_assigned_mass_kg']-h['provisional_reserve_kg']-row['battery_min_for_assumed_limits_kg'],
                                installed_capability_demonstrated=False)
                            cases.append(row)
    assert len(cases)==144
    out=HERE/'ESCENARIOS.csv'
    assert not out.exists()
    with out.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
    thresholds=[]
    for h in hypotheses:
        available=AIRCRAFT_KG-h['partial_assigned_mass_kg']-h['provisional_reserve_kg']
        for speed in (600.,1000.):
            v=speed/3.6
            for accel in (10.,30.,60.,None):
                inertial_power=AIRCRAFT_KG*v*v/accel if accel is not None else 0.
                d_limit=(.7*5000.*available-inertial_power)/v
                thresholds.append(dict(mass_hypothesis=h['hypothesis'],speed_kmh=speed,
                    acceleration_s=accel,maximum_endpoint_drag_N_for_power_only=d_limit,
                    all_remaining_mass_assigned_to_battery=True,
                    unaccounted_hardware_mass_kg_assumed_for_this_bound=0.,
                    negative_means_even_zero_drag_fails_this_power_hypothesis=d_limit<0))
    report=dict(scope='Conditional 5 kg C02, all-electric hypothetical sensitivity; no motor, battery, drag or mass closure',
        cases=len(cases),tests_pass=True, physical_acceptance=False,source_partial_mass_not_lower_bound=True,
        no_C01_rotor_mass_added_to_C02_BOM=True, BEM_hover_and_maneuver_are_exploratory_unvalidated=True,
        maneuver_is_0p5g_lateral_at_fixed_attitude_3s_assumed=True,
        forward_force_scaling='D(v)=Dfinal*(v/V)^2, straight constant acceleration, no thrust lag',
        propulsion_modes_are_sequential=True, kinetic_energy_not_double_counted=True, no_regenerative_recovery=True,
        unknown_hardware_kg_not_zero_or_added=True, remaining_positive_not_proof_of_feasibility=True,
        limitations=['C01 rotor hover powers do not validate C02 installed loads or reversed flow.',
                     'Battery usable specific energy and peak power are simultaneous assumptions, not an identified pack.',
                     'Drag values are sensitivity inputs, not predicted C02 drag; no lift, trimming or transition losses.',
                     'No motor/ESC/actuators/cooling/fast-propulsion unit/sensors/wiring masses included.',
                     'No peak time derating, voltage/current, thermal or structural margins.',
                     'Battery provides hover and axial propulsion; hybrid/turbine architectures not screened by these rows.',
                     'Mass budget uses partial nominal geometric volumes, not a certified or lower-bound mass.'],
        conditional_power_only_drag_thresholds=thresholds,
        source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (MASS,OPS,Path(__file__).resolve())})
    (HERE/'METODO.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    for row in cases:
        if row['speed_kmh']==600 and row['drag_final_N_assumed']==50 and row['acceleration_s_assumed'] in (10,60) and row['hover_s']==30 and row['fast_cruise_s']==30:
            print(row['mass_hypothesis'],row['acceleration_s_assumed'],'peak_kW',round(row['pack_electric_peak_W']/1000,2),'battery_kg',round(row['battery_min_for_assumed_limits_kg'],3),'remaining_kg',round(row['remaining_for_unidentified_hardware_kg'],3))


if __name__=='__main__':main()
