"""
perfil_cinematico.py
====================
Análisis independiente de perfiles temporales para traslación (10 mm) y giro (110°)
en dos fases con polinomio suave quintico s(u) = 10*u^3 - 15*u^4 + 6*u^5.

Cumplimiento estricto de directrices:
- Código estándar de Python 3 (sin dependencias externas).
- Separación rigurosa de cinemática respecto a dinámica/dimensionamiento de motor.
- Chequeo analítico cerrado vs muestreo discreto y diferencias finitas.
- Conservación de unidades y trazabilidad de fuentes.
- No afirma la existencia física ni el encaje de mecanismos.
"""

import math
import json
import csv
import os
from typing import Dict, List, Tuple, Any, Optional


# =====================================================================
# 1. POLINOMIO QUINTICO NORMALIZADO s(u)
# =====================================================================

class SmoothQuinticPolynomial:
    """
    Polinomio normalizado de 5to orden (minimum jerk / perfil suave):
        s(u) = 10*u^3 - 15*u^4 + 6*u^5,  u en [0, 1]

    Condiciones de contorno en u=0 y u=1:
        s(0) = 0,   s(1) = 1
        s'(0) = 0,  s'(1) = 0   (velocidad nula en extremos)
        s''(0) = 0, s''(1) = 0  (aceleración nula en extremos)

    Derivadas analíticas:
        s'(u)   = 30*u^2 - 60*u^3 + 30*u^4 = 30*u^2*(1 - u)^2
        s''(u)  = 60*u - 180*u^2 + 120*u^3 = 60*u*(1 - u)*(1 - 2*u)
        s'''(u) = 60 - 360*u + 360*u^2 = 60*(1 - 6*u + 6*u^2)
        s''''(u)= -360 + 720*u = 360*(2*u - 1)

    Puntos críticos y extremos analíticos exactos:
        - Máximo de s'(u):
            s''(u) = 0 en u en (0, 1) => 1 - 2*u = 0 => u_vmax = 1/2 = 0.5
            s'(0.5) = 30*(1/4)*(1/4) = 30/16 = 15/8 = 1.875
            c_v = 1.875 (coeficiente adimensional exacto de velocidad)

        - Extremos de s''(u):
            s'''(u) = 0 => 6*u^2 - 6*u + 1 = 0
            u_amax1 = 1/2 - sqrt(3)/6 ≈ 0.21132486540518713 (máximo positivo)
            u_amax2 = 1/2 + sqrt(3)/6 ≈ 0.7886751345948129 (mínimo negativo / frenado)
            s''(u_amax1) = +10/sqrt(3) = +10*sqrt(3)/3 ≈ +5.773502691896258
            s''(u_amax2) = -10/sqrt(3) = -10*sqrt(3)/3 ≈ -5.773502691896258
            c_a = 10 / sqrt(3) ≈ 5.773502691896258 (coeficiente adimensional exacto de aceleración)

        - Extremos de s'''(u) (jerk):
            s''''(u) = 0 => u = 0.5 (mínimo de jerk: s'''(0.5) = -30)
            Extremos de contorno: s'''(0) = +60, s'''(1) = +60
            c_j_max = 60.0
    """

    C_V: float = 15.0 / 8.0  # 1.875 exactamente
    C_A: float = 10.0 / math.sqrt(3.0)  # 5.773502691896258...
    U_VMAX: float = 0.5
    U_AMAX1: float = 0.5 - math.sqrt(3.0) / 6.0
    U_AMAX2: float = 0.5 + math.sqrt(3.0) / 6.0
    C_J_MAX: float = 60.0
    C_J_MIN: float = -30.0

    @staticmethod
    def s(u: float) -> float:
        """Posición adimensional s(u). Clampeada a [0, 1] si u está en los límites."""
        if u <= 0.0:
            return 0.0
        if u >= 1.0:
            return 1.0
        return 10.0 * (u ** 3) - 15.0 * (u ** 4) + 6.0 * (u ** 5)

    @staticmethod
    def ds_du(u: float) -> float:
        """Primera derivada ds/du (velocidad adimensional)."""
        if u < 0.0 or u > 1.0:
            return 0.0
        return 30.0 * (u ** 2) - 60.0 * (u ** 3) + 30.0 * (u ** 4)

    @staticmethod
    def d2s_du2(u: float) -> float:
        """Segunda derivada d2s/du2 (aceleración adimensional)."""
        if u < 0.0 or u > 1.0:
            return 0.0
        return 60.0 * u - 180.0 * (u ** 2) + 120.0 * (u ** 3)

    @staticmethod
    def d3s_du3(u: float) -> float:
        """Tercera derivada d3s/du3 (jerk adimensional)."""
        if u < 0.0 or u > 1.0:
            return 0.0
        return 60.0 - 360.0 * u + 360.0 * (u ** 2)


