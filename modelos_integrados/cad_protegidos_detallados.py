"""Presentation-detail CAD, distinct from validated engineering/manufacturing design.
All geometry mm. Fasteners, guards, motors and mechanisms are representative.
"""
from pathlib import Path
import json,math,hashlib,os
import numpy as np
import cadquery as cq
from crear_modelos import hull
import render_cad as r
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'producto_conceptual_detallado';OUT.mkdir(exist_ok=True);r.MESH=OUT/'mallas';r.MESH.mkdir(exist_ok=True)
T=r.T;mi=r.mi
SILVER=(.43,.51,.57);DARK=(.025,.037,.045);BLUE=(.025,.18,.23);METAL=(.3,.33,.35);COPPER=(.38,.16,.055)
def cylinder(p,n,R,h):return cq.Solid.makeCylinder(R,h,cq.Vector(*(np.array(p)-h/2*np.array(n))),cq.Vector(*n))
def box(p,size):return cq.Workplane('XY').box(*size).translate(tuple(p)).val()
def ring(p,n,R,w,h):return cylinder(p,n,R,h).cut(cylinder(p,n,R-w,h+2))
def tube(a,b,R):
 a=np.array(a);b=np.array(b);v=b-a
 return cylinder((a+b)/2,v/np.linalg.norm(v),R,np.linalg.norm(v))
def torus(p,n,R,minor):return cq.Solid.makeTorus(R,minor,cq.Vector(*p),cq.Vector(*n))
def fastener(p,n):return cylinder(p,n,2.6,3).cut(cylinder(np.array(p)+np.array(n),n,1.1,3))
def append(parts,label,shape,color):parts.append((label,shape,color))
def basis(n):
 n=np.array(n,float);n/=np.linalg.norm(n);u=np.cross(n,[1,0,0]);u/=np.linalg.norm(u);return n,u,np.cross(n,u)
def detailed_fan(parts,p,n,R):
 p=np.array(p,float);n,u,v=basis(n)
 append(parts,'conducto',ring(p,n,R+5,5,48),SILVER)
 for s in [-1,1]:append(parts,'labio_redondeado',torus(p+s*24*n,n,R+2,2.4),METAL)
 append(parts,'camisa_motor',cylinder(p,n,17,27),DARK)
 for zz in [-9,-3,3,9]:append(parts,'banda_motor',ring(p+zz*n,n,17.5,2,1.7),COPPER)
 append(parts,'tapa_motor',cylinder(p+17*n,n,16,5),METAL)
 append(parts,'buje',cylinder(p+21*n,n,12,8),DARK)
 append(parts,'eje',cylinder(p+21*n,n,3,17),METAL)
 blades=[]
 for a in np.arange(6)*np.pi/3:
  radial=np.cos(a)*u+np.sin(a)*v;tangent=np.cross(n,radial);wires=[]
  for rr,chord,pitch,thick in [(18,10,32,2.1),(28,18,26,2.8),(.6*R,20,20,2.5),(.88*R,13,15,1.6),(R-5,4,12,.8)]:
   ang=np.deg2rad(pitch);xd=tangent*np.cos(ang)+n*np.sin(ang)
   plane=cq.Plane(origin=tuple(p+10*n+rr*radial),xDir=tuple(xd),normal=tuple(radial))
   wires.append(cq.Workplane(plane).ellipse(chord/2,thick/2).val())
  blades.append(cq.Solid.makeLoft(wires))
 append(parts,'palas_torsionadas',cq.Compound.makeCompound(blades),DARK)
 for a in np.arange(3)*2*np.pi/3:
  radial=np.cos(a)*u+np.sin(a)*v
  append(parts,'estator_soporte',tube(p-16*n+17*radial,p-16*n+(R-1)*radial,2.5),METAL)
 # protective annular guard with cross ribs, illustrative pressure loss unknown
 append(parts,'aro_rejilla',torus(p+28*n,n,.60*R,1.1),METAL)
 for a in np.arange(3)*np.pi/3:
  radial=np.cos(a)*u+np.sin(a)*v
  append(parts,'barra_rejilla',tube(p+28*n-(R-1)*radial,p+28*n+(R-1)*radial,1.1),METAL)
 for a in np.arange(8)*np.pi/4:
  append(parts,'tornillo_conducto',fastener(p+26*n+(R+1)*(np.cos(a)*u+np.sin(a)*v),n),METAL)
