from pathlib import Path
import hashlib,json
import cadquery as cq
HERE=Path(__file__).resolve().parent
src=HERE.parent/'producto_C17_vastagos_radiales/C17_candidata_local.step'
dst=HERE/'C18_abierto_local.step'
def read(path):return {n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(path))}
a,b=read(src),read(dst)
assert len(a)==len(b)==29 and set(a)==set(b) and all(s.isValid() and s.Solids() for s in b.values())
for n in ('piel','camisa','rotor','aro','junta'):
    assert (a[n].Center()-b[n].Center()).Length<1e-4
for n in b:
    if n.startswith(('eje_','casquillo_','vastago_')):
        delta=b[n].Center()-a[n].Center()
        assert abs(delta.x)<1e-4 and abs(delta.y)<1e-4 and abs(delta.z-20)<1e-4
out={'step_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'objects':len(b),
     'scope':'validity and fixed/translated center position; not full equivalence or mechanical validation'}
(HERE/'AUDITORIA.json').write_text(json.dumps(out,indent=2)+'\n')
print('29 valid objects; fixed and translated centers checked')
