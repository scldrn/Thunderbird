from pathlib import Path
import json,hashlib
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image
import cadquery as cq
OUT=Path(__file__).resolve().parent/'producto_conceptual_detallado'
names=['A_internos_detallado','B_retractil_guardado_detallado','B_retractil_desplegado_detallado','C_conductos_detallado'];validation=[]
for name in names:
 path=OUT/(name+'.step');a=cq.Assembly.load(str(path));parts=[s.moved(loc) for s,label,loc,color in a];assert all(s.isValid() for s in parts)
 image=Image.open(OUT/(name+'.png'));assert image.size==(2000,1350);image.verify()
 validation.append(dict(file=path.name,parts=len(parts),valid=True,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 print('Verificado',name,len(parts),flush=True)
board=Image.new('RGB',(2800,1890))
for j,name in enumerate(names):board.paste(Image.open(OUT/(name+'.png')).resize((1400,945)),((j%2)*1400,(j//2)*945))
board.save(OUT/'comparacion_detallada.png')
(OUT/'verificacion_reimportacion.json').write_text(json.dumps(validation,indent=2));(OUT/'manifest.json').write_text(json.dumps(validation,indent=2))
with ZipFile(OUT/'CAD_detallados_y_renders.zip','w',ZIP_DEFLATED) as z:
 for pat in ['*.step','*.png','*.json','*.md']:
  for f in OUT.glob(pat):z.write(f,f.name)
 for name in ['cad_protegidos_detallados.py','corregir_render_detallado.py','empaquetar_cad_detallado.py']:z.write(OUT.parent/name,'fuentes/'+name)
print('Entrega preparada',flush=True)
