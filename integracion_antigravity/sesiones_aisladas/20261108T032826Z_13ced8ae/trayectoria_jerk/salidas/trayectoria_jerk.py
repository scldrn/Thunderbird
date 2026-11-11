#!/usr/bin/env python3
"""
trayectoria_jerk.py
-------------------
Modelo y simulación de trayectoria 1D de reposo a reposo con límites de
aceleración A y jerk J, y comparación con perfil ideal sin jerk.

Desarrollado para verificación autónoma de perfiles cinemáticos simétricos
con cuatro rampas de jerk (ramas triangular y con meseta).

Autor: Asistente de Investigación Cinemática / Antigravity
Fecha: Noviembre 2026
Entorno: Python estándar (sin dependencias externas)
"""

import math
import csv
import os
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any

# Constante de gravedad estándar (ISO 80000-3 / CODATA)
G_STANDARD = 9.80665  # m/s^2


@dataclass
class TrajectoryConfig:
    """Configuración de hipótesis para la trayectoria 1D."""
    name: str
    d: float              # Desplazamiento objetivo [m]
    A_g: float            # Aceleración límite en fracciones de g [-]
    J: float              # Jerk límite [m/s^3]
    g: float = G_STANDARD # Aceleración de la gravedad [m/s^2]

    @property
    def A(self) -> float:
        """Aceleración límite en m/s^2."""
        return self.A_g * self.g


@dataclass
class TrajectoryProfile:
    """Parámetros calculados y características del perfil cinemático."""
    config: TrajectoryConfig
    d_crit: float         # Distancia crítica umbral entre ramas [m]
    branch: str           # 'triangular' o 'meseta'
    a_peak: float         # Aceleración pico alcanzada [m/s^2]
    tj: float             # Duración de cada rampa de jerk [s]
    ta: float             # Duración de la meseta de aceleración [s]
    tm: float             # Tiempo de punto medio (mitad de trayectoria) [s]
    T: float              # Tiempo total con límite de jerk [s]
    t_ideal: float        # Tiempo ideal sin límite de jerk sqrt(4d/A) [s]
    delta_t: float        # Penalización temporal T - t_ideal [s]
    ratio_t: float        # Razón T / t_ideal [-]
    v_max: float          # Velocidad máxima en punto medio [m/s]
    v_max_ideal: float    # Velocidad máxima del perfil ideal sqrt(A*d) [m/s]

    # Momentos temporales de conmutación [s]
    t_switch: List[float] = field(default_factory=list)


@dataclass
class State:
    """Estado cinemático 1D instantáneo."""
    t: float
    jerk: float
    accel: float
    vel: float
    pos: float


@dataclass
class SimulationResult:
    """Resultados de la integración numérica independiente."""
    profile: TrajectoryProfile
    method: str
    dt: float
    n_steps: int
    states: List[State]
    terminal_error_x: float
    terminal_error_v: float
    terminal_error_a: float
    max_error_x: float
    max_error_v: float
    max_error_a: float


