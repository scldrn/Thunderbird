"""Independent saved-array/domain check bridged to the CAD stack coordinates."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
import cadquery as cq

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'vectorizacion_A/reversibilidad_6DOF'
(OUT/'VERIFICACION_INDEPENDIENTE.json').write_text(json.dumps(dict(status='checking_current_files',ideal_model_checks_passed=False,physical_flight_validated=False)))
cadpath=ROOT/'vectorizacion_A/CAD_doble_flujo/VERIFICACION.json'
cad=json.loads(cadpath.read_text());rows={a['name']:a['z_mm']/1000 for a in cad['rows']}
base_step=ROOT/'vectorizacion_A/CAD_modulo/neutro.step'
row_z={'X':[],'Y':[]}
for shape,name,loc,_ in cq.Assembly.load(str(base_step)):
    label=name.split('/')[-1]
    if label.startswith('alabe_'):
        axis=label.split('_')[2];row_z[axis].append(shape.moved(loc).Center().z/1000)
assert all(np.std(a)<1e-10 for a in row_z.values())
base_z={k:float(np.mean(v)) for k,v in row_z.items()}
ref=np.array(json.loads((ROOT/'vectorizacion_A/RESUMEN.json').read_text())['position_m'])
checks=[]
for name in ['doble_salida_refinada','doble_salida_inverso_0p6','doble_salida_2kg','doble_salida_10kg','base_horizontal_5kg','base_horizontal_2kg','base_horizontal_10kg','reversible_horizontal_1g','reversible_horizontal_2g','reversible_horizontal_5g']:
    meta=json.loads((OUT/(name+'.json')).read_text());p=OUT/(name+'.npz');d=np.load(p)
    f=d['force_vectors_N'];w=d['targets_N_Nm'];s=d['signs'];scale=meta['scale']
    upright=name.startswith('base_horizontal_')
    assert np.array_equal(s,[1,1,1,1] if upright else [1,-1,-1,1])
    expected_xy=ref[:,:2]*scale;np.testing.assert_allclose(d['positions_m'][:,:2],expected_xy,atol=1e-12)
    zx=np.ones(4)*base_z['Y']*scale if upright else np.where(s>0,rows['inferior_Y'],rows['superior_Y'])*scale
    zy=np.ones(4)*base_z['X']*scale if upright else np.where(s>0,rows['inferior_X'],rows['superior_X'])*scale
    np.testing.assert_allclose(meta['lateral_force_lever_z_fx_m'],zx,atol=1e-12)
    np.testing.assert_allclose(meta['lateral_force_lever_z_fy_m'],zy,atol=1e-12)
    x=expected_xy[:,0];y=expected_xy[:,1]
    # Explicit component equations, independent of the stored wrench matrices.
    moment=np.column_stack([(y*f[:,:,2]-zy*f[:,:,1]).sum(axis=1),(zx*f[:,:,0]-x*f[:,:,2]).sum(axis=1),(x*f[:,:,1]-y*f[:,:,0]).sum(axis=1)])
    residual=float(np.max(abs(np.c_[f.sum(axis=1),moment]-w)));assert residual<1e-7
    limits=meta['positive_force_capacity_sufficient_N']*d['capacity_factors']
    assert np.max(np.linalg.norm(f,axis=2)-limits)<1e-7
    assert np.min(f[:,:,2]*s)>=meta['preload_signed_vertical_force_N']-1e-7
    angle=np.arctan2(np.linalg.norm(f[:,:,:2],axis=2),s*f[:,:,2])
    assert angle.max()<=np.radians(meta['effective_cone_half_angle_deg'])+1e-7
    # Reconstruct convex hull facets from stored vertices, rather than trusting
    # the construction halfspaces or a 'pass' field in the generator report.
    v=d['force_polytope_unit_vertices'];h=ConvexHull(v)
    distances=-h.equations[:,3]/np.linalg.norm(h.equations[:,:3],axis=1)
    assert min(distances)>=1-1e-8
    force_unique=np.unique(np.round(w[:,:3],8),axis=0)
    assert len(force_unique)==len(v) and len(w)==len(v)*8
    mg=meta['mass_assumed_kg']*9.80665
    centered=upright or name.startswith('reversible_horizontal_')
    expected_center=np.array([0,0,mg]) if centered else np.zeros(3)
    expected_radius=mg*(meta['additional_acceleration_bound_g'] if centered else 1+meta['additional_acceleration_bound_g'])
    np.testing.assert_allclose(meta['force_ball_center_N'],expected_center,atol=1e-10)
    assert abs(meta['force_ball_radius_N']-expected_radius)<1e-9
    normalized=(force_unique-expected_center)/expected_radius
    assert cKDTree(normalized).query(v)[0].max()<1e-7
    for force in force_unique:
        ix=np.linalg.norm(w[:,:3]-force,axis=1)<1e-7
        t=w[ix,3:];assert len(t)==8 and len(np.unique(t,axis=0))==8
        np.testing.assert_allclose(abs(t),meta['torque_component_bound_Nm'],atol=1e-10)
    checks.append(dict(name=name,joint_vertices_checked=len(w),wrench_equilibrium_max_error_N_or_Nm=residual,reconstructed_force_hull_min_facet_distance_in_unit_radius=float(min(distances)),max_force_direction_angle_deg=float(np.degrees(angle.max())),npz_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),geometry_bridge_checked=True))
trajectory_checks=[]
demands={'x_minus':[-.5,0,1],'x_plus':[.5,0,1],'y_minus':[0,-.5,1],'y_plus':[0,.5,1],'z_low':[0,0,.5],'z_high':[0,0,1.5]}
for file in sorted(OUT.glob('*TRANSITORIOS_100ms*.npz')):
    meta= json.loads(file.with_name(file.name.replace('TRANSITORIOS_100ms','TRANSITORIOS_IDEALES').replace('.npz','.json')).read_text())
    source=np.load(OUT/meta['source']);source_meta=json.loads((OUT/meta['source']).with_suffix('.json').read_text())
    ss=source['signs'];limits=source['capacity_factors']*source_meta['positive_force_capacity_sufficient_N'];B=source['wrench_matrices']
    data=np.load(file);t=data['time_s'];beta=.5*(1-np.cos(np.pi*t/.1));maxerror=0.;n=0
    for a,b in [('x_minus','x_plus'),('y_minus','y_plus'),('x_plus','y_plus'),('z_low','z_high')]:
        target=(1-beta[:,None])*np.r_[np.array(demands[a])*5*9.80665,[0,0,0]]+beta[:,None]*np.r_[np.array(demands[b])*5*9.80665,[0,0,0]]
        for suffix in ['_forces_N','_slew_balanced_forces_N','_high_bias_forces_N']:
            f=data[a+'_to_'+b+suffix]
            np.testing.assert_allclose(f,(1-beta[:,None,None])*f[0]+beta[:,None,None]*f[-1],atol=1e-8)
            error=float(np.max(abs(np.einsum('ijk,nik->nj',B,f)-target)));maxerror=max(maxerror,error);assert error<1e-7
            assert np.max(np.linalg.norm(f,axis=2)-limits)<1e-7
            assert np.min(f[:,:,2]*ss)>=meta['selected_endpoint_preload_signed_vertical_N']-2e-7
            assert np.max(np.linalg.norm(f[:,:,:2],axis=2)-f[:,:,2]*ss)<1e-7 # 45 degrees
            n+=len(f)
    trajectory_checks.append(dict(file=file.name,trajectory_states_checked=n,max_equilibrium_residual_N_or_Nm=maxerror,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
report=dict(status='completed',CAD_coordinates_source_sha256=hashlib.sha256(cadpath.read_bytes()).hexdigest(),base_vane_neutral_step_sha256=hashlib.sha256(base_step.read_bytes()).hexdigest(),base_vane_centers_z_m_from_STEP=base_z,checks=checks,trajectory_checks=trajectory_checks,ideal_model_checks_passed=True,physical_flight_validated=False,scope='Saved arrays satisfy ideal constraints and a continuous sufficient-domain construction with assumed CAD-centered lateral lever arms. A numerical tolerance check is not formal interval verification, and CAD row centers are not measured aerodynamic centers of pressure.')
(OUT/'VERIFICACION_INDEPENDIENTE.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(cases=len(checks),joint_vertices=sum(a['joint_vertices_checked'] for a in checks),max_error=max(a['wrench_equilibrium_max_error_N_or_Nm'] for a in checks),physical_flight_validated=False)))
