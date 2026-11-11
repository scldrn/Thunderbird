#!/usr/bin/env python3
"""Verificación analítica y numérica del cribado de potencia simultánea."""

import math
import unittest

import calcular


class MissionTest(unittest.TestCase):
    def test_reproduce_escenario_previo_sin_apoyo(self):
        q = calcular.evaluate(600.0, 50.0, 60.0, 0.0)
        self.assertAlmostEqual(q["energia_total_Wh"], 201.55, delta=0.01)
        self.assertAlmostEqual(q["pico_bateria_W"] / 1000.0, 15.21, delta=0.01)
        self.assertAlmostEqual(q["masa_bateria_minima_kg"], 3.04, delta=0.01)

    def test_carga_simultanea_se_suma_a_pico_y_energia(self):
        base = calcular.evaluate(600.0, 25.0, 60.0, 0.0)
        loaded = calcular.evaluate(600.0, 25.0, 60.0, 1000.0)
        self.assertAlmostEqual(loaded["energia_total_Wh"] - base["energia_total_Wh"], 1000.0 * 90.0 / 3600.0)
        self.assertAlmostEqual(loaded["pico_bateria_W"] - base["pico_bateria_W"], 1000.0)

    def test_cero_arrastre_energia_cinetica_y_pico(self):
        q = calcular.evaluate(360.0, 0.0, 20.0, 0.0)
        self.assertAlmostEqual(q["energia_axial_Wh"], 0.5 * 5 * 100**2 / (3600 * 0.7))
        self.assertAlmostEqual(q["pico_axial_W"], 5 * 100**2 / (20 * 0.7))

    def test_optimo_contrasta_barrido_denso(self):
        for speed, drag, support in ((600, 0, 0), (600, 50, 1000), (1000, 25, 2968.8)):
            exact = calcular.best_time(speed, drag, support, 10.0, 180.0)
            grid = min(calcular.evaluate(speed, drag, 10.0 + i * 0.1, support)["masa_bateria_minima_kg"]
                       for i in range(1701))
            self.assertLessEqual(exact["masa_bateria_minima_kg"], grid + 1e-10)
            self.assertLess(abs(exact["masa_bateria_minima_kg"] - grid), 0.02)

    def test_umbral_es_raiz_y_falla_por_encima(self):
        threshold = calcular.drag_threshold(600.0, 1000.0, 60.0, 2.20416)
        self.assertIsNotNone(threshold)
        self.assertAlmostEqual(calcular.best_time(600.0, threshold, 1000.0, 10, 60)["masa_bateria_minima_kg"], 2.20416, places=8)
        self.assertGreater(calcular.best_time(600.0, threshold + 0.01, 1000.0, 10, 60)["masa_bateria_minima_kg"], 2.20416)

    def test_capacidad_insuficiente_hasta_arrastre_cero(self):
        self.assertIsNone(calcular.drag_threshold(1000.0, 2968.8, 60.0, 1.0))


if __name__ == "__main__":
    unittest.main()
