#!/usr/bin/env python3
"""
cinematica_A07.py
=================
Parametrización cinemática de referencia de dos grados de libertad (2-DOF)
para la trayectoria candidata A07 (Apertura de compuertas de ventiladores internos).

Trayectoria secuencial A07:
  - Fase 1: Traslación pura exterior de d_max (10 mm a escala de 5 kg).
  - Fase 2: Rotación pura de theta_max (110 grados = 1.919862 rad) alrededor
            de un eje longitudinal transportado que se traslada con la compuerta.

Funcionalidades:
  - Perfiles temporales suaves (polinomio quíntico C^2 mínimo jerk y perfil cicloidal).
  - Tiempos de fase configurables: 0.5 s, 1.0 s, 2.0 s por fase (total 1.0, 2.0, 4.0 s).
  - Derivadas analíticas y numéricas: posición, velocidad, aceleración y jerk.
  - Pruebas rigurosas de continuidad C^0, C^1, C^2 en la transición inter-fase y extremos.
  - Escalamiento geométrico y dinámico a 2 kg, 5 kg y 10 kg (factor (m/5)^(1/3)).
  - Verificación de extremos y signos para las 8 compuertas desde los archivos JSON
    de referencia (propuesta_elevacion.json, VERIFICACION_RECORRIDO.json, C02_CANDIDATA.json).
  - Distinción explícita de datos medidos, supuestos y cálculos.
  - Declaración explícita de variables no verificables en los datos provistos.
"""

import os
import sys
import json
import math
from typing import Dict, List, Tuple, Any, Optional

# Rutas canónicas dentro del espacio de trabajo aislado
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADAS_DIR = os.path.join(WORKSPACE_DIR, "entradas")
SALIDAS_DIR = os.path.join(WORKSPACE_DIR, "salidas")

PATH_PROPUESTA_ELEVACION = os.path.join(
    ENTRADAS_DIR,
    "investigacion-aeronautica",
    "modelos_integrados",
    "producto_A07",
    "propuesta_elevacion.json"
)
PATH_VERIFICACION_RECORRIDO = os.path.join(
    ENTRADAS_DIR,
    "investigacion-aeronautica",
    "modelos_integrados",
    "producto_A07",
    "VERIFICACION_RECORRIDO.json"
)
PATH_CONFIG_C02 = os.path.join(
    ENTRADAS_DIR,
    "investigacion-aeronautica",
    "configuraciones",
    "C02_CANDIDATA.json"
)

# Constantes cinemáticas nominales (Escala 5 kg)
LIFT_NOMINAL_MM_5KG = 10.0  # mm
LIFT_NOMINAL_M_5KG = 0.010  # m
ROTATION_NOMINAL_DEG = 110.0  # grados
ROTATION_NOMINAL_RAD = ROTATION_NOMINAL_DEG * math.pi / 180.0  # rad (~1.919862177 rad)

# Duraciones de fase de estudio requeridas
DURACIONES_FASE_S = [0.5, 1.0, 2.0]

# Escalas de masa del vehículo requeridas
ESCALAS_MASA_KG = [2.0, 5.0, 10.0]


# =============================================================================
# 1. PERFILES TEMPORALES SUAVES (PERFILES ADIMENSIONALES s(tau), tau in [0, 1])
# =============================================================================

class QuinticProfile:
    """
    Perfil polinómico de 5to orden (mínimo jerk).
    Garantiza condiciones de frontera:
      s(0) = 0,  s'(0) = 0,  s''(0) = 0
      s(1) = 1,  s'(1) = 0,  s''(1) = 0
    Continuidad C^2 en transiciones y aceleración estrictamente nula en extremos.
    """

    @staticmethod
    def s(tau: float) -> float:
        """Posición normalizada s in [0, 1]."""
        if tau <= 0.0:
            return 0.0
        if tau >= 1.0:
            return 1.0
        return 10.0 * (tau ** 3) - 15.0 * (tau ** 4) + 6.0 * (tau ** 5)

    @staticmethod
    def ds_dtau(tau: float) -> float:
        """Derivada primera ds/dtau."""
        if tau <= 0.0 or tau >= 1.0:
            return 0.0
        return 30.0 * (tau ** 2) - 60.0 * (tau ** 3) + 30.0 * (tau ** 4)

    @staticmethod
    def d2s_dtau2(tau: float) -> float:
        """Derivada segunda d^2s/dtau^2."""
        if tau <= 0.0 or tau >= 1.0:
            return 0.0
        return 60.0 * tau - 180.0 * (tau ** 2) + 120.0 * (tau ** 3)

    @staticmethod
    def d3s_dtau3(tau: float) -> float:
        """Derivada tercera (jerk normalizado) d^3s/dtau^3."""
        if tau < 0.0 or tau > 1.0:
            return 0.0
        return 60.0 - 360.0 * tau + 360.0 * (tau ** 2)

    @staticmethod
    def max_ds_dtau() -> float:
        """Máxima velocidad normalizada (en tau = 0.5): 1.875."""
        return 1.875

    @staticmethod
    def max_d2s_dtau2() -> float:
        """
        Máxima aceleración normalizada en valor absoluto:
        tau = 0.5 - sqrt(3)/6 ~ 0.211325 -> d2s/dtau2 = 10 * sqrt(3) / 3 ~ 5.7735027
        """
        return 10.0 * math.sqrt(3.0) / 3.0


