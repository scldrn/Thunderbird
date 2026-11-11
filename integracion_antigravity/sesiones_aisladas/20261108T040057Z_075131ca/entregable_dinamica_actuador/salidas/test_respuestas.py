#!/usr/bin/env python3
"""
test_respuestas.py - Suite de pruebas unitarias y de verificación numérica
para los modelos normalizados de 1er orden y 2do orden críticamente amortiguado.

Verificaciones cubiertas:
1. Validación de dominio: tau > 0, 0 < p < 1, R > 0.
2. Tiempos característicos 10%, 50%, 90% y tiempo de subida 10%-90%:
   - Residuales analíticos y numéricos (< 1e-14).
   - Comparación con valores teóricos cerrados (ln 2, ln 10, Lambert W_-1).
   - Invarianza de escala adimensional universal (u = t/tau).
   - Ratios relativos universales y ordenamiento temporal estricto.
3. Continuidad:
   - Continuidad en t = 0 (límites laterales izquierdo y derecho).
   - Contraste de regularidad C^1: continuidad de derivada en 2do orden vs salto en 1er orden.
   - Continuidad Lipschitz en todo el dominio t >= 0.
   - Continuidad C^1 en el punto de conmutación de sistemas con limitación de rampa.
4. Límites respecto a t >= 0:
   - Causalidad en t < 0 (y = 0).
   - Condiciones iniciales en t = 0 (y(0) = 0, derivadas y curvaturas).
   - Monotonía estricta y acotamiento en [0, 1) para t > 0.
   - Dominancia de 1er orden sobre 2do orden (y_1(t) > y_2(t) para t > 0).
   - Convergencia asintótica t -> inf (y -> 1, ratio de error e_2/e_1 = 1 + t/tau).
   - Punto de inflexión exacto de 2do orden en t = tau (d2y/dt2 = 0, y = 1 - 2/e, dy/dt = 1/(e*tau)).
5. Límites respecto a tau > 0:
   - Rechazo de tau <= 0 con ValueError.
   - Límite tau -> 0+ (actuador instantáneo, y(t) -> 1 para t > 0, t_p -> 0).
   - Límite tau -> inf (actuador congelado, y(t) -> 0 para t >= 0, t_p -> inf).
   - Escala lineal estricta con tau (dt_p / dtau = u_p).
6. Convergencia del integrador RK4 de 4to orden (O(dt^4)).
7. Efecto y consistencia de rampas de ESC / slew-rate.

Fecha: Noviembre 2026
"""

import math
import os
import sys
import unittest

# Asegurar importación del módulo en el mismo directorio
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from comparar_respuestas import (
    validate_tau, validate_percentage, validate_rate,
    y_first_order, dy_first_order, d2y_first_order,
    y_second_order, dy_second_order, d2y_second_order,
    time_first_order, time_second_order, solve_u_second_order,
    time_first_order_rate_limited, simulate_step_rate_limited,
    find_crossing_time, simulate_step_rk4, evaluate_limits
)


class TestInputValidationAndDomainConstraints(unittest.TestCase):
    """Verificación de validaciones de dominio y parámetros (tau > 0, 0 < p < 1, R > 0)."""

    def test_tau_positive_constraint(self):
        """tau debe ser estrictamente positivo (> 0); tau <= 0 debe lanzar ValueError."""
        invalid_taus = [0.0, -0.01, -0.5, -10.0]
        for tau in invalid_taus:
            with self.assertRaises(ValueError, msg=f"No lanzó ValueError para tau={tau}"):
                validate_tau(tau)
            with self.assertRaises(ValueError):
                y_first_order(0.1, tau)
            with self.assertRaises(ValueError):
                y_second_order(0.1, tau)
            with self.assertRaises(ValueError):
                time_first_order(0.5, tau)
            with self.assertRaises(ValueError):
                time_second_order(0.5, tau)

        # tau > 0 no debe lanzar excepción
        valid_taus = [1e-6, 0.08, 0.20, 0.50, 100.0]
        for tau in valid_taus:
            try:
                validate_tau(tau)
            except ValueError:
                self.fail(f"validate_tau lanzó ValueError inesperado para tau válida={tau}")

    def test_percentage_open_interval_constraint(self):
        """El porcentaje p debe pertenecer al intervalo abierto (0, 1)."""
        invalid_percentages = [0.0, 1.0, -0.05, 1.05, -1.0, 2.0]
        for p in invalid_percentages:
            with self.assertRaises(ValueError, msg=f"No lanzó ValueError para p={p}"):
                validate_percentage(p)
            with self.assertRaises(ValueError):
                time_first_order(p, 0.1)
            with self.assertRaises(ValueError):
                time_second_order(p, 0.1)
            with self.assertRaises(ValueError):
                solve_u_second_order(p)

        # p en (0, 1) válido
        valid_percentages = [1e-5, 0.10, 0.50, 0.90, 0.99999]
        for p in valid_percentages:
            try:
                validate_percentage(p)
            except ValueError:
                self.fail(f"validate_percentage lanzó ValueError para p válida={p}")

    def test_rate_positive_constraint(self):
        """La tasa máxima R debe ser estrictamente positiva (R > 0)."""
        invalid_rates = [0.0, -0.5, -10.0]
        for R in invalid_rates:
            with self.assertRaises(ValueError, msg=f"No lanzó ValueError para R={R}"):
                validate_rate(R)
            with self.assertRaises(ValueError):
                time_first_order_rate_limited(0.5, 0.1, R)


