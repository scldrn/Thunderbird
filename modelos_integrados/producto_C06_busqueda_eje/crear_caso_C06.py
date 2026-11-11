"""Create one reviewable C06 CAD from completed, recorded screening results."""
from pathlib import Path
import gzip,hashlib,json
import FreeCAD as App
import Part
import Import
HERE=Path(__file__).resolve().parent
r=json.loads((HERE/'ELEVACION.json').read_text())
passed=[c for c in r['cases'] if c['pin_sampled_ok'] and c['door_sampled_ok']]
if passed:
 chosen=min(passed,key=lambda c:(c['lift_max_mm'],c['y_mm'],c['z_mm']))
 selected_status='muestras_sin_interseccion_no_validado'
 target=chosen['door_checks'][-1]
else:
 available=[c for c in r['cases'] if c['pin_sampled_ok'] and c['door_checks']]
 def score(c):
  checks=[q['angle_deg'] for q in c['door_checks'] if not q.get('collision') and not q.get('error')]
  return (max(checks,default=-1),-c['lift_max_mm'])
 chosen=max(available,key=score)
 selected_status='rechazado_colision_muestreada'
 target=chosen['door_checks'][-1]
assert not target.get('error')
y,z=chosen['y_mm'],chosen['z_mm'];lift=target['lift_mm'];ang=target['angle_deg']
source=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
src=App.openDocument(str(source))
p={o.Label:o.Shape.copy() for o in src.Objects if o.Name.startswith('pieza_')}
mapnames={'carroceria_C03':'carroceria_C02_superior004','camisa_C03':'modulo_C02_0_camisa_cuna_y_soportes',
          'rotor_C03':'modulo_C02_0_rotor_copa','aro_C03':'aro_C02_0_superior','junta_C03':'junta_C02_0_superior',
          'compuerta':'compuerta_C02_0_superior'}
def make(name,li,angle):
 d=App.newDocument('C06_'+name);g=d.addObject('App::Part','C06')
 out=[]
 def add(label,shape):
  if shape.isNull() or not shape.isValid() or not shape.Solids:raise ValueError('Forma invalida: '+label)
  o=d.addObject('Part::Feature','Pieza');o.Label=label;o.Shape=shape;g.addObject(o);out.append(o)
 for label,key in mapnames.items():
  sh=p[key].copy()
  if label=='compuerta':
   sh.translate(App.Vector(0,0,li));sh.rotate(App.Vector(-160,y,z+li),App.Vector(1,0,0),angle)
  add(label,sh)
 pin=Part.makeCylinder(1.5,56,App.Vector(-188,y,z+li),App.Vector(1,0,0));add('reserva_eje',pin)
 if name=='evaluacion' and target.get('collision'):
  door=out[5].Shape
  overlap=door.common(p[target['collision']])
  if overlap.Volume<=.001:raise RuntimeError('No se reproduce colision registrada')
  add('interseccion_puerta_obstaculo',overlap)
  print('COLISION_REPRODUCIDA',overlap.Volume,flush=True)
 d.recompute()
 fc=HERE/f'C06_{name}.FCStd';st=HERE/f'C06_{name}.step'
 d.saveAs(str(fc));Import.export([g],str(st))
 # Extract only local CAD meshes. Skin and duct are clipped for inspection;
 # the saved CAD remains uncut. No material represents engineering selection.
 clip=Part.makeBox(160,180,150,App.Vector(-240,-175,0))
 ms=[];markers=[]
 for obj in out:
  sh=obj.Shape.common(clip) if obj.Label in ('carroceria_C03','camisa_C03') else obj.Shape
  if sh.isNull() or not sh.Faces:continue
  v,t=sh.tessellate(.4)
  ms.append({'name':obj.Label,'vertices':[[x.x,x.y,x.z] for x in v],'triangles':[list(q) for q in t]})
  if obj.Label=='interseccion_puerta_obstaculo':
   solids=sh.Solids
   center=sum((s.CenterOfMass*s.Volume for s in solids),App.Vector())*(1/sum(s.Volume for s in solids))
   markers.append([center.x,center.y,center.z])
 with gzip.open(HERE/f'C06_{name}_mallas.json.gz','wt') as f:json.dump({'items':ms,'markers':markers},f,separators=(',',':'))
 print('C06_CAD_EXPORTADO',name,'objetos',len(out),flush=True)
 App.closeDocument(d.Name)
 return {'fcstd':fc.name,'step':st.name,'objects':len(out),'fcstd_sha256':hashlib.sha256(fc.read_bytes()).hexdigest(),'step_sha256':hashlib.sha256(st.read_bytes()).hexdigest()}
result={'status':selected_status,'chosen_case':chosen,'target':target,'scope':'CAD local del caso examinado; sin apoyos ni actuador',
        'cerrado':make('cerrado',0,0),'evaluacion':make('evaluacion',lift,ang)}
(HERE/'CASO_C06.json').write_text(json.dumps(result,indent=2)+'\n')
App.closeDocument(src.Name)
print('CASO_C06_COMPLETO',flush=True)
