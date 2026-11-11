"""Tessellate C11 leaves at seven angles, elevated 20 mm."""
from pathlib import Path
import gzip,json
import FreeCAD as A
import Part
H=Path(__file__).resolve().parent
r=json.loads((H/'ELEVADAS_PARCIALES.json').read_text())
s=A.openDocument(str(H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
door=next(o.Shape for o in s.Objects if o.Name.startswith('pieza_') and o.Label=='compuerta_C02_0_superior');b=door.optimalBoundingBox()
leaves=[]
for axis in r['axes']:
 lo,hi=axis['bounds_y_mm'];box=Part.makeBox(b.XLength+4,hi-lo,b.ZLength+4,A.Vector(b.XMin-2,lo,b.ZMin-2))
 leaves.append((axis,door.common(box)))
result={'scope':'mallas de cuatro laminas elevadas 20 mm; sin ejes fisicos','angles':[]}
for angle in (0,15,30,45,60,75,90):
 verts=[];tris=[]
 for axis,orig in leaves:
  sh=orig.copy();sh.translate(A.Vector(0,0,20));sh.rotate(A.Vector(-160,axis['y_mm'],axis['z_mm']+20),A.Vector(1,0,0),angle)
  vs,ts=sh.tessellate(.4);off=len(verts);verts.extend([[v.x,v.y,v.z] for v in vs]);tris.extend([[off+x for x in t] for t in ts])
 result['angles'].append({'angle_deg':angle,'vertices':verts,'triangles':tris})
with gzip.open(H/'PERFIL_MALLAS.json.gz','wt') as f:json.dump(result,f,separators=(',',':'))
print('PERFIL_MALLAS_COMPLETO',flush=True)
