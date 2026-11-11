"""Screen an ideal pivoted telescopic connector to a translating C07 cover.

Connector length and direction change between sampled poses. No joint,
actuator, stroke accommodation, attachment hardware or seal is designed.
"""
from pathlib import Path
import json,math
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent
prior=json.loads((H.parent/'producto_C09_paso_sellado/ENLACES.json').read_text())
rot=json.loads((H.parent/'producto_C08_guias/GUIAS.json').read_text())['rotor_sweep_audit']
d=App.openDocument(str(H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape.copy() for o in d.Objects if o.Name.startswith('pieza_')}
door_names=[f'compuerta_C02_{i}_{side}' for i in range(4) for side in ('superior','inferior')]
own='compuerta_C02_0_superior';allowed=prior['allowed_modification']
static={n:s for n,s in p.items() if n not in door_names and n!=allowed}
for i,r in enumerate(rot):
 x,y=r['center_mm'];static['envolvente_rotor_'+str(i)]=Part.makeCylinder(r['radius_mm'],r['height_mm'],App.Vector(x,y,r['zmin_mm']),App.Vector(0,0,1))
boxes={}
for name,sh in static.items():
 b=sh.optimalBoundingBox();b.enlarge(.05);boxes[name]=b
rails={-130:Part.makeCylinder(2.5,160,App.Vector(-280,-130,25),App.Vector(1,0,0)),
       -25:Part.makeCylinder(2.5,160,App.Vector(-280,-25,75),App.Vector(1,0,0))}
poses=[(0,0),(5,0),(10,0),(10,25),(10,50),(10,75),(10,100)]
cache={}
for lift,dx in poses:
 doors={}
 for n in door_names:
  _,_,i,side=n.split('_');sx=-1 if int(i)<2 else 1;sz=1 if side=='superior' else -1
  sh=p[n].copy();sh.translate(App.Vector(sx*dx,0,sz*lift));bb=sh.optimalBoundingBox();bb.enlarge(.05)
  doors[n]=(sh,bb)
 cache[(lift,dx)]=doors
candidates=[v for v in prior['cases'] if v['only_combined_duct_interference']]
results={'scope':'Enlace recto telescopico ideal: extremo de guia fijo, extremo tapa traslada. Siete poses discretas; se permite interseccion con camisa-cuna-soportes, no hay articulaciones ni sello.',
         'allowed':allowed,'cases':[]}
for c in candidates:
 y,z=c['rail_y_mm'],c['rail_z_mm'];anchor=App.Vector(-160,y,z);target0=App.Vector(*c['target_mm'])
 row={'rail_y_mm':y,'rail_z_mm':z,'target_mm':c['target_mm'],'poses':[]}
 for lift,dx in poses:
  target=target0+App.Vector(-dx,0,lift);direction=target-anchor;length=direction.Length;direction.normalize()
  sh=Part.makeCylinder(1.5,length+2,anchor,direction);bb=sh.optimalBoundingBox();bb.enlarge(.05)
  ownshape=cache[(lift,dx)][own][0]
  try:
   contact=sh.common(ownshape)
   if not(contact.isNull() or contact.isValid()):raise ValueError('contacto invalido')
   contactvol=contact.Volume
  except Exception as e:
   row['poses'].append({'lift_mm':lift,'dx_mm':-dx,'error':'contacto tapa '+str(e)});break
  record={'lift_mm':lift,'dx_mm':-dx,'length_mm':length+2,'contact_mm3':contactvol,'collision':None,'errors':[]}
  if contactvol<=1e-5:
   record['error']='no se obtuvo contacto volumetrico con tapa';row['poses'].append(record);break
  other=rails[-25 if y==-130 else -130];otherbb=other.optimalBoundingBox();otherbb.enlarge(.05)
  candidates_shapes=[(n,s,boxes[n]) for n,s in static.items()]+[(n,v[0],v[1]) for n,v in cache[(lift,dx)].items() if n!=own]+[('reserva_guia_opuesta',other,otherbb)]
  for name,s,b in candidates_shapes:
   if not bb.intersect(b):continue
   try:
    v=sh.common(s)
    if not(v.isNull() or v.isValid()):raise ValueError('comun invalido')
    distance=sh.distToShape(s)[0]
    if v.Volume>1e-5 or distance<=1e-6:
     record['collision']={'name':name,'volume_mm3':v.Volume,'distance_mm':distance};break
   except Exception as e:record['errors'].append({'name':name,'error':str(e)});break
  row['poses'].append(record)
  if record['collision'] or record['errors']:break
 row['sampled_ok']=len(row['poses'])==len(poses) and all(not v.get('collision') and not v.get('errors') and not v.get('error') for v in row['poses'])
 results['cases'].append(row)
 (H/'BUSQUEDA_PARCIAL.json').write_text(json.dumps(results,indent=2)+'\n')
 print('C10_ENLACE',y,'n',len(results['cases']),'pasa',row['sampled_ok'],flush=True)
(H/'BUSQUEDA.json').write_text(json.dumps(results,indent=2)+'\n')
print('C10_BUSQUEDA_COMPLETA',flush=True)
