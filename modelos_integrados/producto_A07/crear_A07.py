from pathlib import Path
import cadquery as cq,json,shutil,numpy as np
P=Path(__file__).resolve().parent;BASE=P/'base_A06'
if not BASE.exists():
 BASE.mkdir()
 for m in (2,5,10):
  (BASE/f'{m}kg').mkdir()
  for f in ('A06_integrado.step','manifest.json'):shutil.copyfile(P.parent/'producto_A06'/f'{m}kg'/f,BASE/f'{m}kg'/f)
rules={r['name']:r for r in json.loads((P/'propuesta_elevacion.json').read_text())}
parts=[dict(name=n.split('/')[-1],shape=s.moved(l),color=c) for s,n,l,c in cq.Assembly.load(str(BASE/'5kg/A06_integrado.step'))]
# Clip internal duct sleeves against a 2-mm inset loft, so covers have a nominal gap.
outerfile=P/'envolvente.step'
if not outerfile.exists():shutil.copyfile(P.parent/'producto_A06/envolvente.step',outerfile)
outer=cq.importers.importStep(str(outerfile)).val().Solids()[0]
sections=[(-680,7,6),(-580,58,36),(-400,127,80),(-140,160,107),(160,150,103),(400,112,78),(570,63,47),(660,25,25)]
wires=[]
for x,w,h in sections:
 yz=np.array([(w,0),(.79*w,.67*h),(.37*w,h),(-.37*w,h),(-.79*w,.67*h),(-w,0),(-.75*w,-.62*h),(-.32*w,-.78*h),(.32*w,-.78*h),(.75*w,-.62*h)])
 edges=np.roll(yz,-1,axis=0)-yz;n=np.column_stack([-edges[:,1],edges[:,0]])/np.linalg.norm(edges,axis=1)[:,None]
 d=min(2.,min(w,h)*.38)
 v=[np.linalg.solve(np.array([n[i-1],n[i]]),[n[i-1]@yz[i]+d,n[i]@yz[i]+d]) for i in range(len(yz))]
 wires.append(cq.Wire.makePolygon([cq.Vector(x,*p) for p in v]+[cq.Vector(x,*v[0])]))
inner=cq.Solid.makeLoft(wires,False)
for p in parts:
 if p['name'].startswith('conducto_'):p['shape']=p['shape'].intersect(inner);assert p['shape'].isValid()
fixed=[p for p in parts if p['name'] not in rules];moving=[p for p in parts if p['name'] in rules]
def moved(s,name,lift,angle):
 r=rules[name];axis=list(r['axis_closed']);axis[2]+=r['out']*lift
 return s.translate((0,0,r['out']*lift)).rotate(axis,(axis[0]+100,axis[1],axis[2]),r['sign']*angle)
def overlapbox(a,b):
 a=a.BoundingBox();b=b.BoundingBox();return all(max(getattr(a,v+'min'),getattr(b,v+'min'))<min(getattr(a,v+'max'),getattr(b,v+'max'))-1e-6 for v in 'xyz')
# Conservative nominal reference volume plus the actual external fins.
cap_union=cq.Compound.makeCompound([p['shape'] for p in moving])
body_obstacle=outer.cut(cap_union)
external=[(p['name'],p['shape']) for p in fixed if p['name'].startswith(('aleta_movil_','carenado_raiz_'))]
records=[];maxov=0;failures=[];tested=0
stages=[(float(l),0.) for l in range(0,11,2)]+[(10.,float(a)) for a in range(2,111,2)]
for lift,angle in stages:
 poses=[(p['name'],moved(p['shape'],p['name'],lift,angle)) for p in moving]
 for i,(name,s) in enumerate(poses):
  for other,t in [('reference_hull_without_closed_caps',body_obstacle)]+external+poses[i+1:]:
   if not overlapbox(s,t):continue
   ov=s.intersect(t).Volume();tested+=1;maxov=max(maxov,ov)
   if ov>1e-3:failures.append(dict(lift=lift,angle=angle,a=name,b=other,overlap_mm3=ov))
 records.append(dict(lift_mm=lift,angle_deg=angle))
 print('POSE',lift,angle,'max overlap',maxov,flush=True)
# Separate actual closed-door vs modified duct check.
duct_checks=[]
for p in moving:
 for d in fixed:
  if d['name'].startswith('conducto_') and overlapbox(p['shape'],d['shape']):
   ov=p['shape'].intersect(d['shape']).Volume();duct_checks.append(dict(door=p['name'],duct=d['name'],overlap_mm3=ov));assert ov<1e-3
(P/'VERIFICACION_RECORRIDO.json').write_text(json.dumps(dict(nodes=len(stages),doors=8,boolean_pairs_tested=tested,max_overlap_mm3=maxov,failures=failures,poses=records,rules=rules,duct_checks=duct_checks,scope='Discrete nominal intersections against reference hull minus caps, actual external fins/fairings and other moving caps. Actual closed cap/duct checks separate. No continuous sweep, tolerance/deformation, loads or mechanism validation.'),indent=2))
# Export even rejected candidates, with explicit status in metadata.
for mass in (2,5,10):
 scale=(mass/5)**(1/3);folder=P/f'{mass}kg';folder.mkdir(exist_ok=True)
 meta=json.loads((BASE/f'{mass}kg/manifest.json').read_text());meta.update(kinematic_candidate=True,motion_collision_screen_passed=not failures,rotor_deployment=False)
 for entry in meta['parts']:
  actual=next(p['shape'] for p in parts if p['name']==entry['name'])
  entry['volume_mm3']=actual.Volume()*scale**3
 (folder/'manifest.json').write_text(json.dumps(meta,indent=2))
 for label,lift,ang in [('cerrado',0,0),('elevado',10,0),('abierto',10,110)]:
  asm=cq.Assembly(name=f'A07_{label}_{mass}kg')
  for p in parts:
   s=moved(p['shape'],p['name'],lift,ang) if p['name'] in rules else p['shape']
   asm.add(s.scale(scale),name=p['name'],color=p['color'])
  file=folder/f'A07_{label}.step';asm.save(str(file));r=list(cq.Assembly.load(str(file)));assert len(r)==208 and all(s.moved(l).isValid() for s,n,l,c in r)
 print('EXPORTED',mass,flush=True)
print('FAILURES',len(failures),flush=True)