def body_details(parts):
 # circumferential seam, conformal access panel, flush-panel fasteners
 append(parts,'junta_central',ring([0,0,0],[1,0,0],210.6,1.8,1.4),DARK)
 patch=hull(1.402,.422).cut(hull(1.400,.420)).intersect(box([0,0,200],[210,110,100]))
 append(parts,'panel_acceso',patch,BLUE)
 for x in [-90,90]:
  for y in [-42,42]:
   z=210*np.sqrt(max(0,1-(x/700)**2-(y/210)**2));append(parts,'tornillo_panel',fastener([x,y,z+2],[0,0,1]),METAL)
def export(name,parts,title,subtitle):
 ass=cq.Assembly(name=name);validation=[]
 for j,(label,sh,color) in enumerate(parts):
  valid=sh.isValid();assert valid,(name,label);validation.append(valid);ass.add(sh,name=f'{label}_{j:03d}',color=cq.Color(*color))
 step=OUT/(name+'.step');ass.save(str(step))
 # Group CAD parts by material; retain individual parts in STEP.
 groups={}
 for label,sh,color in parts:
  if label=='carcasa':
   sh=max(sh.Faces(),key=lambda f:f.BoundingBox().xlen)
  elif label=='panel_acceso':
   sh=max(sh.Faces(),key=lambda f:f.Area())
  groups.setdefault(color,[]).append(sh)
 meshes=[]
 for j,(color,shapes) in enumerate(groups.items()):
  cache=r.MESH/(name+str(j)+'.ply')
  if os.environ.get('CAD_REUSE_MESH')=='1' and cache.exists():
   meshes.append((str(cache),color))
  else:
   sh=cq.Compound.makeCompound(shapes);vs,fs=sh.tessellate(.3,.15);meshes.append((r.ply(name+str(j),np.array([v.toTuple() for v in vs])/1000,fs),color))
 scene={'type':'scene','integrator':{'type':'path','max_depth':6},'sensor':{'type':'perspective','fov':34,'to_world':T.look_at(origin=[-1.95,-2.6,1.85],target=[0,0,0],up=[0,0,1]),'sampler':{'type':'independent'},'film':{'type':'hdrfilm','width':2000,'height':1350,'rfilter':{'type':'tent'}}},'env':{'type':'constant','radiance':{'type':'rgb','value':[.2,.23,.28]}},'floor':{'type':'rectangle','to_world':T.translate([0,0,-.36]).scale([100,100,1]),'bsdf':r.mat([.055,.075,.095],.55)}}
 for j,(path,color) in enumerate(meshes):scene[f'part{j}']={'type':'ply','filename':path,'bsdf':{'type':'twosided','bsdf':r.mat(color,.19 if color==SILVER else .28)}}
 for key,pos,power,size in [('key',[-1,-1,4],11,1.4),('rim',[1,2,3.5],14,1.1),('fill',[-2,2,2],5,.7)]:scene[key]={'type':'rectangle','to_world':T.look_at(origin=pos,target=[0,0,0],up=[0,0,1]).scale([size,size,1]),'emitter':{'type':'area','radiance':{'type':'rgb','value':[power]*3}}}
 print('Renderizando',name,len(parts),'piezas',flush=True)
 im=mi.render(mi.load_dict(scene),spp=int(os.environ.get("CAD_RENDER_SPP","64")),seed=92);png=OUT/(name+'.png');mi.util.write_bitmap(str(png),im,write_async=False)
 image=Image.open(png).convert('RGB');draw=ImageDraw.Draw(image);draw.text((60,45),title,font=r.font(43),fill=(233,241,247));draw.text((60,105),subtitle,font=r.font(25),fill=(162,199,214));draw.text((60,1255),'CAD DE PRESENTACIÓN · ARQUITECTURA CONCEPTUAL',font=r.font(24),fill=(200,218,229));draw.text((60,1295),'L 1,40 m · D 0,42 m · Detalles representativos; dimensionamiento funcional pendiente',font=r.font(21),fill=(155,182,199));image.save(png)
 return dict(file=step.name,parts=len(parts),valid_parts=all(validation),sha256=hashlib.sha256(step.read_bytes()).hexdigest())
