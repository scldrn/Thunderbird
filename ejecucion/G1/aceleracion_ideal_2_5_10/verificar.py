"""Comprueba identidades y límites del cribado cinemático ideal."""

import math
import unittest

from calcular import G_MS2, escenario


class Verificacion(unittest.TestCase):
    def setUp(self):
        self.x = escenario(5, 1000, 2, .7, 150, 5000)

    def test_cinematica_y_trabajo(self):
        v, a = 1000 / 3.6, 2 * G_MS2
        self.assertAlmostEqual(self.x["tiempo_s"], v / a)
        self.assertAlmostEqual(self.x["distancia_m"], v * v / (2 * a))
        self.assertAlmostEqual(self.x["fuerza_horizontal_n"] * self.x["distancia_m"], .5 * 5 * v * v)
        self.assertAlmostEqual(self.x["energia_cinetica_wh"], .5 * 5 * v * v / 3600)

    def test_potencia_y_energia_electricas_supuestas(self):
        self.assertAlmostEqual(self.x["potencia_util_final_w"], 5 * 2 * G_MS2 * 1000 / 3.6)
        self.assertAlmostEqual(self.x["energia_bateria_wh"], self.x["energia_cinetica_wh"] / .7)
        self.assertAlmostEqual(self.x["masa_bateria_hipotetica_kg"], max(self.x["energia_bateria_wh"] / 150, self.x["potencia_bateria_final_w"] / 5000))

    def test_escala_masa_y_aceleracion(self):
        doble = escenario(10, 1000, 2, .7, 150, 5000)
        rapido = escenario(5, 1000, 4, .7, 150, 5000)
        self.assertAlmostEqual(doble["energia_cinetica_wh"], 2 * self.x["energia_cinetica_wh"])
        self.assertAlmostEqual(doble["tiempo_s"], self.x["tiempo_s"])
        self.assertAlmostEqual(rapido["tiempo_s"], self.x["tiempo_s"] / 2)
        self.assertAlmostEqual(rapido["potencia_util_final_w"], 2 * self.x["potencia_util_final_w"])

    def test_entradas_invalidas(self):
        for valores in [(0, 1000, 2, .7, 150, 5000), (5, math.nan, 2, .7, 150, 5000),
                        (5, 1000, 2, 1.1, 150, 5000), (5, 1000, 0, .7, 150, 5000)]:
            with self.assertRaises(ValueError):
                escenario(*valores)


if __name__ == "__main__":
    unittest.main()
