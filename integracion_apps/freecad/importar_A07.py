from pathlib import Path
import json
import FreeCAD as App
import Import
P=Path(__file__).resolve().parent
source=P.parents[1]/'modelos_integrados/producto_A07/5kg/A07_cerrado.step'
doc=App.newDocument('A07_ventiladores_internos')
Import.insert(str(source),doc.Name)
doc.recompute()
shapes=[o for o in doc.Objects if hasattr(o,'Shape') and not o.Shape.isNull()]
invalid=[o.Name for o in shapes if not o.Shape.isValid()]
assert shapes and not invalid
output=P/'A07_ventiladores_internos.FCStd'
doc.saveAs(str(output))
(P/'IMPORTACION.json').write_text(json.dumps(dict(version=App.Version(),source=str(source),document_objects=len(doc.Objects),shape_objects=len(shapes),invalid_shapes=invalid,units='mm',scope='STEP import and geometric validity; not parametric feature reconstruction or structural verification'),indent=2))
print('FREECAD_IMPORT_OK',len(shapes))
App.closeDocument(doc.Name)