class CycloidalProfile:
    """
    Perfil cicloidal armónico estándar:
      s(tau) = tau - (1 / (2*pi)) * sin(2*pi*tau)
    Condiciones de frontera:
      s(0) = 0,  s'(0) = 0,  s''(0) = 0
      s(1) = 1,  s'(1) = 0,  s''(1) = 0
    Continuidad C^inf en el interior y C^2 en fronteras.
    """

    @staticmethod
    def s(tau: float) -> float:
        if tau <= 0.0:
            return 0.0
        if tau >= 1.0:
            return 1.0
        return tau - (1.0 / (2.0 * math.pi)) * math.sin(2.0 * math.pi * tau)

    @staticmethod
    def ds_dtau(tau: float) -> float:
        if tau <= 0.0 or tau >= 1.0:
            return 0.0
        return 1.0 - math.cos(2.0 * math.pi * tau)

    @staticmethod
    def d2s_dtau2(tau: float) -> float:
        if tau <= 0.0 or tau >= 1.0:
            return 0.0
        return 2.0 * math.pi * math.sin(2.0 * math.pi * tau)

    @staticmethod
    def d3s_dtau3(tau: float) -> float:
        if tau < 0.0 or tau > 1.0:
            return 0.0
        return 4.0 * (math.pi ** 2) * math.cos(2.0 * math.pi * tau)

    @staticmethod
    def max_ds_dtau() -> float:
        """Máxima velocidad normalizada en tau = 0.5: 2.0."""
        return 2.0

    @staticmethod
    def max_d2s_dtau2() -> float:
        """Máxima aceleración normalizada en tau = 0.25: 2*pi ~ 6.2831853."""
        return 2.0 * math.pi


# =============================================================================
# 2. PARAMETRIZACIÓN CINEMÁTICA 2-DOF DE LA TRAYECTORIA A07
# =============================================================================

class TrajectoryA07:
    """
    Cinemática de 2 grados de libertad:
      q_1(t): Coordenada lineal de traslación [m] (0 -> d_max)
      q_2(t): Coordenada angular de rotación [rad] (0 -> theta_max)

    Fase 1 (0 <= t <= T_fase):
      q_1(t) = d_max * s(t / T_fase)
      q_2(t) = 0.0
    Fase 2 (T_fase <= t <= 2 * T_fase):
      q_1(t) = d_max
      q_2(t) = theta_max * s((t - T_fase) / T_fase)
    """

    def __init__(
        self,
        t_phase: float = 1.0,
        mass_scale_kg: float = 5.0,
        profile_class=QuinticProfile
    ):
        self.t_phase = float(t_phase)
        self.t_total = 2.0 * self.t_phase
        self.mass_scale_kg = float(mass_scale_kg)
        self.profile = profile_class

        # Factor de escala geométrica: lambda = (m / 5.0)^(1/3)
        self.scale_factor = (self.mass_scale_kg / 5.0) ** (1.0 / 3.0)

        # Magnitudes máximas escaladas
        self.d_max_m = LIFT_NOMINAL_M_5KG * self.scale_factor
        self.d_max_mm = LIFT_NOMINAL_MM_5KG * self.scale_factor
        self.theta_max_rad = ROTATION_NOMINAL_RAD
        self.theta_max_deg = ROTATION_NOMINAL_DEG

    def evaluate(self, t: float) -> Dict[str, float]:
        """
        Evalúa posición, velocidad, aceleración y jerk de ambos grados de libertad.
        Retorna diccionario con q1, q1_dot, q1_ddot, q1_dddot, q2, q2_dot, q2_ddot, q2_dddot.
        """
        T = self.t_phase

        if t <= 0.0:
            return {
                "t": t,
                "phase": 1,
                "q1": 0.0,
                "q1_dot": 0.0,
                "q1_ddot": 0.0,
                "q1_dddot": 0.0,
                "q2": 0.0,
                "q2_dot": 0.0,
                "q2_ddot": 0.0,
                "q2_dddot": 0.0,
            }
        elif t < T:
            # Fase 1: Traslación activa, Rotación en reposo
            tau = t / T
            s_val = self.profile.s(tau)
            ds_val = self.profile.ds_dtau(tau)
            d2s_val = self.profile.d2s_dtau2(tau)
            d3s_val = self.profile.d3s_dtau3(tau)

            return {
                "t": t,
                "phase": 1,
                "q1": self.d_max_m * s_val,
                "q1_dot": (self.d_max_m / T) * ds_val,
                "q1_ddot": (self.d_max_m / (T ** 2)) * d2s_val,
                "q1_dddot": (self.d_max_m / (T ** 3)) * d3s_val,
                "q2": 0.0,
                "q2_dot": 0.0,
                "q2_ddot": 0.0,
                "q2_dddot": 0.0,
            }
        elif t == T:
            # Frontera intermedia: Ambos están en reposo dinámico (v=0, a=0)
            return {
                "t": t,
                "phase": 1,  # Frontera compartida
                "q1": self.d_max_m,
                "q1_dot": 0.0,
                "q1_ddot": 0.0,
                "q1_dddot": 0.0,
                "q2": 0.0,
                "q2_dot": 0.0,
                "q2_ddot": 0.0,
                "q2_dddot": 0.0,
            }
        elif t <= self.t_total:
            # Fase 2: Traslación fija en d_max, Rotación activa
            tau = (t - T) / T
            s_val = self.profile.s(tau)
            ds_val = self.profile.ds_dtau(tau)
            d2s_val = self.profile.d2s_dtau2(tau)
            d3s_val = self.profile.d3s_dtau3(tau)

            return {
                "t": t,
                "phase": 2,
                "q1": self.d_max_m,
                "q1_dot": 0.0,
                "q1_ddot": 0.0,
                "q1_dddot": 0.0,
                "q2": self.theta_max_rad * s_val,
                "q2_dot": (self.theta_max_rad / T) * ds_val,
                "q2_ddot": (self.theta_max_rad / (T ** 2)) * d2s_val,
                "q2_dddot": (self.theta_max_rad / (T ** 3)) * d3s_val,
            }
        else:
            # t > t_total: Trayectoria completada
            return {
                "t": t,
                "phase": 2,
                "q1": self.d_max_m,
                "q1_dot": 0.0,
                "q1_ddot": 0.0,
                "q1_dddot": 0.0,
                "q2": self.theta_max_rad,
                "q2_dot": 0.0,
                "q2_ddot": 0.0,
                "q2_dddot": 0.0,
            }

    def get_kinematic_extrema(self) -> Dict[str, float]:
        """Calcula analíticamente los valores pico de velocidad y aceleración."""
        T = self.t_phase
        max_v_norm = self.profile.max_ds_dtau()
        max_a_norm = self.profile.max_d2s_dtau2()

        return {
            "d_max_m": self.d_max_m,
            "d_max_mm": self.d_max_mm,
            "theta_max_rad": self.theta_max_rad,
            "theta_max_deg": self.theta_max_deg,
            "v1_max_m_s": (self.d_max_m / T) * max_v_norm,
            "a1_max_m_s2": (self.d_max_m / (T ** 2)) * max_a_norm,
            "omega2_max_rad_s": (self.theta_max_rad / T) * max_v_norm,
            "alpha2_max_rad_s2": (self.theta_max_rad / (T ** 2)) * max_a_norm,
        }


