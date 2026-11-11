"""Create local closed/open CAD with four candidate short shaft probes."""
from pathlib import Path
import hashlib
import json
import sys
import cadquery as cq
from barrido import SOURCE,AXES,shaft

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def main():
    candidates=json.loads((HERE/'RESULTADOS.json').read_text())
    if any(not next(r for r in candidates['candidates'] if r['leaf']==i and r['center_x_mm']==-160)['passes_local_sweep'] for i in range(4)):
        raise ValueError('selected probes failed local vertical sweep')
    axes=json.loads(AXES.read_text())['axes']
    parts={name.split('/')[-1]:shape.moved(loc) for shape,name,loc,c in cq.Assembly.load(str(SOURCE))}
    states=[]
    for angle in (0,15,30,45,60):
        leaves=[];probes=[]
        for a in axes:
            pivot=(-165.,a['y_mm'],a['z_mm']+20.)
            leaves.append(parts['lamina_'+str(a['leaf'])].translate((0,0,20)).rotate(pivot,(-164.,pivot[1],pivot[2]),angle))
            probes.append(shaft(-165.,a['y_mm'],a['z_mm']+20,1.,10.))
        state={'angle_deg':angle,'checked_pairs':0,'collisions':[],'errors':[]}
        for i,probe in enumerate(probes):
            for j,other in enumerate(leaves):
                if i==j:continue
                state['checked_pairs']+=1
                if not overlap(probe,other):continue
                try:
                    c=probe.intersect(other)
                    if not c.isValid():raise ValueError('invalid common')
                    if c.Volume()>.001:state['collisions'].append({'shaft':i,'other_leaf':j,'volume_mm3':c.Volume()})
                except Exception as e:state['errors'].append(repr(e))
        states.append(state)
        print('angle',angle,'collisions',len(state['collisions']),'errors',len(state['errors']),flush=True)
    for state in ('cerrado','abierto'):
        model=cq.Assembly(name='C14_LOCAL_NOT_MECHANISM')
        for n in ('piel','camisa','rotor','aro','junta'):model.add(parts[n],name=n)
        for a in axes:
            i=a['leaf'];lift=20 if state=='abierto' else 0;angle=60 if state=='abierto' else 0
            pivot=(-165.,a['y_mm'],a['z_mm']+lift)
            leaf=parts['lamina_'+str(i)].translate((0,0,lift)).rotate(pivot,(-164.,pivot[1],pivot[2]),angle)
            model.add(leaf,name='lamina_'+str(i))
            model.add(shaft(-165.,a['y_mm'],a['z_mm']+lift,1.,10.),name='eje_corto_'+str(i))
        model.save(str(HERE/('C14_'+state+'_local.step')))
    out={'scope':'local poses, short shaft probes, not a bearing or mechanism; only sampled angles',
         'source_results_sha256':hashlib.sha256((HERE/'RESULTADOS.json').read_bytes()).hexdigest(),'rotation_checks':states}
    (HERE/'POSES.json').write_text(json.dumps(out,indent=2)+'\n')
    print('C14_POSES_COMPLETO',flush=True)

if __name__=='__main__':main()
