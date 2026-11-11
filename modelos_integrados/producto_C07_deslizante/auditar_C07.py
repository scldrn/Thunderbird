"""Reopen C07 FCStd/STEP and check door endpoints and fixed rotor centres."""
from pathlib import Path
import hashlib,json
import FreeCAD as App
import Import
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'MANIFIESTO.json').read_text())

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()

report={'scope':'reapertura, reimportacion, validez de formas, traslaciones y centros de rotor; no equivalencia global STEP ni viabilidad fisica','variants':[],'errors':[]}
for e in manifest['variants']:
 mass=e['mass_target_kg'];fc=HERE/e['native'];step=HERE/e['step'];src=Path(e['source'])
 errors=[]
 for path,key in ((fc,'native_sha256'),(step,'step_sha256'),(src,'source_sha256')):
  if sha(path)!=e[key]:errors.append('sha incorrecto '+str(path))
 n=App.openDocument(str(fc));b=App.openDocument(str(src))
 np={o.Label:o for o in n.Objects if o.Name.startswith('pieza_')};bp={o.Label:o for o in b.Objects if o.Name.startswith('pieza_')}
 if len(np)!=316 or len(bp)!=316:errors.append('cantidad de objetos nativos incorrecta')
 invalid=[x for x,o in np.items() if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
 if invalid:errors.append('formas nativas invalidas '+str(invalid))
 door_errors={}
 for m in e['door_transforms']:
  name=m['name'];actual=np[name].Shape.CenterOfMass-bp[name].Shape.CenterOfMass
  err=(actual-App.Vector(m['dx_mm'],0,m['dz_mm'])).Length;door_errors[name]=err
  if err>1e-4:errors.append(f'puerta {name} error {err}')
 rotor_errors={}
 for i in range(4):
  name=f'modulo_C02_{i}_rotor_copa';err=(np[name].Shape.CenterOfMass-bp[name].Shape.CenterOfMass).Length
  rotor_errors[name]=err
  if err>1e-5:errors.append(f'rotor {name} desplazado {err}')
 st=App.newDocument('Revision_STEP_'+str(mass));Import.insert(str(step),st.Name);st.recompute()
 roots=[o for o in st.Objects if o.TypeId=='App::Part' and not o.InList]
 if len(roots)!=1:raise ValueError('STEP raices inesperadas')
 so=list(roots[0].Group)
 sinvalid=[o.Label for o in so if o.Shape.isNull() or not o.Shape.isValid() or not o.Shape.Solids]
 if len(so)!=316 or sinvalid:errors.append('STEP cantidad invalida o formas invalidas')
 row={'mass_target_kg':mass,'native_count':len(np),'step_count':len(so),'native_invalid':invalid,'step_invalid':sinvalid,
      'door_center_errors_mm':door_errors,'rotor_center_motion_mm':rotor_errors,'errors':errors}
 report['variants'].append(row);report['errors']+=errors
 (HERE/'AUDITORIA_PARCIAL.json').write_text(json.dumps(report,indent=2)+'\n')
 App.closeDocument(st.Name);App.closeDocument(b.Name);App.closeDocument(n.Name)
 print('C07_AUDITADO',mass,'errores',len(errors),flush=True)
(HERE/'AUDITORIA.json').write_text(json.dumps(report,indent=2)+'\n')
if report['errors']:raise ValueError('Auditoria fallida')
print('C07_AUDITORIA_COMPLETA',flush=True)
