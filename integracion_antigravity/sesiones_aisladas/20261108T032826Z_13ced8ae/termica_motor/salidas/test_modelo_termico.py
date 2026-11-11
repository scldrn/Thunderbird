#!/usr/bin/env python3
"""
Suite de Pruebas Unitarias y Analíticas para el Modelo Térmico Concentrado
==========================================================================

Verifica rigurosamente:
1. Condiciones de contorno e iniciales (T(0) = Tamb, dT/dt(0) = P/C).
2. Cumplimiento idéntico de la EDO gobernante: C dT/dt + (T - Tamb)/R - P = 0.
3. Límites asintóticos y tiempos característicos (t -> inf, t = tau).
4. Monotonía y concavidad física de la trayectoria térmica.
5. Inversión analítica exacta del tiempo de llegada a temperatura objetivo.
6. Convergencia de integración numérica RK4 frente a solución analítica.
7. Coherencia de los 27 casos de la matriz paramétrica (C, R, t).
8. Consistencia de la potencia disipada con el informe C01/C02 (74.2 W).
9. Integridad del archivo CSV de resultados exportados.
"""

import unittest
import math
import os
import sys
import csv

# Asegurar que el directorio salidas/ esté en sys.path para importaciones relativas y absolutas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from modelo_termico import (
        LumpedThermalModel,
        run_parametric_study,
        export_to_csv
    )
except ImportError:
    from salidas.modelo_termico import (
        LumpedThermalModel,
        run_parametric_study,
        export_to_csv
    )


