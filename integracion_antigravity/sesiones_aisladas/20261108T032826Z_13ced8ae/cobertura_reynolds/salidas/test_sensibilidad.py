#!/usr/bin/env python3
"""
Batería de pruebas unitarias y de integración para la condición cinemática de cuerda mínima:
    c_min = (Re_min * nu) / (M_lim * a)

Verifica:
1. Análisis dimensional y unidades consistentes en SI.
2. Extracción correcta de bloques de Reynolds desde SD8020.DRG.
3. Reproducción exacta del punto canónico (61400, M=0.3) -> 8.781 mm.
4. Monotonía física (crecimiento con Re, decrecimiento con M).
5. Elasticidades y proporciones analíticas exactas (duplicar M reduce a la mitad c_min, etc.).
6. Generación e integridad del archivo CSV.
7. Manejo robusto de errores para entradas no físicas (M <= 0, Re <= 0).
"""

import os
import sys
import csv
import unittest

# Añadir el directorio salidas al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sensibilidad_cinematica import (
    DEFAULT_NU,
    DEFAULT_A,
    DEFAULT_MACH_LIMITS,
    DEFAULT_RE_LIST,
    parse_reynolds_from_drg,
    compute_c_min,
    verify_benchmark_example,
    compute_sensitivity_matrix,
    export_csv_matrix
)


