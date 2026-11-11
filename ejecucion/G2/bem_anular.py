"""Independent annular momentum solve for hover and positive axial throughflow.

Generalises the C01 algebra without changing its frozen design calculations.
This is a screening/verification model, not installed/reverse-flow validation.
"""
import numpy as np
from scipy.optimize import least_squares


def solve_annulus(radius_m, chord_m, beta_rad, rotor_radius_m, hub_radius_m,
                  omega_rad_s, axial_inflow_m_s, blades, rho_kg_m3, polar,
                  nu_m2_s=1.46e-5, sound_speed_m_s=340.3):
    if not (0 < hub_radius_m < radius_m < rotor_radius_m and chord_m > 0
            and omega_rad_s > 0 and axial_inflow_m_s >= 0 and blades > 0 and rho_kg_m3 > 0):
        raise ValueError('Positive forward-flow operating branch and interior radius required')
    r, c, R, h = radius_m, chord_m, rotor_radius_m, hub_radius_m
    V, omega, rho = axial_inflow_m_s, omega_rad_s, rho_kg_m3
    tip = omega*R
    scale_t = rho*tip**2*R

    def evaluate(x):
        u, swirl = x*tip
        axial = V+u
        tangent = omega*r-swirl
        phi = np.arctan2(axial, tangent)
        alpha = np.degrees(beta_rad-phi)
        speed = np.hypot(axial, tangent)
        cl, cd, angle_domain = polar.lookup(alpha, speed*c/nu_m2_s)
        sin_phi = max(np.sin(phi), 1e-12)
        Ftip = 2/np.pi*np.arccos(np.exp(-blades/2*(R-r)/(r*sin_phi)))
        Fhub = 2/np.pi*np.arccos(np.exp(-blades/2*(r-h)/(h*sin_phi)))
        F = Ftip*Fhub
        lift = .5*rho*speed**2*c*blades*cl
        drag = .5*rho*speed**2*c*blades*cd
        thrust = lift*np.cos(phi)-drag*np.sin(phi)
        torque = r*(lift*np.sin(phi)+drag*np.cos(phi))
        residual = [(thrust-4*np.pi*rho*r*F*u*axial)/scale_t,
                    (torque-4*np.pi*rho*r*r*F*axial*swirl)/(scale_t*R)]
        return residual, dict(r_m=r, chord_m=c, beta_rad=beta_rad,
                              alpha_deg=float(alpha), phi_rad=float(phi),
                              u_m_s=float(u), swirl_at_disk_raw_m_s=float(swirl),
                              axial_at_disk_m_s=float(axial), Re=float(speed*c/nu_m2_s),
                              Mach_relative=float(speed/sound_speed_m_s),
                              polar_flag=bool(angle_domain), loss_F=float(F),
                              dT_dr_N_m=float(thrust), dQ_dr_Nm_m=float(torque),
                              profile_power_per_radius_W_m=float(drag*speed))
    low_u = -0.95*V/tip if V > 0 else 1e-6
    low_swirl = -.8*r/R if V > 0 else 1e-7
    initial = [.12, min(.025, .5*r/R)]
    solution = least_squares(lambda x: evaluate(x)[0], initial,
                             bounds=([low_u, low_swirl], [.8, .8*r/R]),
                             ftol=1e-12, xtol=1e-12, gtol=1e-12, max_nfev=500)
    residual, row = evaluate(solution.x)
    row['max_normalized_balance_residual'] = float(np.max(abs(np.asarray(residual))))
    row['solve_success'] = bool(solution.success and row['max_normalized_balance_residual'] < 1e-6)
    mechanical = omega*row['dQ_dr_Nm_m']
    reconstructed = (row['axial_at_disk_m_s']*row['dT_dr_N_m']
                     + row['swirl_at_disk_raw_m_s']/r*row['dQ_dr_Nm_m']
                     + row['profile_power_per_radius_W_m'])
    row['energy_identity_absolute_residual_W_m'] = float(abs(mechanical-reconstructed))
    return row
