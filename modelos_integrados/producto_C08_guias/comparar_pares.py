"""Compare independent rail heights using distances to one cover.

Distance is a lower bound on link length, not a viable connection.
"""
from pathlib import Path
import itertools,json
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent
r=json.loads((H/'GUIAS_MOVIMIENTO.json').read_text())
d=App.openDocument(str(H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
door=next(o.Shape.copy() for o in d.Objects if o.Name.startswith('pieza_') and o.Label=='compuerta_C02_0_superior')
opened=door.copy();opened.translate(App.Vector(-100,0,10))
rails=[]
for c in r['candidates']:
 if not c['screened_ok']:continue
 y,z=c['y_mm'],c['z_mm'];rail=Part.makeCylinder(2.5,160,App.Vector(-280,y,z),App.Vector(1,0,0))
 rails.append({'y_mm':y,'z_mm':z,'distance_closed_mm':rail.distToShape(door)[0],
               'distance_open_mm':rail.distToShape(opened)[0]})
left=[v for v in rails if v['y_mm'] < -76]
right=[v for v in rails if v['y_mm'] > -76]
pairs=[]
for a,b in itertools.product(left,right):
 dist=((a['y_mm']-b['y_mm'])**2+(a['z_mm']-b['z_mm'])**2)**.5-5
 pairs.append({'left':a,'right':b,'rail_spacing_clear_mm':dist,
               'max_closed_gap_mm':max(a['distance_closed_mm'],b['distance_closed_mm']),
               'max_endpoint_gap_mm':max(a['distance_closed_mm'],a['distance_open_mm'],b['distance_closed_mm'],b['distance_open_mm'])})
pairs.sort(key=lambda c:(c['max_endpoint_gap_mm'],c['left']['distance_open_mm']+c['right']['distance_open_mm'],c['left']['z_mm'],c['right']['z_mm']))
out={'scope':'distancias minimas de los cilindros de reserva a la tapa en dos extremos; no garantizan un enlace libre ni conexión cinematica','rails':rails,'pairs':pairs}
(H/'COMPARACION_PARES.json').write_text(json.dumps(out,indent=2)+'\n')
print('PARES_EVALUADOS',len(pairs),'mejor_cota',pairs[0]['max_endpoint_gap_mm'],flush=True)
