"""Check STEP/FCStd reopen and quantify connectivity change in cut skin."""
from pathlib import Path
import json
import FreeCAD as App
import Import
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
s=App.openDocument(str(BASE))
orig=next(o.Shape for o in s.Objects if o.Name.startswith('pieza_') and o.Label=='carroceria_C02_superior004')
n=App.openDocument(str(HERE/'C05_alojamiento_estudio.FCStd'))
ng=list(n.getObject('C05').Group)
modified=next(o.Shape for o in ng if o.Label=='carroceria_superior_C03_recortada')
d=App.newDocument('Validacion_STEP_C05')
Import.insert(str(HERE/'C05_alojamiento_estudio.step'),d.Name)
d.recompute()
roots=[o for o in d.Objects if o.TypeId=='App::Part' and not o.InList]
if len(roots)!=1: raise RuntimeError('raices STEP inesperadas')
sg=list(roots[0].Group)
def info(items):
 return {'count':len(items),'invalid':[o.Label for o in items if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids], 'total_volume_mm3':sum(o.Shape.Volume for o in items)}
def solids(shape):
 return sorted([{'volume_mm3':v.Volume,'area_mm2':v.Area} for v in shape.Solids],key=lambda x:-x['volume_mm3'])
report={'scope':'Reimportacion STEP; validez y volumen de objetos; componentes solidos antes/despues de recorte. No equivalencia por pieza ni rigidez.',
        'native':info(ng),'step':info(sg),'original_body_solids':solids(orig),'modified_body_solids':solids(modified)}
(HERE/'AUDITORIA_C05.json').write_text(json.dumps(report,indent=2)+'\n')
if report['native']['invalid'] or report['step']['invalid'] or len(ng)!=6 or len(sg)!=6:raise RuntimeError('Auditoria basica fallida')
print('AUDITORIA_C05_COMPLETA',flush=True)
