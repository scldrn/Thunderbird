"""Planar, stationary ideal-gas Roe/characteristic boundary reconstruction.

Restricted to the unchanged SU2 JST case defaults: Roe kappa0.5, entropy
fix0.001, no low-dissipation/grid motion. Not a general replacement solver.
"""
import numpy as np


def conservative(state, gamma):
    rho, u, v, p, k = state
    return np.array([rho, rho*u, rho*v, p/(gamma-1)+rho*(.5*(u*u+v*v)+k)])


def physical_flux(state, normal, gamma):
    rho, u, v, p, _ = state
    un = np.dot([u, v], normal)
    U = conservative(state, gamma)
    return np.array([rho*un, rho*u*un+p*normal[0], rho*v*un+p*normal[1], (U[3]+p)*un])


def roe_flux(left, right, normal, gamma=1.4, entropy_fix=.001):
    area = np.linalg.norm(normal)
    n = normal/area
    UL, UR = conservative(left, gamma), conservative(right, gamma)
    weights = np.sqrt([left[0], right[0]])
    velocity = (weights[0]*left[1:3]+weights[1]*right[1:3])/weights.sum()
    H = (weights[0]*(UL[3]+left[3])/left[0]
         + weights[1]*(UR[3]+right[3])/right[0])/weights.sum()
    ke = .5*velocity@velocity
    a = np.sqrt((gamma-1)*(H-ke))
    un = velocity@n
    tangent = np.array([n[1], -n[0]])
    P = np.column_stack(([1., *velocity, ke],
        [0., *tangent, velocity@tangent],
        [1., *(velocity+a*n), H+a*un],
        [1., *(velocity-a*n), H-a*un]))
    eigenvalues = np.maximum(abs(np.array([un, un, un+a, un-a])), entropy_fix*(abs(un)+a))
    dissipation = P@(eigenvalues*np.linalg.solve(P, UR-UL))
    return .5*(physical_flux(left, normal, gamma)+physical_flux(right, normal, gamma)-area*dissipation)


def farfield_state(state, freestream, normal, gamma=1.4):
    rho, u, v, p, _ = state
    rhoi, ui, vi, pi, ki = freestream
    n = normal/np.linalg.norm(normal)
    velocity, infinity = np.array([u, v]), np.array([ui, vi])
    vn, vni = velocity@n, infinity@n
    a, ai = np.sqrt(gamma*p/rho), np.sqrt(gamma*pi/rhoi)
    plus = vn+2*a/(gamma-1) if vni > -ai else vni+2*ai/(gamma-1)
    minus = vn-2*a/(gamma-1) if vni > ai else vni-2*ai/(gamma-1)
    new_vn, new_a = .5*(plus+minus), .25*(gamma-1)*(plus-minus)
    if vni > 0:
        new_u = velocity+(new_vn-vn)*n
        entropy = rho**gamma/p
    else:
        new_u = infinity+(new_vn-vni)*n
        entropy = rhoi**gamma/pi
    new_rho = (entropy*new_a**2/gamma)**(1/(gamma-1))
    return np.array([new_rho, *new_u, new_rho*new_a**2/gamma, ki])


def outlet_state(state, freestream, normal, gamma=1.4):
    rho, u, v, p, _ = state
    n = normal/np.linalg.norm(normal)
    velocity = np.array([u, v])
    a = np.sqrt(gamma*p/rho)
    if np.linalg.norm(velocity)/a >= 1:
        return state.copy()
    entropy = p/rho**gamma
    Rplus = velocity@n+2*a/(gamma-1)
    new_rho = (freestream[3]/entropy)**(1/gamma)
    new_a = np.sqrt(gamma*freestream[3]/new_rho)
    new_velocity = velocity+(Rplus-2*new_a/(gamma-1)-velocity@n)*n
    return np.array([new_rho, *new_velocity, freestream[3], freestream[4]])


def verify_analytic_fluxes():
    state = np.array([1.2, 25., -3., 100000., .2])
    other = np.array([1.1, 23., -2., 101000., .3])
    n = np.array([.3, -.7])
    np.testing.assert_allclose(roe_flux(state, state, n), physical_flux(state, n, 1.4), rtol=1e-12, atol=1e-10)
    np.testing.assert_allclose(roe_flux(state, other, n), -roe_flux(other, state, -n), rtol=1e-12, atol=1e-10)
    # Supersonic moving contact: same p/u/k=0, density jump, upwind flux exact.
    left = np.array([1.2, 1000., 0., 100000., 0.])
    right = np.array([.9, 1000., 0., 100000., 0.])
    np.testing.assert_allclose(roe_flux(left, right, np.array([1., 0.])),
                               physical_flux(left, np.array([1., 0.]), 1.4), rtol=1e-12, atol=1e-7)
    np.testing.assert_allclose(farfield_state(state, state, n), state, rtol=1e-12, atol=1e-9)
    np.testing.assert_allclose(outlet_state(state, state, n), state, rtol=1e-12, atol=1e-9)
    return dict(equal_state_flux=True, orientation_antisymmetry=True,
        supersonic_contact_upwind=True, uniform_characteristic_states=True)