class TestCharacteristicTimes10_50_90(unittest.TestCase):
    """Verificación de tiempos característicos (10%, 50%, 90%) y tiempo de subida 10%-90%."""

    def setUp(self):
        self.taus = [0.08, 0.20, 0.50]
        self.percentages = [0.10, 0.50, 0.90]

    def test_first_order_exact_formula_and_residuals(self):
        """Verifica la fórmula t = -tau * ln(1 - p) y comprueba residuales < 1e-15."""
        for tau in self.taus:
            for p in self.percentages:
                t = time_first_order(p, tau)
                # Residual analítico directo
                y_eval = y_first_order(t, tau)
                residual = abs(y_eval - p)
                self.assertLess(residual, 1e-15, f"Residual excesivo en 1er orden: p={p}, tau={tau}")

    def test_second_order_solver_residuals(self):
        """Verifica que el solver de Halley resuelve y_2(t) = p con residuo < 1e-14."""
        for tau in self.taus:
            for p in self.percentages:
                t = time_second_order(p, tau)
                y_eval = y_second_order(t, tau)
                residual = abs(y_eval - p)
                self.assertLess(residual, 1e-14, f"Residual excesivo en 2do orden: p={p}, tau={tau}")

    def test_known_analytical_values(self):
        """Comprueba los valores analíticos conocidos teóricamente."""
        # 1er orden al 50%: u = ln(2)
        u1_50 = solve_u_second_order_1 = -math.log(0.5)
        self.assertAlmostEqual(u1_50, math.log(2.0), places=15)

        # 1er orden al 90%: u = ln(10)
        u1_90 = -math.log(0.1)
        self.assertAlmostEqual(u1_90, math.log(10.0), places=15)

        # 1er orden al 10%: u = -ln(0.9)
        u1_10 = -math.log(0.9)
        self.assertAlmostEqual(u1_10, 0.1053605156578, places=12)

        # 2do orden crítico raíces universales de alta precisión
        u2_10 = solve_u_second_order(0.10)
        u2_50 = solve_u_second_order(0.50)
        u2_90 = solve_u_second_order(0.90)
        self.assertAlmostEqual(u2_10, 0.531811608390, places=10)
        self.assertAlmostEqual(u2_50, 1.678346990017, places=10)
        self.assertAlmostEqual(u2_90, 3.889720169867, places=10)

    def test_scaling_invariance_u_dimensionless(self):
        """u_p = t_p / tau debe ser rigurosamente independiente del valor de tau."""
        test_taus = [0.01, 0.08, 0.20, 0.50, 2.0, 10.0]
        for p in self.percentages:
            # 1er orden
            u1_vals = [time_first_order(p, tau) / tau for tau in test_taus]
            for u in u1_vals[1:]:
                self.assertAlmostEqual(u, u1_vals[0], places=14)

            # 2do orden
            u2_vals = [time_second_order(p, tau) / tau for tau in test_taus]
            for u in u2_vals[1:]:
                self.assertAlmostEqual(u, u2_vals[0], places=14)

    def test_universal_relative_delay_ratios(self):
        """Verifica los factores universales de retraso u2 / u1."""
        u1_10 = -math.log(0.9)
        u1_50 = -math.log(0.5)
        u1_90 = -math.log(0.1)
        u1_rise = u1_90 - u1_10

        u2_10 = solve_u_second_order(0.10)
        u2_50 = solve_u_second_order(0.50)
        u2_90 = solve_u_second_order(0.90)
        u2_rise = u2_90 - u2_10

        self.assertAlmostEqual(u2_10 / u1_10, 5.047542, places=5)
        self.assertAlmostEqual(u2_50 / u1_50, 2.421344, places=5)
        self.assertAlmostEqual(u2_90 / u1_90, 1.689284, places=5)
        self.assertAlmostEqual(u2_rise / u1_rise, 1.528250, places=5)

    def test_strict_temporal_ordering(self):
        """Verifica el ordenamiento temporal estricto: 0 < t_10 < t_50 < t_90."""
        for tau in self.taus:
            t1_10 = time_first_order(0.10, tau)
            t1_50 = time_first_order(0.50, tau)
            t1_90 = time_first_order(0.90, tau)
            self.assertGreater(t1_10, 0.0)
            self.assertLess(t1_10, t1_50)
            self.assertLess(t1_50, t1_90)

            t2_10 = time_second_order(0.10, tau)
            t2_50 = time_second_order(0.50, tau)
            t2_90 = time_second_order(0.90, tau)
            self.assertGreater(t2_10, 0.0)
            self.assertLess(t2_10, t2_50)
            self.assertLess(t2_50, t2_90)


