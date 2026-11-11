"""Probe straight shaft envelopes against a local C11 STEP, not a mechanism."""
from pathlib import Path
import hashlib
import json
import cadquery as cq

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C11_laminas/C11_cerrado.step'
fixed_names=('piel','camisa','rotor','aro','junta')

def main():
    assembly=cq.Assembly.load(str(SOURCE))
    parts={name.split('/')[-1]:shape.moved(loc) for shape,name,loc,color in assembly}
    expected=set(fixed_names)|{'lamina_'+str(i) for i in range(4)}
    if set(parts)!=expected:raise ValueError('unexpected STEP parts: '+str(set(parts)))
    if any(not s.isValid() or not s.Solids() for s in parts.values()):raise ValueError('invalid STEP solids')
    axes=[]
    for i in range(4):
        bb=parts['lamina_'+str(i)].BoundingBox()
        axes.append({'leaf':i,'x0_mm':bb.xmin,'x1_mm':bb.xmax,'y_mm':(bb.ymin+bb.ymax)/2,
                     'z_mm':(bb.zmin+bb.zmax)/2})
    rows=[]
    for lift in (0.,20.):
        for radius in (1.,2.):
            probes=[]; row={'lift_mm':lift,'radius_mm':radius,'collisions':[],'unknowns':[]}
            for a in axes:
                probe=cq.Solid.makeCylinder(radius,a['x1_mm']-a['x0_mm'],
                    cq.Vector(a['x0_mm'],a['y_mm'],a['z_mm']+lift),cq.Vector(1,0,0))
                if not probe.isValid():raise ValueError('invalid probe')
                probes.append(probe)
                for name in fixed_names:
                    try:
                        volume=probe.intersect(parts[name]).Volume()
                        if volume>1e-3:row['collisions'].append({'leaf':a['leaf'],'obstacle':name,'intersection_mm3':volume})
                    except Exception as error:
                        row['unknowns'].append({'leaf':a['leaf'],'obstacle':name,'error':repr(error)})
            for i in range(4):
                for j in range(i+1,4):
                    try:
                        volume=probes[i].intersect(probes[j]).Volume()
                        if volume>1e-3:row['collisions'].append({'leaf':i,'obstacle':'probe_'+str(j),'intersection_mm3':volume})
                    except Exception as error:row['unknowns'].append({'leaf':i,'obstacle':'probe_'+str(j),'error':repr(error)})
            row['screened_ok']=not row['collisions'] and not row['unknowns']
            rows.append(row)
            if lift==20 and radius==1:
                model=cq.Assembly(name='C12_probe_not_mechanism')
                for n in fixed_names:model.add(parts[n],name=n)
                for i,probe in enumerate(probes):model.add(probe,name='probe_'+str(i))
                model.save(str(HERE/'C12_reservas_ejes_elevados.step'))
            print('lift',lift,'radius',radius,'collisions',len(row['collisions']),'unknown',len(row['unknowns']),flush=True)
    result={'scope':'C11 reduced 9-part STEP, hypothetical shaft envelopes; no mechanism or continuous sweep',
            'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'axes':axes,'rows':rows,'excluded':'associated leaf intentionally; other moving leaves and all missing C03 objects are not checked'}
    (HERE/'RESULTADOS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':main()
