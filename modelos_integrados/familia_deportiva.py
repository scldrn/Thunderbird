"""Sports-product industrial design family; CAD styling and packaging study."""
from pathlib import Path
source=Path(__file__).with_name('diseno_industrial_v2.py').read_text()
exec(compile(source.split('# Recessed fan ports')[0],str(Path(__file__)),'exec'))
BASEBODY=body
OUT=ROOT/'familia_deportiva';OUT.mkdir(exist_ok=True)
BODYDETAILS='# Dorsal recessed insert'+source.split('# Dorsal recessed insert')[1].split("ass=cq.Assembly")[0]
# Reuse same studio and camera as the approved design, with variant-specific titles.
RENDER=source.split('groups={}')[1].split("(OUT/'LEEME.md')")[0]
RENDER='groups={}'+RENDER
RENDER=RENDER.replace("'ESTUDIO DE DISEÑO / 02'","'FAMILIA DEPORTIVA / DISEÑO INDUSTRIAL'").replace("'Integración compacta'",'TITLE').replace('spp=64','spp=96')
results=[]
def sports_fan(p,R):
 p=np.array(p,float);n=np.array([0.,0.,1.])
 add('conducto',ring(p,n,R+5,4,30),GRAPH)
 add('labio_superior',cq.Solid.makeTorus(R+2,1.5,cq.Vector(*(p+16*n)),cq.Vector(*n)),METAL)
 add('filete_cobrizo',ring(p+14*n,n,R+5,.8,1),ACCENT)
 add('motor',cyl(p,n,12,20),BLACK);add('buje',cyl(p+12*n,n,10,5),METAL)
 blades=[]
 for a in np.arange(7)*2*np.pi/7:
  radial=np.array([np.cos(a),np.sin(a),0]);tangent=np.cross(n,radial)
  pts=[p+8*n+12*radial-3*tangent,p+8*n+(R-4)*radial-6*tangent,p+8*n+(R-3)*radial+1*tangent,p+8*n+14*radial+5*tangent]
  w=cq.Wire.makePolygon([cq.Vector(*v) for v in pts]+[cq.Vector(*pts[0])]);blades.append(cq.Solid.extrudeLinear(w,[],cq.Vector(0,0,1.7)))
 add('palas_representativas',cq.Compound.makeCompound(blades),BLACK)
 add('rejilla_anular',cq.Solid.makeTorus(R*.65,.9,cq.Vector(*(p+20*n)),cq.Vector(*n)),METAL)
 for a in [0,np.pi/3,2*np.pi/3]:
  v=np.array([np.cos(a),np.sin(a),0]);add('nervio_rejilla',beam(p+20*n-(R-1)*v,p+20*n+(R-1)*v,.8),METAL)
def finish_body(body):
 upper=body.intersect(box([0,0,160],[1600,700,180]));lower=body.cut(box([0,0,160.3],[1600,700,180]))
 for name,shape,col in [('cubierta_superior',upper,TOP),('cuerpo_principal',lower,GRAPH)]:add(name,shape.cut(box([-65,0,0],[1.2,700,500])),col)
 exec(BODYDETAILS,globals())
def export_variant(name,title,rear=True):
 global TITLE
 TITLE=title;folder=OUT/name;folder.mkdir(exist_ok=True);r.MESH=folder/'mallas';r.MESH.mkdir(exist_ok=True)
 ass=cq.Assembly(name=name)
 for j,(label,s,col) in enumerate(parts):ass.add(s,name=f'{label}_{j}',color=cq.Color(*col))
 ass.save(str(folder/(name+'.step')))
 # renderer uses OUT; restore family path after generating this variant
 family=globals()['OUT'];globals()['OUT']=folder
 code=RENDER if rear else RENDER.replace("[('hero',[-1.95,-2.35,1.9]),('posterior',[1.95,-2.35,1.65])]","[('hero',[-1.95,-2.35,1.9])]")
 exec(compile(code,str(Path(__file__)),'exec'),globals());globals()['OUT']=family
 results.append(dict(variant=name,title=title,parts=len(parts)))
