"""Export a reproducible C10 collision, preserving its rejected status."""
from pathlib import Path
import gzip,json
import FreeCAD as App
import Part
import Import
H=Path(__file__).resolve().parent
scan=json.loads((H/'BUSQUEDA_30.json').read_text())
# Choose the collision against the shell with the largest tested travel;
# this is illustrative, not a claim of best trajectory.
choices=[(abs(c['poses'][-1]['dx_mm']),c) for c in scan['cases'] if c['poses'] and (c['poses'][-1].get('collision') or {}).get('name')=='carroceria_C02_superior004']
if not choices:raise ValueError('No hay caso ilustrativo de colision con piel')
_,c=max(choices,key=lambda x:x[0]);pose=c['poses'][-1];lift,dx=pose['lift_mm'],pose['dx_mm']
s=App.openDocument(str(H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'))
p={o.Label:o.Shape.copy() for o in s.Objects if o.Name.startswith('pieza_')}
door=p['compuerta_C02_0_superior'].copy();door.translate(App.Vector(dx,0,lift))
anchor=App.Vector(-160,c['rail_y_mm'],c['rail_z_mm']);target=App.Vector(*c['target_mm'])+App.Vector(dx,0,lift)
vec=target-anchor;length=vec.Length;vec.normalize();link=Part.makeCylinder(1.5,length+2,anchor,vec)
hit=link.common(p['carroceria_C02_superior004'])
if hit.Volume<=1e-5 or not hit.isValid():raise ValueError('No se reproduce colision')
d=App.newDocument('C10_diagnostico');g=d.addObject('App::Part','C10_local')
items=[]
for label,shape in [('piel',p['carroceria_C02_superior004']),('camisa',p['modulo_C02_0_camisa_cuna_y_soportes']),
                    ('rotor',p['modulo_C02_0_rotor_copa']),('aro',p['aro_C02_0_superior']),('junta',p['junta_C02_0_superior']),
                    ('compuerta',door),('enlace_ideal',link),('interseccion_piel',hit)]:
 o=d.addObject('Part::Feature','Pieza');o.Label=label;o.Shape=shape;g.addObject(o);items.append(o)
 if shape.isNull() or not shape.isValid() or not shape.Solids:raise ValueError('invalida '+label)
note=d.addObject('App::FeaturePython','Advertencia');note.addProperty('App::PropertyString','Alcance','Proyecto');note.Alcance='COLISION DEMOSTRADA: enlace telescopico ideal sin uniones ni actuacion, no apto para integracion.'
d.recompute();fc=H/'C10_diagnostico.FCStd';step=H/'C10_diagnostico.step';d.saveAs(str(fc));Import.export([g],str(step))
clip=Part.makeBox(270,185,165,App.Vector(-330,-175,-10));meshes=[]
for o in items:
 sh=o.Shape.common(clip) if o.Label in ('piel','camisa') else o.Shape
 if sh.isNull() or not sh.Faces:continue
 vs,ts=sh.tessellate(.4);meshes.append({'name':o.Label,'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]})
with gzip.open(H/'C10_diagnostico_mallas.json.gz','wt') as f:json.dump({'items':meshes},f,separators=(',',':'))
(H/'DIAGNOSTICO.json').write_text(json.dumps({'scope':'caso rechazado ilustrativo; no mecanismo funcional','case':c,'pose':pose,'reproduced_volume_mm3':hit.Volume,'native':fc.name,'step':step.name,'objects':len(items)},indent=2)+'\n')
print('DIAGNOSTICO_C10_COMPLETO',flush=True)
