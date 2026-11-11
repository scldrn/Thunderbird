"""Comparative CAD packaging concepts in mm, not validated propulsion hardware."""
from pathlib import Path
import json,math
import numpy as np
import cadquery as cq
from crear_modelos import hull
import render_cad as render
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent/'arquitecturas_protegidas';OUT.mkdir(exist_ok=True)
render.MESH=OUT/'mallas';render.MESH.mkdir(exist_ok=True)
mi=render.mi;T=mi.ScalarTransform4f
L=1.4;D=.42
outer=hull(L,D);inner=hull(L,D,.003);shell=outer.cut(inner)
SILVER=(.48,.56,.63);DARK=(.035,.05,.065);BLUE=(.04,.22,.30);ORANGE=(.65,.3,.07)
def cyl(p,n,r,h):return cq.Solid.makeCylinder(r,h,cq.Vector(*(np.array(p)-np.array(n)*h/2)),cq.Vector(*n))
def box(p,d):return cq.Workplane('XY').box(*d).translate(tuple(p)).val()
def fan(p,n,R):
 p=np.array(p,float);n=np.array(n,float);n/=np.linalg.norm(n);u=np.cross(n,[1,0,0]);u/=np.linalg.norm(u);v=np.cross(n,u)
 ring=cyl(p,n,R+5,48).cut(cyl(p,n,R,52));motor=cyl(p,n,17,30)
 blades=[]
 for a in np.arange(6)*np.pi/3:
  r=math.cos(a)*u+math.sin(a)*v;side=np.cross(n,r)
  pts=[p+18*r-6*side,p+(R-4)*r-10*side,p+(R-4)*r+6*side,p+18*r+6*side]
  wire=cq.Wire.makePolygon([cq.Vector(*q) for q in pts]+[cq.Vector(*pts[0])]);blades.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(*(n*2))))
 return [('conducto',ring,SILVER),('motor',motor,DARK),('palas',cq.Compound.makeCompound(blades),DARK)]
def export(name,parts,title,subtitle):
 a=cq.Assembly(name=name)
 for j,(label,sh,color) in enumerate(parts):
  assert sh.isValid(),(name,label)
  a.add(sh,name=f'{label}_{j}',color=cq.Color(*color))
 a.save(str(OUT/(name+'.step')))
 meshes=[]
 for j,(label,sh,color) in enumerate(parts):
  vs,fs=sh.tessellate(.5,.18);path=render.ply(name+str(j),np.array([v.toTuple() for v in vs])/1000,fs);meshes.append((path,color))
 scene={'type':'scene','integrator':{'type':'path','max_depth':5},'sensor':{'type':'perspective','fov':34,'to_world':T.look_at(origin=[-2.1,-2.8,2.1],target=[0,0,0],up=[0,0,1]),'sampler':{'type':'independent'},'film':{'type':'hdrfilm','width':1500,'height':1000,'rfilter':{'type':'tent'}}},'env':{'type':'constant','radiance':{'type':'rgb','value':[.24,.27,.32]}},'floor':{'type':'rectangle','to_world':T.translate([0,0,-.35]).scale([100,100,1]),'bsdf':render.mat([.09,.115,.14],.6)}}
 for j,(path,color) in enumerate(meshes):scene[f'p{j}']={'type':'ply','filename':path,'bsdf':render.mat(color,.23)}
 for key,pos,power,size in [('key',[-1,-1,4],9,1.3),('rim',[1,2,3],11,1)]:scene[key]={'type':'rectangle','to_world':T.look_at(origin=pos,target=[0,0,0],up=[0,0,1]).scale([size,size,1]),'emitter':{'type':'area','radiance':{'type':'rgb','value':[power]*3}}}
 print('Render',name,flush=True);im=mi.render(mi.load_dict(scene),spp=48,seed=71);png=OUT/(name+'.png');mi.util.write_bitmap(str(png),im,write_async=False)
 image=Image.open(png).convert('RGB');draw=ImageDraw.Draw(image);draw.text((45,35),title,font=render.font(36),fill=(235,242,246));draw.text((45,85),subtitle,font=render.font(22),fill=(170,203,218));draw.text((45,935),'CAD CONCEPTUAL · L 1,40 m · D 0,42 m · SIN VALIDACIÓN DE VUELO',font=render.font(19),fill=(185,205,218));image.save(png)
 return name
