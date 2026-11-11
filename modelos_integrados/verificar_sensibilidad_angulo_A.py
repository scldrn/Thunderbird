"""Independent direct-component wrench and outer-hull coverage checks."""
from pathlib import Path
import itertools,json,math
import numpy as np
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parent/'vectorizacion_A/sensibilidad_angulo'
summary=json.loads((ROOT/'RESUMEN.json').read_text());checks=[]
for item in summary['results']:
 if item['status']!='sufficient_certificate':continue
 r=item['result'];d=np.load(ROOT/(r['name']+'.npz'))
 f=d['force_vectors_N'];target=d['targets_N_Nm'];pos=d['positions_m'];vertices=d['force_polytope_unit_vertices']
 fx,fy,fz=(f[:,:,j] for j in range(3));x=pos[:,0];y=pos[:,1]
 zx=np.asarray(r['lateral_force_lever_z_fx_m']);zy=np.asarray(r['lateral_force_lever_z_fy_m'])
 actual=np.column_stack([fx.sum(1),fy.sum(1),fz.sum(1),(fz*y-fy*zy).sum(1),(fx*zx-fz*x).sum(1),(fy*x-fx*y).sum(1)])
 error=float(abs(actual-target).max());assert error<1e-6
 cap=r['positive_force_capacity_sufficient_N'];delta=math.radians(r['effective_cone_half_angle_deg'])
 assert np.linalg.norm(f,axis=2).max()<=cap+1e-6
 assert fz.min()>=r['preload_signed_vertical_force_N']-1e-6
 assert (np.hypot(fx,fy)-fz*math.tan(delta)).max()<1e-6
 # Hull equations independently demonstrate that the unit ball lies inside.
 eq=ConvexHull(vertices).equations
 distances=-eq[:,-1]/np.linalg.norm(eq[:,:3],axis=1)
 assert distances.min()>=1-1e-9
 torque=r['torque_component_bound_Nm'];corners=np.array(list(itertools.product([-torque,torque],repeat=3)))
 center=np.asarray(r['force_ball_center_N']);radius=r['force_ball_radius_N']
 expected=np.array([np.r_[center+radius*v,t] for v in vertices for t in corners])
 def order(a):return a[np.lexsort(tuple(a[:,j] for j in reversed(range(6))))]
 np.testing.assert_allclose(order(target),order(expected),rtol=0,atol=1e-9)
 checks.append(dict(name=r['name'],vertices=len(target),max_direct_wrench_error=error,minimum_outer_facet_distance=float(distances.min()),cap_force_N=cap))
alpha=.5;point=np.array([alpha*math.sqrt(1-alpha**2),0,1-alpha**2])
np.testing.assert_allclose(np.linalg.norm(point-[0,0,1]),alpha,atol=1e-14)
np.testing.assert_allclose(math.atan2(point[0],point[2]),math.asin(alpha),atol=1e-14)
out=dict(cases_checked=len(checks),vertices_checked=sum(c['vertices'] for c in checks),checks=checks,
 tangent_force_over_mg=point.tolist(),tangent_ball_distance_g=float(np.linalg.norm(point-[0,0,1])),
 tangent_angle_deg=math.degrees(math.atan2(point[0],point[2])),
 interpretation='Numerical allocations and convex coverage verified under ideal positive-cone assumptions; no installed validation.')
(ROOT/'VERIFICACION_INDEPENDIENTE.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