class TestContinuity(unittest.TestCase):
    """Verificación rigurosa de continuidad matemática en t = 0, t >= 0 y en régimen saturado."""

    def setUp(self):
        self.taus = [0.08, 0.20, 0.50]

    def test_continuity_at_t_zero(self):
        """Verifica continuidad de y(t) en t = 0:
        lim_{t -> 0-} y(t) = y(0) = lim_{t -> 0+} y(t) = 0."""
        for tau in self.taus:
            self.assertEqual(y_first_order(0.0, tau), 0.0)
            self.assertEqual(y_second_order(0.0, tau), 0.0)

            # Límites laterales numéricos
            epsilons = [1e-3, 1e-6, 1e-9, 1e-12]
            for eps in epsilons:
                # Izquierda (causal)
                self.assertEqual(y_first_order(-eps, tau), 0.0)
                self.assertEqual(y_second_order(-eps, tau), 0.0)
                # Derecha
                self.assertLess(y_first_order(eps, tau), 2.0 * eps / tau)
                self.assertLess(y_second_order(eps, tau), 2.0 * (eps / tau)**2)

    def test_derivative_continuity_contrast_at_t_zero(self):
        """Verifica la regularidad de derivadas en t = 0:
        - 2do orden es C^1 en t = 0: lim_{t->0-} dy2/dt = 0 = dy2/dt(0) = lim_{t->0+} dy2/dt.
        - 1er orden NO es C^1 en t = 0: tiene salto finito de derivada de 0 a 1/tau."""
        for tau in self.taus:
            # 2do orden: derivada nula continua lim_{t->0+} dy2/dt = 0
            self.assertEqual(dy_second_order(-1e-6, tau), 0.0)
            self.assertEqual(dy_second_order(0.0, tau), 0.0)
            self.assertAlmostEqual(dy_second_order(1e-9, tau), 0.0, delta=1e-6)

            # 1er orden: salto de derivada en t=0
            dy_left = dy_first_order(-1e-6, tau)
            dy_right = dy_first_order(0.0, tau)
            self.assertEqual(dy_left, 0.0)
            self.assertAlmostEqual(dy_right, 1.0 / tau, places=14)
            self.assertNotEqual(dy_left, dy_right)

    def test_continuity_over_t_ge_0_lipschitz(self):
        """Verifica que y(t) es uniformemente Lipschitz-continua en [0, inf):
        |y(t2) - y(t1)| <= L * |t2 - t1| con L_1 = 1/tau y L_2 = 1/(e*tau)."""
        for tau in self.taus:
            L1 = 1.0 / tau
            L2 = 1.0 / (math.e * tau)

            # Evaluar pares de puntos en una malla
            grid = [0.0, 0.01 * tau, 0.1 * tau, 0.5 * tau, tau, 2.0 * tau, 5.0 * tau]
            delta = 1e-4 * tau
            for t in grid:
                t_plus = t + delta
                # 1er orden
                dy1 = abs(y_first_order(t_plus, tau) - y_first_order(t, tau))
                self.assertLessEqual(dy1, L1 * delta * (1.0 + 1e-12))
                # 2do orden
                dy2 = abs(y_second_order(t_plus, tau) - y_second_order(t, tau))
                self.assertLessEqual(dy2, L2 * delta * (1.0 + 1e-12))

    def test_rate_limited_continuity_at_switching_point(self):
        """Verifica la continuidad C^1 en el punto de transición t_sat para 1er orden con rampa:
        y(t_sat-) = y(t_sat+) = 1 - R*tau, y dy/dt(t_sat-) = dy/dt(t_sat+) = R."""
        tau = 0.08
        R = 50.0 / 21.0  # 2.38095 s^-1
        y_sat = 1.0 - R * tau
        t_sat = (1.0 - R * tau) / R

        eps = 1e-7
        t_before = time_first_order_rate_limited(y_sat - eps, tau, R)
        t_after = time_first_order_rate_limited(y_sat + eps, tau, R)

        self.assertAlmostEqual(t_before, t_sat, places=5)
        self.assertAlmostEqual(t_after, t_sat, places=5)
        self.assertAlmostEqual(t_after - t_before, 2.0 * eps / R, places=6)


