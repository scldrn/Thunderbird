"""Screen spherical joint reservations at shared stems of C21 row 0."""
from pathlib import Path
import hashlib,itertools,json,math,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
SELECT=HERE.parent/'producto_C17_vastagos_radiales/AUDITORIA.json'
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def ball(radius,center):
    s=cq.Solid.makeSphere(radius,center,angleDegrees1=-90,angleDegrees2=90)
    if abs(s.Volume()-4*math.pi*radius**3/3)>1e-6:raise ValueError('not a full sphere')
    return s

def vol(a,b):
    if not overlap(a,b):return 0.
    c=a.intersect(b)
    if not c.isValid():raise ValueError('invalid boolean')
    return float(c.Volume())

def main():
    p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes'];sel=json.loads(SELECT.read_text())['selected'];phi={(r['leaf'],r['bearing']):r['phi_deg'] for r in sel}
    leaves={}
    for angle,a in itertools.product((0,15,30,45,60),axes):
        c=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
        leaves[angle,a['leaf']]=p['lamina_recortada_'+str(a['leaf'])].translate((0,0,20)).rotate(c,(c[0]+1,c[1],c[2]),angle)
    rows=[]
    for i,radius in itertools.product((1,2),(.75,1.,1.5)):
        a=axes[i];t=math.radians(phi[i,0]);center=cq.Vector(-164,a['y_mm']+6.5*math.cos(t),a['z_mm']+6.5*math.sin(t))
        sphere=ball(radius,center)
        row={'leaf':i,'bearing':0,'radius_mm':radius,'center_mm':center.toTuple(),
             'intentional_stem_overlap_mm3':None,'first_collision':None,'checks':0,'error':None,'passes':False}
        try:
            row['intentional_stem_overlap_mm3']=vol(sphere,p[f'vastago_{i}_0'])
            if row['intentional_stem_overlap_mm3']<=.001:raise ValueError('missing intended stem connection')
            for angle,k in itertools.product((60,0,45,30,15),range(4)):
                row['checks']+=1;v=vol(sphere.translate((0,0,20)),leaves[angle,k])
                if v>.001:row['first_collision']={'phase':'rotation','angle_deg':angle,'leaf':k,'volume_mm3':v};break
            if row['first_collision'] is None:
                for h,n in itertools.product((0,5,10,15,20),('piel','camisa','rotor','aro','junta')):
                    row['checks']+=1;v=vol(sphere.translate((0,0,h)),p[n])
                    if v>.001:row['first_collision']={'phase':'lift','lift_mm':h,'object':n,'volume_mm3':v};break
            if row['first_collision'] is None:
                for n in [name for name in p if name.startswith(('eje_','casquillo_','vastago_')) and name!=f'vastago_{i}_0']:
                    row['checks']+=1;v=vol(sphere,p[n])
                    if v>.001:row['first_collision']={'phase':'component','object':n,'volume_mm3':v};break
            row['passes']=row['first_collision'] is None
        except Exception as e:row['error']=repr(e)
        rows.append(row);(HERE/'PARCIAL.json').write_text(json.dumps({'cases':rows},indent=2)+'\n')
        print('node',i,'radius',radius,'pass',row['passes'],'collision',row['first_collision'],'error',row['error'],flush=True)
    out={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'scope':'shared stem nodes row 0 only; first collision, sampled poses; no joint design','cases':rows}
    (HERE/'RESULTADOS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('C22_COMPLETO',flush=True)
if __name__=='__main__':main()
