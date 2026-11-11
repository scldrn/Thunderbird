"""Raster projected silhouette of C11 leaves over nominal D84 opening."""
from pathlib import Path
import gzip,json,sys
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'producto_C06_busqueda_eje'))
from proyeccion_apertura import raster_coverage
out={'scope':'Proyeccion XY de cuatro mallas sobre circulo nominal D84, no caudal ni eficiencia; teselacion .4mm','states':{}}
for state in ('cerrado','elevado_60'):
 with gzip.open(H/f'C11_{state}_mallas.json.gz','rt') as f:items=json.load(f)['items']
 vertices=[];triangles=[]
 for a in items:
  if not a['name'].startswith('lamina_'):continue
  offset=len(vertices);vertices.extend(a['vertices']);triangles.extend([[offset+k for k in t] for t in a['triangles']])
 out['states'][state]=[raster_coverage(vertices,triangles,n)[0] for n in (336,672,1344)]
(H/'PROYECCION.json').write_text(json.dumps(out,indent=2)+'\n')
for k,v in out['states'].items():print(k,[round(q['covered_fraction'],6) for q in v],flush=True)