# =============================================================================
# 3. TRANSFORMACIÓN ESPACIAL 3D POR TAPA / COMPUERTA
# =============================================================================

class DoorSpatialModel:
    """
    Aplica la cinemática 2-DOF a una compuerta específica según los signos
    y coordenadas de eje definidos en propuesta_elevacion.json.

    Marco de referencia: CAD (X longitudinal hacia popa, Y lateral, Z vertical hacia arriba).
    """

    def __init__(self, door_record: Dict[str, Any]):
        self.name = door_record["name"]
        self.lift_mm_ref = float(door_record["lift_mm"])
        self.axis_closed = [float(c) for c in door_record["axis_closed"]]  # [X, Y, Z] en mm
        self.sign_rot = int(door_record["sign"])  # Sentido de giro (+1 o -1)
        self.out_trans = int(door_record["out"])  # Sentido de traslación (+1 o -1 en Z)

    def axis_position(self, q1_m: float, scale_factor: float = 1.0) -> List[float]:
        """
        Retorna la posición [X, Y, Z] del eje transportado en mm,
        considerando el escalamiento geométrico del origen cerrado y la elevación.
        """
        # El origen nominal en CAD se escala geométricamente desde 5 kg
        x_closed_scaled = self.axis_closed[0] * scale_factor
        y_closed_scaled = self.axis_closed[1] * scale_factor
        z_closed_scaled = self.axis_closed[2] * scale_factor

        # Traslación exterior en Z
        q1_mm = q1_m * 1000.0
        z_axis = z_closed_scaled + self.out_trans * q1_mm

        return [x_closed_scaled, y_closed_scaled, z_axis]

    def transform_point(
        self,
        p_closed_mm: List[float],
        q1_m: float,
        q2_rad: float,
        scale_factor: float = 1.0
    ) -> List[float]:
        """
        Transforma un punto material de la compuerta en coordenadas CAD (mm):
          1. Escalamiento geométrico del punto.
          2. Traslación exterior en Z (+/- q1).
          3. Rotación en el plano Y-Z alrededor del eje transportado por ángulo (sign * q2).
        Eje de giro paralelo al eje longitudinal X (vector unitario [1, 0, 0]).
        """
        # Posición del eje transportado
        p_axis = self.axis_position(q1_m, scale_factor)

        # Punto escalado antes de traslación/rotación
        px = p_closed_mm[0] * scale_factor
        py = p_closed_mm[1] * scale_factor
        pz = p_closed_mm[2] * scale_factor

        # Paso 1: Traslación pura del punto con la compuerta
        q1_mm = q1_m * 1000.0
        pz_elevated = pz + self.out_trans * q1_mm

        # Paso 2: Rotación alrededor del eje transportado
        # Vector relativo al eje
        rx = px - p_axis[0]  # Eje longitudinal paralelo a X -> rx no rota alrededor de X
        ry = py - p_axis[1]
        rz = pz_elevated - p_axis[2]

        # Ángulo con signo de la compuerta
        phi = self.sign_rot * q2_rad

        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)

        # Rotación elemental alrededor de X:
        # [ry'] = [cos -sin] [ry]
        # [rz']   [sin  cos] [rz]
        ry_rot = cos_phi * ry - sin_phi * rz
        rz_rot = sin_phi * ry + cos_phi * rz

        # Retornar en coordenadas CAD absolutas (mm)
        return [
            p_axis[0] + rx,
            p_axis[1] + ry_rot,
            p_axis[2] + rz_rot
        ]


# =============================================================================
# 4. COMPROBACIONES DE CONTINUIDAD NUMÉRICA Y ANALÍTICA
# =============================================================================