def compute_profile(config: TrajectoryConfig) -> TrajectoryProfile:
    """
    Calcula los parámetros analíticos de la trayectoria simétrica de 4 rampas
    de jerk de reposo a reposo para una distancia d con límites A y J.

    Deducción analítica:
      d_crit = 2 * A^3 / J^2

      Rama triangular (d <= d_crit):
        La aceleración no alcanza A; alcanza a_peak = (0.5 * d * J^2)^(1/3) < A.
        ta = 0 (sin meseta de aceleración constante).
        tj = a_peak / J = (d / (2*J))^(1/3).
        T = 4 * tj = (32 * d / J)^(1/3).
        v_max = a_peak * tj.

      Rama con meseta (d > d_crit):
        La aceleración alcanza A; a_peak = A.
        tj = A / J.
        ta = (-3*tj + sqrt(tj^2 + 4*d/A)) / 2.
        T = 4*tj + 2*ta = tj + sqrt(tj^2 + 4*d/A).
        v_max = A * (tj + ta).

      Perfil ideal sin jerk:
        t_ideal = sqrt(4 * d / A).
        v_max_ideal = sqrt(A * d).
    """
    d = config.d
    A = config.A
    J = config.J

    if d <= 0.0 or A <= 0.0 or J <= 0.0:
        raise ValueError(f"d, A y J deben ser estrictamente positivos: d={d}, A={A}, J={J}")

    d_crit = 2.0 * (A**3) / (J**2)

    if d <= d_crit:
        branch = "triangular"
        a_peak = (0.5 * d * (J**2)) ** (1.0 / 3.0)
        tj = a_peak / J
        ta = 0.0
        T = 4.0 * tj
    else:
        branch = "meseta"
        a_peak = A
        tj = A / J
        discriminant = tj**2 + (4.0 * d / A)
        ta = (-3.0 * tj + math.sqrt(discriminant)) / 2.0
        T = 4.0 * tj + 2.0 * ta

    tm = 2.0 * tj + ta
    v_max = a_peak * (tj + ta)

    t_ideal = math.sqrt(4.0 * d / A)
    v_max_ideal = math.sqrt(A * d)
    delta_t = T - t_ideal
    ratio_t = T / t_ideal

    # Conmutaciones:
    # 0 -> rampa +J hasta tj
    # tj -> meseta +a_peak hasta tj + ta
    # tj + ta -> rampa -J hasta 2*tj + ta (mitad)
    # 2*tj + ta -> rampa -J hasta 3*tj + ta
    # 3*tj + ta -> meseta -a_peak hasta 3*tj + 2*ta
    # 3*tj + 2*ta -> rampa +J hasta 4*tj + 2*ta (fin)
    t_switch = [
        0.0,
        tj,
        tj + ta,
        2.0 * tj + ta,
        3.0 * tj + ta,
        3.0 * tj + 2.0 * ta,
        4.0 * tj + 2.0 * ta
    ]

    return TrajectoryProfile(
        config=config,
        d_crit=d_crit,
        branch=branch,
        a_peak=a_peak,
        tj=tj,
        ta=ta,
        tm=tm,
        T=T,
        t_ideal=t_ideal,
        delta_t=delta_t,
        ratio_t=ratio_t,
        v_max=v_max,
        v_max_ideal=v_max_ideal,
        t_switch=t_switch
    )


