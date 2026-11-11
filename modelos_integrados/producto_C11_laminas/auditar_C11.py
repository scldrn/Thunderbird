"""Reopen and reimport C11; check centres of four ideal leaves and rotor."""
from pathlib import Path
import json
import FreeCAD as A
import Import
H=Path(__file__).resolve().parent
m=json.loads((H/'MANIFIESTO.json').read_text());r=json.loads((H/'ELEVADAS.json').read_text())
axes={a['index']:a for a in r['axes']};rows=[];centres={}
def center(shape):
 solids=shape.Solids;total=sum(v.Volume for v in solids)
 return sum((v.CenterOfMass*v.Volume for v in solids),A.Vector())*(1.0/total)
for v in m['states']:
 n=A.openDocument(str(H/v['fcstd']));items=list(n.getObject('C11_local').Group)
 st=A.newDocument('STEP_'+v['state']);Import.insert(str(H/v['step']),st.Name);st.recompute()
 roots=[o for o in st.Objects if o.TypeId=='App::Part' and not o.InList]
 if len(roots)!=1:raise ValueError('raices STEP inesperadas')
 s=list(roots[0].Group)
 def bad(parts):return [o.Label for o in parts if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
 if len(items)!=9 or len(s)!=9 or bad(items) or bad(s):raise ValueError('piezas invalidas')
 centres[v['state']]={o.Label:center(o.Shape) for o in items if o.Label=='rotor' or o.Label.startswith('lamina_')}
 rows.append({'state':v['state'],'native_count':len(items),'step_count':len(s),'invalid_native':bad(items),'invalid_step':bad(s)})
 A.closeDocument(st.Name);A.closeDocument(n.Name)
errors={};rot=A.Rotation(A.Vector(1,0,0),60)
for i in range(4):
 a=axes[i];origin=A.Vector(-160,a['y_mm'],a['z_mm']+20);start=centres['cerrado'][f'lamina_{i}']+A.Vector(0,0,20)
 expected=origin+rot.multVec(start-origin);actual=centres['elevado_60'][f'lamina_{i}']
 errors[f'lamina_{i}']=(actual-expected).Length
errors['rotor']=(centres['elevado_60']['rotor']-centres['cerrado']['rotor']).Length
if max(errors.values())>1e-4:raise ValueError('error de transformacion')
(H/'AUDITORIA_CAD.json').write_text(json.dumps({'scope':'Reapertura, reimportacion y centros; no equivalencia global ni mecanismo','states':rows,'center_errors_mm':errors},indent=2)+'\n')
print('C11_AUDITORIA_OK',flush=True)
