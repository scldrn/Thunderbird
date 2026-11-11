"""Industrial styling CAD study. Packaging/aerodynamics not validated."""
from pathlib import Path
import json,math
import numpy as np
import cadquery as cq
import render_cad as r
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'diseno_industrial_v2';OUT.mkdir(exist_ok=True);r.MESH=OUT/'mallas';r.MESH.mkdir(exist_ok=True)
mi=r.mi;T=r.T
GRAPH=(.025,.035,.045);TOP=(.05,.065,.075);BLACK=(.012,.02,.026);METAL=(.27,.32,.34);ACCENT=(.55,.19,.065)
parts=[]
def add(name,s,col):assert s.isValid(),name;parts.append((name,s,col))
def box(p,d):return cq.Workplane('XY').box(*d).translate(tuple(p)).val()
def cyl(p,n,R,h):return cq.Solid.makeCylinder(R,h,cq.Vector(*(np.array(p)-np.array(n)*h/2)),cq.Vector(*n))
def ring(p,n,R,w,h):return cyl(p,n,R,h).cut(cyl(p,n,R-w,h+2))
def beam(a,b,R):
 a=np.array(a);b=np.array(b);v=b-a;return cyl((a+b)/2,v/np.linalg.norm(v),R,np.linalg.norm(v))
# Faceted, swept cross sections: lower shoulder and defined dorsal planes.
sections=[(-680,7,6),(-580,58,36),(-400,127,80),(-140,160,107),(160,150,103),(400,112,78),(570,63,47),(660,25,25)]
wires=[]
for x,w,h in sections:
 yz=[(w,0),(.79*w,.67*h),(.37*w,h),(-.37*w,h),(-.79*w,.67*h),(-w,0),(-.75*w,-.62*h),(-.32*w,-.78*h),(.32*w,-.78*h),(.75*w,-.62*h)]
 wires.append(cq.Wire.makePolygon([cq.Vector(x,y,z) for y,z in yz]+[cq.Vector(x,*yz[0])]))
body=cq.Solid.makeLoft(wires,ruled=False)
# Recessed fan ports rather than raised cylindrical appendages.
for xx in [-280,285]:
 for yy in [-65,65]:body=body.cut(cyl([xx,yy,100],[0,0,1],45,130))
# Real gaps between panel-envelope solids; no coincident painted faces.
upper=body.intersect(box([0,0,160],[1600,700,180]));lower=body.cut(box([0,0,160.3],[1600,700,180]))
for name,shape,col in [('cubierta_superior',upper,TOP),('cuerpo_principal',lower,GRAPH)]:
 shape=shape.cut(box([-65,0,0],[1.2,700,500]));add(name,shape,col)
for xx in [-280,285]:
 for yy in [-65,65]:
  p=np.array([xx,yy,58.]);n=np.array([0,0,1])
  add('camisa_interna',ring(p,n,44,3,30),BLACK);add('motor',cyl(p,n,12,20),METAL)
  blades=[]
  for a in np.arange(7)*2*np.pi/7:
   rr=np.array([np.cos(a),np.sin(a),0]);tt=np.cross(n,rr)
   pts=[p+8*n+12*rr-3*tt,p+8*n+40*rr-5*tt,p+8*n+41*rr+1*tt,p+8*n+14*rr+5*tt]
   w=cq.Wire.makePolygon([cq.Vector(*v) for v in pts]+[cq.Vector(*pts[0])]);blades.append(cq.Solid.extrudeLinear(w,[],cq.Vector(0,0,1.5)))
  add('rotor_representativo',cq.Compound.makeCompound(blades),BLACK)
  add('aro_rejilla',cq.Solid.makeTorus(28,1.0,cq.Vector(xx,yy,73),cq.Vector(0,0,1)),METAL)
  for a in [0,np.pi/3,2*np.pi/3]:
   rr=np.array([np.cos(a),np.sin(a),0]);add('rejilla',beam(np.array([xx,yy,73])-42*rr,np.array([xx,yy,73])+42*rr,.9),METAL)