# =====================================================================
# 2. CINEMÁTICA DE UNA FASE INDEPENDIENTE
# =====================================================================

class SinglePhaseKinematics:
    """
    Cinemática para una coordenada q(t) = q_0 + Delta_q * s(t / T).
    Permite evaluar de forma continua y muestreada:
        q(t) = q_0 + Delta_q * s(u)
        v(t) = (Delta_q / T) * s'(u)
        a(t) = (Delta_q / T^2) * s''(u)
        j(t) = (Delta_q / T^3) * s'''(u)
    """

    def __init__(
        self,
        name: str,
        delta_q: float,
        unit: str,
        duration_T: float,
        q0: float = 0.0,
        si_factor: float = 1.0,
        si_unit: str = "m"
    ):
        self.name = name
        self.delta_q = float(delta_q)
        self.unit = unit
        self.duration_T = float(duration_T)
        self.q0 = float(q0)
        self.si_factor = float(si_factor)
        self.si_unit = si_unit

        if self.duration_T <= 0.0:
            raise ValueError(f"La duración T debe ser positiva, recibido {self.duration_T}")

        # Valores analíticos máximos exactos
        self.v_max_exact = SmoothQuinticPolynomial.C_V * (self.delta_q / self.duration_T)
        self.a_max_exact = SmoothQuinticPolynomial.C_A * (self.delta_q / (self.duration_T ** 2))
        self.a_min_exact = -self.a_max_exact
        self.j_max_exact = SmoothQuinticPolynomial.C_J_MAX * (self.delta_q / (self.duration_T ** 3))
        self.j_min_exact = SmoothQuinticPolynomial.C_J_MIN * (self.delta_q / (self.duration_T ** 3))

        # Instantes analíticos exactos de pico
        self.t_vmax = SmoothQuinticPolynomial.U_VMAX * self.duration_T
        self.t_amax = SmoothQuinticPolynomial.U_AMAX1 * self.duration_T
        self.t_amin = SmoothQuinticPolynomial.U_AMAX2 * self.duration_T

        # Equivalentes en SI
        self.delta_q_si = self.delta_q * self.si_factor
        self.v_max_si = self.v_max_exact * self.si_factor
        self.a_max_si = self.a_max_exact * self.si_factor

    # Evaluaciones continuas en tiempo t
    def position(self, t: float) -> float:
        if t <= 0.0:
            return self.q0
        if t >= self.duration_T:
            return self.q0 + self.delta_q
        u = t / self.duration_T
        return self.q0 + self.delta_q * SmoothQuinticPolynomial.s(u)

    def velocity(self, t: float) -> float:
        if t < 0.0 or t > self.duration_T:
            return 0.0
        u = t / self.duration_T
        return (self.delta_q / self.duration_T) * SmoothQuinticPolynomial.ds_du(u)

    def acceleration(self, t: float) -> float:
        if t < 0.0 or t > self.duration_T:
            return 0.0
        u = t / self.duration_T
        return (self.delta_q / (self.duration_T ** 2)) * SmoothQuinticPolynomial.d2s_du2(u)

    def jerk(self, t: float) -> float:
        if t < 0.0 or t > self.duration_T:
            return 0.0
        u = t / self.duration_T
        return (self.delta_q / (self.duration_T ** 3)) * SmoothQuinticPolynomial.d3s_du3(u)

    # Muestreo y comprobaciones discretas
    def sample(self, n_points: int) -> Dict[str, List[float]]:
        """Muestrea el perfil en n_points equidistantes sobre [0, T]."""
        if n_points < 2:
            raise ValueError(f"n_points debe ser >= 2, recibido {n_points}")
        dt = self.duration_T / (n_points - 1)
        t_vals = [i * dt for i in range(n_points)]
        q_vals = [self.position(t) for t in t_vals]
        v_vals = [self.velocity(t) for t in t_vals]
        a_vals = [self.acceleration(t) for t in t_vals]
        j_vals = [self.jerk(t) for t in t_vals]
        return {
            "dt": dt,
            "t": t_vals,
            "q": q_vals,
            "v": v_vals,
            "a": a_vals,
            "j": j_vals
        }

    def evaluate_sampling_accuracy(self, n_points: int) -> Dict[str, Any]:
        """
        Compara los valores máximos muestreados frente a los analíticos exactos,
        e incluye derivadas numéricas por diferencias finitas centrales.
        """
        sampled = self.sample(n_points)
        dt = sampled["dt"]
        q_vals = sampled["q"]
        v_vals = sampled["v"]
        a_vals = sampled["a"]

        # 1. Picos en la malla evaluando las fórmulas analíticas
        v_max_sampled = max(v_vals)
        a_max_sampled = max(a_vals)
        a_min_sampled = min(a_vals)

        # 2. Diferenciación numérica por diferencias finitas centrales
        # v_fd[i] = (q[i+1] - q[i-1]) / (2*dt)
        # a_fd[i] = (q[i+1] - 2*q[i] + q[i-1]) / (dt^2)
        v_fd = [0.0] * n_points
        a_fd = [0.0] * n_points

        # Extremos
        v_fd[0] = (q_vals[1] - q_vals[0]) / dt
        v_fd[-1] = (q_vals[-1] - q_vals[-2]) / dt
        a_fd[0] = 0.0
        a_fd[-1] = 0.0

        for i in range(1, n_points - 1):
            v_fd[i] = (q_vals[i + 1] - q_vals[i - 1]) / (2.0 * dt)
            a_fd[i] = (q_vals[i + 1] - 2.0 * q_vals[i] + q_vals[i - 1]) / (dt ** 2)

        v_fd_max = max(v_fd)
        a_fd_max = max(a_fd)

        # 3. Integración numérica (regla trapezoidal)
        # Integral de v(t) debe ser Delta_q
        int_v = sum(0.5 * (v_vals[i] + v_vals[i + 1]) * dt for i in range(n_points - 1))
        # Integral de a(t) debe ser 0.0 (v(T) - v(0) = 0)
        int_a = sum(0.5 * (a_vals[i] + a_vals[i + 1]) * dt for i in range(n_points - 1))

        # Discrepancias
        err_v_grid = abs(v_max_sampled - self.v_max_exact)
        rel_err_v_grid = (err_v_grid / self.v_max_exact) * 100.0 if self.v_max_exact != 0 else 0.0

        err_a_grid = abs(a_max_sampled - self.a_max_exact)
        rel_err_a_grid = (err_a_grid / self.a_max_exact) * 100.0 if self.a_max_exact != 0 else 0.0

        err_v_fd = abs(v_fd_max - self.v_max_exact)
        err_a_fd = abs(a_fd_max - self.a_max_exact)

        err_integral_q = abs(int_v - self.delta_q)
        err_integral_v = abs(int_a - 0.0)

        return {
            "n_points": n_points,
            "dt_s": dt,
            "v_max_exact": self.v_max_exact,
            "v_max_sampled_analytic": v_max_sampled,
            "err_v_sampled": err_v_grid,
            "rel_err_v_sampled_pct": rel_err_v_grid,
            "v_max_fd": v_fd_max,
            "err_v_fd": err_v_fd,
            "a_max_exact": self.a_max_exact,
            "a_max_sampled_analytic": a_max_sampled,
            "err_a_sampled": err_a_grid,
            "rel_err_a_sampled_pct": rel_err_a_grid,
            "a_max_fd": a_fd_max,
            "err_a_fd": err_a_fd,
            "integral_v_trapezoid": int_v,
            "integral_v_error": err_integral_q,
            "integral_a_trapezoid": int_a,
            "integral_a_error": err_integral_v
        }


