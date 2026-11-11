"""Validate CAD files are reopenable; does not approve the mechanism."""
from pathlib import Path
import json
import FreeCAD as App
import Import
P=Path(__file__).resolve().parent
n=App.openDocument(str(P/'C05_contexto_cerrado.FCStd'))
ns=list(n.getObject('C05_contexto').Group)
s=App.newDocument('RevisionContextoC05')
Import.insert(str(P/'C05_contexto_cerrado.step'),s.Name)
s.recompute()
roots=[o for o in s.Objects if o.TypeId=='App::Part' and not o.InList]
if len(roots)!=1:raise ValueError('Numero de raices inesperado')
ss=list(roots[0].Group)
def audit(items):
 return {'count':len(items),'invalid':[o.Label for o in items if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]}
r={'scope':'reapertura/reimportacion basica, sin equivalencia por pieza ni validacion fisica','FCStd':audit(ns),'STEP':audit(ss)}
(P/'AUDITORIA_CONTEXTO.json').write_text(json.dumps(r,indent=2)+'\n')
if len(ns)!=16 or len(ss)!=16 or r['FCStd']['invalid'] or r['STEP']['invalid']:raise ValueError('auditoria fallida')
print('CONTEXTO_AUDITADO',flush=True)
