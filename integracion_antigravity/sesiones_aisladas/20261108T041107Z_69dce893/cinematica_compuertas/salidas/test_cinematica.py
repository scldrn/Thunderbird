#!/usr/bin/env python3
"""
test_cinematica.py
==================
Suite de pruebas unitarias automatizadas para la verificación de:
  - Condiciones de contorno de posición, velocidad y aceleración en t=0, t=T_fase y t=2*T_fase.
  - Continuidad C^0, C^1 y C^2 en la transición inter-fase.
  - Consistencia del escalamiento geométrico de desplazamientos (m/5)^(1/3) para 2, 5 y 10 kg.
  - Coherencia de signos y ejes para las 8 compuertas desde propuesta_elevacion.json.
  - Correspondencia con los 61 nodos discretos de VERIFICACION_RECORRIDO.json.
  - Consistencia del escalamiento temporal de aceleraciones inversamente proporcional a T^2.
"""

import unittest
import math
import os
import json
import sys

# Importar módulos de cinematica_A07 en salidas/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from cinematica_A07 import (
    QuinticProfile,
    CycloidalProfile,
    TrajectoryA07,
    DoorSpatialModel,
    test_continuity_at_phase_switch,
    verify_finite_differences,
    PATH_PROPUESTA_ELEVACION,
    PATH_VERIFICACION_RECORRIDO,
    LIFT_NOMINAL_M_5KG,
    LIFT_NOMINAL_MM_5KG,
    ROTATION_NOMINAL_RAD,
    ROTATION_NOMINAL_DEG
)


class TestCinematicaPerfiles(unittest.TestCase):

    def test_quintic_boundary_conditions(self):
        """Verifica que el polinomio quíntico cumpla exactamente s(0)=0, s'(0)=0, s''(0)=0, s(1)=1, s'(1)=0, s''(1)=0."""
        self.assertAlmostEqual(QuinticProfile.s(0.0), 0.0, places=12)
        self.assertAlmostEqual(QuinticProfile.ds_dtau(0.0), 0.0, places=12)
        self.assertAlmostEqual(QuinticProfile.d2s_dtau2(0.0), 0.0, places=12)

        self.assertAlmostEqual(QuinticProfile.s(1.0), 1.0, places=12)
        self.assertAlmostEqual(QuinticProfile.ds_dtau(1.0), 0.0, places=12)
        self.assertAlmostEqual(QuinticProfile.d2s_dtau2(1.0), 0.0, places=12)

    def test_cycloidal_boundary_conditions(self):
        """Verifica las condiciones de frontera para el perfil cicloidal."""
        self.assertAlmostEqual(CycloidalProfile.s(0.0), 0.0, places=12)
        self.assertAlmostEqual(CycloidalProfile.ds_dtau(0.0), 0.0, places=12)
        self.assertAlmostEqual(CycloidalProfile.d2s_dtau2(0.0), 0.0, places=12)

        self.assertAlmostEqual(CycloidalProfile.s(1.0), 1.0, places=12)
        self.assertAlmostEqual(CycloidalProfile.ds_dtau(1.0), 0.0, places=12)
        self.assertAlmostEqual(CycloidalProfile.d2s_dtau2(1.0), 0.0, places=12)

    def test_trajectory_extrema_and_endpoints(self):
        """Verifica posiciones y derivadas en t=0, t=T y t=2T para diferentes duraciones y masas."""
        for t_p in [0.5, 1.0, 2.0]:
            for m in [2.0, 5.0, 10.0]:
                traj = TrajectoryA07(t_phase=t_p, mass_scale_kg=m)
                
                # t = 0
                state_0 = traj.evaluate(0.0)
                self.assertEqual(state_0["q1"], 0.0)
                self.assertEqual(state_0["q1_dot"], 0.0)
                self.assertEqual(state_0["q1_ddot"], 0.0)
                self.assertEqual(state_0["q2"], 0.0)
                self.assertEqual(state_0["q2_dot"], 0.0)
                self.assertEqual(state_0["q2_ddot"], 0.0)

                # t = T (conmutación)
                state_T = traj.evaluate(t_p)
                scale_lambda = (m / 5.0) ** (1.0 / 3.0)
                expected_q1 = 0.010 * scale_lambda
                self.assertAlmostEqual(state_T["q1"], expected_q1, places=9)
                self.assertAlmostEqual(state_T["q1_dot"], 0.0, places=9)
                self.assertAlmostEqual(state_T["q1_ddot"], 0.0, places=9)
                self.assertAlmostEqual(state_T["q2"], 0.0, places=9)
                self.assertAlmostEqual(state_T["q2_dot"], 0.0, places=9)
                self.assertAlmostEqual(state_T["q2_ddot"], 0.0, places=9)

                # t = 2T (final)
                state_final = traj.evaluate(2.0 * t_p)
                self.assertAlmostEqual(state_final["q1"], expected_q1, places=9)
                self.assertAlmostEqual(state_final["q1_dot"], 0.0, places=9)
                self.assertAlmostEqual(state_final["q1_ddot"], 0.0, places=9)
                self.assertAlmostEqual(state_final["q2"], ROTATION_NOMINAL_RAD, places=9)
                self.assertAlmostEqual(state_final["q2_dot"], 0.0, places=9)
                self.assertAlmostEqual(state_final["q2_ddot"], 0.0, places=9)

    def test_c2_continuity_at_switch(self):
        """Verifica que no existan discontinuidades finitas en q, q_dot o q_ddot al pasar de fase 1 a fase 2."""
        for t_p in [0.5, 1.0, 2.0]:
            for m in [2.0, 5.0, 10.0]:
                res = test_continuity_at_phase_switch(t_phase=t_p, mass_scale_kg=m, eps=1e-7)
                self.assertTrue(res["c0_continuous"], f"Fallo C0 en T={t_p}, M={m}")
                self.assertTrue(res["c1_continuous"], f"Fallo C1 en T={t_p}, M={m}")
                self.assertTrue(res["c2_continuous"], f"Fallo C2 en T={t_p}, M={m}")

    def test_mass_scaling_values(self):
        """Verifica los valores citados en LEEME.md: aprox 7.37 mm (2kg), 10.0 mm (5kg), 12.60 mm (10kg)."""
        traj_2 = TrajectoryA07(mass_scale_kg=2.0)
        traj_5 = TrajectoryA07(mass_scale_kg=5.0)
        traj_10 = TrajectoryA07(mass_scale_kg=10.0)

        # 2 kg: 10 * (2/5)^(1/3) ~ 7.36806 mm -> redondeado 7.37 mm
        self.assertAlmostEqual(traj_2.d_max_mm, 7.368063, places=3)
        self.assertAlmostEqual(round(traj_2.d_max_mm, 2), 7.37, places=2)

        # 5 kg: 10.0 mm
        self.assertAlmostEqual(traj_5.d_max_mm, 10.000000, places=4)

        # 10 kg: 10 * (10/5)^(1/3) ~ 12.59921 mm -> redondeado 12.60 mm
        self.assertAlmostEqual(traj_10.d_max_mm, 12.599210, places=3)
        self.assertAlmostEqual(round(traj_10.d_max_mm, 2), 12.60, places=2)

    def test_acceleration_time_scaling(self):
        """Verifica que la aceleración escale exactamente con 1 / T^2."""
        traj_05 = TrajectoryA07(t_phase=0.5, mass_scale_kg=5.0)
        traj_10 = TrajectoryA07(t_phase=1.0, mass_scale_kg=5.0)
        traj_20 = TrajectoryA07(t_phase=2.0, mass_scale_kg=5.0)

        ext_05 = traj_05.get_kinematic_extrema()
        ext_10 = traj_10.get_kinematic_extrema()
        ext_20 = traj_20.get_kinematic_extrema()

        # Ratio T=0.5s vs T=1.0s: (1.0 / 0.5)^2 = 4.0
        self.assertAlmostEqual(ext_05["a1_max_m_s2"] / ext_10["a1_max_m_s2"], 4.0, places=6)
        self.assertAlmostEqual(ext_05["alpha2_max_rad_s2"] / ext_10["alpha2_max_rad_s2"], 4.0, places=6)

        # Ratio T=2.0s vs T=1.0s: (1.0 / 2.0)^2 = 0.25
        self.assertAlmostEqual(ext_20["a1_max_m_s2"] / ext_10["a1_max_m_s2"], 0.25, places=6)
        self.assertAlmostEqual(ext_20["alpha2_max_rad_s2"] / ext_10["alpha2_max_rad_s2"], 0.25, places=6)


