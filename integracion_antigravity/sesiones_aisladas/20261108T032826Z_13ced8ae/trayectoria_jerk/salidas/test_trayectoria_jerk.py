#!/usr/bin/env python3
"""
test_trayectoria_jerk.py
------------------------
Suite de pruebas unitarias y de verificación para la comparación 1D de
desplazamiento de reposo a reposo con límites de aceleración y jerk.

Verifica:
  1. Rama triangular (ta = 0, a_peak < A, T = (32d/J)^(1/3)).
  2. Rama con meseta (ta > 0, a_peak = A, T = tj + sqrt(tj^2 + 4d/A)).
  3. Continuidad temporal C0 (aceleración), C1 (velocidad) y C2 (posición).
  4. Continuidad en la transición de ramas en d = d_crit = 2*A^3/J^2.
  5. Invarianza dimensional y consistencia de unidades.
  6. Condiciones de contorno iniciales y finales (reposo a reposo, x=d).
  7. Simetría temporal (aceleración antisimétrica, velocidad simétrica).
  8. Integración numérica independiente (RK4) y concordancia analítica.
  9. Casos de hipótesis de la matriz (A = 0.5g, 1.0g; J = 1, 5, 20 m/s^3).
 10. Comparación con el límite ideal sin jerk t_ideal = sqrt(4d/A).

Uso:
  python3 -m unittest salidas/test_trayectoria_jerk.py
"""

import math
import unittest
import os
import sys

# Permitir importación del módulo local
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from trayectoria_jerk import (
    TrajectoryConfig,
    TrajectoryProfile,
    compute_profile,
    eval_analytical,
    eval_jerk,
    simulate_numerical,
    verify_continuity,
    verify_branch_transition,
    G_STANDARD
)


