#!/usr/bin/env python3
"""
test_respuestas.py - Suite de pruebas unitarias y de verificación numérica
para las respuestas de 1er y 2do orden y control de límites.

Verifica:
1. Valores iniciales, finales y derivadas (límites t -> 0, t -> inf, tau -> 0, tau -> inf).
2. Punto de inflexión y máxima tasa de cambio.
3. Precisión del solver de raíces (residuos < 1e-14 en t_10, t_50, t_90).
4. Monotonía estricta y acotamiento en [0, 1).
5. Invarianza de escala adimensional (u = t/tau).
6. Convergencia del integrador RK4 frente a la solución analítica exacta.
7. Control y comportamiento bajo limitación de tasa (rampas de ESC).

Autor: Antigravity (Entorno aislado)
Fecha: Noviembre 2026
"""

import math
import unittest
import sys
import os

# Asegurar importación del módulo de cálculo
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from comparar_respuestas import (
    y_first_order, dy_first_order, d2y_first_order,
    y_second_order, dy_second_order, d2y_second_order,
    time_first_order, time_second_order, solve_u_second_order,
    time_first_order_rate_limited, simulate_step_rate_limited, find_crossing_time,
    evaluate_limits, simulate_step_rk4
)

class TestAnalyticalLimitsAndProperties(unittest.TestCase):
    """Verificación de límites matemáticos y propiedades analíticas."""
    
    def setUp(self):
        self.taus = [0.08, 0.20, 0.50]
        
    def test_initial_values(self):
        """Verifica que ambas respuestas parten de reposo en t=0: y(0) = 0."""
        for tau in self.taus:
            self.assertEqual(y_first_order(0.0, tau), 0.0)
            self.assertEqual(y_second_order(0.0, tau), 0.0)
            
    def test_initial_derivatives(self):
        """Verifica el contraste fundamental de pendiente inicial en t=0+:
        - 1er orden: dy1/dt(0+) = 1/tau (arranque inmediato sin inercia).
        - 2do orden: dy2/dt(0+) = 0 (arranque suave con inercia continua)."""
        for tau in self.taus:
            self.assertAlmostEqual(dy_first_order(0.0, tau), 1.0 / tau, places=14)
            self.assertEqual(dy_second_order(0.0, tau), 0.0)
            
    def test_initial_curvature(self):
        """Verifica la segunda derivada inicial en t=0+:
        - 1er orden: d2y1/dt2(0+) = -1/tau^2 (cóncava hacia abajo desde el inicio).
        - 2do orden: d2y2/dt2(0+) = +1/tau^2 (convexa, aceleración de respuesta)."""
        for tau in self.taus:
            self.assertAlmostEqual(d2y_first_order(0.0, tau), -1.0 / (tau * tau), places=14)
            self.assertAlmostEqual(d2y_second_order(0.0, tau), 1.0 / (tau * tau), places=14)

    def test_asymptotic_limit_t_infinity(self):
        """Verifica que cuando t -> inf, ambas respuestas tienden asintóticamente a 1."""
        for tau in self.taus:
            # En t = 10 * tau: exp(-10) ~ 4.54e-5, evitando cancelación catastrófica de float64
            t_large = 10.0 * tau
            y1 = y_first_order(t_large, tau)
            y2 = y_second_order(t_large, tau)
            self.assertAlmostEqual(y1, 1.0, delta=1e-4)
            self.assertAlmostEqual(y2, 1.0, delta=1e-3)
            # El error remanente en 2do orden siempre es mayor que en 1er orden:
            err1 = 1.0 - y1
            err2 = 1.0 - y2
            self.assertGreater(err2, err1)
            # Teóricamente: err2 / err1 = (1 + t/tau) = 11.0
            self.assertAlmostEqual(err2 / err1, 1.0 + t_large / tau, places=5)
            
            # En t = 25 * tau, la respuesta es 1 dentro de 9 decimales
            t_very_large = 25.0 * tau
            self.assertAlmostEqual(y_first_order(t_very_large, tau), 1.0, places=9)
            self.assertAlmostEqual(y_second_order(t_very_large, tau), 1.0, places=9)

    def test_second_order_inflection_point(self):
        """Verifica que el 2do orden tiene punto de inflexión en t = tau:
        d2y2/dt2(tau) = 0, y el valor exacto es 1 - 2/e ~ 0.264241."""
        for tau in self.taus:
            # En t = tau, d2y2 = 0
            d2 = d2y_second_order(tau, tau)
            self.assertAlmostEqual(d2, 0.0, places=15)
            # Valor exacto: 1 - 2/e
            y_inflec = y_second_order(tau, tau)
            self.assertAlmostEqual(y_inflec, 1.0 - 2.0 / math.e, places=15)
            # Máxima pendiente en t = tau: dy/dt = 1 / (e * tau)
            dy_max = dy_second_order(tau, tau)
            self.assertAlmostEqual(dy_max, 1.0 / (math.e * tau), places=14)
            # Comprobación de máximo: en tau - delta y tau + delta la pendiente es menor
            delta = 0.01 * tau
            self.assertGreater(dy_max, dy_second_order(tau - delta, tau))
            self.assertGreater(dy_max, dy_second_order(tau + delta, tau))

    def test_limit_tau_zero_and_infinity(self):
        """Control de límites físicos para tau -> 0+ (actuador infinitamente rápido)
        y tau -> inf (actuador congelado)."""
        t = 0.1  # tiempo fijo positivo
        
        # tau -> 0+
        tau_fast = 1e-6
        self.assertAlmostEqual(y_first_order(t, tau_fast), 1.0, places=15)
        self.assertAlmostEqual(y_second_order(t, tau_fast), 1.0, places=15)
        
        # tau -> inf
        tau_slow = 1e6
        self.assertAlmostEqual(y_first_order(t, tau_slow), 0.0, places=6)
        self.assertAlmostEqual(y_second_order(t, tau_slow), 0.0, places=6)


