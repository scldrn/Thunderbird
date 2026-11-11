"""Export one rejected rod in the collision-producing open pose."""
from pathlib import Path
import hashlib,json,math
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
SELECT=HERE.parent/'producto_C17_vastagos_radiales/AUDITORIA.json'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
res=json.loads((HERE/'RESULTADOS.json').read_text());row=next(x for x in res['cases'] if x['bearing']==0 and x['from_leaf']==0)
assert not row['passes_sampled_local'] and row['rotation_collisions']
angle=row['rotation_collisions'][0]['angle_deg'];axes=json.loads(AXES.read_text())['axes'];selected=json.loads(SELECT.read_text())['selected']
mapping={(x['leaf'],x['bearing']):x['phi_deg'] for x in selected}
ends=[]
for i in (0,1):
    a=axes[i];t=math.radians(mapping[i,0]);ends.append(cq.Vector(-164,a['y_mm']+6.5*math.cos(t),a['z_mm']+6.5*math.sin(t)+20))
v=ends[1]-ends[0];rod=cq.Solid.makeCylinder(.5,v.Length,ends[0],v.normalized())
parts={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
model=cq.Assembly(name='C19_RECHAZADO_INTERFERENCIA')
for name,s in parts.items():
    if name.startswith('lamina_recortada_'):
        i=int(name.rsplit('_',1)[-1]);a=axes[i];c=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
        s=s.translate((0,0,20)).rotate(c,(c[0]+1,c[1],c[2]),angle)
    elif name.startswith(('eje_','casquillo_','vastago_')):s=s.translate((0,0,20))
    model.add(s,name=name)
model.add(rod,name='barra_rechazada')
dst=HERE/'C19_barra_rechazada.step';model.save(str(dst))
items=[(n,s) for s,n,loc,c in cq.Assembly.load(str(dst))]
assert len(items)==30 and all(s.isValid() and s.Solids() for n,s in items)
(HERE/'AUDITORIA.json').write_text(json.dumps({'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'angle_deg':angle,'objects':len(items),'scope':'rejected illustration, validity only'},indent=2)+'\n')
print('30 valid objects; REJECTED rod, angle',angle)
