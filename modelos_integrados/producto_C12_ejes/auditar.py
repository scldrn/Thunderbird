from pathlib import Path
import hashlib
import json
import cadquery as cq

HERE=Path(__file__).resolve().parent
path=HERE/'C12_reservas_ejes_elevados.step'
model=cq.Assembly.load(str(path))
objects=[{'name':name.split('/')[-1],'valid':shape.isValid(),
          'solids':len(shape.Solids()),'volume_mm3':shape.Volume()}
         for shape,name,loc,color in model]
assert len(objects)==9 and all(o['valid'] and o['solids']>0 and o['volume_mm3']>0 for o in objects)
assert {o['name'] for o in objects}=={'piel','camisa','rotor','aro','junta','probe_0','probe_1','probe_2','probe_3'}
out={'step_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':objects,
     'scope':'STEP reimport and validity only; no mechanical or global collision validation'}
(HERE/'AUDITORIA.json').write_text(json.dumps(out,indent=2)+'\n')
print('9 solids checked; SHA-256',out['step_sha256'])
