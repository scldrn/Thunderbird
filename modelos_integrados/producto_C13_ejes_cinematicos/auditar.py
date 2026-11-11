from pathlib import Path
import hashlib
import json
import cadquery as cq

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'producto_C11_laminas/C11_cerrado.step'
PATH=HERE/'C13_abierto_local.step'
rows=json.loads((HERE/'RESULTADOS.json').read_text())
src={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(SOURCE))}
out={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(PATH))}
assert len(out)==13 and all(s.isValid() and s.Solids() for s in out.values())
expected={'piel','camisa','rotor','aro','junta'}|{'lamina_'+str(i) for i in range(4)}|{'eje_reserva_'+str(i) for i in range(4)}
assert set(out)==expected
errors=[]
for a in rows['axes']:
    i=a['leaf'];center=(a['x0_mm'],a['y_mm'],a['z_mm']+20)
    predicted=src['lamina_'+str(i)].translate((0,0,20)).rotate(center,(center[0]+1,center[1],center[2]),60)
    error=(predicted.Center()-out['lamina_'+str(i)].Center()).Length
    assert error<1e-4
    errors.append(error)
for name in ('piel','camisa','rotor','aro','junta'):
    assert (src[name].Center()-out[name].Center()).Length<1e-4
report={'step_sha256':hashlib.sha256(PATH.read_bytes()).hexdigest(),'object_count':len(out),
        'leaf_center_errors_mm':errors,'scope':'reimport validity and center positions only; no global collision or mechanism'}
(HERE/'AUDITORIA.json').write_text(json.dumps(report,indent=2)+'\n')
print('13 valid objects; max leaf center error mm:',max(errors))