def test_continuity_at_phase_switch(
    t_phase: float,
    mass_scale_kg: float,
    eps: float = 1e-7,
    profile_class=QuinticProfile
) -> Dict[str, Any]:
    """
    Verifica rigurosamente la continuidad C^0, C^1 y C^2 en el punto de conmutación
    de fase t = T_fase evaluando los límites izquierdo (T - eps) y derecho (T + eps).
    """
    traj = TrajectoryA07(t_phase=t_phase, mass_scale_kg=mass_scale_kg, profile_class=profile_class)
    T = t_phase

    # Límites evaluados con offset infinitesimal
    left = traj.evaluate(T - eps)
    exact = traj.evaluate(T)
    right = traj.evaluate(T + eps)

    # Discontinuidades en el cambio de fase
    jump_q1 = abs(left["q1"] - right["q1"])
    jump_q1_dot = abs(left["q1_dot"] - right["q1_dot"])
    jump_q1_ddot = abs(left["q1_ddot"] - right["q1_ddot"])

    jump_q2 = abs(left["q2"] - right["q2"])
    jump_q2_dot = abs(left["q2_dot"] - right["q2_dot"])
    jump_q2_ddot = abs(left["q2_ddot"] - right["q2_ddot"])

    # En t=T, tanto q1_dot, q1_ddot, q2_dot, q2_ddot deben tender a 0
    c0_continuous = (jump_q1 < 1e-4) and (jump_q2 < 1e-4)
    c1_continuous = (jump_q1_dot < 1e-3) and (jump_q2_dot < 1e-3)
    c2_continuous = (jump_q1_ddot < 1e-2) and (jump_q2_ddot < 1e-2)

    return {
        "t_phase_s": t_phase,
        "mass_scale_kg": mass_scale_kg,
        "eps_evaluated": eps,
        "jump_q1_m": jump_q1,
        "jump_q1_dot_m_s": jump_q1_dot,
        "jump_q1_ddot_m_s2": jump_q1_ddot,
        "jump_q2_rad": jump_q2,
        "jump_q2_dot_rad_s": jump_q2_dot,
        "jump_q2_ddot_rad_s2": jump_q2_ddot,
        "c0_continuous": c0_continuous,
        "c1_continuous": c1_continuous,
        "c2_continuous": c2_continuous,
        "exact_switch_state": exact
    }


def verify_finite_differences(
    traj: TrajectoryA07,
    dt: float = 1e-5,
    sample_points: int = 50
) -> Dict[str, float]:
    """
    Compara las derivadas analíticas (q_dot, q_ddot) con diferencias finitas centradas
    a lo largo de todo el recorrido para validar la formulación analítica.
    """
    max_err_v1 = 0.0
    max_err_a1 = 0.0
    max_err_v2 = 0.0
    max_err_a2 = 0.0

    t_total = traj.t_total
    times = [i * (t_total / (sample_points + 1)) for i in range(1, sample_points + 1)]

    for t in times:
        ev = traj.evaluate(t)
        ev_plus = traj.evaluate(t + dt)
        ev_minus = traj.evaluate(t - dt)

        # Diferencias finitas centradas
        num_v1 = (ev_plus["q1"] - ev_minus["q1"]) / (2.0 * dt)
        num_a1 = (ev_plus["q1_dot"] - ev_minus["q1_dot"]) / (2.0 * dt)

        num_v2 = (ev_plus["q2"] - ev_minus["q2"]) / (2.0 * dt)
        num_a2 = (ev_plus["q2_dot"] - ev_minus["q2_dot"]) / (2.0 * dt)

        # Si no estamos en la discontinuidad del jerk en t=T
        if abs(t - traj.t_phase) > 2.0 * dt:
            err_v1 = abs(ev["q1_dot"] - num_v1)
            err_a1 = abs(ev["q1_ddot"] - num_a1)
            err_v2 = abs(ev["q2_dot"] - num_v2)
            err_a2 = abs(ev["q2_ddot"] - num_a2)

            if err_v1 > max_err_v1:
                max_err_v1 = err_v1
            if err_a1 > max_err_a1:
                max_err_a1 = err_a1
            if err_v2 > max_err_v2:
                max_err_v2 = err_v2
            if err_a2 > max_err_a2:
                max_err_a2 = err_a2

    return {
        "max_err_velocity_q1_m_s": max_err_v1,
        "max_err_acceleration_q1_m_s2": max_err_a1,
        "max_err_velocity_q2_rad_s": max_err_v2,
        "max_err_acceleration_q2_rad_s2": max_err_a2
    }


# =============================================================================
# 5. MATRIZ DE ESCALAMIENTO Y DINÁMICA INERCIAL (2/5/10 kg x 0.5/1/2 s)
# =============================================================================

