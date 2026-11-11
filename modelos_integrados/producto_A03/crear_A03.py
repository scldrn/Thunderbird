"""A03 product-design CAD. Dimensions in mm; hardware remains developmental."""
from pathlib import Path
import ast,json,math,hashlib,csv
import numpy as np
import cadquery as cq
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.gp import gp_Lin,gp_Pnt,gp_Dir

OUT=Path(__file__).resolve().parent;ROOT=OUT.parent
REF=OUT/'referencias'
PARTS=[];CHECKS=[]
COL={'shell':(.055,.070,.080),'top':(.09,.108,.12),'dark':(.018,.025,.032),'copper':(.63,.27,.10),'metal':(.43,.49,.54),'mechanism':(.16,.24,.27),'blue':(.025,.15,.21)}
def add(name,s,color='metal',visible=True,scope='designed_geometry'):
 if s.Volume()<1e-5:return
 if not s.isValid():raise ValueError('Invalid part '+name)
 PARTS.append(dict(name=name,shape=s,color=COL[color],exterior=visible,scope=scope))
def box(center,dims):return cq.Workplane('XY').box(*dims).translate(tuple(center)).val()
def cyl(p,n,r,h):return cq.Solid.makeCylinder(r,h,cq.Vector(*p),cq.Vector(*n))
def ring(p,n,ro,ri,h):return cyl(p,n,ro,h).cut(cyl(p,n,ri,h))
def inset_polygon(yz,d):
 v=np.asarray(yz,float);edges=np.roll(v,-1,axis=0)-v
 normals=np.column_stack([-edges[:,1],edges[:,0]])/np.linalg.norm(edges,axis=1)[:,None]
 return [np.linalg.solve(np.array([normals[i-1],normals[i]]),[normals[i-1]@v[i]+d,normals[i]@v[i]+d]) for i in range(len(v))]
style=REF/'diseno_industrial_v2.py' if REF.exists() else ROOT/'diseno_industrial_v2.py';tree=ast.parse(style.read_text())
sections=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='sections' for t in n.targets))
outer_source=REF/'envolvente_cerrada_referencia.step' if REF.exists() else ROOT/'aerodinamica_A/envolvente_cerrada_referencia.step'
outer=cq.importers.importStep(str(outer_source)).val().Solids()[0]
def inner_loft(offset):
 wires=[]
 for x,w,h in sections:
  yz=[(w,0),(.79*w,.67*h),(.37*w,h),(-.37*w,h),(-.79*w,.67*h),(-w,0),(-.75*w,-.62*h),(-.32*w,-.78*h),(.32*w,-.78*h),(.75*w,-.62*h)]
  # End sections become too small at deep rib offsets: cap offset locally.
  d=min(offset,min(w,h)*.38);v=inset_polygon(yz,d)
  wires.append(cq.Wire.makePolygon([cq.Vector(x,*p) for p in v]+[cq.Vector(x,*v[0])]))
 return cq.Solid.makeLoft(wires,False).intersect(box([-10,0,0],[1334,1000,1000]))
inner=inner_loft(1.0)
outside=inner.cut(outer).Volume(tol=1e-8);CHECKS.append(dict(check='inner_volume_outside_outer_mm3',value=outside));assert outside<1e-3
skin=outer.cut(inner);assert skin.isValid()
upper_box=box([0,0,200.2],[2000,1000,400]);lower_box=box([0,0,-200.2],[2000,1000,400])
positions=[(-200,-76),(-200,76),(200,-76),(200,76)]
port_cuts=[];trim_cuts=[]
for j,(x,y) in enumerate(positions):
 cutter=cyl([x,y,-250],[0,0,1],46.3,500);port_cuts.append(cutter)
 cap=skin.intersect(cyl([x,y,-250],[0,0,1],45.8,500))
 trim=skin.intersect(ring([x,y,-250],[0,0,1],47.4,46.6,500))
 trim_cuts.append(cyl([x,y,-250],[0,0,1],47.4,500))
 for label,half in [('superior',upper_box),('inferior',lower_box)]:
  add(f'compuerta_{j}_{label}_enrasada',cap.intersect(half),'top',True,'closed_cover_opening_kinematics_pending')
  add(f'aro_{j}_{label}_cobre',trim.intersect(half),'copper')
  # An inset bezel between port and accent creates a real parting line.
  bezel=skin.intersect(ring([x,y,-250],[0,0,1],46.55,46.35,500)).intersect(half)
  add(f'junta_{j}_{label}',bezel,'dark')
shell=skin.cut(cq.Compound.makeCompound(trim_cuts))
# Flush nose instrumentation panel and symmetric shoulder cooling-cover patches.
patches=[('panel_sensor_nariz',box([-600,0,80],[95,42,160]),'dark')]
for sign in (-1,1):
 patches.append((f'cubierta_lateral_{sign}',box([405,sign*100,35],[150,58,85]),'dark'))