outer=hull(1.4,.42);shell=outer.cut(hull(1.4,.42,.003));results=[]
# A: actual open shell, caps hinged to side of openings rather than floating disks.
parts=[];body=shell
for x in [-300,300]:
 radius=210*np.sqrt(1-(x/700)**2)
 for j in range(4):
  n=np.array([0,np.cos(j*np.pi/2),np.sin(j*np.pi/2)]);u=np.array([1.,0,0]);v=np.cross(n,u);center=np.array([x,0,0])+radius*n
  body=body.cut(cylinder(np.array([x,0,0])+190*n,n,75,190))
  detailed_fan(parts,np.array([x,0,0])+130*n,n,65)
  hinge=center+76*v;capcenter=hinge+76*n
  append(parts,'compuerta_abatida',cylinder(capcenter,v,74,4),BLUE)
  append(parts,'junta_compuerta',torus(capcenter+3*v,v,70,1.2),DARK)
  for dx in [-32,32]:
   hp=hinge+dx*u;append(parts,'bisagra',ring(hp,u,6.5,2,18),METAL);append(parts,'pasador',cylinder(hp,u,2.5,23),METAL)
  append(parts,'nervio_compuerta',tube(hinge,capcenter,3),METAL)
append(parts,'carcasa',body,SILVER);body_details(parts)
results.append(export('A_internos_detallado',parts,'A / Integración interna','Conductos internos · rejillas · compuertas abiertas y bisagras representativas'))
# B: stowed and deployed endpoints; telescoping sleeves and latches.
for deployed in [False,True]:
 parts=[];body=shell
 for x in [-300,300]:
  for side in [-1,1]:
   body=body.cut(box([x,side*185,0],[210,180,180]));y=side*(340 if deployed else 90)
   detailed_fan(parts,[x,y,0],[0,0,1],80)
   if deployed:
    for dx in [-52,52]:
     sleeve=box([x+dx,side*175,-42],[22,130,22]).cut(box([x+dx,side*175,-42],[15,132,15]));append(parts,'manga_guia',sleeve,METAL)
     append(parts,'guia_interior',box([x+dx,side*280,-42],[13,180,13]),DARK)
    append(parts,'carro',box([x,y,-42],[135,40,12]),METAL)
   capy=side*(430 if deployed else 191)
   append(parts,'tapa_casete',box([x,capy,0],[205,5,175]),BLUE)
   for dx in [-88,88]:
    for zz in [-72,72]:append(parts,'fijacion_tapa',fastener([x+dx,capy+side*4,zz],[0,side,0]),METAL)
   for zz in [-50,50]:append(parts,'cierre_representativo',box([x,capy+side*5,zz],[25,5,9]),DARK)
 append(parts,'carcasa',body,SILVER);body_details(parts)
 results.append(export('B_retractil_'+('desplegado_detallado' if deployed else 'guardado_detallado'),parts,'B / Casetes retráctiles',('Desplegados' if deployed else 'Guardados')+' · guías telescópicas · tapas y cierres representativos'))
# C: protected external pods, short faired attachment blocks and bolts.
parts=[('carcasa',shell,SILVER)];body_details(parts)
for x in [-300,300]:
 for side in [-1,1]:
  detailed_fan(parts,[x,side*230,0],[0,0,1],90)
  support=box([x,side*180,-14],[135,105,28]);support=cq.Workplane(obj=support).edges('|Z').fillet(10).val();append(parts,'sujecion_corta',support,BLUE)
  for dx in [-48,48]:
   for yy in [150,205]:append(parts,'tornillo_sujecion',fastener([x+dx,side*yy,2],[0,0,1]),METAL)
results.append(export('C_conductos_detallado',parts,'C / Conductos integrados al exterior','Labios redondeados · rejillas · soportes cortos y fijaciones'))
(OUT/'manifest.json').write_text(json.dumps(results,indent=2))
names=['A_internos_detallado','B_retractil_guardado_detallado','B_retractil_desplegado_detallado','C_conductos_detallado'];board=Image.new('RGB',(2800,1890))
for j,name in enumerate(names):board.paste(Image.open(OUT/(name+'.png')).resize((1400,945)),((j%2)*1400,(j//2)*945))
board.save(OUT/'comparacion_detallada.png');print('FINALIZADO',flush=True)
