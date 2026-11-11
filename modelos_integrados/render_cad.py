"""Render CPU desde STEP; palas esquemáticas solo para presentación."""
from pathlib import Path
import json,os
import numpy as np
import cadquery as cq
import mitsuba as mi
from PIL import Image,ImageDraw,ImageFont
mi.set_variant('scalar_rgb')
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'renders';OUT.mkdir(exist_ok=True);MESH=OUT/'mallas';MESH.mkdir(exist_ok=True)
DATA=ROOT/os.environ.get('AERO_RENDER_VARIANT','salida')
T=mi.ScalarTransform4f

def ply(name,v,f):
 p=MESH/(name+'.ply')
 with p.open('w') as o:
  o.write(f'ply\nformat ascii 1.0\nelement vertex {len(v)}\nproperty float x\nproperty float y\nproperty float z\nelement face {len(f)}\nproperty list uchar int vertex_indices\nend_header\n')
  for row in v:o.write(' '.join(map(str,row))+'\n')
  for row in f:o.write('3 '+' '.join(map(str,row))+'\n')
 return str(p)
def mat(color,rough=.3):return {'type':'roughplastic','diffuse_reflectance':{'type':'rgb','value':color},'alpha':rough,'int_ior':1.5}
def meshes(m):
 a=cq.Assembly.load(str(DATA/f'{m}kg'/'integracion_desplegada.step'));items=[]
 for shape,name,loc,col in a:
  name=name.split('/')[-1]
  if name.startswith(('barrido','reserva')):continue
  shape=shape.moved(loc);vs,fs=shape.tessellate(.18,.12)
  v=np.array([p.toTuple() for p in vs])/1000
  color=(.52,.59,.65) if name.startswith(('carcasa','ala','cola')) else (.035,.045,.055)
  if name.startswith('bateria'):color=(.025,.16,.24)
  if name.startswith('combustible'):color=(.5,.28,.035)
  items.append((name,ply(f'{m}_{name}',v,fs),color))
 cfg=json.loads((DATA/f'{m}kg'/'configuracion.json').read_text())
 for j,(p,n) in enumerate(zip(cfg['rotor_centers_m'],cfg['rotor_axes'])):
  p=np.array(p);n=np.array(n);u=np.cross(n,[1,0,0]);u/=np.linalg.norm(u);w=np.cross(n,u);R=cfg['rotor_diameter_m']/2
  scale=(m/5)**(1/3);root=p.copy();root[1:]*=(cfg['D_m']/2*np.sqrt(1-(p[0]/(cfg['L_m']/2))**2))/np.linalg.norm(p[1:]);mount=p+np.sign(np.dot(root-p,n))*.065*scale*n
  shaft=cq.Solid.makeCylinder(.004*scale*1000,float(np.linalg.norm(p-mount))*1000,cq.Vector(*(mount*1000)),cq.Vector(*((p-mount)/np.linalg.norm(p-mount))))
  hub=cq.Solid.makeCylinder(.018*scale*1000,.012*scale*1000,cq.Vector(*((p-.006*scale*n)*1000)),cq.Vector(*n))
  for label,sh in [('eje',shaft),('buje',hub)]:
   vv,ff=sh.tessellate(.15,.15);items.append((f'{label}_visual_{j}',ply(f'{m}_{label}_{j}',np.array([v.toTuple() for v in vv])/1000,ff),(.13,.17,.20)))
  # display-only symmetric tapered blade silhouette, within existing swept disk
  for k,sign in enumerate([-1,1]):
   profile=np.array([[.07,-.025],[.22,-.06],[.82,-.045],[.98,-.012],[.98,.012],[.82,.045],[.22,.06],[.07,.025]])*R
   vs=[]
   for dz in [-.0015,.0015]:
    vs.extend([p+sign*x*u+y*w+dz*n for x,y in profile])
   fs=[]
   for i in range(1,7):fs.extend([(0,i+1,i),(8,8+i,8+i+1)])
   for i in range(8):q=(i+1)%8;fs.extend([(i,q,8+q),(i,8+q,8+i)])
   items.append((f'pala_visual_{j}_{k}',ply(f'{m}_pala_{j}_{k}',vs,fs),(.025,.035,.045)))
 return items

def scene(items,m,interior=False):
 s={'type':'scene','integrator':{'type':'path','max_depth':6},'sensor':{'type':'perspective','fov':36,'to_world':T.look_at(origin=[-2.4,-3.3,1.9],target=[0,0,0],up=[0,0,1]),'sampler':{'type':'independent','sample_count':64},'film':{'type':'hdrfilm','width':2200,'height':1400,'rfilter':{'type':'tent'}}},'env':{'type':'constant','radiance':{'type':'rgb','value':[.22,.25,.3]}}}
 for i,(name,path,color) in enumerate(items):
  if interior and name.startswith('carcasa'):continue
  s[f'part{i}']={'type':'ply','filename':path,'bsdf':mat(color,.18 if name.startswith('carcasa') else .3)}
 s['floor']={'type':'rectangle','to_world':T.translate([0,0,-.69]).scale([200,200,1]),'bsdf':mat([.09,.115,.14],.55)}
 for key,position,power,size in [('key',[-1,-1,4],7,1.3),('rim',[1.4,1.8,3.5],9,1.0),('fill',[-3,1,3],5,.8)]:
  s[key]={'type':'rectangle','to_world':T.look_at(origin=position,target=[0,0,0],up=[0,0,1]).scale([size,size,1]),'emitter':{'type':'area','radiance':{'type':'rgb','value':[power,power,power]}}}
 return mi.load_dict(s)

def font(size):
 for path in ['/System/Library/Fonts/Supplemental/Arial.ttf','/System/Library/Fonts/Helvetica.ttc']:
  if Path(path).exists():return ImageFont.truetype(path,size)
 return ImageFont.load_default()
def label(path,m,interior):
 im=Image.open(path).convert('RGB');w,h=im.size;d=ImageDraw.Draw(im)
 d.text((85,65),'PLATAFORMA OMNIDIRECCIONAL',font=font(34),fill=(160,193,208))
 d.text((82,115),f'Concepto {m:02d} / '+('Integración interior' if interior else 'Configuración desplegada'),font=font(57),fill=(238,243,246))
 d.text((85,h-110),'RENDER CAD · DISEÑO EN DESARROLLO',font=font(27),fill=(220,232,239))
 d.text((85,h-65),'Masas objetivo. Palas y bujes ilustrativos; integración mecánica pendiente de validación.',font=font(22),fill=(175,194,207))
 im.save(path)

if __name__=='__main__':
 for m in [5,10]:
  items=meshes(m)
  for interior in ([False] if m==5 else [False,True]):
   p=OUT/f'render_CAD_{m}kg_{"interior" if interior else "exterior"}.png'
   print('Rendering',p,flush=True)
   image=mi.render(scene(items,m,interior),spp=256,seed=27)
   mi.util.write_bitmap(str(p),image,write_async=False);label(p,m,interior);print('Saved',p,flush=True)
