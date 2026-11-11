from pathlib import Path
import cadquery as cq,json,shutil
P=Path(__file__).resolve().parent;BASE=P/'base_A06'
if not BASE.exists():
 BASE.mkdir()
 for m in (2,5,10):
  (BASE/f'{m}kg').mkdir()
  for f in ('A06_integrado.step','manifest.json'):shutil.copyfile(P.parent/'producto_A06'/f'{m}kg'/f,BASE/f'{m}kg'/f)
rules={r['name']:r for r in json.loads((P/'propuesta_elevacion.json').read_text())}
parts=[dict(name=n.split('/')[-1],shape=s.moved(l),color=c) for s,n,l,c in cq.Assembly.load(str(BASE/'5kg/A06_integrado.step'))]
fixed=[p for p in parts if p['name'] not in rules];moving=[p for p in parts if p['name'] in rules]
def moved(s,name,lift,angle):
 r=rules[name];axis=list(r['axis_closed']);axis[2]+=r['out']*lift
 return s.translate((0,0,r['out']*lift)).rotate(axis,(axis[0]+100,axis[1],axis[2]),r['sign']*angle)
def overlapbox(a,b):
 a=a.BoundingBox();b=b.BoundingBox();return all(max(getattr(a,v+'min'),getattr(b,v+'min'))<min(getattr(a,v+'max'),getattr(b,v+'max'))-1e-6 for v in 'xyz')
# Full installed geometry at simultaneous prescribed poses; no added unselected hardware.
records=[];maxov=0;failures=[];tested=0
stages=[(0.,0.)]
for lift,angle in stages:
 poses=[(p['name'],moved(p['shape'],p['name'],lift,angle)) for p in moving]
 for i,(name,s) in enumerate(poses):
  for other,t in [(p['name'],p['shape']) for p in fixed]+poses[i+1:]:
   if not overlapbox(s,t):continue
   ov=s.intersect(t).Volume();tested+=1;maxov=max(maxov,ov)
   if ov>1e-3:
    failures.append(dict(lift=lift,angle=angle,a=name,b=other,overlap_mm3=ov));print('COLLISION',failures[-1],flush=True)
 records.append(dict(lift_mm=lift,angle_deg=angle))
 print('POSE',lift,angle,'max overlap',maxov,flush=True)
(P/'VERIFICACION_RECORRIDO.json').write_text(json.dumps(dict(nodes=len(stages),doors=8,boolean_pairs_tested=tested,max_overlap_mm3=maxov,failures=failures,poses=records,rules=rules,scope='Discrete nominal solid intersections, simultaneous door poses. No continuous sweep or tolerance/deformation, loads or mechanism validation.'),indent=2))
