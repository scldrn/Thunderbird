from pathlib import Path
import cadquery as cq,json
p=Path(__file__).resolve().parent
outer=cq.importers.importStep(str(p/'envolvente.step')).val().Solids()[0]
rows=[]
for s,n,loc,c in cq.Assembly.load(str(p/'5kg/A06_integrado.step')):
 n=n.split('/')[-1]
 if 'base_rotor_' in n:
  s=s.moved(loc);outside=s.cut(outer).Volume();rows.append(dict(part=n,volume_outside_hull_mm3=outside));assert outside<1e-4
assert len(rows)==4
(p/'VERIFICACION_ROTORES_INTERNOS.json').write_text(json.dumps(dict(reference='5kg, shared geometrical scaling for 2 and 10kg',results=rows,scope='Static representative rotor geometry inside reference envelope; not blade deformation, swept tolerances, duct performance or safety clearance validation.'),indent=2))
print(rows)
