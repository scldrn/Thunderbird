from pathlib import Path
import hashlib,json
import cadquery as cq

HERE=Path(__file__).resolve().parent
path=HERE/'C15_apoyos_conceptuales.step'
items=[(n.split('/')[-1],s.moved(loc)) for s,n,loc,c in cq.Assembly.load(str(path))]
p=dict(items)
expected={'piel','camisa','rotor','aro','junta'}|{'lamina_recortada_'+str(i) for i in range(4)}|{'eje_'+str(i) for i in range(4)}|{'casquillo_'+str(i)+'_'+str(j) for i in range(4) for j in range(2)}
assert len(items)==21 and set(p)==expected and all(s.isValid() and s.Solids() for s in p.values())
records=[]
for i in range(4):
    shaft=p['eje_'+str(i)];leaf=p['lamina_recortada_'+str(i)]
    intentional=shaft.intersect(leaf).Volume()
    for j in range(2):
        bearing=p['casquillo_'+str(i)+'_'+str(j)]
        shaft_overlap=bearing.intersect(shaft).Volume()
        leaf_overlap=bearing.intersect(leaf).Volume()
        assert shaft_overlap<.001 and leaf_overlap<.001
        records.append({'leaf':i,'bearing':j,'shaft_overlap_mm3':shaft_overlap,'leaf_overlap_mm3':leaf_overlap,
                        'intentional_shaft_leaf_overlap_mm3':intentional})
report={'step_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'object_count':len(items),'checks':records,
        'scope':'local STEP validity and selected cutout overlaps; no attachment or mechanism'}
(HERE/'AUDITORIA.json').write_text(json.dumps(report,indent=2)+'\n')
print('21 valid objects; 8 selected clearances pass')