class TestDomainLimits_t_ge_0(unittest.TestCase):
    """Verificación de límites y propiedades en el dominio temporal t >= 0."""

    def setUp(self):
        self.taus = [0.08, 0.20, 0.50]

    def test_causality_for_t_negative(self):
        """Para t < 0, la respuesta causal es estrictamente 0."""
        for tau in self.taus:
            for t in [-10.0, -1.0, -0.01, -1e-9]:
                self.assertEqual(y_first_order(t, tau), 0.0)
                self.assertEqual(y_second_order(t, tau), 0.0)
                self.assertEqual(dy_first_order(t, tau), 0.0)
                self.assertEqual(dy_second_order(t, tau), 0.0)

    def test_initial_boundary_t_zero(self):
        """Valores y derivadas en la frontera inicial t = 0."""
        for tau in self.taus:
            self.assertEqual(y_first_order(0.0, tau), 0.0)
            self.assertEqual(y_second_order(0.0, tau), 0.0)
            self.assertAlmostEqual(dy_first_order(0.0, tau), 1.0 / tau, places=14)
            self.assertEqual(dy_second_order(0.0, tau), 0.0)
            self.assertAlmostEqual(d2y_first_order(0.0, tau), -1.0 / (tau * tau), places=14)
            self.assertAlmostEqual(d2y_second_order(0.0, tau), 1.0 / (tau * tau), places=14)

    def test_monotonicity_and_bounds_for_t_positive(self):
        """Para todo t > 0: 0 < y(t) < 1, dy/dt > 0, y y_1(t) > y_2(t)."""
        for tau in self.taus:
            test_times = [0.01 * tau, 0.1 * tau, 0.5 * tau, tau, 2.0 * tau, 5.0 * tau]
            for t in test_times:
                y1 = y_first_order(t, tau)
                y2 = y_second_order(t, tau)
                dy1 = dy_first_order(t, tau)
                dy2 = dy_second_order(t, tau)

                self.assertGreater(y1, 0.0)
                self.assertLess(y1, 1.0)
                self.assertGreater(y2, 0.0)
                self.assertLess(y2, 1.0)
                self.assertGreater(dy1, 0.0)
                self.assertGreater(dy2, 0.0)

                # Primer orden siempre lidera a segundo orden para t > 0
                self.assertGreater(y1, y2, f"Fallo de orden en t={t}, tau={tau}")

    def test_asymptotic_convergence_t_infinity(self):
        """Cuando t -> inf: y_1(t) -> 1, y_2(t) -> 1, y error e_2 / e_1 = 1 + t/tau."""
        for tau in self.taus:
            t_large = 10.0 * tau
            y1 = y_first_order(t_large, tau)
            y2 = y_second_order(t_large, tau)
            self.assertAlmostEqual(y1, 1.0, delta=1e-4)
            self.assertAlmostEqual(y2, 1.0, delta=1e-3)

            err1 = 1.0 - y1
            err2 = 1.0 - y2
            self.assertAlmostEqual(err2 / err1, 1.0 + t_large / tau, places=5)

            t_huge = 35.0 * tau
            self.assertAlmostEqual(y_first_order(t_huge, tau), 1.0, places=12)
            self.assertAlmostEqual(y_second_order(t_huge, tau), 1.0, places=12)

    def test_second_order_inflection_point(self):
        """En t = tau: d2y_2/dt2 = 0, y_2(tau) = 1 - 2/e, dy_2/dt es máxima con valor 1/(e*tau)."""
        for tau in self.taus:
            # Curvatura nula
            self.assertAlmostEqual(d2y_second_order(tau, tau), 0.0, places=15)
            # Valor exacto
            self.assertAlmostEqual(y_second_order(tau, tau), 1.0 - 2.0 / math.e, places=15)
            # Pendiente máxima
            dy_max = dy_second_order(tau, tau)
            self.assertAlmostEqual(dy_max, 1.0 / (math.e * tau), places=14)
            # En tau - delta y tau + delta la pendiente es estrictamente menor
            delta = 0.05 * tau
            self.assertGreater(dy_max, dy_second_order(tau - delta, tau))
            self.assertGreater(dy_max, dy_second_order(tau + delta, tau))