class TestCharacteristicTimesAndAccuracy(unittest.TestCase):
    """Verificación de la exactitud numérica de los tiempos al 10%, 50% y 90%."""

    def setUp(self):
        self.taus = [0.08, 0.20, 0.50]
        self.percentages = [0.10, 0.50, 0.90]

    def test_first_order_exact_formula(self):
        """Verifica la fórmula analítica t = -tau * ln(1 - p) y residuales < 1e-15."""
        for tau in self.taus:
            for p in self.percentages:
                t = time_first_order(p, tau)
                val = y_first_order(t, tau)
                residual = abs(val - p)
                self.assertLess(residual, 1e-15, f"Residual excesivo en 1er orden p={p}, tau={tau}")

    def test_second_order_solver_residual(self):
        """Verifica que el método de Halley resuelve 1 - (1+t/tau)exp(-t/tau) = p
        con residuo inferior a 1e-14 para todos los casos."""
        for tau in self.taus:
            for p in self.percentages:
                t = time_second_order(p, tau)
                val = y_second_order(t, tau)
                residual = abs(val - p)
                self.assertLess(residual, 1e-14, f"Residual excesivo en 2do orden p={p}, tau={tau}")

    def test_known_analytical_values(self):
        """Verifica valores analíticos conocidos contra la teoría."""
        # 1er orden al 50%: t = tau * ln(2)
        u_50_1 = -math.log(0.5)
        self.assertAlmostEqual(u_50_1, math.log(2.0), places=15)
        
        # 1er orden al 90%: t = tau * ln(10)
        u_90_1 = -math.log(0.1)
        self.assertAlmostEqual(u_90_1, math.log(10.0), places=15)
        
        # 2do orden al 10%, 50%, 90%
        u_10_2 = solve_u_second_order(0.10)
        u_50_2 = solve_u_second_order(0.50)
        u_90_2 = solve_u_second_order(0.90)
        
        # Valores de referencia de alta precisión calculados por inversión
        self.assertAlmostEqual(u_10_2, 0.531811608390, places=10)
        self.assertAlmostEqual(u_50_2, 1.678346990017, places=10)
        self.assertAlmostEqual(u_90_2, 3.889720169867, places=10)


