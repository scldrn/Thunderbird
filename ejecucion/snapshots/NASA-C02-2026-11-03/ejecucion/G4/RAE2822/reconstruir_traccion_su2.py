"""Independent wall traction reconstruction from exported native primitives.

Uses edge-neighbour inverse-distance weighted least squares and full 3D
Newtonian stress restricted to planar velocity. The saved primitive gradients
may lag the segregated update, so differences are measured, never fitted away.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

import numpy as np
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy

from auditar_malla_su2 import read_mesh
from auditar_su2 import table
from flujo_frontera_su2 import farfield_state, outlet_state, roe_flux, verify_analytic_fluxes


def boundary_cycle(edges, xy):
    adjacency = {}
    for a, b in edges:
        adjacency.setdefault(a, []).append(b)
        adjacency.setdefault(b, []).append(a)
    assert all(len(v) == 2 for v in adjacency.values())
    cycle = [min(adjacency)]
    previous, current = None, cycle[0]
    while True:
        following = next(i for i in adjacency[current] if i != previous)
        if following == cycle[0]:
            break
        assert following not in cycle
        cycle.append(following)
        previous, current = current, following
    assert len(cycle) == len(adjacency)
    cycle = np.array(cycle)
    poly = xy[cycle]
    area = np.sum(poly[:, 0]*np.roll(poly[:, 1], -1)-poly[:, 1]*np.roll(poly[:, 0], -1))
    return cycle if area > 0 else cycle[::-1]


def gradient_at_nodes(xy, values, neighbours, selected):
    result = []
    conditions = []
    for i in selected:
        near = np.array(sorted(neighbours[i]))
        delta = xy[near] - xy[i]
        radius = np.linalg.norm(delta, axis=1)
        assert (radius > 0).all()
        A = delta/radius[:, None]
        b = (values[near] - values[i])/radius[:, None]
        # QR/SVD avoids explicitly squaring the condition number.
        grad, _, rank, singular = np.linalg.lstsq(A, b, rcond=None)
        assert rank == 2
        result.append(grad.T)
        conditions.append(singular[0]/singular[-1])
    return np.asarray(result), np.asarray(conditions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, required=True)
    args = parser.parse_args()
    case = args.case.resolve()
    terminal = json.loads((case/'EJECUCION.json').read_text())
    assert terminal['stage'] == 'solver_exited' and terminal['exit_code'] == 0
    audit = json.loads((case/'AUDITORIA_SU2.json').read_text())
    inputs = json.loads((case/'ENTRADAS.json').read_text())
    cond = inputs['declared_conditions']
    config = dict(re.findall(r'^\s*([A-Z0-9_]+)\s*=\s*([^%\n]+)', (case/'case.cfg').read_text(), re.M))
    config = {k:v.strip() for k,v in config.items()}
    assert inputs['source_SU2_version'] == '8.6.0'
    assert config['CONV_NUM_METHOD_FLOW'] == 'JST' and config['KIND_TURB_MODEL'] == 'SST'
    assert float(config.get('ROE_KAPPA', '.5')) == .5
    assert float(config.get('ENTROPY_FIX_COEFF', '.001')) == .001
    assert config.get('AXISYMMETRIC', 'NO') == 'NO'
    assert config.get('GRID_MOVEMENT', 'NO') == 'NO'
    assert 'MARKER_WALL_FUNCTIONS' not in config and 'MARKER_WALL_ROUGHNESS' not in config
    xy, cells, markers = read_mesh(case/'mesh_RAE2822_turb.su2')
    neighbours = [set() for _ in xy]
    for cell in cells:
        for a, b in zip(cell, cell[1:]+cell[:1]):
            neighbours[a].add(b)
            neighbours[b].add(a)
    reader = vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(case/'flow.vtu'))
    reader.Update()
    grid = reader.GetOutput()
    coords = vtk_to_numpy(grid.GetPoints().GetData())[:, :2]
    a, b = np.lexsort((coords[:, 1], coords[:, 0])), np.lexsort((xy[:, 1], xy[:, 0]))
    np.testing.assert_allclose(coords[a], xy[b], rtol=0, atol=1e-12)
    mapping = np.empty(len(xy), dtype=int)
    mapping[b] = a
    def field(name):
        data = vtk_to_numpy(grid.GetPointData().GetArray(name))[mapping]
        assert np.isfinite(data).all()
        return data
    velocity = field('Velocity')[:, :2]
    cycle = boundary_cycle(markers['AIRFOIL'], xy)
    edge = np.roll(xy[cycle], -1, axis=0)-xy[cycle]
    edge_normal = np.column_stack((edge[:, 1], -edge[:, 0]))
    dual_normal = .5*(edge_normal+np.roll(edge_normal, 1, axis=0))
    dual_area = np.linalg.norm(dual_normal, axis=1)
    unit = dual_normal/dual_area[:, None]
    np.testing.assert_allclose(dual_normal.sum(axis=0), 0, atol=1e-14)
    # Independent divergence-theorem reference: p=x gives force=(-area,0).
    poly = xy[cycle]
    polygon_area = .5*np.sum(poly[:, 0]*np.roll(poly[:, 1], -1)
                              - poly[:, 1]*np.roll(poly[:, 0], -1))
    analytic_pressure_force = -np.sum(poly[:, 0, None]*dual_normal, axis=0)
    np.testing.assert_allclose(analytic_pressure_force, [-polygon_area, 0], rtol=1e-12, atol=1e-14)
    gradients, conditioning = gradient_at_nodes(xy, velocity, neighbours, cycle)
    # Analytic manufactured affine velocity on the same wall stencil.
    known = np.array([[2., -3.], [4., .5]])
    affine = xy@known.T + np.array([.7, -.4])
    affine_grad, _ = gradient_at_nodes(xy, affine, neighbours, cycle)
    np.testing.assert_allclose(affine_grad, np.broadcast_to(known, affine_grad.shape), atol=1e-7, rtol=1e-7)
    mu = field('Laminar_Viscosity')[cycle]
    divergence = np.trace(gradients, axis1=1, axis2=2)
    tau = mu[:, None, None]*(gradients+gradients.transpose(0, 2, 1)
                            - (2/3)*divergence[:, None, None]*np.eye(2))
    traction = np.einsum('nij,nj->ni', tau, unit)
    normal_scalar = np.einsum('ni,ni->n', traction, unit)
    tangential = traction-normal_scalar[:, None]*unit
    q = audit['reconstructed_reference']['q_Pa']
    cp = field('Pressure_Coefficient')[cycle]
    pressure = -np.sum(cp[:, None]*dual_normal, axis=0)/cond['chord']
    viscous = np.sum(traction*dual_area[:, None], axis=0)/(q*cond['chord'])
    viscous_tangent = np.sum(tangential*dual_area[:, None], axis=0)/(q*cond['chord'])
    history = table(case/'history.csv')
    solver_force = np.array([history['CFx'][-1], history['CFy'][-1]])
    cf = field('Skin_Friction_Coefficient')[cycle, :2]
    mismatch_cf = tangential/q-cf
    alpha = np.deg2rad(cond['alpha_deg'])
    def to_drag_lift(force):
        return np.array([np.cos(alpha)*force[0]+np.sin(alpha)*force[1],
                         -np.sin(alpha)*force[0]+np.cos(alpha)*force[1]])
    total = pressure+viscous
    # History has ten significant decimal digits; 1e-8 is a reporting/stencil
    # consistency threshold, not a physical uncertainty or momentum balance.
    force_atol, cf_atol = 1e-8, 1e-10
    force_match = bool(np.max(abs(total-solver_force)) <= force_atol)
    cf_match = bool(np.max(abs(mismatch_cf)) <= cf_atol)
    # Exterior physical flux diagnostic. Native numerical Riemann fluxes and
    # artificial dissipation are not exported, so this is not their exact sum.
    outer_edges = [e for name, values in markers.items() if name != 'AIRFOIL' for e in values]
    outer = boundary_cycle(outer_edges, xy)
    outer_edge = np.roll(xy[outer], -1, axis=0)-xy[outer]
    outer_edge_normal = np.column_stack((outer_edge[:, 1], -outer_edge[:, 0]))
    outer_dual_normal = .5*(outer_edge_normal+np.roll(outer_edge_normal, 1, axis=0))
    np.testing.assert_allclose(outer_dual_normal.sum(axis=0), 0, atol=1e-12)
    rho_outer = field('Density')[outer]
    u_outer = velocity[outer]
    grad_outer, _ = gradient_at_nodes(xy, velocity, neighbours, outer)
    mu_outer = (field('Laminar_Viscosity')+field('Eddy_Viscosity'))[outer]
    div_outer = np.trace(grad_outer, axis1=1, axis2=2)
    tau_outer = mu_outer[:, None, None]*(grad_outer+grad_outer.transpose(0, 2, 1)
        - (2/3)*div_outer[:, None, None]*np.eye(2))
    pressure_outer = np.sum(field('Pressure_Coefficient')[outer, None]*outer_dual_normal, axis=0)/cond['chord']
    viscous_outer = np.einsum('nij,nj->i', tau_outer, outer_dual_normal)/(q*cond['chord'])
    mass_lumped = np.sum(rho_outer*np.einsum('ni,ni->n', u_outer, outer_dual_normal))
    conv_lumped = np.sum((rho_outer*np.einsum('ni,ni->n', u_outer, outer_dual_normal))[:, None]*u_outer, axis=0)
    mass_gauss, conv_gauss = 0., np.zeros(2)
    # Two-point Gauss exactly integrates products of linearly interpolated
    # rho,U along each straight edge (degree<=3 for momentum).
    for xi in (.5-.5/np.sqrt(3), .5+.5/np.sqrt(3)):
        rho_g = (1-xi)*rho_outer+xi*np.roll(rho_outer, -1)
        u_g = (1-xi)*u_outer+xi*np.roll(u_outer, -1, axis=0)
        mdot = rho_g*np.einsum('ni,ni->n', u_g, outer_edge_normal)
        mass_gauss += .5*mdot.sum()
        conv_gauss += .5*np.sum(mdot[:, None]*u_g, axis=0)
    uniform_velocity = np.array([2., -3.])
    uniform_mdot = outer_dual_normal@uniform_velocity
    np.testing.assert_allclose(np.sum(uniform_mdot[:, None]*uniform_velocity, axis=0), 0, atol=1e-12)
    reference = audit['reconstructed_reference']
    mass_scale = reference['rho_kg_m3']*reference['U_m_s']*cond['chord']
    cv = dict(scope='Physical flux reconstruction on saved primitives, not exact assembled numerical residual',
        SST2003m_isotropic_k_stress_excluded_as_in_native_diffusion=True,
        mass_flux_kg_m_s=dict(vertex_lumped=float(mass_lumped), linear_edge_Gauss=float(mass_gauss)),
        mass_flux_relative_rho_U_chord=dict(vertex_lumped=float(mass_lumped/mass_scale),
            linear_edge_Gauss=float(mass_gauss/mass_scale)),
        outer_pressure_coeff_force=pressure_outer.tolist(), outer_viscous_coeff_force=viscous_outer.tolist(),
        outward_convective_momentum_coeff=dict(vertex_lumped=(conv_lumped/(q*cond['chord'])).tolist(),
            linear_edge_Gauss=(conv_gauss/(q*cond['chord'])).tolist()),
        momentum_defect_coeff=dict(vertex_lumped=(total+pressure_outer-viscous_outer+conv_lumped/(q*cond['chord'])).tolist(),
            linear_edge_Gauss=(total+pressure_outer-viscous_outer+conv_gauss/(q*cond['chord'])).tolist()),
        uniform_flux_analytic_reference_verified=True,
        numerical_flux_and_artificial_dissipation_not_reconstructed=True,
        global_balance_accepted=False)
    gamma = cond.get('gamma', 1.4)
    phi = np.deg2rad(cond['alpha_deg'])
    U_inf = reference['U_m_s']*np.array([np.cos(phi), np.sin(phi)])
    k_inf = 1.5*reference['U_m_s']**2*cond['turbulence_intensity']**2
    freestream = np.array([reference['rho_kg_m3'], *U_inf, reference['p_Pa'], k_inf])
    # Keep corner normals separate for each marker, as in the native boundary
    # vertex storage. Combining markers before the Riemann state is nonlinear.
    edge_normal_by_key = {tuple(sorted((int(i), int(j)))): normal
        for i, j, normal in zip(outer, np.roll(outer, -1), outer_edge_normal)}
    outer_position = {int(i): j for j, i in enumerate(outer)}
    raw_rho, raw_p, raw_k = field('Density'), field('Pressure'), field('Turb_Kin_Energy')
    roe_total, roe_viscous = np.zeros(4), np.zeros(2)
    marker_results = {}
    assert set(markers)-{'AIRFOIL'} <= {'FARFIELD', 'OUTFLOW'}
    for name, boundary_edges in markers.items():
        if name == 'AIRFOIL':
            continue
        normals = {}
        for i, j in boundary_edges:
            normal = edge_normal_by_key[tuple(sorted((i, j)))]
            for at in (i, j):
                normals[at] = normals.get(at, np.zeros(2))+.5*normal
        convective, viscous = np.zeros(4), np.zeros(2)
        for at, normal in normals.items():
            state = np.array([raw_rho[at], *velocity[at], raw_p[at], raw_k[at]])
            ghost = (farfield_state(state, freestream, normal, gamma) if name == 'FARFIELD'
                     else outlet_state(state, freestream, normal, gamma))
            convective += roe_flux(state, ghost, normal, gamma)
            # CDriver uses uncorrected average gradients on the far boundary;
            # BC_Outlet omits the viscous term in the pinned source.
            if name == 'FARFIELD':
                viscous += tau_outer[outer_position[at]]@normal
        roe_total += convective
        roe_viscous += viscous
        marker_results[name] = dict(vertices=len(normals),
            convective_mass_kg_m_s=float(convective[0]),
            convective_plus_pressure_momentum_N_m=convective[1:3].tolist(),
            viscous_momentum_N_m=viscous.tolist())
    numerical_defect = total+(roe_total[1:3]-roe_viscous)/(q*cond['chord'])
    cv['Roe_characteristic_reconstruction'] = dict(
        analytic_checks=verify_analytic_fluxes(),
        assumed_pinned_defaults=dict(ROE_KAPPA=.5, ENTROPY_FIX_COEFF=.001),
        marker_fluxes=marker_results,
        mass_flux_kg_m_s=float(roe_total[0]),
        mass_flux_relative_rho_U_chord=float(roe_total[0]/mass_scale),
        momentum_defect_coeff=numerical_defect.tolist(),
        momentum_defect_norm_over_q_chord=float(np.linalg.norm(numerical_defect)),
        directly_exported_native_numerical_flux=False,
        full_native_assembly_identity_not_asserted=True,
        source_notes='JST boundaries use CUpwRoe_Flow with characteristic BC_Far_Field/BC_Outlet; fixed ideal gas, mesh and smooth wall only.')
    report = dict(
        scope='Independent polygon dual-normal/full-stress reconstruction; not global numerical momentum closure or physical validation',
        wall_nodes=len(cycle), method='WLS weights1/r^2, edge connectivity, smooth adiabatic wall, fullTau=mu*(gradU+gradU^T-2/3divU*I)',
        analytic_affine_stencil_verified=True,
        analytic_linear_pressure_force_verified=True,
        affine_max_gradient_error=float(abs(affine_grad-known).max()),
        wall_stencil_condition_range=[float(conditioning.min()), float(conditioning.max())],
        dual_normal_sum_m=dual_normal.sum(axis=0).tolist(),
        force_coeff_pressure=pressure.tolist(), force_coeff_full_viscous=viscous.tolist(),
        force_coeff_tangential_viscous=viscous_tangent.tolist(),
        force_coeff_normal_viscous=(viscous-viscous_tangent).tolist(),
        independently_reconstructed_CD_CL=to_drag_lift(total).tolist(),
        solver_CD_CL=[float(history['CD'][-1]), float(history['CL'][-1])],
        complete_traction_minus_solver_coeff_force=(total-solver_force).tolist(),
        reconstructed_Cf_minus_exported_max_abs=float(abs(mismatch_cf).max()),
        reconstructed_Cf_minus_exported_RMS=float(np.sqrt(np.mean(mismatch_cf**2))),
        solver_surface_force_reconstruction_verified=force_match and cf_match,
        consistency_tolerances=dict(force_coefficient_absolute=force_atol, Cf_absolute=cf_atol),
        global_momentum_closure_verified=False,
        exterior_physical_CV_diagnostic=cv,
        limitations=['Saved primitive gradients are reconstructed, not exported at the exact native force-assembly stage.',
            'Wall functions, roughness, QCR, moving walls, multizone/MPI and nonplanar cases are outside this implementation.',
            'No exterior flux/discrete residual closure, mesh independence, or experimental validation follows from agreement.'],
        source_formula='https://github.com/su2code/SU2/blob/v8.6.0/SU2_CFD/include/solvers/CFVMFlowSolverBase.inl',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       (case/'flow.vtu', case/'history.csv', case/'mesh_RAE2822_turb.su2',
                        case/'case.cfg', Path(__file__), Path(__file__).with_name('flujo_frontera_su2.py'))})
    (case/'TRACCION_RECONSTRUIDA.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('solver_surface_force_reconstruction_verified', 'affine_max_gradient_error', 'independently_reconstructed_CD_CL',
        'complete_traction_minus_solver_coeff_force', 'reconstructed_Cf_minus_exported_max_abs')}, indent=2))


if __name__ == '__main__':
    main()
