"""Discrete, simultaneous 8-cover motion screen for C07, reference 5 kg.

Not a continuous sweep and not a whole-vehicle collision certification.
"""
from pathlib import Path
import json,time
import FreeCAD as App
HERE=Path(__file__).resolve().parent
src=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
d=App.openDocument(str(src))
p={o.Label:o.Shape.copy() for o in d.Objects if o.Name.startswith('pieza_')}
keys=[f'compuerta_C02_{i}_{side}' for i in range(4) for side in ('superior','inferior')]
fixed=['carroceria_C02_superior004','carroceria_C02_inferior003']
fixed += [f'modulo_C02_{i}_camisa_cuna_y_soportes' for i in range(4)]
fixed += [f'modulo_C02_{i}_rotor_copa' for i in range(4)]
fixed += [f'{prefix}_C02_{i}_{side}' for prefix in ('aro','junta') for i in range(4) for side in ('superior','inferior')]
assert all(n in p for n in keys+fixed),[n for n in keys+fixed if n not in p]

def posed(name,lift,dx):
 _,_,num,side=name.split('_');i=int(num)
 sign_x=-1 if i<2 else 1;sign_z=1 if side=='superior' else -1
 s=p[name].copy();s.translate(App.Vector(sign_x*dx,0,sign_z*lift));return s

def overlap(a,b):
 if not a.BoundBox.intersect(b.BoundBox):return None,False
 q=a.common(b)
 if not (q.isNull() or q.isValid()):raise ValueError('interseccion invalida')
 return q.Volume,True

report={'scope':'8 compuertas simultaneas, 6 poses discretas, pieles, cuatro conductos y rotores, ocho aros y ocho juntas; no revisa todas las 316 piezas, guias ni barrido continuo',
        'source':str(src),'threshold_mm3':.001,'fixed_obstacles':fixed,'poses':[],'errors':[]}
poses=[(5,0),(10,0),(10,25),(10,50),(10,75),(10,100)]
for lift,dx in poses:
 t=time.monotonic();moved={n:posed(n,lift,dx) for n in keys}
 row={'lift_mm':lift,'abs_dx_mm':dx,'screened_pairs':0,'boolean_pairs':0,'intersections':[],'errors':[]}
 for i,a in enumerate(keys):
  for b in fixed+keys[i+1:]:
   other=p[b] if b in p and b in fixed else moved[b]
   row['screened_pairs']+=1
   try:
    v,used=overlap(moved[a],other)
    row['boolean_pairs']+=int(used)
    if v is not None and v>.001:
     row['intersections'].append({'door':a,'obstacle':b,'volume_mm3':v})
   except Exception as e:row['errors'].append({'door':a,'obstacle':b,'error':repr(e)})
 row['seconds']=time.monotonic()-t
 report['poses'].append(row)
 (HERE/'TRAYECTORIA_PARCIAL.json').write_text(json.dumps(report,indent=2)+'\n')
 print('C07_POSE',lift,dx,'pares',row['screened_pairs'],'interferencias',len(row['intersections']),'errores',len(row['errors']),flush=True)
report['passed_screen']=len(report['poses'])==len(poses) and all(not r['intersections'] and not r['errors'] for r in report['poses'])
(HERE/'TRAYECTORIA.json').write_text(json.dumps(report,indent=2)+'\n')
print('C07_TRAYECTORIA_COMPLETA',report['passed_screen'],flush=True)
