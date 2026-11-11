"""Audit all intersections of 36 C08 straight links, rather than first hit.

Allowing intersection with the combined duct/cradle/support shape is only a
hypothesis for a possible aperture, not a design or seal approval.
"""
from pathlib import Path
import json
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent
C08=H.parent/'producto_C08_guias'
refs=json.loads((C08/'UNION_ALT.json').read_text())
rotors=json.loads((C08/'GUIAS.json').read_text())['rotor_sweep_audit']
src=H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
d=App.openDocument(str(src));objs=[o for o in d.Objects if o.Name.startswith('pieza_')]
p={o.Label:o.Shape.copy() for o in objs}
if len(p)!=316:raise ValueError('recuento inesperado')
door='compuerta_C02_0_superior';allowed='modulo_C02_0_camisa_cuna_y_soportes'
shapes={n:s for n,s in p.items() if n!=door}
for i,r in enumerate(rotors):
 x,y=r['center_mm'];shapes['envolvente_rotor_'+str(i)]=Part.makeCylinder(r['radius_mm'],r['height_mm'],App.Vector(x,y,r['zmin_mm']),App.Vector(0,0,1))
boxes={}
for n,s in shapes.items():
 b=s.optimalBoundingBox();b.enlarge(.05);boxes[n]=b
out={'scope':'36 barras rectas en cerrado, todos los obstaculos C03 salvo tapa propia (contacto propuesto), cuatro cilindros de giro nominal; no trayectorias ni tolerancias reales',
     'allowed_modification':allowed,'collision_threshold_mm3':1e-5,'cases':[]}
for i,c in enumerate(refs['cases']):
 y=c['rail_y_mm'];z=refs['selected_pair']['left_z_mm'] if y==refs['selected_pair']['left_y_mm'] else refs['selected_pair']['right_z_mm']
 a=App.Vector(-160,y,z);b=App.Vector(*c['target_mm']);direction=b-a;length=direction.Length;direction.normalize()
 link=Part.makeCylinder(1.5,length+2,a,direction);lb=link.optimalBoundingBox();lb.enlarge(.05)
 row={'rail_y_mm':y,'rail_z_mm':z,'target_mm':c['target_mm'],'link_length_mm':length+2,
      'door_overlap_mm3':link.common(p[door]).Volume,'screened':0,'boolean_count':0,'collisions':[],'errors':[]}
 for name,shape in shapes.items():
  row['screened']+=1
  if not lb.intersect(boxes[name]):continue
  row['boolean_count']+=1
  try:
   q=link.common(shape)
   if not(q.isNull() or q.isValid()):raise ValueError('interseccion invalida')
   v=q.Volume;distance=link.distToShape(shape)[0]
   if v>1e-5 or distance<=1e-6:row['collisions'].append({'name':name,'volume_mm3':v,'distance_mm':distance})
  except Exception as e:row['errors'].append({'name':name,'error':repr(e)})
 collateral=[a for a in row['collisions'] if a['name']!=allowed]
 row['only_combined_duct_interference']=not collateral and not row['errors'] and any(a['name']==allowed for a in row['collisions']) and row['door_overlap_mm3']>1e-5
 out['cases'].append(row)
 if (i+1)%3==0:
  (H/'ENLACES_PARCIAL.json').write_text(json.dumps(out,indent=2)+'\n')
  print('ENLACES',i+1,'de',len(refs['cases']),'solo_conducto',sum(r['only_combined_duct_interference'] for r in out['cases']),flush=True)
(H/'ENLACES.json').write_text(json.dumps(out,indent=2)+'\n')
print('ENLACES_COMPLETO',flush=True)
