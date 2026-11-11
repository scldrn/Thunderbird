"""Range download of public official package; installation still checks signed SHA256."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request,math,hashlib
ROOT=Path(__file__).resolve().parent
url='https://downloads.sourceforge.net/project/foam/foam/ubuntu/dists/noble/main/binary-arm64/openfoam13_20260624_arm64.deb'
size=114996196;parts=8;chunk=math.ceil(size/parts)
def fetch(i):
 start=i*chunk;end=min(size-1,(i+1)*chunk-1);p=ROOT/f'package.part{i}'
 req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
 with urllib.request.urlopen(req,timeout=40) as response:
  assert response.status==206,response.status
  data=response.read();assert len(data)==end-start+1,(i,len(data));p.write_bytes(data)
 print('Parte completada',i,flush=True);return p
with ThreadPoolExecutor(max_workers=8) as pool:paths=list(pool.map(fetch,range(parts)))
out=ROOT/'openfoam13.complete.deb'
with out.open('wb') as f:
 for p in paths:f.write(p.read_bytes())
assert out.stat().st_size==size
print('SHA256 descargado',hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
for p in paths:p.unlink()
