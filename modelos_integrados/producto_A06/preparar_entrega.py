from pathlib import Path
import json,csv,hashlib
from zipfile import ZipFile,ZIP_DEFLATED
p=Path(__file__).resolve().parent
rows=[]
for m in (2,5,10):
 d=json.loads((p/f'{m}kg/manifest.json').read_text())
 rows.append([m,*d['assembly_dimensions_mm'],d['fin_root_chord_mm'],d['fin_tip_chord_mm'],d['fin_exposed_span_mm'],d['valid_parts']])
 with (p/f'{m}kg/lista_piezas.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['pieza','alcance','volumen_mm3','exterior'])
  for part in d['parts']:w.writerow([part['name'],part['scope'],part['volume_mm3'],part['exterior']])
with (p/'dimensiones.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['masa_objetivo_kg','largo_mm','ancho_mm','alto_mm','cuerda_raiz_aleta_mm','cuerda_punta_mm','envergadura_radial_expuesta_mm','piezas']);w.writerows(rows)

files=[f for f in p.rglob('*') if f.is_file() and f.name!='ENTREGA.json' and f.suffix in ('.py','.step','.stl','.json','.csv','.md','.png') and 'render_meshes' not in f.parts]
(p/'ENTREGA.json').write_text(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
with ZipFile(p/'A06_CAD_integrado.zip','w',ZIP_DEFLATED) as z:
 for f in files+[p/'ENTREGA.json']:z.write(f,f.relative_to(p))
with ZipFile(p/'A06_CAD_integrado.zip') as z:assert z.testzip() is None
print(rows)
