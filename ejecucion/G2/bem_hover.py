"""Annular blade-element/momentum screening in hover, with angular momentum.

The SD8020 2D polar is experimental; rotating/cascade/compressible corrections
are NOT validated. Endpoint extension is used for solving only and reported.
This is not the installed force or power map of the A07.
"""
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[2]


class Polar:
    def __init__(self, path=None):
        self.path = Path(path) if path else ROOT / "fuentes/uiuc/SD8020.DRG"
        self.blocks = []
        for block in self.path.read_text().split("Average Reynolds #:")[1:]:
            lines = block.strip().splitlines()
            values = []
            for line in lines[1:]:
                fields = line.split()
                if len(fields) >= 7:
                    try:
                        values.append([float(x) for x in fields[:3]])
                    except ValueError:
                        pass
            a = np.asarray(values)
            assert np.all(np.diff(a[:, 0]) > 0) and np.all(a[:, 2] > 0)
            self.blocks.append((float(lines[0]), a))
        self.re = np.array([r for r, _ in self.blocks])
        assert len(self.blocks) == 4 and np.all(np.diff(self.re) > 0)

    def lookup(self, alpha_deg, reynolds):
        hi = int(np.clip(np.searchsorted(self.re, reynolds), 1, len(self.re)-1))
        lo = hi - 1
        w = float(np.clip((reynolds-self.re[lo])/(self.re[hi]-self.re[lo]), 0, 1))
        result = np.zeros(2)
        valid = self.re[0] <= reynolds <= self.re[-1]
        for index, weight in ((lo, 1-w), (hi, w)):
            data = self.blocks[index][1]
            result += weight*np.array([np.interp(alpha_deg, data[:, 0], data[:, k]) for k in (1, 2)])
            if weight > 1e-12:
                valid &= data[0, 0] <= alpha_deg <= data[-1, 0]
        return float(result[0]), float(result[1]), bool(valid)


