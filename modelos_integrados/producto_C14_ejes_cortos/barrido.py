"""Sweep short candidate shaft envelopes upward in the local C11 assembly."""
from pathlib import Path
import hashlib
import json
import math
import sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C11_laminas/C11_cerrado.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def shaft(x,y,z,r,length):
    return cq.Solid.makeCylinder(r,length,cq.Vector(x,y,z),cq.Vector(1,0,0))

def swept_shaft(x,y,z,r,length,height):
    bottom=shaft(x,y,z,r,length)
    if height==0:return bottom
    top=shaft(x,y,z+height,r,length)
    web=cq.Solid.makeBox(length,2*r,height,cq.Vector(x,y-r,z))
    s=bottom.fuse(top,web).clean()
    expected=length*(math.pi*r*r+2*r*height)
    if not s.isValid() or len(s.Solids())!=1 or abs(s.Volume()-expected)>1e-6*expected:
        raise ValueError('invalid swept shaft')
    return s

def main():
    data=json.loads(AXES.read_text());source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if source_hash!=data['source_sha256']:raise ValueError('C13 source differs')
    parts={name.split('/')[-1]:shape.moved(loc) for shape,name,loc,c in cq.Assembly.load(str(SOURCE))}
    expected={'piel','camisa','rotor','aro','junta'}|{'lamina_'+str(i) for i in range(4)}
    if set(parts)!=expected or any(not s.isValid() or not s.Solids() for s in parts.values()):raise ValueError('bad STEP')
    result={'scope':'short internal shaft envelope translation 0–20mm, local C11 geometry only; no bearings or supports',
            'source_sha256':source_hash,'axis_source_sha256':hashlib.sha256(AXES.read_bytes()).hexdigest(),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'radius_mm':1.,'length_mm':10.,'travel_mm':20.,'candidates':[]}
    for a in data['axes']:
        for center_x in (-190.,-180.,-170.,-160.,-150.,-140.,-130.):
            x=center_x-5
            if x<a['x0_mm'] or x+10>a['x1_mm']:continue
            sweep=swept_shaft(x,a['y_mm'],a['z_mm'],1.,10.,20.)
            # Other leaves translate synchronously; their relative separation
            # from this shaft is constant before rotation.
            original=shaft(x,a['y_mm'],a['z_mm'],1.,10.)
            items=[(n,parts[n],sweep) for n in ('piel','camisa','rotor','aro','junta')]
            items += [('otra_lamina_'+str(j),parts['lamina_'+str(j)],original) for j in range(4) if j!=a['leaf']]
            row={'leaf':a['leaf'],'center_x_mm':center_x,'collisions':[],'unknown':[],'checks':0,'booleans':0}
            for name,other,probe in items:
                row['checks']+=1
                if not overlap(probe,other):continue
                row['booleans']+=1
                try:
                    cross=probe.intersect(other)
                    if not cross.isValid():raise ValueError('invalid boolean')
                    volume=cross.Volume()
                    if volume>.001:row['collisions'].append({'obstacle':name,'volume_mm3':volume})
                except Exception as error:row['unknown'].append({'obstacle':name,'error':repr(error)})
            row['passes_local_sweep']=not row['collisions'] and not row['unknown']
            result['candidates'].append(row)
            (HERE/'PARCIAL.json').write_text(json.dumps(result,indent=2)+'\n')
            print('leaf',a['leaf'],'x',center_x,'collisions',len(row['collisions']),'errors',len(row['unknown']),flush=True)
    for i in range(4):
        cs=[r for r in result['candidates'] if r['leaf']==i]
        print('leaf',i,'pass',sum(r['passes_local_sweep'] for r in cs),'/',len(cs),flush=True)
    (HERE/'RESULTADOS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('C14_COMPLETO',flush=True)

if __name__=='__main__':main()
