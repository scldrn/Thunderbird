"""Turn packaging envelopes into explicit, unqualified motor requirements.

C01 loads are applied as design scenarios, not accepted C02 installed loads.
The electrical loss includes the prescribed combined motor+ESC efficiency.
"""
from pathlib import Path
import csv
import json
import math

from crear_modulo import ROOT, parameters

HERE=Path(__file__).resolve().parent


def main():
    op=list(csv.DictReader((ROOT/'ejecucion/G2/modulo_preliminar/OPERACION_CONDICIONAL.csv').open()))
    rows=[];thermal=[]
    for factor in (1.,1.25):
        p=parameters(factor)
        height=p['motor_top']-p['motor_bottom']
        outer_volume=math.pi*p['motor_R']**2*height/1000 # cm3
        exposed_area=2*math.pi*(p['motor_R']*.001)*(height*.001)
        r_gap=.85*p['motor_R']*.001
        active_length=.7*height*.001
        strut_length=(p['R_in']-(p['motor_R']+1.6))*.001
        for r in op:
            if r['mass_target_kg']!='5' or float(r['diameter_factor'])!=factor or float(r['force_transfer_ASSUMED'])!=.85:continue
            shaft=float(r['four_rotor_shaft_model_W'])/4
            electrical=float(r['electrical_W_eta_0_9_ASSUMED'])/4
            torque=float(r['Q_per_rotor_model_Nm'])
            for voltage in (24.,48.):
                rows.append(dict(diameter_factor=factor,scenario=r['maneuver'],
                    motor_envelope_OD_mm=2*p['motor_R'],motor_envelope_height_mm=height,
                    gross_cylinder_volume_cm3=outer_volume,
                    shaft_requirement_W_C01=shaft,shaft_requirement_Nm_C01=torque,
                    rpm_requirement_C01=float(r['rpm_model']),
                    combined_conversion_loss_W_ASSUMED=electrical-shaft,
                    gross_shaft_power_density_requirement_W_cm3=shaft/outer_volume,
                    airgap_radius_m_ASSUMED=r_gap,active_length_m_ASSUMED=active_length,
                    mean_airgap_shear_requirement_Pa=torque/(2*math.pi*r_gap*r_gap*active_length),
                    DC_bus_voltage_V_ASSUMED=voltage,DC_module_input_A_ASSUMED=electrical/voltage,
                    DC_four_modules_A_ASSUMED=4*electrical/voltage,
                    motor_or_controller_qualified=False))
            for heat_share in (.5,1.):
                motor_loss=(electrical-shaft)*heat_share
                for h_effective in (100.,300.,1000.):
                    for k_strut in (1.,130.,200.):
                        # Optimistic direct exposure of the entire motor cylinder.
                        # Actual motor is inside a rotating cup; series resistances,
                        # contact, magnet/coil paths and cavity flow are not modeled.
                        g_air=h_effective*exposed_area
                        g_strut=4*k_strut*(2e-3*(p['support_top']-p['support_bottom'])*.001)/strut_length
                        conductance=g_air+g_strut
                        thermal.append(dict(diameter_factor=factor,scenario=r['maneuver'],
                            motor_share_of_conversion_loss_ASSUMED=heat_share,
                            motor_heat_W_ASSUMED=motor_loss,
                            effective_h_W_m2K_ASSUMED=h_effective,
                            strut_k_W_mK_ASSUMED=k_strut,
                            direct_exposed_cylinder_area_m2_OPTIMISTIC=exposed_area,
                            direct_air_conductance_W_K_OPTIMISTIC=g_air,
                            solid_strut_conductance_W_K_ASSUMED=g_strut,
                            total_conductance_W_K_OPTIMISTIC=conductance,
                            required_conductance_for_80K_W_K=motor_loss/80,
                            continuous_equilibrium_rise_K_OPTIMISTIC=motor_loss/conductance,
                            actual_motor_temperature_predicted=False))
    for filename,values in [('REQUISITOS_MOTOR.csv',rows),('CRIBADO_TERMICO_OPTIMISTA.csv',thermal)]:
        with (HERE/'salida'/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
    result=dict(motor_requirement_rows=len(rows),thermal_sensitivity_rows=len(thermal),
        rated_motor_hardware_selected=False,
        limits=['Envelope dimensions are available space, not evidence that a motor delivers the specified torque, speed or heat rejection.',
                'Airgap radius and active stack length are assumed fractions, not an electromagnetic design.',
                'DC current is input power/assumed voltage, not phase or winding current; no bus sag/R/L/back-EMF/control model.',
                'Loss split between motor and ESC is unknown; both heat-share scenarios are assumptions.',
                'Thermal estimate assumes direct exposure despite the motor being inside a cup. It is deliberately optimistic, not validated or a rigorous bound.',
                'Continuous equilibrium at a peak operating point is not the temperature of a 3-s maneuver.',
                'The 80-K rise is a sensitivity reference, not a material/component temperature rating.',
                'Missing: cooling paths/contact, coil/core/magnet losses, saturation, winding geometry, torque-speed map, bearings and rotor retention.'])
    (HERE/'salida/REQUISITOS_MOTOR.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
