"""Consolidate duplicate presentation sleeves and vector-module ducts.

Pure geometric correction; selected motor/rotor, tolerances and loads remain open.
"""
from pathlib import Path
import json,math,hashlib
import cadquery as cq

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'vectorizacion_A/CAD_modulo/integracion_preliminar.step'
OUT=ROOT/'vectorizacion_A/CAD_integracion_coherente';OUT.mkdir(exist_ok=True)
base=cq.Assembly.load(str(SRC));parts=[]
for s,name,loc,color in base:
    parts.append(dict(shape=s.moved(loc),name=name.split('/')[-1],color=color))
sleeves=[a for a in parts if a['name'].startswith('base_camisa_interna')]
ducts=[a for a in parts if a['name'].startswith('vector_conducto')]
rotors=[a for a in parts if a['name'].startswith('base_rotor_representativo')]
assert len(sleeves)==len(ducts)==len(rotors)==4
assembly=cq.Assembly(name='A_integracion_conductos_coherentes')
for a in parts:
    if a in sleeves or a in ducts:continue
    assembly.add(a['shape'],name=a['name'],color=a['color'] or cq.Color(.2,.2,.2))
checks=[]
for i,a in enumerate(sleeves):
    c=a['shape'].Center();x,y=c.x,c.y
    distance=lambda b:math.hypot(b['shape'].Center().x-x,b['shape'].Center().y-y)
    duct=min(ducts,key=distance);rotor=min(rotors,key=distance)
    # Lower ducts are clipped by an asymmetric hull: their volume centroid
    # is not the cylinder axis. Pair by proximity; bore/intersection checks
    # below test the resulting geometry instead of equating those centroids.
    assert distance(duct)<5 and distance(rotor)<1e-4
    bore=cq.Solid.makeCylinder(42,400,cq.Vector(x,y,-200),cq.Vector(0,0,1))
    sleeve=a['shape'].cut(bore)
    merged=sleeve.fuse(duct['shape']).clean()
    assert merged.isValid() and len(merged.Solids())==1
    radial_extent=max(math.hypot(v.Center().x-x,v.Center().y-y) for v in rotor['shape'].Vertices())
    before=a['shape'].intersect(rotor['shape']).Volume()
    after=merged.intersect(rotor['shape']).Volume()
    occupied_bore=merged.intersect(bore).Volume()
    assert after<1e-6 and occupied_bore<1e-6 and 42-radial_extent>0
    checks.append(dict(x_mm=x,y_mm=y,blade_tip_radial_extent_mm=radial_extent,bore_radius_mm=42,geometric_blade_tip_radial_gap_mm=42-radial_extent,original_sleeve_rotor_overlap_mm3=before,corrected_duct_rotor_overlap_mm3=after,solid_inside_nominal_bore_mm3=occupied_bore,duct_volume_mm3=merged.Volume(),duct_solids=len(merged.Solids())))
    assembly.add(merged,name=f'conducto_unificado_{i}',color=cq.Color(.2,.22,.25))
step=OUT/'A_integracion_conductos_coherentes.step';assembly.save(str(step))
loaded=cq.Assembly.load(str(step));valid=[s.moved(loc).isValid() for s,_,loc,_ in loaded]
assert all(valid) and len(valid)==len(parts)-4
report=dict(source_step=str(SRC),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),export_step=str(step),valid_reimported_parts=len(valid),source_parts=len(parts),checks=checks,scope='Local geometry correction: four original sleeves and four lower ducts consolidated into four single solids with 42 mm bore.',not_validated=['Running/tolerance clearance','Rotor deformation and overspeed containment','Blade aerodynamics and installed thrust','Motor bearings, fixation and transmission','Complete multi-part interference sweep','Mass, composite layup, structural or thermal adequacy','CFD installation model including rotor and grilles'])
(OUT/'VERIFICACION.json').write_text(json.dumps(report,indent=2))
(OUT/'LEEME.md').write_text('''# A: conductos geométricamente coherentes

Se consolidaron las cuatro camisas ilustrativas originales y los cuatro conductos del módulo vectorial en cuatro sólidos únicos, con taladro de radio 42 mm. La fuente y su huella están en `VERIFICACION.json`.

Las camisas originales tenían radio interior 41 mm, menor que el radio de un vértice de pala de aproximadamente 41,012 mm. El ensamblaje corregido deja una separación radial geométrica aproximada de 0,988 mm entre ese vértice y el taladro. Se comprobaron las intersecciones rotor/conducto por canal y la ausencia de material del conducto dentro del cilindro nominal. Los pares de volúmenes y los valores exactos están en `VERIFICACION.json`.

Se reimportó el STEP y se verificaron 101 piezas válidas. Validez de sólidos y ausencia de estas interferencias locales no equivalen a un ensamblaje funcional: faltan tolerancias, deformaciones, contención de rotor, fijaciones, rodamientos, servos/transmisiones, fabricación, masa, cargas y una revisión global de interferencias. La holgura geométrica no se declara suficiente para operación.

Este archivo es la nueva rama de integración para continuar los estudios. No acredita empuje, vuelo omnidireccional o velocidad máxima. Las simulaciones del conducto actuales excluyen rotor, motor y rejillas: esta corrección CAD no las convierte en simulación de la instalación completa.
''')
print(json.dumps(dict(output=str(step),valid_parts=len(valid),min_geometric_blade_gap_mm=min(a['geometric_blade_tip_radial_gap_mm'] for a in checks),max_original_overlap_mm3=max(a['original_sleeve_rotor_overlap_mm3'] for a in checks),max_corrected_overlap_mm3=max(a['corrected_duct_rotor_overlap_mm3'] for a in checks))))
