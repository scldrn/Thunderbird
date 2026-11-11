"""Search straight rods across individually screened radial-stem directions."""
from pathlib import Path
import hashlib,itertools,json,math,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C15_apoyos/C15_apoyos_conceptuales.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
OPTIONS=HERE.parent/'producto_C17_vastagos_radiales/RESULTADOS.json'
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def stem(x,a,phi):
    t=math.radians(phi);dy,dz=math.cos(t),math.sin(t)
    return cq.Solid.makeCylinder(.75,5,cq.Vector(x,a['y_mm']+1.75*dy,a['z_mm']+1.75*dz),cq.Vector(0,dy,dz))

def rod(x,a,pa,b,pb):
    def tip(axis,phi):
        t=math.radians(phi)
        return cq.Vector(x,axis['y_mm']+6.5*math.cos(t),axis['z_mm']+6.5*math.sin(t))
    u,v=tip(a,pa),tip(b,pb);d=v-u
    return cq.Solid.makeCylinder(.5,d.Length,u,d.normalized())

def vol(a,b):
    if not overlap(a,b):return 0.
    c=a.intersect(b)
    if not c.isValid():raise ValueError('invalid boolean')
    return float(c.Volume())

def main():
    p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes'];options=json.loads(OPTIONS.read_text())['cases']
    angles={}
    for t,a in itertools.product((0,15,30,45,60),axes):
        c=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
        angles[t,a['leaf']]=p['lamina_recortada_'+str(a['leaf'])].translate((0,0,20)).rotate(c,(c[0]+1,c[1],c[2]),t)
    out={'scope':'straight synchronization rods, local C15 assembly, C17-passing stem orientations; sampled poses only',
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'options_sha256':hashlib.sha256(OPTIONS.read_bytes()).hexdigest(),
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':[]}
    for j in range(2):
        x=(-164.,-156.)[j]
        for i in range(3):
            aa=[r['phi_deg'] for r in options if r['leaf']==i and r['bearing']==j and r['passes']]
            bb=[r['phi_deg'] for r in options if r['leaf']==i+1 and r['bearing']==j and r['passes']]
            for pa,pb in itertools.product(aa,bb):
                line=rod(x,axes[i],pa,axes[i+1],pb)
                row={'bearing':j,'edge':i,'phi_from':pa,'phi_to':pb,'first_collision':None,'error':None,'passes':False,'checks':0}
                try:
                    if min(vol(line,stem(x,axes[i],pa)),vol(line,stem(x,axes[i+1],pb)))<=.001:raise ValueError('end does not overlap stem')
                    for t,k in itertools.product((60,0,45,30,15),range(4)):
                        row['checks']+=1;v=vol(line.translate((0,0,20)),angles[t,k])
                        if v>.001:row['first_collision']={'phase':'rotation','angle_deg':t,'leaf':k,'volume_mm3':v};break
                    if row['first_collision'] is None:
                        for h,n in itertools.product((0,5,10,15,20),('piel','camisa','rotor','aro','junta')):
                            row['checks']+=1;v=vol(line.translate((0,0,h)),p[n])
                            if v>.001:row['first_collision']={'phase':'lift','lift_mm':h,'object':n,'volume_mm3':v};break
                    if row['first_collision'] is None:
                        for n in [x for x in p if x.startswith(('eje_','casquillo_'))]:
                            row['checks']+=1;v=vol(line,p[n])
                            if v>.001:row['first_collision']={'phase':'other_component','object':n,'volume_mm3':v};break
                    row['passes']=row['first_collision'] is None
                except Exception as e:row['error']=repr(e);row['passes']=False
                out['cases'].append(row)
            (HERE/'PARCIAL.json').write_text(json.dumps(out,indent=2)+'\n')
            group=[r for r in out['cases'] if (r['bearing'],r['edge'])==(j,i)]
            print('row',j,'edge',i,'passing',sum(r['passes'] for r in group),'/',len(group),flush=True)
    for j in range(2):
        feasible=[]
        choices=[[r['phi_deg'] for r in options if r['leaf']==i and r['bearing']==j and r['passes']] for i in range(4)]
        for path in itertools.product(*choices):
            if all(any(r['passes'] and (r['bearing'],r['edge'],r['phi_from'],r['phi_to'])==(j,i,path[i],path[i+1]) for r in out['cases']) for i in range(3)):
                feasible.append(path)
        out.setdefault('row_paths',{})[str(j)]=feasible
        print('row',j,'consistent paths',len(feasible),flush=True)
    (HERE/'RESULTADOS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('C20_COMPLETO',flush=True)
if __name__=='__main__':main()