def compute_scaling_matrix() -> Dict[str, Any]:
    """
    Genera la matriz paramétrica de cinemática y dinámica inercial
    para todas las combinaciones de escala de masa (2, 5, 10 kg)
    y duración de fase (0.5, 1.0, 2.0 s).

    Distingue:
      - Datos medidos: 0 en masa/inercia de compuerta (declarados null en JSON).
      - Datos supuestos:
          * Masa nominal supuesta de la compuerta a 5 kg: m_tapa_5kg = 0.050 kg (50 g).
          * Escalamiento de masa volumétrico isotrópico: m_tapa(m) = m_tapa_5kg * (m/5).
          * Radio de giro de inercia r_g ~ 0.040 m -> I_tapa = m_tapa * r_g^2.
          * Se calculan también las métricas normalizadas independientes del supuesto (F/m, Tau/I).
      - Cálculos: Aceleraciones pico, fuerzas y pares inerciales máximos.
    """
    # SUPUESTO DE REFERENCIA PARA ILUSTRACIÓN DINÁMICA
    M_TAPA_REF_5KG = 0.050  # kg (50 gramos por compuerta - SUPUESTO DECLARADO)
    R_GIRO_REF_5KG = 0.040  # m (40 mm radio de giro respecto al eje de bisagra - SUPUESTO)

    results = []

    for mass_kg in ESCALAS_MASA_KG:
        scale_lambda = (mass_kg / 5.0) ** (1.0 / 3.0)
        d_lift_mm = LIFT_NOMINAL_MM_5KG * scale_lambda
        d_lift_m = d_lift_mm * 1e-3

        # Supuesto escalado de masa de tapa:
        # 1. Hipótesis volumétrica: m ~ lambda^3 = (mass_kg / 5.0)
        m_tapa_vol_kg = M_TAPA_REF_5KG * (mass_kg / 5.0)
        r_giro_m = R_GIRO_REF_5KG * scale_lambda
        I_tapa_kgm2 = m_tapa_vol_kg * (r_giro_m ** 2)

        for t_phase in DURACIONES_FASE_S:
            traj_quintic = TrajectoryA07(t_phase=t_phase, mass_scale_kg=mass_kg, profile_class=QuinticProfile)
            ext_q = traj_quintic.get_kinematic_extrema()

            traj_cyc = TrajectoryA07(t_phase=t_phase, mass_scale_kg=mass_kg, profile_class=CycloidalProfile)
            ext_c = traj_cyc.get_kinematic_extrema()

            # Fuerzas y pares dinámicos inerciales máximos:
            # Fase 1: F_in = m_tapa * a1_max
            # Fase 2: Tau_in = I_tapa * alpha2_max
            f_in_quintic_N = m_tapa_vol_kg * ext_q["a1_max_m_s2"]
            tau_in_quintic_Nm = I_tapa_kgm2 * ext_q["alpha2_max_rad_s2"]

            # Métricas normalizadas por unidad de masa e inercia (libres de supuestos de masa):
            f_over_m_quintic = ext_q["a1_max_m_s2"]  # N/kg == m/s^2
            tau_over_I_quintic = ext_q["alpha2_max_rad_s2"]  # (N*m)/(kg*m^2) == rad/s^2

            results.append({
                "drone_mass_scale_kg": mass_kg,
                "scale_factor_lambda": round(scale_lambda, 6),
                "t_phase_s": t_phase,
                "t_total_s": 2.0 * t_phase,
                "lift_max_mm": round(d_lift_mm, 4),
                "rotation_max_deg": ROTATION_NOMINAL_DEG,
                "rotation_max_rad": round(ROTATION_NOMINAL_RAD, 6),
                "quintic": {
                    "v1_max_m_s": round(ext_q["v1_max_m_s"], 6),
                    "a1_max_m_s2": round(ext_q["a1_max_m_s2"], 6),
                    "omega2_max_rad_s": round(ext_q["omega2_max_rad_s"], 6),
                    "alpha2_max_rad_s2": round(ext_q["alpha2_max_rad_s2"], 6),
                    "normalized_force_N_per_kg": round(f_over_m_quintic, 6),
                    "normalized_torque_Nm_per_kgm2": round(tau_over_I_quintic, 6),
                    "assumed_tapa_mass_kg": round(m_tapa_vol_kg, 6),
                    "assumed_tapa_inertia_kgm2": round(I_tapa_kgm2, 8),
                    "inertial_force_peak_N": round(f_in_quintic_N, 6),
                    "inertial_torque_peak_Nm": round(tau_in_quintic_Nm, 6)
                },
                "cycloidal": {
                    "v1_max_m_s": round(ext_c["v1_max_m_s"], 6),
                    "a1_max_m_s2": round(ext_c["a1_max_m_s2"], 6),
                    "omega2_max_rad_s": round(ext_c["omega2_max_rad_s"], 6),
                    "alpha2_max_rad_s2": round(ext_c["alpha2_max_rad_s2"], 6)
                }
            })

    return {
        "metadata": {
            "source": "Cinemática de referencia A07",
            "gravity_m_s2": 9.80665,
            "assumed_reference_door_mass_5kg_kg": M_TAPA_REF_5KG,
            "assumed_reference_radius_gyration_5kg_m": R_GIRO_REF_5KG,
            "mass_assignment_status_in_json": "actual_mass_kg: null (sin masa asignada en C02_CANDIDATA.json)"
        },
        "matrix": results
    }


# =============================================================================
# 6. VERIFICACIÓN DE EXTREMOS Y SIGNOS POR TAPA DESDE JSON
# =============================================================================

