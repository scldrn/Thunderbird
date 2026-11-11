"""Sufficient continuous wrench coverage for four ideal reversible vector cones.

One fixed checkerboard sign pattern is used throughout each certificate. Never
convexify the union of positive and negative cones of an individual actuator.
The LP cone is an INSIDE approximation. The requested force ball is enclosed in
an OUTSIDE polytope, so testing every Cartesian-product vertex is sufficient
under the declared convex ideal actuator model. This is not a hardware model.
"""
from pathlib import Path
import itertools,json,math,hashlib,time
import numpy as np
from scipy.optimize import linprog
from scipy.spatial import HalfspaceIntersection

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'vectorizacion_A/reversibilidad_6DOF';OUT.mkdir(exist_ok=True)
G=9.80665

def outer_force_polytope(resolution):
    n=np.array([v for v in itertools.product(range(-resolution,resolution+1),repeat=3) if any(v)],float)
    n/=np.linalg.norm(n,axis=1)[:,None]
    n=np.unique(np.round(n,13),axis=0);n/=np.linalg.norm(n,axis=1)[:,None]
    halfspaces=np.c_[n,-np.ones(len(n))*(1+1e-12)]
    v=HalfspaceIntersection(halfspaces,np.zeros(3)).intersections
    assert np.all(-halfspaces[:,3]/np.linalg.norm(n,axis=1)>=1-1e-14)
    assert np.max(n@v.T-1)<1e-8
    return n,v

def cone_rays(delta,azimuths=32,polar_rings=4):
    rays=[[0.,0.,1.]]
    for theta in np.linspace(0,math.radians(delta),polar_rings+1)[1:]:
        for phi in np.arange(azimuths)*2*math.pi/azimuths:
            rays.append([math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)])
    return np.array(rays)

def wrench_matrix(p,z_fx,z_fy):
    """Separate ideal lateral-force lever arms; no measured couple is implied."""
    x,y,_=p
    return np.array([[1,0,0],[0,1,0],[0,0,1],[0,-z_fy,y],[z_fx,0,-x],[-y,x,0]],float)