# =====================================================================
# 3. SECUENCIA CINEMÁTICA EN DOS FASES (TRASLACIÓN + GIRO)
# =====================================================================

class TwoPhaseMotionProfile:
    """
    Representa la maniobra combinada en dos fases desacopladas en el tiempo:
        Fase 1 (t in [0, T1]):
            Traslación: 0 -> Delta_h (10 mm)
            Giro: 0 deg (fijo en posición cerrada de rotación)
        Fase 2 (t in [T1, T1 + T2]):
            Traslación: Delta_h (10 mm, fija en posición elevada)
            Giro: 0 -> Delta_theta (110 deg)

    Continuidad en la frontera t = T1:
        - h(T1) = Delta_h, v_h(T1-) = 0, a_h(T1-) = 0.
        - theta(T1) = 0, omega(T1+) = 0, alpha(T1+) = 0.
        Ambas fases parten y concluyen con velocidad y aceleración exactamente nulas,
        garantizando suavidad C^2 sin discontinuidades dinámicas ni choques en el enlace.
    """

    def __init__(
        self,
        delta_h_mm: float = 10.0,
        delta_theta_deg: float = 110.0,
        T1: float = 0.5,
        T2: float = 0.5
    ):
        self.delta_h_mm = float(delta_h_mm)
        self.delta_theta_deg = float(delta_theta_deg)
        self.delta_theta_rad = math.radians(self.delta_theta_deg)
        self.T1 = float(T1)
        self.T2 = float(T2)
        self.T_total = self.T1 + self.T2

        self.phase1_h = SinglePhaseKinematics(
            name="Fase 1: Traslacion",
            delta_q=self.delta_h_mm,
            unit="mm",
            duration_T=self.T1,
            q0=0.0,
            si_factor=1e-3,
            si_unit="m"
        )

        self.phase2_theta_deg = SinglePhaseKinematics(
            name="Fase 2: Giro (deg)",
            delta_q=self.delta_theta_deg,
            unit="deg",
            duration_T=self.T2,
            q0=0.0,
            si_factor=math.pi / 180.0,
            si_unit="rad"
        )

        self.phase2_theta_rad = SinglePhaseKinematics(
            name="Fase 2: Giro (rad)",
            delta_q=self.delta_theta_rad,
            unit="rad",
            duration_T=self.T2,
            q0=0.0,
            si_factor=1.0,
            si_unit="rad"
        )

    def state_at(self, t: float) -> Dict[str, float]:
        """Devuelve el estado completo del mecanismo en cualquier instante t."""
        if t < 0.0:
            return {
                "t": t, "phase": 0,
                "h_mm": 0.0, "v_mm_s": 0.0, "a_mm_s2": 0.0,
                "theta_deg": 0.0, "omega_deg_s": 0.0, "alpha_deg_s2": 0.0,
                "theta_rad": 0.0, "omega_rad_s": 0.0, "alpha_rad_s2": 0.0
            }
        elif t <= self.T1:
            # Fase 1 activa
            return {
                "t": t, "phase": 1,
                "h_mm": self.phase1_h.position(t),
                "v_mm_s": self.phase1_h.velocity(t),
                "a_mm_s2": self.phase1_h.acceleration(t),
                "theta_deg": 0.0, "omega_deg_s": 0.0, "alpha_deg_s2": 0.0,
                "theta_rad": 0.0, "omega_rad_s": 0.0, "alpha_rad_s2": 0.0
            }
        elif t <= self.T_total:
            # Fase 2 activa
            tau = t - self.T1
            return {
                "t": t, "phase": 2,
                "h_mm": self.delta_h_mm,
                "v_mm_s": 0.0,
                "a_mm_s2": 0.0,
                "theta_deg": self.phase2_theta_deg.position(tau),
                "omega_deg_s": self.phase2_theta_deg.velocity(tau),
                "alpha_deg_s2": self.phase2_theta_deg.acceleration(tau),
                "theta_rad": self.phase2_theta_rad.position(tau),
                "omega_rad_s": self.phase2_theta_rad.velocity(tau),
                "alpha_rad_s2": self.phase2_theta_rad.acceleration(tau)
            }
        else:
            # Fin del recorrido
            return {
                "t": t, "phase": 3,
                "h_mm": self.delta_h_mm, "v_mm_s": 0.0, "a_mm_s2": 0.0,
                "theta_deg": self.delta_theta_deg, "omega_deg_s": 0.0, "alpha_deg_s2": 0.0,
                "theta_rad": self.delta_theta_rad, "omega_rad_s": 0.0, "alpha_rad_s2": 0.0
            }


