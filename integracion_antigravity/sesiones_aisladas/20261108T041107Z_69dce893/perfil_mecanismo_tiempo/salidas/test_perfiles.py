"""
test_perfiles.py
================
Conjunto de pruebas estándar con unittest para validar la cinemática analítica,
el muestreo numérico, la continuidad en dos fases y la separación rigurosa
de los requerimientos dinámicos.
"""

import math
import os
import unittest
from salidas.perfil_cinematico import (
    SmoothQuinticPolynomial,
    SinglePhaseKinematics,
    TwoPhaseMotionProfile,
    DynamicsIndeterminacyAnalysis,
    generate_phase_tables
)


class TestSmoothQuinticPolynomial(unittest.TestCase):
    """Pruebas del polinomio suave s(u) = 10*u^3 - 15*u^4 + 6*u^5."""

    def test_boundary_conditions(self):
        """Comprueba que s(0)=0, s(1)=1 y derivadas nulas en extremos."""
        self.assertAlmostEqual(SmoothQuinticPolynomial.s(0.0), 0.0, places=9)
        self.assertAlmostEqual(SmoothQuinticPolynomial.s(1.0), 1.0, places=9)

        self.assertAlmostEqual(SmoothQuinticPolynomial.ds_du(0.0), 0.0, places=9)
        self.assertAlmostEqual(SmoothQuinticPolynomial.ds_du(1.0), 0.0, places=9)

        self.assertAlmostEqual(SmoothQuinticPolynomial.d2s_du2(0.0), 0.0, places=9)
        self.assertAlmostEqual(SmoothQuinticPolynomial.d2s_du2(1.0), 0.0, places=9)

    def test_monotonicity(self):
        """Comprueba que ds/du >= 0 para todo u en [0, 1]."""
        for i in range(1001):
            u = i / 1000.0
            vel = SmoothQuinticPolynomial.ds_du(u)
            self.assertGreaterEqual(vel, 0.0)

    def test_symmetry(self):
        """Comprueba propiedades de simetría de posición, velocidad y aceleración."""
        for i in range(101):
            u = i / 100.0
            # Simetría de punto de inflexión en u=0.5: s(u) = 1 - s(1-u)
            self.assertAlmostEqual(
                SmoothQuinticPolynomial.s(u),
                1.0 - SmoothQuinticPolynomial.s(1.0 - u),
                places=9
            )
            # Simetría par de velocidad: s'(u) = s'(1-u)
            self.assertAlmostEqual(
                SmoothQuinticPolynomial.ds_du(u),
                SmoothQuinticPolynomial.ds_du(1.0 - u),
                places=9
            )
            # Simetría impar de aceleración: s''(u) = -s''(1-u)
            self.assertAlmostEqual(
                SmoothQuinticPolynomial.d2s_du2(u),
                -SmoothQuinticPolynomial.d2s_du2(1.0 - u),
                places=9
            )

    def test_exact_velocity_maximum(self):
        """Comprueba que c_v = 15/8 = 1.875 exactamente en u=0.5."""
        u_max = SmoothQuinticPolynomial.U_VMAX
        self.assertEqual(u_max, 0.5)
        c_v_calc = SmoothQuinticPolynomial.ds_du(u_max)
        self.assertAlmostEqual(c_v_calc, 1.875, places=9)
        self.assertAlmostEqual(c_v_calc, SmoothQuinticPolynomial.C_V, places=9)

        # Comprobar que en puntos vecinos es menor
        eps = 1e-3
        self.assertGreater(c_v_calc, SmoothQuinticPolynomial.ds_du(u_max - eps))
        self.assertGreater(c_v_calc, SmoothQuinticPolynomial.ds_du(u_max + eps))

    def test_exact_acceleration_extrema(self):
        """Comprueba que c_a = 10 / sqrt(3) en u = 0.5 +- sqrt(3)/6."""
        c_a_exact = 10.0 / math.sqrt(3.0)

        u1 = SmoothQuinticPolynomial.U_AMAX1
        u2 = SmoothQuinticPolynomial.U_AMAX2

        self.assertAlmostEqual(u1, 0.5 - math.sqrt(3.0) / 6.0, places=9)
        self.assertAlmostEqual(u2, 0.5 + math.sqrt(3.0) / 6.0, places=9)

        a1 = SmoothQuinticPolynomial.d2s_du2(u1)
        a2 = SmoothQuinticPolynomial.d2s_du2(u2)

        self.assertAlmostEqual(a1, c_a_exact, places=9)
        self.assertAlmostEqual(a2, -c_a_exact, places=9)

    def test_jerk_extrema(self):
        """Comprueba valores de jerk en contorno y centro."""
        self.assertAlmostEqual(SmoothQuinticPolynomial.d3s_du3(0.0), 60.0, places=9)
        self.assertAlmostEqual(SmoothQuinticPolynomial.d3s_du3(1.0), 60.0, places=9)
        self.assertAlmostEqual(SmoothQuinticPolynomial.d3s_du3(0.5), -30.0, places=9)


