"""Export one conditional row-0 combination, not a completed elevator."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
SELECT=HERE.parent/'producto_C17_vastagos_radiales/AUDITORIA.json'
sys.path.insert(0,str(HERE.parent/'producto_C21_barras_desviadas'))
from revisar_conjunto import route

combos=json.loads((HERE/'COMBINACIONES.json').read_text())['combinations']
best=next(c for c in combos if c['passes']);rails=best['rails']
axes=json.loads(AXES.read_text())['axes'];select=json.loads(SELECT.read_text())['selected'];phi={(r['leaf'],r['bearing']):r['phi_deg'] for r in select}
nodes_data=json.loads((HERE/'RESULTADOS.json').read_text())['cases'];nodes={}
for i in (1,2):
    n=next(r for r in nodes_data if r['leaf']==i and r['radius_mm']==1.5 and r['passes'])
    nodes[i]=cq.Solid.makeSphere(1.5,cq.Vector(*n['center_mm']),angleDegrees1=-90,angleDegrees2=90)
rods=[route(0,i,rails[i],axes,phi) for i in range(3)]
connect=[]
for i,node in nodes.items():
    for edge in (i-1,i):
        volumes=[]
        for solid in rods[edge].Solids():
            common=solid.intersect(node)
            if not common.wrapped.IsNull():volumes.append(common.Volume())
        maximum=max(volumes,default=0.)
        if maximum<=.001:raise ValueError('rod does not reach shared junction')
        connect.append({'node':i,'edge':edge,'max_component_overlap_mm3':maximum})
model=cq.Assembly(name='C22_ROW0_ONLY_NOT_MECHANISM')
for s,n,loc,c in cq.Assembly.load(str(SOURCE)):model.add(s.moved(loc),name=n.split('/')[-1])
for i,s in enumerate(rods):model.add(s,name='ruta_fila0_'+str(i))
for i,s in nodes.items():model.add(s,name='nudo_fila0_'+str(i))
dst=HERE/'C22_fila0_parcial.step';model.save(str(dst))
items=[(n,s) for s,n,loc,c in cq.Assembly.load(str(dst))]
assert all(s.isValid() and s.Solids() for n,s in items)
out={'step_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'records':len(items),'rails':rails,
     'intentional_joint_overlap':connect,'scope':'partial local row 0 only, STEP validity and intended joint overlap, no mechanism'}
(HERE/'AUDITORIA.json').write_text(json.dumps(out,indent=2)+'\n')
print('exported',len(items),'records; junction checks',len(connect),flush=True)
