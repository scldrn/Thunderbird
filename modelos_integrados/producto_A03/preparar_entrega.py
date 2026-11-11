from pathlib import Path
import json,csv,zipfile,hashlib,argparse
import cadquery as cq
from cadquery.occ_impl.exporters.assembly import exportGLTF
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--skip-glb',action='store_true');args=parser.parse_args()
audit=json.loads((ROOT/'VERIFICACION.json').read_text())
sizes=[]
for mass in (2,5,10):
 folder=ROOT/f'{mass}kg';m=json.loads((folder/'manifest.json').read_text());sizes.append(m)
 if not args.skip_glb:
  asm=cq.Assembly.load(str(folder/'A03_integrado.step'))
  exportGLTF(asm,str(folder/'A03_integrado.glb'),binary=True,tolerance=.3,angularTolerance=.15)
 else:assert (folder/'A03_integrado.glb').exists()
 with (folder/'lista_piezas.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['pieza','alcance','volumen_geometrico_mm3','dimension_x_mm','dimension_y_mm','dimension_z_mm'])
  for p in m['parts']:w.writerow([p['name'],p['scope'],p['volume_mm3'],*p['bbox_mm']])
 print('GLB/BOM',mass,flush=True)
with (ROOT/'dimensiones.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['masa_objetivo_kg_no_verificada','longitud_conjunto_mm','anchura_conjunto_mm','altura_conjunto_mm','taladro_ventilador_mm','interfaz_axial_exterior_mm'])
 for m in sizes:w.writerow([m['target_mass_kg'],*m['assembly_dimensions_mm'],m['fan_bore_mm'],m['axial_outer_mm']])
lines=['# A03 · Plataforma deportiva integrada','','Revisión CAD de presentación de producto, derivada de la arquitectura A y del diseño industrial aprobado. Es geometría tridimensional editable, no una imagen generada por IA. La apariencia se presenta como producto; el dimensionamiento funcional continúa en desarrollo.','','## Entrega','','- `2kg/`, `5kg/`, `10kg/`: conjuntos STEP coloreados, corte de inspección STEP, exterior STL, visor GLB y lista de piezas CSV. Las masas son objetivos, no masas cerradas o pesadas.','- `crear_A03.py`: construcción paramétrica en CadQuery, con 5 kg como escala de referencia.','- `render_A03.py`: trazado de rayos desde los STEP exportados mediante Mitsuba.','- `VERIFICACION.json` y manifiestos: comprobaciones geométricas y medidas del conjunto.','','## Dimensiones del CAD exportado','','| Escala objetivo | Longitud | Anchura | Altura | Paso de ventilador | Interfaz axial exterior |','|---|---:|---:|---:|---:|---:|']
for m in sizes:
 l,w,h=m['assembly_dimensions_mm'];lines.append(f"| {m['target_mass_kg']:g} kg | {l:.1f} mm | {w:.1f} mm | {h:.1f} mm | {m['fan_bore_mm']:.1f} mm | {m['axial_outer_mm']:.1f} mm |")
lines += ['','## Cambios integrados','','Se mantiene la carrocería facetada y deportiva en grafito/cobre. Se propone para esta revisión la distribución intermedia estudiada: centros x=±200 mm, y=±76 mm en la escala de 5 kg, con reserva axial exterior de 60 mm. Es una propuesta equilibrada de empaquetado, no una demostración de óptimo global ni sustitución de la arquitectura A seleccionada.','','Los cuatro módulos giratorios quedan dentro del cuerpo y las ocho cubiertas siguen la superficie exterior en la pose cerrada de avance. Se conservan los bancos de álabes superior/inferior y sus ejes, se perforan sus pasos en las camisas y se añaden alojamientos de actuación fuera del flujo principal. El tubo central vacío tiene diámetro exterior de 60 mm e interior de 56 mm en la referencia; no representa un motor. La interfaz posterior tampoco es una tobera dimensionada.','','La estructura visible incorpora cuadernas y apoyos del canal axial. La piel se construye con un loft interior desplazado 1 mm en las secciones transversales: no es una pared de espesor normal uniforme ni un laminado dimensionado. El espesor, los refuerzos y sus uniones requieren cálculo estructural y cierre de masa. No se han trasladado inercias o tiempos de giro de carcasas anteriores a este nuevo conjunto.','','Las cubiertas de sensores, paneles laterales, tornillería, juntas de panel y aros son piezas separadas. Las superficies principales tienen recortes para los insertos; el render no usa piezas superpuestas para simular cambios de color.','','## Alcance mecánico y verificación','','Los STEP se reimportan y se verifica que todas las piezas son geométricamente válidas. Se comprueba la contención del loft interior, alojamientos de actuador, paso axial y apoyos, así como la ausencia de volumen de intersección de ejes con los conductos perforados en los casos locales evaluados. Estas comprobaciones no constituyen una revisión global de todas las interferencias, tolerancias o cargas.','','El corte de inspección retira la cubierta superior y secciona parcialmente dos camisas para que se vea el interior. No es una pose operativa de las compuertas. La cinemática de apertura/retracción, transmisiones, cojinetes/sellos y el rotor reversible siguen por desarrollar. Los rotores/motores procedentes del estudio anterior son representativos; no se presentan como componentes funcionales seleccionados.','','Los ensayos CFD y las asignaciones ideales de fuerza no validan todavía el mapa instalado, el arrastre total, la velocidad de 600–1000 km/h ni el vuelo autónomo. El CAD conserva esa distinción: se integran hallazgos de espacio y protección, sin convertir hipótesis de fuerza o material en prestaciones demostradas.','','## Abrir y modificar','','Los STEP pueden abrirse en FreeCAD, Fusion, SolidWorks, Onshape u otro modelador compatible. Los GLB sirven para inspección/presentación, no sustituyen las superficies editables STEP. Los STL contienen solo el exterior para visualización y no son instrucciones de fabricación. Para regenerar con el entorno existente: `.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/producto_A03/crear_A03.py`. No se necesita instalar software adicional para esta entrega.']
(ROOT/'LEEME.md').write_text('\n'.join(lines)+'\n')
files=[]
for folder in [ROOT/f'{m}kg' for m in (2,5,10)]:files.extend(p for p in folder.iterdir() if p.suffix in ('.step','.stl','.glb','.csv','.json'))
files += [ROOT/n for n in ['LEEME.md','VERIFICACION.json','dimensiones.csv','crear_A03.py','render_A03.py','preparar_entrega.py']]
files.extend(ROOT.glob('A03_*kg_*.png'));files.extend(ROOT.glob('render_*kg_*.json'))
files.extend((ROOT/'referencias').glob('*'))
if (ROOT/'REVISION_ENTREGA.json').exists():files.append(ROOT/'REVISION_ENTREGA.json')
with zipfile.ZipFile(ROOT/'A03_CAD_y_presentacion.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(ROOT))
(ROOT/'ENTREGA.json').write_text(json.dumps(dict(part_count_per_scale=audit['parts'],files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files],physical_validation=False),indent=2))
print('DELIVERY_READY',flush=True)
