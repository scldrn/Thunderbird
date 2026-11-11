"""
Batería de pruebas unitarias y de verificación para conversiones y contraste trazable NASA vs C02.
Ejecución: python3 -m unittest salidas/test_conversiones.py
"""

import unittest
import os
import csv
from decimal import Decimal

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import conversiones


class TestMetrologiaYConversiones(unittest.TestCase):
    """Pruebas metrológicas de factores estándar y conversiones exactas."""

    def test_pulgadas_a_mm_valor_solicitado(self):
        """Verifica que 5.11 pulgadas sea exactamente 129.794 mm."""
        res = conversiones.inches_to_mm(5.11)
        self.assertAlmostEqual(res, 129.794, places=6)
        self.assertEqual(conversiones.inches_to_mm(5.11, precision=3), 129.794)

    def test_lbf_a_newtons_valor_solicitado(self):
        """Verifica que 21.25 lbf se convierta a ~94.5247 N con definición internacional."""
        res = conversiones.lbf_to_newtons(21.25)
        # Factor internacional: 1 lb = 0.45359237 kg; g0 = 9.80665 m/s^2; 1 lbf = 4.4482216152605 N
        # 21.25 * 4.4482216152605 = 94.524709324285625 N
        self.assertAlmostEqual(res, 94.524709324285625, places=5)
        self.assertEqual(conversiones.lbf_to_newtons(21.25, precision=4), 94.5247)
        self.assertEqual(conversiones.lbf_to_newtons(21.25, precision=2), 94.52)

    def test_diametro_exterior_conducto_nasa(self):
        """Verifica la conversión del diámetro exterior de conducto NASA (5.23 in)."""
        res = conversiones.inches_to_mm(5.23)
        self.assertAlmostEqual(res, 132.842, places=6)

    def test_inversas(self):
        """Verifica consistencia en conversiones de ida y vuelta."""
        mm = 129.794
        in_calc = conversiones.mm_to_inches(mm, precision=2)
        self.assertEqual(in_calc, 5.11)

        n = 94.524709324285625
        lbf_calc = conversiones.newtons_to_lbf(n, precision=2)
        self.assertEqual(lbf_calc, 21.25)


class TestComparacionGeometricaYMasica(unittest.TestCase):
    """Pruebas sobre dimensiones, contención y masa."""

    def test_diametros_rotor(self):
        """Compara diámetros de rotor: NASA (129.794 mm) vs C02 D82 y D102.5."""
        nasa_rotor_mm = conversiones.inches_to_mm(5.11)
        c02_d82 = 82.0
        c02_d102_5 = 102.5

        self.assertGreater(nasa_rotor_mm, c02_d82)
        self.assertGreater(nasa_rotor_mm, c02_d102_5)

        # Relación de áreas de barrido (NASA vs D82)
        relacion_area = (nasa_rotor_mm / c02_d82) ** 2
        self.assertGreater(relacion_area, 2.50)  # >2.5 veces el área

    def test_incompatibilidad_motor_nasa_en_c02(self):
        """
        Verifica formalmente que el motor NASA NO cabe en las reservas de C02.
        Regla: No afirmar que el motor NASA quepa en C02.
        """
        fit = conversiones.check_motor_fit()
        # No cabe en D82
        self.assertFalse(fit["fits_d82"], "El motor NASA no debe caber en la reserva D82 de C02")
        # No cabe en D102.5
        self.assertFalse(fit["fits_d102"], "El motor NASA no debe caber en la reserva D102.5 de C02")
        # El diámetro del motor NASA (56 mm) supera con creces el alojamiento de C02
        self.assertGreater(fit["diam_ratio_d82"], 2.5)
        self.assertGreater(fit["diam_ratio_d102"], 2.0)

    def test_impacto_masico_motor_nasa(self):
        """Evalúa la inviabilidad de masa del motor NASA (1.100 g) en el vehículo de 5 kg C02."""
        fit = conversiones.check_motor_fit()
        # 4 motores NASA = 4.40 kg
        self.assertEqual(fit["mass_4_motors_g"], 4400.0)
        # Consumen 88% del peso total del vehículo
        self.assertAlmostEqual(fit["mass_fraction_veh"], 0.88, places=2)


class TestRigorMetodologicoYFuentes(unittest.TestCase):
    """Pruebas de trazabilidad de fuentes y no suposición de puntos simultáneos."""

    def test_extremos_no_simultaneos_nasa(self):
        """
        Verifica que los extremos de empuje (21.25 lbf) y potencia (6420 W)
        no se traten como un punto único de operación.
        """
        data = conversiones.get_comparison_data()
        empuje_row = next(r for r in data if r["Parametro"] == "Empuje estático reportado")
        potencia_row = next(r for r in data if r["Parametro"] == "Potencia reportada")

        self.assertIn("NO se asumen medidos en un mismo punto", empuje_row["Observaciones_Trazabilidad"])
        self.assertIn("Tabla 6", empuje_row["Fuente_NASA"])
        self.assertTrue("Tabla 6" in potencia_row["Fuente_NASA"] or "6" in potencia_row["Fuente_NASA"])

    def test_distincion_fuente_primaria_vs_nota(self):
        """Verifica que la fuente primaria NASA (Weinstein et al.) y la nota copiada queden distinguidas."""
        data = conversiones.get_comparison_data()
        for row in data:
            self.assertIn("NOTA-NASA-EDF.md", row["Fuente_NASA"])
            self.assertIn("INFORME-C02.md", row["Fuente_C02"])

    def test_generacion_archivos_salida(self):
        """Verifica que los archivos CSV y MD se generen correctamente en salidas/."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, "tabla_comparativa.csv")
        md_path = os.path.join(base_dir, "tabla_comparativa.md")

        conversiones.generate_csv_table(csv_path)
        conversiones.generate_markdown_table(md_path)

        self.assertTrue(os.path.exists(csv_path))
        self.assertTrue(os.path.exists(md_path))
        self.assertGreater(os.path.getsize(csv_path), 500)
        self.assertGreater(os.path.getsize(md_path), 500)


if __name__ == "__main__":
    unittest.main()
