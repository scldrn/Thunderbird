"""Check concentric invariant cutters for each own bearing/leaf pair."""
from pathlib import Path
import hashlib,json,math
import cadquery as cq
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
AXES=HERE.parent/'producto_C13_ejes_cinematicos/RESULTADOS.json'
p={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
axes=json.loads(AXES.read_text())['axes'];checks=[]
for a in axes:
    i=a['leaf'];leaf=p['lamina_recortada_'+str(i)]
    for j,x in enumerate((-165.,-157.)):
        cutter=cq.Solid.makeCylinder(2.2,2.1,cq.Vector(x-.05,a['y_mm'],a['z_mm']),cq.Vector(1,0,0))
        bearing=p[f'casquillo_{i}_{j}']
        outside=bearing.cut(cutter).Volume()
        inside_leaf=leaf.intersect(cutter).Volume()
        rotated=cutter.rotate((x,a['y_mm'],a['z_mm']),(x+1,a['y_mm'],a['z_mm']),23)
        mismatch=cutter.cut(rotated).Volume()+rotated.cut(cutter).Volume()
        assert max(outside,inside_leaf,mismatch)<.001
        checks.append({'leaf':i,'bearing':j,'bearing_outside_cut_mm3':outside,
                       'leaf_inside_cut_mm3':inside_leaf,'rotated_cutter_difference_mm3':mismatch})
out={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'checks':checks,
     'scope':'nominal cylinders and own leaves only; no tolerances, other leaves, supports or motion dynamics'}
(HERE/'ALOJAMIENTOS.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(checks),'own bearing/cavity containment checks passed')
