"""Reopen C08 assemblies and STEP; check simple endpoint translations."""
from pathlib import Path
import json
import FreeCAD as App
import Import
H=Path(__file__).resolve().parent
m=json.loads((H/'MANIFIESTO.json').read_text());rows=[];centres={}
for v in m['states']:
 name=v['state'];n=App.openDocument(str(H/v['fcstd']));items=list(n.getObject('C08_local').Group)
 s=App.newDocument('STEP_'+name);Import.insert(str(H/v['step']),s.Name);s.recompute()
 roots=[o for o in s.Objects if o.TypeId=='App::Part' and not o.InList]
 if len(roots)!=1:raise ValueError('raices inesperadas')
 step=list(roots[0].Group)
 def invalid(objs):return [o.Label for o in objs if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
 if len(items)!=8 or len(step)!=8 or invalid(items) or invalid(step):raise ValueError('reimportacion invalida')
 centres[name]={o.Label:o.Shape.CenterOfMass for o in items if o.Label in ('compuerta_C03','rotor_C03','reserva_guia_0','reserva_guia_1')}
 rows.append({'state':name,'native_count':len(items),'step_count':len(step),'native_invalid':invalid(items),'step_invalid':invalid(step)})
 App.closeDocument(s.Name);App.closeDocument(n.Name)
move=centres['abierto']['compuerta_C03']-centres['cerrado']['compuerta_C03']
errors={'door_translation_mm':(move-App.Vector(-100,0,10)).Length}
for name in ('rotor_C03','reserva_guia_0','reserva_guia_1'):
 errors[name+'_movement_mm']=(centres['abierto'][name]-centres['cerrado'][name]).Length
if max(errors.values())>1e-5:raise ValueError('movimiento inesperado')
(H/'AUDITORIA_CAD.json').write_text(json.dumps({'scope':'reapertura e identidad de centros en extremos, no equivalencia global, mecanismo ni vuelo','states':rows,'errors_mm':errors},indent=2)+'\n')
print('C08_AUDITORIA_OK',flush=True)