# =====================================================================
# 4. SEPARACIÓN RIGUROSA: CINEMÁTICA VS FUERZA, POTENCIA Y ENERGÍA
# =====================================================================

class DynamicsIndeterminacyAnalysis:
    """
    Analiza y documenta la imposibilidad física y matemática de dimensionar
    un motor a partir de un perfil puramente cinemático sin los parámetros
    reales de masa, inercia, rozamiento, cargas aerodinámicas y transmisión.
    """

    @staticmethod
    def inspect_reference_model(config_path: str) -> Dict[str, Any]:
        """
        Lee la configuración de referencia (C02_CANDIDATA.json u otra)
        y extrae el estado de masa, inercia, mecanismos y validaciones.
        """
        if not os.path.exists(config_path):
            return {
                "status": "file_not_found",
                "path": config_path,
                "actual_mass_kg": None,
                "actual_CG_m": None,
                "actual_inertia_kgm2": None
            }

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "status": "loaded",
            "path": config_path,
            "id": data.get("id"),
            "actual_mass_kg": data.get("actual_mass_kg"),
            "actual_CG_m": data.get("actual_CG_m"),
            "actual_inertia_kgm2": data.get("actual_inertia_kgm2"),
            "rotor_motor_servo_and_cooling_qualified": data.get("rotor_motor_servo_and_cooling_qualified"),
            "mass_targets_are_actual_masses": data.get("mass_targets_are_actual_masses"),
            "door_motion": data.get("door_motion")
        }

    @staticmethod
    def get_indeterminacy_breakdown() -> Dict[str, Any]:
        """
        Devuelve el desglose formal de ecuaciones dinámicas y la lista
        exhaustiva de parámetros ausentes indispensables para el dimensionamiento.
        """
        return {
            "fase_1_traslacion": {
                "ecuacion_fuerza_actuador": "F_act(t) = m * a(t) + F_grav + F_fric(v) + F_aero(v_aire, P_ducto) + F_sello",
                "ecuacion_potencia": "P_mec(t) = F_act(t) * v(t)",
                "energia_mecanica": "E_mec = integral(P_mec^+(t) * dt)",
                "potencia_electrica_motor": "P_elec(t) = P_mec(t) / eta_mecanica + I_motor^2 * R_bobina",
                "parametros_requeridos": [
                    {"param": "m", "desc": "Masa física real de la compuerta y herrajes móviles", "estado": "INDETERMINADO (null en C02)"},
                    {"param": "g_vector", "desc": "Orientación de la compuerta respecto al vector gravedad (+Z vs -Z)", "estado": "GEOMETRÍA DIVERGENTE (4 superiores elevan contra gravedad, 4 inferiores descienden a favor)"},
                    {"param": "F_fric", "desc": "Fuerza de fricción en guías lineales (fricción estática/Coulomb y viscosa)", "estado": "DESCONOCIDO (no existe síntesis de guía ni cojinetes)"},
                    {"param": "F_aero", "desc": "Carga aerodinámica por gradiente de presión entre exterior y conducto del ventilador", "estado": "DESCONOCIDO (solvers CFD pausados, flujo no resuelto)"},
                    {"param": "F_sello", "desc": "Resistencia de compresión/despegue del labio de sellado perimetral", "estado": "DESCONOCIDO (sellos no dimensionados ni diseñados)"},
                    {"param": "i_transmision", "desc": "Relación de transmisión cinemática husillo/biela/motor", "estado": "DESCONOCIDO (mecanismo no existente)"},
                    {"param": "eta_mecanica", "desc": "Rendimiento mecánico de la transmisión", "estado": "DESCONOCIDO"}
                ]
            },
            "fase_2_giro": {
                "ecuacion_par_actuador": "tau_act(t) = I_eje * alpha(t) + tau_grav(theta) + tau_fric(omega) + tau_aero(theta, v_aire)",
                "ecuacion_potencia": "P_mec(t) = tau_act(t) * omega(t)",
                "energia_mecanica": "E_mec = integral(P_mec^+(t) * dt)",
                "parametros_requeridos": [
                    {"param": "I_eje", "desc": "Momento de inercia másico respecto al eje real de giro", "estado": "INDETERMINADO (null en C02)"},
                    {"param": "tau_grav(theta)", "desc": "Par de gravedad variable m * g * r_CG(theta)", "estado": "INDETERMINADO (CG real null)"},
                    {"param": "tau_fric", "desc": "Fricción en muñones/bisagras", "estado": "DESCONOCIDO (bisagras son líneas de construcción CAD, no herrajes)"},
                    {"param": "tau_aero(theta)", "desc": "Momento aerodinámico de deflexión sobre la placa expuesta al flujo externo", "estado": "DESCONOCIDO"},
                    {"param": "i_reductor", "desc": "Brazo de palanca o reductor del servomotor/actuador", "estado": "DESCONOCIDO"}
                ]
            },
            "metricas_cinematicas_normalizadas": {
                "aceleracion_especifica_traslacion": "a(t) [m/s^2] = F_inercial / m [N/kg]",
                "aceleracion_especifica_rotacion": "alpha(t) [rad/s^2] = tau_inercial / I [N*m / (kg*m^2)]",
                "nota": "Estas métricas adimensionales o normalizadas son los únicos invariantes estrictamente cinemáticos independientes de la masa."
            }
        }


