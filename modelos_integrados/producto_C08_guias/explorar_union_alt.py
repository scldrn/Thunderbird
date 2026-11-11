"""Screen straight candidate links from two rail axes to one closed cover.

The selected rails are space reservations, not mounted guides. Contact with the
cover and rail is intended; no slider, pin, or actuator is modeled. Candidates
are sampled from the tessellated cover surface, not a global optimization.
"""
from pathlib import Path
import json,math
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent
best=json.loads((H/'COMPARACION_PARES.json').read_text())['pairs'][0]
pair={'left_y_mm':best['left']['y_mm'],'left_z_mm':best['left']['z_mm'],'right_y_mm':best['right']['y_mm'],'right_z_mm':best['right']['z_mm']}
d=App.openDocument(str(H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
objs=[o for o in d.Objects if o.Name.startswith('pieza_')]
p={o.Label:o.Shape.copy() for o in objs}
door_name='compuerta_C02_0_superior';door=p[door_name]
priority=['carroceria_C02_superior004','modulo_C02_0_camisa_cuna_y_soportes','aro_C02_0_superior','junta_C02_0_superior','modulo_C02_0_rotor_copa']
names=priority+[o.Label for o in objs if o.Label not in priority and o.Label!=door_name]
assert len(names)==315 and len(set(names))==315
boxes={}
for n in names:
 b=p[n].optimalBoundingBox();b.enlarge(.05);boxes[n]=b
# Cylinder that contains all nominal rotor geometry in the current axle-aligned
# envelope; output audit records containment but not runout or deflection.
base=p['modulo_C02_0_rotor_copa'];bb=base.optimalBoundingBox()
xc=(bb.XMin+bb.XMax)/2;yc=(bb.YMin+bb.YMax)/2;radius=max(bb.XLength,bb.YLength)/2+.5
sweep=Part.makeCylinder(radius,bb.ZLength+1,App.Vector(xc,yc,bb.ZMin-.5),App.Vector(0,0,1))
rem=base.cut(sweep)
if rem.Volume>.001:raise ValueError('cilindro no contiene rotor')
bs=sweep.optimalBoundingBox();bs.enlarge(.05)
verts,faces=door.tessellate(.3)
samples=list(verts)
for ia,ib,ic in faces:
 a,b,c=verts[ia],verts[ib],verts[ic]
 for i,j in ((1,1),(1,2),(2,1),(1,3),(3,1),(2,2)):
  samples.append(a*(i/5)+b*(j/5)+c*(1-(i+j)/5))
out={'scope':'Barras rectas nominales en cerrado, candidatas muestreadas, contra registros C03 y barrido nominal de rotor 0; no conexion funcional ni barrido completo',
     'selected_pair':pair,'nominal_radius_mm':1.5,'x_anchor_mm':-160,'cases':[]}
for rail_y in (pair['left_y_mm'],pair['right_y_mm']):
 rail_z=pair['left_z_mm'] if rail_y==pair['left_y_mm'] else pair['right_z_mm']
 origin=App.Vector(-160,rail_y,rail_z);groups={}
 for v in samples:
  if abs(v.x+160)>4 or not(-122<v.y<-30):continue
  bin_y=round((v.y+120)/5)
  distance=(v-origin).Length
  if bin_y not in groups or distance<groups[bin_y][0]:groups[bin_y]=(distance,v)
 candidates=sorted(groups.values(),key=lambda a:a[0])[:18]
 for _,target in candidates:
  direction=target-origin;length=direction.Length;direction.normalize()
  link=Part.makeCylinder(1.5,length+2,origin,direction)
  box=link.optimalBoundingBox();box.enlarge(.05)
  record={'rail_y_mm':rail_y,'target_mm':[target.x,target.y,target.z],'length_mm':length+2,'tested':0,'boolean_count':0}
  # Attachment overlap is allowed and quantified, not treated as a designed joint.
  record['door_contact_volume_mm3']=link.common(door).Volume
  for n in names+['envolvente_giro_0']:
   shape=sweep if n=='envolvente_giro_0' else p[n];other_box=bs if n=='envolvente_giro_0' else boxes[n]
   record['tested']+=1
   if not box.intersect(other_box):continue
   record['boolean_count']+=1
   try:
    inter=link.common(shape)
    if not(inter.isNull() or inter.isValid()):raise ValueError('comun invalido')
    v=inter.Volume;dist=link.distToShape(shape)[0]
    if v>1e-5 or dist<=1e-6:
     record['obstruction']={'name':n,'volume_mm3':v,'distance_mm':dist};break
   except Exception as e:record['error']={'name':n,'detail':repr(e)};break
  record['clear_closed']=('obstruction' not in record and 'error' not in record and record['tested']==len(names)+1 and record['door_contact_volume_mm3']>1e-5)
  out['cases'].append(record)
 (H/'UNION_ALT_PARCIAL.json').write_text(json.dumps(out,indent=2)+'\n')
 print('UNIONES',rail_y,'casos',len(candidates),'libres',sum(c['clear_closed'] for c in out['cases'] if c['rail_y_mm']==rail_y),flush=True)
(H/'UNION_ALT.json').write_text(json.dumps(out,indent=2)+'\n')
print('UNION_ALT_COMPLETA',len(out['cases']),'libres',sum(c['clear_closed'] for c in out['cases']),flush=True)