for name,cut,color in patches:
 panel=shell.intersect(cut);shell=shell.cut(cut)
 add(name,panel,color,True,'flush_cover_equipment_reservation')
# True transverse gaps in the skin, not lines painted on a render.
for x in (-465,470):shell=shell.cut(box([x,0,0],[.55,1000,1000]))
add('carroceria_superior',shell.intersect(upper_box),'top')
add('carroceria_inferior',shell.intersect(lower_box),'shell')

# Reuse actual vane/shaft geometry from the checked 60-mm layout.
src=REF/'reserva_axial_60mm.step' if REF.exists() else ROOT/'empaquetado_axial_A/reserva_axial_60mm.step'
source_parts=[(s.moved(loc),n.split('/')[-1],col) for s,n,loc,col in cq.Assembly.load(str(src))]
template=[]
for s,n,col in source_parts:
 if n.startswith('canal_'):
  template.append((s,n))
  add(n,s,'mechanism' if 'alabe_' in n else ('dark' if 'rotor' in n else 'metal'),False,
      'representative_rotor_motor' if 'base_' in n else 'vane_or_shaft_geometry')
for j,(x,y) in enumerate(positions):
 duct=next(s for s,n,c in source_parts if n==f'camisa_reserva_{j}')
 shafts=[s for s,n in template if n.startswith(f'canal_{j}_') and '_eje_' in n]
 holes=[]
 for shaft in shafts:
  c=np.array(shaft.Center().toTuple());bb=shaft.BoundingBox();axis=np.array([1,0,0]) if bb.xlen>bb.ylen else np.array([0,1,0])
  holes.append(cyl(c-60*axis,axis,1.35,120))
 duct=duct.cut(cq.Compound.makeCompound(holes))
 add(f'conducto_{j}_84mm_con_taladros',duct,'dark',False)
 overlap=max(shaft.intersect(duct).Volume(tol=1e-8) for shaft in shafts)
 CHECKS.append(dict(check='shaft_duct_overlap_mm3',channel=j,value=overlap));assert overlap<1e-4
 # Rounded actuator packaging volumes outside flow, not unselected commercial servos.
 for row,z in enumerate((-39,-21,19,37)):
  sx=x+math.copysign(54,x)
  servo=box([sx,y,z],[12,16,10])
  servo=cq.Workplane(obj=servo).edges().fillet(1.2).val()
  out=servo.cut(outer).Volume(tol=1e-8);assert out<1e-4
  add(f'alojamiento_actuador_{j}_{row}',servo,'metal',False,'actuator_package_motion_transmission_pending')

# Empty axial tube is an installation interface, never depicted as an engine.
axial=ring([-400,0,0],[1,0,0],30,28,800)
assert axial.cut(outer).Volume(tol=1e-8)<1e-4
add('canal_axial_60_exterior_56_interior',axial,'metal',False,'empty_axial_packaging_interface_not_propulsor')
for x in (-350,0,350):add(f'abrazadera_axial_{x}',ring([x-2,0,0],[1,0,0],32.2,30.3,4),'dark',False)
# Inner ribs share the body cross-section, clipped around real channels.
deep=inner_loft(6.)
for x in (-400,-350,0,350,400):
 rib=inner.cut(deep).intersect(box([x,0,0],[2.5,1000,1000]))
 rib=rib.cut(cyl([-700,0,0],[1,0,0],32.5,1400))
 for xx,yy in positions:rib=rib.cut(cyl([xx,yy,-250],[0,0,1],45.2,500))
 add(f'cuaderna_{x}',rib,'metal',False,'support_geometry_not_structural_validation')
# Local support webs join the central interface collars to the lower ribs.
for x in (-350,0,350):
 for sign in (-1,1):
  ray=IntCurvesFace_ShapeIntersector();ray.Load(outer.wrapped,1e-6)
  ray.Perform(gp_Lin(gp_Pnt(x,sign*80,-250),gp_Dir(0,0,1)),0,500)
  assert ray.NbPnt()
  zlower=min(ray.Pnt(j).Z() for j in range(1,ray.NbPnt()+1))
  start=np.array([x,sign*24.,-21.]);end=np.array([x,sign*80.,zlower+3.5])
  direction=end-start
  web=cyl(start,direction/np.linalg.norm(direction),1.7,float(np.linalg.norm(direction)))
  assert web.cut(outer).Volume(tol=1e-8)<1e-4
  add(f'soporte_canal_axial_{x}_{sign}',web,'metal',False,'support_geometry_not_structural_validation')
# Aft interface follows the envelope, with a capped service/exhaust reserve.
aft=outer.intersect(box([634,0,0],[52,1000,1000]))
aftskin=skin.intersect(box([634,0,0],[52,1000,1000]))
add('inserto_terminal',aftskin.cut(cyl([650,0,0],[1,0,0],18,12)),'dark')
nozzle=ring([656,0,0],[1,0,0],17.5,14.5,5)
add('interfaz_posterior_reservada',nozzle,'metal',True,'rear_interface_not_sized_nozzle')
add('tapa_interior_interfaz',cyl([656.1,0,0],[1,0,0],14.4,.5),'dark')

