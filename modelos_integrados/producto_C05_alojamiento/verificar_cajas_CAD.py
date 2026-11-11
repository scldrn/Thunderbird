"""Compare actual transformed CAD tessellation vertices to C05 bounds."""
from pathlib import Path
import json
import FreeCAD as App
H=Path(__file__).resolve().parent
r=json.loads((H/'RESULTADOS.json').read_text())
bounds={e['nombre']:e['caja_mm'] for e in r['motion_envelopes']}
motion={e['nombre']:e['movimiento'] for e in r['motion_envelopes']}
d=App.openDocument(str(H.parent/'producto_C04_estudio_bisagra_v2/C04_cerrado.FCStd'))
objs=list(d.getObject('Estudio_C04').Group)[3:]
axis=App.Vector(*r['axis_mm']);samples=[(float(x),0.0) for x in (0,2,4,6,8,10)]+[(10.0,float(x)) for x in (22,44,66,88,110)]
checks=0;vertices_tested=0;worst=0;failures=[]
for o in objs:
 b=bounds[o.Label];kind=motion[o.Label]
 for lift,ang in samples:
  sh=o.Shape.copy()
  if kind!='fijo':sh.translate(App.Vector(0,0,lift))
  if kind=='giro':sh.rotate(axis+App.Vector(0,0,lift),App.Vector(1,0,0),ang)
  pts,_=sh.tessellate(.3)
  for v in pts:
   for i,x in enumerate((v.x,v.y,v.z)):
    miss=max(b[2*i]-x,x-b[2*i+1],0)
    worst=max(worst,miss)
    if miss>1e-5 and len(failures)<20:failures.append({'shape':o.Label,'lift':lift,'angle':ang,'axis':i,'error_mm':miss})
  vertices_tested+=len(pts);checks+=1
out={'scope':'vertices de teselacion en 11 poses; no demuestra por si sola cobertura continua de superficies','shape_pose_checks':checks,'vertices_tested':vertices_tested,'max_outside_mm':worst,'failures':failures}
(H/'AUDITORIA_CAJAS_CAD.json').write_text(json.dumps(out,indent=2)+'\n')
if failures:raise ValueError('Vertices fuera de caja')
print('CAJAS_VERIFICADAS',checks,vertices_tested,flush=True)
