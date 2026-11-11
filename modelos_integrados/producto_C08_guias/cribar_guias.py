"""Screen hypothetical 160-mm axial rail reservations in C03 5kg.

A 5-mm-diameter cylinder includes a notional 4-mm guide plus 0.5 mm radial
allowance. No guides, anchorage or kinematic connection are thereby designed.
"""
from pathlib import Path
import hashlib,itertools,json,math,time
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent
SRC=H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
X0=-280.0;L=160.0;RAD=2.5
YS=(-145,-130,-115,-100,-85,-70,-55,-40,-25)
ZS=(5,15,25,35,45,55,65,75)
d=App.openDocument(str(SRC))
objs=[o for o in d.Objects if o.Name.startswith('pieza_')]
if len(objs)!=316:raise ValueError('recuento inesperado')
p={o.Label:o.Shape.copy() for o in objs}
if len(p)!=316:raise ValueError('nombres duplicados')
# Expanded optimal AABBs filter; actual intersections use exact CAD booleans.
boxes={}
for i,o in enumerate(objs):
 b=o.Shape.optimalBoundingBox()
 if not b.isValid():raise ValueError('caja invalida '+o.Label)
 b.enlarge(.05);boxes[o.Label]=b
 if (i+1)%100==0:print('CAJAS',i+1,flush=True)

# A rotor-rotation cylinder is checked to contain the nominal CAD rotor first.
sweeps={};rotor_audit=[]
for i in range(4):
 n=f'modulo_C02_{i}_rotor_copa';shape=p[n];b=shape.optimalBoundingBox()
 xc=(b.XMin+b.XMax)/2;yc=(b.YMin+b.YMax)/2
 radius=max((b.XMax-b.XMin)/2,(b.YMax-b.YMin)/2)+.5
 low=b.ZMin-.5;height=b.ZMax-b.ZMin+1
 cylinder=Part.makeCylinder(radius,height,App.Vector(xc,yc,low),App.Vector(0,0,1))
 rem=shape.cut(cylinder)
 if not (rem.isNull() or rem.isValid()):raise ValueError('auditoria de rotor invalida')
 rotor_audit.append({'rotor':n,'center_mm':[xc,yc], 'radius_mm':radius,'zmin_mm':low,'height_mm':height,'outside_volume_mm3':rem.Volume})
 if rem.Volume>.001:raise ValueError('cilindro no contiene rotor '+n)
 sweeps['envolvente_giro_'+str(i)]=cylinder
 b=cylinder.optimalBoundingBox();b.enlarge(.05);boxes['envolvente_giro_'+str(i)]=b
print('ROTORES_ENVUELTOS',len(rotor_audit),flush=True)

# Sample roof and floor with three x stations and three lateral stations.
upper=[p['carroceria_C02_superior004']]+[p[f'compuerta_C02_{i}_superior'] for i in (0,1)]
lower=[p['carroceria_C02_inferior003']]+[p[f'compuerta_C02_{i}_inferior'] for i in (0,1)]
roof={}
for y in YS:
 rays=[]
 for x in (-279,-200,-121):
  for dy in (0,-2.4,2.4):
   ray=Part.makeLine(App.Vector(x,y+dy,-180),App.Vector(x,y+dy,180))
   top=[];bottom=[]
   for s in upper:top.extend(v.Point.z for v in s.section(ray).Vertexes)
   for s in lower:bottom.extend(v.Point.z for v in s.section(ray).Vertexes)
   rays.append({'x_mm':x,'y_mm':y+dy,'upper_z_mm':max(top) if top else None,'lower_z_mm':min(bottom) if bottom else None})
 roof[y]=rays
 print('ENVOLVENTE_RAYOS',y,flush=True)

report={'scope':'Una reserva fija por candidato, bajo techo/suelo muestreados y contra 316 registros CAD y cuatro cilindros de giro nominal. No prueba conexion, soportes, trayectoria completa, deformacion ni flujo.',
        'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
        'rail_mm':{'x_start':X0,'length':L,'radius_reservation':RAD,'nominal_diameter_assumption':4,'radial_allowance_assumption':.5},
        'grid_y_mm':YS,'grid_z_mm':ZS,'rotor_sweep_audit':rotor_audit,'roof_samples':roof,'candidates':[]}
allshapes=list(p.items())+list(sweeps.items())
for i,(y,z) in enumerate(itertools.product(YS,ZS)):
 rows=roof[y]
 contained=all(a['upper_z_mm'] is not None and a['lower_z_mm'] is not None and z+RAD<a['upper_z_mm'] and z-RAD>a['lower_z_mm'] for a in rows)
 row={'y_mm':y,'z_mm':z,'roof_floor_sampled_ok':contained,'tested_count':0,'boolean_count':0}
 if contained:
  rail=Part.makeCylinder(RAD,L,App.Vector(X0,y,z),App.Vector(1,0,0))
  rb=rail.optimalBoundingBox();rb.enlarge(.05)
  for n,shape in allshapes:
   row['tested_count']+=1
   if not rb.intersect(boxes[n]):continue
   row['boolean_count']+=1
   try:
    inter=rail.common(shape)
    if not(inter.isNull() or inter.isValid()):raise ValueError('comun invalido')
    v=inter.Volume;dist=rail.distToShape(shape)[0]
    if v>1e-5 or dist<=1e-6:
     row['obstruction']={'name':n,'volume_mm3':v,'distance_mm':dist};break
   except Exception as e:
    row['error']={'name':n,'detail':repr(e)};break
  row['clear_closed']=('obstruction' not in row and 'error' not in row and row['tested_count']==len(allshapes))
 else:row['clear_closed']=False
 report['candidates'].append(row)
 if (i+1)%5==0 or i+1==len(YS)*len(ZS):
  (H/'GUIAS_PARCIAL.json').write_text(json.dumps(report,indent=2)+'\n')
  print('GUIAS',i+1,'de',len(YS)*len(ZS),'libres',sum(x['clear_closed'] for x in report['candidates']),flush=True)
clear=[x for x in report['candidates'] if x['clear_closed']]
report['same_z_straddling_pairs']=[{'left_y_mm':a['y_mm'],'right_y_mm':b['y_mm'],'z_mm':a['z_mm'],'spacing_mm':b['y_mm']-a['y_mm']}
 for a in clear for b in clear if a['y_mm']<-76<b['y_mm'] and a['z_mm']==b['z_mm'] and b['y_mm']-a['y_mm']>=30]
(H/'GUIAS.json').write_text(json.dumps(report,indent=2)+'\n')
print('GUIAS_COMPLETO libres',len(clear),'pares',len(report['same_z_straddling_pairs']),flush=True)
