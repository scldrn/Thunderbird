"""Independent analytic-volume and tetrahedron checks for open-duct mesh."""
from pathlib import Path
import argparse,json,math
import numpy as np
import gmsh
p=argparse.ArgumentParser();p.add_argument('case',type=Path);a=p.parse_args()
m=json.loads((a.case/'mesh_metadata.json').read_text())
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.open(str(a.case/'fluid.msh'))
tags,coordinates,_=gmsh.model.mesh.getNodes();xyz=np.asarray(coordinates).reshape(-1,3)
lookup=np.full(int(max(tags))+1,-1,dtype=np.int64);lookup[np.asarray(tags,dtype=int)]=np.arange(len(tags))
types,element_tags,nodes=gmsh.model.mesh.getElements(3)
if list(types)!=[4]:raise ValueError('This audit expects linear tetrahedra only')
tet=lookup[np.asarray(nodes[0],dtype=int)].reshape(-1,4)
if tet.min()<0:raise ValueError('Missing node')
v=xyz[tet];det=np.linalg.det(np.stack((v[:,1]-v[:,0],v[:,2]-v[:,0],v[:,3]-v[:,0]),axis=2))
if np.any(det<=0):raise ValueError('Non-positive oriented tetrahedra')
mesh_volume=float(det.sum()/6)
# Independent closed-form volume subtracts the sleeve and six rotated boxes.
R=m['bore_radius_m'];Ro=m['sleeve_outer_radius_m'];H=m['top_z_m']-m['lip_z_m']
full=math.pi*m['domain_radius_m']**2*(m['top_z_m']-m['bottom_z_m'])
sleeve=math.pi*(Ro**2-R**2)*H
c=.016;t=.0015;maxhalf=math.hypot(c/2,t/2)
vanes=2*sum((2*math.sqrt(.04**2-(abs(offset)+maxhalf)**2)-.002)*t*c for offset in [-.022,0,.022])
analytic=full-sleeve-vanes
np.testing.assert_allclose(m['volume_m3'],analytic,rtol=1e-10,atol=1e-12)
relative_mesh_volume_error=abs(mesh_volume-analytic)/analytic
if relative_mesh_volume_error>.005:raise ValueError('Polygonal volume discrepancy exceeds 0.5% geometric audit threshold')
np.testing.assert_allclose(m['patches']['inlet']['area_m2'],math.pi*R**2,rtol=1e-10)
out=dict(cells=len(tet),all_tetrahedra_positive=True,min_tetra_volume_m3=float(det.min()/6),
         analytic_volume_m3=analytic,occ_volume_m3=m['volume_m3'],tetra_mesh_volume_m3=mesh_volume,
         relative_polygonal_volume_error=relative_mesh_volume_error,inlet_area_verified=True,
         flow_solved=False,loads_accepted=False,limitations=['not a non-orthogonality, skewness or wall-resolution check','no flow or domain-size sensitivity'])
gmsh.finalize();(a.case/'GEOMETRY_AUDIT.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
