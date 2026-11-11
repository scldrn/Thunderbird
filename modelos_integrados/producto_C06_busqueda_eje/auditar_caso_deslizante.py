"""Reopen C06 sliding local CAD and reimport STEP; test endpoint movement."""
from pathlib import Path
import json
import FreeCAD as App
import Import
H=Path(__file__).resolve().parent
case=json.loads((H/'CASO_DESLIZANTE.json').read_text())
rows=[];centres={}
for state in ('cerrado','evaluacion'):
 entry=case[state]
 n=App.openDocument(str(H/entry['fcstd'])); items=list(n.getObject('C06_deslizante').Group)
 bad=[o.Label for o in items if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
 d=App.newDocument('Reimport_'+state);Import.insert(str(H/entry['step']),d.Name);d.recompute()
 roots=[o for o in d.Objects if o.TypeId=='App::Part' and not o.InList]
 if len(roots)!=1:raise ValueError('raices inesperadas')
 step=list(roots[0].Group)
 bads=[o.Label for o in step if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
 if len(items)!=entry['objects'] or len(step)!=entry['objects'] or bad or bads:raise ValueError('piezas invalidas')
 centres[state]={o.Label:o.Shape.CenterOfMass for o in items if o.Label in ('rotor_C03','compuerta_C03')}
 rows.append({'state':state,'native_count':len(items),'step_count':len(step),'invalid_native':bad,'invalid_step':bads})
 App.closeDocument(d.Name);App.closeDocument(n.Name)
t=case['target']
diff=centres['evaluacion']['compuerta_C03']-centres['cerrado']['compuerta_C03']
err=(diff-App.Vector(t['dx_mm'],0,t['lift_mm'])).Length
rotorerr=(centres['evaluacion']['rotor_C03']-centres['cerrado']['rotor_C03']).Length
if err>1e-5 or rotorerr>1e-5:raise ValueError('Movimiento final inesperado')
out={'scope':'Reapertura STEP/FCStd y comprobacion de centros en extremos; no valida trayectoria, mecanismo, ni equivalencia geometrica global',
     'states':rows,'door_translation_error_mm':err,'rotor_motion_error_mm':rotorerr}
(H/'AUDITORIA_CASO_DESLIZANTE.json').write_text(json.dumps(out,indent=2)+'\n')
print('CASO_DESLIZANTE_AUDITADO',flush=True)