def eval_analytical(profile: TrajectoryProfile, t: float) -> State:
    """
    Evalúa analíticamente el jerk, la aceleración, la velocidad y la posición
    en el instante t para el perfil de 4 rampas de jerk.
    """
    tj = profile.tj
    ta = profile.ta
    J = profile.config.J
    a_peak = profile.a_peak
    d = profile.config.d

    t1 = tj
    t2 = tj + ta
    t3 = 2.0 * tj + ta
    t4 = 3.0 * tj + ta
    t5 = 3.0 * tj + 2.0 * ta
    t6 = 4.0 * tj + 2.0 * ta

    # Estados frontera de cada intervalo:
    v1 = 0.5 * J * (t1**2)
    x1 = (1.0 / 6.0) * J * (t1**3)

    v2 = v1 + a_peak * ta
    x2 = x1 + v1 * ta + 0.5 * a_peak * (ta**2)

    v3 = a_peak * (tj + ta)  # v_max
    x3 = 0.5 * d

    v4 = v3 - 0.5 * J * (tj**2)
    x4 = x3 + v3 * tj - (1.0 / 6.0) * J * (tj**3)

    v5 = 0.5 * J * (tj**2)
    x5 = x4 + v4 * ta - 0.5 * a_peak * (ta**2)

    if t <= 0.0:
        return State(t=t, jerk=0.0, accel=0.0, vel=0.0, pos=0.0)
    elif t < t1:
        # Segmento 1: rampa de aceleración positiva (+J)
        j = J
        a = J * t
        v = 0.5 * J * (t**2)
        x = (1.0 / 6.0) * J * (t**3)
        return State(t=t, jerk=j, accel=a, vel=v, pos=x)
    elif t < t2:
        # Segmento 2: meseta de aceleración positiva
        tau = t - t1
        j = 0.0
        a = a_peak
        v = v1 + a_peak * tau
        x = x1 + v1 * tau + 0.5 * a_peak * (tau**2)
        return State(t=t, jerk=j, accel=a, vel=v, pos=x)
    elif t < t3:
        # Segmento 3: rampa de desaceleración hasta a=0 (-J)
        tau = t - t2
        j = -J
        a = a_peak - J * tau
        v = v2 + a_peak * tau - 0.5 * J * (tau**2)
        x = x2 + v2 * tau + 0.5 * a_peak * (tau**2) - (1.0 / 6.0) * J * (tau**3)
        return State(t=t, jerk=j, accel=a, vel=v, pos=x)
    elif t < t4:
        # Segmento 4: rampa de aceleración negativa (-J)
        tau = t - t3
        j = -J
        a = -J * tau
        v = v3 - 0.5 * J * (tau**2)
        x = x3 + v3 * tau - (1.0 / 6.0) * J * (tau**3)
        return State(t=t, jerk=j, accel=a, vel=v, pos=x)
    elif t < t5:
        # Segmento 5: meseta de aceleración negativa (-a_peak)
        tau = t - t4
        j = 0.0
        a = -a_peak
        v = v4 - a_peak * tau
        x = x4 + v4 * tau - 0.5 * a_peak * (tau**2)
        return State(t=t, jerk=j, accel=a, vel=v, pos=x)
    elif t <= t6:
        # Segmento 6: rampa de frenado hasta reposo (+J)
        tau = t - t5
        j = J
        a = -a_peak + J * tau
        v = v5 - a_peak * tau + 0.5 * J * (tau**2)
        x = x5 + v5 * tau - 0.5 * a_peak * (tau**2) + (1.0 / 6.0) * J * (tau**3)
        return State(t=t, jerk=j, accel=a, vel=v, pos=x)
    else:
        # Fin de la trayectoria
        return State(t=t, jerk=0.0, accel=0.0, vel=0.0, pos=d)


def eval_jerk(profile: TrajectoryProfile, t: float) -> float:
    """Devuelve el jerk prescrito en el instante t."""
    t_sw = profile.t_switch
    if t < 0.0 or t > t_sw[6]:
        return 0.0
    elif t < t_sw[1]:
        return profile.config.J
    elif t < t_sw[2]:
        return 0.0
    elif t < t_sw[3]:
        return -profile.config.J
    elif t < t_sw[4]:
        return -profile.config.J
    elif t < t_sw[5]:
        return 0.0
    elif t <= t_sw[6]:
        return profile.config.J
    else:
        return 0.0


