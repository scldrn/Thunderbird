from pathlib import Path
import cadquery as cq,json
P=Path(__file__).resolve().parent
for mass in (2,5,10):
 folder=P/f'{mass}kg';m=json.loads((folder/'manifest.json').read_text());scale=m['scale'];asm=cq.Assembly(name='A05_compuertas_abiertas_concepto')
 centers=[(-200,-76),(-200,76),(200,-76),(200,76)]
 for s,n,loc,c in cq.Assembly.load(str(folder/'A05_integrado.step')):
  n=n.split('/')[-1];s=s.moved(loc)
  if n.startswith('compuerta_'):
   j=int(n.split('_')[1]);x,y=centers[j];side=1 if y>0 else -1;top='superior' in n
   bb=s.BoundingBox();z=(bb.zmin+bb.zmax)/2
   pivot=(x*scale,(y+side*46)*scale,z)
   s=s.rotate(pivot,(pivot[0]+100*scale,pivot[1],pivot[2]),side*(105 if top else -105))
  asm.add(s,name=n,color=c)
 dest=folder/'A05_compuertas_abiertas.step';asm.save(str(dest))
 r=list(cq.Assembly.load(str(dest)));assert len(r)==208 and all(s.moved(l).isValid() for s,n,l,c in r)
 print(mass,'ok',flush=True)
s=(P/'render_A05.py').read_text()
s=s.replace("source=folder/('A05_corte.step' if a.view=='interior' else ('A05_controles_15deg.step' if a.view=='control' else 'A05_integrado.step'))","source=folder/'A05_compuertas_abiertas.step'")
s=s.replace("if a.view!='interior' and not meta[name]['exterior']:continue","# All parts visible through open ports")
s=s.replace("'hero':[-.90,-2.25,2.00]","'hero':[-.65,-1.45,2.7]")
s=s.replace("out=ROOT/f'A05_{a.mass}kg_{a.view}.png'","out=ROOT/f'A05_{a.mass}kg_desplegado.png'")
s=s.replace('EXTERIOR · CUBIERTAS ENRASADAS','ROTORES INTERNOS · COMPUERTAS ABIERTAS')
s=s.replace('DISEÑO EN DESARROLLO','APERTURA CONCEPTUAL SIN VALIDAR')
s=s.replace("f'render_{a.mass}kg_{a.view}.json'","f'render_{a.mass}kg_desplegado.json'")
(P/'render_despliegue.py').write_text(s)
(P/'NOTA_DESPLIEGUE.md').write_text('''# Pose de apertura conceptual\n\nLos cuatro rotores permanecen dentro de los conductos. Las ocho tapas superior/inferior se representan giradas 105 grados sobre ejes longitudinales provisionales próximos a su borde exterior. No existen bisagras, varillaje o actuadores de compuertas dimensionados. No se verificaron barridos o interferencias de apertura, área efectiva de entrada/salida, cargas, ni compatibilidad con las aletas de control. No acredita vuelo estacionario o transición. STEP reimportado con 208 piezas válidas por escala.\n''')