# B: conformal cassette doors, no rectangular plates sticking out in stored mode.
for deployed in [False,True]:
 parts=[];body=BASEBODY;skin=BASEBODY.cut(BASEBODY.scale(.955))
 for xx in [-280,285]:
  for side in [-1,1]:
   window=box([xx,side*190,0],[175,180,135]);door=skin.intersect(window)
   body=body.cut(window)
   travel=side*(165 if deployed else 0)
   add('tapa_conformada',door.translate((0,travel,0)),TOP)
   cy=side*(70+165 if deployed else 70);sports_fan([xx,cy,-4],52)
   if deployed:
    for dx in [-38,38]:
     add('manga_telescopica',box([xx+dx,side*138,-28],[14,100,18]),GRAPH)
     add('guia_interior',box([xx+dx,side*200,-28],[9,140,10]),METAL)
    add('soporte_casete',box([xx,cy,-25],[100,28,9]),GRAPH)
   # inset door latch represented as compact capsule, not a projecting panel
   yy=side*(146+165 if deployed else 146)
   add('cierre_panel',box([xx,yy,12],[20,2.4,5]),BLACK)
 finish_body(body)
 export_variant('B_retractil_desplegado' if deployed else 'B_retractil_guardado','Retráctil / '+('modo desplegado' if deployed else 'modo compacto'),rear=deployed)
# C: swept shrouds blended into shoulders, no long external arms.
parts=[];body=BASEBODY
for xx in [-280,285]:
 for side in [-1,1]:
  cy=side*155
  body=body.cut(cyl([xx,cy,30],[0,0,1],60,180))
  wires=[]
  for dx,w,h in [(-105,8,8),(-65,55,28),(0,68,35),(65,55,28),(105,8,8)]:
   yz=[(w,0),(.72*w,.7*h),(0,h),(-.72*w,.7*h),(-w,0),(-.72*w,-.7*h),(0,-h),(.72*w,-.7*h)]
   wires.append(cq.Wire.makePolygon([cq.Vector(xx+dx,cy+y,10+z) for y,z in yz]+[cq.Vector(xx+dx,cy+yz[0][0],10+yz[0][1])]))
  pod=cq.Solid.makeLoft(wires).cut(cyl([xx,cy,10],[0,0,1],60,120))
  add('carenado_barrido',pod,GRAPH);sports_fan([xx,cy,10],57)
finish_body(body);export_variant('C_conductos_integrados','Conductos / integración deportiva')
# Approved A is included as the baseline of the same visual family.
import shutil
approved=ROOT/'diseno_industrial_v2';dest=OUT/'A_integracion_interna';dest.mkdir(exist_ok=True)
for filename in ['hero.png','posterior.png','diseno_industrial_v2.step']:
 shutil.copy2(approved/filename,dest/filename)
(OUT/'manifest.json').write_text(json.dumps(results,indent=2))
board=Image.new('RGB',(2800,1750))
for j,path in enumerate([dest/'hero.png',OUT/'B_retractil_guardado/hero.png',OUT/'B_retractil_desplegado/hero.png',OUT/'C_conductos_integrados/hero.png']):board.paste(Image.open(path).resize((1400,875)),((j%2)*1400,(j//2)*875))
board.save(OUT/'familia_completa.png')
(OUT/'LEEME.md').write_text('''# Familia de producto deportivo\n\nLínea industrial aprobada extendida a integración interna, casetes retráctiles y conductos externos carenados. CAD conceptual y renders por trazado de rayos, sin generación de imágenes por IA. Grafito, paneles angulosos, acentos cobrizos y módulos protegidos.\n\nLa forma de puertas y carenados se ha rediseñado estéticamente. Los estados de B son extremos de una propuesta de traslación; no se ha comprobado el recorrido continuo, las interferencias o los cierres. Tampoco se han cerrado empuje, control omnidireccional, masa, pérdidas de rejillas, cargas, refrigeración ni régimen transónico. Las piezas son volúmenes conceptuales; no son planos de fabricación. El aspecto deportivo no certifica ninguna prestación.\n\nLa versión A conserva el diseño aprobado. B y C son estudios nuevos y no heredan cálculos de vuelo de geometrías anteriores.\n''')
print('FAMILIA FINALIZADA',flush=True)