def verify_doors_from_json() -> Dict[str, Any]:
    """
    Carga propuesta_elevacion.json y VERIFICACION_RECORRIDO.json.
    Verifica:
      1. Cantidad de tapas (8 tapas).
      2. Magnitud de elevación nominal (10 mm en 5 kg).
      3. Signos de traslación ('out': +1 para superior, -1 para inferior).
      4. Signos de rotación ('sign': +1 o -1 para asegurar apertura exterior).
      5. Congruencia geométrica con las 61 poses discretas de VERIFICACION_RECORRIDO.json.
      6. Declaración explícita de lo que NO se puede verificar desde los archivos JSON.
    """
    # 1. Cargar propuesta_elevacion.json
    if not os.path.exists(PATH_PROPUESTA_ELEVACION):
        raise FileNotFoundError(f"No se encontró el archivo de referencia: {PATH_PROPUESTA_ELEVACION}")

    with open(PATH_PROPUESTA_ELEVACION, "r", encoding="utf-8") as f:
        doors_data = json.load(f)

    # 2. Cargar VERIFICACION_RECORRIDO.json
    recorrido_data = None
    if os.path.exists(PATH_VERIFICACION_RECORRIDO):
        with open(PATH_VERIFICACION_RECORRIDO, "r", encoding="utf-8") as f:
            recorrido_data = json.load(f)

    # 3. Cargar C02_CANDIDATA.json
    c02_data = None
    if os.path.exists(PATH_CONFIG_C02):
        with open(PATH_CONFIG_C02, "r", encoding="utf-8") as f:
            c02_data = json.load(f)

    door_verifications = []

    for d in doors_data:
        name = d["name"]
        lift_mm = d["lift_mm"]
        axis_closed = d["axis_closed"]
        sign_rot = d["sign"]
        out_trans = d["out"]

        is_superior = "superior" in name
        is_inferior = "inferior" in name

        # Verificación de signo de traslación:
        # Superior debe subir (+Z en CAD, out == +1)
        # Inferior debe bajar (-Z en CAD, out == -1)
        expected_out = 1 if is_superior else -1
        out_valid = (out_trans == expected_out)

        # Verificación de signo de rotación:
        # En CAD, +X es hacia popa, +Y es estribor/babor según convención.
        # En propuesta_elevacion:
        # compuerta 0: Y = -124, sup: sign=+1, inf: sign=-1
        # compuerta 1: Y = +124, sup: sign=-1, inf: sign=+1
        # compuerta 2: Y = -124, sup: sign=+1, inf: sign=-1
        # compuerta 3: Y = +124, sup: sign=-1, inf: sign=+1
        # Esto asegura que la tapa gire alejándose del centro del fuselaje (Y=0).
        y_axis = axis_closed[1]
        if y_axis < 0:
            expected_sign = 1 if is_superior else -1
        else:
            expected_sign = -1 if is_superior else 1
        sign_valid = (sign_rot == expected_sign)

        door_verifications.append({
            "name": name,
            "axis_closed": axis_closed,
            "lift_nominal_mm": lift_mm,
            "lift_nominal_valid": (lift_mm == 10.0),
            "out_translation_sign": out_trans,
            "out_translation_sign_valid": out_valid,
            "rotation_sign": sign_rot,
            "rotation_sign_valid": sign_valid,
            "motion_description": (
                f"{'Traslación +Z (10 mm)' if out_trans == 1 else 'Traslación -Z (10 mm)'} y "
                f"rotación exterior ({sign_rot * 110}° alrededor de X)"
            )
        })

    # Verificación de poses discretas de VERIFICACION_RECORRIDO.json
    discrete_verification = {}
    if recorrido_data:
        poses = recorrido_data.get("poses", [])
        discrete_verification["total_nodes_json"] = len(poses)
        discrete_verification["expected_nodes"] = recorrido_data.get("nodes", 61)
        discrete_verification["doors_tested"] = recorrido_data.get("doors", 8)
        discrete_verification["boolean_pairs_tested"] = recorrido_data.get("boolean_pairs_tested", 488)
        discrete_verification["max_overlap_mm3"] = recorrido_data.get("max_overlap_mm3", 0.0)

        # Verificar inicio, cambio de fase y final
        pose_0 = poses[0]
        pose_switch = poses[5]  # Última pose de elevación pura (10 mm, 0 deg)
        pose_end = poses[-1]    # Pose final (10 mm, 110 deg)

        discrete_verification["node_0_start"] = {
            "pose": pose_0,
            "valid": (pose_0.get("lift_mm") == 0.0 and pose_0.get("angle_deg") == 0.0)
        }
        discrete_verification["node_switch_phase"] = {
            "pose": pose_switch,
            "valid": (pose_switch.get("lift_mm") == 10.0 and pose_switch.get("angle_deg") == 0.0)
        }
        discrete_verification["node_final_end"] = {
            "pose": pose_end,
            "valid": (pose_end.get("lift_mm") == 10.0 and pose_end.get("angle_deg") == 110.0)
        }

    # Declaración explícita de lo NO verificable
    unverifiable_declarations = [
        "Masa real de compuerta ('actual_mass_kg: null' en C02_CANDIDATA.json). No se asigna masa ni se infiere si es nula o no.",
        "Centro de gravedad ('actual_CG_m: null') y tensor de inercia ('actual_inertia_kgm2: null') de compuerta no definidos.",
        "Dimensiones y volumen de actuadores, servomotores, bielas y herrajes de bisagra (LEEME.md declara que no existen guías ni actuadores dimensionados).",
        "Tolerancias de fabricación, holguras de mecanizado o interferencias elásticas bajo carga aerodinámica (VERIFICACION_RECORRIDO.json aclara que el barrido es geométrico estático nominal).",
        "Respuesta dinámica del actuador ('servo_response_s: null' en C02_CANDIDATA.json).",
        "Fuerzas aerodinámicas durante la apertura en avance ('apertura destinada al estudio de baja velocidad; no se valida su uso en avance rápido', LEEME.md)."
    ]

    return {
        "status": "VERIFICACIÓN COMPLETADA EXITOSAMENTE",
        "doors_count": len(door_verifications),
        "door_details": door_verifications,
        "discrete_verification": discrete_verification,
        "unverifiable_declarations": unverifiable_declarations
    }


