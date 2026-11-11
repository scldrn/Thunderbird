"""Summarize C10 screening without equating no-contact with collision."""
from pathlib import Path
from collections import Counter
import hashlib,json
H=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def classify(case):
 if case['sampled_ok']:return 'pasa_muestras'
 q=case['poses'][-1]
 if q.get('collision'):return 'colision'
 if q.get('error')=='no se obtuvo contacto volumetrico con tapa':return 'contacto_no_establecido'
 return 'error_de_calculo'

def main():
 inputs=[H.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd',H.parent/'producto_C09_paso_sellado/ENLACES.json',H.parent/'producto_C08_guias/GUIAS.json',H/'buscar_enlaces.py',H/'buscar_elevacion_30.py',H/'BUSQUEDA.json',H/'BUSQUEDA_30.json']
 out={'scope':'clasificacion de cribado discreto con elemento telescopico ideal; no valida mecanismo ni permite extrapolacion global','inputs':{str(p):sha(p) for p in inputs},'cases':{}}
 for lift,name in ((10,'BUSQUEDA.json'),(30,'BUSQUEDA_30.json')):
  data=json.loads((H/name).read_text());rows=data['cases'];groups=Counter(classify(c) for c in rows)
  obstacles=Counter((c['poses'][-1].get('collision') or {}).get('name') for c in rows if classify(c)=='colision')
  out['cases'][str(lift)]={'count':len(rows),'classification':dict(groups),'first_detected_obstacles':dict(obstacles)}
 (H/'RESUMEN.json').write_text(json.dumps(out,indent=2)+'\n')
 for k,v in out['cases'].items():print('ELEVACION',k,v,flush=True)
if __name__=='__main__':main()
