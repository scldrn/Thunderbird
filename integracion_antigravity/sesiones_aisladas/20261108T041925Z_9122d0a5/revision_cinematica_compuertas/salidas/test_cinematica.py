#!/usr/bin/env python3
"""
test_cinematica.py
==================
Suite de pruebas unitarias automatizadas para la verificación de:
  - Condiciones de contorno de posición, velocidad, aceleración y jerk.
  - Derivación analítica y numérica de límites unilaterales del movimiento frente al reposo estático.
  - Continuidad C^0, C^1 y C^2 en transiciones y demostración del salto finito de jerk (no C^3).
  - Demostración de que el perfil quíntico NO minimiza la aceleración pico global.
  - Escalamiento geométrico de desplazamientos con (m/5)^(1/3) para 2, 5 y 10 kg.
  - Escalamiento temporal de aceleración (1/T^2) y de jerk (1/T^3).
  - Coherencia geométrica y de signos de apertura para las 8 compuertas A07.
  - Portabilidad estricta: No inferir inexistencia ante archivos no copiados.
"""

import unittest
import math
import os
import json
import sys

# Asegurar importación de módulos en salidas/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from cinematica_A07 import (
    QuinticProfile,
    CycloidalProfile,
    TrajectoryA07,
    DoorSpatialModel,
    A07_DOORS_NOMINAL_SPEC,
    test_continuity_at_phase_switch,
    verify_finite_differences,
    compare_peak_acceleration_with_other_profiles,
    PATH_PROPUESTA_ELEVACION,
    PATH_VERIFICACION_RECORRIDO,
    LIFT_NOMINAL_M_5KG,
    LIFT_NOMINAL_MM_5KG,
    ROTATION_NOMINAL_RAD,
    ROTATION_NOMINAL_DEG
)