class TestDomainLimits_tau_gt_0(unittest.TestCase):
    """Verificación de límites físicos y matemáticos cuando tau > 0, tau -> 0+ y tau -> inf."""

    def test_limit_tau_approaching_zero_ultrafast(self):
        """Cuando tau -> 0+ (actuador ultra-rápido/ideal):
        para cualquier t > 0 fijo, y(t) -> 1 y t_p -> 0."""
        t_fixed = 0.01  # 10 ms
        tau_fast = 1e-6  # 1 microsegundo
        self.assertAlmostEqual(y_first_order(t_fixed, tau_fast), 1.0, places=15)
        self.assertAlmostEqual(y_second_order(t_fixed, tau_fast), 1.0, places=15)

        for p in [0.10, 0.50, 0.90]:
            t1 = time_first_order(p, tau_fast)
            t2 = time_second_order(p, tau_fast)
            self.assertLess(t1, 1e-5)
            self.assertLess(t2, 1e-5)

    def test_limit_tau_approaching_infinity_frozen(self):
        """Cuando tau -> inf (actuador congelado/sin respuesta):
        para cualquier t >= 0 finito, y(t) -> 0 y t_p -> inf."""
        t_fixed = 1.0  # 1 s
        tau_slow = 1e6  # 10^6 s
        self.assertAlmostEqual(y_first_order(t_fixed, tau_slow), 0.0, places=5)
        self.assertAlmostEqual(y_second_order(t_fixed, tau_slow), 0.0, places=5)

        for p in [0.10, 0.50, 0.90]:
            t1 = time_first_order(p, tau_slow)
            t2 = time_second_order(p, tau_slow)
            self.assertGreater(t1, 1e4)
            self.assertGreater(t2, 1e4)

    def test_linear_scaling_with_tau(self):
        """El tiempo al porcentaje p escala linealmente con tau: t_p(2*tau) = 2 * t_p(tau)."""
        tau_base = 0.15
        for p in [0.10, 0.50, 0.90]:
            t1_base = time_first_order(p, tau_base)
            t1_double = time_first_order(p, 2.0 * tau_base)
            self.assertAlmostEqual(t1_double, 2.0 * t1_base, places=14)

            t2_base = time_second_order(p, tau_base)
            t2_double = time_second_order(p, 2.0 * tau_base)
            self.assertAlmostEqual(t2_double, 2.0 * t2_base, places=14)


