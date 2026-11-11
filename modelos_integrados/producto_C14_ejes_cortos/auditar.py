from pathlib import Path
import hashlib
import json
import cadquery as cq

HERE=Path(__file__).resolve().parent
reports=[]
for state in ('cerrado','abierto'):
    p=HERE/('C14_'+state+'_local.step')
    items=[(name.split('/')[-1],shape.moved(loc)) for shape,name,loc,c in cq.Assembly.load(str(p))]
    names={name for name,shape in items}
    expected={'piel','camisa','rotor','aro','junta'}|{'lamina_'+str(i) for i in range(4)}|{'eje_corto_'+str(i) for i in range(4)}
    assert len(items)==13 and names==expected and all(s.isValid() and len(s.Solids())>0 for n,s in items)
    reports.append({'state':state,'object_count':len(items),'step_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(HERE/'AUDITORIA.json').write_text(json.dumps({'states':reports,'scope':'STEP object validity only'},indent=2)+'\n')
print('Both STEP files: 13 valid objects')
