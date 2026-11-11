"""Sample C11-like axis envelopes through lift and synchronized tilt.

Local 9-part STEP only; hypothetical unsupported cylinders, not a mechanism.
"""
from pathlib import Path
import hashlib
import json
import cadquery as cq

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C11_laminas/C11_cerrado.step'
FIXED=('piel','camisa','rotor','aro','junta')
STATES=[(h,0.) for h in (0.,2.,5.,10.,15.,20.)]+[(20.,a) for a in (15.,30.,45.,60.)]

def overlap(a,b,tol=.01):
    a=a.BoundingBox();b=b.BoundingBox()
    return not (a.xmax+tol<b.xmin or b.xmax+tol<a.xmin or a.ymax+tol<b.ymin or b.ymax+tol<a.ymin or a.zmax+tol<b.zmin or b.zmax+tol<a.zmin)

def main():
    assembly=cq.Assembly.load(str(SOURCE))
    parts={name.split('/')[-1]:shape.moved(loc) for shape,name,loc,color in assembly}
    expected=set(FIXED)|{'lamina_'+str(i) for i in range(4)}
    if set(parts)!=expected or any(not s.isValid() or not s.Solids() for s in parts.values()):raise ValueError('bad STEP')
    axes=[]
    for i in range(4):
        shape=parts['lamina_'+str(i)];bb=shape.BoundingBox();y=(bb.ymin+bb.ymax)/2
        line=cq.Edge.makeLine(cq.Vector(-160,y,0),cq.Vector(-160,y,180))
        zs=sorted(v.Z for v in shape.intersect(line).Vertices())
        if len(zs)<2:raise ValueError('cannot reconstruct axis '+str(i))
        axes.append({'leaf':i,'x0_mm':bb.xmin,'x1_mm':bb.xmax,'y_mm':y,'z_mm':(zs[0]+zs[-1])/2,'intersections_z_mm':zs})
    res={'scope':'C11 local STEP; reconstructed axes; ideal cylinders and sampled poses, not full vehicle or mechanism',
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'radius_mm':1.,
         'axes':axes,'states':[]}
    for lift,angle in STATES:
        leaves=[]; shafts=[]
        for a in axes:
            center=(a['x0_mm'],a['y_mm'],a['z_mm']+lift)
            leaf=parts['lamina_'+str(a['leaf'])].translate((0,0,lift)).rotate(center,(center[0]+1,center[1],center[2]),angle)
            shaft=cq.Solid.makeCylinder(1.,a['x1_mm']-a['x0_mm'],cq.Vector(*center),cq.Vector(1,0,0))
            if not leaf.isValid() or not shaft.isValid():raise ValueError('invalid pose')
            leaves.append(leaf);shafts.append(shaft)
        state={'lift_mm':lift,'angle_deg':angle,'checked':0,'booleans':0,'collisions':[],'errors':[]}
        for i,shaft in enumerate(shafts):
            items=[(n,parts[n]) for n in FIXED]+[('otra_lamina_'+str(j),leaves[j]) for j in range(4) if j!=i]+[('otro_eje_'+str(j),shafts[j]) for j in range(i+1,4)]
            for name,obstacle in items:
                state['checked']+=1
                if not overlap(shaft,obstacle):continue
                state['booleans']+=1
                try:
                    cross=shaft.intersect(obstacle)
                    if not cross.isValid():raise ValueError('invalid boolean')
                    volume=cross.Volume()
                    if volume>1e-3:state['collisions'].append({'axis':i,'obstacle':name,'intersection_mm3':volume})
                except Exception as e:state['errors'].append({'axis':i,'obstacle':name,'error':repr(e)})
        state['screened_ok']=not state['collisions'] and not state['errors']
        res['states'].append(state)
        (HERE/'PARCIAL.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
        print('pose',lift,angle,'checks',state['checked'],'booleans',state['booleans'],'collisions',len(state['collisions']),'errors',len(state['errors']),flush=True)
        if lift==20. and angle==60.:
            model=cq.Assembly(name='C13_local_not_mechanism')
            for n in FIXED:model.add(parts[n],name=n)
            for i in range(4):model.add(leaves[i],name='lamina_'+str(i));model.add(shafts[i],name='eje_reserva_'+str(i))
            model.save(str(HERE/'C13_abierto_local.step'))
    (HERE/'RESULTADOS.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
    print('C13_COMPLETO',flush=True)

if __name__=='__main__':main()