class TestLumpedThermalModel(unittest.TestCase):
    """Pruebas analíticas y físicas del modelo térmico concentrado."""

    def setUp(self):
        self.C_list = [10.0, 50.0, 100.0]
        self.R_list = [1.0, 3.0, 10.0]
        self.t_list = [10.0, 30.0, 120.0]
        self.P_loss = 74.2
        self.T_amb = 25.0
        self.T_thresh = 80.0

    def test_initial_condition(self):
        """Verifica que en t=0 la temperatura es exactamente T_amb y delta_T es 0."""
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                self.assertAlmostEqual(model.temperature(0.0), self.T_amb, places=9)
                self.assertAlmostEqual(model.delta_temperature(0.0), 0.0, places=9)

    def test_initial_heating_rate(self):
        """Verifica que la tasa inicial de calentamiento es exactamente P_loss / C."""
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                expected_rate = self.P_loss / C
                self.assertAlmostEqual(model.initial_dT_dt, expected_rate, places=9)
                self.assertAlmostEqual(model.dT_dt(0.0), expected_rate, places=9)

    def test_asymptotic_limit(self):
        """Verifica que para tiempos muy largos (t >> tau), T(t) converge asintóticamente a T_ss."""
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                t_long = 25.0 * model.tau  # 25 constantes de tiempo
                expected_T_ss = self.T_amb + R * self.P_loss
                self.assertAlmostEqual(model.temperature(t_long), expected_T_ss, places=6)
                self.assertAlmostEqual(model.T_ss, expected_T_ss, places=9)

    def test_characteristic_time_constant(self):
        """Verifica que en t = tau, la sobretemperatura alcanza exactamente el 63.212% del régimen permanente."""
        one_minus_inv_e = 1.0 - math.exp(-1.0)  # ~0.6321205588
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                dT_at_tau = model.delta_temperature(model.tau)
                fraction = dT_at_tau / model.delta_T_ss
                self.assertAlmostEqual(fraction, one_minus_inv_e, places=9)

    def test_governing_ode_identity(self):
        """
        Verifica analíticamente que la solución satisface de forma idéntica la EDO:
            C * (dT/dt) + (T - T_amb)/R - P_loss == 0
        en múltiples instantes de tiempo.
        """
        times_to_check = [0.0, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                for t in times_to_check:
                    T_val = model.temperature(t)
                    rate_val = model.dT_dt(t)
                    residual = C * rate_val + (T_val - self.T_amb) / R - self.P_loss
                    self.assertAlmostEqual(residual, 0.0, places=9,
                                           msg=f"EDO no satisfecha en t={t} para C={C}, R={R}: residuo={residual}")

    def test_monotonicity_and_concavity(self):
        """
        Verifica que:
        - dT/dt > 0 para todo t >= 0 (calentamiento estrictamente monotónico creciente).
        - dT/dt decrece con t (concavidad negativa d^2T/dt^2 < 0).
        """
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                prev_T = self.T_amb
                prev_rate = model.initial_dT_dt
                for t in [1.0, 5.0, 10.0, 30.0, 60.0, 120.0]:
                    curr_T = model.temperature(t)
                    curr_rate = model.dT_dt(t)
                    self.assertGreater(curr_T, prev_T, msg="La temperatura debe ser estrictamente creciente")
                    self.assertGreater(curr_rate, 0.0, msg="La tasa de calentamiento debe ser estrictamente positiva")
                    self.assertLess(curr_rate, prev_rate, msg="La tasa de calentamiento debe ser monótonamente decreciente")
                    prev_T = curr_T
                    prev_rate = curr_rate

    def test_time_to_temperature_inversion(self):
        """
        Verifica la relación de inversión analítica:
            T(time_to_temperature(T_target)) == T_target
        para varias temperaturas intermedias dentro del rango alcanzable.
        """
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                # Seleccionar temperaturas intermedias entre T_amb y T_ss
                for frac in [0.1, 0.25, 0.5, 0.75, 0.9]:
                    T_target = self.T_amb + frac * model.delta_T_ss
                    t_reach = model.time_to_temperature(T_target)
                    self.assertIsNotNone(t_reach)
                    T_eval = model.temperature(t_reach)
                    self.assertAlmostEqual(T_eval, T_target, places=8)

    def test_unreachable_temperature(self):
        """Verifica que una temperatura superior o igual al régimen permanente devuelve None."""
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                T_unreachable = model.T_ss + 10.0
                self.assertIsNone(model.time_to_temperature(T_unreachable))
                self.assertIsNone(model.time_to_temperature(model.T_ss))

    def test_threshold_80C_specific_values(self):
        """
        Verifica los tiempos analíticos exactos para alcanzar el umbral de 80.0 °C:
            t_80 = - tau * ln(1 - 55 / (R * P_loss))
        Dado que R * P_loss >= 74.2 > 55 K en todos los casos evaluados (R in {1, 3, 10}),
        el umbral de 80 °C es siempre alcanzable en régimen permanente.
        """
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                t_80 = model.time_to_temperature(self.T_thresh)
                self.assertIsNotNone(t_80)
                # Verificación analítica directa
                expected_t_80 = - (R * C) * math.log(1.0 - 55.0 / (R * self.P_loss))
                self.assertAlmostEqual(t_80, expected_t_80, places=9)
                self.assertAlmostEqual(model.temperature(t_80), self.T_thresh, places=8)

    def test_rk4_numerical_integration_convergence(self):
        """
        Compara la integración numérica RK4 (dt=0.005 s) con la solución analítica
        exacta en todos los puntos de la matriz. El error absoluto debe ser < 1e-5 K.
        """
        for C in self.C_list:
            for R in self.R_list:
                model = LumpedThermalModel(C=C, R=R, P_loss=self.P_loss, T_amb=self.T_amb)
                rk4_dict = model.solve_rk4(self.t_list, dt=0.005)
                for t in self.t_list:
                    T_exact = model.temperature(t)
                    T_num = rk4_dict[t]
                    error = abs(T_exact - T_num)
                    self.assertLess(error, 1e-5,
                                    msg=f"Discrepancia RK4 excesiva en t={t} para C={C}, R={R}: error={error}")

    def test_c02_loss_value_consistency(self):
        """
        Verifica la trazabilidad del valor P_loss = 74.2 W con el informe C02:
            - Potencia de eje requerida C01/C02: 668 W
            - Eficiencia eléctrica conjunta supuesta: 0.90
            - Potencia eléctrica total: 668 / 0.90 = 742.22 W
            - Pérdida térmica conjunta: 742.22 - 668 = 74.22 W ~ 74.2 W
        """
        P_shaft_c02 = 668.0
        eta_c02 = 0.90
        P_loss_derived = P_shaft_c02 * (1.0 - eta_c02) / eta_c02
        self.assertAlmostEqual(P_loss_derived, 74.222, places=2)
        # El informe redondea explícitamente a 74.2 W
        self.assertAlmostEqual(self.P_loss, 74.2, places=1)

    def test_parametric_grid_structure_and_csv(self):
        """
        Verifica que el estudio paramétrico genera exactamente 27 registros
        y que el CSV exportado conserva todas las columnas y filas con integridad.
        """
        records = run_parametric_study(
            C_values=self.C_list,
            R_values=self.R_list,
            t_values=self.t_list,
            P_loss=self.P_loss,
            T_amb=self.T_amb,
            T_illustrative=self.T_thresh
        )
        self.assertEqual(len(records), 27)
        
        # Guardar en CSV temporal en salidas/ y verificar
        test_csv_path = os.path.join(os.path.dirname(__file__), "test_sensibilidad.csv")
        export_to_csv(records, test_csv_path)
        self.assertTrue(os.path.exists(test_csv_path))
        
        with open(test_csv_path, mode="r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 27)
            # Verificar presencia de columnas esenciales
            expected_headers = [
                "id_caso", "C_J_K", "R_K_W", "P_loss_W", "T_amb_degC", "tau_s",
                "t_eval_s", "T_analitica_degC", "delta_T_K", "T_estacionaria_degC",
                "supera_umbral_80C", "margen_seguridad_80C_K", "t_alcance_80C_s",
                "categoria_epistemica_temperatura", "fuente_potencia_perdida",
                "fuente_umbral_referencia"
            ]
            for col in expected_headers:
                self.assertIn(col, reader[0])

        # Limpiar CSV temporal de prueba
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)


if __name__ == "__main__":
    unittest.main()
