"""Screen vertical stem concepts attached to C15 bearing surfaces."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C15_apoyos/C15_apoyos_conceptuales.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def stem(x,y,z,direction,length):
    return cq.Solid.makeCylinder(.75,length,cq.Vector(x,y,z+direction*1.75),cq.Vector(0,0,direction))

def stem_sweep(x,y,z,direction,length):
    z0=z+direction*1.75
    bottom=min(z0,z0+direction*length)
    return cq.Solid.makeCylinder(.75,length+20,cq.Vector(x,y,bottom),cq.Vector(0,0,1))

def collision(a,b):
    if not overlap(a,b):return 0.
    shape=a.intersect(b)
    if not shape.isValid():raise ValueError('invalid intersection')
    return float(shape.Volume())

def main():
    p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes'];rows=[]
    for a in axes:
        i=a['leaf'];y=a['y_mm'];z=a['z_mm']
        for j,x in enumerate((-164.,-156.)):
            bearing=p['casquillo_'+str(i)+'_'+str(j)]
            for direction in (-1,1):
                for length in (5.,10.):
                    bar=stem(x,y,z,direction,length);sweep=stem_sweep(x,y,z,direction,length)
                    row={'leaf':i,'bearing':j,'direction':direction,'length_mm':length,
                         'bearing_overlap_mm3':collision(bar,bearing),'sweep_collisions':[],
                         'leaf_rotation_collisions':[],'errors':[]}
                    fixed=[(n,p[n],sweep) for n in ('piel','camisa','rotor','aro','junta')]
                    fixed += [('lamina_relativa_'+str(k),p['lamina_recortada_'+str(k)],bar) for k in range(4)]
                    for name,other,probe in fixed:
                        try:
                            v=collision(probe,other)
                            if v>.001:row['sweep_collisions'].append({'obstacle':name,'volume_mm3':v})
                        except Exception as e:row['errors'].append({'phase':'translation','obstacle':name,'error':repr(e)})
                    bar_open=bar.translate((0,0,20))
                    for angle in (0,15,30,45,60):
                        for k in range(4):
                            t=axes[k];center=(t['x0_mm'],t['y_mm'],t['z_mm']+20)
                            leaf=p['lamina_recortada_'+str(k)].translate((0,0,20)).rotate(center,(center[0]+1,center[1],center[2]),angle)
                            try:
                                v=collision(bar_open,leaf)
                                if v>.001:row['leaf_rotation_collisions'].append({'angle_deg':angle,'leaf':k,'volume_mm3':v})
                            except Exception as e:row['errors'].append({'phase':'rotation','leaf':k,'angle_deg':angle,'error':repr(e)})
                    row['passes_sampled_local']=(row['bearing_overlap_mm3']>.001 and not row['sweep_collisions'] and not row['leaf_rotation_collisions'] and not row['errors'])
                    rows.append(row)
                    (HERE/'PARCIAL.json').write_text(json.dumps({'cases':rows},indent=2)+'\n')
                    print('leaf',i,'bearing',j,'dir',direction,'len',length,'trans',len(row['sweep_collisions']),'rot',len(row['leaf_rotation_collisions']),'errors',len(row['errors']),flush=True)
    out={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'scope':'local hypothetical stems with cylindrical swept translation and 5 rotation poses; no connection to actuator or structure', 'cases':rows}
    (HERE/'RESULTADOS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('C16_COMPLETO passing',sum(r['passes_sampled_local'] for r in rows),'/',len(rows),flush=True)

if __name__=='__main__':main()
