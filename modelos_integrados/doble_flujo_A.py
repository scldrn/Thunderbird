"""Packaging concept for downstream vane banks in BOTH flow directions.

No fan selection, pitch hub, seals, bearings or servo installation is validated.
The approved exterior is a presentation envelope, not a closed thin-wall model.
"""
from pathlib import Path
import json,math,hashlib
import numpy as np
import cadquery as cq

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'vectorizacion_A/CAD_doble_flujo';OUT.mkdir(exist_ok=True)
src=ROOT/'vectorizacion_A/CAD_integracion_coherente/A_integracion_conductos_coherentes.step'
style=(ROOT/'diseno_industrial_v2.py').read_text()
env={'__file__':str(ROOT/'diseno_industrial_v2.py')}
exec(compile(style.split('# Recessed fan ports')[0],str(ROOT/'diseno_industrial_v2.py'),'exec'),env)
outer=env['body']
positions=json.loads((ROOT/'vectorizacion_A/RESUMEN.json').read_text())['position_m']
centers=[(1000*p[0],1000*p[1]) for p in positions]
rows=[('inferior_X','X',-21.),('inferior_Y','Y',-39.),('superior_X','X',19.),('superior_Y','Y',37.)]
chord=16.;thickness=1.5;half=math.hypot(chord/2,thickness/2)

def vane(x,y,axis,z,offset,angle):
    span=2*math.sqrt(40**2-(abs(offset)+half)**2)-2
    c=np.array([x,y+offset,z]) if axis=='X' else np.array([x+offset,y,z])
    direction=np.array([1.,0,0]) if axis=='X' else np.array([0.,1,0])
    dims=[span,thickness,chord] if axis=='X' else [thickness,span,chord]
    s=cq.Workplane('XY').box(*dims).translate(tuple(c)).val()
    return s.rotate(cq.Vector(*c),cq.Vector(*(c+direction)),angle),c,direction,span

base=[]
for s,name,loc,color in cq.Assembly.load(str(src)):
    label=name.split('/')[-1]
    if label.startswith(('vector_alabe_','vector_eje_')):continue
    s=s.moved(loc)
    if label.startswith(('base_motor_','base_rotor_representativo_')):s=s.translate((0,0,-59))
    base.append(dict(name=label,shape=s,color=color))
assert len(base)==53
rotor_parts=[a['shape'] for a in base if a['name'].startswith('base_rotor_representativo')]
motor_parts=[a['shape'] for a in base if a['name'].startswith('base_motor_')]
def nearest(parts,x,y):
    s=min(parts,key=lambda a:math.hypot(a.Center().x-x,a.Center().y-y))
    assert math.hypot(s.Center().x-x,s.Center().y-y)<1e-5
    return s
rotors=[nearest(rotor_parts,x,y) for x,y in centers]
motors=[nearest(motor_parts,x,y) for x,y in centers]
rotor_motor_outside=[s.cut(outer).Volume() for s in rotors+motors]
assert max(rotor_motor_outside)<1e-6
holes=[];shafts=[];blocks=[];checks=[]
for j,(x,y) in enumerate(centers):
    for row,axis,z in rows:
        for k,offset in enumerate([-22.,0,22.]):
            _,c,d,span=vane(x,y,axis,z,offset,0)
            shaft_length=2*math.sqrt(43.5**2-offset**2)
            shaft=cq.Solid.makeCylinder(1.2,shaft_length,cq.Vector(*(c-d*shaft_length/2)),cq.Vector(*d))
            bore_length=2*math.sqrt(43.8**2-offset**2)
            bore=cq.Solid.makeCylinder(1.35,bore_length,cq.Vector(*(c-d*bore_length/2)),cq.Vector(*d))
            shafts.append((j,row,k,shaft));holes.append(bore)
            dims=[span,2*half,2*half] if axis=='X' else [2*half,span,2*half]
            block=cq.Workplane('XY').box(*dims).translate(tuple(c)).val();blocks.append(block)
            outside=block.cut(outer).Volume()
            interference=max(block.intersect(s).Volume() for s in [rotors[j],motors[j]])
            checks.append(dict(channel=j,row=row,offset_mm=offset,span_mm=span,full_rotation_swept_box_outside_envelope_mm3=outside,swept_box_intersection_with_rotor_or_motor_mm3=interference,shaft_volume_outside_envelope_mm3=shaft.cut(outer).Volume()))
            assert outside<1e-6 and interference<1e-6 and checks[-1]['shaft_volume_outside_envelope_mm3']<1e-6
allholes=cq.Compound.makeCompound(holes)
for a in base:
    if a['name'].startswith(('base_cuerpo_principal','base_cubierta_superior','conducto_unificado')):
        a['shape']=a['shape'].cut(allholes)
        assert a['shape'].isValid()
