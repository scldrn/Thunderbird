"""Export one split-cover candidate at closed and lifted/60deg poses."""
from pathlib import Path
import gzip,json,hashlib
import FreeCAD as A
import Part,Import
H=Path(__file__).resolve().parent
result=json.loads((H/'ELEVADAS_PARCIALES.json').read_text())
src=H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
s=A.openDocument(str(src));p={o.Label:o.Shape.copy() for o in s.Objects if o.Name.startswith('pieza_')}
door=p['compuerta_C02_0_superior'];bb=door.optimalBoundingBox()
leaves=[]
for a in result['axes']:
 lo,hi=a['bounds_y_mm'];box=Part.makeBox(bb.XLength+4,hi-lo,bb.ZLength+4,A.Vector(bb.XMin-2,lo,bb.ZMin-2))
 sh=door.common(box)
 if sh.isNull() or not sh.isValid() or len(sh.Solids)!=1:raise ValueError('lamina invalida')
 leaves.append((a,sh))
fixed={'piel':'carroceria_C02_superior004','camisa':'modulo_C02_0_camisa_cuna_y_soportes',
       'rotor':'modulo_C02_0_rotor_copa','aro':'aro_C02_0_superior','junta':'junta_C02_0_superior'}
manifest={'scope':'una tapa fraccionada en cuatro laminas; apertura ideal, sin eje fisico, mecanismo, sello ni cargas', 'states':[]}
for state,lift,angle in [('cerrado',0,0),('elevado_60',20,60)]:
 d=A.newDocument('C11_'+state);g=d.addObject('App::Part','C11_local');items=[]
 def add(label,shape):
  if shape.isNull() or not shape.isValid() or not shape.Solids:raise ValueError(label)
  o=d.addObject('Part::Feature','Pieza');o.Label=label;o.Shape=shape;g.addObject(o);items.append(o)
 for label,name in fixed.items():add(label,p[name])
 for a,shape in leaves:
  sh=shape.copy();sh.translate(A.Vector(0,0,lift));sh.rotate(A.Vector(-160,a['y_mm'],a['z_mm']+lift),A.Vector(1,0,0),angle)
  add('lamina_'+str(a['index']),sh)
 note=d.addObject('App::FeaturePython','Advertencia');note.addProperty('App::PropertyString','Alcance','Proyecto')
 note.Alcance='Estudio de poses: sin sellos ni guias ni ejes ni actuacion; cribado C11 obligatorio.'
 d.recompute();fc=H/f'C11_{state}.FCStd';step=H/f'C11_{state}.step';d.saveAs(str(fc));Import.export([g],str(step))
 clip=Part.makeBox(200,170,165,A.Vector(-255,-160,0));mesh=[]
 for o in items:
  sh=o.Shape.common(clip) if o.Label in ('piel','camisa') else o.Shape
  if sh.isNull() or not sh.Faces:continue
  vs,ts=sh.tessellate(.4);mesh.append({'name':o.Label,'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]})
 with gzip.open(H/f'C11_{state}_mallas.json.gz','wt') as f:json.dump({'items':mesh},f,separators=(',',':'))
 manifest['states'].append({'state':state,'lift_mm':lift,'angle_deg':angle,'objects':len(items),'fcstd':fc.name,'step':step.name,
                            'fcstd_sha256':hashlib.sha256(fc.read_bytes()).hexdigest(),'step_sha256':hashlib.sha256(step.read_bytes()).hexdigest()})
 A.closeDocument(d.Name);print('C11_CAD',state,flush=True)
(H/'MANIFIESTO.json').write_text(json.dumps(manifest,indent=2)+'\n')
A.closeDocument(s.Name);print('C11_CAD_COMPLETO',flush=True)