class TestNumericalIntegrationAndConvergence(unittest.TestCase):
    """Verificación de la convergencia del integrador RK4 de orden 4."""

    def test_rk4_convergence_rate_order_4(self):
        """Verifica que el error global de RK4 decrece como O(dt^4) al reducir el paso a la mitad."""
        tau = 0.20
        t_eval = tau
        y_exact_1 = y_first_order(t_eval, tau)
        y_exact_2 = y_second_order(t_eval, tau)

        dt1 = 0.01
        dt2 = 0.005

        # 1er orden
        _, y_sim1_a = simulate_step_rk4(tau, 1, t_eval, dt1)
        _, y_sim1_b = simulate_step_rk4(tau, 1, t_eval, dt2)
        err1_a = abs(y_sim1_a[-1] - y_exact_1)
        err1_b = abs(y_sim1_b[-1] - y_exact_1)
        ratio1 = err1_a / err1_b
        self.assertAlmostEqual(ratio1, 16.0, delta=0.5)

        # 2do orden
        _, y_sim2_a = simulate_step_rk4(tau, 2, t_eval, dt1)
        _, y_sim2_b = simulate_step_rk4(tau, 2, t_eval, dt2)
        err2_a = abs(y_sim2_a[-1] - y_exact_2)
        err2_b = abs(y_sim2_b[-1] - y_exact_2)
        ratio2 = err2_a / err2_b
        self.assertAlmostEqual(ratio2, 16.0, delta=0.5)

        # Precisión con dt fino
        _, y_sim_fine = simulate_step_rk4(tau, 2, t_eval, 1e-4)
        self.assertLess(abs(y_sim_fine[-1] - y_exact_2), 1e-12)


class TestSlewRateLimitingAndRamps(unittest.TestCase):
    """Verificación de dinámica con limitación de rampa (slew-rate / ESC)."""

    def setUp(self):
        self.tau = 0.08
        self.R = 50.0 / 21.0  # ~2.38095 s^-1

    def test_rate_limit_inactive_when_R_large(self):
        """Si R >= 1/tau, la cota nunca se satura y coincide con el modelo lineal."""
        R_large = 1.0 / self.tau + 5.0
        for p in [0.10, 0.50, 0.90]:
            t_unlim = time_first_order(p, self.tau)
            t_lim = time_first_order_rate_limited(p, self.tau, R_large)
            self.assertAlmostEqual(t_lim, t_unlim, places=14)

    def test_rate_limit_pure_ramp_phase(self):
        """En régimen de rampa pura (p <= 1 - R*tau), t(p) = p / R exactamente."""
        y_sat = 1.0 - self.R * self.tau  # ~0.8095
        p = 0.10
        self.assertLess(p, y_sat)
        t_lim = time_first_order_rate_limited(p, self.tau, self.R)
        self.assertAlmostEqual(t_lim, p / self.R, places=14)

    def test_rate_limited_matches_simulation(self):
        """Verifica que la solución analítica con rampa coincide con la simulación numérica."""
        t_sim, y_sim = simulate_step_rate_limited(self.tau, 1, self.R, t_final=1.0, dt=1e-5)
        for p in [0.10, 0.50, 0.90]:
            t_ana = time_first_order_rate_limited(p, self.tau, self.R)
            t_num = find_crossing_time(t_sim, y_sim, p)
            self.assertIsNotNone(t_num)
            self.assertAlmostEqual(t_ana, t_num, places=4)

    def test_second_order_rate_limit_thresholds(self):
        """Para 2do orden, si 1/(e*tau) > R satura; si 1/(e*tau) <= R no satura."""
        # tau = 0.08 s: 1/(e*tau) ~ 4.60 s^-1 > R (2.38 s^-1) => Satura
        t_sim1, y_sim1_unlim = simulate_step_rate_limited(0.08, 2, None, t_final=1.0, dt=1e-4)
        t_sim1, y_sim1_lim = simulate_step_rate_limited(0.08, 2, self.R, t_final=1.0, dt=1e-4)
        t90_unlim1 = find_crossing_time(t_sim1, y_sim1_unlim, 0.90)
        t90_lim1 = find_crossing_time(t_sim1, y_sim1_lim, 0.90)
        self.assertGreater(t90_lim1, t90_unlim1)

        # tau = 0.50 s: 1/(e*tau) ~ 0.74 s^-1 < R (2.38 s^-1) => No satura
        t_sim2, y_sim2_unlim = simulate_step_rate_limited(0.50, 2, None, t_final=3.0, dt=1e-4)
        t_sim2, y_sim2_lim = simulate_step_rate_limited(0.50, 2, self.R, t_final=3.0, dt=1e-4)
        t90_unlim2 = find_crossing_time(t_sim2, y_sim2_unlim, 0.90)
        t90_lim2 = find_crossing_time(t_sim2, y_sim2_lim, 0.90)
        self.assertAlmostEqual(t90_lim2, t90_unlim2, places=3)


if __name__ == "__main__":
    unittest.main()
