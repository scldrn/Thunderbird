"""Screen six straight synchronization rods for local C17 candidate."""
from pathlib import Path
import hashlib,json,math,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
SELECT=HERE.parent/'producto_C17_vastagos_radiales/AUDITORIA.json'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from cribar import overlap

def volume(a,b):
    if not overlap(a,b):return 0.
    c=a.intersect(b)
    if not c.isValid():raise ValueError('invalid boolean')
    return float(c.Volume())

def main():
    parts={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes'];sel=json.loads(SELECT.read_text())['selected']
    lookup={(r['leaf'],r['bearing']):r for r in sel};out=[]
    for bearing in range(2):
        for i in range(3):
            ends=[]
            for k in (i,i+1):
                a=axes[k];phi=math.radians(lookup[k,bearing]['phi_deg']);x=(-164.,-156.)[bearing]
                ends.append(cq.Vector(x,a['y_mm']+6.5*math.cos(phi),a['z_mm']+6.5*math.sin(phi)))
            vec=ends[1]-ends[0]
            rod=cq.Solid.makeCylinder(.5,vec.Length,ends[0],vec.normalized())
            row={'bearing':bearing,'from_leaf':i,'to_leaf':i+1,'length_mm':vec.Length,
                 'endpoint_overlap_mm3':[],'lift_collisions':[],'rotation_collisions':[],'errors':[]}
            for k in (i,i+1):row['endpoint_overlap_mm3'].append(volume(rod,parts[f'vastago_{k}_{bearing}']))
            for h in (0,5,10,15,20):
                for name in ('piel','camisa','rotor','aro','junta'):
                    try:
                        v=volume(rod.translate((0,0,h)),parts[name])
                        if v>.001:row['lift_collisions'].append({'lift_mm':h,'object':name,'volume_mm3':v})
                    except Exception as e:row['errors'].append({'phase':'lift','error':repr(e)})
            for angle in (0,15,30,45,60):
                for a in axes:
                    k=a['leaf'];c=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
                    leaf=parts[f'lamina_recortada_{k}'].translate((0,0,20)).rotate(c,(c[0]+1,c[1],c[2]),angle)
                    try:
                        v=volume(rod.translate((0,0,20)),leaf)
                        if v>.001:row['rotation_collisions'].append({'angle_deg':angle,'leaf':k,'volume_mm3':v})
                    except Exception as e:row['errors'].append({'phase':'rotation','error':repr(e)})
            others=[n for n in parts if n.startswith(('eje_','casquillo_','vastago_')) and n not in (f'vastago_{i}_{bearing}',f'vastago_{i+1}_{bearing}')]
            row['other_component_collisions']=[]
            for name in others:
                try:
                    v=volume(rod,parts[name])
                    if v>.001:row['other_component_collisions'].append({'object':name,'volume_mm3':v})
                except Exception as e:row['errors'].append({'phase':'component','error':repr(e)})
            row['passes_sampled_local']=all(v>.001 for v in row['endpoint_overlap_mm3']) and not any(row[k] for k in ('lift_collisions','rotation_collisions','other_component_collisions','errors'))
            out.append(row)
            (HERE/'PARCIAL.json').write_text(json.dumps({'cases':out},indent=2)+'\n')
            print('bearing',bearing,'link',i,'connected',all(v>.001 for v in row['endpoint_overlap_mm3']), 'lift',len(row['lift_collisions']),'rotation',len(row['rotation_collisions']),'other',len(row['other_component_collisions']),'errors',len(row['errors']),flush=True)
    result={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'six straight 1mm diameter connecting rods, local sampled poses only, not mechanism', 'cases':out}
    (HERE/'RESULTADOS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('C19_COMPLETO',flush=True)

if __name__=='__main__':main()
