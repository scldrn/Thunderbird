"""Screen a shortlist of translated C08 links at C07 sampled poses.

The combined casing intersection is allowed for study only. Rails and link
connections to cover are excluded intentionally; no carriage is modeled.
"""
from pathlib import Path
import json
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent
ref=json.loads((H/'ENLACES.json').read_text())
rot=json.loads((H.parent/'producto_C08_guias/GUIAS.json').read_text())['rotor_sweep_audit']
d=App.openDocument(str(H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
objs=[o for o in d.Objects if o.Name.startswith('pieza_')];p={o.Label:o.Shape.copy() for o in objs}
allowed=ref['allowed_modification'];own_door='compuerta_C02_0_superior'
door_names=[f'compuerta_C02_{i}_{side}' for i in range(4) for side in ('superior','inferior')]
static={n:s for n,s in p.items() if n not in door_names and n!=allowed}
for i,r in enumerate(rot):
 x,y=r['center_mm'];static['envolvente_rotor_'+str(i)]=Part.makeCylinder(r['radius_mm'],r['height_mm'],App.Vector(x,y,r['zmin_mm']),App.Vector(0,0,1))
# The opposite rail is an obstacle; the rail associated with a link is a
# deliberate unresolved interface, not a physical contact approval.
rails={-130:Part.makeCylinder(2.5,160,App.Vector(-280,-130,25),App.Vector(1,0,0)),
       -25:Part.makeCylinder(2.5,160,App.Vector(-280,-25,75),App.Vector(1,0,0))}
boxes={}
for n,s in static.items():
 b=s.optimalBoundingBox();b.enlarge(.05);boxes[n]=b
poses=[(0,0),(5,0),(10,0),(10,25),(10,50),(10,75),(10,100)]
cache={}
for lift,dx in poses:
 movable={}
 for n in door_names:
  if n==own_door:continue
  _,_,idx,side=n.split('_');sgn_x=-1 if int(idx)<2 else 1;sgn_z=1 if side=='superior' else -1
  sh=p[n].copy();sh.translate(App.Vector(sgn_x*dx,0,sgn_z*lift));b=sh.optimalBoundingBox();b.enlarge(.05)
  movable[n]=(sh,b)
 cache[(lift,dx)]=movable
selected=[]
for y in (-130,-25):
 c=sorted((x for x in ref['cases'] if x['rail_y_mm']==y and x['only_combined_duct_interference']),key=lambda x:x['link_length_mm'])
 selected.extend(c[:4])
res={'scope':'Hasta cuatro enlaces mas cortos por lado, pasador raiz ideal, siete poses discretas; permitido solo componente combinado de ducto; sin carro, fijaciones ni sellos',
     'allowed':allowed,'cases':[]}
for c in selected:
 y,z=c['rail_y_mm'],c['rail_z_mm'];a=App.Vector(-160,y,z);target=App.Vector(*c['target_mm']);direction=target-a;length=direction.Length;direction.normalize()
 base=Part.makeCylinder(1.5,length+2,a,direction)
 row={'rail_y_mm':y,'rail_z_mm':z,'target_mm':c['target_mm'],'length_mm':length+2,'poses':[]}
 for lift,dx in poses:
  sh=base.copy();sh.translate(App.Vector(-dx,0,lift));bb=sh.optimalBoundingBox();bb.enlarge(.05)
  checks=[];fail=None;errors=[]
  otherrail=rails[-25 if y==-130 else -130]
  moving=cache[(lift,dx)]
  for n,s,b in [(n,s,boxes[n]) for n,s in static.items()]+[(n,v[0],v[1]) for n,v in moving.items()]+[('reserva_guia_opuesta',otherrail,otherrail.optimalBoundingBox())]:
   if not bb.intersect(b):continue
   try:
    inter=sh.common(s)
    if not(inter.isNull() or inter.isValid()):raise ValueError('comun invalido')
    volume=inter.Volume;distance=sh.distToShape(s)[0]
    if volume>1e-5 or distance<=1e-6:
     fail={'obstacle':n,'volume_mm3':volume,'distance_mm':distance};break
   except Exception as e:errors.append({'obstacle':n,'error':repr(e)});break
  duct=sh.common(p[allowed]);volume=duct.Volume
  q={'lift_mm':lift,'dx_mm':-dx,'duct_overlap_mm3':volume,'failure':fail,'errors':errors}
  row['poses'].append(q)
  if fail or errors:break
 row['sampled_otherwise_clear']=len(row['poses'])==len(poses) and all(not q['failure'] and not q['errors'] for q in row['poses'])
 res['cases'].append(row)
 (H/'MOVIMIENTO_ENLACES_PARCIAL.json').write_text(json.dumps(res,indent=2)+'\n')
 print('ENLACE_MOVIL',y,'largo',round(length+2,2),'pasa',row['sampled_otherwise_clear'],flush=True)
(H/'MOVIMIENTO_ENLACES.json').write_text(json.dumps(res,indent=2)+'\n')
print('MOVIMIENTO_ENLACES_COMPLETO',flush=True)
