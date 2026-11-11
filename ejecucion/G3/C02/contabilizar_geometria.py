"""Partial C02 mass/inertia sensitivity from actual STEP, with unknowns blank.

Assigned densities are hypotheses; aggregate properties omit unknown hardware
and are NOT a flight mass, CG, tensor or a certified lower bound.
"""
from pathlib import Path
import csv
import hashlib
import json
import sys

import cadquery as cq
import numpy as np
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'configuraciones'))
from base import inertia_cad_to_flu, vectors_cad_to_flu


def density(name,scope,case):
    envelope={'ligera_1200':1200.,'mixta_1600':1600.,'aluminio_2700':2700.}[case]
    if name.startswith('modulo_C02_'):
        n=name.split('_',3)[3]
        if n.startswith('reserva_'):return None,'unknown_device_or_interface'
        if n.startswith('eje_rotor_'):return 7800.,'shaft_steel_density_assumption'
        if n.startswith('casquillo_'):return (1200. if case=='ligera_1200' else 8800.),'bushing_material_sensitivity'
        if n.startswith(('alabe_integral_','barra_sincrona_','acoplamiento_servo_')):
            return (1200. if case=='ligera_1200' else 2700.),'integral_vane_linkage_material_sensitivity'
        return envelope,'rotor_or_carrier_material_sensitivity'
    if scope in {'representative_rotor_motor','actuator_package_motion_transmission_pending',
        'direct_drive_actuator_package_unselected','bearing_envelope_not_selected_hardware',
        'rear_interface_not_sized_nozzle','empty_axial_packaging_interface_not_propulsor'}:
        return None,'unknown_hardware_or_empty_interface'
    if 'eje_' in name or name.startswith('vis_'):return 7800.,'steel_density_assumption'
    if name.startswith(('junta_','abrazadera_')):return 1200.,'seal_or_clamp_density_assumption'
    if name.startswith(('cuaderna_','soporte_')):return 2700.,'frame_support_density_assumption'
    return envelope,'envelope_material_sensitivity'


def main():
    folder=HERE/'integracion_x160'
    source=folder/'C02_integracion_x160_5kg_cerrado_CANDIDATA.step'
    scopes={r['name']:r['scope'] for r in csv.DictReader((ROOT/'ejecucion/G1/BOM_GEOMETRICA_5kg.csv').open())}
    props=[];bom=[]
    for shape,name,loc,color in cq.Assembly.load(str(source)):
        name=name.split('/')[-1];shape=shape.moved(loc)
        g=GProp_GProps();error=BRepGProp.VolumeProperties_s(shape.wrapped,g,1e-8,True,False)
        matrix=g.MatrixOfInertia();c=g.CentreOfMass()
        inertia=np.array([[matrix.Value(i+1,j+1) for j in range(3)] for i in range(3)])*1e-15
        scope=scopes.get(name,'new_C02_geometry_unqualified')
        record=dict(name=name,scope=scope,volume_m3=g.Mass()*1e-9,
            centre_m=np.array([c.X(),c.Y(),c.Z()])*.001,inertia_per_density=inertia)
        props.append(record)
        rho,role=density(name,scope,'mixta_1600')
        bom.append(dict(name=name,scope=scope,volume_mm3=g.Mass(),
            x_CAD_m=c.X()*.001,y_CAD_m=c.Y()*.001,z_CAD_m=c.Z()*.001,
            integration_error_estimate=error,assumed_role=role,
            rho_mixta_ASSUMED_kg_m3='' if rho is None else rho,
            assigned_mass_mixta_kg='' if rho is None else rho*record['volume_m3'],
            actual_mass_kg='',actual_material='',actual_hardware_qualified=False))
    assert len(props)==316
    with (folder/'BOM_GEOMETRICA_PARCIAL.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(bom[0]));w.writeheader();w.writerows(bom)
    scenarios=[]
    for case in ('ligera_1200','mixta_1600','aluminio_2700'):
        mass=0.;moment=np.zeros(3);inertia_origin=np.zeros((3,3));unknown=[]
        for p in props:
            rho,role=density(p['name'],p['scope'],case)
            if rho is None:unknown.append(p['name']);continue
            m=rho*p['volume_m3'];c=p['centre_m']
            mass+=m;moment+=m*c
            inertia_origin+=rho*p['inertia_per_density']+m*(np.dot(c,c)*np.eye(3)-np.outer(c,c))
        cg=moment/mass
        inertia_cg=inertia_origin-mass*(np.dot(cg,cg)*np.eye(3)-np.outer(cg,cg))
        assert np.linalg.eigvalsh(inertia_cg).min()>0
        scenarios.append(dict(hypothesis=case,partial_assigned_mass_kg=mass,
            provisional_reserve_kg=.75,remaining_for_energy_and_unidentified_hardware_kg=5-.75-mass,
            partial_assigned_CG_CAD_m=cg.tolist(),partial_assigned_CG_FLU_m=vectors_cad_to_flu(cg).tolist(),
            partial_inertia_about_assigned_CG_CAD_kgm2=inertia_cg.tolist(),
            partial_inertia_about_assigned_CG_FLU_kgm2=inertia_cad_to_flu(inertia_cg).tolist(),
            unidentified_part_records=len(unknown),unidentified_records=unknown,
            physical_mass_CG_and_inertia_closed=False))
    result=dict(source_STEP_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        geometry_records=len(props),hypotheses=scenarios,
        assumptions_are_not_measurements=True,
        note='Gross nominal part volumes; unresolved legacy joints may share material. Partial CG/inertia excludes hardware and energy and must not drive a physical flight simulator.',
        inertia_model_acceptance_for_predictive_flight=False)
    (folder/'MASA_INERCIA_PARCIAL.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('hypothesis','partial_assigned_mass_kg','remaining_for_energy_and_unidentified_hardware_kg','unidentified_part_records')} for r in scenarios],indent=2))


if __name__=='__main__':main()
