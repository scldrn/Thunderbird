"""Make per-scale review archives. The complete repository is needed to regenerate."""
from pathlib import Path
import hashlib,json,zipfile
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'MANIFIESTO.json').read_text())
common=['LEEME.md','MANIFIESTO.json','AUDITORIA.json','TRAYECTORIA.json','POSICION_GLOBAL.json','AUDITORIA_CAJAS_OPTIMAS.json',
        'crear_C07.py','auditar_C07.py','auditar_trayectoria.py','auditar_posicion_global.py','verificar_cajas_optimas.py','render_C07.py']
archives=[]
for v in manifest['variants']:
 mass=v['mass_target_kg']
 files=[(HERE/f,'producto_C07_deslizante/'+f) for f in common]
 for ext in ('FCStd','step'):
  files.append((HERE/v['native' if ext=='FCStd' else 'step'],f'producto_C07_deslizante/{mass}kg/C07_{mass}kg_deslizante_abierto.{ext}'))
  files.append((HERE.parent/'producto_C03'/f'{mass}kg'/f'C03_{mass}kg_cerrado.{ext}',f'producto_C03/{mass}kg/C03_{mass}kg_cerrado.{ext}'))
 for state in ('abierto','interior'):
  files.append((HERE/f'{mass}kg'/f'C07_{mass}kg_{state}.png',f'producto_C07_deslizante/{mass}kg/C07_{mass}kg_{state}.png'))
 dest=HERE/f'C07_{mass}kg_kit_CAD.zip';temp=HERE/f'C07_{mass}kg_kit_CAD.zip.tmp'
 with zipfile.ZipFile(temp,'w',allowZip64=True) as z:
  for path,name in files:
   if not path.is_file():raise FileNotFoundError(path)
   kind=zipfile.ZIP_STORED if path.suffix.lower() in ('.fcstd','.png') else zipfile.ZIP_DEFLATED
   z.write(path,arcname=f'C07_{mass}kg/'+name,compress_type=kind,compresslevel=4)
 with zipfile.ZipFile(temp) as z:
  if z.testzip():raise ValueError('error CRC')
 temp.replace(dest)
 h=hashlib.sha256()
 with dest.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 archives.append({'target_mass_kg':mass,'file':dest.name,'size_bytes':dest.stat().st_size,'sha256':h.hexdigest(),'entries':len(files)})
 print('C07_KIT_OK',mass,dest.stat().st_size,flush=True)
(HERE/'ENTREGA.json').write_text(json.dumps({'revision':'C07_conceptual','archives':archives,'reproduction_requires_full_repository':True},indent=2)+'\n')