# =====================================================================
# 5. GENERADOR DE RESULTADOS, TABLAS Y COMPARATIVAS
# =====================================================================

def generate_phase_tables(
    durations: List[float] = [0.25, 0.5, 1.0, 2.0],
    dh_mm: float = 10.0,
    dtheta_deg: float = 110.0
) -> Dict[str, Any]:
    """
    Genera las tablas completas de traslación y rotación para las duraciones dadas,
    con chequeo analítico y muestreos a diferentes densidades de malla N.
    """
    dtheta_rad = math.radians(dtheta_deg)
    g0 = 9.80665  # m/s^2 (referencia C02_CANDIDATA)

    results_translation = []
    results_rotation = []
    sampling_sensitivity = []

    for T in durations:
        # Traslación
        trans = SinglePhaseKinematics("Traslacion", dh_mm, "mm", T, si_factor=1e-3, si_unit="m")
        v_max_mms = trans.v_max_exact
        v_max_ms = trans.v_max_si
        a_max_mms2 = trans.a_max_exact
        a_max_ms2 = trans.a_max_si
        a_max_g = a_max_ms2 / g0
        j_max_mms3 = trans.j_max_exact
        j_max_ms3 = j_max_mms3 * 1e-3

        results_translation.append({
            "T_fase_s": T,
            "delta_h_mm": dh_mm,
            "v_max_mm_s": v_max_mms,
            "v_max_m_s": v_max_ms,
            "a_max_mm_s2": a_max_mms2,
            "a_max_m_s2": a_max_ms2,
            "a_max_g0": a_max_g,
            "j_max_mm_s3": j_max_mms3,
            "j_max_m_s3": j_max_ms3,
            "t_vmax_s": trans.t_vmax,
            "t_amax_s": trans.t_amax,
            "fuerza_especifica_inercial_N_kg": a_max_ms2
        })

        # Rotación
        rot_deg = SinglePhaseKinematics("Rotacion_deg", dtheta_deg, "deg", T, si_factor=math.pi / 180.0, si_unit="rad")
        rot_rad = SinglePhaseKinematics("Rotacion_rad", dtheta_rad, "rad", T, si_factor=1.0, si_unit="rad")

        w_max_degs = rot_deg.v_max_exact
        w_max_rads = rot_rad.v_max_exact
        w_max_rpm = (w_max_degs / 360.0) * 60.0

        alpha_max_degs2 = rot_deg.a_max_exact
        alpha_max_rads2 = rot_rad.a_max_exact

        j_rot_degs3 = rot_deg.j_max_exact
        j_rot_rads3 = rot_rad.j_max_exact

        results_rotation.append({
            "T_fase_s": T,
            "delta_theta_deg": dtheta_deg,
            "delta_theta_rad": dtheta_rad,
            "omega_max_deg_s": w_max_degs,
            "omega_max_rad_s": w_max_rads,
            "omega_max_rpm": w_max_rpm,
            "alpha_max_deg_s2": alpha_max_degs2,
            "alpha_max_rad_s2": alpha_max_rads2,
            "jerk_rot_max_deg_s3": j_rot_degs3,
            "jerk_rot_max_rad_s3": j_rot_rads3,
            "t_wmax_s": rot_deg.t_vmax,
            "t_alphamax_s": rot_deg.t_amax,
            "par_especifico_inercial_Nm_kgm2": alpha_max_rads2
        })

    # Sensibilidad de muestreo para T = 0.5 s (caso representativo)
    trans_ref = SinglePhaseKinematics("Traslacion_Ref", dh_mm, "mm", 0.5, si_factor=1e-3, si_unit="m")
    rot_ref = SinglePhaseKinematics("Rotacion_Ref", dtheta_deg, "deg", 0.5, si_factor=math.pi / 180.0, si_unit="rad")

    grid_sizes = [21, 51, 101, 501, 1001, 5001, 10001]
    for n in grid_sizes:
        check_trans = trans_ref.evaluate_sampling_accuracy(n)
        check_rot = rot_ref.evaluate_sampling_accuracy(n)
        sampling_sensitivity.append({
            "n_points": n,
            "dt_s": check_trans["dt_s"],
            # Traslación
            "trans_v_exact": check_trans["v_max_exact"],
            "trans_v_sampled": check_trans["v_max_sampled_analytic"],
            "trans_v_err_rel_pct": check_trans["rel_err_v_sampled_pct"],
            "trans_a_exact": check_trans["a_max_exact"],
            "trans_a_sampled": check_trans["a_max_sampled_analytic"],
            "trans_a_err_rel_pct": check_trans["rel_err_a_sampled_pct"],
            "trans_a_fd": check_trans["a_max_fd"],
            "trans_a_fd_err": check_trans["err_a_fd"],
            "trans_int_v_err": check_trans["integral_v_error"],
            "trans_int_a": check_trans["integral_a_trapezoid"],
            # Rotación
            "rot_w_exact": check_rot["v_max_exact"],
            "rot_w_sampled": check_rot["v_max_sampled_analytic"],
            "rot_w_err_rel_pct": check_rot["rel_err_v_sampled_pct"],
            "rot_alpha_exact": check_rot["a_max_exact"],
            "rot_alpha_sampled": check_rot["a_max_sampled_analytic"],
            "rot_alpha_err_rel_pct": check_rot["rel_err_a_sampled_pct"],
            "rot_alpha_fd": check_rot["a_max_fd"],
            "rot_alpha_fd_err": check_rot["err_a_fd"]
        })

    return {
        "metadata": {
            "polinomio": "10*u^3 - 15*u^4 + 6*u^5",
            "c_v_adimensional": SmoothQuinticPolynomial.C_V,
            "c_a_adimensional": SmoothQuinticPolynomial.C_A,
            "c_a_exacto_formula": "10 / sqrt(3)",
            "u_vmax": SmoothQuinticPolynomial.U_VMAX,
            "u_amax1": SmoothQuinticPolynomial.U_AMAX1,
            "u_amax2": SmoothQuinticPolynomial.U_AMAX2,
            "g0_m_s2": g0,
            "fuente_geometria": "entradas/investigacion-aeronautica/modelos_integrados/producto_A07/LEEME.md",
            "fuente_configuracion": "entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json"
        },
        "translation_table": results_translation,
        "rotation_table": results_rotation,
        "sampling_sensitivity": sampling_sensitivity
    }


