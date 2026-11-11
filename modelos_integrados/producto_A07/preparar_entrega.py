from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,csv
import cadquery as cq
p=Path(__file__).resolve().parent
with (p/'ejes_y_recorridos.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['compuerta','x_eje_mm','y_eje_mm','z_eje_cerrado_mm','elevacion_mm','sentido_Z','sentido_giro','giro_grados'])
 for r in json.loads((p/'propuesta_elevacion.json').read_text()):w.writerow([r['name'],*r['axis_closed'],r['lift_mm'],r['out'],r['sign'],110])
for mass in (2,5,10):
 folder=p/f'{mass}kg';m=json.loads((folder/'manifest.json').read_text())
 # Refresh changed sleeve volumes in metadata.
 actual={n.split('/')[-1]:s.moved(l) for s,n,l,c in cq.Assembly.load(str(folder/'A07_cerrado.step'))}
 for e in m['parts']:
  if e['name'].startswith('conducto_'):e['volume_mm3']=actual[e['name']].Volume()
 (folder/'manifest.json').write_text(json.dumps(m,indent=2))
 with (folder/'lista_piezas.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['pieza','alcance','volumen_mm3'])
  for e in m['parts']:w.writerow([e['name'],e['scope'],e['volume_mm3']])
files=[f for f in p.rglob('*') if f.is_file() and f.suffix in ('.step','.json','.py','.md','.csv','.png') and f.name!='ENTREGA.json' and 'render_meshes' not in f.parts]
(p/'ENTREGA.json').write_text(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
with ZipFile(p/'A07_CAD_apertura_interna.zip','w',ZIP_DEFLATED) as z:
 for f in files+[p/'ENTREGA.json']:z.write(f,f.relative_to(p))
with ZipFile(p/'A07_CAD_apertura_interna.zip') as z:
 assert len(z.namelist())==len(set(z.namelist()));assert z.testzip() is None
print('ZIP verified')
