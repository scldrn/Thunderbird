"""Native FreeCAD document of the integrated candidate, not a feature-history rebuild."""
from pathlib import Path
import hashlib
import json

import FreeCAD as App
import Import

HERE=Path(__file__).resolve().parent
FOLDER=HERE/'integracion_x160'
source=FOLDER/'C02_integracion_x160_5kg_cerrado_CANDIDATA.step'
doc=App.newDocument('C02_interna_x160_5kg_objetivo')
Import.insert(str(source),doc.Name)
note=doc.addObject('App::FeaturePython','Alcance_investigacion')
for name,value in (
    ('SourceSHA256',hashlib.sha256(source.read_bytes()).hexdigest()),
    ('Scope','Integrated packaging candidate. Imported solids, not native manufacturing feature history.'),
    ('Hardware','Motor, servo and bearing envelopes are reserves; performance, materials and mass not closed.'),
    ('RegenerateWith','ejecucion/G3/C02/integrar_x160.py'),
):
    note.addProperty('App::PropertyString',name,'Evidence')
    setattr(note,name,value)
note.addProperty('App::PropertyBool','FlightPerformanceValidated','Evidence')
note.FlightPerformanceValidated=False
doc.recompute()
shapes=[o for o in doc.Objects if hasattr(o,'Shape') and not o.Shape.isNull()]
invalid=[o.Name for o in shapes if not o.Shape.isValid()]
assert shapes and not invalid
output=FOLDER/'C02_integracion_x160_5kg_CANDIDATA.FCStd'
doc.saveAs(str(output))
count=len(doc.Objects)
App.closeDocument(doc.Name)
reopened=App.openDocument(str(output))
assert len(reopened.Objects)==count
App.closeDocument(reopened.Name)
(FOLDER/'FREECAD.json').write_text(json.dumps(dict(version=App.Version(),
    source_SHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
    output_SHA256=hashlib.sha256(output.read_bytes()).hexdigest(),
    document_objects=count,shape_objects=len(shapes),invalid_shapes=invalid,
    design_part_records_in_STEP=316,
    note='FreeCAD hierarchy counts differ from design part records; import/reopen test only, not parametric manufacturing or physical validation'),indent=2)+'\n')
print('FREECAD_C02_IMPORT_AND_REOPEN_OK',count,len(shapes),flush=True)