def export_tables_to_csv(data: Dict[str, Any], output_path: str) -> None:
    """Exporta las tablas en formato CSV legible."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Sección 1: Traslación
        writer.writerow(["=== FASE 1: TRASLACION (Delta h = 10.0 mm) ==="])
        writer.writerow([
            "T_fase [s]", "Delta_h [mm]", "v_max [mm/s]", "v_max [m/s]",
            "a_max [mm/s^2]", "a_max [m/s^2]", "a_max [g0]", "j_max [mm/s^3]",
            "t_vmax [s]", "t_amax [s]", "Fuerza_especifica_inercial [N/kg]"
        ])
        for row in data["translation_table"]:
            writer.writerow([
                f"{row['T_fase_s']:.2f}",
                f"{row['delta_h_mm']:.1f}",
                f"{row['v_max_mm_s']:.4f}",
                f"{row['v_max_m_s']:.6f}",
                f"{row['a_max_mm_s2']:.4f}",
                f"{row['a_max_m_s2']:.6f}",
                f"{row['a_max_g0']:.5f}",
                f"{row['j_max_mm_s3']:.2f}",
                f"{row['t_vmax_s']:.4f}",
                f"{row['t_amax_s']:.4f}",
                f"{row['fuerza_especifica_inercial_N_kg']:.6f}"
            ])

        writer.writerow([])
        # Sección 2: Rotación
        writer.writerow(["=== FASE 2: ROTACION (Delta theta = 110.0 deg) ==="])
        writer.writerow([
            "T_fase [s]", "Delta_theta [deg]", "Delta_theta [rad]",
            "omega_max [deg/s]", "omega_max [rad/s]", "omega_max [rpm]",
            "alpha_max [deg/s^2]", "alpha_max [rad/s^2]", "jerk_rot_max [deg/s^3]",
            "t_wmax [s]", "t_alphamax [s]", "Par_especifico_inercial [N*m/(kg*m^2)]"
        ])
        for row in data["rotation_table"]:
            writer.writerow([
                f"{row['T_fase_s']:.2f}",
                f"{row['delta_theta_deg']:.1f}",
                f"{row['delta_theta_rad']:.6f}",
                f"{row['omega_max_deg_s']:.4f}",
                f"{row['omega_max_rad_s']:.6f}",
                f"{row['omega_max_rpm']:.4f}",
                f"{row['alpha_max_deg_s2']:.4f}",
                f"{row['alpha_max_rad_s2']:.6f}",
                f"{row['jerk_rot_max_deg_s3']:.2f}",
                f"{row['t_wmax_s']:.4f}",
                f"{row['t_alphamax_s']:.4f}",
                f"{row['par_especifico_inercial_Nm_kgm2']:.6f}"
            ])

        writer.writerow([])
        # Sección 3: Sensibilidad muestreo
        writer.writerow(["=== SENSIBILIDAD DE MUESTREO (T = 0.5 s) ==="])
        writer.writerow([
            "N_puntos", "dt [s]", "v_analitico [mm/s]", "v_muestreado [mm/s]", "err_rel_v [%]",
            "a_analitico [mm/s^2]", "a_muestreado [mm/s^2]", "err_rel_a [%]",
            "a_diferencias_finitas [mm/s^2]", "err_df [mm/s^2]", "err_integral_posicion [mm]"
        ])
        for row in data["sampling_sensitivity"]:
            writer.writerow([
                row["n_points"],
                f"{row['dt_s']:.6f}",
                f"{row['trans_v_exact']:.4f}",
                f"{row['trans_v_sampled']:.4f}",
                f"{row['trans_v_err_rel_pct']:.6f}",
                f"{row['trans_a_exact']:.4f}",
                f"{row['trans_a_sampled']:.4f}",
                f"{row['trans_a_err_rel_pct']:.6f}",
                f"{row['trans_a_fd']:.4f}",
                f"{row['trans_a_fd_err']:.6f}",
                f"{row['trans_int_v_err']:.2e}"
            ])


def main():
    print("=" * 70)
    print("ANÁLISIS INDEPENDIENTE DE PERFILES TEMPORALES (A07 / C02)")
    print("Polinomio quintico: s(u) = 10*u^3 - 15*u^4 + 6*u^5")
    print("=" * 70)

    # 1. Generar tablas cinemáticas
    durations = [0.25, 0.5, 1.0, 2.0]
    data = generate_phase_tables(durations=durations, dh_mm=10.0, dtheta_deg=110.0)

    # 2. Imprimir tablas por consola
    print("\n--- FASE 1: TRASLACIÓN PURA (Delta h = 10 mm) ---")
    print(f"{'T (s)':<8} | {'v_max (mm/s)':<14} | {'v_max (m/s)':<12} | {'a_max (mm/s^2)':<15} | {'a_max (m/s^2)':<13} | {'a_max (g0)':<10}")
    print("-" * 80)
    for r in data["translation_table"]:
        print(f"{r['T_fase_s']:<8.2f} | {r['v_max_mm_s']:<14.4f} | {r['v_max_m_s']:<12.6f} | {r['a_max_mm_s2']:<15.4f} | {r['a_max_m_s2']:<13.6f} | {r['a_max_g0']:<10.5f}")

    print("\n--- FASE 2: ROTACIÓN PURA (Delta theta = 110 deg) ---")
    print(f"{'T (s)':<8} | {'w_max (deg/s)':<14} | {'w_max (rad/s)':<14} | {'w_max (rpm)':<12} | {'alpha_max (deg/s^2)':<20} | {'alpha_max (rad/s^2)':<20}")
    print("-" * 98)
    for r in data["rotation_table"]:
        print(f"{r['T_fase_s']:<8.2f} | {r['omega_max_deg_s']:<14.4f} | {r['omega_max_rad_s']:<14.6f} | {r['omega_max_rpm']:<12.4f} | {r['alpha_max_deg_s2']:<20.4f} | {r['alpha_max_rad_s2']:<20.6f}")

    print("\n--- CHEQUEO ANALÍTICO VS MUESTREO (T = 0.5 s) ---")
    print(f"{'N pts':<8} | {'dt (ms)':<8} | {'v_muestreo':<12} | {'err_v (%)':<10} | {'a_muestreo':<12} | {'err_a (%)':<10} | {'a_dif_fin':<12}")
    print("-" * 82)
    for s in data["sampling_sensitivity"]:
        dt_ms = s["dt_s"] * 1000.0
        print(f"{s['n_points']:<8} | {dt_ms:<8.2f} | {s['trans_v_sampled']:<12.4f} | {s['trans_v_err_rel_pct']:<10.4f} | {s['trans_a_sampled']:<12.4f} | {s['trans_a_err_rel_pct']:<10.4f} | {s['trans_a_fd']:<12.4f}")

    # 3. Diagnóstico de parámetros dinámicos en modelo de referencia
    ref_path = "entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json"
    inspection = DynamicsIndeterminacyAnalysis.inspect_reference_model(ref_path)
    breakdown = DynamicsIndeterminacyAnalysis.get_indeterminacy_breakdown()

    print("\n--- AUDITORÍA DE PARÁMETROS DINÁMICOS EN CONFIGURACIÓN DE REFERENCIA ---")
    print(f"Archivo de configuración: {ref_path}")
    print(f"Estado de lectura: {inspection['status']}")
    print(f"Masa física real asignada (actual_mass_kg): {inspection.get('actual_mass_kg')}")
    print(f"Centro de gravedad físico real (actual_CG_m): {inspection.get('actual_CG_m')}")
    print(f"Tensor de inercia real (actual_inertia_kgm2): {inspection.get('actual_inertia_kgm2')}")
    print(f"Calificación de actuadores/rotores: {inspection.get('rotor_motor_servo_and_cooling_qualified')}")
    print("Conclusión dinámica: Imposible dimensionar motor sin masa, inercia, rozamiento ni cargas aerodinámicas.")

    # 4. Guardar salidas estructuradas
    salidas_dir = "salidas"
    os.makedirs(salidas_dir, exist_ok=True)

    json_path = os.path.join(salidas_dir, "tablas_perfiles.json")
    with open(json_path, "w", encoding="utf-8") as f:
        export_payload = {
            **data,
            "auditoria_referencia": inspection,
            "desglose_indeterminacion_dinamica": breakdown
        }
        json.dump(export_payload, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Datos estructurados guardados en: {json_path}")

    csv_path = os.path.join(salidas_dir, "tablas_perfiles.csv")
    export_tables_to_csv(data, csv_path)
    print(f"[OK] Tablas CSV guardadas en: {csv_path}")


if __name__ == "__main__":
    main()
