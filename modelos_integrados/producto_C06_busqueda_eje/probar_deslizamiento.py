"""Explore lifting a door then translating it along x, without rotation.

Closed and elevated covers are C03 solid; supports and motors not modelled.
"""
from pathlib import Path
import json
import FreeCAD as App
HERE=Path(__file__).resolve().parent
d=App.openDocument(str(HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape.copy() for o in d.Objects if o.Name.startswith('pieza_')}
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
   q=s.common(obs)
   if not(q.isNull() or q.isValid()):raise ValueError('interseccion invalida')
   if q.Volume>.001:return {'collision':n,'volume_mm3':q.Volume}
  except Exception as e:return {'error':n,'detail':repr(e)}
 return {}

def move(lift,dx):
 s=door.copy();s.translate(App.Vector(dx,0,lift));return s

out={'scope':'Candidatos tapa elevada y deslizada sin girar; muestras discretas de una tapa, sin guias, motor ni deformaciones',
     'obstacles':names,'threshold_mm3':.001,'nominal_opening':{'x_center_mm':-160,'diameter_mm':84},'cases':[]}
for liftmax in (10,20,30):
 for direction in (-1,1):
  row={'lift_max_mm':liftmax,'direction_x':direction,'target_dx_mm':direction*100,'checks':[]}
  poses=[(float(k),0.0) for k in range(5,liftmax+1,5)]+[(float(liftmax),float(direction*k)) for k in range(10,101,10)]
  for lift,dx in poses:
   q=check(move(lift,dx));row['checks'].append({'lift_mm':lift,'dx_mm':dx,**q})
   if q:break
  row['sampled_ok']=len(row['checks'])==len(poses) and not any('collision' in q or 'error' in q for q in row['checks'])
  s=move(liftmax,direction*100)
  pts,_=s.tessellate(.3)
  xmin=min(v.x for v in pts);xmax=max(v.x for v in pts)
  # Sufficient, not necessary, test of XY projection separation from a circle
  # enclosed by x in [-202,-118], using sampled mesh bounds (not exact BRep).
  xgap=(-202-xmax) if direction<0 else (xmin-(-118))
  row['display_mesh_x_bounds_mm']=[xmin,xmax]
  row['sampled_projection_x_gap_mm']=xgap
  out['cases'].append(row)
  (HERE/'DESLIZAMIENTO_PARCIAL.json').write_text(json.dumps(out,indent=2)+'\n')
  print('DESLIZAMIENTO',liftmax,direction,'pasa',row['sampled_ok'],'gap_proy_malla',xgap,flush=True)
(HERE/'DESLIZAMIENTO.json').write_text(json.dumps(out,indent=2)+'\n')
print('DESLIZAMIENTO_COMPLETO',flush=True)
