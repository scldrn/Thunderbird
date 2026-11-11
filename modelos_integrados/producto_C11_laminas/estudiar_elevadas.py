"""Screen a split C03 cover with four ideal rotating leaves.

One cover only, nominal independent axes and no physical shafts, seal, actuator,
load model or aerodynamic claim. FreeCAD, units mm.
"""
from pathlib import Path
import json,hashlib
import FreeCAD as A
import Part
H=Path(__file__).resolve().parent
src=H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
d=A.openDocument(str(src));objs=[o for o in d.Objects if o.Name.startswith('pieza_')]
p={o.Label:o.Shape.copy() for o in objs};door_name='compuerta_C02_0_superior';door=p[door_name]
rot=json.loads((H.parent/'producto_C08_guias/GUIAS.json').read_text())['rotor_sweep_audit']
obstacles={n:s for n,s in p.items() if n!=door_name}
for i,r in enumerate(rot):
 x,y=r['center_mm'];obstacles['envolvente_rotor_'+str(i)]=Part.makeCylinder(r['radius_mm'],r['height_mm'],A.Vector(x,y,r['zmin_mm']),A.Vector(0,0,1))
boxes={}
for n,s in obstacles.items():
 b=s.optimalBoundingBox();b.enlarge(.05);boxes[n]=b
b=door.optimalBoundingBox();ymin,ymax=b.YMin,b.YMax
kerf=.3;w=(ymax-ymin)/4
leaves=[]
for i in range(4):
 low=ymin+i*w+(kerf/2 if i>0 else 0);high=ymin+(i+1)*w-(kerf/2 if i<3 else 0)
 box=Part.makeBox(b.XLength+4,high-low,b.ZLength+4,A.Vector(b.XMin-2,low,b.ZMin-2))
 s=door.common(box)
 if s.isNull() or not s.isValid() or len(s.Solids)!=1:raise ValueError('lamina invalida '+str(i))
 yc=(low+high)/2;ray=Part.makeLine(A.Vector(-160,yc,0),A.Vector(-160,yc,180));hits=door.section(ray).Vertexes
 if len(hits)<2:raise ValueError('eje no hallado '+str(i))
 zs=[v.Point.z for v in hits];z=(min(zs)+max(zs))/2
 leaves.append({'index':i,'shape':s,'y_axis_mm':yc,'z_axis_mm':z,'low_mm':low,'high_mm':high})
 print('LAMINA',i,'volumen',s.Volume,'eje',yc,z,flush=True)
res={'scope':'Una tapa dividida en cuatro hojas, juntas nominales 0.3mm, ejes ideales sin soportes, rotor envolvente nominal; no sella ni certifica mecanismo o flujo',
     'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
     'closed_original_volume_mm3':door.Volume,'closed_leaves_volume_mm3':sum(x['shape'].Volume for x in leaves),
     'kerf_mm':kerf,'lift_mm':20,'axes':[{'index':x['index'],'y_mm':x['y_axis_mm'],'z_mm':x['z_axis_mm'],'bounds_y_mm':[x['low_mm'],x['high_mm']]} for x in leaves],
     'angles':[]}
(H/'ELEVADAS_PARCIALES.json').write_text(json.dumps(res,indent=2)+'\n')
for angle in (15,30,45,60,75,90):
 rotated=[]
 for leaf in leaves:
  sh=leaf['shape'].copy();sh.translate(A.Vector(0,0,20));sh.rotate(A.Vector(-160,leaf['y_axis_mm'],leaf['z_axis_mm']+20),A.Vector(1,0,0),angle)
  bb=sh.optimalBoundingBox();bb.enlarge(.05);rotated.append((sh,bb))
 row={'angle_deg':angle,'checked_pairs':0,'boolean_count':0,'collisions':[],'errors':[]}
 for i,(shape,bb) in enumerate(rotated):
  for name,other in obstacles.items():
   row['checked_pairs']+=1
   if not bb.intersect(boxes[name]):continue
   row['boolean_count']+=1
   try:
    q=shape.common(other)
    if not(q.isNull() or q.isValid()):raise ValueError('common invalido')
    if q.Volume>.001:row['collisions'].append({'leaf':i,'obstacle':name,'volume_mm3':q.Volume})
   except Exception as e:row['errors'].append({'leaf':i,'obstacle':name,'error':repr(e)})
  for j in range(i+1,4):
   other,ob=rotated[j];row['checked_pairs']+=1
   if not bb.intersect(ob):continue
   row['boolean_count']+=1
   try:
    q=shape.common(other)
    if not(q.isNull() or q.isValid()):raise ValueError('common invalido')
    if q.Volume>.001:row['collisions'].append({'leaf':i,'obstacle':'lamina_'+str(j),'volume_mm3':q.Volume})
   except Exception as e:row['errors'].append({'leaf':i,'obstacle':'lamina_'+str(j),'error':repr(e)})
 row['screened_ok']=not row['collisions'] and not row['errors']
 res['angles'].append(row)
 (H/'ELEVADAS_PARCIALES.json').write_text(json.dumps(res,indent=2)+'\n')
 print('ANGULO',angle,'colisiones',len(row['collisions']),'errores',len(row['errors']),flush=True)
(H/'ELEVADAS.json').write_text(json.dumps(res,indent=2)+'\n')
print('C11_ELEVADAS_COMPLETO',flush=True)
