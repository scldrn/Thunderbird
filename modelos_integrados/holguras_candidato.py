import cadquery as cq,json,csv,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parent
summary=[]
for m in [5,10]:
 folder=ROOT/'candidato_ejes'/f'{m}kg';a=cq.Assembly.load(str(folder/'integracion_desplegada.step'))
 objects={name.split('/')[-1]:s.moved(loc) for s,name,loc,color in a}
 assert all(s.isValid() for s in objects.values())
 rows=[]
 for (na,sa),(nb,sb) in itertools.combinations(objects.items(),2):
  if not (na.startswith('barrido') or nb.startswith('barrido')):continue
  if na.startswith('reserva') or nb.startswith('reserva'):continue
  rows.append(dict(a=na,b=nb,distance_m=sa.distance(sb)/1000))
 with (folder/'holguras_rotores.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 collisions=list(csv.DictReader((folder/'interferencias.csv').open()))
 assert len(collisions)==8 and all(r['a'].startswith('brazo') and r['b'].startswith('modulo') for r in collisions)
 assert all(float(r['intersection_m3'])<1e-9 for r in csv.DictReader((folder/'rotores_fuselaje.csv').open()))
 summary.append(dict(target_mass_kg=m,closest_pair=min(rows,key=lambda r:r['distance_m']),minimum_rotor_pair=min([r for r in rows if r['a'].startswith('barrido') and r['b'].startswith('barrido')],key=lambda r:r['distance_m'])))
(ROOT/'candidato_ejes'/'holguras_RESUMEN.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