def certificate(name,mass=5.,additional_acceleration_g=.5,delta=45.,reverse_ratio=1.,z=.058,resolution=1,preload_z=1.,torque_component=.5,scale=1.,lever_z_fx=None,lever_z_fy=None,upright_only=False,center_at_hover=False,positions_m=None):
    start=time.monotonic()
    ref=json.loads((ROOT/'vectorizacion_A/RESUMEN.json').read_text())
    p=np.array(ref['position_m'],float)*scale if positions_m is None else np.array(positions_m,float)
    assert p.shape==(4,3) and np.isfinite(p).all()
    p[:,2]=z
    signs=np.ones(4) if upright_only else np.array([1.,-1.,-1.,1.]);capacity=np.where(signs>0,1.,reverse_ratio)
    rays=cone_rays(delta);K=len(rays);L=1.345*scale
    zx=np.broadcast_to(np.asarray(z if lever_z_fx is None else lever_z_fx,float),(4,))
    zy=np.broadcast_to(np.asarray(z if lever_z_fy is None else lever_z_fy,float),(4,))
    B=np.array([wrench_matrix(pi,x,y) for pi,x,y in zip(p,zx,zy)]);Bscaled=B.copy();Bscaled[:,3:,:]/=L
    Aeq=np.zeros((6,4*K+1));Aub=np.zeros((8,4*K+1));bub=np.r_[np.zeros(4),-np.ones(4)*preload_z]
    signed=rays[None,:,:]*signs[:,None,None]
    for i in range(4):
        Aeq[:,i*K:(i+1)*K]=Bscaled[i]@signed[i].T
        Aub[i,i*K:(i+1)*K]=1;Aub[i,-1]=-capacity[i]
        Aub[4+i,i*K:(i+1)*K]=-rays[:,2]
    cost=np.zeros(4*K+1);cost[-1]=1
    normals,vertices=outer_force_polytope(resolution)
    centered=upright_only or center_at_hover
    radius=mass*G*(additional_acceleration_g if centered else 1+additional_acceleration_g)
    center=mass*G*np.array([0.,0.,1.]) if centered else np.zeros(3)
    torques=np.array(list(itertools.product([-torque_component,torque_component],repeat=3)))
    targets=[];forces=[];required=[];residuals=[]
    for fv in vertices:
        for tau in torques:
            target=np.r_[center+radius*fv,tau/L]
            sol=linprog(cost,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=target,bounds=(0,None),method='highs')
            if not sol.success:raise RuntimeError(f'{name}: missing certificate vertex, status={sol.status}')
            f=np.einsum('ik,ikj->ij',sol.x[:-1].reshape(4,K),signed)
            T=float(sol.x[-1]);err=float(np.max(abs(np.einsum('ijk,ik->j',Bscaled,f)-target)))
            assert err<2e-7
            assert np.max(np.linalg.norm(f,axis=1)-capacity*T)<2e-7
            assert np.min(signs*f[:,2])>=preload_z-2e-7
            assert np.max(np.linalg.norm(f[:,:2],axis=1)-signs*f[:,2]*math.tan(math.radians(delta)))<2e-7
            targets.append(np.r_[center+radius*fv,tau]);forces.append(f);required.append(T);residuals.append(err)
    targets=np.array(targets);forces=np.array(forces);required=np.array(required)
    common=float(max(required)*(1+1e-8));worst=int(np.argmax(required))
    # Reconstruct hundreds of interior convex combinations. The mathematical
    # sufficiency is convexity plus vertex coverage; this is an implementation check.
    rng=np.random.default_rng(63421);max_combo_error=0.
    for _ in range(100):
        ix=rng.choice(len(targets),12,replace=False);w=rng.dirichlet(np.ones(12))
        f=np.einsum('j,jik->ik',w,forces[ix]);target=w@targets[ix]
        actual=np.einsum('ijk,ik->j',B,f)
        max_combo_error=max(max_combo_error,float(max(abs(actual-target))))
        assert max_combo_error<2e-7
        assert np.max(np.linalg.norm(f,axis=1)-capacity*common)<2e-7
        assert np.min(signs*f[:,2])>=preload_z-2e-7
        assert np.max(np.linalg.norm(f[:,:2],axis=1)-signs*f[:,2]*math.tan(math.radians(delta)))<2e-7
    np.savez_compressed(OUT/(name+'.npz'),targets_N_Nm=targets,force_vectors_N=forces,required_positive_capacity_N=required,positions_m=p,wrench_matrices=B,signs=signs,capacity_factors=capacity,force_polytope_normals=normals,force_polytope_unit_vertices=vertices)
    cancellation=1-np.linalg.norm(targets[:,:3],axis=1)/np.linalg.norm(forces,axis=2).sum(axis=1)
    lever_error=.008*np.column_stack([np.abs(forces[:,:,1]).sum(axis=1),np.abs(forces[:,:,0]).sum(axis=1)])
    result=dict(name=name,mass_assumed_kg=mass,scale=scale,CG_assumed_m=[0,0,0],positions_m=p.tolist(),lateral_force_lever_z_fx_m=zx.tolist(),lateral_force_lever_z_fy_m=zy.tolist(),lateral_lever_model='Hypothetical constant lever arms; real vane/duct free couples and centers of pressure are unknown.',attitude_scope='Upright body; three-axis acceleration about hover' if centered else 'Any attitude; force ball is a sufficient superset of gravity plus bounded acceleration',additional_acceleration_bound_g=additional_acceleration_g,force_ball_center_N=center.tolist(),force_ball_radius_N=radius,torque_component_bound_Nm=torque_component,preload_signed_vertical_force_N=preload_z,effective_cone_half_angle_deg=delta,inverse_capacity_ratio=reverse_ratio,fixed_sign_pattern=signs.tolist(),positive_force_capacity_sufficient_N=common,negative_force_capacity_sufficient_N=None if upright_only else reverse_ratio*common,force_vertices=len(vertices),joint_vertices_checked=len(targets),force_outer_polytope_max_radius_factor=float(max(np.linalg.norm(vertices,axis=1))),max_wrench_equilibrium_residual_N_or_Nm_per_m=max(residuals),max_convex_combination_residual_N_or_Nm=max_combo_error,worst_vertex_wrench_N_Nm=targets[worst].tolist(),worst_vertex_force_vectors_N=forces[worst].tolist(),max_force_cancellation_fraction_in_saved_allocations=float(max(cancellation)),moment_error_bound_for_example_8mm_independent_lateral_lever_errors_Nm=lever_error.max(axis=0).tolist(),elapsed_calculation_s=time.monotonic()-start,coverage='Continuous force ball times torque box sufficient in declared ideal fixed-sign convex model; conservative capacity, not exact optimum.',hardware_validated=False)
    (OUT/(name+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['name','positive_force_capacity_sufficient_N','joint_vertices_checked','elapsed_calculation_s']}),flush=True)
    return result

