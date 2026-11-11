"""Export a local candidate only if every bearing has a sampled-pass stem."""
from pathlib import Path
import hashlib,json,math
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C15_apoyos/C15_apoyos_conceptuales.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
results=json.loads((HERE/'RESULTADOS.json').read_text());axes=json.loads(AXES.read_text())['axes']
model=cq.Assembly(name='C17_candidate_not_mechanism')
for s,n,loc,c in cq.Assembly.load(str(SOURCE)):model.add(s.moved(loc),name=n.split('/')[-1])
selected=[];shapes=[]
for i in range(4):
    for j in range(2):
        candidates=[r for r in results['cases'] if r['leaf']==i and r['bearing']==j and r['passes']]
        if not candidates:raise ValueError('no passing candidate for leaf/bearing '+str((i,j)))
        r=candidates[0];phi=math.radians(r['phi_deg']);dy,dz=math.cos(phi),math.sin(phi)
        x=(-164.,-156.)[j];a=axes[i]
        s=cq.Solid.makeCylinder(.75,5.,cq.Vector(x,a['y_mm']+1.75*dy,a['z_mm']+1.75*dz),cq.Vector(0,dy,dz))
        selected.append({'leaf':i,'bearing':j,'phi_deg':r['phi_deg']});shapes.append(s)
        model.add(s,name='vastago_'+str(i)+'_'+str(j))
for i in range(8):
    for j in range(i+1,8):
        cross=shapes[i].intersect(shapes[j])
        if not cross.isValid() or cross.Volume()>.001:raise ValueError('stem interaction '+str((i,j)))
path=HERE/'C17_candidata_local.step';model.save(str(path))
items=[(n.split('/')[-1],s.moved(loc)) for s,n,loc,c in cq.Assembly.load(str(path))]
assert len(items)==29 and len({n for n,s in items})==29 and all(s.isValid() and s.Solids() for n,s in items)
out={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'selected':selected,'object_count':29,
     'scope':'local closed pose, 8 sampled-pass radial stems, no structure, guides or actuator'}
(HERE/'AUDITORIA.json').write_text(json.dumps(out,indent=2)+'\n')
print('29 objects reimported',selected)