class TestCondicionCinematica(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.drg_path = os.path.join(
            self.base_dir, "entradas", "investigacion-aeronautica", "fuentes", "uiuc", "SD8020.DRG"
        )
        self.salidas_dir = os.path.join(self.base_dir, "salidas")

    def test_01_analisis_dimensional_y_unidades(self):
        """
        Verificación analítica de unidades:
            [Re] = 1 (adimensional)
            [nu] = m^2 / s
            [M]  = 1 (adimensional)
            [a]  = m / s
            [c_min] = (1 * m^2 / s) / (1 * m / s) = m
        """
        re_test = 61400.0  # [-]
        nu_test = 1.46e-5  # [m^2/s]
        m_test = 0.3       # [-]
        a_test = 340.3     # [m/s]

        # Numerador: Re * nu -> [m^2/s]
        numerador = re_test * nu_test
        # Denominador: M * a -> [m/s]
        denominador = m_test * a_test

        c_calculada_m = numerador / denominador  # [m]
        self.assertAlmostEqual(c_calculada_m, 0.0087808796, places=8)

        # Conversión a milímetros: 1 m = 1000 mm
        c_calculada_mm = c_calculada_m * 1000.0
        self.assertEqual(round(c_calculada_mm, 3), 8.781)

    def test_02_extraccion_reynolds_drg(self):
        """Verifica que el parser extraiga exactamente los 4 bloques del SD8020.DRG."""
        self.assertTrue(os.path.exists(self.drg_path), f"El archivo {self.drg_path} debe existir.")
        re_blocks = parse_reynolds_from_drg(self.drg_path)
        expected_blocks = [61400, 101500, 203300, 304800]
        self.assertEqual(re_blocks, expected_blocks, f"Esperado {expected_blocks}, obtenido {re_blocks}")

    def test_03_reproduccion_ejemplo_benchmark(self):
        """Reproduce exactamente la referencia de la especificación: 61400 / 0.3 -> 8.781 mm."""
        res = verify_benchmark_example(nu=DEFAULT_NU, a=DEFAULT_A)
        self.assertTrue(res["matches_expected_3dec"])
        self.assertEqual(res["c_min_mm_rounded_3dec"], 8.781)
        self.assertLess(res["absolute_diff_mm"], 0.0005)

    def test_04_monotonia_y_elasticidad(self):
        """
        Verifica el comportamiento funcional de c_min:
        1. Monótonamente creciente respecto a Re_min.
        2. Monótonamente decreciente respecto a M_lim.
        3. Elasticidad unitaria (+1 respecto a Re, -1 respecto a M).
        """
        # 1. Crecimiento con Re
        re_vals = [61400, 101500, 203300, 304800]
        for m in [0.2, 0.3, 0.4]:
            c_prev = 0.0
            for re_v in re_vals:
                c_cur = compute_c_min(re_v, m, DEFAULT_NU, DEFAULT_A)
                self.assertGreater(c_cur, c_prev)
                c_prev = c_cur

        # 2. Decrecimiento con M
        for re_v in re_vals:
            c_m02 = compute_c_min(re_v, 0.2, DEFAULT_NU, DEFAULT_A)
            c_m03 = compute_c_min(re_v, 0.3, DEFAULT_NU, DEFAULT_A)
            c_m04 = compute_c_min(re_v, 0.4, DEFAULT_NU, DEFAULT_A)
            self.assertGreater(c_m02, c_m03)
            self.assertGreater(c_m03, c_m04)

            # 3. Relaciones analíticas exactas
            # M=0.2 es el doble de M=0.4 en denominador -> c_min(0.2) debe ser exactamente el doble de c_min(0.4)
            self.assertAlmostEqual(c_m02 / c_m04, 2.0, places=9)
            # M=0.3 vs M=0.2 -> ratio 0.2/0.3 = 2/3
            self.assertAlmostEqual(c_m03 / c_m02, 2.0 / 3.0, places=9)

    def test_05_matriz_sensibilidad_y_derivadas(self):
        """Verifica el cálculo de derivadas analíticas contra diferencias finitas."""
        re_vals = [61400, 101500, 203300, 304800]
        m_vals = [0.2, 0.3, 0.4]
        matrix = compute_sensitivity_matrix(re_vals, m_vals, DEFAULT_NU, DEFAULT_A)
        self.assertEqual(len(matrix), 12)  # 4 * 3 = 12 combinaciones

        eps_re = 1.0  # 1 unidad de Reynolds
        eps_m = 1e-5  # perturbación en Mach

        for rec in matrix:
            re_v = rec["re_min"]
            m_v = rec["m_lim"]
            c_base = rec["c_min_m"]

            # Derivada respecto a Re
            c_re_pert = compute_c_min(re_v + eps_re, m_v, DEFAULT_NU, DEFAULT_A)
            fd_dre = (c_re_pert - c_base) / eps_re
            self.assertAlmostEqual(rec["dc_dre_m"], fd_dre, places=9)

            # Derivada respecto a M
            c_m_pert = compute_c_min(re_v, m_v + eps_m, DEFAULT_NU, DEFAULT_A)
            fd_dm = (c_m_pert - c_base) / eps_m
            self.assertAlmostEqual(rec["dc_dm_m"], fd_dm, places=4)

    def test_06_generacion_y_formato_csv(self):
        """Verifica que el archivo CSV se cree con estructura correcta y datos no nulos."""
        csv_path = os.path.join(self.salidas_dir, "test_matriz.csv")
        re_vals = [61400, 101500, 203300, 304800]
        m_vals = [0.2, 0.3, 0.4]
        records = compute_sensitivity_matrix(re_vals, m_vals, DEFAULT_NU, DEFAULT_A)
        export_csv_matrix(records, csv_path)

        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 12)
            for row in reader:
                self.assertIn("re_min", row)
                self.assertIn("m_lim", row)
                self.assertIn("c_min_mm", row)
                self.assertGreater(float(row["c_min_mm"]), 0.0)

        # Limpieza de archivo temporal de prueba
        if os.path.exists(csv_path):
            os.remove(csv_path)

    def test_07_manejo_errores_entradas_invalidas(self):
        """Verifica que valores no físicos disparen excepciones controladas."""
        with self.assertRaises(ValueError):
            compute_c_min(-100, 0.3)
        with self.assertRaises(ValueError):
            compute_c_min(61400, 0.0)
        with self.assertRaises(ValueError):
            compute_c_min(61400, -0.3)
        with self.assertRaises(ValueError):
            compute_c_min(61400, 0.3, nu=-1.0)
        with self.assertRaises(ValueError):
            compute_c_min(61400, 0.3, a=0.0)


if __name__ == "__main__":
    unittest.main()
