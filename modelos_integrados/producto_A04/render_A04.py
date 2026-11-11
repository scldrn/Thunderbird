"""Studio path-traced render directly from the exported coloured STEP."""
from pathlib import Path
import argparse,json,hashlib,os,math
os.environ.setdefault('DRJIT_CACHE_DIR','/private/tmp/A04_drjit_cache')
import numpy as np
import cadquery as cq
import mitsuba as mi
from PIL import Image,ImageDraw,ImageFont
mi.set_variant('scalar_rgb');T=mi.ScalarTransform4f
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--view',choices=['hero','posterior','interior'],default='hero');p.add_argument('--mass',type=int,default=5);p.add_argument('--width',type=int,default=1800);p.add_argument('--spp',type=int,default=32);a=p.parse_args()
folder=ROOT/f'{a.mass}kg';manifest=json.loads((folder/'manifest.json').read_text());meta={v['name']:v for v in manifest['parts']}
source=folder/('A04_corte.step' if a.view=='interior' else 'A04_integrado.step')
cache=ROOT/'render_meshes'/f'{a.mass}kg_{a.view}';cache.mkdir(parents=True,exist_ok=True)
groups={}
for s,name,loc,color in cq.Assembly.load(str(source)):
 name=name.split('/')[-1]
 if a.view!='interior' and not meta[name]['exterior']:continue
 rgb=tuple(meta[name]['color']);groups.setdefault(rgb,[]).append(s.moved(loc))
def ply(path,shape):
 vv,ff=shape.tessellate(.22,angularTolerance=.10);v=np.array([p.toTuple() for p in vv])/1000;f=np.asarray(ff)
 with path.open('w') as out:
  out.write(f'ply\nformat ascii 1.0\nelement vertex {len(v)}\nproperty float x\nproperty float y\nproperty float z\nelement face {len(f)}\nproperty list uchar int vertex_indices\nend_header\n')
  for row in v:out.write(' '.join(map(str,row))+'\n')
  for row in f:out.write('3 '+' '.join(map(str,row))+'\n')
def plastic(rgb,alpha):
 rgb=np.asarray(rgb);linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
 return {'type':'roughplastic','diffuse_reflectance':{'type':'rgb','value':linear.tolist()},'alpha':alpha,'int_ior':1.5}
s=manifest['scale'];height=round(a.width*.625)
origins={'hero':[-.90,-2.25,2.00],'posterior':[1.80,-2.25,1.35],'interior':[-1.20,-2.05,1.70]}
scene={'type':'scene','integrator':{'type':'path','max_depth':5},'sensor':{'type':'perspective','fov':31,'to_world':T.look_at(origin=np.array(origins[a.view])*s,target=[0,0,.005*s],up=[0,0,1]),'sampler':{'type':'ldsampler'},'film':{'type':'hdrfilm','width':a.width,'height':height,'rfilter':{'type':'tent'}}},'env':{'type':'constant','radiance':{'type':'rgb','value':[.075,.085,.1]}},'floor':{'type':'rectangle','to_world':T.translate([0,0,-.12*s]).scale([50,50,1]),'bsdf':plastic([.035,.045,.057],.55)}}
for i,(rgb,parts) in enumerate(groups.items()):
 path=cache/f'{i}.ply';ply(path,cq.Compound.makeCompound(parts))
 if rgb[0]>.6:bsdf={'type':'roughconductor','material':'Cu','alpha':.20}
 elif rgb[0]>.4:bsdf={'type':'roughconductor','material':'Al','alpha':.28}
 else:bsdf=plastic(rgb,.12 if rgb[0]>.04 else .055)
 scene[f'group{i}']={'type':'ply','filename':str(path),'bsdf':{'type':'twosided','bsdf':bsdf}}
for name,position,power,size in [('key',[-1.0,-1.7,3.0],2.1,1.8),('rim',[1.0,1.7,2.1],4.0,1.35),('fill',[-2.0,1.0,1.3],1.5,1.2)]:
 scene[name]={'type':'rectangle','to_world':T.look_at(origin=np.asarray(position)*s,target=[0,0,0],up=[0,0,1]).scale([size*s,size*s,1]),'emitter':{'type':'area','radiance':{'type':'rgb','value':[power]*3}}}
out=ROOT/f'A04_{a.mass}kg_{a.view}.png';print('RENDER_START',a.view,flush=True)
effective_spp=4**math.ceil(math.log(max(1,a.spp),4))
pixels=mi.render(mi.load_dict(scene),spp=effective_spp,seed=103);mi.util.write_bitmap(str(out),pixels,write_async=False)
def font(size):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',size)
im=Image.open(out).convert('RGB');draw=ImageDraw.Draw(im)
draw.text((55,40),'A04  /  SPORT PLATFORM',font=font(round(a.width/58)),fill=(166,187,200))
draw.text((53,86),'Obsidian / Vector',font=font(round(a.width/36)),fill=(235,240,244))
caption={'hero':'EXTERIOR · CUBIERTAS ENRASADAS','posterior':'INTERFAZ POSTERIOR · MECANISMOS PROTEGIDOS','interior':'CORTE DE INSPECCIÓN · INTEGRACIÓN INTERNA'}[a.view]
draw.text((55,height-70),caption,font=font(round(a.width/82)),fill=(176,193,203))
draw.text((55,height-38),f'CAD REV.04   /   ESCALA OBJETIVO {a.mass} KG   /   DISEÑO EN DESARROLLO',font=font(round(a.width/100)),fill=(134,156,172))
im.save(out)
(ROOT/f'render_{a.mass}kg_{a.view}.json').write_text(json.dumps(dict(source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),renderer='Mitsuba3 scalar CPU path tracing from actual STEP',resolution=[a.width,height],requested_samples_per_pixel=a.spp,samples_per_pixel=effective_spp,view=a.view,no_AI_image_generator=True),indent=2))
print('RENDER_DONE',out,flush=True)
