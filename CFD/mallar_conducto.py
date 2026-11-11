"""3D fluid mesh of isolated straight duct with the six current vane rectangles.
SI geometry is independently reconstructed from the declared CAD dimensions.
"""
from pathlib import Path
import sys,json,math
import gmsh
ROOT=Path(__file__).resolve().parent
angleX=float(sys.argv[1]) if len(sys.argv)>1 else 0.;angleY=float(sys.argv[2]) if len(sys.argv)>2 else 0.;h=float(sys.argv[3]) if len(sys.argv)>3 else .0035
OUT=ROOT/f'conducto_X{angleX:g}_Y{angleY:g}_h{h:g}';OUT.mkdir(exist_ok=True)
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.add('conducto')
occ=gmsh.model.occ;R=.042;zlo=-.065;zhi=.080
fluid=occ.addCylinder(0,0,zlo,0,0,zhi-zlo,R);vanes=[];centers=[]
c=.016;t=.0015;maxhalf=math.hypot(c/2,t/2)
for row,z,angle in [('X',-.012,angleX),('Y',-.040,angleY)]:
 for j,offset in enumerate([-.022,0,.022]):
  span=2*math.sqrt(.04**2-(abs(offset)+maxhalf)**2)-.002
  if row=='X':
   p=[0,offset,z];sh=occ.addBox(-span/2,offset-t/2,z-c/2,span,t,c);axis=(1,0,0)
  else:
   p=[offset,0,z];sh=occ.addBox(offset-t/2,-span/2,z-c/2,t,span,c);axis=(0,1,0)
  occ.rotate([(3,sh)],*p,*axis,math.radians(angle));vanes.append((3,sh));centers.append((f'vane{row}{j}',p))
result,_=occ.cut([(3,fluid)],vanes);occ.synchronize();volumes=[x for x in result if x[0]==3];assert len(volumes)==1
surfaces=gmsh.model.getBoundary(volumes,oriented=False);patches={k:[] for k in ['inlet','outlet','walls']+[n for n,p in centers]}
for dim,tag in surfaces:
 bb=gmsh.model.getBoundingBox(dim,tag);com=occ.getCenterOfMass(dim,tag)
 if abs(bb[2]-zhi)<1e-6 and abs(bb[5]-zhi)<1e-6:name='inlet'
 elif abs(bb[2]-zlo)<1e-6 and abs(bb[5]-zlo)<1e-6:name='outlet'
 elif gmsh.model.getType(dim,tag)=='Cylinder':name='walls'
 else:
  row='X' if abs(com[2]+.012)<abs(com[2]+.040) else 'Y'
  coordinate=1 if row=='X' else 0
  name=min([a for a in centers if a[0].startswith('vane'+row)],key=lambda a:abs(a[1][coordinate]-com[coordinate]))[0]
 patches[name].append(tag)
for name,tags in patches.items():
 assert tags,name
 if name.startswith('vane'):assert len(tags)==6,(name,tags)
 pg=gmsh.model.addPhysicalGroup(2,tags);gmsh.model.setPhysicalName(2,pg,name)
pg=gmsh.model.addPhysicalGroup(3,[v for d,v in volumes]);gmsh.model.setPhysicalName(3,pg,'fluid')
vanefaces=sum([tags for name,tags in patches.items() if name.startswith('vane')],[])
dist=gmsh.model.mesh.field.add('Distance');gmsh.model.mesh.field.setNumbers(dist,'FacesList',vanefaces);gmsh.model.mesh.field.setNumber(dist,'Sampling',60)
th=gmsh.model.mesh.field.add('Threshold');gmsh.model.mesh.field.setNumber(th,'InField',dist);gmsh.model.mesh.field.setNumber(th,'SizeMin',h/4);gmsh.model.mesh.field.setNumber(th,'SizeMax',h);gmsh.model.mesh.field.setNumber(th,'DistMin',.002);gmsh.model.mesh.field.setNumber(th,'DistMax',.015);gmsh.model.mesh.field.setAsBackgroundMesh(th)
gmsh.option.setNumber('Mesh.MeshSizeMin',h/4);gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.Algorithm3D',1);gmsh.option.setNumber('Mesh.MshFileVersion',2.2);gmsh.model.mesh.generate(3);gmsh.model.mesh.optimize('Netgen')
types,tags,nodes=gmsh.model.mesh.getElements(3);N=sum(len(a) for a in tags)
gmsh.write(str(OUT/'fluid.msh'));volume=occ.getMass(3,volumes[0][1]);meta=dict(angles_mechanical_deg=[angleX,angleY],h_m=h,cells=N,volume_m3=volume,patches={k:len(v) for k,v in patches.items()},radius_m=R,inlet_z_m=zhi,outlet_z_m=zlo,note='No rotor, shafts, motor, stators, grids, outer air or hull. Uniform prescribed post-rotor inlet. Isotropic tetrahedra, no prism boundary layers; prototype mesh only.')
(OUT/'mesh_metadata.json').write_text(json.dumps(meta,indent=2));gmsh.finalize();print(json.dumps(meta,indent=2))
