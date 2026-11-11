"""Full 3D external mesh of the measured closed styling hull (SI).

Pressure-flow preparation only: no prism layers, installed doors or propulsion.
The approved product CAD is not changed. This is its closed-envelope reference.
"""
from pathlib import Path
import argparse,json,hashlib,math
import gmsh
ROOT=Path(__file__).resolve().parent
REF=ROOT.parent/'modelos_integrados/aerodinamica_A'
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--h',type=float,default=.008);a=p.parse_args()
if a.output.exists():raise FileExistsError(a.output)
if a.h<=0:raise ValueError('h must be positive')
a.output.mkdir(parents=True);meta=json.loads((REF/'METROLOGIA.json').read_text());L=meta['bounds_m']['length']
source=REF/'envolvente_cerrada_referencia.step'
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
gmsh.option.setString('Geometry.OCCTargetUnit','MM');gmsh.model.add('hull_A_closed')
occ=gmsh.model.occ;body=occ.importShapes(str(source));assert len(body)==1 and body[0][0]==3
occ.dilate(body,0,0,0,.001,.001,.001);occ.synchronize()
volume=occ.getMass(*body[0]);assert abs(volume/meta['gross_enclosed_volume_m3']-1)<1e-6
xmin=meta['bounds_m']['x_min']-3*L;xmax=meta['bounds_m']['x_max']+5*L;side=3*L
domain=occ.addBox(xmin,-side,-side,xmax-xmin,2*side,2*side)
fluid,_=occ.cut([(3,domain)],body);occ.synchronize();assert len(fluid)==1 and fluid[0][0]==3
patches={k:[] for k in ('inlet','outlet','farfield','hull')}
for dim,tag in gmsh.model.getBoundary(fluid,oriented=False):
 bb=gmsh.model.getBoundingBox(dim,tag)
 if abs(bb[0]-xmin)<1e-5 and abs(bb[3]-xmin)<1e-5:name='inlet'
 elif abs(bb[0]-xmax)<1e-5 and abs(bb[3]-xmax)<1e-5:name='outlet'
 elif any(abs(abs(bb[j])-side)<1e-5 for j in (1,2,4,5)):name='farfield'
 else:name='hull'
 patches[name].append(tag)
assert len(patches['inlet'])==len(patches['outlet'])==1
assert len(patches['farfield'])==4 and len(patches['hull'])==12
for name,tags in patches.items():
 group=gmsh.model.addPhysicalGroup(2,tags);gmsh.model.setPhysicalName(2,group,name)
group=gmsh.model.addPhysicalGroup(3,[fluid[0][1]]);gmsh.model.setPhysicalName(3,group,'fluid')
dist=gmsh.model.mesh.field.add('Distance');gmsh.model.mesh.field.setNumbers(dist,'FacesList',patches['hull']);gmsh.model.mesh.field.setNumber(dist,'Sampling',80)
grade=gmsh.model.mesh.field.add('Threshold');gmsh.model.mesh.field.setNumber(grade,'InField',dist)
for k,v in [('SizeMin',a.h),('SizeMax',.7),('DistMin',.015),('DistMax',3.)]:gmsh.model.mesh.field.setNumber(grade,k,v)
gmsh.model.mesh.field.setAsBackgroundMesh(grade)
gmsh.option.setNumber('Mesh.MeshSizeMin',a.h);gmsh.option.setNumber('Mesh.MeshSizeMax',.7)
gmsh.option.setNumber('Mesh.Algorithm3D',1);gmsh.option.setNumber('Mesh.MshFileVersion',2.2)
gmsh.model.mesh.generate(3);gmsh.model.mesh.optimize('Netgen')
types,tags,nodes=gmsh.model.mesh.getElements(3);assert list(types)==[4]
gmsh.write(str(a.output/'fluid.msh'))
result=dict(geometry_scope='Closed styling loft before ports and inserts. Not full installed product or validated cruise doors.',source_step=str(source.resolve()),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
 units='metres',body_volume_m3=volume,reference_area_m2=meta['max_sampled_section_area_m2'],body_length_m=L,
 domain_bounds_m=[xmin,-side,-side,xmax,side,side],domain_distances_in_lengths=dict(upstream=3,downstream=5,side=3),
 analytic_fluid_volume_m3=(xmax-xmin)*(2*side)**2-volume,occ_fluid_volume_m3=occ.getMass(*fluid[0]),
 cells=sum(len(x) for x in tags),minimum_target_size_m=a.h,
 patches={k:dict(surfaces=len(v),area_m2=sum(occ.getMass(2,t) for t in v)) for k,v in patches.items()},
 flow_solved=False,drag_or_critical_Mach_validated=False,
 limitations=['No prism layers or wall resolution proof','No mesh/domain sensitivity','No propulsion, ports, lids or seams','No solver fields or Mach result yet','Not a claim of global optimum'])
(a.output/'mesh_metadata.json').write_text(json.dumps(result,indent=2));gmsh.finalize();print(json.dumps(result,indent=2))