def main():
    results=[]
    for angle in [15,30,45,60]:
        results.append(certificate('angulo_'+str(angle),delta=angle))
    for alpha in [.8,.6]:
        results.append(certificate('inverso_'+str(alpha).replace('.','p'),reverse_ratio=alpha))
    for z in [0.,.029]:
        results.append(certificate('plano_z_'+str(z).replace('.','p'),z=z))
    results.append(certificate('referencia_refinada',resolution=2))
    results.append(certificate('palancas_filas_idealizadas',lever_z_fx=-.040,lever_z_fy=-.012))
    results.append(certificate('palancas_filas_refinadas',lever_z_fx=-.040,lever_z_fy=-.012,resolution=2))
    signs=np.array([1.,-1.,-1.,1.])
    zx=np.where(signs>0,-.039,.037);zy=np.where(signs>0,-.021,.019)
    results.append(certificate('doble_salida_refinada',z=.007,lever_z_fx=zx,lever_z_fy=zy,resolution=2))
    results.append(certificate('doble_salida_inverso_0p6',z=.007,lever_z_fx=zx,lever_z_fy=zy,reverse_ratio=.6,resolution=2))
    results.append(certificate('base_horizontal_5kg',lever_z_fx=-.040,lever_z_fy=-.012,upright_only=True,resolution=2))
    for acceleration in [1,2,5]:
        results.append(certificate(f'reversible_horizontal_{acceleration}g',additional_acceleration_g=acceleration,z=.007,lever_z_fx=zx,lever_z_fy=zy,center_at_hover=True,resolution=2))
    for m in [2.,10.]:
        r=m/5;s=r**(1/3)
        results.append(certificate(f'escala_{int(m)}kg',mass=m,scale=s,z=.058*s,preload_z=r,torque_component=.5*r**(5/3)))
        results.append(certificate(f'doble_salida_{int(m)}kg',mass=m,scale=s,z=.007*s,lever_z_fx=zx*s,lever_z_fy=zy*s,preload_z=r,torque_component=.5*r**(5/3),resolution=2))
        results.append(certificate(f'base_horizontal_{int(m)}kg',mass=m,scale=s,z=.058*s,lever_z_fx=-.040*s,lever_z_fy=-.012*s,preload_z=r,torque_component=.5*r**(5/3),upright_only=True,resolution=2))
    results.append(certificate('aceleracion_1g',additional_acceleration_g=1.))
    summary=dict(method='Inner multi-ring ray polytope per signed actuator; continuous force ball enclosed by outer halfspace polytope; Cartesian product with torque box certified at every vertex.',source_position_file_sha256=hashlib.sha256((ROOT/'vectorizacion_A/RESUMEN.json').read_bytes()).hexdigest(),cases=results,omnidirectional_hardware_validated=False)
    (OUT/'RESUMEN.json').write_text(json.dumps(summary,indent=2))

if __name__=='__main__':main()
