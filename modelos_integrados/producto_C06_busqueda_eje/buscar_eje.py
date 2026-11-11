"""Coarse screen for an internal hinge axis, using original C03 BReps.

A 56-mm long cylinder represents the space for a hypothetical 1-mm-radius
pin plus 0.5 mm radial allowance. Passing is not a mechanical design.
"""
from pathlib import Path
import hashlib
import json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
X=-188.0
LENGTH=56.0
RADIUS=1.5
INTERSECTION_THRESHOLD_MM3=1e-5

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for v in iter(lambda:f.read(1024*1024),b''):h.update(v)
 return h.hexdigest()

doc=App.openDocument(str(SOURCE))
p={o.Label:o.Shape.copy() for o in doc.Objects if o.Name.startswith('pieza_')}
# Screening order prioritizes inexpensive obvious collisions; every surviving
# candidate is checked against every listed shape.
names=['modulo_C02_0_rotor_copa','junta_C02_0_superior','aro_C02_0_superior',
       'compuerta_C02_0_superior','modulo_C02_0_camisa_cuna_y_soportes','carroceria_C02_superior004']
obstacles=[(name,p[name]) for name in names]
ys=(-140,-130,-120,-110,-100,-90,-80)
zs=(55,65,75,85,95,105,115)
candidates=[(float(y),float(z),'grilla') for y in ys for z in zs]
candidates.append((-124.0,67.9767683408146,'referencia_C04'))
result={'source':str(SOURCE),'source_sha256':sha(SOURCE),
 'scope':'Eje aislado en cerrado, sin soportes ni trayectoria, contra seis objetos C03; no prueba de instalacion ni flujo',
 'pin_envelope_mm':{'start_x':X,'length':LENGTH,'radius':RADIUS,'allowance_hypothesis':0.5},
 'intersection_reject_threshold_mm3':INTERSECTION_THRESHOLD_MM3,'obstacles':names,'candidates':[]}
for i,(y,z,origin) in enumerate(candidates):
 cylinder=Part.makeCylinder(RADIUS,LENGTH,App.Vector(X,y,z),App.Vector(1,0,0))
 checks=[]
 for name,shape in obstacles:
  try:
   overlap=cylinder.common(shape)
   if not (overlap.isNull() or overlap.isValid()):raise ValueError('interseccion invalida')
   vol=overlap.Volume
   dist=cylinder.distToShape(shape)[0]
   check={'name':name,'overlap_mm3':vol,'distance_mm':dist}
   checks.append(check)
   if vol>INTERSECTION_THRESHOLD_MM3 or dist<=1e-6:break
  except Exception as exc:
   checks.append({'name':name,'error':repr(exc)})
   break
 passed=len(checks)==len(obstacles) and all('error' not in q and q['overlap_mm3']<=INTERSECTION_THRESHOLD_MM3 and q['distance_mm']>1e-6 for q in checks)
 result['candidates'].append({'y_mm':y,'z_mm':z,'origin':origin,'checked':checks,'passed_closed':passed})
 if i%5==0 or i+1==len(candidates):
  (HERE/'BUSQUEDA_PARCIAL.json').write_text(json.dumps(result,indent=2)+'\n')
  print('CRIBADOS',i+1,'DE',len(candidates),'pasan',sum(c['passed_closed'] for c in result['candidates']),flush=True)
(HERE/'BUSQUEDA_EJE.json').write_text(json.dumps(result,indent=2)+'\n')
print('BUSQUEDA_EJE_COMPLETA',flush=True)
