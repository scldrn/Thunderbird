from pathlib import Path
import os,json,hashlib
os.environ['AERO_RENDER_VARIANT']='candidato_ejes'
import render_cad as base
from PIL import Image,ImageDraw
base.OUT=base.ROOT/'renders_revisados';base.OUT.mkdir(exist_ok=True);base.MESH=base.OUT/'mallas';base.MESH.mkdir(exist_ok=True)
path=base.OUT/'render_CAD_5kg_ejes_revisados.png'
items=base.meshes(5)
print('Renderizando CAD actualizado',flush=True)
image=base.mi.render(base.scene(items,5),spp=128,seed=81)
base.mi.util.write_bitmap(str(path),image,write_async=False)
im=Image.open(path).convert('RGB');w,h=im.size;draw=ImageDraw.Draw(im)
draw.text((85,65),'PLATAFORMA OMNIDIRECCIONAL',font=base.font(34),fill=(160,193,208))
draw.text((82,115),'Concepto 05 / Ejes revisados',font=base.font(57),fill=(238,243,246))
draw.text((85,h-110),'RENDER CAD · DISEÑO EN DESARROLLO',font=base.font(27),fill=(220,232,239))
draw.text((85,h-65),'Objetivo 5 kg · Palas y bujes ilustrativos · Retracción pendiente de diseño',font=base.font(22),fill=(175,194,207))
im.save(path)
source=base.DATA/'5kg/integracion_desplegada.step'
(base.OUT/'procedencia.json').write_text(json.dumps(dict(source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),samples=128,resolution=[w,h],renderer='Mitsuba CPU',display_only=['palas','ejes y bujes cilíndricos'],revision='ejes revisados'),indent=2))
print(path,flush=True)