# A: eight radial internal fan stations, actual shell openings, open cover placeholders.
ports=[];parts=[];cutters=[]
for xx in [-300,300]:
 for j in range(4):
  ang=j*np.pi/2;n=np.array([0,np.cos(ang),np.sin(ang)]);p=np.array([xx,0,0])+130*n
  cutters.append(cyl(np.array([xx,0,0])+190*n,n,75,180))
  parts.extend(fan(p,n,65))
  # Raised cover leaf shown clear of flow; hinge/drive not designed.
  cap=cyl(np.array([xx,0,0])+260*n,n,74,4);parts.append(('compuerta_abierta',cap,BLUE))
opened=shell
for c in cutters:opened=opened.cut(c)
# Remove upper front quadrant for inspection; this is a display section, not a flight shape.
section=box([0,-250,250],[1500,500,500])
parts.insert(0,('carcasa_seccionada',opened.cut(section),SILVER))
export('A_internos_seccion',parts,'A / Ventiladores internos','Corte de inspección · 8 módulos Ø130 mm · compuertas abiertas esquemáticas')
# B: four enclosed cassettes stow inside body and translate on short lateral rails.
for deployed in [False,True]:
 parts=[];body=shell
 for xx in [-300,300]:
  for side in [-1,1]:
   # display storage bay cut; actuator/cinematic load closure remains pending
   body=body.cut(box([xx,side*185,0],[210,180,180]))
   p=[xx,side*(340 if deployed else 90),0]
   parts.extend(fan(p,[0,0,1],80))
   if deployed:parts.append(('guia_telescopica',box([xx,side*220,-38],[35,270,20]),DARK))
   parts.append(('tapa_casete',box([xx,side*(430 if deployed else 191),0],[205,5,175]),BLUE))
 parts.insert(0,('carcasa',body,SILVER))
 export('B_retractiles_'+('desplegado' if deployed else 'guardado'),parts,'B / Módulos retráctiles',('Desplegados' if deployed else 'Guardados')+' · 4 casetes Ø160 mm · recorrido conceptual, sin cinemática validada')
# C: four short conformal duct pods attached without long arms.
parts=[('carcasa',shell,SILVER)]
for xx in [-300,300]:
 for side in [-1,1]:
  p=[xx,side*230,0];parts.extend(fan(p,[0,0,1],90));parts.append(('union_corta',box([xx,side*185,0],[160,100,38]),SILVER))
export('C_conductos_exteriores',parts,'C / Conductos exteriores','4 módulos Ø180 mm · unión corta al fuselaje · protección periférica')
# Contact sheet same camera and scale; no CAD solids are altered by image layout.
names=['A_internos_seccion','B_retractiles_guardado','B_retractiles_desplegado','C_conductos_exteriores']
board=Image.new('RGB',(2400,1600))
for k,name in enumerate(names):board.paste(Image.open(OUT/(name+'.png')).resize((1200,800)),((k%2)*1200,(k//2)*800))
board.save(OUT/'comparacion_arquitecturas.png')
(OUT/'dimensiones.json').write_text(json.dumps(dict(units='STEP mm',body_length_mm=1400,body_diameter_mm=420,internal=dict(rotors=8,diameter_mm=130),retractable=dict(rotors=4,diameter_mm=160,stored_center_abs_y_mm=90,deployed_center_abs_y_mm=340),external=dict(rotors=4,diameter_mm=180),status='Packaging concepts. No claim of six-axis controllability, thrust, aerodynamic drag, mass closure, thermal or structural validation. Retractable endpoint states do not verify continuous mechanism path.'),indent=2))
print('DONE',OUT,flush=True)
