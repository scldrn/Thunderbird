"""Exact CAD metrology of the styling hull, not a flow solution or mass closure."""
from pathlib import Path
import json,hashlib,math,csv
import cadquery as cq
import numpy as np
from scipy.integrate import simpson
from scipy.spatial import ConvexHull
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'aerodinamica_A';OUT.mkdir(exist_ok=True)
source=ROOT/'diseno_industrial_v2.py'
env={'__file__':str(source)}
exec(compile(source.read_text().split('# Recessed fan ports')[0],str(source),'exec'),env)
body=env['body'];bb=body.BoundingBox()
def adaptive_area(s):
    props=GProp_GProps();error=BRepGProp.SurfaceProperties_s(s.wrapped,props,1e-10,False)
    return props.Mass()
def adaptive_volume(s):return s.Volume(tol=1e-10)
body_area=adaptive_area(body);body_volume=adaptive_volume(body)

def section_area(s,x):
    plane=cq.Face.makePlane(3000,3000,basePnt=cq.Vector(x,0,0),dir=cq.Vector(1,0,0))
    return adaptive_area(s.intersect(plane))

def mesh_measures(shape,tol):
    vertices,triangles=shape.tessellate(tol,angularTolerance=.08)
    v=np.array([a.toTuple() for a in vertices]);t=np.array(triangles)
    p=v[t];av=.5*np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);a=np.linalg.norm(av,axis=1)
    good=a>1e-14;p=p[good];av=av[good];a=a[good]
    nx=av[:,0]/a
    return dict(triangles=len(a),tolerance_mm=tol,surface_area_mm2=float(sum(a)),signed_volume_mm3=float(np.einsum('ij,ij->i',p[:,0],av).sum()/3),streamwise_tangent_projected_surface_area_mm2=float(np.sum(a*np.sqrt(np.maximum(0,1-nx**2)))),uniform_pressure_area_vector_mm2=av.sum(axis=0).tolist(),uniform_pressure_moment_vector_mm3=np.cross(p.mean(axis=1),av).sum(axis=0).tolist(),YZ_projected_convex_hull_area_mm2=float(ConvexHull(v[:,1:]).volume))

# Verify section extraction on an independent analytic solid.
ell=cq.Solid.makeSphere(1,angleDegrees1=-90,angleDegrees2=90).transformGeometry(cq.Matrix([[150,0,0,0],[0,50,0,0],[0,0,25,0],[0,0,0,1]]))
analytic=[]
for x in [-120,0,90]:
    exact=math.pi*50*25*(1-(x/150)**2);got=section_area(ell,x)
    assert abs(got/exact-1)<1e-6
    analytic.append(dict(x_mm=x,exact_area_mm2=exact,CAD_area_mm2=got,relative_error=got/exact-1))
analytic_volume=4/3*math.pi*150*50*25
assert abs(adaptive_volume(ell)/analytic_volume-1)<1e-6

tables={};volcheck=[]
for intervals in [134,268]:
    xs=np.linspace(bb.xmin+1e-5,bb.xmax-1e-5,intervals+1)
    areas=np.array([section_area(body,x) for x in xs])
    volume=float(simpson(areas,x=xs));err=abs(volume/body_volume-1)
    volcheck.append(dict(intervals=intervals,section_integrated_volume_mm3=volume,adaptive_CAD_volume_mm3=body_volume,relative_volume_error=err))
    tables[intervals]=(xs,areas)
    print(json.dumps(volcheck[-1]),flush=True)
assert volcheck[-1]['relative_volume_error']<5e-4
xs,areas=tables[268]
with (OUT/'secciones_envolvente.csv').open('w') as f:
    writer=csv.writer(f);writer.writerow(['x_m','area_section_m2','equivalent_circular_diameter_m'])
    writer.writerows((x/1000,a/1e6,math.sqrt(4*a/math.pi)/1000) for x,a in zip(xs,areas))

mesh=[]
for tol in [1.,.5,.25]:
    m=mesh_measures(body,tol);m['relative_surface_area_error']=abs(m['surface_area_mm2']/body_area-1);m['relative_volume_error']=abs(abs(m['signed_volume_mm3'])/body_volume-1);mesh.append(m)
assert mesh[-1]['relative_surface_area_error']<.005 and mesh[-1]['relative_volume_error']<.005
centers=json.loads((ROOT/'vectorizacion_A/RESUMEN.json').read_text())['position_m']
open_body=body;ports=[]
for i,c in enumerate(centers):
    x,y=1000*c[0],1000*c[1]
    cutter=cq.Solid.makeCylinder(42,500,cq.Vector(x,y,-250),cq.Vector(0,0,1))
    removed=body.intersect(cutter)
    external=[f for f in removed.Faces() if f.geomType()!='CYLINDER']
    top=sum(adaptive_area(f) for f in external if f.Center().z>0);bottom=sum(adaptive_area(f) for f in external if f.Center().z<0)
    assert top>0 and bottom>0
    ports.append(dict(channel=i,x_mm=x,y_mm=y,radius_mm=42,planar_projected_area_each_end_m2=math.pi*.042**2,upper_removed_hull_surface_area_m2=top/1e6,lower_removed_hull_surface_area_m2=bottom/1e6,removed_channel_envelope_volume_m3=adaptive_volume(removed)/1e9,external_patch_faces=len(external)))
    open_body=open_body.cut(cutter)
assert body.isValid() and open_body.isValid()
cq.exporters.export(body,str(OUT/'envolvente_cerrada_referencia.step'))
cq.exporters.export(open_body,str(OUT/'envolvente_con_pasajes_84mm.step'))
measured=dict(source_styling_script=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),geometry_scope='Raw closed styling loft before fan-port cuts, accents, nozzle and inserts. Reference with closed envelope, not an installed closed-door vehicle.',integration='OCCT adaptive surface and volume integration, requested relative per-face tolerance 1e-10; numerical geometry, not manufacturing accuracy.',units='SI unless field explicitly says mm',bounds_m=dict(x_min=bb.xmin/1000,x_max=bb.xmax/1000,length=bb.xlen/1000,width=bb.ylen/1000,height=bb.zlen/1000),gross_enclosed_volume_m3=body_volume/1e9,closed_surface_area_m2=body_area/1e6,CAD_default_vs_adaptive_volume_relative_difference=body.Volume()/body_volume-1,max_sampled_section_area_m2=float(max(areas)/1e6),max_section_x_m=float(xs[np.argmax(areas)]/1000),max_equivalent_diameter_m=float(math.sqrt(4*max(areas)/math.pi)/1000),length_over_max_equivalent_diameter=float(bb.xlen/math.sqrt(4*max(areas)/math.pi)),mean_density_if_5kg_over_gross_envelope_kgm3=5/(body_volume/1e9),analytic_section_validation=analytic,analytic_ellipsoid_volume_relative_error=adaptive_volume(ell)/analytic_volume-1,section_volume_checks=volcheck,surface_mesh_checks=mesh,ports=ports,open_reference_volume_m3=adaptive_volume(open_body)/1e9,open_reference_all_boundary_area_m2=adaptive_area(open_body)/1e6,open_area_warning='Open-reference area includes inside passage walls. It is not an external wetted area for applying the closed-body skin-friction estimate.',actual_drag_or_critical_Mach_validated=False)
(OUT/'METROLOGIA.json').write_text(json.dumps(measured,indent=2))
print(json.dumps({k:measured[k] for k in ['gross_enclosed_volume_m3','closed_surface_area_m2','max_sampled_section_area_m2','max_equivalent_diameter_m','length_over_max_equivalent_diameter']}))