# Dorsal recessed insert and longitudinal accent, separate solids.
insert=box([90,0,105],[235,35,3]);add('inserto_dorsal',insert,BLACK)
for side in [-1,1]:
 # Close-fitted segmented shoulder accent; visual styling, not a control surface.
 for xx,yy,zz,length in [(-180,149,37,95),(-30,154,38,95),(120,146,37,95)]:
  add('acento_hombro',box([xx,side*yy,zz],[length,2.5,3.5]),ACCENT)
 # Recessed-looking side cooling-slot inserts; no thermal performance implied.
 for j in range(5):
  sh=box([390+j*15,side*(105-j*4),8],[5,2.5,32]).rotate((390+j*15,side*(105-j*4),8),(390+j*15+1,side*(105-j*4),8),side*22)
  add('lamela_lateral',sh,BLACK)
# Compact flush rear interface/port, no exposed propellers or arms.
add('interfaz_trasera',ring([661,0,0],[1,0,0],20,4,8),METAL)
add('fondo_interfaz',cyl([660,0,0],[1,0,0],16,2),BLACK)
for xx in [-120,200]:
 for yy in [-30,30]:add('fijacion_enrasada',ring([xx,yy,108],[0,0,1],2.2,1.1,1.2),METAL)
ass=cq.Assembly(name='diseno_industrial_v2')
for j,(name,s,col) in enumerate(parts):ass.add(s,name=f'{name}_{j}',color=cq.Color(*col))
step=OUT/'diseno_industrial_v2.step';ass.save(str(step))
groups={}
for name,s,col in parts:groups.setdefault(col,[]).append(s)
meshes=[]
for j,(col,shapes) in enumerate(groups.items()):
 vs,fs=cq.Compound.makeCompound(shapes).tessellate(.25,.12);path=r.ply('material'+str(j),np.array([v.toTuple() for v in vs])/1000,fs);meshes.append((path,col))
for view,origin in [('hero',[-1.95,-2.35,1.9]),('posterior',[1.95,-2.35,1.65])]:
 scene={'type':'scene','integrator':{'type':'path','max_depth':5},'sensor':{'type':'perspective','fov':31,'to_world':T.look_at(origin=origin,target=[0,0,0],up=[0,0,1]),'sampler':{'type':'independent'},'film':{'type':'hdrfilm','width':2000,'height':1250,'rfilter':{'type':'tent'}}},'env':{'type':'constant','radiance':{'type':'rgb','value':[.16,.19,.23]}},'floor':{'type':'rectangle','to_world':T.translate([0,0,-.15]).scale([100,100,1]),'bsdf':r.mat([.025,.035,.045],.5)}}
 for j,(path,col) in enumerate(meshes):scene[f'p{j}']={'type':'ply','filename':path,'bsdf':{'type':'twosided','bsdf':r.mat(col,.2 if col!=BLACK else .38)}}
 for key,pos,power,size in [('key',[-1,-1,4],8,1.6),('rim',[1.5,2,3],12,1.2),('fill',[-2,2,2],5,1)]:scene[key]={'type':'rectangle','to_world':T.look_at(origin=pos,target=[0,0,0],up=[0,0,1]).scale([size,size,1]),'emitter':{'type':'area','radiance':{'type':'rgb','value':[power]*3}}}
 print('Render',view,flush=True);image=mi.render(mi.load_dict(scene),spp=64,seed=14);png=OUT/(view+'.png');mi.util.write_bitmap(str(png),image,write_async=False)
 im=Image.open(png).convert('RGB');draw=ImageDraw.Draw(im);draw.text((65,55),'ESTUDIO DE DISEÑO / 02',font=r.font(30),fill=(183,201,214));draw.text((65,100),'Integración compacta',font=r.font(52),fill=(233,240,245));draw.text((65,1185),'CAD CONCEPTUAL · CARROCERÍA Y ALOJAMIENTO PENDIENTES DE VALIDACIÓN',font=r.font(20),fill=(154,176,193));im.save(png)
(OUT/'LEEME.md').write_text('''# Diseño industrial 02\n\nRediseño estético de la arquitectura con ventiladores internos. CAD conceptual de envolvente exterior y componentes representativos. No conserva geometría ni resultados físicos del modelo anterior. Longitud nominal 1340 mm, anchura máxima aproximada 320 mm; el loft puede exceder las cotas de sección. No se ha cerrado espesor de pared, masa, control omnidireccional, capacidad propulsiva, refrigeración ni régimen transónico. Los cuatro rotores ilustran alojamiento, no una selección funcional. Los insertos laterales y dorsal son de estilo y requieren integración real.\n\nSTEP editable y dos renders trazados desde el CAD. No se ha usado generación de imágenes por IA.\n''')
print('DONE',flush=True)
