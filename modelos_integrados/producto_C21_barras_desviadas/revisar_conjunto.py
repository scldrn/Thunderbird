"""Check chosen dogleg rods against each other and other local components."""
from pathlib import Path
import hashlib,itertools,json,math,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
SELECT=HERE.parent/'producto_C17_vastagos_radiales/AUDITORIA.json'
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def rod(a,b):
    d=b-a
    return cq.Solid.makeCylinder(.5,d.Length,a,d.normalized())

def route(j,i,rail,axes,phi):
    ends=[]
    for k in (i,i+1):
        t=math.radians(phi[k,j]);a=axes[k]
        ends.append(cq.Vector((-164.,-156.)[j],a['y_mm']+6.5*math.cos(t),a['z_mm']+6.5*math.sin(t)))
    q=[cq.Vector(rail,e.y,e.z) for e in ends]
    return cq.Compound.makeCompound([rod(ends[0],q[0]),rod(q[0],q[1]),rod(q[1],ends[1]),cq.Solid.makeSphere(.5,q[0]),cq.Solid.makeSphere(.5,q[1])])

def main():
    cases=json.loads((HERE/'RESULTADOS.json').read_text())['cases']
    p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes'];selected=json.loads(SELECT.read_text())['selected'];phi={(r['leaf'],r['bearing']):r['phi_deg'] for r in selected}
    rods=[];selection=[];missing=[]
    for j,i in itertools.product(range(2),range(3)):
        candidates=[c for c in cases if (c['bearing'],c['edge'])==(j,i) and c['passes']]
        if not candidates:
            missing.append({'bearing':j,'edge':i})
            continue
        c=candidates[0];selection.append({'bearing':j,'edge':i,'rail_x_mm':c['rail_x_mm']});rods.append(route(j,i,c['rail_x_mm'],axes,phi))
    failures=[];errors=[];checked=0
    def check(a,b,label,allowed=None):
        nonlocal checked
        checked+=1
        if not overlap(a,b):return
        try:
            cross=a.intersect(b)
            if not cross.isValid():raise ValueError('invalid boolean')
            if allowed is not None:cross=cross.cut(allowed)
            v=cross.Volume()
            if v>.001:failures.append({'pair':label,'volume_mm3':v})
        except Exception as e:errors.append({'pair':label,'error':repr(e)})
    for n,shape in enumerate(rods):
        j,i=selection[n]['bearing'],selection[n]['edge']
        excluded={f'vastago_{i}_{j}',f'vastago_{i+1}_{j}'}
        for name,other in p.items():
            if name.startswith(('eje_','casquillo_','vastago_')) and name not in excluded:check(shape,other,[n,name])
        for k in range(n+1,len(rods)):
            other=selection[k]
            shared=p[f'vastago_{i+1}_{j}'] if other['bearing']==j and other['edge']==i+1 else None
            check(shape,rods[k],[n,k],shared)
    out={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'selection':selection,'missing':missing,'pairs_checked':checked,
         'collisions':failures,'errors':errors,'scope':'local closed pose: dogleg rods vs other stems, bearings, shafts and rods; connections excluded'}
    (HERE/'REVISION_CONJUNTO.json').write_text(json.dumps(out,indent=2)+'\n')
    print('checked',checked,'collisions',len(failures),'errors',len(errors),flush=True)
    # Export even if rejected: explicitly label the result with its status.
    label='C21_REJECTED' if failures or errors else ('C21_PARTIAL' if missing else 'C21_LOCAL_CANDIDATE')
    model=cq.Assembly(name=label)
    for name,s in p.items():model.add(s,name=name)
    for n,s in enumerate(rods):model.add(s,name='ruta_'+str(n))
    suffix='rechazado' if failures or errors else ('parcial' if missing else 'candidato')
    dst=HERE/('C21_'+suffix+'_local.step');model.save(str(dst))
    imported=[(n,s) for s,n,loc,c in cq.Assembly.load(str(dst))]
    if not all(s.isValid() and s.Solids() for n,s in imported):raise ValueError('invalid imported STEP')
    (HERE/'AUDITORIA.json').write_text(json.dumps({'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'imported_records':len(imported),'label':label},indent=2)+'\n')
    print('exported',label,'records',len(imported),flush=True)
if __name__=='__main__':main()
