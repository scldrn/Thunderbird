"""Sample radial stem directions for C15; no continuous sweep claimed."""
from pathlib import Path
import hashlib,itertools,json,math,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C15_apoyos/C15_apoyos_conceptuales.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def make_stem(x,y,z,phi_deg):
    t=math.radians(phi_deg);dy=math.cos(t);dz=math.sin(t)
    return cq.Solid.makeCylinder(.75,5.,cq.Vector(x,y+1.75*dy,z+1.75*dz),cq.Vector(0,dy,dz))

def volume(a,b):
    if not overlap(a,b):return 0.
    x=a.intersect(b)
    if not x.isValid():raise ValueError('invalid intersection')
    return float(x.Volume())

def main():
    p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes']; rotations={}
    for angle in (0,15,30,45,60):
        for a in axes:
            center=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
            rotations[angle,a['leaf']]=p['lamina_recortada_'+str(a['leaf'])].translate((0,0,20)).rotate(center,(center[0]+1,center[1],center[2]),angle)
    data={'scope':'radial stems, local C15 assembly, sampled translation and rotation; no functional mechanism',
          'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'candidate_phi_deg':list(range(0,360,45)), 'lift_samples_mm':[0,5,10,15,20],
          'rotation_samples_deg':[0,15,30,45,60], 'cases':[]}
    for a in axes:
        i=a['leaf'];y=a['y_mm'];z=a['z_mm']
        for j,x in enumerate((-164.,-156.)):
            for phi in range(0,360,45):
                bar=make_stem(x,y,z,phi);openbar=bar.translate((0,0,20))
                row={'leaf':i,'bearing':j,'phi_deg':phi,'first_collision':None,'error':None,
                     'rotation_checks':0,'lift_checks':0,'bearing_overlap_mm3':None,'passes':False}
                try:
                    row['bearing_overlap_mm3']=volume(bar,p['casquillo_'+str(i)+'_'+str(j)])
                    if row['bearing_overlap_mm3']<=.001:raise ValueError('does not overlap bearing')
                    for angle,k in itertools.product((0,15,30,45,60),(i,)+tuple(n for n in range(4) if n!=i)):
                        row['rotation_checks']+=1;v=volume(openbar,rotations[angle,k])
                        if v>.001:
                            row['first_collision']={'phase':'rotation','angle_deg':angle,'leaf':k,'volume_mm3':v};break
                    if row['first_collision'] is None:
                        for h,name in itertools.product((0,5,10,15,20),('piel','camisa','rotor','aro','junta')):
                            row['lift_checks']+=1;v=volume(bar.translate((0,0,h)),p[name])
                            if v>.001:
                                row['first_collision']={'phase':'lift','lift_mm':h,'obstacle':name,'volume_mm3':v};break
                    row['passes']=row['first_collision'] is None
                except Exception as e:row['error']=repr(e);row['passes']=False
                data['cases'].append(row)
            (HERE/'PARCIAL.json').write_text(json.dumps(data,indent=2)+'\n')
            group=[r for r in data['cases'] if r['leaf']==i and r['bearing']==j]
            print('leaf',i,'bearing',j,'passing',sum(r['passes'] for r in group),'/',len(group),flush=True)
    (HERE/'RESULTADOS.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print('C17_COMPLETO',flush=True)

if __name__=='__main__':main()
