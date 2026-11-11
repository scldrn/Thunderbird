"""End-pose collision screen: 8 doors vs all other C07 5kg CAD records.

Uses FreeCAD's optimalBoundingBox expanded by 0.05 mm for broad phase, then
BRep common volume; this does not cover intermediate poses or deformation.
"""
from pathlib import Path
import json,time
import FreeCAD as App
HERE=Path(__file__).resolve().parent
src=HERE/'5kg/C07_5kg_deslizante_abierto.FCStd'
d=App.openDocument(str(src))
objs=[o for o in d.Objects if o.Name.startswith('pieza_')]
if len(objs)!=316:raise ValueError('recuento de piezas inesperado')
doors=[o for o in objs if o.Label.startswith('compuerta_C02_')]
rest=[o for o in objs if not o.Label.startswith('compuerta_C02_')]
if len(doors)!=8 or len(rest)!=308:raise ValueError('recuento de compuertas inesperado')
boxes={}
for i,o in enumerate(objs):
 b=o.Shape.optimalBoundingBox()
 if not b.isValid():raise ValueError('caja invalida '+o.Label)
 b.enlarge(.05);boxes[o.Name]=b
 if (i+1)%50==0:print('CAJAS_OPTIMAS',i+1,'de',len(objs),flush=True)
report={'scope':'Posicion abierta final 5kg: ocho tapas vs 308 registros restantes y parejas mutuas; cajas optimas ensanchadas .05mm y comun BRep; sin trayectorias, tolerancias reales ni validacion de funcionamiento',
        'source':str(src),'screened_pairs':0,'boolean_pairs':0,'collisions':[],'errors':[],'per_door':[]}
for i,a in enumerate(doors):
 t=time.monotonic();row={'door':a.Label,'screened':0,'boolean':0,'collisions':0,'errors':0}
 for b in rest+doors[i+1:]:
  row['screened']+=1;report['screened_pairs']+=1
  if not boxes[a.Name].intersect(boxes[b.Name]):continue
  row['boolean']+=1;report['boolean_pairs']+=1
  try:
   x=a.Shape.common(b.Shape)
   if not(x.isNull() or x.isValid()):raise ValueError('interseccion invalida')
   if x.Volume>.001:
    row['collisions']+=1;report['collisions'].append({'door':a.Label,'obstacle':b.Label,'volume_mm3':x.Volume})
  except Exception as e:
   row['errors']+=1;report['errors'].append({'door':a.Label,'obstacle':b.Label,'error':repr(e)})
 row['seconds']=time.monotonic()-t;report['per_door'].append(row)
 (HERE/'POSICION_GLOBAL_PARCIAL.json').write_text(json.dumps(report,indent=2)+'\n')
 print('C07_PUERTA_GLOBAL',a.Label,'pares',row['screened'],'boolean',row['boolean'],'colisiones',row['collisions'],'errores',row['errors'],flush=True)
report['passed_screen']=not report['collisions'] and not report['errors']
(HERE/'POSICION_GLOBAL.json').write_text(json.dumps(report,indent=2)+'\n')
print('C07_GLOBAL_COMPLETO',report['passed_screen'],flush=True)