def solve_design(radius_m, tip_speed_m_s, blades=8, alpha_deg=6.0, cells=64,
                 root_ratio=.30, rho=1.225, nu=1.46e-5, sound_speed=340.3,
                 polar=None, fixed_beta_rad=None):
    """Inverse twist at fixed alpha, or a fixed-twist operating point.

    Local nondimensional unknowns are v_i/U_tip and wake swirl at disk/U_tip.
    dT/dr=4*pi*rho*r*F*v_i^2; dQ/dr=4*pi*rho*r^2*F*v_i*v_theta.
    The rotor air-relative tangential speed is Omega*r-v_theta.
    """
    polar = polar or Polar()
    if radius_m <= 0 or tip_speed_m_s <= 0 or not 0 < root_ratio < 1:
        raise ValueError("Positive geometry/speed and a root ratio in (0,1) required")
    dr = radius_m*(1-root_ratio)/cells
    radii = radius_m*(root_ratio+(np.arange(cells)+.5)*(1-root_ratio)/cells)
    chord = radius_m*np.interp(radii/radius_m, [.30, .40, .65, .85, 1.0], [.20, .32, .34, .28, .14])
    if fixed_beta_rad is not None and np.shape(fixed_beta_rad) != (cells,):
        raise ValueError("Fixed twist must be supplied at this same radial grid")
    omega = tip_speed_m_s/radius_m
    rows = []
    for j, (r, c) in enumerate(zip(radii, chord)):
        radial_fraction = r/radius_m

        def evaluate(x):
            vi, swirl = x*tip_speed_m_s
            tangential = omega*r-swirl
            phi = np.arctan2(vi, tangential)
            alpha = alpha_deg if fixed_beta_rad is None else np.degrees(fixed_beta_rad[j]-phi)
            speed = np.hypot(vi, tangential)
            reynolds = speed*c/nu
            cl, cd, valid = polar.lookup(alpha, reynolds)
            sin_phi = max(np.sin(phi), 1e-10)
            tip_f = 2/np.pi*np.arccos(np.exp(-blades/2*(radius_m-r)/(r*sin_phi)))
            root_f = 2/np.pi*np.arccos(np.exp(-blades/2*(r-root_ratio*radius_m)/(root_ratio*radius_m*sin_phi)))
            loss = tip_f*root_f
            lift = .5*rho*speed**2*c*blades*cl
            drag = .5*rho*speed**2*c*blades*cd
            thrust = lift*np.cos(phi)-drag*np.sin(phi)
            torque = r*(lift*np.sin(phi)+drag*np.cos(phi))
            momentum_thrust = 4*np.pi*rho*r*loss*vi*vi
            momentum_torque = 4*np.pi*rho*r*r*loss*vi*swirl
            scale_t = rho*tip_speed_m_s**2*radius_m
            residual = [(thrust-momentum_thrust)/scale_t,
                        (torque-momentum_torque)/(scale_t*radius_m)]
            return residual, dict(r_m=r, chord_m=c, beta_rad=np.radians(alpha)+phi,
                                  alpha_deg=alpha, Re=reynolds, Mach_relative=speed/sound_speed,
                                  polar_in_domain=valid, vi_m_s=vi, swirl_at_disk_m_s=swirl,
                                  tip_root_loss=loss, dT_dr_N_m=thrust, dQ_dr_Nm_m=torque,
                                  profile_power_per_radius_W_m=drag*speed)

        sol = least_squares(lambda x: evaluate(x)[0], [.12, .025],
                            bounds=([1e-6, 1e-7], [.8, .80*radial_fraction]),
                            ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=200)
        residual, row = evaluate(sol.x)
        row.update(max_normalized_balance_residual=float(np.max(np.abs(residual))),
                   solve_success=bool(sol.success and np.max(np.abs(residual)) < 1e-6))
        rows.append(row)
    def arr(name):
        return np.asarray([r[name] for r in rows])
    thrust = float(arr("dT_dr_N_m").sum()*dr)
    torque = float(arr("dQ_dr_Nm_m").sum()*dr)
    power = torque*omega
    ideal = thrust**1.5/np.sqrt(2*rho*np.pi*radius_m**2) if thrust > 0 else float("nan")
    reconstructed_power = float((arr("dT_dr_N_m")*arr("vi_m_s")
                                 +arr("dQ_dr_Nm_m")*arr("swirl_at_disk_m_s")/radii
                                 +arr("profile_power_per_radius_W_m")).sum()*dr)
    abs_t = np.abs(arr("dT_dr_N_m"))
    abs_q = np.abs(arr("dQ_dr_Nm_m"))
    beta = arr("beta_rad")
    tangential_chord = chord*np.cos(beta)
    spacing = 2*np.pi*radii/blades
    return {
        "radius_m": radius_m, "diameter_m": 2*radius_m, "blades": blades,
        "rpm": float(omega*60/(2*np.pi)), "tip_rotational_speed_m_s": tip_speed_m_s,
        "Mach_tip_rotational": tip_speed_m_s/sound_speed,
        "T_isolated_model_N": thrust, "Q_isolated_model_Nm": torque,
        "shaft_model_W": power, "ideal_free_disk_W_same_T": ideal,
        "free_rotor_model_FM": ideal/power,
        "energy_identity_relative_residual": abs(power-reconstructed_power)/abs(power),
        "all_annular_balances_converged": all(r["solve_success"] for r in rows),
        "max_normalized_balance_residual": float(max(r["max_normalized_balance_residual"] for r in rows)),
        "outside_polar_thrust_fraction": float(abs_t[~arr("polar_in_domain")].sum()/abs_t.sum()),
        "outside_polar_torque_fraction": float(abs_q[~arr("polar_in_domain")].sum()/abs_q.sum()),
        "Mach_gt_0_3_torque_fraction": float(abs_q[arr("Mach_relative") > .3].sum()/abs_q.sum()),
        "max_relative_Mach": float(arr("Mach_relative").max()),
        "Re_min": float(arr("Re").min()), "Re_max": float(arr("Re").max()),
        "max_local_solidity": float((chord/spacing).max()),
        "projected_chord_over_pitch_max": float((tangential_chord/spacing).max()),
        "root_ratio": root_ratio, "alpha_design_deg": alpha_deg if fixed_beta_rad is None else None,
        "twist_min_deg": float(np.degrees(beta).min()), "twist_max_deg": float(np.degrees(beta).max()),
        "CT_nD": thrust/(rho*(omega/(2*np.pi))**2*(2*radius_m)**4),
        "CP_nD": power/(rho*(omega/(2*np.pi))**3*(2*radius_m)**5),
        "annuli": rows,
    }
