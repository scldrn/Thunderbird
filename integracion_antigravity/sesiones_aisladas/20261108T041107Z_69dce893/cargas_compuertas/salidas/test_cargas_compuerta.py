#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cargas_compuerta.py
-------------------------------------------------------------------------------
Batería de pruebas unitarias y de verificación física para el análisis
paramétrico de cargas aerodinámicas de compuerta.

Verifica:
  1. Conversiones de unidades exactas (km/h -> m/s).
  2. Presión dinámica q a 1000 km/h (~47261 Pa) y a 600 km/h (~17014 Pa).
  3. Relaciones de presión diferencial Delta_p = Cp * q.
  4. Factores de escala isomórfica (2 kg, 5 kg, 10 kg).
  5. Cálculo de fuerzas F = Delta_p * A y momentos M = F * brazo.
  6. Leyes de semejanza de momentos (M escala linealmente con masa m/5).
  7. Consistencia y validez de exportación de artefactos (CSV, JSON, Markdown).
-------------------------------------------------------------------------------
"""

import math
import sys
import json
import csv
import unittest
from pathlib import Path

# Asegurar que el directorio de salidas esté en sys.path
salidas_path = Path(__file__).resolve().parent
if str(salidas_path) not in sys.path:
    sys.path.insert(0, str(salidas_path))

# Importar funciones del script de análisis ubicado en el mismo directorio salidas
from analisis_cargas_compuerta import (
    kmh_to_ms,
    dynamic_pressure,
    differential_pressure,
    geometric_scale_factors,
    scale_hypothetical_area,
    scale_hypothetical_arm,
    aerodynamic_force,
    aerodynamic_moment,
    run_parametric_case,
    run_full_parametric_sweep,
    export_to_csv,
    export_to_json,
    export_to_markdown_tables,
    RHO_STD_KG_M3,
    REF_MASS_KG,
    HIPOTETICO_AREA_REF_M2,
    HIPOTETICO_ARM_REF_M,
    VELOCITIES_KMH,
    MASS_TARGETS_KG,
    CP_DIFFERENTIAL_VALUES,
)


class TestAerodynamicConversionsAndQ(unittest.TestCase):
    """Pruebas de conversiones y presión dinámica q."""

    def test_kmh_to_ms_exact(self):
        """Comprueba conversiones exactas de velocidad."""
        # 600 km/h = 600 / 3.6 = 500 / 3 m/s = 166.6666... m/s
        v600_ms = kmh_to_ms(600.0)
        self.assertAlmostEqual(v600_ms, 500.0 / 3.0, places=9)
        self.assertAlmostEqual(v600_ms, 166.666666667, places=5)

        # 1000 km/h = 1000 / 3.6 = 2500 / 9 m/s = 277.7777... m/s
        v1000_ms = kmh_to_ms(1000.0)
        self.assertAlmostEqual(v1000_ms, 2500.0 / 9.0, places=9)
        self.assertAlmostEqual(v1000_ms, 277.777777778, places=5)

        # 0 km/h = 0 m/s
        self.assertEqual(kmh_to_ms(0.0), 0.0)

        # Velocidad negativa debe lanzar ValueError
        with self.assertRaises(ValueError):
            kmh_to_ms(-10.0)

    def test_dynamic_pressure_1000kmh(self):
        """
        Verifica q para 1000 km/h con rho = 1.225 kg/m³:
          q = 0.5 * 1.225 * (1000 / 3.6)^2 = 3828125 / 81 = 47260.802469... Pa
          Comprueba que q ~ 47261 Pa (diferencia < 0.2 Pa, redondeo exacto 47261 Pa).
        """
        v_ms = kmh_to_ms(1000.0)
        q = dynamic_pressure(rho=1.225, v_ms=v_ms)
        expected_exact = 0.5 * 1.225 * ((1000.0 / 3.6) ** 2)

        self.assertAlmostEqual(q, expected_exact, places=7)
        self.assertAlmostEqual(q, 47260.802469, places=3)
        self.assertEqual(round(q), 47261, "q a 1000 km/h debe redondear a 47261 Pa")
        self.assertLess(abs(q - 47261.0), 0.2)

    def test_dynamic_pressure_600kmh(self):
        """
        Verifica q para 600 km/h con rho = 1.225 kg/m³:
          q = 0.5 * 1.225 * (600 / 3.6)^2 = 153125 / 9 = 17013.8888... Pa (~17013.89 Pa)
        """
        v_ms = kmh_to_ms(600.0)
        q = dynamic_pressure(rho=1.225, v_ms=v_ms)
        expected_exact = 0.5 * 1.225 * ((600.0 / 3.6) ** 2)

        self.assertAlmostEqual(q, expected_exact, places=7)
        self.assertAlmostEqual(q, 17013.888889, places=3)
        self.assertEqual(round(q), 17014)

    def test_dynamic_pressure_invalid_inputs(self):
        """Verifica que entradas no físicas lancen excepciones."""
        with self.assertRaises(ValueError):
            dynamic_pressure(rho=0.0, v_ms=100.0)
        with self.assertRaises(ValueError):
            dynamic_pressure(rho=-1.2, v_ms=100.0)
        with self.assertRaises(ValueError):
            dynamic_pressure(rho=1.225, v_ms=-50.0)


class TestAerodynamicFormulasAndScaling(unittest.TestCase):
    """Pruebas de Delta_p, escalado geométrico isomórfico, fuerza y momento."""

    def test_differential_pressure(self):
        """Verifica Delta_p = Cp * q."""
        q = 10000.0
        self.assertEqual(differential_pressure(q, 0.0), 0.0)
        self.assertEqual(differential_pressure(q, 1.0), 10000.0)
        self.assertEqual(differential_pressure(q, 0.5), 5000.0)
        self.assertEqual(differential_pressure(q, 1.5), 15000.0)

    def test_geometric_scaling_factors(self):
        """
        Verifica los factores isomórficos (m/5)^(1/3):
          - 5 kg:  lambda_L = 1.0, lambda_A = 1.0, lambda_V = 1.0
          - 2 kg:  lambda_L = (0.4)^(1/3) ~ 0.736806, lambda_A ~ 0.542884
          - 10 kg: lambda_L = 2.0^(1/3)   ~ 1.259921, lambda_A ~ 1.587401
        """
        scale_5 = geometric_scale_factors(5.0, 5.0)
        self.assertEqual(scale_5["lambda_L"], 1.0)
        self.assertEqual(scale_5["lambda_A"], 1.0)
        self.assertEqual(scale_5["lambda_V"], 1.0)

        scale_2 = geometric_scale_factors(2.0, 5.0)
        expected_l2 = (2.0 / 5.0) ** (1.0 / 3.0)
        self.assertAlmostEqual(scale_2["lambda_L"], expected_l2, places=9)
        self.assertAlmostEqual(scale_2["lambda_L"], 0.7368063, places=5)
        self.assertAlmostEqual(scale_2["lambda_A"], expected_l2 ** 2, places=9)
        self.assertAlmostEqual(scale_2["lambda_A"], 0.5428835, places=5)
        self.assertAlmostEqual(scale_2["lambda_V"], 0.4, places=9)

        scale_10 = geometric_scale_factors(10.0, 5.0)
        expected_l10 = (10.0 / 5.0) ** (1.0 / 3.0)
        self.assertAlmostEqual(scale_10["lambda_L"], expected_l10, places=9)
        self.assertAlmostEqual(scale_10["lambda_L"], 1.2599210, places=5)
        self.assertAlmostEqual(scale_10["lambda_A"], expected_l10 ** 2, places=9)
        self.assertAlmostEqual(scale_10["lambda_A"], 1.5874011, places=5)
        self.assertAlmostEqual(scale_10["lambda_V"], 2.0, places=9)

    def test_force_and_moment_calculations(self):
        """Verifica F = Delta_p * A y M = F * brazo."""
        dp = 20000.0  # Pa
        area = 0.0070  # m²
        arm = 0.048   # m

        f = aerodynamic_force(dp, area)
        self.assertAlmostEqual(f, 140.0, places=6)

        m = aerodynamic_moment(f, arm)
        self.assertAlmostEqual(m, 140.0 * 0.048, places=6)
        self.assertAlmostEqual(m, 6.72, places=6)

    def test_moment_scales_linearly_with_mass_target(self):
        """
        Leyes de semejanza:
          A proporcional a lambda_L^2
          brazo proporcional a lambda_L
          M = F * brazo = Delta_p * A * brazo proporcional a lambda_L^3 = m / m_ref
          Por tanto:
            M(10 kg) / M(5 kg) == 10 / 5 == 2.0
            M(2 kg) / M(5 kg) == 2 / 5 == 0.4
        """
        case_5 = run_parametric_case(v_kmh=1000.0, rho=1.225, mass_target_kg=5.0, cp_diff=1.0)
        case_10 = run_parametric_case(v_kmh=1000.0, rho=1.225, mass_target_kg=10.0, cp_diff=1.0)
        case_2 = run_parametric_case(v_kmh=1000.0, rho=1.225, mass_target_kg=2.0, cp_diff=1.0)

        ratio_10_5 = case_10["momento_nm"] / case_5["momento_nm"]
        ratio_2_5 = case_2["momento_nm"] / case_5["momento_nm"]

        self.assertAlmostEqual(ratio_10_5, 2.0, places=6)
        self.assertAlmostEqual(ratio_2_5, 0.4, places=6)

    def test_force_scales_with_area(self):
        """
        Verifica que F(m) / F(5) == (m / 5)^(2/3).
        """
        case_5 = run_parametric_case(v_kmh=600.0, rho=1.225, mass_target_kg=5.0, cp_diff=0.8)
        case_10 = run_parametric_case(v_kmh=600.0, rho=1.225, mass_target_kg=10.0, cp_diff=0.8)
        case_2 = run_parametric_case(v_kmh=600.0, rho=1.225, mass_target_kg=2.0, cp_diff=0.8)

        expected_ratio_10 = (10.0 / 5.0) ** (2.0 / 3.0)
        expected_ratio_2 = (2.0 / 5.0) ** (2.0 / 3.0)

        self.assertAlmostEqual(case_10["fuerza_n"] / case_5["fuerza_n"], expected_ratio_10, places=6)
        self.assertAlmostEqual(case_2["fuerza_n"] / case_5["fuerza_n"], expected_ratio_2, places=6)


class TestParametricSweepAndOutputs(unittest.TestCase):
    """Pruebas del barrido completo y archivos de salida."""

    def setUp(self):
        self.salidas_dir = Path(__file__).resolve().parent
        self.results = run_full_parametric_sweep()

    def test_parametric_sweep_cardinality(self):
        """Verifica que se generen exactamente 48 casos (2 vel * 3 masas * 8 Cp)."""
        expected_count = len(VELOCITIES_KMH) * len(MASS_TARGETS_KG) * len(CP_DIFFERENTIAL_VALUES)
        self.assertEqual(expected_count, 48)
        self.assertEqual(len(self.results), 48)

    def test_case_values_monotonicity(self):
        """Verifica monotonicidad de F y M con respecto a Cp y V."""
        # A mayor Cp, mayor Delta_p, F y M
        cases_v1000_m5 = [r for r in self.results if r["velocidad_kmh"] == 1000.0 and r["masa_objetivo_kg"] == 5.0]
        sorted_cases = sorted(cases_v1000_m5, key=lambda x: x["cp_diferencial"])
        for i in range(len(sorted_cases) - 1):
            self.assertLess(sorted_cases[i]["cp_diferencial"], sorted_cases[i+1]["cp_diferencial"])
            self.assertLess(sorted_cases[i]["fuerza_n"], sorted_cases[i+1]["fuerza_n"])
            self.assertLess(sorted_cases[i]["momento_nm"], sorted_cases[i+1]["momento_nm"])

    def test_exported_csv_validity(self):
        """Verifica integridad del archivo CSV generado."""
        csv_file = self.salidas_dir / "tablas_cargas_compuerta.csv"
        self.assertTrue(csv_file.exists(), "El archivo CSV debe existir en salidas/")
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 48)
        # Verificar un registro representativo (1000 km/h, 5 kg, Cp=1.0)
        matching = [r for r in rows if float(r["velocidad_kmh"]) == 1000.0 and float(r["masa_objetivo_kg"]) == 5.0 and float(r["cp_diferencial"]) == 1.0]
        self.assertEqual(len(matching), 1)
        target = matching[0]
        self.assertAlmostEqual(float(target["q_pa"]), 47260.802469, places=2)
        self.assertAlmostEqual(float(target["fuerza_n"]), 330.8256, places=2)
        self.assertAlmostEqual(float(target["momento_nm"]), 15.8796, places=2)

    def test_exported_json_validity(self):
        """Verifica integridad del archivo JSON generado."""
        json_file = self.salidas_dir / "resultados_cargas_compuerta.json"
        self.assertTrue(json_file.exists(), "El archivo JSON debe existir en salidas/")
        with open(json_file, mode="r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["conteo_casos"], 48)
        self.assertIn("advertencia_critica", data)
        self.assertIn("casos", data)
        self.assertEqual(len(data["casos"]), 48)

    def test_exported_markdown_validity(self):
        """Verifica que el archivo Markdown contenga las advertencias y tablas requeridas."""
        md_file = self.salidas_dir / "tablas_cargas_compuerta.md"
        self.assertTrue(md_file.exists(), "El archivo Markdown debe existir en salidas/")
        content = md_file.read_text(encoding="utf-8")
        self.assertIn("47260.80", content)
        self.assertIn("17013.89", content)
        self.assertIn("EXPLÍCITAMENTE HIPOTÉTICOS", content)
        self.assertIn("baja velocidad", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
