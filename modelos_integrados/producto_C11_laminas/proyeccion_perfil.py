from pathlib import Path
import gzip,json,sys
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'producto_C06_busqueda_eje'))
from proyeccion_apertura import raster_coverage
with gzip.open(H/'PERFIL_MALLAS.json.gz','rt') as f:d=json.load(f)
out={'scope':'Fraccion de proyeccion de malla sobre circulo D84, no caudal ni CFD; solo 672 pixeles y teselacion .4mm','cases':[]}
for a in d['angles']:
 q=raster_coverage(a['vertices'],a['triangles'],672)[0]
 out['cases'].append({'angle_deg':a['angle_deg'],**q})
(H/'PERFIL_PROYECCION.json').write_text(json.dumps(out,indent=2)+'\n')
for q in out['cases']:print(q['angle_deg'],round(q['covered_fraction'],4),flush=True)