def simulate_numerical(
    profile: TrajectoryProfile,
    method: str = "rk4_segment_aligned",
    steps_per_segment: int = 1000,
    uniform_dt: Optional[float] = None
) -> SimulationResult:
    """
    Simulación mediante integración numérica independiente:
      da/dt = j(t)
      dv/dt = a(t)
      dx/dt = v(t)

    Métodos disponibles:
      - 'rk4_segment_aligned': Runge-Kutta 4to orden alineado con las conmutaciones.
      - 'rk4_uniform': Runge-Kutta 4to orden con paso temporal uniforme fijo.
    """
    t_sw = profile.t_switch
    J = profile.config.J
    d = profile.config.d

    states: List[State] = []
    max_err_x = 0.0
    max_err_v = 0.0
    max_err_a = 0.0

    if method == "rk4_segment_aligned":
        segments = [
            (t_sw[0], t_sw[1], J),
            (t_sw[1], t_sw[2], 0.0),
            (t_sw[2], t_sw[3], -J),
            (t_sw[3], t_sw[4], -J),
            (t_sw[4], t_sw[5], 0.0),
            (t_sw[5], t_sw[6], J),
        ]

        t = 0.0
        x = 0.0
        v = 0.0
        a = 0.0
        states.append(State(t=t, jerk=0.0, accel=a, vel=v, pos=x))

        total_steps = 0
        min_dt = float("inf")

        for t_start, t_end, j_val in segments:
            seg_dur = t_end - t_start
            if seg_dur <= 0.0:
                continue

            dt = seg_dur / steps_per_segment
            min_dt = min(min_dt, dt)

            for step in range(steps_per_segment):
                # RK4 para sistema lineal forzado por j_val
                k1_x = v
                k1_v = a
                k1_a = j_val

                k2_x = v + 0.5 * dt * k1_v
                k2_v = a + 0.5 * dt * k1_a
                k2_a = j_val

                k3_x = v + 0.5 * dt * k2_v
                k3_v = a + 0.5 * dt * k2_a
                k3_a = j_val

                k4_x = v + dt * k3_v
                k4_v = a + dt * k3_a
                k4_a = j_val

                x += (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
                v += (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
                a += (dt / 6.0) * (k1_a + 2.0 * k2_a + 2.0 * k3_a + k4_a)
                t += dt
                total_steps += 1

                ana = eval_analytical(profile, t)
                err_x = abs(x - ana.pos)
                err_v = abs(v - ana.vel)
                err_a = abs(a - ana.accel)

                max_err_x = max(max_err_x, err_x)
                max_err_v = max(max_err_v, err_v)
                max_err_a = max(max_err_a, err_a)

                if step % (steps_per_segment // 20 or 1) == 0 or step == steps_per_segment - 1:
                    states.append(State(t=t, jerk=j_val, accel=a, vel=v, pos=x))

        term_err_x = x - d
        term_err_v = v - 0.0
        term_err_a = a - 0.0
        dt_eff = min_dt

    elif method == "rk4_uniform":
        dt = uniform_dt if uniform_dt is not None else (profile.T / 20000.0)
        n_steps = int(math.ceil(profile.T / dt))
        dt = profile.T / n_steps

        t = 0.0
        x = 0.0
        v = 0.0
        a = 0.0
        states.append(State(t=t, jerk=eval_jerk(profile, t), accel=a, vel=v, pos=x))
        total_steps = n_steps
        dt_eff = dt

        sample_interval = max(1, n_steps // 200)

        for step in range(n_steps):
            j1 = eval_jerk(profile, t)
            k1_x = v
            k1_v = a
            k1_a = j1

            t_half = t + 0.5 * dt
            j2 = eval_jerk(profile, t_half)
            k2_x = v + 0.5 * dt * k1_v
            k2_v = a + 0.5 * dt * k1_a
            k2_a = j2

            k3_x = v + 0.5 * dt * k2_v
            k3_v = a + 0.5 * dt * k2_a
            k3_a = j2

            t_full = t + dt
            j4 = eval_jerk(profile, t_full)
            k4_x = v + dt * k3_v
            k4_v = a + dt * k3_a
            k4_a = j4

            x += (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
            v += (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
            a += (dt / 6.0) * (k1_a + 2.0 * k2_a + 2.0 * k3_a + k4_a)
            t += dt

            ana = eval_analytical(profile, t)
            err_x = abs(x - ana.pos)
            err_v = abs(v - ana.vel)
            err_a = abs(a - ana.accel)

            max_err_x = max(max_err_x, err_x)
            max_err_v = max(max_err_v, err_v)
            max_err_a = max(max_err_a, err_a)

            if step % sample_interval == 0 or step == n_steps - 1:
                states.append(State(t=t, jerk=j4, accel=a, vel=v, pos=x))

        term_err_x = x - d
        term_err_v = v - 0.0
        term_err_a = a - 0.0

    else:
        raise ValueError(f"Método de integración desconocido: {method}")

    return SimulationResult(
        profile=profile,
        method=method,
        dt=dt_eff,
        n_steps=total_steps,
        states=states,
        terminal_error_x=term_err_x,
        terminal_error_v=term_err_v,
        terminal_error_a=term_err_a,
        max_error_x=max_err_x,
        max_error_v=max_err_v,
        max_error_a=max_err_a
    )


def verify_continuity(profile: TrajectoryProfile, eps: float = 1e-9) -> Dict[str, Any]:
    """
    Verifica la continuidad de la aceleración (C0), velocidad (C1) y posición (C2)
    a través de todos los puntos de conmutación interna del perfil.
    """
    discontinuities = []
    t_switch = profile.t_switch

    for i, t_sw in enumerate(t_switch[1:-1], start=1):
        t_left = t_sw - eps
        t_right = t_sw + eps
        s_left = eval_analytical(profile, t_left)
        s_right = eval_analytical(profile, t_right)

        diff_a = abs(s_right.accel - s_left.accel)
        diff_v = abs(s_right.vel - s_left.vel)
        diff_x = abs(s_right.pos - s_left.pos)

        max_expected_diff_a = 2.0 * profile.config.J * eps
        max_expected_diff_v = 2.0 * profile.a_peak * eps
        max_expected_diff_x = 2.0 * profile.v_max * eps

        is_c0_accel = diff_a <= (max_expected_diff_a + 1e-12)
        is_c1_vel = diff_v <= (max_expected_diff_v + 1e-12)
        is_c2_pos = diff_x <= (max_expected_diff_x + 1e-12)

        discontinuities.append({
            "switch_idx": i,
            "t_sw": t_sw,
            "diff_accel": diff_a,
            "diff_vel": diff_v,
            "diff_pos": diff_x,
            "continuous_a": is_c0_accel,
            "continuous_v": is_c1_vel,
            "continuous_x": is_c2_pos
        })

    all_continuous = all(
        d["continuous_a"] and d["continuous_v"] and d["continuous_x"]
        for d in discontinuities
    )

    return {
        "all_continuous": all_continuous,
        "switches": discontinuities
    }


def verify_branch_transition(A: float, J: float, eps: float = 1e-5) -> Dict[str, Any]:
    """
    Verifica la continuidad del tiempo total y de los parámetros del perfil
    en la transición crítica d = d_crit entre la rama triangular y la rama con meseta.
    """
    d_crit = 2.0 * (A**3) / (J**2)

    cfg_below = TrajectoryConfig(name="Below_crit", d=d_crit - eps, A_g=A / G_STANDARD, J=J)
    p_below = compute_profile(cfg_below)

    cfg_exact = TrajectoryConfig(name="Exact_crit", d=d_crit, A_g=A / G_STANDARD, J=J)
    p_exact = compute_profile(cfg_exact)

    cfg_above = TrajectoryConfig(name="Above_crit", d=d_crit + eps, A_g=A / G_STANDARD, J=J)
    p_above = compute_profile(cfg_above)

    diff_T_below = abs(p_exact.T - p_below.T)
    diff_T_above = abs(p_above.T - p_exact.T)

    return {
        "d_crit": d_crit,
        "p_below_branch": p_below.branch,
        "p_exact_branch": p_exact.branch,
        "p_above_branch": p_above.branch,
        "T_below": p_below.T,
        "T_exact": p_exact.T,
        "T_above": p_above.T,
        "ta_exact": p_exact.ta,
        "ta_above": p_above.ta,
        "diff_T_below": diff_T_below,
        "diff_T_above": diff_T_above,
        "is_smooth": (diff_T_below < 1e-4) and (diff_T_above < 1e-4) and (p_exact.ta < 1e-12)
    }


def run_standard_matrix() -> List[Dict[str, Any]]:
    """
    Ejecuta el conjunto de 6 combinaciones especificadas por la hipótesis:
      A = 0.5 g y 1.0 g
      J = 1, 5, 20 m/s^3
      d = 5.0 m
    """
    configs = [
        TrajectoryConfig(name="Caso_1_A05_J1", d=5.0, A_g=0.5, J=1.0),
        TrajectoryConfig(name="Caso_2_A05_J5", d=5.0, A_g=0.5, J=5.0),
        TrajectoryConfig(name="Caso_3_A05_J20", d=5.0, A_g=0.5, J=20.0),
        TrajectoryConfig(name="Caso_4_A10_J1", d=5.0, A_g=1.0, J=1.0),
        TrajectoryConfig(name="Caso_5_A10_J5", d=5.0, A_g=1.0, J=5.0),
        TrajectoryConfig(name="Caso_6_A10_J20", d=5.0, A_g=1.0, J=20.0),
    ]

    results = []
    for cfg in configs:
        prof = compute_profile(cfg)
        sim_aligned = simulate_numerical(prof, method="rk4_segment_aligned", steps_per_segment=1000)
        sim_uniform = simulate_numerical(prof, method="rk4_uniform", uniform_dt=1e-4)
        cont = verify_continuity(prof)
        results.append({
            "config": cfg,
            "profile": prof,
            "sim_aligned": sim_aligned,
            "sim_uniform": sim_uniform,
            "continuity": cont
        })

    return results


def export_summary_csv(results: List[Dict[str, Any]], filepath: str) -> None:
    """Exporta tabla de resumen comparativo en formato CSV estándar."""
    headers = [
        "caso",
        "A_g",
        "A_mps2",
        "J_mps3",
        "d_m",
        "d_crit_m",
        "rama",
        "a_pico_mps2",
        "a_pico_g",
        "tj_s",
        "ta_s",
        "tm_s",
        "T_jerk_s",
        "t_ideal_sin_jerk_s",
        "delta_t_s",
        "penalizacion_porc",
        "v_max_mps",
        "v_max_ideal_mps",
        "err_term_x_m",
        "err_term_v_mps",
        "err_term_a_mps2",
        "max_err_x_m"
    ]

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in results:
            p = r["profile"]
            s = r["sim_aligned"]
            writer.writerow([
                p.config.name,
                f"{p.config.A_g:.2f}",
                f"{p.config.A:.6f}",
                f"{p.config.J:.2f}",
                f"{p.config.d:.4f}",
                f"{p.d_crit:.6f}",
                p.branch,
                f"{p.a_peak:.6f}",
                f"{p.a_peak / p.config.g:.6f}",
                f"{p.tj:.6f}",
                f"{p.ta:.6f}",
                f"{p.tm:.6f}",
                f"{p.T:.6f}",
                f"{p.t_ideal:.6f}",
                f"{p.delta_t:.6f}",
                f"{100.0 * (p.ratio_t - 1.0):.3f}",
                f"{p.v_max:.6f}",
                f"{p.v_max_ideal:.6f}",
                f"{s.terminal_error_x:.6e}",
                f"{s.terminal_error_v:.6e}",
                f"{s.terminal_error_a:.6e}",
                f"{s.max_error_x:.6e}"
            ])


def export_time_series_csv(results: List[Dict[str, Any]], filepath: str, n_samples: int = 500) -> None:
    """Exporta las series temporales de simulación numérica y solución analítica con sus errores."""
    headers = [
        "caso",
        "t_s",
        "jerk_mps3",
        "accel_analitica_mps2",
        "vel_analitica_mps",
        "pos_analitica_m",
        "accel_sim_mps2",
        "vel_sim_mps",
        "pos_sim_m",
        "error_pos_m",
        "error_vel_mps",
        "error_accel_mps2"
    ]

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for r in results:
            p = r["profile"]
            # Obtener tiempos de muestreo regulares más los momentos de conmutación
            times = set()
            for i in range(n_samples + 1):
                times.add(round(i * p.T / n_samples, 8))
            for t_sw in p.t_switch:
                times.add(round(t_sw, 8))

            sorted_times = sorted(list(times))

            # Ejecutamos integración numérica segmentada paso a paso registrando los puntos deseados
            # Para garantizar que 'sim' proviene de integración paso a paso de las ecuaciones diferenciales
            t_curr = 0.0
            x_sim = 0.0
            v_sim = 0.0
            a_sim = 0.0

            sub_dt = 1e-4  # paso de integración fina

            for target_t in sorted_times:
                # Avanzamos la integración numérica hasta target_t
                while t_curr < target_t - 1e-12:
                    dt_step = min(sub_dt, target_t - t_curr)
                    # RK4 sobre [x, v, a]
                    j1 = eval_jerk(p, t_curr)
                    k1_x = v_sim
                    k1_v = a_sim
                    k1_a = j1

                    t_mid = t_curr + 0.5 * dt_step
                    j2 = eval_jerk(p, t_mid)
                    k2_x = v_sim + 0.5 * dt_step * k1_v
                    k2_v = a_sim + 0.5 * dt_step * k1_a
                    k2_a = j2

                    k3_x = v_sim + 0.5 * dt_step * k2_v
                    k3_v = a_sim + 0.5 * dt_step * k2_a
                    k3_a = j2

                    t_end = t_curr + dt_step
                    j4 = eval_jerk(p, t_end)
                    k4_x = v_sim + dt_step * k3_v
                    k4_v = a_sim + dt_step * k3_a
                    k4_a = j4

                    x_sim += (dt_step / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
                    v_sim += (dt_step / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
                    a_sim += (dt_step / 6.0) * (k1_a + 2.0 * k2_a + 2.0 * k3_a + k4_a)
                    t_curr += dt_step

                ana = eval_analytical(p, target_t)
                err_pos = abs(x_sim - ana.pos)
                err_vel = abs(v_sim - ana.vel)
                err_acc = abs(a_sim - ana.accel)

                writer.writerow([
                    p.config.name,
                    f"{target_t:.6f}",
                    f"{ana.jerk:.4f}",
                    f"{ana.accel:.8f}",
                    f"{ana.vel:.8f}",
                    f"{ana.pos:.8f}",
                    f"{a_sim:.8f}",
                    f"{v_sim:.8f}",
                    f"{x_sim:.8f}",
                    f"{err_pos:.6e}",
                    f"{err_vel:.6e}",
                    f"{err_acc:.6e}"
                ])


def print_comparison_table(results: List[Dict[str, Any]]) -> None:
    """Imprime una tabla de comparación formateada en la terminal."""
    print("=" * 105)
    print("COMPARACIÓN 1D DE TRAYECTORIA REST-TO-REST (d = 5.0 m) CON LÍMITES DE ACELERACIÓN Y JERK")
    print("=" * 105)
    header_fmt = "{:<16} | {:>4} | {:>4} | {:>10} | {:>6} | {:>6} | {:>7} | {:>7} | {:>8} | {:>7}"
    row_fmt = "{:<16} | {:>4.1f} | {:>4.0f} | {:>10} | {:>6.3f} | {:>6.3f} | {:>7.3f} | {:>7.3f} | {:>7.1f}% | {:>7.3f}"
    print(header_fmt.format("Caso", "A [g]", "J", "Rama", "tj [s]", "ta [s]", "T [s]", "T_id [s]", "ΔT / T_id", "vmax [m/s]"))
    print("-" * 105)
    for r in results:
        p = r["profile"]
        penaliz = 100.0 * (p.ratio_t - 1.0)
        print(row_fmt.format(
            p.config.name,
            p.config.A_g,
            p.config.J,
            p.branch,
            p.tj,
            p.ta,
            p.T,
            p.t_ideal,
            penaliz,
            p.v_max
        ))
    print("=" * 105)


def main() -> int:
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    summary_csv = os.path.join(output_dir, "resumen_comparativo.csv")
    series_csv = os.path.join(output_dir, "series_temporales.csv")

    results = run_standard_matrix()
    print_comparison_table(results)

    export_summary_csv(results, summary_csv)
    print(f"\n[OK] Resumen comparativo exportado a: {summary_csv}")

    export_time_series_csv(results, series_csv)
    print(f"[OK] Series temporales exportadas a: {series_csv}")

    # Verificación de transición de ramas
    trans_05g = verify_branch_transition(0.5 * G_STANDARD, 20.0)
    trans_10g = verify_branch_transition(1.0 * G_STANDARD, 20.0)
    print("\n--- Verificación de Continuidad en Frontera d = d_crit ---")
    print(f"A=0.5g, J=20: d_crit={trans_05g['d_crit']:.4f} m, suave={trans_05g['is_smooth']}, diff_T_below={trans_05g['diff_T_below']:.2e} s")
    print(f"A=1.0g, J=20: d_crit={trans_10g['d_crit']:.4f} m, suave={trans_10g['is_smooth']}, diff_T_below={trans_10g['diff_T_below']:.2e} s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
