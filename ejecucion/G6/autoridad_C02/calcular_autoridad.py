"""Conservative ideal-force allocation for C02; no installed fan map implied."""
from pathlib import Path
import csv
import hashlib
import json
import math

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONFIG = ROOT/'configuraciones/C02_CANDIDATA.json'
G = 9.80665
MASS = 5.0


def rays(theta_deg, azimuths=16, radial_levels=4):
    result = [[0., 0., 1.]]
    for i in range(1, radial_levels+1):
        theta = math.radians(theta_deg)*i/radial_levels
        for j in range(azimuths):
            phi = 2*math.pi*j/azimuths
            result.append([math.sin(theta)*math.cos(phi), math.sin(theta)*math.sin(phi), math.cos(theta)])
    out = np.array(result)
    np.testing.assert_allclose(np.linalg.norm(out, axis=1), 1., atol=2e-15)
    return out


def matrices(centres, cg, vectors):
    force = np.tile(vectors.T, (1, len(centres)))
    moments = np.concatenate([np.cross(np.broadcast_to(point-cg, vectors.shape), vectors).T
                              for point in centres], axis=1)
    group = np.zeros((len(centres), len(centres)*len(vectors)))
    for i in range(len(centres)):
        group[i, i*len(vectors):(i+1)*len(vectors)] = 1.
    return force, moments, group


def maximize_acceleration(centres, cg, theta_deg, fan_limit_N, roll_moment_Nm=0.):
    vectors = rays(theta_deg)
    f, moments, groups = matrices(centres, cg, vectors)
    # Axis x here is CAD longitudinal; magnitudes are invariant under CAD->FLU.
    aeq = np.vstack([f[1], f[2], moments])
    beq = np.array([0., MASS*G, roll_moment_Nm, 0., 0.])
    result = linprog(-f[0], A_ub=groups, b_ub=np.full(4, fan_limit_N),
                     A_eq=aeq, b_eq=beq, bounds=(0., None), method='highs')
    if not result.success:
        return dict(feasible=False,solver_status=int(result.status),solver_message=result.message)
    values=result.x; per_fan=np.stack([vectors.T@values[i*len(vectors):(i+1)*len(vectors)] for i in range(4)])
    forces=per_fan.sum(axis=0); moment=np.cross(centres-cg,per_fan).sum(axis=0)
    np.testing.assert_allclose(aeq@values,beq,atol=2e-7,rtol=0.)
    assert values.min()>=-1e-9 and (groups@values).max()<=fan_limit_N+1e-7
    assert np.linalg.norm(per_fan,axis=1).max()<=fan_limit_N+1e-7
    np.testing.assert_allclose(moment,[roll_moment_Nm,0.,0.],atol=2e-7)
    assert forces[0] >= -1e-7
    return dict(feasible=True,acceleration_m_s2=float(forces[0]/MASS),
        acceleration_g=float(forces[0]/(MASS*G)),total_force_N=forces.tolist(),total_moment_Nm=moment.tolist(),
        fan_force_vectors_N=per_fan.tolist(),fan_force_magnitudes_N=np.linalg.norm(per_fan,axis=1).tolist(),
        minimum_requested_time_5m_rest_to_rest_s=float(math.sqrt(20/(forces[0]/MASS))) if forces[0]>1e-9 else None,
        displacement_time_is_ideal_symmetric_accel_without_jerk_drag_or_attitude_dynamics=True,
        maximum_allocation_residual=float(np.max(abs(aeq@values-beq))),
        cone_is_hypothesis_not_measured=True,physical_performance_accepted=False)


def min_hover_capacity(centres, cg):
    vectors=rays(45.)
    f,moments,groups=matrices(centres,cg,vectors)
    n=f.shape[1]
    aeq=np.column_stack([np.vstack([f,moments]),np.zeros(6)])
    aub=np.column_stack([groups,-np.ones(4)])
    objective=np.r_[np.zeros(n),1.]
    result=linprog(objective,A_ub=aub,b_ub=np.zeros(4),A_eq=aeq,
        b_eq=[0.,0.,MASS*G,0.,0.,0.],bounds=[(0.,None)]*(n+1),method='highs')
    assert result.success and np.max(abs(aeq@result.x-np.array([0,0,MASS*G,0,0,0])))<2e-7
    return float(result.x[-1])


def main():
    config=json.loads(CONFIG.read_text())
    xy=np.array(config['fan_reference']['centres_xy_m'])
    assert xy.shape==(4,2) and np.allclose(np.sort(np.unique(xy[:,0])),[-.16,.16])
    assert np.allclose(np.sort(np.unique(xy[:,1])),[-.076,.076])
    centres=np.column_stack([xy,np.zeros(4)])
    # Check geometry/solver against independent symmetric-cone and pitch-balance identities.
    theoretical=math.tan(math.radians(35.))
    unlimited=maximize_acceleration(centres,np.zeros(3),35.,1000.)
    np.testing.assert_allclose(unlimited['acceleration_g'],theoretical,rtol=1e-9,atol=1e-9)
    expected=MASS*G/4*(1+.096/.16)
    np.testing.assert_allclose(min_hover_capacity(centres,np.array([.096,0.,0.])),expected,rtol=1e-9)
    rows=[]
    for cg_x in (0.,.04,.08,.096,.12):
        for theta in (35.,45.):
            for limit in (20.58,25.):
                for roll in (0.,.5):
                    result=maximize_acceleration(centres,np.array([cg_x,0.,0.]),theta,limit,roll)
                    row=dict(cg_x_CAD_m=cg_x,cg_z_m=0.,effective_cone_deg_ASSUMED=theta,
                             max_fan_force_N_ASSUMED=limit,roll_moment_Nm_ASSUMED=roll,**result)
                    rows.append(row)
    out=HERE/'salida_r1';assert not out.exists();out.mkdir()
    compact=[{k:v for k,v in r.items() if k not in ('fan_force_vectors_N','fan_force_magnitudes_N',
        'total_force_N','total_moment_Nm','solver_message')} for r in rows]
    with (out/'ESCENARIOS.csv').open('w',newline='') as f:
        keys=sorted(set().union(*(r.keys() for r in compact)));writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader();writer.writerows(compact)
    report=dict(scope='Conditional 5 kg ideal C02 force-allocation comparison; not a real control capability',
        config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        fan_centres_CAD_m=centres.tolist(),fan_force_application_z_assumed_m=0.,mass_kg=MASS,g_m_s2=G,
        ideal_force_ray_azimuths=16,ideal_force_ray_radial_levels=4,convex_hull_inner_approximation=True,
        max_individual_20_58N_origin='prior A ideal sufficient-force scenario, not C02 measured capacity',
        incomplete_C02_geometric_CG_x_m=.09605024872370113,
        incomplete_CG_is_not_a_physical_vehicle_CG=True,
        all_cases_ignore_rotor_reaction_torque_and_gyro=True,
        axial_engine_aerodynamic_forces_and_actuator_lag_omitted=True,
        ideal_hover_pitch_balance_check_pass=True,ideal_unlimited_thrust_cone_check_pass=True,
        solved_cases=len(rows),physical_vehicle_performance_accepted=False,cases=rows)
    (out/'RESULTADOS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    for r in rows:
        if r['max_fan_force_N_ASSUMED']==20.58 and r['effective_cone_deg_ASSUMED']==45.:
            print(r['cg_x_CAD_m'],r['roll_moment_Nm_ASSUMED'],r.get('acceleration_g'),r['feasible'])


if __name__=='__main__':
    main()
