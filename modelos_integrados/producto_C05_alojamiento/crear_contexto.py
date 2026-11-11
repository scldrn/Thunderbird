"""Assemble one local C05 study with original C04 hardware and cut skin."""
from pathlib import Path
import hashlib
import json
import FreeCAD as App
import Import
HERE=Path(__file__).resolve().parent
study=App.openDocument(str(HERE/'C05_alojamiento_estudio.FCStd'))
mech=App.openDocument(str(HERE.parent/'producto_C04_estudio_bisagra_v2/C04_cerrado.FCStd'))
base=App.openDocument(str(HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
ss=list(study.getObject('C05').Group)
ms=list(mech.getObject('Estudio_C04').Group)
body=next(o.Shape.copy() for o in ss if o.Label=='carroceria_superior_C03_recortada')
gasket=next(o.Shape.copy() for o in ss if o.Label=='junta_original_C03')
assert len(ms)==14
out=App.newDocument('C05_contexto_cerrado')
g=out.addObject('App::Part','C05_contexto')
for label,shape in [('carroceria_recortada',body),('junta_C03',gasket)]+[(o.Label,o.Shape.copy()) for o in ms]:
 obj=out.addObject('Part::Feature','Pieza');obj.Label=label;obj.Shape=shape;g.addObject(obj)
 if not shape.isValid() or not shape.Solids:raise ValueError(label)
meta=out.addObject('App::FeaturePython','Advertencia')
meta.addProperty('App::PropertyString','Alcance','Proyecto')
meta.Alcance='ESTUDIO RECHAZADO: recorte fragmenta carroceria y brazos atraviesan aro/junta; no es CAD funcional.'
out.recompute()
fc=HERE/'C05_contexto_cerrado.FCStd'; step=HERE/'C05_contexto_cerrado.step'
out.saveAs(str(fc));Import.export([g],str(step))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(HERE/'MANIFIESTO_CONTEXTO.json').write_text(json.dumps({'scope':'CAD local ilustrativo rechazado, 16 objetos','fcstd':fc.name,'fcstd_sha256':digest(fc),'step':step.name,'step_sha256':digest(step),'objects':len(g.Group)},indent=2)+'\n')
print('CONTEXTO_C05_COMPLETO',len(g.Group),flush=True)
