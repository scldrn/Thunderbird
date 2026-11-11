#!/usr/bin/env python3
"""Invariantes analíticos de autoridad vertical ideal."""

import unittest

import numpy as np

import calcular_autoridad as base
from envolvente_vertical import horizontal_limit, vertical_limit
from sensibilidad_brazo_vertical import solve


class VerticalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.centres = np.array([[-0.16, -0.076, 0.0], [-0.16, 0.076, 0.0],
                                [0.16, -0.076, 0.0], [0.16, 0.076, 0.0]])

    def test_limite_vertical_analitico_cg_centrado_y_desplazado(self):
        for cg_x in (0.0, 0.04, 0.096, 0.12, 0.16):
            result = vertical_limit(self.centres, cg_x, 0.039, 45.0, 20.58)
            expected_force = 4 * 20.58 / (1 + abs(cg_x) / 0.16)
            self.assertAlmostEqual(result["fuerza_vertical_total_max_N"], expected_force, places=8)

    def test_cg_fuera_base_sin_fuerza_horizontal(self):
        result = vertical_limit(self.centres, 0.161, 0.0, 45.0, 20.58)
        self.assertAlmostEqual(result["fuerza_vertical_total_max_N"], 0.0, places=8)

    def test_caida_gravedad_no_deja_fuerza_horizontal(self):
        result = horizontal_limit(self.centres, 0.0, 0.0, 45.0, 20.58, -1.0, 1)
        self.assertTrue(result["solucion_lp"])
        self.assertAlmostEqual(result["aceleracion_horizontal_g"], 0.0, places=9)

    def test_mas_de_un_g_hacia_abajo_no_cumple_cono_unidireccional(self):
        result = horizontal_limit(self.centres, 0.0, 0.0, 45.0, 20.58, -1.2, 1)
        self.assertFalse(result["solucion_lp"])
        self.assertEqual(result["estado_lp"], 2)

    def test_igualdad_con_modelo_horizontal_anterior(self):
        older = solve(self.centres, 0.096, 0.039, 45.0, 20.58, 0.0, 1)
        new = horizontal_limit(self.centres, 0.096, 0.039, 45.0, 20.58, 0.0, 1)
        self.assertTrue(older["solucion_lp"] and new["solucion_lp"])
        self.assertAlmostEqual(older["aceleracion_en_direccion_g"], new["aceleracion_horizontal_g"], places=9)

    def test_demanda_vertical_sobre_limite_es_inviable(self):
        result = horizontal_limit(self.centres, 0.096, 0.0, 45.0, 20.58, 0.2, 1)
        self.assertFalse(result["solucion_lp"])


if __name__ == "__main__":
    unittest.main()
