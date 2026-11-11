"""Screen illustrative annular bearings and cutouts; not a mechanism."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'producto_C14_ejes_cortos'
sys.path.insert(0,str(BASE))
sys.path.insert(0,str(HERE.parent/'producto_C13_ejes_cinematicos'))
from barrido import SOURCE,AXES,shaft,swept_shaft
from cribar import overlap

def main():
    parts={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
    axes=json.loads(AXES.read_text())['axes']
    out={'scope':'illustrative bearing sleeves and local cutouts, 4 leaves, 5 fixed objects, no mounting or actuation',
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'axes_sha256':hashlib.sha256(AXES.read_bytes()).hexdigest(),
         'assumptions_mm':{'shaft_radius':1.,'sleeve_inner_radius':1.1,'sleeve_outer_radius':2.,
                           'cutout_radius':2.2,'bearing_width':2.,'travel':20.},
         'leaves':[]}
    model=cq.Assembly(name='C15_concept_not_mechanism')
    for name in ('piel','camisa','rotor','aro','junta'):model.add(parts[name],name=name)
    for a in axes:
        i=a['leaf'];y=a['y_mm'];z=a['z_mm'];leaf=parts['lamina_'+str(i)]
        bearings=[];cutters=[];row={'leaf':i,'sweep_collisions':[],'errors':[],'checks':0}
        for j,x in enumerate((-165.,-157.)):
            outer=shaft(x,y,z,2.,2.);inner=shaft(x-.1,y,z,1.1,2.2)
            bearing=outer.cut(inner)
            if not bearing.isValid() or len(bearing.Solids())!=1:raise ValueError('invalid bearing')
            cutter=shaft(x-.05,y,z,2.2,2.1)
            bearings.append(bearing);cutters.append(cutter)
            swept=swept_shaft(x,y,z,2.,2.,20.)
            original=outer
            targets=[(n,parts[n],swept) for n in ('piel','camisa','rotor','aro','junta')]
            targets += [('otra_lamina_'+str(k),parts['lamina_'+str(k)],original) for k in range(4) if k!=i]
            for name,other,probe in targets:
                row['checks']+=1
                if not overlap(probe,other):continue
                try:
                    inter=probe.intersect(other)
                    if not inter.isValid():raise ValueError('invalid boolean')
                    vol=inter.Volume()
                    if vol>.001:row['sweep_collisions'].append({'bearing':j,'obstacle':name,'volume_mm3':vol})
                except Exception as e:row['errors'].append({'bearing':j,'obstacle':name,'error':repr(e)})
        cut=leaf.cut(*cutters).clean()
        row.update({'leaf_before_mm3':leaf.Volume(),'leaf_after_mm3':cut.Volume(),
                    'removed_mm3':leaf.Volume()-cut.Volume(),'cut_valid':cut.isValid(),
                    'cut_solids':len(cut.Solids()),'local_sweep_clear':not row['sweep_collisions'] and not row['errors']})
        if not cut.isValid() or len(cut.Solids())==0:raise ValueError('invalid cut')
        model.add(cut,name='lamina_recortada_'+str(i))
        model.add(shaft(-165.,y,z,1.,10.),name='eje_'+str(i))
        for j,b in enumerate(bearings):model.add(b,name='casquillo_'+str(i)+'_'+str(j))
        out['leaves'].append(row)
        (HERE/'PARCIAL.json').write_text(json.dumps(out,indent=2)+'\n')
        print('leaf',i,'remaining solids',row['cut_solids'],'removed',round(row['removed_mm3'],3),'collisions',len(row['sweep_collisions']),'errors',len(row['errors']),flush=True)
    model.save(str(HERE/'C15_apoyos_conceptuales.step'))
    (HERE/'RESULTADOS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('C15_COMPLETO',flush=True)

if __name__=='__main__':main()