class TestCinematicaPerfiles(unittest.TestCase):

    def test_quintic_boundary_conditions(self):
        """
        Verifica que el polinomio quíntico cumpla exactamente:
          s(0)=0, s'(0)=0, s''(0)=0
          s(1)=1, s'(1)=0, s''(1)=0
        Y verifica que s'''(0)=60 != 0 y s'''(1)=60 != 0 (el jerk NO es nulo en fronteras).
        """
        self.assertAlmostEqual(QuinticProfile.s(0.0), 0.0, places=12)
        self.assertAlmostEqual(QuinticProfile.ds_dtau(0.0), 0.0, places=12)
        self.assertAlmostEqual(QuinticProfile.d2s_dtau2(0.0), 0.0, places=12)

        self.assertAlmostEqual(QuinticProfile.s(1.0), 1.0, places=12)
        self.assertAlmostEqual(QuinticProfile.ds_dtau(1.0), 0.0, places=12)
        self.assertAlmostEqual(QuinticProfile.d2s_dtau2(1.0), 0.0, places=12)

        # Derivada tercera en extremos: NO nula (vale 60.0)
        self.assertAlmostEqual(QuinticProfile.d3s_dtau3(0.0), 60.0, places=12)
        self.assertAlmostEqual(QuinticProfile.d3s_dtau3(1.0), 60.0, places=12)

    def test_cycloidal_boundary_conditions(self):
        """
        Verifica condiciones de frontera para el perfil cicloidal:
          s(0)=0, s'(0)=0, s''(0)=0
          s(1)=1, s'(1)=0, s''(1)=0
        Y verifica que s'''(0)=4*pi^2 y s'''(1)=4*pi^2 (jerk NO nulo en extremos).
        """
        self.assertAlmostEqual(CycloidalProfile.s(0.0), 0.0, places=12)
        self.assertAlmostEqual(CycloidalProfile.ds_dtau(0.0), 0.0, places=12)
        self.assertAlmostEqual(CycloidalProfile.d2s_dtau2(0.0), 0.0, places=12)

        self.assertAlmostEqual(CycloidalProfile.s(1.0), 1.0, places=12)
        self.assertAlmostEqual(CycloidalProfile.ds_dtau(1.0), 0.0, places=12)
        self.assertAlmostEqual(CycloidalProfile.d2s_dtau2(1.0), 0.0, places=12)

        expected_jerk_extrema = 4.0 * (math.pi ** 2)
        self.assertAlmostEqual(CycloidalProfile.d3s_dtau3(0.0), expected_jerk_extrema, places=10)
        self.assertAlmostEqual(CycloidalProfile.d3s_dtau3(1.0), expected_jerk_extrema, places=10)

    def test_trajectory_extrema_and_endpoints(self):
        """Verifica posiciones y derivadas en t=0, t=T y t=2T para diferentes duraciones y masas."""
        for t_p in [0.5, 1.0, 2.0]:
            for m in [2.0, 5.0, 10.0]:
                traj = TrajectoryA07(t_phase=t_p, mass_scale_kg=m)
                scale_lambda = (m / 5.0) ** (1.0 / 3.0)
                expected_q1 = 0.010 * scale_lambda

                # t = 0 (inicio)
                st_0 = traj.evaluate(0.0)
                self.assertEqual(st_0["q1"], 0.0)
                self.assertEqual(st_0["q1_dot"], 0.0)
                self.assertEqual(st_0["q1_ddot"], 0.0)
                self.assertEqual(st_0["q2"], 0.0)
                self.assertEqual(st_0["q2_dot"], 0.0)
                self.assertEqual(st_0["q2_ddot"], 0.0)

                # t = T (conmutación inter-fase)
                st_T = traj.evaluate(t_p)
                self.assertAlmostEqual(st_T["q1"], expected_q1, places=9)
                self.assertAlmostEqual(st_T["q1_dot"], 0.0, places=9)
                self.assertAlmostEqual(st_T["q1_ddot"], 0.0, places=9)
                self.assertAlmostEqual(st_T["q2"], 0.0, places=9)
                self.assertAlmostEqual(st_T["q2_dot"], 0.0, places=9)
                self.assertAlmostEqual(st_T["q2_ddot"], 0.0, places=9)

                # t = 2T (final)
                st_final = traj.evaluate(2.0 * t_p)
                self.assertAlmostEqual(st_final["q1"], expected_q1, places=9)
                self.assertAlmostEqual(st_final["q1_dot"], 0.0, places=9)
                self.assertAlmostEqual(st_final["q1_ddot"], 0.0, places=9)
                self.assertAlmostEqual(st_final["q2"], ROTATION_NOMINAL_RAD, places=9)
                self.assertAlmostEqual(st_final["q2_dot"], 0.0, places=9)
                self.assertAlmostEqual(st_final["q2_ddot"], 0.0, places=9)

    def test_c2_continuity_and_jerk_jump_at_switch(self):
        """
        Verifica rigurosamente que en la conmutación t = T:
          - q, q_dot, q_ddot no presenten discontinuidades (Continuidad C0, C1, C2).
          - q_dddot (jerk) presente un salto finito no nulo (no pertenece a C3).
        """
        for t_p in [0.5, 1.0, 2.0]:
            for m in [2.0, 5.0, 10.0]:
                res = test_continuity_at_phase_switch(t_phase=t_p, mass_scale_kg=m, eps=1e-7)
                self.assertTrue(res["c0_continuous"], f"Fallo C0 en T={t_p}, M={m}")
                self.assertTrue(res["c1_continuous"], f"Fallo C1 en T={t_p}, M={m}")
                self.assertTrue(res["c2_continuous"], f"Fallo C2 en T={t_p}, M={m}")
                self.assertFalse(res["c3_continuous"], "El perfil no debe ser C3 (el jerk salta)")

                # Comprobar magnitud del salto de jerk en t=T
                # Salto esperado en q1: 60 * d_max / T^3
                # Salto esperado en q2: 60 * theta_max / T^3
                self.assertAlmostEqual(res["jump_q1_dddot_m_s3"], res["expected_j1_jump_m_s3"], places=3)
                self.assertAlmostEqual(res["jump_q2_dddot_rad_s3"], res["expected_j2_jump_rad_s3"], places=2)

    def test_unilateral_limits_and_jerk_jumps_at_all_boundaries(self):
        """
        Prueba precisa de límites unilaterales del movimiento frente al reposo estático:
          1. En t=0:
             - lim_{t->0^-} q1=0, v1=0, a1=0, j1=0 (reposo estático previo)
             - lim_{t->0^+} q1=0, v1=0, a1=0, j1 = +60*d_max/T^3 (inicio Fase 1)
             - Saltos: Delta q1=0, Delta v1=0, Delta a1=0 (C2 continua); Delta j1 = +60*d_max/T^3 != 0.
          2. En t=T (conmutación):
             - lim_{t->T^-} q1=d_max, v1=0, a1=0, j1 = +60*d_max/T^3; q2=0, v2=0, a2=0, j2=0
             - lim_{t->T^+} q1=d_max, v1=0, a1=0, j1 = 0; q2=0, v2=0, a2=0, j2 = +60*theta_max/T^3
             - Saltos: Delta q=0, Delta v=0, Delta a=0 (C2 continua)
             - Saltos de jerk: Delta j1 = -60*d_max/T^3 != 0; Delta j2 = +60*theta_max/T^3 != 0.
          3. En t=2T:
             - lim_{t->2T^-} q2=theta_max, v2=0, a2=0, j2 = +60*theta_max/T^3
             - lim_{t->2T^+} q2=theta_max, v2=0, a2=0, j2 = 0 (reposo estático final)
             - Saltos: Delta q=0, Delta v=0, Delta a=0 (C2 continua); Delta j2 = -60*theta_max/T^3 != 0.
        """
        for t_p in [0.5, 1.0, 2.0]:
            for m in [2.0, 5.0, 10.0]:
                traj = TrajectoryA07(t_phase=t_p, mass_scale_kg=m)
                unilateral = traj.get_unilateral_limits_and_jumps()

                expected_j1 = 60.0 * traj.d_max_m / (t_p ** 3)
                expected_j2 = 60.0 * traj.theta_max_rad / (t_p ** 3)

                # 1. Frontera t = 0
                b0 = unilateral["t_0.0s"]
                self.assertTrue(b0["is_C0"])
                self.assertTrue(b0["is_C1"])
                self.assertTrue(b0["is_C2"])
                self.assertFalse(b0["is_C3"])
                self.assertAlmostEqual(b0["jumps"]["jump_q1_dddot_m_s3"], expected_j1, places=3)
                self.assertAlmostEqual(b0["jumps"]["jump_q2_dddot_rad_s3"], 0.0, places=6)

                # 2. Frontera t = T
                bT = unilateral[f"t_{t_p:3.1f}s"]
                self.assertTrue(bT["is_C0"])
                self.assertTrue(bT["is_C1"])
                self.assertTrue(bT["is_C2"])
                self.assertFalse(bT["is_C3"])
                self.assertAlmostEqual(bT["jumps"]["jump_q1_dddot_m_s3"], -expected_j1, places=3)
                self.assertAlmostEqual(bT["jumps"]["jump_q2_dddot_rad_s3"], expected_j2, places=3)

                # 3. Frontera t = 2T
                b2T = unilateral[f"t_{2.0*t_p:3.1f}s"]
                self.assertTrue(b2T["is_C0"])
                self.assertTrue(b2T["is_C1"])
                self.assertTrue(b2T["is_C2"])
                self.assertFalse(b2T["is_C3"])
                self.assertAlmostEqual(b2T["jumps"]["jump_q1_dddot_m_s3"], 0.0, places=6)
                self.assertAlmostEqual(b2T["jumps"]["jump_q2_dddot_rad_s3"], -expected_j2, places=3)

    def test_peak_acceleration_not_globally_minimal(self):
        """
        Demuestra formalmente que el polinomio quíntico NO minimiza la aceleración pico
        entre todos los perfiles posibles.
        """
        comp = compare_peak_acceleration_with_other_profiles()

        # El perfil parabólico (bang-bang) alcanza a_max = 4.0
        # El perfil quíntico alcanza a_max = 10*sqrt(3)/3 ~ 5.7735
        # 4.0 < 5.7735 -> el quíntico tiene un 44.3% más de aceleración pico que el bang-bang
        self.assertLess(comp["parabolic_bang_bang_normalized_a_max"], comp["quintic_normalized_a_max"])
        self.assertAlmostEqual(comp["parabolic_bang_bang_normalized_a_max"], 4.0, places=6)
        self.assertAlmostEqual(comp["quintic_normalized_a_max"], 5.773503, places=5)

        # El quíntico sí es menor que el cicloidal (5.7735 < 6.2832)
        self.assertLess(comp["quintic_normalized_a_max"], comp["cycloidal_normalized_a_max"])

    def test_mass_scaling_values(self):
        """Verifica los valores citados en LEEME.md: aprox 7.37 mm (2kg), 10.0 mm (5kg), 12.60 mm (10kg)."""
        traj_2 = TrajectoryA07(mass_scale_kg=2.0)
        traj_5 = TrajectoryA07(mass_scale_kg=5.0)
        traj_10 = TrajectoryA07(mass_scale_kg=10.0)

        self.assertAlmostEqual(traj_2.d_max_mm, 7.368063, places=3)
        self.assertAlmostEqual(round(traj_2.d_max_mm, 2), 7.37, places=2)

        self.assertAlmostEqual(traj_5.d_max_mm, 10.000000, places=4)

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

        self.assertAlmostEqual(ext_05["a1_max_m_s2"] / ext_10["a1_max_m_s2"], 4.0, places=6)
        self.assertAlmostEqual(ext_05["alpha2_max_rad_s2"] / ext_10["alpha2_max_rad_s2"], 4.0, places=6)

        self.assertAlmostEqual(ext_20["a1_max_m_s2"] / ext_10["a1_max_m_s2"], 0.25, places=6)
        self.assertAlmostEqual(ext_20["alpha2_max_rad_s2"] / ext_10["alpha2_max_rad_s2"], 0.25, places=6)

    def test_jerk_time_scaling_inverse_cube(self):
        """Verifica que el salto de Jerk escale con 1 / T^3."""
        traj_05 = TrajectoryA07(t_phase=0.5, mass_scale_kg=5.0)
        traj_10 = TrajectoryA07(t_phase=1.0, mass_scale_kg=5.0)
        traj_20 = TrajectoryA07(t_phase=2.0, mass_scale_kg=5.0)

        u_05 = traj_05.get_unilateral_limits_and_jumps()["t_0.0s"]["jumps"]["jump_q1_dddot_m_s3"]
        u_10 = traj_10.get_unilateral_limits_and_jumps()["t_0.0s"]["jumps"]["jump_q1_dddot_m_s3"]
        u_20 = traj_20.get_unilateral_limits_and_jumps()["t_0.0s"]["jumps"]["jump_q1_dddot_m_s3"]

        # Ratio T=0.5s vs T=1.0s: (1.0 / 0.5)^3 = 8.0
        self.assertAlmostEqual(u_05 / u_10, 8.0, places=6)

        # Ratio T=2.0s vs T=1.0s: (1.0 / 2.0)^3 = 0.125
        self.assertAlmostEqual(u_20 / u_10, 0.125, places=6)


