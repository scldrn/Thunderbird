"""Screen fixed rail reservations against all 8 moving C07 covers."""
from pathlib import Path
import json,time
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent
r=json.loads((H/'GUIAS.json').read_text())
d=App.openDocument(str(H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape.copy() for o in d.Objects if o.Name.startswith('pieza_')}
keys=[f'compuerta_C02_{i}_{side}' for i in range(4) for side in ('superior','inferior')]
poses=[(5,0),(10,0),(10,25),(10,50),(10,75),(10,100)]
# Cache moving BReps/bounds once; actual cover collisions still use BRep.
cache=[]
for lift,dx in poses:
 for n in keys:
  _,_,num,side=n.split('_');sgn_x=-1 if int(num)<2 else 1;sgn_z=1 if side=='superior' else -1
  s=p[n].copy();s.translate(App.Vector(sgn_x*dx,0,sgn_z*lift))
  b=s.optimalBoundingBox();b.enlarge(.05)
  cache.append((lift,dx,n,s,b))
print('PUERTAS_EN_CACHE',len(cache),flush=True)
result={'scope':'Reservas fijas individualmente contra ocho tapas moviles en seis poses discretas; sin guias montadas, tolerancias, ni analisis continuo','candidates':[]}
for c in r['candidates']:
 if not c['clear_closed']:continue
 y,z=c['y_mm'],c['z_mm'];rail=Part.makeCylinder(2.5,160,App.Vector(-280,y,z),App.Vector(1,0,0));rb=rail.optimalBoundingBox();rb.enlarge(.05)
 row={'y_mm':y,'z_mm':z,'pairs_screened':0,'boolean_count':0,'intersections':[],'errors':[]}
 for lift,dx,name,s,b in cache:
  row['pairs_screened']+=1
  if not rb.intersect(b):continue
  row['boolean_count']+=1
  try:
   q=rail.common(s)
   if not(q.isNull() or q.isValid()):raise ValueError('comun invalido')
   volume=q.Volume;distance=rail.distToShape(s)[0]
   if volume>1e-5 or distance<=1e-6:row['intersections'].append({'door':name,'lift_mm':lift,'abs_dx_mm':dx,'volume_mm3':volume,'distance_mm':distance})
  except Exception as e:row['errors'].append({'door':name,'lift_mm':lift,'abs_dx_mm':dx,'error':repr(e)})
 row['screened_ok']=not row['intersections'] and not row['errors'] and row['pairs_screened']==len(cache)
 result['candidates'].append(row)
 (H/'GUIAS_MOVIMIENTO_PARCIAL.json').write_text(json.dumps(result,indent=2)+'\n')
 print('GUIA_MOVIL',y,z,'pasa',row['screened_ok'],'interferencias',len(row['intersections']),flush=True)
clear=[v for v in result['candidates'] if v['screened_ok']]
result['pairs']=[{'left_y_mm':a['y_mm'],'right_y_mm':b['y_mm'],'z_mm':a['z_mm'],'spacing_mm':b['y_mm']-a['y_mm']}
                 for a in clear for b in clear if a['y_mm']<-76<b['y_mm'] and a['z_mm']==b['z_mm'] and b['y_mm']-a['y_mm']>=30]
(H/'GUIAS_MOVIMIENTO.json').write_text(json.dumps(result,indent=2)+'\n')
print('GUIAS_MOVIMIENTO_COMPLETO',len(clear),'pares',len(result['pairs']),flush=True)