class TestUniversalDimensionlessScaling(unittest.TestCase):
    """Verificación de que u = t/tau es independiente de tau."""

    def test_scaling_invariance(self):
        """El tiempo normalizado u_p = t_p / tau debe ser estrictamente idéntico
        para cualquier valor de tau."""
        taus = [0.08, 0.20, 0.50, 1.0, 5.0]
        for p in [0.10, 0.50, 0.90]:
            # Primer orden
            u1_list = [time_first_order(p, tau) / tau for tau in taus]
            for u in u1_list[1:]:
                self.assertAlmostEqual(u, u1_list[0], places=14)
                
            # Segundo orden
            u2_list = [time_second_order(p, tau) / tau for tau in taus]
            for u in u2_list[1:]:
                self.assertAlmostEqual(u, u2_list[0], places=14)

    def test_relative_delay_factors(self):
        """Verifica los factores adimensionales universales de retardo de 2do orden vs 1er orden:
        - 10%: el retardo de arranque es ~5.0475 veces mayor.
        - 50%: el tiempo a mitad de camino es ~2.4213 veces mayor.
        - 90%: el tiempo al 90% es ~1.6893 veces mayor.
        - Subida 10%-90%: el tiempo de subida es ~1.5283 veces mayor."""
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


class TestMonotonicityAndOrdering(unittest.TestCase):
    """Verificación de propiedades de monotonicidad y orden temporal."""

    def test_strict_temporal_ordering(self):
        """Verifica t_10 < t_50 < t_90 para todos los modelos y tau."""
        for tau in [0.08, 0.20, 0.50]:
            t1_10 = time_first_order(0.10, tau)
            t1_50 = time_first_order(0.50, tau)
            t1_90 = time_first_order(0.90, tau)
            self.assertLess(t1_10, t1_50)
            self.assertLess(t1_50, t1_90)
            
            t2_10 = time_second_order(0.10, tau)
            t2_50 = time_second_order(0.50, tau)
            t2_90 = time_second_order(0.90, tau)
            self.assertLess(t2_10, t2_50)
            self.assertLess(t2_50, t2_90)

    def test_first_order_leads_second_order(self):
        """Verifica que para todo t > 0, y_1(t) > y_2(t), es decir,
        el segundo orden críticamente amortiguado SIEMPRE va retrasado
        respecto al primer orden con la misma tau."""
        for tau in [0.08, 0.20, 0.50]:
            for fraction in [0.01, 0.1, 0.5, 1.0, 2.0, 5.0]:
                t = fraction * tau
                y1 = y_first_order(t, tau)
                y2 = y_second_order(t, tau)
                self.assertGreater(y1, y2, f"Fallo de adelanto en t={t}, tau={tau}")


