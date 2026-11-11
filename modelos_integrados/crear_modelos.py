"""CAD de integración preliminar. SI internamente; STEP en mm. No hardware validado."""
import os,sys,json,csv,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'salida';OUT.mkdir(exist_ok=True)
os.environ['MPLCONFIGDIR']=str(OUT/'mpl-cache')
sys.path.insert(0,str(ROOT.parent/'legacy'/'scripts'))
import numpy as np
import cadquery as cq
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from control import allocation
from calcular import geometry
from scipy.optimize import brentq
from trimado_superficies import trim

def cylinder(p,n,r,h):
 return cq.Solid.makeCylinder(r*1000,h*1000,cq.Vector(*(np.array(p)-np.array(n)*h/2)*1000),cq.Vector(*n))
def box(p,d):
 return cq.Workplane('XY').box(*(np.array(d)*1000)).translate(tuple(np.array(p)*1000)).val()
def hull(L,D,t=0):
 a=L/2-t;b=D/2-t
 pts=[(a*np.cos(u)*1000,b*np.sin(u)*1000) for u in np.linspace(0,np.pi,101)]
 return cq.Workplane('XY').moveTo(*pts[0]).spline(pts[1:],includeCurrent=True).close().revolve(360,(0,0),(1,0)).val()
def writecsv(path,rows,fields=None):
 with path.open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 summary=[];fig=plt.figure(figsize=(16,9))
 for ii,m in enumerate([5,10]):
  folder=OUT/f'{m}kg';folder.mkdir(exist_ok=True)
  scale=(m/5)**(1/3);g=geometry(m/200,6,'esferoide');L,D=g['L_m'],g['D_m'];R=D/2
  _,pos,norm=allocation(L,D,2,2.126346107402112,2.3209109878730265);pos[:,0]*=1.25
  rotorD=.4572*scale
  st=1.2*(m/200)/(.4*L)
  sw=brentq(lambda s:trim(m,6,s,st,150,a_slope=2,cross=.3)['alpha_deg']-8,0,2)
  config=dict(target_mass_kg=m,units='m, kg, s; STEP mm',L_m=L,D_m=D,rotor_diameter_m=rotorD,rotor_centers_m=pos.tolist(),rotor_axes=norm.tolist(),wing_oneplane_m2=sw,tail_oneplane_m2=st,assumptions=['Densidad global 200 kg/m3 solo fija volumen exterior','Rotores 10kg: escalado geométrico, sin motor seleccionado','Masas estimadas, ninguna pesada','Configuración desplegada; sin mecanismo de retracción resuelto'])
  (folder/'configuracion.json').write_text(json.dumps(config,indent=2))
  outer=hull(L,D);skin=outer.cut(hull(L,D,.0005))
  comps=[];envelopes=[]
  def add(name,shape,mass,color,role='componente',status='estimado'):
   comps.append(dict(name=name,shape=shape,mass=mass,color=color,role=role,status=status))
  add('carcasa_sin_aberturas',skin,skin.Volume()*1e-9*2700,(.65,.72,.77),'carcasa','material equivalente aluminio; espesor supuesto 0.5 mm')
  englen,engdia,engmass=(.241,.097,1.08) if m==5 else (.322,.121,2.155)
  add('envolvente_reactor',cylinder([.22*L,0,0],[1,0,0],engdia/2,englen),engmass,(.55,.56,.6),status='envolvente publicada; instalación pendiente')
  for j,sign in enumerate([-1,1]):
   # 10kg packs are provisional scaled envelopes, not selected products
   dims=np.array([.110,.034,.050])*scale
   add(f'bateria_{j+1}',box([-.12*L,sign*.065*scale,0],dims),.357*(m/5),(.12,.35,.8),status='5kg ficha; 10kg extrapolación')
  fuel=.156*(m/5);fuelvol=fuel/800;fd=(fuelvol/(.12*scale))**.5
  add('combustible_sin_deposito',box([.05*L,0,-.065*scale],[.12*scale,fd,fd]),fuel,(.9,.65,.12))
  # Flow passage is a reserved volume; never counted as mass or solid material
  duct=cylinder([-.17*L,0,0],[1,0,0],.028*scale,.50*L)
  envelopes.append(('reserva_conducto',duct,(.1,.7,.8)))
  for j,(p,n) in enumerate(zip(pos,norm)):
   root=np.array([p[0],p[1],p[2]]) ;root[1:]*=(R*np.sqrt(1-(p[0]/(L/2))**2))/np.linalg.norm(p[1:])
   mount=p+np.sign(np.dot(root-p,n))*.065*scale*n
   v=mount-root;length=np.linalg.norm(v)
   arm=cylinder((mount+root)/2,v/length,.008*scale,length)
   add(f'brazo_{j+1}',arm,.25/8*(m/5),(.2,.24,.28))
   add(f'modulo_{j+1}',cylinder(mount,n,.0278*scale,.032*scale),(.128+.070)*(m/5),(.25,.27,.3),status='masa provisional incluye palas servo ESC; buje aún ausente')
   envelopes.append((f'barrido_rotor_{j+1}',cylinder(p,n,rotorD/2,.012*scale),(.3,.65,.8)))
  for label,S,x in [('ala',sw,0),('cola',st,.4*L)]:
   span=(2*S)**.5/2;chord=S/(2*span)
   localR=R*np.sqrt(1-(x/(L/2))**2)
   for j in range(4):
    sh=box([x,localR+span/2,0],[chord,span,.002*scale]).rotate((0,0,0),(1,0,0),90*j)
    add(f'{label}_{j+1}',sh,S/2,(.7,.75,.78),status='área del modelo aero; masa superficial supuesta 1kg/m2')
  # non-geometric allowances kept separate to avoid fabricated placement/inertia
  allowances={'avionica_cableado':.20*m/5,'instalacion_reactor':.15*m/5,'integracion_bateria':.04*m/5,'reserva':.25*m/5}
  ass=cq.Assembly(name=f'concepto_{m}kg_desplegado')
  for c in comps: ass.add(c['shape'],name=c['name'],color=cq.Color(*c['color'],.28 if c['role']=='carcasa' else 1))
  for name,sh,color in envelopes:ass.add(sh,name=name,color=cq.Color(*color,.15))
  assert all(c['shape'].isValid() for c in comps), 'Invalid CAD solid'
  assert abs(outer.Volume()*1e-9-m/200)<1e-5
  ass.save(str(folder/'integracion_desplegada.step'))
  cq.exporters.export(cq.Compound.makeCompound([c['shape'] for c in comps]),str(folder/'componentes.stl'),tolerance=.5,angularTolerance=.2)
  masses=[];centers=[];Is=[]
  for c in comps:
   sh=c['shape'];center=np.array(sh.Center().toTuple())/1000
   geomI=np.array(cq.Shape.matrixOfInertia(sh));I=geomI*c['mass']/sh.Volume()/1e6
   masses.append(c['mass']);centers.append(center);Is.append(I)
  masses=np.array(masses);centers=np.array(centers);cg=np.average(centers,axis=0,weights=masses)
  inertia=sum(I+mass*((d@d)*np.eye(3)-np.outer(d,d)) for I,mass,d in zip(Is,masses,centers-cg))
  bom=[dict(componente=c['name'],masa_kg=c['mass'],x_m=p[0],y_m=p[1],z_m=p[2],estado=c['status']) for c,p in zip(comps,centers)]
  writecsv(folder/'masas_y_centros_ESTIMADOS.csv',bom)
  collisions=[]
  objects=[(c['name'],c['shape']) for c in comps if c['role']!='carcasa']+[(n,s) for n,s,_ in envelopes]
  for (an,a),(bn,b) in itertools.combinations(objects,2):
   vol=a.intersect(b).Volume()/1e9
   if vol>1e-9:collisions.append(dict(a=an,b=bn,interseccion_m3=vol,interpretacion='revisar: envolventes pueden incluir conexiones intencionales'))
  writecsv(folder/'interferencias.csv',collisions,['a','b','interseccion_m3','interpretacion'])
  containment=[]
  for c in comps:
   if c['name'].startswith(('bateria','combustible','envolvente_reactor')):
    outside=c['shape'].cut(outer).Volume()/1e9
    containment.append(dict(componente=c['name'],volumen_fuera_fuselaje_m3=outside))
  writecsv(folder/'alojamiento_interno.csv',containment)
  rotor_hull=[dict(rotor=n,intersection_m3=sh.intersect(outer).Volume()/1e9) for n,sh,_ in envelopes if n.startswith('barrido')]
  writecsv(folder/'rotores_fuselaje.csv',rotor_hull)
  solids=[s for _,s,_ in envelopes]+[c['shape'] for c in comps];bb=cq.Compound.makeCompound(solids).BoundingBox()
  report=dict(**config,geometric_mass_kg=float(masses.sum()),allowances_kg=allowances,total_budget_kg=float(masses.sum()+sum(allowances.values())),missing_mass_items=['buje paso variable','mecanismos plegado','deposito','toma y tobera','refuerzos de aberturas'],CG_geometric_components_only_m=cg.tolist(),inertia_geometric_components_only_kgm2=inertia.tolist(),bounds_deployed_m=[bb.xlen/1000,bb.ylen/1000,bb.zlen/1000],intersection_count=len(collisions),internal_containment=containment)
  (folder/'mediciones_DIGITALES.json').write_text(json.dumps(report,indent=2));summary.append(report)
  ax=fig.add_subplot(1,2,ii+1,projection='3d')
  for c in comps:
   verts,tris=c['shape'].tessellate(4)
   v=np.array([p.toTuple() for p in verts])/1000;t=np.array(tris)
   ax.plot_trisurf(v[:,0],v[:,1],v[:,2],triangles=t,color=c['color'],alpha=.13 if c['role']=='carcasa' else .85,linewidth=0)
  for p,n in zip(pos,norm):
   u=np.cross(n,[1,0,0]);u/=np.linalg.norm(u);v=np.cross(n,u);a=np.linspace(0,2*np.pi,80);pts=p[:,None]+rotorD/2*(u[:,None]*np.cos(a)+v[:,None]*np.sin(a));ax.plot(*pts,color='teal',alpha=.7,lw=1)
  a=np.linspace(0,2*np.pi,160)
  for ang in [0,np.pi/2]:
   ax.plot(L/2*np.cos(a),R*np.sin(a)*np.cos(ang),R*np.sin(a)*np.sin(ang),color='slategray',lw=1)
  ax.set(xlabel='x (m)',ylabel='y (m)',zlabel='z (m)',title=f'Objetivo {m} kg | presupuesto {report["total_budget_kg"]:.2f} kg + faltantes\nL={L:.3f} m · D={D:.3f} m · rotor Ø{rotorD:.3f} m')
  ax.set_box_aspect([bb.xlen,bb.ylen,bb.zlen]);ax.view_init(23,-55)
 fig.suptitle('CAD integrado preliminar — configuración desplegada\nEnvolventes y masas supuestas; sin validación de vuelo ni plegado',fontsize=16)
 fig.tight_layout();fig.savefig(OUT/'modelos_integrados.png',dpi=180)
 (OUT/'resumen.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps([{k:r[k] for k in ['target_mass_kg','total_budget_kg','intersection_count','bounds_deployed_m','internal_containment']} for r in summary],indent=2))
if __name__=='__main__':main()
