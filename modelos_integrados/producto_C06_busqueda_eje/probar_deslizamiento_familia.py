"""Screen three more C03 doors using lift and axial translation.

Each door is moved separately while the seven other doors stay closed.
This is not a simultaneous mechanism, complete collision or flight validation.
"""
from pathlib import Path
import json
import FreeCAD as App
HERE=Path(__file__).resolve().parent
d=App.openDocument(str(HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape.copy() for o in d.Objects if o.Name.startswith('pieza_')}
configs=[(0,'inferior',-1,-1),(2,'superior',1,1),(2,'inferior',1,-1)]

def check(s,names):
 for n in names:
  obs=p[n]
  if not s.BoundBox.intersect(obs.BoundBox):continue
  try:
   v=s.common(obs)
   if not(v.isNull() or v.isValid()):raise ValueError('interseccion invalida')
   if v.Volume>.001:return {'collision':n,'volume_mm3':v.Volume}
  except Exception as e:return {'error':n,'detail':repr(e)}
 return {}

out={'scope':'Tres puertas adicionales, movidas por separado; 6 muestras; obstaculos seleccionados; sin soportes ni simultaneidad','cases':[]}
for module,side,dx_sign,z_sign in configs:
 name=f'compuerta_C02_{module}_{side}';door=p[name]
 names=[f'modulo_C02_{module}_rotor_copa',f'junta_C02_{module}_{side}',f'aro_C02_{module}_{side}',
        f'modulo_C02_{module}_camisa_cuna_y_soportes','carroceria_C02_superior004','carroceria_C02_inferior003']
 names += [f'modulo_C02_{i}_camisa_cuna_y_soportes' for i in range(4) if i!=module]
 names += [f'compuerta_C02_{i}_{s}' for i in range(4) for s in ('superior','inferior') if (i,s)!=(module,side)]
 assert all(n in p for n in names)
 case={'door':name,'lift_direction':z_sign,'dx_direction':dx_sign,'obstacles':names,'checks':[]}
 poses=[(5,0),(10,0),(10,25),(10,50),(10,75),(10,100)]
 for a,b in poses:
  sh=door.copy();sh.translate(App.Vector(dx_sign*b,0,z_sign*a))
  q=check(sh,names);case['checks'].append({'lift_mm':z_sign*a,'dx_mm':dx_sign*b,**q})
  if q:break
 case['sampled_ok']=len(case['checks'])==len(poses) and not any('collision' in q or 'error' in q for q in case['checks'])
 out['cases'].append(case)
 (HERE/'FAMILIA_DESLIZANTE_PARCIAL.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PUERTA',name,'pasa',case['sampled_ok'],flush=True)
(HERE/'FAMILIA_DESLIZANTE.json').write_text(json.dumps(out,indent=2)+'\n')
print('FAMILIA_COMPLETA',flush=True)
