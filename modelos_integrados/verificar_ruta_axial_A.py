"""Check straight tube/sleeve intersections in the actual integrated STEP."""
from pathlib import Path
import cadquery as cq
import json,hashlib
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'aerodinamica_A'
source=ROOT/'vectorizacion_A/CAD_integracion_coherente/A_integracion_conductos_coherentes.step'
ducts=[]
for s,n,loc,_ in cq.Assembly.load(str(source)):
    if n.split('/')[-1].startswith('conducto_unificado'):ducts.append(s.moved(loc))
assert len(ducts)==4
rows=[]
for diameter in [40,42,46,50,60,80,100]:
    tube_envelope=cq.Solid.makeCylinder(diameter/2,800,cq.Vector(-400,0,0),cq.Vector(1,0,0))
    volumes=[tube_envelope.intersect(d).Volume(tol=1e-9) for d in ducts]
    total=sum(volumes)
    if diameter<=42:assert abs(total)<1e-4
    else:assert total>1e-4
    rows.append(dict(axial_outer_diameter_mm=diameter,per_sleeve_intersection_mm3=volumes,total_intersection_mm3=total))
report=dict(source_step=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),checks=rows,scope='Outer cylindrical tube envelope on x-axis, x=-400..400 mm, against four unified sleeves of the selected integration branch. Boundary contact at 42 mm is not manufacturing clearance. No engine, intake performance or routed duct is validated.',axial_installation_validated=False)
(OUT/'VERIFICACION_RUTA_AXIAL.json').write_text(json.dumps(report,indent=2));print(json.dumps(rows))
