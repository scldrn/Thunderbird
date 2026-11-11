"""Test covered axes and C04 control at discrete positions, using original C03."""
from pathlib import Path
import json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
scans=json.loads((HERE/'COBERTURA.json').read_text())
source=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
doc=App.openDocument(str(source))
p={o.Label:o.Shape.copy() for o in doc.Objects if o.Name.startswith('pieza_')}
door=p['compuerta_C02_0_superior']
common=['modulo_C02_0_rotor_copa','junta_C02_0_superior','aro_C02_0_superior',
 'modulo_C02_0_camisa_cuna_y_soportes','carroceria_C02_superior004','carroceria_C02_inferior003']
common += [f'modulo_C02_{i}_camisa_cuna_y_soportes' for i in (1,2,3)]
common += [f'compuerta_C02_{i}_{side}' for i in range(4) for side in ('superior','inferior') if (i,side)!=(0,'superior')]
assert all(name in p for name in common),[name for name in common if name not in p]
THRESHOLD=.001

def check(shape, obstacle_names):
 checks=[]
 for name in obstacle_names:
  # A disjoint bounding box is a safe rejection of geometric intersection;
  # bounding boxes can be loose and are never treated as proof of a collision.
  obs=p[name]
  if not shape.BoundBox.intersect(obs.BoundBox):continue
  try:
   overlap=shape.common(obs)
   if not (overlap.isNull() or overlap.isValid()):raise ValueError('invalida')
   v=overlap.Volume
   if v>THRESHOLD:
    return {'collision':{'obstacle':name,'overlap_mm3':v},'checked':len(checks)+1}
   checks.append(name)
  except Exception as exc:
   return {'error':{'obstacle':name,'detail':repr(exc)},'checked':len(checks)+1}
 return {'collision':None,'checked':len(checks)}


def move(shape,y,z,lift,angle):
 out=shape.copy();out.translate(App.Vector(0,0,lift))
 out.rotate(App.Vector(-160,y,z+lift),App.Vector(1,0,0),angle)
 return out

candidates=[{'y_mm':c['y_mm'],'z_mm':c['z_mm'],'origin':'grilla_cubierta'} for c in scans['candidates'] if c['all_rays_covered']]
candidates.append({'y_mm':-124.0,'z_mm':67.9767683408146,'origin':'control_C04_no_seleccionable'})
report={'scope':'Cotas discretas de puerta y eje contra obstaculos listados. No soportes, holguras, cargas ni barrido continuo.',
        'obstacles':common,'threshold_mm3':THRESHOLD,'candidates':[]}
for i,c in enumerate(candidates):
 y,z=c['y_mm'],c['z_mm'];entry={**c,'pin_checks':[],'door_checks':[]}
 # Lift of cylindrical pin, against fixed obstacles. Closed C04 control may
 # fail immediately; this records why it is not selectable.
 for lift in (0,2,4,6,8,10):
  pin=Part.makeCylinder(1.5,56,App.Vector(-188,y,z+lift),App.Vector(1,0,0))
  result=check(pin,common)
  entry['pin_checks'].append({'lift_mm':lift,**result})
  if result.get('collision') or result.get('error'):break
 entry['pin_sampled_ok']=len(entry['pin_checks'])==6 and all(q.get('collision') is None and 'error' not in q for q in entry['pin_checks'])
 # Check door motion even when pin fails so C04 trajectory remains a useful control.
 for lift,ang in [(5,0),(10,0),(10,22),(10,44),(10,66),(10,88),(10,110)]:
  result=check(move(door,y,z,lift,ang),common)
  entry['door_checks'].append({'lift_mm':lift,'angle_deg':ang,**result})
  if result.get('collision') or result.get('error'):break
 entry['door_sampled_ok']=len(entry['door_checks'])==7 and all(q.get('collision') is None and 'error' not in q for q in entry['door_checks'])
 entry['selected_for_followup']=entry['origin']=='grilla_cubierta' and entry['pin_sampled_ok'] and entry['door_sampled_ok']
 report['candidates'].append(entry)
 (HERE/'MOVIMIENTO_PARCIAL.json').write_text(json.dumps(report,indent=2)+'\n')
 print('MUESTRA_EJE',i+1,'de',len(candidates),'y',y,'z',z,'pin',entry['pin_sampled_ok'],'puerta',entry['door_sampled_ok'],flush=True)
(HERE/'MOVIMIENTO.json').write_text(json.dumps(report,indent=2)+'\n')
print('MOVIMIENTO_COMPLETO',flush=True)
