"""Geometry checks normalized by hull size, not the much larger air box."""
from pathlib import Path
import argparse,json
import numpy as np
import gmsh
p=argparse.ArgumentParser();p.add_argument('case',type=Path);a=p.parse_args()
m=json.loads((a.case/'mesh_metadata.json').read_text())
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.open(str(a.case/'fluid.msh'))
tags,coords,_=gmsh.model.mesh.getNodes();v=np.asarray(coords).reshape(-1,3)
lookup=np.full(int(max(tags))+1,-1,dtype=np.int64);lookup[np.asarray(tags,dtype=int)]=np.arange(len(tags))
types,_,nodes=gmsh.model.mesh.getElements(3);assert list(types)==[4]
tet=lookup[np.asarray(nodes[0],dtype=int)].reshape(-1,4);xyz=v[tet]
det=np.linalg.det(np.stack((xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0],xyz[:,3]-xyz[:,0]),axis=2));assert np.all(det>0)
fluid_volume=float(det.sum()/6)
body_triangles=[]
for dim,tag in gmsh.model.getPhysicalGroups(2):
 if gmsh.model.getPhysicalName(dim,tag)!='hull':continue
 for face in gmsh.model.getEntitiesForPhysicalGroup(dim,tag):
  types,_,nodes=gmsh.model.mesh.getElements(2,int(face));assert list(types)==[2]
  body_triangles.append(lookup[np.asarray(nodes[0],dtype=int)].reshape(-1,3))
tri=np.vstack(body_triangles);q=v[tri];cross=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])
body_volume=float(abs(np.einsum('ij,ij->i',q[:,0],cross).sum()/6));body_area=float(np.linalg.norm(cross,axis=1).sum()/2)
relative_body_error=abs(body_volume/m['body_volume_m3']-1);assert relative_body_error<.005
relative_area_error=abs(body_area/m['patches']['hull']['area_m2']-1);assert relative_area_error<.005
b=m['domain_bounds_m'];box=(b[3]-b[0])*(b[4]-b[1])*(b[5]-b[2])
closure_error=abs(fluid_volume+body_volume-box);assert closure_error<1e-7*m['body_volume_m3']
edges=np.sort(np.vstack((tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]])),axis=1)
_,counts=np.unique(edges,axis=0,return_counts=True);assert np.all(counts==2)
out=dict(tetrahedra=len(tet),all_tetrahedra_positive=True,hull_triangles=len(tri),hull_mesh_closed_edge_incidence_two=True,
 hull_volume_m3=body_volume,CAD_hull_volume_m3=m['body_volume_m3'],relative_hull_volume_error=relative_body_error,
 hull_mesh_area_m2=body_area,CAD_hull_area_m2=m['patches']['hull']['area_m2'],relative_hull_area_error=relative_area_error,
 fluid_tetra_volume_m3=fluid_volume,box_partition_closure_error_m3=closure_error,
 flow_computed=False,drag_and_Mach_critical_validated=False,
 note='Geometric audit only; body-relative errors prevent the farfield volume from hiding hull discretization errors.')
gmsh.finalize();(a.case/'GEOMETRY_AUDIT.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