class TestSinglePhaseKinematics(unittest.TestCase):
    """Pruebas de cinemática de fase única para traslación y rotación."""

    def test_translation_durations(self):
        """Valida traslación 10 mm en duraciones 0.25, 0.5, 1.0, 2.0 s."""
        dh = 10.0  # mm
        cv = 1.875
        ca = 10.0 / math.sqrt(3.0)

        test_cases = [
            (0.25, cv * 40.0, ca * 160.0),
            (0.50, cv * 20.0, ca * 40.0),
            (1.00, cv * 10.0, ca * 10.0),
            (2.00, cv * 5.0, ca * 2.5)
        ]

        for T, exp_v, exp_a in test_cases:
            phase = SinglePhaseKinematics("test_trans", dh, "mm", T)
            self.assertAlmostEqual(phase.v_max_exact, exp_v, places=6)
            self.assertAlmostEqual(phase.a_max_exact, exp_a, places=6)
            self.assertAlmostEqual(phase.position(0.0), 0.0, places=9)
            self.assertAlmostEqual(phase.position(T), dh, places=9)
            self.assertAlmostEqual(phase.velocity(0.0), 0.0, places=9)
            self.assertAlmostEqual(phase.velocity(T), 0.0, places=9)
            self.assertAlmostEqual(phase.acceleration(0.0), 0.0, places=9)
            self.assertAlmostEqual(phase.acceleration(T), 0.0, places=9)

    def test_rotation_durations(self):
        """Valida giro 110 deg en duraciones 0.25, 0.5, 1.0, 2.0 s."""
        dtheta_deg = 110.0
        dtheta_rad = math.radians(110.0)
        cv = 1.875
        ca = 10.0 / math.sqrt(3.0)

        for T in [0.25, 0.5, 1.0, 2.0]:
            p_deg = SinglePhaseKinematics("rot_deg", dtheta_deg, "deg", T)
            p_rad = SinglePhaseKinematics("rot_rad", dtheta_rad, "rad", T)

            exp_w_deg = cv * (dtheta_deg / T)
            exp_alpha_deg = ca * (dtheta_deg / (T ** 2))
            exp_w_rad = cv * (dtheta_rad / T)
            exp_alpha_rad = ca * (dtheta_rad / (T ** 2))

            self.assertAlmostEqual(p_deg.v_max_exact, exp_w_deg, places=6)
            self.assertAlmostEqual(p_deg.a_max_exact, exp_alpha_deg, places=6)
            self.assertAlmostEqual(p_rad.v_max_exact, exp_w_rad, places=6)
            self.assertAlmostEqual(p_rad.a_max_exact, exp_alpha_rad, places=6)

            # Relación angular deg <-> rad
            self.assertAlmostEqual(math.radians(p_deg.v_max_exact), p_rad.v_max_exact, places=6)
            self.assertAlmostEqual(math.radians(p_deg.a_max_exact), p_rad.a_max_exact, places=6)

    def test_numerical_integrals(self):
        """Verifica que integral(v*dt) = Delta_q e integral(a*dt) = 0."""
        phase = SinglePhaseKinematics("test", 10.0, "mm", 0.5)
        accuracy = phase.evaluate_sampling_accuracy(5001)

        self.assertLess(accuracy["integral_v_error"], 1e-7)
        self.assertLess(accuracy["integral_a_error"], 1e-12)


class TestSamplingAccuracyAndConvergence(unittest.TestCase):
    """Comprobación analítica vs muestreo y estudio de convergencia."""

    def test_velocity_zero_sampling_error_for_odd_n(self):
        """Para N impar, u=0.5 cae exactamente en la malla => error de v_max es 0."""
        phase = SinglePhaseKinematics("test", 10.0, "mm", 0.5)
        for n in [21, 51, 101, 1001]:
            acc = phase.evaluate_sampling_accuracy(n)
            self.assertAlmostEqual(acc["v_max_sampled_analytic"], phase.v_max_exact, places=9)
            self.assertAlmostEqual(acc["err_v_sampled"], 0.0, places=9)

    def test_acceleration_sampling_convergence(self):
        """
        Para la aceleración, u_amax1 es irracional (0.5 - sqrt(3)/6).
        El error disminuye cuadráticamente conforme N aumenta.
        """
        phase = SinglePhaseKinematics("test", 10.0, "mm", 0.5)

        acc_21 = phase.evaluate_sampling_accuracy(21)
        acc_101 = phase.evaluate_sampling_accuracy(101)
        acc_1001 = phase.evaluate_sampling_accuracy(1001)
        acc_10001 = phase.evaluate_sampling_accuracy(10001)

        # Monotonía estricta de reducción de error de muestreo
        self.assertGreater(acc_21["err_a_sampled"], acc_101["err_a_sampled"])
        self.assertGreater(acc_101["err_a_sampled"], acc_1001["err_a_sampled"])
        self.assertGreater(acc_1001["err_a_sampled"], acc_10001["err_a_sampled"])

        # Error relativo a N=10001 es inferior al 0.0001%
        self.assertLess(acc_10001["rel_err_a_sampled_pct"], 1e-4)

    def test_finite_difference_convergence(self):
        """Verifica convergencia de la aceleración por diferencias finitas centrales."""
        phase = SinglePhaseKinematics("test", 10.0, "mm", 0.5)
        acc_101 = phase.evaluate_sampling_accuracy(101)
        acc_1001 = phase.evaluate_sampling_accuracy(1001)

        self.assertGreater(acc_101["err_a_fd"], acc_1001["err_a_fd"])
        self.assertLess(acc_1001["err_a_fd"], 0.01)  # Menos de 0.01 mm/s^2 con dt=0.5ms


