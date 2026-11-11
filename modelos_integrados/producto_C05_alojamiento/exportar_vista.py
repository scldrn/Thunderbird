"""Mesh data for inspection render. Skin is cropped; red markers are visual."""
from pathlib import Path
import gzip,json
import FreeCAD as A
import Part
H=Path(__file__).resolve().parent
c=A.openDocument(str(H/'C05_contexto_cerrado.FCStd'))
items=list(c.getObject('C05_contexto').Group)
parts={o.Label:o.Shape for o in items}
box=Part.makeBox(150,140,105,A.Vector(-235,-165,15))
records=[]
for o in items:
 s=o.Shape.common(box) if o.Label=='carroceria_recortada' else o.Shape
 if s.isNull() or not s.Faces:continue
 vs,ts=s.tessellate(.4)
 records.append({'name':o.Label,'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]})
markers=[]
for o in items:
 if not o.Label.startswith('brazo_tapa_reserva'):continue
 for target in ('aro_C03','junta_C03'):
  shape=o.Shape.common(parts[target])
  if shape.Volume>.001:
   c=sum((v.CenterOfMass*v.Volume for v in shape.Solids),A.Vector(0,0,0))*(1.0/sum(v.Volume for v in shape.Solids))
   markers.append({'arm':o.Label,'obstacle':target,'volume_mm3':shape.Volume,'position_mm':[c.x,c.y,c.z]})
with gzip.open(H/'vista_C05_malla.json.gz','wt') as f:json.dump({'items':records,'markers':markers},f,separators=(',',':'))
print('VISTA_EXTRAIDA',len(records),'marcadores',len(markers),flush=True)
