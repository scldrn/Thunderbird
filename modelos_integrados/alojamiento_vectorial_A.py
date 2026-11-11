"""Geometric prototype of two-axis vane rows; no flow-to-angle calibration."""
from pathlib import Path
import json,math,numpy as np
import cadquery as cq
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'vectorizacion_A'/'CAD_modulo';OUT.mkdir(parents=True,exist_ok=True)
source=(ROOT/'diseno_industrial_v2.py').read_text();env={'__file__':str(ROOT/'diseno_industrial_v2.py')};exec(compile(source.split('# Recessed fan ports')[0],str(ROOT/'diseno_industrial_v2.py'),'exec'),env)
outer=env['body'];R=40.;chord=16.;thickness=1.5;rows=[('X',-12.),('Y',-40.)]
def vane(x,y,axis,z,offset,angle):
 maxhalf=math.hypot(chord/2,thickness/2);span=2*math.sqrt(R*R-(abs(offset)+maxhalf)**2)-2
 if axis=='X':
  c=np.array([x,y+offset,z]);d=[span,thickness,chord];a=cq.Vector(x,y+offset,z);b=cq.Vector(x+1,y+offset,z)
 else:
  c=np.array([x+offset,y,z]);d=[thickness,span,chord];a=cq.Vector(x+offset,y,z);b=cq.Vector(x+offset,y+1,z)
 sh=cq.Workplane('XY').box(*d).translate(tuple(c)).val().rotate(a,b,angle)
 return sh,span
centers=[(x,y) for x in [-280.,285.] for y in [-65.,65.]]
checks=[]
for x,y in centers:
 for axis,z in rows:
  for offset in [-22.,0,22.]:
   for angle in [-45,-30,-15,0,15,30,45]:
    sh,span=vane(x,y,axis,z,offset,angle);assert sh.isValid();outside=sh.cut(outer).Volume();rr=max(math.hypot(v.Center().x-x,v.Center().y-y) for v in sh.Vertices());checks.append(dict(x_mm=x,y_mm=y,row=axis,offset_mm=offset,angle_deg=angle,span_mm=span,outside_envelope_mm3=outside,max_radius_mm=rr))
# Full-range analytical separation bound between rows, independent of their angles.
vertical_half=math.hypot(chord/2,thickness/2);row_gap=abs(rows[1][1]-rows[0][1])-2*vertical_half
swept_checks=[]
for x,y in centers:
 for axis,z in rows:
  for offset in [-22.,0,22.]:
   _,span=vane(x,y,axis,z,offset,0)
   size=[span,2*vertical_half,2*vertical_half] if axis=='X' else [2*vertical_half,span,2*vertical_half]
   center=[x,y+offset,z] if axis=='X' else [x+offset,y,z]
   block=cq.Workplane('XY').box(*size).translate(tuple(center)).val()
   swept_checks.append(block.cut(outer).Volume())
assert row_gap>0 and max(a['max_radius_mm'] for a in checks)<R
for pose,angles in [('neutro',(0,0)),('desviado',(35,-35))]:
 ass=cq.Assembly(name='A_modulo_vectorial_'+pose)
 for j,(x,y) in enumerate(centers):
  for i,(axis,z) in enumerate(rows):
   for k,offset in enumerate([-22.,0,22.]):
    sh,span=vane(x,y,axis,z,offset,angles[i]);ass.add(sh,name=f'alabe_{j}_{axis}_{k}',color=cq.Color(.2,.3,.35))
    if axis=='X':start=[x-span/2-3,y+offset,z];direction=[1,0,0]
    else:start=[x+offset,y-span/2-3,z];direction=[0,1,0]
    pin=cq.Solid.makeCylinder(1.2,span+6,cq.Vector(*start),cq.Vector(*direction));ass.add(pin,name=f'eje_{j}_{axis}_{k}',color=cq.Color(.5,.52,.54))
  duct=cq.Solid.makeCylinder(44,125,cq.Vector(x,y,-65),cq.Vector(0,0,1)).cut(cq.Solid.makeCylinder(42,129,cq.Vector(x,y,-67),cq.Vector(0,0,1))).intersect(outer)
  ass.add(duct,name=f'conducto_{j}',color=cq.Color(.2,.22,.25))
 ass.save(str(OUT/(pose+'.step')))
# A separate one-channel assembly for inspecting vanes and shafts without external casing.
result=dict(samples=len(checks),max_vane_volume_outside_body_mm3=max(a['outside_envelope_mm3'] for a in checks),max_radial_extent_mm=max(a['max_radius_mm'] for a in checks),min_radial_clearance_to_42mm_bore_mm=42-max(a['max_radius_mm'] for a in checks),row_vertical_separation_lower_bound_mm=row_gap,rotor_blade_plane_z_mm=66,upper_row_max_z_mm=rows[0][1]+vertical_half,max_swept_box_outside_body_mm3=max(swept_checks),assumed_angles_deg=[-45,45],excluded=['shaft radial containment and body clearance','bearings','servo envelopes','transmission/linkages','flow-path blockage by other components','vane structural/aerodynamic loads','flow deflection calibration','manufacturing tolerances','mass and torque budget'])
(OUT/'CHEQUEOS.json').write_text(json.dumps(checks,indent=2));(OUT/'RESUMEN.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
# Separate integration branch: through-passages in the presentation envelopes.
base=cq.Assembly.load(str(ROOT/'diseno_industrial_v2/diseno_industrial_v2.step'))
assembly=cq.Assembly(name='A_integracion_vectorial_preliminar')
for shape,name,loc,color in base:
 label=name.split('/')[-1];shape=shape.moved(loc)
 if label.startswith(('cubierta_superior','cuerpo_principal')):
  for x,y in centers:shape=shape.cut(cq.Solid.makeCylinder(42,320,cq.Vector(x,y,-160),cq.Vector(0,0,1)))
 assert shape.isValid();assembly.add(shape,name='base_'+label,color=color or cq.Color(.15,.18,.2))
module=cq.Assembly.load(str(OUT/'neutro.step'))
for shape,name,loc,color in module:
 shape=shape.moved(loc);assert shape.isValid();assembly.add(shape,name='vector_'+name.split('/')[-1],color=color or cq.Color(.3,.35,.4))
assembly.save(str(OUT/'integracion_preliminar.step'))
# Reopen exported assemblies and check solid validity; not engineering approval.
validation=[]
for file in ['neutro.step','desviado.step','integracion_preliminar.step']:
 a=cq.Assembly.load(str(OUT/file));shapes=[s.moved(loc) for s,name,loc,color in a];assert all(s.isValid() for s in shapes);validation.append(dict(file=file,valid=True,parts=len(shapes)))
(OUT/'VERIFICACION_STEP.json').write_text(json.dumps(validation,indent=2));print(validation)
