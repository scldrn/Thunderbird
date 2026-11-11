"""Local blade-element loads from disk velocity, without induced-flow closure.

Positive axial direction is downstream; positive theta follows rotor spin.
This is a 2-D-polar screening law, not a validated rotating/cascade model.
"""
import math


def local_loads(radius_m, chord_m, beta_rad, omega_rad_s, axial_at_disk_m_s,
                swirl_at_disk_m_s, blades, rho_kg_m3, polar,
                nu_m2_s=1.46e-5, sound_speed_m_s=340.3):
    values = (radius_m, chord_m, beta_rad, omega_rad_s, axial_at_disk_m_s,
              swirl_at_disk_m_s, rho_kg_m3, nu_m2_s, sound_speed_m_s)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Finite geometry and local flow required')
    if not (radius_m > 0 and chord_m > 0 and omega_rad_s > 0
            and axial_at_disk_m_s > 0 and rho_kg_m3 > 0 and nu_m2_s > 0
            and sound_speed_m_s > 0 and isinstance(blades, int) and blades > 0):
        raise ValueError('Positive forward-flow branch and integer blade count required')
    relative_tangent = omega_rad_s*radius_m-swirl_at_disk_m_s
    if relative_tangent <= 0:
        raise ValueError('Reversed relative tangential flow not identified')
    axial = axial_at_disk_m_s
    speed = math.hypot(axial, relative_tangent)
    phi = math.atan2(axial, relative_tangent)
    alpha = math.degrees(beta_rad-phi)
    reynolds = speed*chord_m/nu_m2_s
    cl, cd, in_domain = polar.lookup(alpha, reynolds)
    if not (math.isfinite(cl) and math.isfinite(cd) and cd >= 0):
        raise ValueError('Finite lift and nonnegative drag coefficient required')
    lift = .5*rho_kg_m3*speed**2*chord_m*blades*cl
    drag = .5*rho_kg_m3*speed**2*chord_m*blades*cd
    axial_force = lift*math.cos(phi)-drag*math.sin(phi)
    theta_force = lift*math.sin(phi)+drag*math.cos(phi)
    torque = radius_m*theta_force
    shaft_power = omega_rad_s*torque
    mean_work = axial_force*axial+theta_force*swirl_at_disk_m_s
    profile_deficit = drag*speed
    return dict(r_m=radius_m, chord_m=chord_m, beta_rad=beta_rad,
                axial_at_disk_m_s=axial, swirl_at_disk_m_s=swirl_at_disk_m_s,
                relative_speed_m_s=speed, phi_rad=phi, alpha_deg=alpha, Re=reynolds,
                Mach_relative=speed/sound_speed_m_s,
                polar_in_domain=bool(in_domain), compressibility_model_present=False,
                dT_dr_N_m=axial_force, dFtheta_dr_N_m=theta_force,
                dQ_dr_Nm_m=torque, shaft_power_per_radius_W_m=shaft_power,
                mean_force_work_per_radius_W_m=mean_work,
                profile_work_deficit_per_radius_W_m=profile_deficit,
                energy_identity_residual_W_m=shaft_power-mean_work-profile_deficit,
                induced_velocity_added=False, rotation_or_duct_validation=False)