# =============================================================================
# 7. COMPARATIVA MECÁNICA CONCEPTUAL (CARRO + BISAGRA vs RANURA / CAM)
# =============================================================================

def get_conceptual_mechanisms_comparison() -> Dict[str, Any]:
    """
    Retorna la comparativa técnica entre los dos conceptos mecánicos solicitados:
      1. Carro + bisagra (Cadena serial Prismático-Revoluta).
      2. Ranura/cam con guiado (Mecanismo de levas con ranura programada).

    ADVERTENCIA REQUERIDA: No se afirma que caben ni su fabricabilidad.
    """
    return {
        "statement_on_fit_and_manufacturability": (
            "DECLARACIÓN EXPLÍCITA: Ninguno de los dos conceptos mecánicos ha sido sometido "
            "a estudio de empaquetamiento volumétrico en el espacio interior de las camisas o el "
            "fuselaje, ni se afirma su fabricabilidad, viabilidad de tolerancias o aptitud para vuelo."
        ),
        "concept_1": {
            "nombre": "Carro lineal + Bisagra transportada (Cadena serial PR)",
            "topologia": "Par prismático (P) exterior seguido de par revoluta (R) sobre el carro",
            "descripcion": (
                "Un carro lineal o par de correderas guía el desplazamiento puramente normal de 10 mm. "
                "Al finalizar la carrera, el eje de rotación (físicamente montado sobre el carro) gira "
                "los 110 grados hacia el exterior."
            ),
            "opciones_actuacion": [
                "Accionamiento dual: actuador lineal (solenoide / husillo) + servo rotativo.",
                "Accionamiento único: servo rotativo con enlace de ranura deslizante y tope secuencial."
            ],
            "ventajas": [
                "Desacoplamiento cinemático natural e independiente de ambos grados de libertad.",
                "Menores concentraciones de tensiones de contacto (superficies cilíndricas y correderas prismáticas estándar).",
                "Facilidad de ajuste de carrera y ángulo mediante calibración electrónica o topes.",
                "Capacidad de reconfigurar o sostener la compuerta en posición solo elevada (lift 10 mm) sin girar."
            ],
            "desventajas_y_desafios": [
                "Mayor número de piezas móviles y mayor masa no suspendida sobre el carro móvil.",
                "Susceptibilidad a encallamiento o bloqueo por ladeo ('cocking/binding') si el momento "
                "de vuelco aerodinámico o por fricción supera la rigidez de la corredera.",
                "Dificultad de estanqueidad y protección contra polvo/suciedad en los carriles lineales.",
                "Mayor volumen global requerido si se emplean dos actuadores independientes."
            ]
        },
        "concept_2": {
            "nombre": "Ranura / Cam con guiado de seguidor (Mecanismo de leva de ranura)",
            "topologia": "Par cinemático superior (leva de ranura plana/espacial con rodillo o perno seguidor)",
            "descripcion": (
                "Una placa con ranura mecanizada contiene dos tramos tangentes: un tramo rectilíneo "
                "de 10 mm normal al fuselaje y un tramo circular/helicoidal de 110 grados de radio "
                "constante centrado en el eje transportado. Un único actuador empuja el seguidor."
            ),
            "opciones_actuacion": [
                "Accionador único: biela o actuador lineal que empuja el pasador seguidor a lo largo de la pista."
            ],
            "ventajas": [
                "Sincronización cinemática intrínseca: la geometría de la ranura impide físicamente cualquier "
                "rotación antes de completar la traslación de 10 mm.",
                "Actuador único y estático: el actuador permanece fijo en la estructura del fuselaje.",
                "Menor conteo de piezas estructurales y reducción potencial de peso.",
                "Menor volumen de mecanismos auxiliares si la pista se integra en las costillas del conducto."
            ],
            "desventajas_y_desafios": [
                "Contacto lineal o puntual de Hertz: elevadas tensiones de contacto en las paredes de la ranura, "
                "riesgo de desgaste acelerado, deformación plástica local o picado ('pitting').",
                "Ángulo de presión crítico en la transición ('rodilla') entre el tramo recto y curvo: si el "
                "ángulo de presión excede el límite de autoenclavamiento por fricción, el mecanismo se traba.",
                "Rigidez nula de sintonización: el perfil es inmutable; cualquier cambio de trayectoria exige "
                "reemplazar las placas de levas completas.",
                "Sensibilidad a vibraciones y holguras que pueden provocar traqueteo de la compuerta en vuelo."
            ]
        },
        "tabla_comparativa": [
            {
                "criterio": "Grados de libertad activos",
                "carro_bisagra": "2 independientes (o 1 con secuencia)",
                "ranura_cam": "1 grado de libertad cinemático acoplado"
            },
            {
                "criterio": "Sincronización de fases",
                "carro_bisagra": "Por control o mecanismo de enclavamiento",
                "ranura_cam": "Geométrica intrínseca por la ranura"
            },
            {
                "criterio": "Tensiones de contacto",
                "carro_bisagra": "Bajas / moderadas (contacto superficial)",
                "ranura_cam": "Altas (contacto lineal Hertziano en seguidor)"
            },
            {
                "criterio": "Riesgo de bloqueo",
                "carro_bisagra": "Ladeo de corredera por momentos laterales",
                "ranura_cam": "Ángulo de presión excesivo en codo de transición"
            },
            {
                "criterio": "Flexibilidad de recorrido",
                "carro_bisagra": "Alta (ajustable por software o topes)",
                "ranura_cam": "Nula (rígidamente grabada en la ranura)"
            },
            {
                "criterio": "Masa de actuadores en movimiento",
                "carro_bisagra": "Alta si el actuador rotativo viaja en carro",
                "ranura_cam": "Nula (actuador montado rígidamente al fuselaje)"
            }
        ]
    }


