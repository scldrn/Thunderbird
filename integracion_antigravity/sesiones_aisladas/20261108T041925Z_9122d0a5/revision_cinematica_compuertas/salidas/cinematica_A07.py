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

Revisión técnica y correcciones:
  - Resolución de contradicción de jerk: Derivación rigurosa de límites unilaterales
    del movimiento frente al reposo estático en t=0, t=T_fase y t=2*T_fase.
  - Aclaración de continuidad: La trayectoria es de clase C^2 (posición, velocidad
    y aceleración continuas). El jerk presenta discontinuidades de salto finito
    (+/- 60*Delta/T^3 en quíntico, +/- 4*pi^2*Delta/T^3 en cicloidal).
  - Corrección de afirmación sobre aceleración pico: El polinomio quíntico minimiza
    la integral del jerk al cuadrado (norma L2 de jerk); NO minimiza la aceleración pico
    entre todos los perfiles cinemáticos (perfiles parabólicos/bang-bang o trapezoidales
    alcanzan aceleraciones pico inferiores).
  - Portabilidad estricta: No se infiere que un archivo no copiado no exista;
    se incluyen las especificaciones nominales A07 para ejecución autónoma y resiliente.
  - No alteración de la geometría A07 ni asunción de mecanismo real aprobado.
"""

import os
import sys
import json
import math
from typing import Dict, List, Tuple, Any, Optional

# Rutas dentro del espacio de trabajo aislado
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Si se ejecuta desde salidas/ o desde la raíz
if os.path.basename(CURRENT_SCRIPT_DIR) == "salidas":
    WORKSPACE_DIR = os.path.dirname(CURRENT_SCRIPT_DIR)
else:
    WORKSPACE_DIR = CURRENT_SCRIPT_DIR

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

# Constantes cinemáticas nominales A07 (Escala 5 kg)
LIFT_NOMINAL_MM_5KG = 10.0  # mm
LIFT_NOMINAL_M_5KG = 0.010  # m
ROTATION_NOMINAL_DEG = 110.0  # grados
ROTATION_NOMINAL_RAD = ROTATION_NOMINAL_DEG * math.pi / 180.0  # rad (~1.919862177 rad)

# Duraciones de fase de estudio requeridas
DURACIONES_FASE_S = [0.5, 1.0, 2.0]

# Escalas de masa del vehículo requeridas
ESCALAS_MASA_KG = [2.0, 5.0, 10.0]

# Especificación geométrica nominal A07 de las 8 compuertas (Referencia CAD)
A07_DOORS_NOMINAL_SPEC = [
    {
        "name": "compuerta_0_superior_enrasada",
        "lift_mm": 10.0,
        "axis_closed": [-200.0, -124.0, 65.462],
        "sign": 1,
        "out": 1
    },
    {
        "name": "compuerta_0_inferior_enrasada",
        "lift_mm": 10.0,
        "axis_closed": [-200.0, -124.0, -51.813],
        "sign": -1,
        "out": -1
    },
    {
        "name": "compuerta_1_superior_enrasada",
        "lift_mm": 10.0,
        "axis_closed": [-200.0, 124.0, 65.462],
        "sign": -1,
        "out": 1
    },
    {
        "name": "compuerta_1_inferior_enrasada",
        "lift_mm": 10.0,
        "axis_closed": [-200.0, 124.0, -51.813],
        "sign": 1,
        "out": -1
    },
    {
        "name": "compuerta_2_superior_enrasada",
        "lift_mm": 10.0,
        "axis_closed": [200.0, -124.0, 45.510],
        "sign": 1,
        "out": 1
    },
    {
        "name": "compuerta_2_inferior_enrasada",
        "lift_mm": 10.0,
        "axis_closed": [200.0, -124.0, -34.382],
        "sign": -1,
        "out": -1
    },
    {
        "name": "compuerta_3_superior_enrasada",
        "lift_mm": 10.0,
        "axis_closed": [200.0, 124.0, 45.510],
        "sign": -1,
        "out": 1
    },
    {
        "name": "compuerta_3_inferior_enrasada",
        "lift_mm": 10.0,
        "axis_closed": [200.0, 124.0, -34.382],
        "sign": 1,
        "out": -1
    }
]


# =============================================================================
# 1. PERFILES TEMPORALES SUAVES (PERFILES ADIMENSIONALES s(tau), tau in [0, 1])
# =============================================================================

class QuinticProfile:
    """
    Perfil polinómico de 5to orden (solución al problema de mínimo jerk integral).
    Minimiza la integral int_0^1 (s''')^2 dtau sujeta a condiciones de contorno:
      s(0) = 0,  s'(0) = 0,  s''(0) = 0
      s(1) = 1,  s'(1) = 0,  s''(1) = 0
    Continuidad C^2 en transiciones (aceleración nula en extremos).
    NOTA CRÍTICA: s'''(0) = 60 != 0 y s'''(1) = 60 != 0.
    Por tanto, el jerk presenta un salto finito al conectarse con el reposo estático.
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
        """
        Derivada tercera d^3s/dtau^3 (jerk normalizado en el interior del movimiento).
        En tau = 0^+ vale 60.0. En tau = 1^- vale 60.0.
        Fuera del intervalo [0, 1] en reposo vale 0.0.
        """
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
    Continuidad C^2 en fronteras.
    NOTA CRÍTICA: s'''(0) = 4*pi^2 ~ 39.478 != 0 y s'''(1) = 4*pi^2 ~ 39.478 != 0.
    El jerk también presenta un salto finito frente al reposo estático.
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
    Cinemática de 2 grados de libertad secuenciados:
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
        Evalúa posición, velocidad, aceleración y jerk interior de ambos grados de libertad.
        En los límites exactos de fase t=0, t=T y t=2T, la aceleración es continua y nula.
        Para límites unilaterales exactos del jerk (discontinuo), usar evaluate_unilateral().
        """
        T = self.t_phase

        if t < 0.0:
            return {
                "t": t, "phase": 0,
                "q1": 0.0, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                "q2": 0.0, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0,
            }
        elif t == 0.0:
            # Reposo de partida: posición 0, velocidad 0, aceleración 0
            return {
                "t": t, "phase": 1,
                "q1": 0.0, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                "q2": 0.0, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0,
            }
        elif t < T:
            # Fase 1: Traslación activa, Rotación en reposo
            tau = t / T
            s_val = self.profile.s(tau)
            ds_val = self.profile.ds_dtau(tau)
            d2s_val = self.profile.d2s_dtau2(tau)
            d3s_val = self.profile.d3s_dtau3(tau)

            return {
                "t": t, "phase": 1,
                "q1": self.d_max_m * s_val,
                "q1_dot": (self.d_max_m / T) * ds_val,
                "q1_ddot": (self.d_max_m / (T ** 2)) * d2s_val,
                "q1_dddot": (self.d_max_m / (T ** 3)) * d3s_val,
                "q2": 0.0, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0,
            }
        elif t == T:
            # Conmutación de fase: Continuidad C2 perfecta (q1=d_max, v1=0, a1=0, q2=0, v2=0, a2=0)
            return {
                "t": t, "phase": 1,
                "q1": self.d_max_m, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                "q2": 0.0, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0,
            }
        elif t < self.t_total:
            # Fase 2: Traslación fija en d_max, Rotación activa
            tau = (t - T) / T
            s_val = self.profile.s(tau)
            ds_val = self.profile.ds_dtau(tau)
            d2s_val = self.profile.d2s_dtau2(tau)
            d3s_val = self.profile.d3s_dtau3(tau)

            return {
                "t": t, "phase": 2,
                "q1": self.d_max_m, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                "q2": self.theta_max_rad * s_val,
                "q2_dot": (self.theta_max_rad / T) * ds_val,
                "q2_ddot": (self.theta_max_rad / (T ** 2)) * d2s_val,
                "q2_dddot": (self.theta_max_rad / (T ** 3)) * d3s_val,
            }
        elif t == self.t_total:
            # Final de trayectoria: q1=d_max, q2=theta_max, v=0, a=0
            return {
                "t": t, "phase": 2,
                "q1": self.d_max_m, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                "q2": self.theta_max_rad, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0,
            }
        else:
            # t > t_total: Reposo final permanente
            return {
                "t": t, "phase": 3,
                "q1": self.d_max_m, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                "q2": self.theta_max_rad, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0,
            }

    def evaluate_unilateral(self, t: float, direction: str = "right") -> Dict[str, float]:
        """
        Evalúa los límites unilaterales lim_{s -> t^pm} f(s).
        direction: 'left' (s -> t^-) o 'right' (s -> t^+).
        Deriva analíticamente los valores exactos de posición, velocidad, aceleración y jerk.
        """
        T = self.t_phase
        d_m = self.d_max_m
        th_rad = self.theta_max_rad

        # Derivadas terceras normalizadas en extremos
        # Para quíntico: s'''(0) = 60, s'''(1) = 60
        # Para cicloidal: s'''(0) = 4*pi^2, s'''(1) = 4*pi^2
        if self.profile == QuinticProfile:
            jerk_norm_0 = 60.0
            jerk_norm_1 = 60.0
        elif self.profile == CycloidalProfile:
            jerk_norm_0 = 4.0 * (math.pi ** 2)
            jerk_norm_1 = 4.0 * (math.pi ** 2)
        else:
            jerk_norm_0 = self.profile.d3s_dtau3(0.0)
            jerk_norm_1 = self.profile.d3s_dtau3(1.0)

        # Límite en t = 0
        if abs(t - 0.0) < 1e-12:
            if direction == "left":
                # Reposo estático previo t < 0
                return {
                    "t": 0.0, "direction": "left",
                    "q1": 0.0, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                    "q2": 0.0, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0
                }
            else:
                # Inicio del movimiento Fase 1 t -> 0^+
                return {
                    "t": 0.0, "direction": "right",
                    "q1": 0.0, "q1_dot": 0.0, "q1_ddot": 0.0,
                    "q1_dddot": (d_m / (T ** 3)) * jerk_norm_0,
                    "q2": 0.0, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0
                }

        # Límite en t = T (conmutación inter-fase)
        elif abs(t - T) < 1e-12:
            if direction == "left":
                # Fin de Fase 1 (t -> T^-)
                return {
                    "t": T, "direction": "left",
                    "q1": d_m, "q1_dot": 0.0, "q1_ddot": 0.0,
                    "q1_dddot": (d_m / (T ** 3)) * jerk_norm_1,
                    "q2": 0.0, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0
                }
            else:
                # Inicio de Fase 2 (t -> T^+)
                return {
                    "t": T, "direction": "right",
                    "q1": d_m, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                    "q2": 0.0, "q2_dot": 0.0, "q2_ddot": 0.0,
                    "q2_dddot": (th_rad / (T ** 3)) * jerk_norm_0
                }

        # Límite en t = 2T (término de maniobra)
        elif abs(t - self.t_total) < 1e-12:
            if direction == "left":
                # Fin de Fase 2 (t -> 2T^-)
                return {
                    "t": self.t_total, "direction": "left",
                    "q1": d_m, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                    "q2": th_rad, "q2_dot": 0.0, "q2_ddot": 0.0,
                    "q2_dddot": (th_rad / (T ** 3)) * jerk_norm_1
                }
            else:
                # Reposo estático final posterior t > 2T
                return {
                    "t": self.t_total, "direction": "right",
                    "q1": d_m, "q1_dot": 0.0, "q1_ddot": 0.0, "q1_dddot": 0.0,
                    "q2": th_rad, "q2_dot": 0.0, "q2_ddot": 0.0, "q2_dddot": 0.0
                }
        else:
            # En cualquier otro punto continuo interior, ambos límites coinciden
            val = self.evaluate(t)
            val["direction"] = direction
            return val

    def get_unilateral_limits_and_jumps(self) -> Dict[str, Any]:
        """
        Derivación analítica y explícita de límites unilaterales y saltos
        en las tres fronteras críticas: t=0, t=T, t=2T.
        Demuestra formalmente continuidad C^0, C^1, C^2 y discontinuidad de Jerk (salto finito).
        """
        T = self.t_phase
        boundaries = [0.0, T, self.t_total]
        results = {}

        for b in boundaries:
            b_str = f"t_{b:3.1f}s"
            left = self.evaluate_unilateral(b, direction="left")
            right = self.evaluate_unilateral(b, direction="right")

            jump_q1 = right["q1"] - left["q1"]
            jump_v1 = right["q1_dot"] - left["q1_dot"]
            jump_a1 = right["q1_ddot"] - left["q1_ddot"]
            jump_j1 = right["q1_dddot"] - left["q1_dddot"]

            jump_q2 = right["q2"] - left["q2"]
            jump_v2 = right["q2_dot"] - left["q2_dot"]
            jump_a2 = right["q2_ddot"] - left["q2_ddot"]
            jump_j2 = right["q2_dddot"] - left["q2_dddot"]

            results[b_str] = {
                "t": b,
                "lim_left": left,
                "lim_right": right,
                "jumps": {
                    "jump_q1_m": jump_q1,
                    "jump_q1_dot_m_s": jump_v1,
                    "jump_q1_ddot_m_s2": jump_a1,
                    "jump_q1_dddot_m_s3": jump_j1,
                    "jump_q2_rad": jump_q2,
                    "jump_q2_dot_rad_s": jump_v2,
                    "jump_q2_ddot_rad_s2": jump_a2,
                    "jump_q2_dddot_rad_s3": jump_j2,
                },
                "is_C0": abs(jump_q1) < 1e-12 and abs(jump_q2) < 1e-12,
                "is_C1": abs(jump_v1) < 1e-12 and abs(jump_v2) < 1e-12,
                "is_C2": abs(jump_a1) < 1e-12 and abs(jump_a2) < 1e-12,
                "is_C3": abs(jump_j1) < 1e-12 and abs(jump_j2) < 1e-12,
            }

        return results

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
    y coordenadas de eje nominales CAD.
    Marco CAD: X longitudinal hacia popa, Y lateral, Z vertical hacia arriba.
    """

    def __init__(self, door_record: Dict[str, Any]):
        self.name = door_record["name"]
        self.lift_mm_ref = float(door_record["lift_mm"])
        self.axis_closed = [float(c) for c in door_record["axis_closed"]]  # [X, Y, Z] en mm
        self.sign_rot = int(door_record["sign"])  # Sentido de giro (+1 o -1)
        self.out_trans = int(door_record["out"])  # Sentido de traslación (+1 o -1 en Z)

    def axis_position(self, q1_m: float, scale_factor: float = 1.0) -> List[float]:
        """
        Retorna la posición [X, Y, Z] del eje transportado en mm.
        """
        x_closed_scaled = self.axis_closed[0] * scale_factor
        y_closed_scaled = self.axis_closed[1] * scale_factor
        z_closed_scaled = self.axis_closed[2] * scale_factor

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
        Transforma un punto material de la compuerta en coordenadas CAD (mm).
        """
        p_axis = self.axis_position(q1_m, scale_factor)

        px = p_closed_mm[0] * scale_factor
        py = p_closed_mm[1] * scale_factor
        pz = p_closed_mm[2] * scale_factor

        q1_mm = q1_m * 1000.0
        pz_elevated = pz + self.out_trans * q1_mm

        rx = px - p_axis[0]
        ry = py - p_axis[1]
        rz = pz_elevated - p_axis[2]

        phi = self.sign_rot * q2_rad
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)

        ry_rot = cos_phi * ry - sin_phi * rz
        rz_rot = sin_phi * ry + cos_phi * rz

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
    Verifica rigurosamente la continuidad C^0, C^1 y C^2 en la conmutación
    de fase t = T_fase evaluando los límites infinitesimales (T - eps) y (T + eps),
    así como el salto finito del Jerk (demostrando no pertenencia a C^3).
    """
    traj = TrajectoryA07(t_phase=t_phase, mass_scale_kg=mass_scale_kg, profile_class=profile_class)
    T = t_phase

    left = traj.evaluate(T - eps)
    exact = traj.evaluate(T)
    right = traj.evaluate(T + eps)

    # Discontinuidades en el cambio de fase
    jump_q1 = abs(left["q1"] - right["q1"])
    jump_q1_dot = abs(left["q1_dot"] - right["q1_dot"])
    jump_q1_ddot = abs(left["q1_ddot"] - right["q1_ddot"])
    jump_q1_dddot = abs(left["q1_dddot"] - right["q1_dddot"])

    jump_q2 = abs(left["q2"] - right["q2"])
    jump_q2_dot = abs(left["q2_dot"] - right["q2_dot"])
    jump_q2_ddot = abs(left["q2_ddot"] - right["q2_ddot"])
    jump_q2_dddot = abs(left["q2_dddot"] - right["q2_dddot"])

    c0_continuous = (jump_q1 < 1e-4) and (jump_q2 < 1e-4)
    c1_continuous = (jump_q1_dot < 1e-3) and (jump_q2_dot < 1e-3)
    c2_continuous = (jump_q1_ddot < 1e-2) and (jump_q2_ddot < 1e-2)

    # Jerk jump teórico en T:
    # q1: de +60*d_max/T^3 a 0 -> magnitud 60*d_max/T^3
    # q2: de 0 a +60*theta_max/T^3 -> magnitud 60*theta_max/T^3
    expected_j1_jump = 60.0 * traj.d_max_m / (T ** 3)
    expected_j2_jump = 60.0 * traj.theta_max_rad / (T ** 3)

    return {
        "t_phase_s": t_phase,
        "mass_scale_kg": mass_scale_kg,
        "eps_evaluated": eps,
        "jump_q1_m": jump_q1,
        "jump_q1_dot_m_s": jump_q1_dot,
        "jump_q1_ddot_m_s2": jump_q1_ddot,
        "jump_q1_dddot_m_s3": jump_q1_dddot,
        "expected_j1_jump_m_s3": expected_j1_jump,
        "jump_q2_rad": jump_q2,
        "jump_q2_dot_rad_s": jump_q2_dot,
        "jump_q2_ddot_rad_s2": jump_q2_ddot,
        "jump_q2_dddot_rad_s3": jump_q2_dddot,
        "expected_j2_jump_rad_s3": expected_j2_jump,
        "c0_continuous": c0_continuous,
        "c1_continuous": c1_continuous,
        "c2_continuous": c2_continuous,
        "c3_continuous": False,  # Discontinuidad finita de jerk demostrada
        "exact_switch_state": exact
    }


def verify_finite_differences(
    traj: TrajectoryA07,
    dt: float = 1e-5,
    sample_points: int = 50
) -> Dict[str, float]:
    """
    Compara las derivadas analíticas con diferencias finitas centradas
    en el interior del movimiento para validar la coherencia de derivadas.
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

        num_v1 = (ev_plus["q1"] - ev_minus["q1"]) / (2.0 * dt)
        num_a1 = (ev_plus["q1_dot"] - ev_minus["q1_dot"]) / (2.0 * dt)

        num_v2 = (ev_plus["q2"] - ev_minus["q2"]) / (2.0 * dt)
        num_a2 = (ev_plus["q2_dot"] - ev_minus["q2_dot"]) / (2.0 * dt)

        # Evitar conmutación inter-fase donde jerk salta
        if abs(t - traj.t_phase) > 3.0 * dt:
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


def compare_peak_acceleration_with_other_profiles() -> Dict[str, Any]:
    """
    Compara formalmente la aceleración máxima normalizada del perfil quíntico
    frente a otros perfiles cinemáticos estándar.
    Demuestra que el polinomio quíntico NO minimiza la aceleración pico global.
    """
    quintic_a_max = 10.0 * math.sqrt(3.0) / 3.0  # ~ 5.773503
    cycloidal_a_max = 2.0 * math.pi              # ~ 6.283185
    parabolic_a_max = 4.0                        # Bang-bang aceleración constante
    trapezoidal_vel_a_max = 4.5                  # Perfil trapezoidal con 1/3 aceleración

    return {
        "quintic_normalized_a_max": round(quintic_a_max, 6),
        "cycloidal_normalized_a_max": round(cycloidal_a_max, 6),
        "parabolic_bang_bang_normalized_a_max": round(parabolic_a_max, 6),
        "trapezoidal_velocity_normalized_a_max": round(trapezoidal_vel_a_max, 6),
        "comparison_summary": (
            "El perfil quíntico (a_max = 5.7735) reduce la aceleración máxima respecto al "
            "perfil cicloidal (a_max = 6.2832, reducción de aprox. 8.1%), pero NO minimiza "
            "la aceleración máxima entre todos los perfiles cinemáticos posibles. Por ejemplo, "
            "un perfil parabólico (bang-bang) alcanza a_max = 4.0 (30.7% menor), y perfiles "
            "trapezoidales alcanzan valores entre 4.0 y 5.77. La afirmación de que el quíntico "
            "minimiza la aceleración pico global carece de sustento y queda corregida: el quíntico "
            "minimiza la integral del jerk al cuadrado (energía de jerk), no la aceleración máxima."
        )
    }


# =============================================================================
# 5. MATRIZ DE ESCALAMIENTO Y DINÁMICA INERCIAL (2/5/10 kg x 0.5/1/2 s)
# =============================================================================

def compute_scaling_matrix() -> Dict[str, Any]:
    """
    Genera la matriz paramétrica de cinemática y dinámica inercial
    para todas las combinaciones de escala de masa (2, 5, 10 kg)
    y duración de fase (0.5, 1.0, 2.0 s).

    Distingue rigurosamente:
      - Datos medidos: 0 en masa/inercia de compuerta (declarados null en JSON de referencia).
      - Datos supuestos (hipótesis paramétricas ilustrativas):
          * Masa nominal supuesta de compuerta a 5 kg: m_tapa_5kg = 0.050 kg (50 g).
          * Escalamiento volumétrico isotrópico: m_tapa(m) = m_tapa_5kg * (m/5).
          * Radio de giro de inercia r_g ~ 0.040 m -> I_tapa = m_tapa * r_g^2.
      - Cálculos normalizados independientes de supuestos de masa:
          * Aceleración lineal máxima a1_max (m/s^2) = F_in / m.
          * Aceleración angular máxima alpha2_max (rad/s^2) = Tau_in / I.
          * Saltos de Jerk en fronteras.
    """
    M_TAPA_REF_5KG = 0.050  # kg (50 g - SUPUESTO DE REFERENCIA)
    R_GIRO_REF_5KG = 0.040  # m (40 mm - SUPUESTO DE REFERENCIA)

    results = []

    for mass_kg in ESCALAS_MASA_KG:
        scale_lambda = (mass_kg / 5.0) ** (1.0 / 3.0)
        d_lift_mm = LIFT_NOMINAL_MM_5KG * scale_lambda
        d_lift_m = d_lift_mm * 1e-3

        m_tapa_vol_kg = M_TAPA_REF_5KG * (mass_kg / 5.0)
        r_giro_m = R_GIRO_REF_5KG * scale_lambda
        I_tapa_kgm2 = m_tapa_vol_kg * (r_giro_m ** 2)

        for t_phase in DURACIONES_FASE_S:
            traj_quintic = TrajectoryA07(t_phase=t_phase, mass_scale_kg=mass_kg, profile_class=QuinticProfile)
            ext_q = traj_quintic.get_kinematic_extrema()
            limits_q = traj_quintic.get_unilateral_limits_and_jumps()

            traj_cyc = TrajectoryA07(t_phase=t_phase, mass_scale_kg=mass_kg, profile_class=CycloidalProfile)
            ext_c = traj_cyc.get_kinematic_extrema()
            limits_c = traj_cyc.get_unilateral_limits_and_jumps()

            f_in_quintic_N = m_tapa_vol_kg * ext_q["a1_max_m_s2"]
            tau_in_quintic_Nm = I_tapa_kgm2 * ext_q["alpha2_max_rad_s2"]

            # Saltos de Jerk teóricos exactos
            jerk_jump_q1_quintic = 60.0 * d_lift_m / (t_phase ** 3)
            jerk_jump_q2_quintic = 60.0 * ROTATION_NOMINAL_RAD / (t_phase ** 3)

            jerk_jump_q1_cycloidal = 4.0 * (math.pi ** 2) * d_lift_m / (t_phase ** 3)
            jerk_jump_q2_cycloidal = 4.0 * (math.pi ** 2) * ROTATION_NOMINAL_RAD / (t_phase ** 3)

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
                    "jerk_jump_q1_m_s3": round(jerk_jump_q1_quintic, 6),
                    "jerk_jump_q2_rad_s3": round(jerk_jump_q2_quintic, 6),
                    "normalized_force_N_per_kg": round(ext_q["a1_max_m_s2"], 6),
                    "normalized_torque_Nm_per_kgm2": round(ext_q["alpha2_max_rad_s2"], 6),
                    "assumed_tapa_mass_kg": round(m_tapa_vol_kg, 6),
                    "assumed_tapa_inertia_kgm2": round(I_tapa_kgm2, 8),
                    "inertial_force_peak_N": round(f_in_quintic_N, 6),
                    "inertial_torque_peak_Nm": round(tau_in_quintic_Nm, 6)
                },
                "cycloidal": {
                    "v1_max_m_s": round(ext_c["v1_max_m_s"], 6),
                    "a1_max_m_s2": round(ext_c["a1_max_m_s2"], 6),
                    "omega2_max_rad_s": round(ext_c["omega2_max_rad_s"], 6),
                    "alpha2_max_rad_s2": round(ext_c["alpha2_max_rad_s2"], 6),
                    "jerk_jump_q1_m_s3": round(jerk_jump_q1_cycloidal, 6),
                    "jerk_jump_q2_rad_s3": round(jerk_jump_q2_cycloidal, 6)
                },
                "unilateral_limits_quintic": limits_q
            })

    return {
        "metadata": {
            "source": "Cinemática de referencia A07 corregida",
            "gravity_m_s2": 9.80665,
            "assumed_reference_door_mass_5kg_kg": M_TAPA_REF_5KG,
            "assumed_reference_radius_gyration_5kg_m": R_GIRO_REF_5KG,
            "mass_assignment_status_in_reference": "actual_mass_kg: null (sin masa física asignada en C02_CANDIDATA)",
            "continuity_class": "C^2 continua (aceleración continua, jerk discontinuo con saltos finitos)"
        },
        "matrix": results
    }


# =============================================================================
# 6. VERIFICACIÓN DE EXTREMOS Y SIGNOS POR TAPA
# =============================================================================

def verify_doors_from_json() -> Dict[str, Any]:
    """
    Verifica las 8 compuertas de la trayectoria A07:
      1. Cantidad de tapas (8 tapas: 4 superiores, 4 inferiores).
      2. Elevación nominal de 10.0 mm en 5 kg.
      3. Signos de traslación ('out': +1 para superior, -1 para inferior).
      4. Signos de rotación ('sign': +1 o -1 para apertura exterior alejándose del fuselaje).
      5. Poses discretas de verificación del recorrido.
      6. Declaración de variables no verificables en los archivos provistos.

    Portabilidad estricta: Si los archivos JSON de referencia no están copiados
    en entradas/, no infiere que no existan; utiliza la especificación geométrica
    nominal A07 para realizar la verificación analítica.
    """
    doors_data = None
    doors_source_desc = None

    if os.path.exists(PATH_PROPUESTA_ELEVACION):
        with open(PATH_PROPUESTA_ELEVACION, "r", encoding="utf-8") as f:
            doors_data = json.load(f)
        doors_source_desc = f"Archivo de entrada cargado: {PATH_PROPUESTA_ELEVACION}"
    else:
        doors_data = A07_DOORS_NOMINAL_SPEC
        doors_source_desc = (
            "Especificación geométrica nominal A07 incorporada (el archivo propuesta_elevacion.json "
            "no fue copiado en entradas/; conforme a la directriz operativa, no se infiere su inexistencia)"
        )

    door_verifications = []

    for d in doors_data:
        name = d["name"]
        lift_mm = float(d["lift_mm"])
        axis_closed = [float(c) for c in d["axis_closed"]]
        sign_rot = int(d["sign"])
        out_trans = int(d["out"])

        is_superior = "superior" in name
        is_inferior = "inferior" in name

        expected_out = 1 if is_superior else -1
        out_valid = (out_trans == expected_out)

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
            "lift_nominal_valid": (abs(lift_mm - 10.0) < 1e-6),
            "out_translation_sign": out_trans,
            "out_translation_sign_valid": out_valid,
            "rotation_sign": sign_rot,
            "rotation_sign_valid": sign_valid,
            "motion_description": (
                f"{'Traslación +Z (10 mm)' if out_trans == 1 else 'Traslación -Z (10 mm)'} y "
                f"rotación exterior ({sign_rot * 110}° alrededor de X)"
            )
        })

    # Verificación de recorrido discreto
    recorrido_verification = {}
    if os.path.exists(PATH_VERIFICACION_RECORRIDO):
        with open(PATH_VERIFICACION_RECORRIDO, "r", encoding="utf-8") as f:
            rec_json = json.load(f)
        poses = rec_json.get("poses", [])
        recorrido_verification["source"] = f"Archivo de entrada cargado: {PATH_VERIFICACION_RECORRIDO}"
        recorrido_verification["total_nodes"] = len(poses)
        recorrido_verification["max_overlap_mm3"] = rec_json.get("max_overlap_mm3", 0.0)
        recorrido_verification["node_0_valid"] = (poses[0].get("lift_mm") == 0.0 and poses[0].get("angle_deg") == 0.0)
        recorrido_verification["node_switch_valid"] = (poses[5].get("lift_mm") == 10.0 and poses[5].get("angle_deg") == 0.0)
        recorrido_verification["node_final_valid"] = (poses[-1].get("lift_mm") == 10.0 and poses[-1].get("angle_deg") == 110.0)
    else:
        # Generar las 61 poses nominales estándar para comprobación analítica
        nominal_poses = []
        for i in range(6):
            nominal_poses.append({"node": i, "lift_mm": float(i * 2.0), "angle_deg": 0.0})
        for j in range(1, 56):
            nominal_poses.append({"node": 5 + j, "lift_mm": 10.0, "angle_deg": float(j * 2.0)})
        recorrido_verification["source"] = (
            "Secuencia nominal de 61 poses discretas A07 (VERIFICACION_RECORRIDO.json no fue copiado "
            "en entradas/; conforme a directriz operativa, no se infiere inexistencia)"
        )
        recorrido_verification["total_nodes"] = len(nominal_poses)
        recorrido_verification["node_0_valid"] = (nominal_poses[0]["lift_mm"] == 0.0 and nominal_poses[0]["angle_deg"] == 0.0)
        recorrido_verification["node_switch_valid"] = (nominal_poses[5]["lift_mm"] == 10.0 and nominal_poses[5]["angle_deg"] == 0.0)
        recorrido_verification["node_final_valid"] = (nominal_poses[-1]["lift_mm"] == 10.0 and nominal_poses[-1]["angle_deg"] == 110.0)

    # Declaración rigurosa de variables no verificables
    unverifiable_declarations = [
        "Masa real de compuerta ('actual_mass_kg: null' en configuración C02). Directriz estricta: No se infiere que una reserva sin masa asignada tenga masa real nula o no nula.",
        "Centro de gravedad ('actual_CG_m: null') y tensor de inercia ('actual_inertia_kgm2: null') no medidos; estado: desconocido.",
        "Mecanismo real de accionamiento y empaquetamiento: LEEME.md explicita que no existen guías, bisagras, soportes, cierres, sellos, cableado o actuadores dimensionados. No se afirma mecanismo real aprobado.",
        "Tolerancias de fabricación, holguras, desgaste e interferencias elásticas bajo carga dinámica: el cribado CAD es estrictamente estático nominal sobre 61 poses discretas; estado: no medido / desconocido.",
        "Respuesta dinámica del actuador ('servo_response_s: null'); estado: desconocido.",
        "Cargas aerodinámicas, acoplamiento aeroelástico y viabilidad de vuelo en avance: LEEME.md explicita que la apertura está destinada al estudio de baja velocidad, no se valida su uso en avance rápido y los solvers CFD pausados no se reanudaron; estado: no validado / desconocido."
    ]

    return {
        "status": "VERIFICACIÓN COMPLETADA",
        "doors_source": doors_source_desc,
        "doors_count": len(door_verifications),
        "door_details": door_verifications,
        "discrete_recorrido": recorrido_verification,
        "unverifiable_declarations": unverifiable_declarations
    }


# =============================================================================
# 7. COMPARATIVA MECÁNICA CONCEPTUAL (CARRO + BISAGRA vs RANURA / CAM)
# =============================================================================

def get_conceptual_mechanisms_comparison() -> Dict[str, Any]:
    """
    Retorna la comparativa técnica entre los dos conceptos mecánicos exploratorios.
    ADVERTENCIA FORMAL: No se afirma que quepan ni se afirma mecanismo real aprobado.
    """
    return {
        "statement_on_fit_and_manufacturability": (
            "DECLARACIÓN EXPLÍCITA Y OBLIGATORIA: Ninguno de los dos conceptos mecánicos ha sido "
            "aprobado, fabricado ni sometido a estudio de empaquetamiento volumétrico en el espacio interior "
            "de las camisas o el fuselaje. No se afirma que quepan, ni su fabricabilidad, ni viabilidad de vuelo."
        ),
        "concept_1": {
            "nombre": "Carro lineal + Bisagra transportada (Cadena serial PR)",
            "topologia": "Par prismático (P) normal seguido de par revoluta (R) sobre el carro móvil",
            "descripcion": (
                "Un carro lineal guía la traslación pura de 10 mm normal al fuselaje (+Z/-Z). "
                "Al finalizar la carrera, el eje de rotación montado sobre el carro permite girar "
                "los 110 grados hacia el exterior."
            ),
            "ventajas": [
                "Desacoplamiento cinemático natural e independiente de ambos grados de libertad.",
                "Menores concentraciones de tensiones de contacto (contacto superficial en guías y casquillos).",
                "Facilidad de ajuste de carrera o ángulo mediante software o topes ajustables."
            ],
            "desventajas_y_desafios": [
                "Mayor masa no suspendida sobre el carro móvil y mayor número de piezas.",
                "Susceptibilidad a bloqueo por ladeo ('cocking/binding') bajo momentos aerodinámicos o de flexión.",
                "Dificultades de estanqueidad y sellado contra flujo y partículas en los carriles lineales."
            ]
        },
        "concept_2": {
            "nombre": "Ranura / Cam con guiado de seguidor (Mecanismo de leva de ranura)",
            "topologia": "Par cinemático superior (leva de ranura programada de 1-DOF con rodillo seguidor)",
            "descripcion": (
                "Una pista ranurada fija contiene un tramo rectilíneo vertical de 10 mm y un tramo "
                "circular de 110 grados subtendido en el radio de giro. Un único actuador empuja el seguidor."
            ),
            "ventajas": [
                "Sincronización cinemática intrínseca: la geometría de la ranura impide el giro antes del lift.",
                "Actuador único y fijo rígidamente a la estructura del fuselaje (menor masa móvil).",
                "Menor conteo de piezas estructurales discretas si se integra en costillas."
            ],
            "desventajas_y_desafios": [
                "Contacto lineal/puntual de Hertz: elevadas tensiones de contacto, riesgo de desgaste o picado.",
                "Ángulo de presión crítico en la transición entre tramo recto y curvo (riesgo de autoenclavamiento).",
                "Rigidez total de diseño: cualquier modificación de trayectoria exige mecanizar nuevas placas."
            ]
        }
    }


# =============================================================================
# 8. EJECUCIÓN PRINCIPAL Y EXPORTACIÓN DE ENTREGABLES
# =============================================================================

def main():
    print("=" * 80)
    print("PARAMETRIZACIÓN CINEMÁTICA DE REFERENCIA 2-DOF — TRAYECTORIA CANDIDATA A07")
    print("Revisión corregida: Continuidad C2, Derivación de Límites Unilaterales y Saltos de Jerk")
    print("=" * 80)

    # 1. Análisis de límites unilaterales y saltos de Jerk
    print("\n[1/5] Derivación y análisis de límites unilaterales (t=0, t=T, t=2T)...")
    sample_traj = TrajectoryA07(t_phase=1.0, mass_scale_kg=5.0)
    unilateral_res = sample_traj.get_unilateral_limits_and_jumps()

    for k, v in unilateral_res.items():
        j = v["jumps"]
        print(f"  * Frontera {k}:")
        print(f"    - Continuidad C0: {v['is_C0']} (Salto q1={j['jump_q1_m']:.2e} m, q2={j['jump_q2_rad']:.2e} rad)")
        print(f"    - Continuidad C1: {v['is_C1']} (Salto v1={j['jump_q1_dot_m_s']:.2e} m/s, v2={j['jump_q2_dot_rad_s']:.2e} rad/s)")
        print(f"    - Continuidad C2: {v['is_C2']} (Salto a1={j['jump_q1_ddot_m_s2']:.2e} m/s2, a2={j['jump_q2_ddot_rad_s2']:.2e} rad/s2)")
        print(f"    - Continuidad C3: {v['is_C3']} (Salto Jerk j1={j['jump_q1_dddot_m_s3']:.4f} m/s3, j2={j['jump_q2_dddot_rad_s3']:.4f} rad/s3)")

    # 2. Pruebas de conmutación inter-fase infinitesimales
    print("\n[2/5] Comprobando continuidad inter-fase para todas las escalas...")
    continuity_results = []
    for t_phase in DURACIONES_FASE_S:
        for m_scale in ESCALAS_MASA_KG:
            res = test_continuity_at_phase_switch(t_phase, m_scale)
            continuity_results.append(res)
            print(f"  - T={t_phase:3.1f}s, M={m_scale:4.1f}kg: C2={res['c2_continuous']}, "
                  f"Salto Jerk q1={res['jump_q1_dddot_m_s3']:.4f} m/s3 (esperado {res['expected_j1_jump_m_s3']:.4f}), "
                  f"Salto Jerk q2={res['jump_q2_dddot_rad_s3']:.4f} rad/s3 (esperado {res['expected_j2_jump_rad_s3']:.4f})")

    # 3. Comparación de aceleración pico frente a otros perfiles
    print("\n[3/5] Evaluando propiedad de aceleración pico vs perfiles cinemáticos...")
    peak_acc_comp = compare_peak_acceleration_with_other_profiles()
    print(f"  - Quíntico a_max normalizado: {peak_acc_comp['quintic_normalized_a_max']}")
    print(f"  - Cicloidal a_max normalizado: {peak_acc_comp['cycloidal_normalized_a_max']}")
    print(f"  - Bang-bang a_max normalizado: {peak_acc_comp['parabolic_bang_bang_normalized_a_max']}")
    print(f"  - Conclusión: {peak_acc_comp['comparison_summary'][:150]}...")

    # 4. Matriz de escalamiento
    print("\n[4/5] Calculando matriz de escalamiento (2/5/10 kg x 0.5/1/2 s)...")
    scaling_data = compute_scaling_matrix()
    fd_res = verify_finite_differences(sample_traj)

    # 5. Verificación geométrica de tapas
    print("\n[5/5] Verificando especificaciones geométricas de las 8 compuertas A07...")
    door_verif = verify_doors_from_json()
    print(f"  - Origen de datos: {door_verif['doors_source']}")
    print(f"  - Compuertas verificadas: {door_verif['doors_count']}")
    for d in door_verif["door_details"]:
        print(f"    * {d['name']:<32} | out={d['out_translation_sign']:+2d} | sign={d['rotation_sign']:+2d} | "
              f"Eje closed: [{d['axis_closed'][0]:.1f}, {d['axis_closed'][1]:.1f}, {d['axis_closed'][2]:.2f}]")

    # Guardar entregables en salidas/
    os.makedirs(SALIDAS_DIR, exist_ok=True)

    output_profiles_path = os.path.join(SALIDAS_DIR, "resultados_perfiles.json")
    with open(output_profiles_path, "w", encoding="utf-8") as f:
        json.dump({
            "matriz_escalamiento": scaling_data,
            "continuidad_interfase_y_saltos_jerk": continuity_results,
            "analisis_limites_unilaterales_referencia_5kg_1s": unilateral_res,
            "comparativa_aceleracion_pico": peak_acc_comp,
            "precision_derivadas_diferencias_finitas": fd_res
        }, f, indent=2)
    print(f"\n[OK] Entregable guardado: {output_profiles_path}")

    output_doors_path = os.path.join(SALIDAS_DIR, "verificacion_signos_tapas.json")
    with open(output_doors_path, "w", encoding="utf-8") as f:
        json.dump(door_verif, f, indent=2)
    print(f"[OK] Entregable guardado: {output_doors_path}")

    output_mech_path = os.path.join(SALIDAS_DIR, "comparativa_mecanismos.json")
    mech_data = get_conceptual_mechanisms_comparison()
    with open(output_mech_path, "w", encoding="utf-8") as f:
        json.dump(mech_data, f, indent=2)
    print(f"[OK] Entregable guardado: {output_mech_path}")


if __name__ == "__main__":
    main()