class TestGeometriaTapas(unittest.TestCase):

    def test_nominal_doors_geometry_and_signs(self):
        """Verifica la especificación nominal A07 para las 8 compuertas."""
        self.assertEqual(len(A07_DOORS_NOMINAL_SPEC), 8)

        for d in A07_DOORS_NOMINAL_SPEC:
            name = d["name"]
            lift_mm = d["lift_mm"]
            axis = d["axis_closed"]
            sign = d["sign"]
            out = d["out"]

            self.assertEqual(lift_mm, 10.0)

            if "superior" in name:
                self.assertEqual(out, 1, f"Compuerta superior {name} debe tener out=+1 (+Z)")
                self.assertGreater(axis[2], 0.0, f"Eje superior {name} debe tener Z > 0")
            elif "inferior" in name:
                self.assertEqual(out, -1, f"Compuerta inferior {name} debe tener out=-1 (-Z)")
                self.assertLess(axis[2], 0.0, f"Eje inferior {name} debe tener Z < 0")

            # Signo de giro respecto a la coordenada lateral Y
            y_axis = axis[1]
            if y_axis < 0:
                expected_sign = 1 if "superior" in name else -1
            else:
                expected_sign = -1 if "superior" in name else 1
            self.assertEqual(sign, expected_sign, f"Signo incorrecto de rotación en {name}")

    def test_door_spatial_transform(self):
        """Verifica el cálculo de cinemática espacial 3D para una compuerta representativa."""
        door_record = A07_DOORS_NOMINAL_SPEC[0]  # compuerta_0_superior_enrasada: Y=-124, Z=+65.462, out=+1, sign=+1
        model = DoorSpatialModel(door_record)

        # 1. Pose cerrada (q1=0, q2=0)
        p_closed = [-200.0, -124.0, 65.462]
        p_t0 = model.transform_point(p_closed, q1_m=0.0, q2_rad=0.0)
        self.assertAlmostEqual(p_t0[0], -200.0, places=4)
        self.assertAlmostEqual(p_t0[1], -124.0, places=4)
        self.assertAlmostEqual(p_t0[2], 65.462, places=4)

        # 2. Pose elevada (q1=10 mm = 0.010 m, q2=0)
        p_elevated = model.transform_point(p_closed, q1_m=0.010, q2_rad=0.0)
        self.assertAlmostEqual(p_elevated[0], -200.0, places=4)
        self.assertAlmostEqual(p_elevated[1], -124.0, places=4)
        self.assertAlmostEqual(p_elevated[2], 65.462 + 10.0, places=4)

    def test_propuesta_elevacion_file_conditional(self):
        """
        Prueba condicional de archivo: Si propuesta_elevacion.json está presente,
        verifica que coincida con las 8 compuertas nominales.
        Si no fue copiado a entradas/, la prueba se omite cleanly conforme a la directriz:
        'No infieras que un archivo no copiado no existe'.
        """
        if not os.path.exists(PATH_PROPUESTA_ELEVACION):
            self.skipTest(
                f"Archivo propuesta_elevacion.json no fue copiado en entradas/ ({PATH_PROPUESTA_ELEVACION}). "
                "Conforme a directriz operativa, no se infiere su inexistencia; comprobación omitida."
            )

        with open(PATH_PROPUESTA_ELEVACION, "r", encoding="utf-8") as f:
            doors = json.load(f)
        self.assertEqual(len(doors), 8)

    def test_recorrido_file_conditional(self):
        """
        Prueba condicional de archivo: Si VERIFICACION_RECORRIDO.json está presente,
        verifica sus 61 nodos discretos.
        Si no fue copiado a entradas/, la prueba se omite cleanly conforme a la directriz.
        """
        if not os.path.exists(PATH_VERIFICACION_RECORRIDO):
            self.skipTest(
                f"Archivo VERIFICACION_RECORRIDO.json no fue copiado en entradas/ ({PATH_VERIFICACION_RECORRIDO}). "
                "Conforme a directriz operativa, no se infiere su inexistencia; comprobación omitida."
            )

        with open(PATH_VERIFICACION_RECORRIDO, "r", encoding="utf-8") as f:
            rec = json.load(f)
        poses = rec.get("poses", [])
        self.assertEqual(len(poses), 61)


if __name__ == "__main__":
    unittest.main()
