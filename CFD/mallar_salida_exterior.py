"""Isolated open duct and vanes in surrounding air, SI units.

Concept geometry derived from the old straight-channel dimensions; not CAD A.
No rotor, body or prism layers. Domain size/mesh remain sensitivity parameters.
"""
from pathlib import Path
import argparse,json,math
import gmsh

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
p.add_argument('--angle-x',type=float,default=35);p.add_argument('--angle-y',type=float,default=-35)
p.add_argument('--radius',type=float,default=.336);p.add_argument('--downstream',type=float,default=.504)
p.add_argument('--h',type=float,default=.006)
a=p.parse_args()
if a.output.exists():raise FileExistsError(a.output)
if a.radius<=.084 or a.downstream<=.084 or a.h<=0:raise ValueError('Invalid domain/mesh')
a.output.mkdir(parents=True)
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
gmsh.model.add('open_duct');occ=gmsh.model.occ
R=.042;Ro=.046;lip=-.065;top=.080;bottom=lip-a.downstream
outer=occ.addCylinder(0,0,bottom,0,0,top-bottom,a.radius)
sleeve=occ.addCylinder(0,0,lip,0,0,top-lip,Ro)
bore=occ.addCylinder(0,0,lip,0,0,top-lip,R)
shell,_=occ.cut([(3,sleeve)],[(3,bore)])
fluid,_=occ.cut([(3,outer)],shell)
vanes=[];centers=[];c=.016;thickness=.0015;maxhalf=math.hypot(c/2,thickness/2)
for row,z,angle in [('X',-.012,a.angle_x),('Y',-.040,a.angle_y)]:
 for j,offset in enumerate([-.022,0,.022]):
  span=2*math.sqrt(.04**2-(abs(offset)+maxhalf)**2)-.002
  if row=='X':
   center=[0,offset,z];box=occ.addBox(-span/2,offset-thickness/2,z-c/2,span,thickness,c);axis=(1,0,0)
  else:
   center=[offset,0,z];box=occ.addBox(offset-thickness/2,-span/2,z-c/2,thickness,span,c);axis=(0,1,0)
  occ.rotate([(3,box)],*center,*axis,math.radians(angle))
  vanes.append((3,box));centers.append((f'vane{row}{j}',center))
fluid,_=occ.cut(fluid,vanes);occ.synchronize()
assert len(fluid)==1 and fluid[0][0]==3
patches={name:[] for name in ['inlet','farfield','walls']+[n for n,_ in centers]}
for dim,tag in gmsh.model.getBoundary(fluid,oriented=False):
 bb=gmsh.model.getBoundingBox(dim,tag);com=occ.getCenterOfMass(dim,tag)
 if abs(bb[2]-top)<1e-6 and abs(bb[5]-top)<1e-6:
  name='inlet' if occ.getMass(dim,tag)<.01 else 'farfield'
 elif abs(bb[2]-bottom)<1e-6 or max(abs(bb[i]) for i in (0,1,3,4))>a.radius*.99:
  name='farfield'
 elif gmsh.model.getType(dim,tag)=='Cylinder' or (abs(bb[2]-lip)<1e-6 and abs(bb[5]-lip)<1e-6):
  name='walls'
 else:
  row='X' if abs(com[2]+.012)<abs(com[2]+.040) else 'Y';coordinate=1 if row=='X' else 0
  name=min([v for v in centers if v[0].startswith('vane'+row)],key=lambda v:abs(v[1][coordinate]-com[coordinate]))[0]
 patches[name].append(tag)
for name,tags in patches.items():
 assert tags,name
 if name.startswith('vane'):assert len(tags)==6,(name,len(tags))
 group=gmsh.model.addPhysicalGroup(2,tags);gmsh.model.setPhysicalName(2,group,name)
group=gmsh.model.addPhysicalGroup(3,[fluid[0][1]]);gmsh.model.setPhysicalName(3,group,'fluid')
# Face distance grades the mesh near the sleeve and vanes, leaving the far field coarse.
near=gmsh.model.mesh.field.add('Distance')
gmsh.model.mesh.field.setNumbers(near,'FacesList',sum([v for k,v in patches.items() if k not in ('farfield','inlet')],[]))
gmsh.model.mesh.field.setNumber(near,'Sampling',50)
grade=gmsh.model.mesh.field.add('Threshold');gmsh.model.mesh.field.setNumber(grade,'InField',near)
for key,value in [('SizeMin',a.h/4),('SizeMax',.035),('DistMin',.002),('DistMax',.12)]:gmsh.model.mesh.field.setNumber(grade,key,value)
gmsh.model.mesh.field.setAsBackgroundMesh(grade)
gmsh.option.setNumber('Mesh.MeshSizeMin',a.h/4);gmsh.option.setNumber('Mesh.MeshSizeMax',.035)
gmsh.option.setNumber('Mesh.Algorithm3D',1);gmsh.option.setNumber('Mesh.MshFileVersion',2.2)
gmsh.model.mesh.generate(3);gmsh.model.mesh.optimize('Netgen')
_,tags,_=gmsh.model.mesh.getElements(3)
meta=dict(angles_mechanical_deg=[a.angle_x,a.angle_y],domain_radius_m=a.radius,lip_z_m=lip,
         top_z_m=top,bottom_z_m=bottom,bore_radius_m=R,sleeve_outer_radius_m=Ro,
         cells=sum(len(v) for v in tags),volume_m3=occ.getMass(3,fluid[0][1]),
         patches={k:dict(surface_count=len(v),area_m2=sum(occ.getMass(2,t) for t in v)) for k,v in patches.items()},
         status='Mesh only, no computed flow or accepted loads',
         limitations=['old channel geometry, not full selected CAD','no rotor/motor/shafts or body','no prism layers or demonstrated wall resolution','domain extent and mesh sensitivity unverified'])
gmsh.write(str(a.output/'fluid.msh'));(a.output/'mesh_metadata.json').write_text(json.dumps(meta,indent=2))
gmsh.finalize();print(json.dumps(meta,indent=2))
