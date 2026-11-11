#!/usr/bin/env python3
"""Contrastes analíticos del cribado de fuerza ideal."""

import math
import unittest

import numpy as np

import calcular_autoridad as base
from sensibilidad_brazo_vertical import solve


class ForceSensitivityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.centres = np.array([[-0.16, -0.076, 0.0], [-0.16, 0.076, 0.0],
                                [0.16, -0.076, 0.0], [0.16, 0.076, 0.0]])

    def test_simetria_sin_desplazamientos(self):
        positive = solve(self.centres, 0.0, 0.0, 45.0, 20.58, 0.0, 1)
        negative = solve(self.centres, 0.0, 0.0, 45.0, 20.58, 0.0, -1)
        self.assertTrue(positive["solucion_lp"] and negative["solucion_lp"])
        self.assertAlmostEqual(positive["aceleracion_en_direccion_g"], negative["aceleracion_en_direccion_g"], places=9)
        self.assertAlmostEqual(positive["aceleracion_en_direccion_g"], 1.0, places=9)

    def test_reproduce_lp_base(self):
        known = base.maximize_acceleration(self.centres, np.array([0.096, 0.0, 0.0]), 45.0, 20.58)
        new = solve(self.centres, 0.096, 0.0, 45.0, 20.58, 0.0, 1)
        self.assertTrue(known["feasible"] and new["solucion_lp"])
        self.assertAlmostEqual(known["acceleration_g"], new["aceleracion_en_direccion_g"], places=9)

    def test_simetria_reflexion_signo_del_brazo(self):
        forward = solve(self.centres, 0.08, 0.039, 45.0, 20.58, 0.0, 1)
        backward = solve(self.centres, 0.08, -0.039, 45.0, 20.58, 0.0, -1)
        self.assertTrue(forward["solucion_lp"] and backward["solucion_lp"])
        self.assertAlmostEqual(forward["aceleracion_en_direccion_g"], backward["aceleracion_en_direccion_g"], places=9)

    def test_simetria_cg_y_sentido_longitudinal(self):
        first = solve(self.centres, 0.08, 0.039, 45.0, 20.58, 0.0, 1)
        reflected = solve(self.centres, -0.08, 0.039, 45.0, 20.58, 0.0, -1)
        self.assertTrue(first["solucion_lp"] and reflected["solucion_lp"])
        self.assertAlmostEqual(first["aceleracion_en_direccion_g"], reflected["aceleracion_en_direccion_g"], places=9)

    def test_simetria_signo_momento_alabeo(self):
        positive = solve(self.centres, 0.08, 0.039, 45.0, 20.58, 0.5, 1)
        negative = solve(self.centres, 0.08, 0.039, 45.0, 20.58, -0.5, 1)
        self.assertTrue(positive["solucion_lp"] and negative["solucion_lp"])
        self.assertAlmostEqual(positive["aceleracion_en_direccion_g"], negative["aceleracion_en_direccion_g"], places=9)

    def test_cg_fuera_limite_con_brazo_cero(self):
        cutoff = 0.16 * (4.0 * 20.58 / (base.MASS * base.G) - 1.0)
        self.assertLess(cutoff, 0.12)
        result = solve(self.centres, 0.12, 0.0, 45.0, 20.58, 0.0, 1)
        self.assertFalse(result["solucion_lp"])

    def test_angulos_ideales_con_limite_alto(self):
        result = solve(self.centres, 0.0, 0.0, 35.0, 1000.0, 0.0, 1)
        self.assertAlmostEqual(result["aceleracion_en_direccion_g"], math.tan(math.radians(35)), places=9)


if __name__ == "__main__":
    unittest.main()
