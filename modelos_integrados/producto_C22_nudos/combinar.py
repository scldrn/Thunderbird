"""Check C21 row-0 dogleg combinations with explicit local junction volumes."""
from pathlib import Path
import hashlib,itertools,json,math,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
SEL=HERE.parent/'producto_C17_vastagos_radiales/AUDITORIA.json'
ROUTES=HERE.parent/'producto_C21_barras_desviadas/RESULTADOS.json'
sys.path.insert(0,str(HERE.parent/'producto_C21_barras_desviadas'))
from revisar_conjunto import route
from cribar import overlap

def main():
    p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes'];sel=json.loads(SEL.read_text())['selected'];phi={(r['leaf'],r['bearing']):r['phi_deg'] for r in sel}
    nodes=json.loads((HERE/'RESULTADOS.json').read_text())['cases']
    n={}
    for i in (1,2):
        row=next(r for r in nodes if r['leaf']==i and r['radius_mm']==1.5)
        if not row['passes']:raise ValueError('junction failed sampled screen')
        n[i]=cq.Solid.makeSphere(1.5,cq.Vector(*row['center_mm']),angleDegrees1=-90,angleDegrees2=90)
    cases=json.loads(ROUTES.read_text())['cases'];rods={};ind=[]
    for i,rail in itertools.product(range(3),(-215.,-105.)):
        row=next(r for r in cases if (r['bearing'],r['edge'],r['rail_x_mm'])==(0,i,rail))
        if not row['passes']:raise ValueError('individual rod not screened')
        rods[i,rail]=route(0,i,rail,axes,phi)
        bad=[];errors=[]
        for name,other in p.items():
            if not name.startswith(('eje_','casquillo_','vastago_')) or name in (f'vastago_{i}_0',f'vastago_{i+1}_0'):continue
            try:
                shape=rods[i,rail].intersect(other)
                if shape.wrapped.IsNull():continue
                if not shape.isValid():raise ValueError('invalid intersection')
                v=shape.Volume()
                if v>.001:bad.append({'object':name,'volume_mm3':v})
            except Exception as e:errors.append({'object':name,'error':repr(e)})
        ind.append({'edge':i,'rail_x_mm':rail,'collisions':bad,'errors':errors,'passes':not bad and not errors})
        print('route',i,rail,'other collisions',len(bad),'errors',len(errors),flush=True)
    pairs=[]
    for i,j,ri,rj in itertools.chain(itertools.product((0,),(1,),(-215.,-105.),(-215.,-105.)),
                                      itertools.product((1,),(2,),(-215.,-105.),(-215.,-105.)),
                                      itertools.product((0,),(2,),(-215.,-105.),(-215.,-105.))):
        row={'edge_a':i,'edge_b':j,'rail_a':ri,'rail_b':rj,'overlap_outside_node_mm3':None,'error':None}
        try:
            volumes=[]
            # Components overlap at their own route nodes; compare solids
            # separately to avoid ambiguous booleans on compound compounds.
            for sa,sb in itertools.product(rods[i,ri].Solids(),rods[j,rj].Solids()):
                if not overlap(sa,sb):continue
                c=sa.intersect(sb)
                if c.wrapped.IsNull() or c.Volume()<=1e-9:continue
                if not c.isValid():raise ValueError('invalid common')
                if j==i+1:
                    c=c.cut(n[j])
                if not c.wrapped.IsNull():volumes.append(c.Volume())
            v=max(volumes,default=0.)
            row['overlap_outside_node_mm3']=v
        except Exception as e:row['error']=repr(e)
        pairs.append(row)
    combos=[]
    for rails in itertools.product((-215.,-105.),repeat=3):
        own=[next(r for r in ind if (r['edge'],r['rail_x_mm'])==(i,rails[i])) for i in range(3)]
        cross=[next(r for r in pairs if (r['edge_a'],r['edge_b'],r['rail_a'],r['rail_b'])==(i,j,rails[i],rails[j])) for i,j in ((0,1),(1,2),(0,2))]
        combos.append({'rails':rails,'passes':all(r['passes'] for r in own) and all(r['error'] is None and r['overlap_outside_node_mm3']<=.001 for r in cross)})
    out={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'node_source_sha256':hashlib.sha256((HERE/'RESULTADOS.json').read_bytes()).hexdigest(),
         'scope':'row 0 only, selected C17 stems, 1.5mm sampled nodes, closed pair check, local poses only',
         'routes':ind,'pairs':pairs,'combinations':combos}
    (HERE/'COMBINACIONES.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('passing combinations',sum(c['passes'] for c in combos),'/',len(combos),'errors',sum(bool(r['error']) for r in pairs),flush=True)
if __name__=='__main__':main()
