"""Screen larger lifts and internal axes; sparse rigid-body samples only."""
from pathlib import Path
import json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
doc=App.openDocument(str(HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape.copy() for o in doc.Objects if o.Name.startswith('pieza_')}
door=p['compuerta_C02_0_superior']
names=['modulo_C02_0_rotor_copa','junta_C02_0_superior','aro_C02_0_superior','modulo_C02_0_camisa_cuna_y_soportes',
       'carroceria_C02_superior004','carroceria_C02_inferior003']
names += [f'modulo_C02_{i}_camisa_cuna_y_soportes' for i in (1,2,3)]
names += [f'compuerta_C02_{i}_{side}' for i in range(4) for side in ('superior','inferior') if (i,side)!=(0,'superior')]
assert all(n in p for n in names)

def check(s):
 for n in names:
  obs=p[n]
  if not s.BoundBox.intersect(obs.BoundBox):continue
  try:
   com=s.common(obs)
   if not (com.isNull() or com.isValid()):raise ValueError('interseccion invalida')
   if com.Volume>.001:return {'collision':n,'volume_mm3':com.Volume}
  except Exception as e:return {'error':n,'detail':repr(e)}
 return {}

def moved(y,z,lift,angle):
 s=door.copy();s.translate(App.Vector(0,0,lift));s.rotate(App.Vector(-160,y,z+lift),App.Vector(1,0,0),angle);return s

axes=[(-100,55),(-100,65),(-90,55),(-90,65),(-80,75)]
res={'scope':'Exploracion discreta de mayor elevacion; no incluye soportes, continuidad o carga',
 'obstacles':names,'threshold_mm3':.001,'cases':[]}
for liftmax in (20,30,40):
 for y,z in axes:
  r={'y_mm':y,'z_mm':z,'lift_max_mm':liftmax,'pin_checks':[],'door_checks':[]}
  for lift in range(0,liftmax+1,10):
   pin=Part.makeCylinder(1.5,56,App.Vector(-188,y,z+lift),App.Vector(1,0,0))
   q=check(pin);r['pin_checks'].append({'lift_mm':lift,**q})
   if q:break
  r['pin_sampled_ok']=len(r['pin_checks'])==liftmax//10+1 and not any('collision' in q or 'error' in q for q in r['pin_checks'])
  if r['pin_sampled_ok']:
   poses=[(float(v),0) for v in range(10,liftmax+1,10)]+[(float(liftmax),float(v)) for v in (22,44,66,88,110)]
   for lift,ang in poses:
    q=check(moved(y,z,lift,ang));r['door_checks'].append({'lift_mm':lift,'angle_deg':ang,**q})
    if q:break
   r['door_sampled_ok']=len(r['door_checks'])==len(poses) and not any('collision' in q or 'error' in q for q in r['door_checks'])
  else:r['door_sampled_ok']=False
  res['cases'].append(r)
  (HERE/'ELEVACION_PARCIAL.json').write_text(json.dumps(res,indent=2)+'\n')
  print('ELEVACION',liftmax,'eje',y,z,'pin',r['pin_sampled_ok'],'puerta',r['door_sampled_ok'],flush=True)
(HERE/'ELEVACION.json').write_text(json.dumps(res,indent=2)+'\n')
print('ELEVACION_COMPLETA',flush=True)