class TestTwoPhaseMotionSequence(unittest.TestCase):
    """Comprobación de la maniobra completa en dos fases."""

    def test_phase_independence_and_continuity(self):
        """
        Fase 1: elevación 0 -> 10 mm, theta = 0.
        Fase 2: traslación 10 mm constante, theta 0 -> 110 deg.
        Continuidad suave C^2 en t = T1.
        """
        profile = TwoPhaseMotionProfile(delta_h_mm=10.0, delta_theta_deg=110.0, T1=0.5, T2=0.5)

        # Inicio t = 0
        s0 = profile.state_at(0.0)
        self.assertAlmostEqual(s0["h_mm"], 0.0, places=9)
        self.assertAlmostEqual(s0["v_mm_s"], 0.0, places=9)
        self.assertAlmostEqual(s0["theta_deg"], 0.0, places=9)
        self.assertAlmostEqual(s0["omega_deg_s"], 0.0, places=9)

        # Punto de transición t = T1 = 0.5
        s_trans = profile.state_at(0.5)
        self.assertAlmostEqual(s_trans["h_mm"], 10.0, places=9)
        self.assertAlmostEqual(s_trans["v_mm_s"], 0.0, places=9)
        self.assertAlmostEqual(s_trans["a_mm_s2"], 0.0, places=9)
        self.assertAlmostEqual(s_trans["theta_deg"], 0.0, places=9)
        self.assertAlmostEqual(s_trans["omega_deg_s"], 0.0, places=9)
        self.assertAlmostEqual(s_trans["alpha_deg_s2"], 0.0, places=9)

        # Mitad de Fase 2: t = 0.75
        s_mid2 = profile.state_at(0.75)
        self.assertAlmostEqual(s_mid2["h_mm"], 10.0, places=9)
        self.assertAlmostEqual(s_mid2["v_mm_s"], 0.0, places=9)
        self.assertAlmostEqual(s_mid2["theta_deg"], 55.0, places=9)  # Mitad de 110 deg
        self.assertAlmostEqual(s_mid2["omega_deg_s"], 412.5, places=6)

        # Final t = 1.0
        s_end = profile.state_at(1.0)
        self.assertAlmostEqual(s_end["h_mm"], 10.0, places=9)
        self.assertAlmostEqual(s_end["theta_deg"], 110.0, places=9)
        self.assertAlmostEqual(s_end["omega_deg_s"], 0.0, places=9)
        self.assertAlmostEqual(s_end["alpha_deg_s2"], 0.0, places=9)


class TestDynamicIndeterminacy(unittest.TestCase):
    """
    Verifica que la ausencia de masa, inercia y rozamiento en los archivos
    de referencia impida físicamente el dimensionamiento de motores.
    """

    def test_config_audit_contains_null_mass(self):
        """Verifica que C02_CANDIDATA.json contiene masa e inercia nulas/no asignadas."""
        ref_path = "entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json"
        self.assertTrue(os.path.exists(ref_path), f"Falta archivo de referencia {ref_path}")

        audit = DynamicsIndeterminacyAnalysis.inspect_reference_model(ref_path)
        self.assertEqual(audit["status"], "loaded")
        self.assertIsNone(audit["actual_mass_kg"], "actual_mass_kg debe ser None")
        self.assertIsNone(audit["actual_CG_m"], "actual_CG_m debe ser None")
        self.assertIsNone(audit["actual_inertia_kgm2"], "actual_inertia_kgm2 debe ser None")
        self.assertFalse(audit["rotor_motor_servo_and_cooling_qualified"])

    def test_specific_acceleration_is_pure_kinematic_invariant(self):
        """
        La aceleración lineal a_max (N/kg) y angular alpha_max (N*m/(kg*m^2))
        son los únicos invariantes independientes de la masa asignada.
        """
        table_data = generate_phase_tables([0.5], dh_mm=10.0, dtheta_deg=110.0)
        t_row = table_data["translation_table"][0]
        r_row = table_data["rotation_table"][0]

        # F_inercial / m = a_max = 0.230940 m/s^2 = 0.230940 N/kg
        self.assertAlmostEqual(t_row["fuerza_especifica_inercial_N_kg"], t_row["a_max_m_s2"], places=9)

        # tau_inercial / I = alpha_max = 44.337318 rad/s^2 = 44.337318 N*m/(kg*m^2)
        self.assertAlmostEqual(r_row["par_especifico_inercial_Nm_kgm2"], r_row["alpha_max_rad_s2"], places=6)


if __name__ == "__main__":
    unittest.main()