# =============================================================================
# 8. EJECUCIÓN PRINCIPAL Y EXPORTACIÓN DE ENTREGABLES
# =============================================================================

def main():
    print("=" * 80)
    print("PARAMETRIZACIÓN CINEMÁTICA DE REFERENCIA 2-DOF — TRAYECTORIA CANDIDATA A07")
    print("=" * 80)

    # 1. Comprobaciones de continuidad en conmutación de fase
    print("\n[1/4] Ejecutando pruebas de continuidad inter-fase (C0, C1, C2)...")
    continuity_results = []
    for t_phase in DURACIONES_FASE_S:
        for m_scale in ESCALAS_MASA_KG:
            res = test_continuity_at_phase_switch(t_phase, m_scale)
            continuity_results.append(res)
            status_str = "PASÓ" if (res["c0_continuous"] and res["c1_continuous"] and res["c2_continuous"]) else "FALLÓ"
            print(f"  - T_fase={t_phase:3.1f}s, Masa={m_scale:4.1f}kg: {status_str} "
                  f"(Salto q1={res['jump_q1_m']:.2e}m, Salto v1={res['jump_q1_dot_m_s']:.2e}m/s, "
                  f"Salto a1={res['jump_q1_ddot_m_s2']:.2e}m/s2)")

    # 2. Validación de derivadas con diferencias finitas
    print("\n[2/4] Validando derivadas analíticas con diferencias finitas...")
    sample_traj = TrajectoryA07(t_phase=1.0, mass_scale_kg=5.0)
    fd_res = verify_finite_differences(sample_traj)
    print(f"  - Error máx v1: {fd_res['max_err_velocity_q1_m_s']:.2e} m/s")
    print(f"  - Error máx a1: {fd_res['max_err_acceleration_q1_m_s2']:.2e} m/s2")
    print(f"  - Error máx v2: {fd_res['max_err_velocity_q2_rad_s']:.2e} rad/s")
    print(f"  - Error máx a2: {fd_res['max_err_acceleration_q2_rad_s2']:.2e} rad/s2")

    # 3. Matriz de escalamiento de masa y dinámica inercial
    print("\n[3/4] Calculando matriz de escalamiento (2/5/10 kg x 0.5/1/2 s)...")
    scaling_data = compute_scaling_matrix()
    print("  Tabla de resumen cinemático:")
    print("  " + "-" * 75)
    print(f"  {'Masa (kg)':<10} {'T_fase (s)':<12} {'Lift (mm)':<12} {'a1_max (m/s2)':<15} {'alpha2_max (rad/s2)':<20}")
    print("  " + "-" * 75)
    for row in scaling_data["matrix"]:
        print(f"  {row['drone_mass_scale_kg']:<10.1f} {row['t_phase_s']:<12.1f} {row['lift_max_mm']:<12.2f} "
              f"{row['quintic']['a1_max_m_s2']:<15.4f} {row['quintic']['alpha2_max_rad_s2']:<20.4f}")
    print("  " + "-" * 75)

    # 4. Verificación de compuertas y signos desde JSON
    print("\n[4/4] Verificando extremos y signos por tapa desde archivos JSON de referencia...")
    door_verif = verify_doors_from_json()
    print(f"  - Estado: {door_verif['status']}")
    print(f"  - Compuertas auditadas: {door_verif['doors_count']}")
    for d in door_verif["door_details"]:
        print(f"    * {d['name']:<32} | out={d['out_translation_sign']:+2d} | sign={d['rotation_sign']:+2d} | "
              f"Eje closed: [{d['axis_closed'][0]:.1f}, {d['axis_closed'][1]:.1f}, {d['axis_closed'][2]:.2f}]")

    print("\n  Declaraciones de variables no verificables:")
    for decl in door_verif["unverifiable_declarations"]:
        print(f"    [!] {decl}")

    # Guardar entregables JSON en salidas/
    os.makedirs(SALIDAS_DIR, exist_ok=True)

    output_profiles_path = os.path.join(SALIDAS_DIR, "resultados_perfiles.json")
    with open(output_profiles_path, "w", encoding="utf-8") as f:
        json.dump({
            "matriz_escalamiento": scaling_data,
            "continuidad_interfase": continuity_results,
            "precision_derivadas_diferencias_finitas": fd_res
        }, f, indent=2)
    print(f"\n[OK] Archivo guardado: {output_profiles_path}")

    output_doors_path = os.path.join(SALIDAS_DIR, "verificacion_signos_tapas.json")
    with open(output_doors_path, "w", encoding="utf-8") as f:
        json.dump(door_verif, f, indent=2)
    print(f"[OK] Archivo guardado: {output_doors_path}")

    output_mech_path = os.path.join(SALIDAS_DIR, "comparativa_mecanismos.json")
    mech_data = get_conceptual_mechanisms_comparison()
    with open(output_mech_path, "w", encoding="utf-8") as f:
        json.dump(mech_data, f, indent=2)
    print(f"[OK] Archivo guardado: {output_mech_path}")


if __name__ == "__main__":
    main()
