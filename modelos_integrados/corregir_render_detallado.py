from pathlib import Path
import sys
source=Path(__file__).with_name('cad_protegidos_detallados.py')
exec(compile(source.read_text().split('outer=hull(1.4,.42);shell=')[0],str(source),'exec'))
variants={
 'A_internos_detallado':('A / Integración interna','Conductos internos · rejillas · compuertas y bisagras representativas'),
 'B_retractil_guardado_detallado':('B / Casetes retráctiles','Guardados · guías telescópicas · tapas y cierres representativos'),
 'B_retractil_desplegado_detallado':('B / Casetes retráctiles','Desplegados · guías telescópicas · tapas y cierres representativos'),
 'C_conductos_detallado':('C / Conductos integrados al exterior','Labios redondeados · rejillas · soportes cortos y fijaciones')}
for name in sys.argv[1:]:
 ass=cq.Assembly.load(str(OUT/(name+'.step')));parts=[]
 for shape,label,loc,color in ass:
  label=label.split('/')[-1].rsplit('_',1)[0]
  shape=shape.moved(loc);loc=cq.Location()
  if label=='panel_acceso':shape=shape.translate((0,0,214-shape.BoundingBox().zmax))
  if label=='tornillo_panel':
   cc=shape.Center();target_z=210*np.sqrt(max(0,1-(cc.x/700)**2-(cc.y/210)**2))+6.5
   shape=shape.translate((0,0,target_z-shape.BoundingBox().zmax))
  parts.append((label,shape.moved(loc),tuple(color.toTuple()[:3]) if color else (DARK if any(k in label for k in ['pala','motor','cierre','guia_interior','junta_central']) else BLUE if any(k in label for k in ['panel_acceso','compuerta_abatida','tapa_casete','sujecion_corta']) else COPPER if label=='banda_motor' else METAL)))
 export(name,parts,*variants[name])
