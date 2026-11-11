from pathlib import Path
import json
import FreeCAD as A
import Import
H=Path(__file__).resolve().parent
r=json.loads((H/'DIAGNOSTICO.json').read_text())
n=A.openDocument(str(H/r['native']));objs=list(n.getObject('C10_local').Group)
s=A.newDocument('Revision_STEP_C10');Import.insert(str(H/r['step']),s.Name);s.recompute()
roots=[o for o in s.Objects if o.TypeId=='App::Part' and not o.InList]
if len(roots)!=1:raise ValueError('raices STEP inesperadas')
items=list(roots[0].Group)
def bad(v):return [o.Label for o in v if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
if len(objs)!=8 or len(items)!=8 or bad(objs) or bad(items):raise ValueError('solidos invalidos')
p={o.Label:o.Shape for o in objs};v=p['enlace_ideal'].common(p['piel']).Volume
if abs(v-r['reproduced_volume_mm3'])>1e-5:raise ValueError('colision no reproducida')
(H/'AUDITORIA_CAD.json').write_text(json.dumps({'scope':'reapertura, reimportacion y reproduccion de colision; no equivalencia geometrica global','native_count':8,'step_count':8,'invalid_native':bad(objs),'invalid_step':bad(items),'overlap_mm3':v},indent=2)+'\n')
print('AUDITORIA_C10_OK',flush=True)
