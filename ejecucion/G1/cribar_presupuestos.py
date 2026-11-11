"""Conditional geometry/material and ideal disk screening; no installed performance claims."""
from pathlib import Path
import csv, json, math
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
CFG=json.loads((ROOT/'configuraciones/A07_BASE.json').read_text())
rho=CFG['operating_reference']['rho_kg_m3'];g=CFG['operating_reference']['g_m_s2']
with (OUT/'BOM_GEOMETRICA_5kg.csv').open() as f:parts=list(csv.DictReader(f))
assert len(parts)==208
unknown_scopes={'representative_rotor_motor','actuator_package_motion_transmission_pending',
                'direct_drive_actuator_package_unselected','bearing_envelope_not_selected_hardware',
                'rear_interface_not_sized_nozzle'}

def assumed_density(part,case):
    n=part['name'];scope=part['scope']
    if scope in unknown_scopes or scope=='empty_axial_packaging_interface_not_propulsor':return None
    if 'eje_' in n or n.startswith('eje_control_') or n.startswith('vis_'):return 7800.
    if n.startswith(('junta_','abrazadera_')):return 1200.
    if n.startswith(('cuaderna_','soporte_')):return 2700.
    if 'alabe_' in n:return 1200. if case!='geometria_aluminio' else 2700.
    if case=='geometria_aluminio':return 2700.
    return 1600. if case=='envolvente_1600' else 1200.

material_cases=['envolvente_1200','envolvente_1600','geometria_aluminio']
rows=[]
for mass in (2,5,10):
    for case in material_cases:
        geometric_mass=0.
        for p in parts:
            density=assumed_density(p,case)
            if density is not None:geometric_mass+=float(p['volume_mm3'])*1e-9*density*mass/5
        pipe_volume=sum(float(p['volume_mm3'])*1e-9 for p in parts if p['scope']=='empty_axial_packaging_interface_not_propulsor')*mass/5
        for include_pipe in (False,True):
            pipe_mass=pipe_volume*2700 if include_pipe else 0.
            reserve=.15*mass
            rows.append(dict(mass_target_kg=mass,material_hypothesis=case,axial_pipe_as_aluminium=include_pipe,
                             nominal_geometry_mass_sensitivity_kg=geometric_mass,axial_pipe_sensitivity_kg=pipe_mass,
                             provisional_mass_reserve_kg=reserve,
                             remaining_for_ALL_unidentified_hardware_and_energy_kg=mass-reserve-geometric_mass-pipe_mass,
                             physical_mass_closed=False,
                             caveat='Gross nominal part volumes; potential joint overlaps not deducted. No approved materials, strengths, components or mass lower bound.'))
