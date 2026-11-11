"""Create full C07 conceptual sliding-cover configurations from C03.

The doors are posed only. No hardware, actuator, mass or flight is approved.
The 10 kg version is geometric similarity, not a component selection.
"""
from pathlib import Path
import gzip,hashlib,json
import FreeCAD as App
import Import
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C03'

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()

manifest={'revision':'C07_DESLIZANTE_EXPLORATORIA','status':'conceptual_no_validado','architecture':'ventiladores internos; ocho tapas trasladadas; sin guias ni accionamiento',
          'scale_10kg':'semejanza geometrica, masa y hardware no resueltos','variants':[]}
for mass in (5,10):
 factor=(mass/5.0)**(1/3)
 src=SOURCE/f'{mass}kg'/f'C03_{mass}kg_cerrado.FCStd'
 doc=App.openDocument(str(src)); group=doc.getObject('Conjunto_C03')
 if not group:raise ValueError('Grupo de referencia no encontrado')
 objs=[o for o in doc.Objects if o.Name.startswith('pieza_')]
 if len(objs)!=316:raise ValueError(f'Numero de piezas inesperado {len(objs)}')
 moved=[]
 for o in objs:
  name=o.Label
  if not name.startswith('compuerta_C02_'):continue
  _,_,num,side=name.split('_')
  i=int(num)
  sign_x=-1 if i in (0,1) else 1
  sign_z=1 if side=='superior' else -1
  before=o.Shape.CenterOfMass
  shape=o.Shape.copy();shape.translate(App.Vector(sign_x*100*factor,0,sign_z*10*factor))
  if not shape.isValid() or not shape.Solids:raise ValueError('Compuerta invalida '+name)
  o.Shape=shape
  actual=shape.CenterOfMass-before
  err=(actual-App.Vector(sign_x*100*factor,0,sign_z*10*factor)).Length
  if err>1e-5:raise ValueError('Traslacion incorrecta '+name)
  moved.append({'name':name,'dx_mm':sign_x*100*factor,'dz_mm':sign_z*10*factor,'error_mm':err})
 if len(moved)!=8:raise ValueError(f'Se esperaban ocho compuertas, no {len(moved)}')
 note=doc.getObject('Alcance_conceptual')
 if note:
  note.Revision='C07_deslizante_exploratoria'
  note.Estado='abierto por traslacion; soporte y secuencia no implementados'
  note.Compuertas='Poses de las ocho tapas; guias, accionamientos y cierres no definidos.'
  note.PrestacionesValidadas=False
 doc.recompute()
 dest=HERE/f'{mass}kg';dest.mkdir(parents=True,exist_ok=True)
 native=dest/f'C07_{mass}kg_deslizante_abierto.FCStd'
 step=dest/f'C07_{mass}kg_deslizante_abierto.step'
 doc.saveAs(str(native));Import.export([group],str(step))
 print('C07_CAD_EXPORTADO',mass,flush=True)
 entry={'mass_target_kg':mass,'scale':factor,'source':str(src),'source_sha256':sha(src),'native':str(native.relative_to(HERE)),
        'native_sha256':sha(native),'step':str(step.relative_to(HERE)),'step_sha256':sha(step),'parts':len(objs),'door_transforms':moved}
 manifest['variants'].append(entry)
 (HERE/'MANIFIESTO_PARCIAL.json').write_text(json.dumps(manifest,indent=2)+'\n')
 if mass==5:
  parts=[]
  for o in objs:
   vertices=[];triangles=[]
   for face in o.Shape.Faces:
    fv,ft=face.tessellate(.3);offset=len(vertices)
    vertices.extend([[v.x*.001,v.y*.001,v.z*.001] for v in fv])
    triangles.extend([[offset+j for j in tri] for tri in ft])
   parts.append({'name':o.Label,'vertices_m':vertices,'triangles':triangles})
  m={'revision':'C07','state':'abierto','source_native_sha256':sha(native),'parts':parts}
  with gzip.open(dest/'C07_5kg_mallas_caras.json.gz','wt') as f:json.dump(m,f,separators=(',',':'))
  print('C07_MALLA_EXPORTADA',len(parts),flush=True)
 App.closeDocument(doc.Name)
(HERE/'MANIFIESTO.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('C07_GENERACION_COMPLETA',flush=True)
