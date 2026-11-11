"""Sample vertical rays over a candidate axis; not a full containment proof."""
from pathlib import Path
import json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
scan=json.loads((HERE/'BUSQUEDA_EJE.json').read_text())
d=App.openDocument(str(HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape for o in d.Objects if o.Name.startswith('pieza_')}
roof=[p['carroceria_C02_superior004'],p['compuerta_C02_0_superior']]
# At every station sample the projected centre and two radial edges.
# The ends are inset slightly because a circular end-face shrinks to a point.
stations=(-160,-187,-133)
y_offsets=(0,-1.4,1.4)
records=[]
for c in scan['candidates']:
 if not c['passed_closed']:continue
 y,z=c['y_mm'],c['z_mm']
 rays=[]
 for x in stations:
  for dy in y_offsets:
   ray=Part.makeLine(App.Vector(x,y+dy,z-5),App.Vector(x,y+dy,180))
   heights=[]
   try:
    for solid in roof:
     hit=solid.section(ray)
     heights.extend(v.Point.z for v in hit.Vertexes if v.Point.z>z+1.5+1e-5)
    top=max(heights) if heights else None
    rays.append({'x_mm':x,'y_mm':y+dy,'surface_above_z_mm':top})
   except Exception as e:
    rays.append({'x_mm':x,'y_mm':y+dy,'error':str(e)})
   if not heights:break
  if not rays[-1].get('surface_above_z_mm'):break
 passes=len(rays)==9 and all(r.get('surface_above_z_mm') is not None and 'error' not in r for r in rays)
 records.append({'y_mm':y,'z_mm':z,'rays':rays,'all_rays_covered':passes})
 (HERE/'COBERTURA_PARCIAL.json').write_text(json.dumps({'candidates':records},indent=2)+'\n')
print('AUDITADAS_CUBIERTAS',len(records),'nueve_rayos_pasan',sum(r['all_rays_covered'] for r in records),flush=True)
(HERE/'COBERTURA.json').write_text(json.dumps({'scope':'Nueve rayos verticales por eje contra carroceria superior y una compuerta; no prueba de contencion global ni espacio para soportes', 'candidates':records},indent=2)+'\n')