with (OUT/'MASA_SENSIBILIDAD.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

power=[];energy=[]
for mass in (2,5,10):
    scale=(mass/5)**(1/3);diam=.084*scale;area=4*math.pi*diam**2/4
    for vertical_accel_g in (0,.5,1):
        T=mass*g*(1+vertical_accel_g);vi=math.sqrt(T/(2*rho*area));ideal=T*vi
        power.append(dict(mass_target_kg=mass,free_disk_diameter_reference_m=diam,free_disks_total_area_m2=area,
                          upward_net_accel_g=vertical_accel_g,required_total_force_N=T,
                          ideal_isolated_disk_induced_velocity_ms=vi,ideal_isolated_disk_power_W=ideal,
                          scope='Reference unshrouded ideal disks with equal axial loading, NOT installed fan electrical power or universal ducted-fan lower bound.'))
        for effective_efficiency in (.4,.6,.8):
            electrical=ideal/effective_efficiency
            for duration in (30,120,300):
                Wh=electrical*duration/3600
                for usable in (100,150,200):
                    energy.append(dict(mass_target_kg=mass,upward_net_accel_g=vertical_accel_g,
                                       effective_efficiency_ASSUMED=effective_efficiency,duration_s=duration,
                                       usable_energy_Wh_kg_ASSUMED=usable,electrical_power_sensitivity_W=electrical,
                                       battery_energy_only_mass_kg=Wh/usable,
                                       scope='Energy-only sensitivity; does not verify pack power, heat, voltage, life or installed fan map.'))
with (OUT/'REFERENCIA_DISCO.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(power[0]));w.writeheader();w.writerows(power)
with (OUT/'ENERGIA_ESTACIONARIO_SENSIBILIDAD.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(energy[0]));w.writeheader();w.writerows(energy)

fast=[]
for speed in (600,1000):
    V=speed/3.6
    for D in (20,50,100,200):
        for efficiency in (.4,.6,.8):
            for duration in (30,120,300):
                powerW=D*V/efficiency
                for usable in (100,150,200):
                    fast.append(dict(speed_target_kmh=speed,drag_N_ASSUMED=D,overall_propulsive_efficiency_ASSUMED=efficiency,
                                     duration_s=duration,usable_energy_Wh_kg_ASSUMED=usable,
                                     electrical_power_sensitivity_W=powerW,battery_energy_only_mass_kg=powerW*duration/3600/usable,
                                     scope='Independent drag/efficiency/energy assumptions; not motor selection, actual drag, integrated mass or energy feasibility.'))
with (OUT/'ENERGIA_AVANCE_SENSIBILIDAD.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(fast[0]));w.writeheader();w.writerows(fast)

cones=[]
for angle in (15,30,35,40,45,60):
    cones.append(dict(cone_half_angle_ASSUMED_deg=angle,
                      maximum_additional_acceleration_ball_radius_g_NECESSARY=math.sin(math.radians(angle)),
                      maximum_horizontal_acceleration_at_fixed_altitude_g_NECESSARY=math.tan(math.radians(angle)),
                      caveat='Upward force cone, fixed horizontal attitude, no external aerodynamic force, unlimited magnitude; ignores moments and power. Necessary bounds, not sufficient performance.'))
(OUT/'LIMITES_GEOMETRICOS_CONO.json').write_text(json.dumps(cones,indent=2))

missing=[
 ('fan_motors',4,'Motor and bearings/cooling','unidentified'),
 ('rotors_and_hubs',4,'Blade geometry, retention and hub','unidentified'),
 ('fan_ESCs',4,'Voltage/current/thermal compatible controllers','unidentified'),
 ('vane_transmissions_and_actuators',None,'16 packaging proxies exist, actual architecture/count pending','unidentified'),
 ('tail_actuators',None,'4 packaging proxies, bearings/linkages pending','unidentified'),
 ('door_actuation_and_latches',None,'Eight doors with two-coordinate motion; drive topology pending','unidentified'),
 ('axial_propulsion_installation',None,'Engine, intake, exhaust, ECU, cooling/shielding and mount','unidentified'),
 ('battery_and_power_distribution',None,'Pack, BMS if appropriate, wiring, connectors and protection','unidentified'),
 ('fuel_system_if_combustion',None,'Tank, fuel, feed, pump, filters and thermal separation','conditional_unknown'),
 ('avionics_sensors_communications',None,'IMU, localization, compute, communication and telemetry','unidentified'),
 ('seals_fasteners_reinforcements',None,'Full mount and load path design, not only visible screws','unidentified'),
 ('payload_and_mission_equipment',None,'User payload not yet quantified','unidentified'),
]
with (OUT/'BOM_PENDIENTES.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['group','quantity_if_defined','scope','status','mass_kg','source'])
    for name,q,scope,status in missing:w.writerow([name,q,scope,status,'','No installed hardware data supplied; blank is unknown, not zero'])

# Analytic sanity checks for the formulas and the frame contract.
R=np.array(CFG['flight_body_frame']['R_flight_from_CAD']);assert np.allclose(R@R.T,np.eye(3)) and np.linalg.det(R)==1
assert np.allclose(R@np.array([-1,0,0]),[1,0,0])
assert abs(math.sqrt((5*g)/(2*rho*(4*math.pi*.084**2/4)))*(5*g)-power[3]['ideal_isolated_disk_power_W'])<1e-9
# Sample tangent points of a force ball to verify asin(r/g) geometrically.
r=.5;z=1-r*r;x=r*math.sqrt(1-r*r);assert abs(math.degrees(math.atan2(x,z))-30)<1e-10
assert abs(math.sin(math.radians(30))-.5)<1e-12
summary=dict(config_id=CFG['id'],material_cases=len(material_cases),mass_sensitivity_cases=len(rows),hover_reference_cases=len(power),
             hover_energy_sensitivity_cases=len(energy),fast_energy_sensitivity_cases=len(fast),
             unidentified_hardware_groups=len(missing),cad_to_flight_rotation_verified=True,
             provisional_reserve_mass_fraction=.15,actual_mass_or_energy_closed=False,
             statement='Numerical references and conditional scenarios only. Neither feasibility nor impossibility of the entire architecture is established.')
(OUT/'CRIBADO_RESUMEN.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
for p in power:
    if p['upward_net_accel_g']==0:print('FREE_DISK_HOVER_REFERENCE',p['mass_target_kg'],round(p['ideal_isolated_disk_power_W'],1),'W')
for p in rows:
    if p['mass_target_kg']==5 and not p['axial_pipe_as_aluminium']:print('5kg_GEOMETRY_CASE',p['material_hypothesis'],round(p['nominal_geometry_mass_sensitivity_kg'],3),'kg; remaining',round(p['remaining_for_ALL_unidentified_hardware_and_energy_kg'],3),'kg')