# Flush top mounting fasteners, placed on the real loft by line intersections.
def z_surface(x,y):
 ray=IntCurvesFace_ShapeIntersector();ray.Load(outer.wrapped,1e-6)
 ray.Perform(gp_Lin(gp_Pnt(x,y,-250),gp_Dir(0,0,1)),0,500)
 if not ray.NbPnt():raise ValueError(f'Fastener outside hull {x},{y}')
 return max(ray.Pnt(j).Z() for j in range(1,ray.NbPnt()+1))
fastener_holes=[]
for i,(x,y) in enumerate([(-390,-35),(-390,35),(0,-110),(0,110),(380,-35),(380,35)]):
 z=z_surface(x,y)
 head=cyl([x,y,z-.7],[0,0,1],2.2,.5)
 socket=cq.Workplane('XY').polygon(6,1.8).extrude(.4).translate((x,y,z-.45)).val()
 add(f'vis_encastree_{i}',head.cut(socket),'metal')
 fastener_holes.append(cyl([x,y,z-2],[0,0,1],2.3,3))
# Long narrow copper badges are actual inset patches, flush with the hull.
badge=skin.intersect(box([330,0,110],[82,10,45]))
add('signature_dorsale_cuivre',badge,'copper')
# Remove shared skin volumes from the other panels: no painted duplicates.
skin_pockets=[box([634,0,0],[52,1000,1000]),box([330,0,110],[82,10,45])]+fastener_holes
for p in PARTS:
 if p['name'].startswith('carroceria_'):
  p['shape']=p['shape'].cut(cq.Compound.makeCompound(skin_pockets))
  assert p['shape'].isValid()

def export(mass):
 scale=(mass/5)**(1/3);folder=OUT/f'{mass:g}kg';folder.mkdir(exist_ok=True)
 asm=cq.Assembly(name=f'A03_{mass:g}kg_objectif');cut=cq.Assembly(name=f'A03_{mass:g}kg_coupe')
 manifest=[]
 for p in PARTS:
  s=p['shape'].scale(scale);asm.add(s,name=p['name'],color=cq.Color(*p['color']))
  if p['name']!='carroceria_superior' and not p['name'].startswith(('compuerta_','aro_','junta_','panel_sensor','signature_','vis_')):
   display=s
   if p['name'].startswith(('conducto_0_','conducto_2_')):
    display=display.cut(box([0,-200*scale,100*scale],[2000*scale,248*scale,220*scale]))
   cut.add(display,name=p['name'],color=cq.Color(*p['color']))
  bb=s.BoundingBox();manifest.append(dict(name=p['name'],scope=p['scope'],volume_mm3=s.Volume(tol=1e-7),bbox_mm=[bb.xlen,bb.ylen,bb.zlen],color=p['color'],exterior=p['exterior']))
 filename=folder/'A03_integrado.step';asm.save(str(filename));cut.save(str(folder/'A03_corte.step'))
 reread=list(cq.Assembly.load(str(filename)));assert len(reread)==len(PARTS) and all(s.moved(loc).isValid() for s,n,loc,col in reread)
 silhouette=cq.Compound.makeCompound([p['shape'].scale(scale) for p in PARTS if p['exterior']]);cq.exporters.export(silhouette,str(folder/'A03_exterior.stl'),tolerance=.25,angularTolerance=.12)
 bounds=cq.Compound.makeCompound([p['shape'].scale(scale) for p in PARTS]).BoundingBox()
 (folder/'manifest.json').write_text(json.dumps(dict(target_mass_kg=mass,mass_closed=False,scale=scale,assembly_dimensions_mm=[bounds.xlen,bounds.ylen,bounds.zlen],fan_bore_mm=84*scale,axial_outer_mm=60*scale,parts=manifest,reimported_valid_parts=len(reread)),indent=2))
 print(f'Exported {mass:g}kg {len(reread)} valid parts',flush=True)
for mass in (2,5,10):export(mass)
(OUT/'VERIFICACION.json').write_text(json.dumps(dict(source_layout_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),checks=CHECKS,parts=len(PARTS),shell_method='Two lofts with 1 mm section-plane insets; not a constant normal-thickness offset or structurally validated laminate.',layout='Research proposal: x +/-200, y +/-76 mm, central OD60 mm, 5kg reference',physical_performance_validated=False,remaining=['Cover opening/retraction kinematics','Rotor/motor and axial propulsion sizing','Actuator transmission, bearing/seal detail and tolerances','Full-assembly collision and tolerance audit','Structural sizing and mass/CG closure','Converged installed aerodynamics and flutter']),indent=2))
print('CAD_COMPLETE',flush=True)
