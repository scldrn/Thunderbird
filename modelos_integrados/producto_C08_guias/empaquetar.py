"""Create inspection package; full C03 repository required for regeneration."""
from pathlib import Path
import hashlib,json,zipfile
H=Path(__file__).resolve().parent
files=['LEEME.md','MANIFIESTO.json','MANIFIESTO_ALT.json','GUIAS.json','GUIAS_MOVIMIENTO.json','COMPARACION_PARES.json','UNION.json','UNION_ALT.json',
       'AUDITORIA_CAD.json','AUDITORIA_CAD_ALT.json','AUDITORIA_CAJAS_OPTIMAS.json',
       'cribar_guias.py','auditar_guias_movimiento.py','comparar_pares.py','explorar_union.py','explorar_union_alt.py',
       'crear_estudio.py','crear_estudio_alt.py','auditar_estudio.py','auditar_estudio_alt.py','verificar_registros.py','verificar_cajas_optimas.py',
       'render_C08.py','render_C08_alt.py']
for variant in ('local','alt'):
 for state in ('cerrado','abierto'):
  for suffix in ('FCStd','step','png'):files.append(f'C08_{variant}_{state}.{suffix}')
dest=H/'C08_estudio_guias.zip';tmp=H/'C08_estudio_guias.zip.tmp'
with zipfile.ZipFile(tmp,'w',allowZip64=True) as z:
 for name in files:
  path=H/name
  if not path.is_file():raise FileNotFoundError(path)
  compression=zipfile.ZIP_STORED if path.suffix.lower() in ('.fcstd','.png') else zipfile.ZIP_DEFLATED
  z.write(path,arcname='C08_estudio_guias/'+name,compress_type=compression,compresslevel=4)
with zipfile.ZipFile(tmp) as z:
 if z.testzip():raise ValueError('CRC invalido')
tmp.replace(dest)
h=hashlib.sha256()
with dest.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
(H/'ENTREGA.json').write_text(json.dumps({'file':dest.name,'sha256':h.hexdigest(),'size_bytes':dest.stat().st_size,'entries':len(files),'reproduction_requires_full_repository':True},indent=2)+'\n')
print('C08_KIT_OK',dest.stat().st_size,flush=True)
