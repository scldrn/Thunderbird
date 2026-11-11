from pathlib import Path
import cadquery as cq,json
P=Path(__file__).resolve().parent;src=P/'base_A06'
outer=cq.importers.importStep(str(P/'envolvente.step')).val().Solids()[0]
parts={n.split('/')[-1]:s.moved(l) for s,n,l,c in cq.Assembly.load(str(src/'5kg/A06_integrado.step'))}
rows=[]
for name,s in parts.items():
 if not name.startswith('compuerta_'):continue
 j=int(name.split('_')[1]);y=(-76,76,-76,76)[j];x=(-200,-200,200,200)[j];side=1 if y>0 else -1;top='superior' in name
 b=s.BoundingBox();z=b.zmax+4 if top else b.zmin-4
 axis=(x,y+side*48,z);sign=-side if top else side
 fixed=outer.cut(s)
 for angle in (0,5,15,30,60,90,110):
  m=s.rotate(axis,(x+100,axis[1],axis[2]),sign*angle);over=m.intersect(fixed).Volume()
  rows.append(dict(name=name,angle_deg=angle,overlap_mm3=over,axis=axis,sign=sign))
 print(name,max(r['overlap_mm3'] for r in rows if r['name']==name),flush=True)
(P/'cribado_apertura.json').write_text(json.dumps(rows,indent=2))
