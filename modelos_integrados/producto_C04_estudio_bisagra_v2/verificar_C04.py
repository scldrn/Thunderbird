"""Reopen native C04 and reimport STEP; check basic solid validity only."""
from pathlib import Path
import hashlib
import json
import FreeCAD as App
import Import

HERE=Path(__file__).resolve().parent
results=json.loads((HERE/'RESULTADOS.json').read_text())
audit={'scope':'Reapertura y reimportacion; validez de solidos y conteos. No prueba de equivalencia geometrica completa ni de mecanismo.', 'states':[]}
errors=[]
for state in results['states']:
 name=state['estado']
 nd=App.openDocument(str(HERE/state['fcstd']))
 ng=nd.getObject('Estudio_C04')
 ns=list(ng.Group)
 sd=App.newDocument('test_'+name)
 Import.insert(str(HERE/state['step']),sd.Name)
 sd.recompute()
 roots=[o for o in sd.Objects if o.TypeId=='App::Part' and not o.InList]
 if len(roots)!=1: raise ValueError('STEP root count '+str(len(roots)))
 ss=list(roots[0].Group)
 invalid_n=[o.Label for o in ns if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
 invalid_s=[o.Label for o in ss if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
 if len(ns)!=14 or len(ss)!=14 or invalid_n or invalid_s:
  errors.append({'estado':name,'native_count':len(ns),'step_count':len(ss),'native_invalid':invalid_n,'step_invalid':invalid_s})
 rec={'estado':name,'native_count':len(ns),'step_count':len(ss),'native_invalid':invalid_n,'step_invalid':invalid_s,
      'native_total_volume_mm3':sum(o.Shape.Volume for o in ns),'step_total_volume_mm3':sum(o.Shape.Volume for o in ss)}
 audit['states'].append(rec)
 App.closeDocument(sd.Name)
 App.closeDocument(nd.Name)
 print('VERIFICADO',name,flush=True)
audit['errors']=errors
(HERE/'AUDITORIA_REIMPORTACION.json').write_text(json.dumps(audit,indent=2)+'\n')
if errors: raise RuntimeError('Verificacion con errores')
