"""Sample C17 bearing/leaf interaction and export its local open pose."""
from pathlib import Path
import hashlib,json
import cadquery as cq

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'

def box_overlap(a,b,t=.01):
    a=a.BoundingBox();b=b.BoundingBox()
    return not (a.xmax+t<b.xmin or b.xmax+t<a.xmin or a.ymax+t<b.ymin or b.ymax+t<a.ymin or a.zmax+t<b.zmin or b.zmax+t<a.zmin)

def main():
    p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    if len(p)!=29 or any(not s.isValid() or not s.Solids() for s in p.values()):raise ValueError('invalid source')
    axes=json.loads(AXES.read_text())['axes'];states=[]
    for angle in (0,15,30,45,60):
        state={'angle_deg':angle,'checks':0,'booleans':0,'collisions':[],'errors':[]}
        for a in axes:
            i=a['leaf'];c=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
            leaf=p['lamina_recortada_'+str(i)].translate((0,0,20)).rotate(c,(c[0]+1,c[1],c[2]),angle)
            for j in range(4):
                for k in range(2):
                    state['checks']+=1;bearing=p[f'casquillo_{j}_{k}'].translate((0,0,20))
                    if not box_overlap(leaf,bearing):continue
                    state['booleans']+=1
                    try:
                        cross=leaf.intersect(bearing)
                        if not cross.isValid():raise ValueError('invalid boolean')
                        v=cross.Volume()
                        if v>.001:state['collisions'].append({'leaf':i,'bearing':[j,k],'volume_mm3':v})
                    except Exception as e:state['errors'].append({'leaf':i,'bearing':[j,k],'error':repr(e)})
        states.append(state)
        (HERE/'PARCIAL.json').write_text(json.dumps({'states':states},indent=2)+'\n')
        print('angle',angle,'checked',state['checks'],'booleans',state['booleans'],'collisions',len(state['collisions']),'errors',len(state['errors']),flush=True)
    model=cq.Assembly(name='C18_OPEN_LOCAL_NOT_MECHANISM')
    for name,s in p.items():
        if name.startswith('lamina_recortada_'):
            i=int(name.rsplit('_',1)[-1]);a=axes[i];c=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
            s=s.translate((0,0,20)).rotate(c,(c[0]+1,c[1],c[2]),60)
        elif name.startswith(('eje_','casquillo_','vastago_')):s=s.translate((0,0,20))
        model.add(s,name=name)
    model.save(str(HERE/'C18_abierto_local.step'))
    result={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'axes_sha256':hashlib.sha256(AXES.read_bytes()).hexdigest(),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'local C17 raised 20 mm, 5 sampled angles; bearings versus leaves only', 'states':states}
    (HERE/'RESULTADOS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('C18_COMPLETO',flush=True)
if __name__=='__main__':main()
