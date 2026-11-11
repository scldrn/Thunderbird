"""Check that face-tessellation vertices fall within expanded CAD AABBs."""
from pathlib import Path
import gzip,json,math
import FreeCAD as App
HERE=Path(__file__).resolve().parent
native=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
with gzip.open(HERE.parent/'producto_C03/5kg/C03_5kg_cerrado_mallas_caras.json.gz','rt') as f:mesh=json.load(f)
d=App.openDocument(str(native))
objs={o.Label:o for o in d.Objects if o.Name.startswith('pieza_')}
if len(objs)!=316 or len(mesh['parts'])!=316:raise ValueError('recuento inesperado')
vertices=0;worst=0.0;failures=[]
for item in mesh['parts']:
 b=objs[item['name']].Shape.optimalBoundingBox();b.enlarge(.05)
 if not b.isValid():raise ValueError('caja invalida')
 for v in item['vertices_m']:
  xyz=[c*1000 for c in v]
  if not all(math.isfinite(c) for c in xyz):raise ValueError('vertice no finito')
  for val,lo,hi in zip(xyz,(b.XMin,b.YMin,b.ZMin),(b.XMax,b.YMax,b.ZMax)):
   error=max(lo-val,val-hi,0.0);worst=max(worst,error)
   if error>1e-5 and len(failures)<20:failures.append({'part':item['name'],'error_mm':error})
  vertices+=1
out={'scope':'Vertices de la malla derivada del mismo CAD, 316 piezas; verificacion discreta, no prueba de superficie continua',
     'parts':len(objs),'vertices':vertices,'max_outside_mm':worst,'failures':failures}
(HERE/'AUDITORIA_CAJAS_OPTIMAS.json').write_text(json.dumps(out,indent=2)+'\n')
if failures:raise ValueError('vertices fuera de las cajas')
print('C08_CAJAS_VERIFICADAS',len(objs),vertices,flush=True)