class TestTrayectoriaJerk(unittest.TestCase):

    def setUp(self):
        self.g = G_STANDARD
        self.d = 5.0

    def test_branch_classification(self):
        """Verifica la clasificación correcta de ramas según d_crit = 2*A^3 / J^2."""
        # A = 0.5g
        A_05 = 0.5 * self.g
        d_crit_j1 = 2.0 * (A_05**3) / (1.0**2)
        d_crit_j5 = 2.0 * (A_05**3) / (5.0**2)
        d_crit_j20 = 2.0 * (A_05**3) / (20.0**2)

        self.assertGreater(d_crit_j1, self.d)   # 235.8 m > 5 m -> triangular
        self.assertGreater(d_crit_j5, self.d)   # 9.43 m > 5 m -> triangular
        self.assertLess(d_crit_j20, self.d)     # 0.589 m < 5 m -> meseta

        p1 = compute_profile(TrajectoryConfig("p1", self.d, 0.5, 1.0))
        p2 = compute_profile(TrajectoryConfig("p2", self.d, 0.5, 5.0))
        p3 = compute_profile(TrajectoryConfig("p3", self.d, 0.5, 20.0))

        self.assertEqual(p1.branch, "triangular")
        self.assertEqual(p2.branch, "triangular")
        self.assertEqual(p3.branch, "meseta")

        # A = 1.0g
        p4 = compute_profile(TrajectoryConfig("p4", self.d, 1.0, 1.0))
        p5 = compute_profile(TrajectoryConfig("p5", self.d, 1.0, 5.0))
        p6 = compute_profile(TrajectoryConfig("p6", self.d, 1.0, 20.0))

        self.assertEqual(p4.branch, "triangular")
        self.assertEqual(p5.branch, "triangular")
        self.assertEqual(p6.branch, "meseta")

    def test_triangular_branch_properties(self):
        """Verifica que en la rama triangular ta == 0, a_peak < A y T no depende de A."""
        p_05_j1 = compute_profile(TrajectoryConfig("A05_J1", self.d, 0.5, 1.0))
        p_10_j1 = compute_profile(TrajectoryConfig("A10_J1", self.d, 1.0, 1.0))

        # En rama triangular, ta debe ser exactamente cero
        self.assertEqual(p_05_j1.ta, 0.0)
        self.assertEqual(p_10_j1.ta, 0.0)

        # La aceleración pico debe ser menor al límite A
        self.assertLess(p_05_j1.a_peak, p_05_j1.config.A)
        self.assertLess(p_10_j1.a_peak, p_10_j1.config.A)

        # Como ninguna alcanza A, ambos casos tienen IDÉNTICA aceleración pico, tj y T
        self.assertAlmostEqual(p_05_j1.a_peak, p_10_j1.a_peak, places=10)
        self.assertAlmostEqual(p_05_j1.tj, p_10_j1.tj, places=10)
        self.assertAlmostEqual(p_05_j1.T, p_10_j1.T, places=10)

        # Comprobación de fórmula cerrada: T = (32 * d / J)^(1/3)
        t_expected = (32.0 * self.d / 1.0) ** (1.0 / 3.0)
        self.assertAlmostEqual(p_05_j1.T, t_expected, places=10)

    def test_plateau_branch_properties(self):
        """Verifica que en la rama con meseta a_peak == A, ta > 0 y T satisface la fórmula cerrada."""
        p = compute_profile(TrajectoryConfig("A05_J20", self.d, 0.5, 20.0))

        self.assertEqual(p.branch, "meseta")
        self.assertAlmostEqual(p.a_peak, p.config.A, places=10)
        self.assertGreater(p.ta, 0.0)
        self.assertAlmostEqual(p.tj, p.config.A / p.config.J, places=10)

        # Comprobación de la relación fundamental de desplazamiento d = A * (tj + ta) * (2*tj + ta)
        tj = p.tj
        ta = p.ta
        A = p.config.A
        d_recalc = A * (tj + ta) * (2.0 * tj + ta)
        self.assertAlmostEqual(d_recalc, self.d, places=10)

        # Comprobación de la fórmula T = tj + sqrt(tj^2 + 4d/A)
        t_expected = tj + math.sqrt(tj**2 + 4.0 * self.d / A)
        self.assertAlmostEqual(p.T, t_expected, places=10)

    def test_branch_transition_continuity(self):
        """Verifica que en d = d_crit la transición entre ramas sea estrictamente continua y suave."""
        A = 0.5 * self.g
        J = 20.0
        d_crit = 2.0 * (A**3) / (J**2)

        # Evaluación analítica en el punto crítico con rama triangular y rama meseta
        # Triangular:
        a_p_crit_tri = (0.5 * d_crit * (J**2)) ** (1.0 / 3.0)
        tj_crit_tri = a_p_crit_tri / J
        T_crit_tri = 4.0 * tj_crit_tri

        # Meseta con ta = 0:
        tj_crit_mes = A / J
        T_crit_mes = 4.0 * tj_crit_mes

        self.assertAlmostEqual(a_p_crit_tri, A, places=10)
        self.assertAlmostEqual(tj_crit_tri, tj_crit_mes, places=10)
        self.assertAlmostEqual(T_crit_tri, T_crit_mes, places=10)

        # Comprobación de la función de transición
        res = verify_branch_transition(A, J, eps=1e-6)
        self.assertTrue(res["is_smooth"])
        self.assertLess(res["diff_T_below"], 1e-5)
        self.assertLess(res["diff_T_above"], 1e-5)

    def test_internal_continuity(self):
        """Verifica la continuidad C0 de la aceleración, C1 de la velocidad y C2 de la posición."""
        configs = [
            TrajectoryConfig("Triangular", 5.0, 0.5, 1.0),
            TrajectoryConfig("Meseta", 5.0, 0.5, 20.0),
            TrajectoryConfig("Casi_Critico", 5.0, 1.0, 20.0)
        ]

        for cfg in configs:
            prof = compute_profile(cfg)
            cont = verify_continuity(prof, eps=1e-8)
            self.assertTrue(cont["all_continuous"], f"Fallo de continuidad en {cfg.name}")

    def test_boundary_conditions(self):
        """Verifica que el movimiento inicie y termine en reposo con posición exacta d."""
        for A_g in [0.5, 1.0]:
            for J in [1.0, 5.0, 20.0]:
                cfg = TrajectoryConfig("test_bc", self.d, A_g, J)
                prof = compute_profile(cfg)

                # Inicio t = 0
                s0 = eval_analytical(prof, 0.0)
                self.assertAlmostEqual(s0.pos, 0.0, places=10)
                self.assertAlmostEqual(s0.vel, 0.0, places=10)
                self.assertAlmostEqual(s0.accel, 0.0, places=10)

                # Fin t = T
                sT = eval_analytical(prof, prof.T)
                self.assertAlmostEqual(sT.pos, self.d, places=10)
                self.assertAlmostEqual(sT.vel, 0.0, places=10)
                self.assertAlmostEqual(sT.accel, 0.0, places=10)

    def test_symmetry_properties(self):
        """Verifica la simetría de la aceleración antisimétrica y velocidad simétrica respecto a T/2."""
        for A_g in [0.5, 1.0]:
            for J in [1.0, 20.0]:
                cfg = TrajectoryConfig("sym", self.d, A_g, J)
                prof = compute_profile(cfg)
                T = prof.T

                # Probar en varios puntos de la trayectoria
                for frac in [0.1, 0.25, 0.4, 0.5]:
                    t_a = frac * T
                    t_b = (1.0 - frac) * T

                    s_a = eval_analytical(prof, t_a)
                    s_b = eval_analytical(prof, t_b)

                    # Aceleración antisimétrica: a(t) = -a(T - t)
                    self.assertAlmostEqual(s_a.accel, -s_b.accel, places=9)
                    # Velocidad simétrica: v(t) = v(T - t)
                    self.assertAlmostEqual(s_a.vel, s_b.vel, places=9)
                    # Posición simétrica complementaria: x(t) + x(T - t) = d
                    self.assertAlmostEqual(s_a.pos + s_b.pos, self.d, places=9)

    def test_numerical_simulation_convergence(self):
        """Verifica que la integración numérica independiente converja a la solución analítica."""
        cfg = TrajectoryConfig("sim_test", 5.0, 0.5, 20.0)
        prof = compute_profile(cfg)

        # 1. Integración alineada por segmentos
        sim_aligned = simulate_numerical(prof, method="rk4_segment_aligned", steps_per_segment=500)
        self.assertLess(abs(sim_aligned.terminal_error_x), 1e-10)
        self.assertLess(abs(sim_aligned.terminal_error_v), 1e-12)
        self.assertLess(abs(sim_aligned.terminal_error_a), 1e-12)
        self.assertLess(sim_aligned.max_error_x, 1e-10)

        # 2. Integración uniforme con paso fino (rejilla no alineada sufre O(dt) en discontinuidades)
        sim_uniform = simulate_numerical(prof, method="rk4_uniform", uniform_dt=1e-5)
        self.assertLess(abs(sim_uniform.terminal_error_x), 5e-5)
        self.assertLess(abs(sim_uniform.terminal_error_v), 1e-4)

    def test_ideal_profile_comparison(self):
        """Verifica que T_jerk > t_ideal para todo J finito y que tienda a t_ideal cuando J -> inf."""
        A = 0.5 * self.g
        d = self.d
        t_ideal = math.sqrt(4.0 * d / A)

        # Para J finito
        for J in [1.0, 5.0, 20.0, 100.0]:
            p = compute_profile(TrajectoryConfig("id_comp", d, 0.5, J))
            self.assertGreater(p.T, t_ideal)
            self.assertGreater(p.delta_t, 0.0)

        # Monotonía del tiempo respecto a J: a mayor J, menor tiempo T
        p1 = compute_profile(TrajectoryConfig("J1", d, 0.5, 1.0))
        p5 = compute_profile(TrajectoryConfig("J5", d, 0.5, 5.0))
        p20 = compute_profile(TrajectoryConfig("J20", d, 0.5, 20.0))
        p100 = compute_profile(TrajectoryConfig("J100", d, 0.5, 100.0))

        self.assertGreater(p1.T, p5.T)
        self.assertGreater(p5.T, p20.T)
        self.assertGreater(p20.T, p100.T)

        # Límite asintótico cuando J -> infinito: delta_t -> 0
        p_huge = compute_profile(TrajectoryConfig("J_huge", d, 0.5, 100000.0))
        self.assertAlmostEqual(p_huge.T, t_ideal, places=4)

    def test_units_and_scaling(self):
        """Verifica consistencia dimensional: el tiempo es invariante si se reescalan las unidades de longitud."""
        # Si cambiamos d [m] -> d*1000 [mm], A [m/s2] -> A*1000 [mm/s2], J [m/s3] -> J*1000 [mm/s3]
        scale = 1000.0  # de metros a milímetros
        d_m = 5.0
        A_m = 0.5 * self.g
        J_m = 20.0

        p_m = compute_profile(TrajectoryConfig("SI_m", d_m, 0.5, J_m))

        # En milímetros:
        d_mm = d_m * scale
        A_mm = A_m * scale
        J_mm = J_m * scale

        # d_crit reescalado: 2 * (A*scale)^3 / (J*scale)^2 = scale * (2*A^3/J^2)
        d_crit_mm = 2.0 * (A_mm**3) / (J_mm**2)
        self.assertAlmostEqual(d_crit_mm, p_m.d_crit * scale, places=7)

        # El tiempo T es puramente temporal ([T]), debe ser idéntico
        tj_mm = A_mm / J_mm
        ta_mm = (-3.0 * tj_mm + math.sqrt(tj_mm**2 + 4.0 * d_mm / A_mm)) / 2.0
        T_mm = 4.0 * tj_mm + 2.0 * ta_mm

        self.assertAlmostEqual(T_mm, p_m.T, places=10)
        self.assertAlmostEqual(tj_mm, p_m.tj, places=10)
        self.assertAlmostEqual(ta_mm, p_m.ta, places=10)


if __name__ == "__main__":
    unittest.main()
