"""Full obstacle bookkeeping for the shortest eligible C08 link per side.

No collider is silently permitted; intended own-cover and own-rail interfaces
are excluded and are not modeled. Positions are discrete.
"""
from pathlib import Path
from collections import Counter
import json
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent
source=json.loads((H/'ENLACES.json').read_text())
rot=json.loads((H.parent/'producto_C08_guias/GUIAS.json').read_text())['rotor_sweep_audit']
d=App.openDocument(str(H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape.copy() for o in d.Objects if o.Name.startswith('pieza_')}
all_doors=[f'compuerta_C02_{i}_{side}' for i in range(4) for side in ('superior','inferior')]
own='compuerta_C02_0_superior'
static={n:s for n,s in p.items() if n not in all_doors}
for i,r in enumerate(rot):
 x,y=r['center_mm'];static['envolvente_rotor_'+str(i)]=Part.makeCylinder(r['radius_mm'],r['height_mm'],App.Vector(x,y,r['zmin_mm']),App.Vector(0,0,1))
boxes={}
for n,s in static.items():
 b=s.optimalBoundingBox();b.enlarge(.05);boxes[n]=b
rails={-130:Part.makeCylinder(2.5,160,App.Vector(-280,-130,25),App.Vector(1,0,0)),
       -25:Part.makeCylinder(2.5,160,App.Vector(-280,-25,75),App.Vector(1,0,0))}
chosen=[]
for y in (-130,-25):
 cases=[c for c in source['cases'] if c['rail_y_mm']==y and c['only_combined_duct_interference']]
 chosen.append(min(cases,key=lambda c:c['link_length_mm']))
poses=[(0,0),(5,0),(10,0),(10,25),(10,50),(10,75),(10,100)]
res={'scope':'Dos enlaces mas cortos elegibles, colisiones completas en 7 poses; sin interfaz con tapa o guia, sin estructura o sellado',
     'cases':[]}
for c in chosen:
 y,z=c['rail_y_mm'],c['rail_z_mm'];a=App.Vector(-160,y,z);b=App.Vector(*c['target_mm']);direction=b-a;length=direction.Length;direction.normalize()
 initial=Part.makeCylinder(1.5,length+2,a,direction)
 row={'rail_y_mm':y,'rail_z_mm':z,'target_mm':c['target_mm'],'length_mm':length+2,'poses':[]}
 for lift,dx in poses:
  link=initial.copy();link.translate(App.Vector(-dx,0,lift));lb=link.optimalBoundingBox();lb.enlarge(.05)
  mov={}
  for name in all_doors:
   if name==own:continue
   _,_,idx,side=name.split('_');sx=-1 if int(idx)<2 else 1;sz=1 if side=='superior' else -1
   sh=p[name].copy();sh.translate(App.Vector(sx*dx,0,sz*lift));bb=sh.optimalBoundingBox();bb.enlarge(.05);mov[name]=(sh,bb)
  otherrail=rails[-25 if y==-130 else -130];rb=otherrail.optimalBoundingBox();rb.enlarge(.05)
  comparisons=[(n,s,boxes[n]) for n,s in static.items()]+[(n,s,b) for n,(s,b) in mov.items()]+[('reserva_guia_opuesta',otherrail,rb)]
  record={'lift_mm':lift,'dx_mm':-dx,'pairs':0,'boolean_count':0,'collisions':[],'errors':[]}
  for n,s,bb in comparisons:
   record['pairs']+=1
   if not lb.intersect(bb):continue
   record['boolean_count']+=1
   try:
    q=link.common(s)
    if not(q.isNull() or q.isValid()):raise ValueError('comun invalido')
    v=q.Volume;dist=link.distToShape(s)[0]
    if v>1e-5 or dist<=1e-6:record['collisions'].append({'name':n,'volume_mm3':v,'distance_mm':dist})
   except Exception as e:record['errors'].append({'name':n,'error':repr(e)})
  row['poses'].append(record)
  (H/'RUTA_DETALLADA_PARCIAL.json').write_text(json.dumps({'scope':res['scope'],'cases':res['cases']+[row]},indent=2)+'\n')
  print('RUTA',y,lift,-dx,'colisiones',len(record['collisions']),'errores',len(record['errors']),flush=True)
 res['cases'].append(row)
(H/'RUTA_DETALLADA.json').write_text(json.dumps(res,indent=2)+'\n')
print('RUTA_COMPLETA',flush=True)
