exec((__import__('pathlib').Path(__file__).parent/'estudiar_apertura.py').read_text().split('rows=[]')[0])
result=[]
for name,s in parts.items():
 if not name.startswith('compuerta_'):continue
 j=int(name.split('_')[1]);y=(-76,76,-76,76)[j];x=(-200,-200,200,200)[j];side=1 if y>0 else -1;top='superior' in name;out=1 if top else -1
 b=s.BoundingBox();z=b.zmin-4 if top else b.zmax+4;sign=-side if top else side;fixed=outer.cut(s)
 for lift in range(0,101,5):
  axis=(x,y+side*48,z+out*lift);lifted=s.translate((0,0,out*lift))
  maxov=max(lifted.rotate(axis,(x+100,axis[1],axis[2]),sign*ang).intersect(fixed).Volume() for ang in (5,15,30,45,60,90,110))
  if maxov<1e-4:break
 else:raise ValueError(name)
 result.append(dict(name=name,lift_mm=lift+5,axis_closed=[x,y+side*48,z],sign=sign,out=out))
 print(name,lift+5,flush=True)
(P/'propuesta_elevacion.json').write_text(json.dumps(result,indent=2))