ducts=[a['shape'] for a in base if a['name'].startswith('conducto_unificado')]
assert len(ducts)==4
ducts=[min(ducts,key=lambda a:math.hypot(a.Center().x-x,a.Center().y-y)) for x,y in centers]
# Clipped duct centroids differ from their axes; direct rotor intersections
# below check the paired geometry, rather than equating their centroids.
rotor_duct_intersections=[rotors[j].intersect(ducts[j]).Volume() for j in range(4)]
assert max(rotor_duct_intersections)<1e-6
shaft_wall_intersections=[]
for j,row,k,shaft in shafts:
    overlap=shaft.intersect(ducts[j]).Volume();shaft_wall_intersections.append(overlap);assert overlap<1e-6
exports=[];volumes={}
for pose in ['neutro','omni_diagonal']:
    assembly=cq.Assembly(name='A_doble_flujo_'+pose)
    for a in base:assembly.add(a['shape'],name=a['name'],color=a['color'] or cq.Color(.2,.22,.25))
    vv=0.;ss=0.
    for j,(x,y) in enumerate(centers):
        for row,axis,z in rows:
            selected=('inferior' in row) if j in [0,3] else ('superior' in row)
            angle=(35 if axis=='X' else -35) if pose=='omni_diagonal' and selected else 0
            for k,offset in enumerate([-22.,0,22.]):
                s,_,_,_=vane(x,y,axis,z,offset,angle);assert s.isValid();vv+=s.Volume()
                assembly.add(s,name=f'alabe_{j}_{row}_{k}',color=cq.Color(.18,.26,.29))
    for j,row,k,shaft in shafts:
        ss+=shaft.Volume();assembly.add(shaft,name=f'eje_{j}_{row}_{k}',color=cq.Color(.5,.52,.54))
    path=OUT/(pose+'.step');assembly.save(str(path))
    imported=[s.moved(loc) for s,_,loc,_ in cq.Assembly.load(str(path))]
    assert len(imported)==149 and all(s.isValid() for s in imported)
    exports.append(dict(file=path.name,valid_reimported_parts=len(imported)))
    volumes=dict(vanes_mm3=vv,shafts_mm3=ss,ducts_mm3=sum(s.Volume() for s in ducts))
densities=dict(ducts_kgm3=1600,vanes_kgm3=1600,shafts_kgm3=7850)
masses={name.split('_')[0]+'_kg':volumes[name.split('_')[0]+'_mm3']*1e-9*rho for name,rho in densities.items()}
row_vane_volume=volumes['vanes_mm3']/16*1e-9
row_shaft_volume=volumes['shafts_mm3']/16*1e-9
Irow=densities['vanes_kgm3']*row_vane_volume*((chord/1000)**2+(thickness/1000)**2)/12+.5*densities['shafts_kgm3']*row_shaft_volume*.0012**2
inertia_demands=[]
for t in [.05,.1,.2,.5]:
    angle=math.pi/2;acc=4*angle/t**2;omega=2*angle/t
    inertia_demands.append(dict(stroke_deg=90,duration_s=t,bang_bang_peak_speed_deg_s=math.degrees(omega),bang_bang_acceleration_rad_s2=acc,vanes_and_shafts_only_inertial_torque_Nm=Irow*acc))
report=dict(source_step=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),rows=[dict(name=n,axis=a,z_mm=z) for n,a,z in rows],rotor_blade_plane_z_mm=7,motor_center_z_mm=-1,mechanical_angle_range_deg=[-45,45],row_to_row_full_sweep_gap_mm=18-2*half,row_to_motor_axial_gap_mm=19-half-9,max_rotor_motor_volume_outside_envelope_mm3=max(rotor_motor_outside),max_rotor_duct_overlap_mm3=max(rotor_duct_intersections),geometric_checks=checks,max_shaft_duct_overlap_mm3=max(shaft_wall_intersections),exports=exports,component_geometric_volumes=volumes,assumed_material_densities=densities,component_material_mass_scenarios=masses,total_three_component_material_mass_scenario_kg=sum(masses.values()),row_vanes_and_shafts_only_assumed_inertia_kgm2=Irow,row_inertial_demands=inertia_demands,actuated_rows=16,assumed_actuators_if_one_per_row=16,mechanical_flight_validation=False,excluded=['Actual reversible rotor/pitch hub and electrical power','Actuator, linkage, bearing and seal installation and mass','Aerodynamic hinge moments, pitch moments and transient flow','Mapping of mechanical vane angle to net force cone','Flow interaction of inactive inlet banks and neighbouring opposite jets','Full assembly interference audit and actual thin-wall structure','Manufacturing tolerances, deflection, fatigue and aeroelastic loads','High-speed doors and transition logic'])
(OUT/'VERIFICACION.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(output=str(OUT),valid_parts=149,swept_boxes=len(checks),row_gap_mm=report['row_to_row_full_sweep_gap_mm'],component_material_mass_scenario_kg=sum(masses.values()),inertia_row_assumed_kgm2=Irow)))
