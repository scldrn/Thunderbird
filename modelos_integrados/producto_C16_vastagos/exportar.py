from pathlib import Path
import hashlib,json
import cadquery as cq

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C15_apoyos/C15_apoyos_conceptuales.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
def stem(x,y,z,direction,length):
    return cq.Solid.makeCylinder(.75,length,cq.Vector(x,y,z+direction*1.75),cq.Vector(0,0,direction))
res=json.loads((HERE/'RESULTADOS.json').read_text())
axes=json.loads(AXES.read_text())['axes']
selected=[(3,0,1,5.),(3,1,-1,5.)]
model=cq.Assembly(name='C16_concept_not_mechanism')
for s,n,loc,c in cq.Assembly.load(str(SOURCE)):
    model.add(s.moved(loc),name=n.split('/')[-1])
for i,j,d,length in selected:
    row=next(r for r in res['cases'] if (r['leaf'],r['bearing'],r['direction'],r['length_mm'])==(i,j,d,length))
    assert row['passes_sampled_local']
    a=axes[i];x=(-164.,-156.)[j]
    model.add(stem(x,a['y_mm'],a['z_mm'],d,length),name='vastago_'+str(i)+'_'+str(j))
path=HERE/'C16_vastagos_lamina3_local.step'
model.save(str(path))
items=[(n.split('/')[-1],s.moved(loc)) for s,n,loc,c in cq.Assembly.load(str(path))]
assert len(items)==23 and len({n for n,s in items})==23 and all(s.isValid() and s.Solids() for n,s in items)
audit={'step_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'object_count':len(items),
       'scope':'local STEP validity; 2 stems for one leaf only; not a complete mechanism'}
(HERE/'AUDITORIA.json').write_text(json.dumps(audit,indent=2)+'\n')
print('23 valid objects; only two stems in leaf 3')
