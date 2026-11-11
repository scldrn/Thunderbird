"""Check selected closed stems against other bearings and all shafts."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap
path=HERE/'C17_candidata_local.step'
p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(path))}
collisions=[];errors=[];count=0
for i in range(4):
    for j in range(2):
        stem=p[f'vastago_{i}_{j}']
        others=[f'eje_{k}' for k in range(4)]+[f'casquillo_{k}_{q}' for k in range(4) for q in range(2) if (k,q)!=(i,j)]
        for n in others:
            count+=1
            if not overlap(stem,p[n]):continue
            try:
                s=stem.intersect(p[n])
                if not s.isValid():raise ValueError('invalid intersection')
                if s.Volume()>.001:collisions.append({'stem':[i,j],'object':n,'volume_mm3':s.Volume()})
            except Exception as error:errors.append({'stem':[i,j],'object':n,'error':repr(error)})
result={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pairs_checked':count,'collisions':collisions,'errors':errors,
        'scope':'only closed pose, stems vs shafts and other bearings, own bearing excluded intentionally'}
(HERE/'REVISION_CONJUNTO.json').write_text(json.dumps(result,indent=2)+'\n')
print(count,'pairs,',len(collisions),'collisions,',len(errors),'errors')
if errors:raise RuntimeError('unknown collisions')
