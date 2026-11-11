from pathlib import Path
import cadquery as cq
import numpy as np,json,shutil,csv
OUT=Path(__file__).resolve().parent
BASE=OUT/'base_A04'
if not BASE.exists():
 BASE.mkdir()
 for m in (2,5,10):
  (BASE/f'{m}kg').mkdir()
  for f in ('A04_integrado.step','manifest.json'):shutil.copyfile(OUT.parent/'producto_A04'/f'{m}kg'/f,BASE/f'{m}kg'/f)
parts=[];checks=[]
meta=json.loads((BASE/'5kg/manifest.json').read_text())
lookup={p['name']:p for p in meta['parts']}
for s,n,loc,col in cq.Assembly.load(str(BASE/'5kg/A04_integrado.step')):
 n=n.split('/')[-1];parts.append(dict(name=n,shape=s.moved(loc),**{k:lookup[n][k] for k in ('color','exterior','scope')}))
def box(c,d):return cq.Workplane('XY').box(*d).translate(c).val()
def cy(r,y,h):return cq.Solid.makeCylinder(r,h,cq.Vector(555,y,0),cq.Vector(0,1,0))
def wire(y,poly):return cq.Wire.makePolygon([cq.Vector(x,y,z) for x,z in poly]+[cq.Vector(poly[0][0],y,poly[0][1])])
def section(y,le,te,t):return wire(y,[(le,0),(le+.15*(te-le),t/2),(te-.12*(te-le),t/3),(te,0),(te-.12*(te-le),-t/3),(le+.15*(te-le),-t/2)])
if not (OUT/'envolvente.step').exists():shutil.copyfile(OUT.parent/'producto_A04/referencias/envolvente_cerrada_referencia.step',OUT/'envolvente.step')
outer=cq.importers.importStep(str(OUT/'envolvente.step')).val().Solids()[0]
blade=cq.Solid.makeLoft([section(100,440,595,6),section(135,488,613,4.5),section(170,535,630,3)],True)
hub=cy(5,100,10);blade=blade.fuse(hub).cut(cy(2.8,99,13))
mount=cq.Solid.makeLoft([section(42,430,618,28),section(78,438,612,22),section(98,445,603,12)],True).cut(outer)
actuator=box((555,79,0),(24,22,10));mount=mount.cut(actuator).cut(cy(6,88,11))
bearing=cy(5.8,91,7).cut(cy(2.8,90,10))
shaft=cy(2.5,80,30)
for i,angle in enumerate((45,135,225,315)):
 def rot(s):return s.rotate((0,0,0),(1,0,0),angle)
 for name,s,col,vis,scope in [('aleta_movil',blade,(.065,.068,.075),True,'concept_all_moving_fin'),('carenado_raiz',mount,(.018,.025,.032),True,'mount_fairing_not_structurally_sized'),('eje_control',shaft,(.43,.49,.54),False,'shaft_geometry_not_load_sized'),('cojinete',bearing,(.43,.49,.54),False,'bearing_envelope_not_selected_hardware'),('actuador_reserva',actuator,(.16,.24,.27),False,'direct_drive_actuator_package_unselected')]:
  shape=rot(s);assert shape.isValid() and shape.Volume()>0
  parts.append(dict(name=f'{name}_{i}',shape=shape,color=col,exterior=vis,scope=scope))
 for deg in range(-20,21,5):
  moving=rot(blade.rotate((555,0,0),(555,1,0),deg))
  ov=moving.intersect(rot(mount)).Volume();bodyov=moving.intersect(outer).Volume()
  checks.append(dict(fin=i,angle_deg=deg,fin_mount_overlap_mm3=ov,fin_hull_overlap_mm3=bodyov))
  assert max(ov,bodyov)<1e-4
for mass in (2,5,10):
 scale=(mass/5)**(1/3);folder=OUT/f'{mass}kg';folder.mkdir(exist_ok=True)
 asm=cq.Assembly(name=f'A06_{mass}kg');posed=cq.Assembly(name='A06_controles_15deg');cut=cq.Assembly(name='A06_corte');manifest=[]
 for p in parts:
  s=p['shape'];pose=s
  if p['name'].startswith('aleta_movil_'):
   i=int(p['name'].split('_')[-1]);a=np.deg2rad((45,135,225,315)[i]);pose=s.rotate((555,0,0),(555,float(np.cos(a)),float(np.sin(a))),15 if i%2==0 else -15)
  asm.add(s.scale(scale),name=p['name'],color=cq.Color(*p['color']));posed.add(pose.scale(scale),name=p['name'],color=cq.Color(*p['color']))
  if p['name']!='carroceria_superior' and not p['name'].startswith(('compuerta_','aro_','junta_','panel_sensor','signature_','vis_','sculpture_','epaule_','lame_')):
   shown=s
   if p['name'].startswith(('conducto_0_','conducto_2_')):
    shown=s.cut(box((0,-100,150),(2000,200,300)))
   cut.add(shown.scale(scale),name=p['name'],color=cq.Color(*p['color']))
  manifest.append({k:v for k,v in p.items() if k!='shape'}|dict(volume_mm3=s.Volume()*scale**3))
 for name,a in [('integrado',asm),('controles_15deg',posed),('corte',cut)]:
  dest=folder/f'A06_{name}.step';a.save(str(dest));r=list(cq.Assembly.load(str(dest)));assert all(s.moved(l).isValid() for s,n,l,c in r)
 cq.exporters.export(cq.Compound.makeCompound([p['shape'].scale(scale) for p in parts if p['exterior']]),str(folder/'A06_exterior.stl'),tolerance=.25)
 bb=cq.Compound.makeCompound([p['shape'].scale(scale) for p in parts]).BoundingBox()
 (folder/'manifest.json').write_text(json.dumps(dict(architecture='A_internal_fans_user_confirmed',rotor_deployment=False,target_mass_kg=mass,mass_closed=False,scale=scale,parts=manifest,assembly_dimensions_mm=[bb.xlen,bb.ylen,bb.zlen],valid_parts=len(parts),fin_root_chord_mm=155*scale,fin_tip_chord_mm=95*scale,fin_exposed_span_mm=70*scale),indent=2))
 print('EXPORTED',mass,len(parts),flush=True)
(OUT/'VERIFICACION_ALETAS.json').write_text(json.dumps(dict(checks=checks,physical_performance_validated=False,note='Local geometric screening only: hull and own fairing at sampled angles. Not full tolerance, loads, flutter or actuator validation.'),indent=2))
