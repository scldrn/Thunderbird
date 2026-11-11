"""Export one recorded sliding-door scenario as local inspection CAD."""
from pathlib import Path
import gzip,hashlib,json
import FreeCAD as App
import Part
import Import
HERE=Path(__file__).resolve().parent
source_results = HERE/'DESLIZAMIENTO.json'
if not source_results.exists():
 source_results = HERE/'DESLIZAMIENTO_PARCIAL.json'
r=json.loads(source_results.read_text())
passing=[c for c in r['cases'] if c['sampled_ok']]
if passing:
 c=min(passing,key=lambda c:(c['lift_max_mm'],c['direction_x']))
 status='muestras_sin_interseccion_no_validado'
else:
 def score(row):
  passed=[abs(q['dx_mm']) for q in row['checks'] if not q.get('collision') and not q.get('error')]
  return max(passed,default=-1),-row['lift_max_mm']
 c=max(r['cases'],key=score);status='rechazado_colision_muestreada'
target=c['checks'][-1]
if target.get('error'):raise ValueError('El caso termino en error')
source=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
s=App.openDocument(str(source))
p={o.Label:o.Shape.copy() for o in s.Objects if o.Name.startswith('pieza_')}
mapnames={'carroceria_C03':'carroceria_C02_superior004','camisa_C03':'modulo_C02_0_camisa_cuna_y_soportes',
          'rotor_C03':'modulo_C02_0_rotor_copa','aro_C03':'aro_C02_0_superior','junta_C03':'junta_C02_0_superior',
          'compuerta_C03':'compuerta_C02_0_superior'}

def make(name,lift,dx):
 d=App.newDocument('C06_deslizante_'+name);g=d.addObject('App::Part','C06_deslizante')
 objs=[]
 for label,key in mapnames.items():
  sh=p[key].copy()
  if label=='compuerta_C03':sh.translate(App.Vector(dx,0,lift))
  if sh.isNull() or not sh.isValid() or not sh.Solids:raise ValueError(label)
  o=d.addObject('Part::Feature','Pieza');o.Label=label;o.Shape=sh;g.addObject(o);objs.append(o)
 if name=='evaluacion' and target.get('collision'):
  sh=objs[-1].Shape.common(p[target['collision']])
  if sh.Volume<=.001:raise ValueError('Colision no reproducida')
  o=d.addObject('Part::Feature','Pieza');o.Label='interseccion';o.Shape=sh;g.addObject(o);objs.append(o)
 d.recompute()
 fc=HERE/f'C06_deslizante_{name}.FCStd';step=HERE/f'C06_deslizante_{name}.step'
 d.saveAs(str(fc));Import.export([g],str(step))
 clip=Part.makeBox(270,180,160,App.Vector(-330,-175,-10))
 meshes=[];markers=[]
 for o in objs:
  sh=o.Shape.common(clip) if o.Label in ('carroceria_C03','camisa_C03') else o.Shape
  if sh.isNull() or not sh.Faces:continue
  verts,faces=sh.tessellate(.4)
  meshes.append({'name':o.Label,'vertices':[[v.x,v.y,v.z] for v in verts],'triangles':[list(t) for t in faces]})
  if o.Label=='interseccion':
   solids=sh.Solids
   v=sum((z.CenterOfMass*z.Volume for z in solids),App.Vector())*(1/sum(z.Volume for z in solids))
   markers.append([v.x,v.y,v.z])
 with gzip.open(HERE/f'C06_deslizante_{name}_mallas.json.gz','wt') as f:json.dump({'items':meshes,'markers':markers},f,separators=(',',':'))
 result={'fcstd':fc.name,'step':step.name,'objects':len(objs),'fcstd_sha256':hashlib.sha256(fc.read_bytes()).hexdigest(),'step_sha256':hashlib.sha256(step.read_bytes()).hexdigest()}
 App.closeDocument(d.Name)
 print('CAD_DESLIZANTE',name,len(objs),flush=True)
 return result
report={'source_results':source_results.name,'status':status,'chosen_case':c,'target':target,'scope':'Posiciones geométricas de una sola tapa; no incluye guias, accionadores ni soportes',
        'cerrado':make('cerrado',0,0),'evaluacion':make('evaluacion',target['lift_mm'],target['dx_mm'])}
(HERE/'CASO_DESLIZANTE.json').write_text(json.dumps(report,indent=2)+'\n')
App.closeDocument(s.Name)
print('CASO_DESLIZANTE_COMPLETO',flush=True)
