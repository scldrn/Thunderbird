from pathlib import Path
import cadquery as cq,json,hashlib
from PIL import Image
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'familia_deportiva';checks=[]
for f in sorted(OUT.rglob('*.step')):
 ass=cq.Assembly.load(str(f));parts=[s.moved(loc) for s,name,loc,color in ass];assert all(s.isValid() for s in parts)
 checks.append(dict(file=str(f.relative_to(OUT)),parts=len(parts),valid=True,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
for p in OUT.rglob('*.png'):
 im=Image.open(p);im.verify()
(OUT/'verificacion_CAD.json').write_text(json.dumps(checks,indent=2))
with ZipFile(OUT/'familia_deportiva_CAD_y_renders.zip','w',ZIP_DEFLATED) as z:
 for f in sorted(OUT.rglob('*')):
  if f.is_file() and f.suffix in ['.step','.png','.json','.md']:z.write(f,str(f.relative_to(OUT)))
 z.write(ROOT/'familia_deportiva.py','fuentes/familia_deportiva.py');z.write(ROOT/'diseno_industrial_v2.py','fuentes/diseno_industrial_v2.py')
with ZipFile(OUT/'familia_deportiva_CAD_y_renders.zip') as z:assert z.testzip() is None
print(json.dumps(checks,indent=2));print('Entrega verificada')
