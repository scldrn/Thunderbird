"""Screen straight conceptual door arms versus fixed parts at closed pose.

No claim about swept clearance or actuator viability. Endpoints are sampled from
actual door tessellation; the bar extends 2 mm past that surface point.
"""
from pathlib import Path
import json
import math
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
base=App.openDocument(str(HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape.copy() for o in base.Objects if o.Name.startswith('pieza_')}
study=App.openDocument(str(HERE/'C05_alojamiento_estudio.FCStd'))
cutbody=next(o.Shape.copy() for o in study.getObject('C05').Group if o.Label=='carroceria_superior_C03_recortada')
door=p['compuerta_C02_0_superior']
obstacles={'aro':p['aro_C02_0_superior'],'junta':p['junta_C02_0_superior'],
           'carroceria_recortada':cutbody,'camisa':p['modulo_C02_0_camisa_cuna_y_soportes'],
           'rotor':p['modulo_C02_0_rotor_copa']}
verts,_=door.tessellate(0.3)
results={'scope':'Barras rectas candidatas en posicion cerrada, 1.5 mm radio; puntos de malla de tapa C03; no analisis de recorrido ni integracion mecanica', 'arms':[]}
for x in (-177.5,-145.5):
 origin=App.Vector(x,-124,67.9767683408146)
 points=[v for v in verts if abs(v.x-x)<3 and -121<v.y<-83]
 # Choose points spread by y bands. Sort proximity to origin; more than one per band risks redundancy.
 groups={}
 for v in points:
  key=round((v.y+120)/4)
  score=(v-origin).Length
  if key not in groups or score<groups[key][0]:groups[key]=(score,v)
 candidates=sorted(groups.values())[:12]
 rows=[]
 for _,pnt in candidates:
  vec=pnt-origin
  length=vec.Length
  direction=vec.normalize()
  bar=Part.makeCylinder(1.5,length+2,origin,direction)
  row={'target_mm':[pnt.x,pnt.y,pnt.z], 'length_mm':length+2, 'pairs':{}}
  for name,shape in obstacles.items():
   try:row['pairs'][name]={'interseccion_mm3':bar.common(shape).Volume}
   except Exception as e:row['pairs'][name]={'error':str(e)}
  row['door_intersection_mm3']=bar.common(door).Volume
  rows.append(row)
 results['arms'].append({'x_mm':x,'samples':rows})
 print('BRAZO',x,'evaluados',len(rows),flush=True)
 (HERE/'EXPLORACION_BRAZOS_PARCIAL.json').write_text(json.dumps(results,indent=2)+'\n')
(HERE/'EXPLORACION_BRAZOS.json').write_text(json.dumps(results,indent=2)+'\n')
