"""C05 local cutout study derived from the C04 v2 mechanism.

Conservative boxes enclose the specified continuous motion of each mechanism
solid. This program tests a *candidate cutout*, not a structural design.
Run under FreeCAD command line, dimensions in mm.
"""
from pathlib import Path
import sys
import hashlib
import json
import math
import FreeCAD as App
import Part
import Import

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from envolvente import motion_bounds
SOURCE=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
MECHANISM=HERE.parent/'producto_C04_estudio_bisagra_v2/C04_cerrado.FCStd'
AXIS=(-160.0,-124.0,67.9767683408146)
MARGIN=0.5


def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()


def bb(s):
 b=s.BoundBox
 return (b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax)


def makebox(b):
 return Part.makeBox(b[1]-b[0],b[3]-b[2],b[5]-b[4],App.Vector(b[0],b[2],b[4]))


def measure(a,b):
 try:
  c=a.common(b)
  return {'distancia_mm':a.distToShape(b)[0], 'interseccion_mm3':c.Volume,
          'interseccion_valida':c.isNull() or c.isValid()}
 except Exception as e:
  return {'error':repr(e)}


def moved(s,lift,angle):
 r=s.copy()
 r.translate(App.Vector(0,0,lift))
 r.rotate(App.Vector(AXIS[0],AXIS[1],AXIS[2]+lift),App.Vector(1,0,0),angle)
 return r


def main():
 source=App.openDocument(str(SOURCE))
 baseline={o.Label:o.Shape.copy() for o in source.Objects if o.Name.startswith('pieza_')}
 mechdoc=App.openDocument(str(MECHANISM))
 objs=list(mechdoc.getObject('Estudio_C04').Group)
 assert len(objs)==14
 assert [o.Label for o in objs[:3]]==['compuerta_C03','aro_C03','rotor_C03']
 hardware=[]
 for o in objs[3:]:
  kind='fijo' if o.Label.startswith('guia_fija') else ('giro' if o.Label.startswith('brazo_tapa') else 'traslacion')
  bound=motion_bounds(bb(o.Shape),AXIS,10,110,kind,MARGIN)
  hardware.append({'nombre':o.Label,'movimiento':kind,'caja_mm':bound,'shape':o.Shape.copy(),'cutter':makebox(bound)})
 print('CAJAS_GENERADAS',len(hardware),flush=True)
 union=hardware[0]['cutter'].multiFuse([h['cutter'] for h in hardware[1:]])
 if union.isNull() or not union.isValid(): raise ValueError('Union de envolventes invalida')
 print('UNION_CAJAS_VALIDA',union.Volume,flush=True)
 body=baseline['carroceria_C02_superior004']
 revised=body.cut(union)
 if revised.isNull() or not revised.isValid(): raise ValueError('Carroceria recortada invalida')
 removed=body.common(union)
 if not removed.isValid():raise ValueError('Interseccion recortada invalida')
 print('CUERPO_RECORTADO',len(body.Solids),len(revised.Solids),body.Volume,revised.Volume,removed.Volume,flush=True)
 obs=[('carroceria_original',body),('carroceria_recortada',revised),('camisa_C03',baseline['modulo_C02_0_camisa_cuna_y_soportes']),
      ('rotor_C03',objs[2].Shape),('aro_C03',objs[1].Shape),('junta_C03',baseline['junta_C02_0_superior']),('compuerta_cerrada',objs[0].Shape)]
 cut_obstacles={name:measure(union,shape) for name,shape in obs if name not in ('carroceria_recortada',)}
 print('OBSTACULOS_CORTE',json.dumps(cut_obstacles),flush=True)
 report={'revision':'C05_recorte_exploratorio','source_C03':str(SOURCE),'source_C03_sha256':sha(SOURCE),
  'mechanism_C04':str(MECHANISM),'mechanism_C04_sha256':sha(MECHANISM),'axis_mm':AXIS,'lift_mm':10,'angle_deg':110,
  'box_clearance_mm':MARGIN,'scope':'Una compuerta; cajas conservadoras para las piezas propuestas, sin mecanismo real ni validacion de estructura',
  'motion_envelopes':[{k:v for k,v in h.items() if k not in ('shape','cutter')} for h in hardware],
  'original_body':{'volume_mm3':body.Volume,'solids':len(body.Solids),'area_mm2':body.Area},
  'revised_body':{'volume_mm3':revised.Volume,'solids':len(revised.Solids),'area_mm2':revised.Area},
  'removed':{'volume_mm3':removed.Volume,'solids':len(removed.Solids)},
  'cutout_against_obstacles':cut_obstacles,'samples':[]}
 (HERE/'RESULTADOS_PARCIALES.json').write_text(json.dumps(report,indent=2)+'\n')
 # Keep the cut body and cutting envelopes for independent inspection.
 doc=App.newDocument('C05_estudio')
 group=doc.addObject('App::Part','C05')
 def add(label,shape):
  obj=doc.addObject('Part::Feature','Pieza');obj.Label=label;obj.Shape=shape;group.addObject(obj)
  return obj
 add('carroceria_superior_C03_recortada',revised)
 add('material_retirado',removed)
 add('envolventes_reserva',union)
 add('aro_original_C03',objs[1].Shape)
 add('junta_original_C03',baseline['junta_C02_0_superior'])
 add('compuerta_original_C03',objs[0].Shape)
 doc.recompute()
 native=HERE/'C05_alojamiento_estudio.FCStd'
 step=HERE/'C05_alojamiento_estudio.step'
 doc.saveAs(str(native));Import.export([group],str(step))
 report['artifacts']={'native':native.name,'native_sha256':sha(native),'step':step.name,'step_sha256':sha(step)}
 print('CAD_EXPORTADO',flush=True)
 # The 12 instants give a useful kernel check, not the continuous proof.
 # Analytical boxes enclose both phases for ideal rigid solids and fixed axis.
 for phase,lift,angle in [('elevacion',float(i),0.0) for i in (0,2,4,6,8,10)] + [('giro',10.0,float(i)) for i in (22,44,66,88,110)]:
  rows=[]
  for h in hardware:
   shape=h['shape'] if h['movimiento']=='fijo' else moved(h['shape'],lift,angle if h['movimiento']=='giro' else 0)
   record={'nombre':h['nombre']}
   record['vs_carroceria_recortada']=measure(shape,revised)
   record['vs_camisa']=measure(shape,baseline['modulo_C02_0_camisa_cuna_y_soportes'])
   record['vs_rotor']=measure(shape,objs[2].Shape)
   rows.append(record)
  report['samples'].append({'fase':phase,'lift_mm':lift,'angulo_deg':angle,'partes':rows})
  (HERE/'RESULTADOS_PARCIALES.json').write_text(json.dumps(report,indent=2)+'\n')
  print('MUESTRA',phase,lift,angle,flush=True)
 (HERE/'RESULTADOS.json').write_text(json.dumps(report,indent=2)+'\n')
 App.closeDocument(doc.Name);App.closeDocument(mechdoc.Name);App.closeDocument(source.Name)
 print('C05_COMPLETO',flush=True)

main()