class TestNumericalRK4Convergence(unittest.TestCase):
    """Verificación de convergencia numérica de orden 4 con simulación Runge-Kutta."""

    def test_rk4_convergence_rate(self):
        """Verifica que el error global de RK4 decrece como O(dt^4)."""
        tau = 0.20
        t_eval = tau
        y_exact_1 = y_first_order(t_eval, tau)
        y_exact_2 = y_second_order(t_eval, tau)
        
        dt1 = 0.01
        dt2 = 0.005
        
        # Orden 1
        _, y_sim1_a = simulate_step_rk4(tau, 1, t_eval, dt1)
        _, y_sim1_b = simulate_step_rk4(tau, 1, t_eval, dt2)
        err1_a = abs(y_sim1_a[-1] - y_exact_1)
        err1_b = abs(y_sim1_b[-1] - y_exact_1)
        ratio1 = err1_a / err1_b
        # Para O(dt^4), al reducir el paso a la mitad el error se reduce en un factor ~16
        self.assertAlmostEqual(ratio1, 16.0, delta=0.5)
        
        # Orden 2
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
    """Verificación de límites de rampa y slew-rate (análisis NASA Weinstein et al. e INFORME.md)."""

    def setUp(self):
        self.tau = 0.08
        self.R = 50.0 / 21.0  # ~2.38095 s^-1 (supuesto en INFORME.md para 5 kg)

    def test_rate_limit_inactive_when_R_large(self):
        """Si la cota R >= 1/tau, el límite de rampa nunca se activa en 1er orden."""
        R_large = 1.0 / self.tau + 5.0
        for p in [0.10, 0.50, 0.90]:
            t_unlim = time_first_order(p, self.tau)
            t_lim = time_first_order_rate_limited(p, self.tau, R_large)
            self.assertAlmostEqual(t_lim, t_unlim, places=14)

    def test_rate_limit_pure_ramp_phase(self):
        """En régimen de rampa pura (p <= 1 - R*tau), t(p) = p / R exactamente."""
        y_sat = 1.0 - self.R * self.tau  # ~0.8095
        p = 0.10  # Está dentro del régimen saturado
        self.assertLess(p, y_sat)
        t_lim = time_first_order_rate_limited(p, self.tau, self.R)
        self.assertAlmostEqual(t_lim, p / self.R, places=14)

    def test_rate_limit_desaturation_continuity(self):
        """Verifica la continuidad exacta en el punto de desaturación p = 1 - R*tau."""
        y_sat = 1.0 - self.R * self.tau
        t_sat_expected = (1.0 - self.R * self.tau) / self.R
        
        # Evaluando justo antes y justo después de y_sat
        eps = 1e-7
        t_before = time_first_order_rate_limited(y_sat - eps, self.tau, self.R)
        t_after = time_first_order_rate_limited(y_sat + eps, self.tau, self.R)
        
        self.assertAlmostEqual(t_before, t_sat_expected, places=5)
        self.assertAlmostEqual(t_after, t_sat_expected, places=5)
        self.assertAlmostEqual(t_before, t_after, places=6)

    def test_rate_limited_matches_simulation(self):
        """Verifica que la fórmula analítica de 1er orden con rampa coincide
        con la integración numérica en el tiempo."""
        t_sim, y_sim = simulate_step_rate_limited(self.tau, 1, self.R, t_final=1.0, dt=1e-5)
        for p in [0.10, 0.50, 0.90]:
            t_ana = time_first_order_rate_limited(p, self.tau, self.R)
            t_num = find_crossing_time(t_sim, y_sim, p)
            self.assertIsNotNone(t_num)
            self.assertAlmostEqual(t_ana, t_num, places=4)

    def test_second_order_rate_limit_thresholds(self):
        """Para 2do orden, la tasa máxima natural es 1/(e*tau).
        - Si R < 1/(e*tau), hay retardo adicional por rampa.
        - Si R >= 1/(e*tau), no hay afectación de la respuesta."""
        # Caso 1: tau = 0.08 s => 1/(e*tau) ~ 4.60 s^-1 > R (2.38 s^-1) => SATURA
        t_sim1, y_sim1_unlim = simulate_step_rate_limited(0.08, 2, None, t_final=1.0, dt=1e-4)
        t_sim1, y_sim1_lim = simulate_step_rate_limited(0.08, 2, self.R, t_final=1.0, dt=1e-4)
        t90_unlim1 = find_crossing_time(t_sim1, y_sim1_unlim, 0.90)
        t90_lim1 = find_crossing_time(t_sim1, y_sim1_lim, 0.90)
        self.assertGreater(t90_lim1, t90_unlim1)  # Se retrasa
        
        # Caso 2: tau = 0.50 s => 1/(e*tau) ~ 0.74 s^-1 < R (2.38 s^-1) => NO SATURA
        t_sim2, y_sim2_unlim = simulate_step_rate_limited(0.50, 2, None, t_final=3.0, dt=1e-4)
        t_sim2, y_sim2_lim = simulate_step_rate_limited(0.50, 2, self.R, t_final=3.0, dt=1e-4)
        t90_unlim2 = find_crossing_time(t_sim2, y_sim2_unlim, 0.90)
        t90_lim2 = find_crossing_time(t_sim2, y_sim2_lim, 0.90)
        self.assertAlmostEqual(t90_lim2, t90_unlim2, places=3)  # Prácticamente idéntico


if __name__ == "__main__":
    unittest.main()
