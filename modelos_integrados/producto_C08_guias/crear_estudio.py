"""Export selected rail space reservations and one C07 cover at two poses."""
from pathlib import Path
import gzip,hashlib,json
import FreeCAD as App
import Part
import Import
H=Path(__file__).resolve().parent
scan=json.loads((H/'GUIAS_MOVIMIENTO.json').read_text())
pair=next(a for a in scan['pairs'] if a['z_mm']==25)
src=H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
s=App.openDocument(str(src));p={o.Label:o.Shape.copy() for o in s.Objects if o.Name.startswith('pieza_')}
labels={'piel_superior_C03':'carroceria_C02_superior004','camisa_C03':'modulo_C02_0_camisa_cuna_y_soportes',
        'rotor_C03':'modulo_C02_0_rotor_copa','aro_C03':'aro_C02_0_superior',
        'junta_C03':'junta_C02_0_superior','compuerta_C03':'compuerta_C02_0_superior'}

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

out={'scope':'Dos envolventes de reserva para guias no construidas; una tapa C07, sin conexion ni actuacion',
     'source':str(src),'source_sha256':sha(src),'pair':pair,'states':[]}
for state,lift,dx in [('cerrado',0,0),('abierto',10,-100)]:
 d=App.newDocument('C08_'+state);g=d.addObject('App::Part','C08_local')
 items=[]
 def add(label,shape):
  if shape.isNull() or not shape.isValid() or not shape.Solids:raise ValueError(label)
  o=d.addObject('Part::Feature','Pieza');o.Label=label;o.Shape=shape;g.addObject(o);items.append(o);return o
 for label,n in labels.items():
  sh=p[n].copy()
  if label=='compuerta_C03':sh.translate(App.Vector(dx,0,lift))
  add(label,sh)
 door=next(o.Shape for o in items if o.Label=='compuerta_C03')
 distances=[]
 for j,y in enumerate((pair['left_y_mm'],pair['right_y_mm'])):
  sh=Part.makeCylinder(2.5,160,App.Vector(-280,y,25),App.Vector(1,0,0))
  add('reserva_guia_'+str(j),sh)
  distances.append({'rail':j,'distance_to_cover_mm':sh.distToShape(door)[0]})
 note=d.addObject('App::FeaturePython','Advertencia')
 note.addProperty('App::PropertyString','Alcance','Proyecto')
 note.Alcance='RESERVAS GEOMETRICAS: no son guias construidas, no hay conexion a tapa, actuador ni soportes.'
 d.recompute()
 fc=H/f'C08_local_{state}.FCStd';step=H/f'C08_local_{state}.step'
 d.saveAs(str(fc));Import.export([g],str(step))
 clip=Part.makeBox(270,185,165,App.Vector(-330,-175,-10))
 meshes=[]
 for o in items:
  sh=o.Shape.common(clip) if o.Label in ('piel_superior_C03','camisa_C03') else o.Shape
  if sh.isNull() or not sh.Faces:continue
  vs,ts=sh.tessellate(.4)
  meshes.append({'name':o.Label,'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]})
 with gzip.open(H/f'C08_local_{state}_mallas.json.gz','wt') as f:json.dump({'items':meshes},f,separators=(',',':'))
 out['states'].append({'state':state,'lift_mm':lift,'dx_mm':dx,'fcstd':fc.name,'fcstd_sha256':sha(fc),
                       'step':step.name,'step_sha256':sha(step),'objects':len(items),'rail_door_distances':distances})
 App.closeDocument(d.Name)
 print('C08_CAD',state,flush=True)
(H/'MANIFIESTO.json').write_text(json.dumps(out,indent=2)+'\n')
App.closeDocument(s.Name)
print('C08_ESTUDIO_COMPLETO',flush=True)
