"""Synthetic controls for geometry primitives used in hinge screening."""
from pathlib import Path
import json
import math
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent

def volume(a,b):
 if not a.BoundBox.intersect(b.BoundBox):return 0.0
 return a.common(b).Volume

cube=Part.makeBox(10,10,10,App.Vector(0,0,0))
far=Part.makeBox(10,10,10,App.Vector(20,0,0))
partial=Part.makeBox(10,10,10,App.Vector(5,0,0))
touching=Part.makeBox(10,10,10,App.Vector(10,0,0))
assert not cube.BoundBox.intersect(far.BoundBox)
assert cube.BoundBox.intersect(partial.BoundBox)
assert abs(volume(cube,far))<1e-9
assert abs(volume(cube,partial)-500.0)<1e-7
assert abs(volume(cube,touching))<1e-9
moved=cube.copy();moved.translate(App.Vector(0,0,10));moved.rotate(App.Vector(0,0,10),App.Vector(1,0,0),90)
assert abs(moved.Volume-cube.Volume)<1e-7
p=moved.CenterOfMass
assert (p-App.Vector(5,-5,15)).Length<1e-7
out={'scope':'geometrias analiticas sinteticas para bounding box, booleanos y transformacion; no valida C03','checks':7,'passed':True}
(HERE/'AUDITORIA_OPERADORES.json').write_text(json.dumps(out,indent=2)+'\n')
print('OPERADORES_OK',flush=True)