class TestVerificacionJSON(unittest.TestCase):

    def test_propuesta_elevacion_signs_and_axes(self):
        """Verifica integridad y coherencia física de los signos en propuesta_elevacion.json."""
        self.assertTrue(os.path.exists(PATH_PROPUESTA_ELEVACION))
        with open(PATH_PROPUESTA_ELEVACION, "r", encoding="utf-8") as f:
            doors = json.load(f)

        self.assertEqual(len(doors), 8, "Deben existir exactamente 8 compuertas en el JSON")

        for d in doors:
            name = d["name"]
            lift_mm = d["lift_mm"]
            axis = d["axis_closed"]
            sign = d["sign"]
            out = d["out"]

            self.assertEqual(lift_mm, 10, f"Lift nominal debe ser 10 mm en {name}")

            # Superior vs Inferior
            if "superior" in name:
                self.assertEqual(out, 1, f"Compuerta superior {name} debe tener out=+1 (+Z)")
                self.assertGreater(axis[2], 0.0, f"Eje superior {name} debe tener Z > 0")
            elif "inferior" in name:
                self.assertEqual(out, -1, f"Compuerta inferior {name} debe tener out=-1 (-Z)")
                self.assertLess(axis[2], 0.0, f"Eje inferior {name} debe tener Z < 0")

            # Signo de giro respecto a la posición lateral Y
            y_axis = axis[1]
            if y_axis < 0:  # Lado Y negativo
                expected_sign = 1 if "superior" in name else -1
            else:  # Lado Y positivo
                expected_sign = -1 if "superior" in name else 1
            self.assertEqual(sign, expected_sign, f"Signo incorrecto de rotación en {name}")

    def test_recorrido_discrete_poses_agreement(self):
        """Verifica congruencia entre los 61 nodos de VERIFICACION_RECORRIDO.json y la cinemática."""
        self.assertTrue(os.path.exists(PATH_VERIFICACION_RECORRIDO))
        with open(PATH_VERIFICACION_RECORRIDO, "r", encoding="utf-8") as f:
            rec = json.load(f)

        poses = rec.get("poses", [])
        self.assertEqual(len(poses), 61, "Deben existir 61 poses discretas")

        # Poses 0 a 5: elevación pura de 0 a 10 mm (ángulo 0)
        for i in range(6):
            expected_lift = float(i * 2.0)
            self.assertAlmostEqual(poses[i]["lift_mm"], expected_lift, places=6)
            self.assertAlmostEqual(poses[i]["angle_deg"], 0.0, places=6)

        # Poses 5 a 60: rotación pura de 0 a 110 deg (lift 10 mm)
        for j in range(5, 61):
            expected_angle = float((j - 5) * 2.0)
            self.assertAlmostEqual(poses[j]["lift_mm"], 10.0, places=6)
            self.assertAlmostEqual(poses[j]["angle_deg"], expected_angle, places=6)


if __name__ == "__main__":
    unittest.main()
