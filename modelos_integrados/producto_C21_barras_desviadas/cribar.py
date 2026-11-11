"""Explore two dogleg routes around C17 leaves, sampled poses only."""
from pathlib import Path
import hashlib,itertools,json,math,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
SEL=HERE.parent/'producto_C17_vastagos_radiales/AUDITORIA.json'
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def rod(a,b):
    d=b-a
    if d.Length<1e-6:raise ValueError('degenerate segment')
    return cq.Solid.makeCylinder(.5,d.Length,a,d.normalized())

def vol(a,b):
    if not overlap(a,b):return 0.
    c=a.intersect(b)
    if not c.isValid():raise ValueError('invalid boolean')
    return c.Volume()

def main():
    p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes'];selected=json.loads(SEL.read_text())['selected']
    phis={(r['leaf'],r['bearing']):r['phi_deg'] for r in selected}
    leaves={}
    for angle,a in itertools.product((0,15,30,45,60),axes):
        c=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
        leaves[angle,a['leaf']]=p['lamina_recortada_'+str(a['leaf'])].translate((0,0,20)).rotate(c,(c[0]+1,c[1],c[2]),angle)
    rows=[]
    for j,i,rail_x in itertools.product(range(2),range(3),(-215.,-105.)):
        endpoints=[]
        for k in (i,i+1):
            t=math.radians(phis[k,j]);a=axes[k]
            endpoints.append(cq.Vector((-164.,-156.)[j],a['y_mm']+6.5*math.cos(t),a['z_mm']+6.5*math.sin(t)))
        outer=[cq.Vector(rail_x,e.y,e.z) for e in endpoints]
        parts=[rod(endpoints[0],outer[0]),rod(outer[0],outer[1]),rod(outer[1],endpoints[1]),cq.Solid.makeSphere(.5,outer[0]),cq.Solid.makeSphere(.5,outer[1])]
        route=cq.Compound.makeCompound(parts)
        row={'bearing':j,'edge':i,'rail_x_mm':rail_x,'first_collision':None,'error':None,'checks':0,'passes':False}
        try:
            if any(vol(route,p[f'vastago_{k}_{j}'])<=.001 for k in (i,i+1)):raise ValueError('end not connected')
            for angle,k in itertools.product((60,0,45,30,15),range(4)):
                row['checks']+=1;v=vol(route.translate((0,0,20)),leaves[angle,k])
                if v>.001:row['first_collision']={'phase':'rotation','angle_deg':angle,'leaf':k,'volume_mm3':v};break
            if row['first_collision'] is None:
                for h,n in itertools.product((0,5,10,15,20),('piel','camisa','rotor','aro','junta')):
                    row['checks']+=1;v=vol(route.translate((0,0,h)),p[n])
                    if v>.001:row['first_collision']={'phase':'lift','lift_mm':h,'object':n,'volume_mm3':v};break
            row['passes']=row['first_collision'] is None
        except Exception as e:row['error']=repr(e);row['passes']=False
        rows.append(row);(HERE/'PARCIAL.json').write_text(json.dumps({'cases':rows},indent=2)+'\n')
        print('bearing',j,'edge',i,'x',rail_x,'pass',row['passes'],'error',row['error'],flush=True)
    out={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'scope':'two speculative dogleg x routes; sampled poses, no joints or full assembly', 'cases':rows}
    (HERE/'RESULTADOS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('C21_COMPLETO',flush=True)
if __name__=='__main__':main()
