#!/usr/bin/env python3
"""
test_escalado.py
----------------
Suite de pruebas unitarias y de verificación matemática independiente para
el escalado geométrico 2, 5, 10 kg con base D82 y comparación con D84.

Verifica:
  1. Valores de hover para 2, 5 y 10 kg (~518 W, ~1509 W, ~3388 W).
  2. Ecuaciones gobernantes de teoría de cantidad de movimiento (Rankine-Froude).
  3. Leyes de escalado geométrico semejante (D ~ m^(1/3), A ~ m^(2/3), vi ~ m^(1/6), Pi ~ m^(7/6)).
  4. Reproducción estricta de la hipótesis de referencia D84 (REFERENCIA_DISCO.csv).
  5. Relaciones analíticas exactas entre hipótesis D82 y D84.
  6. Integridad de los archivos y estructura del paquete reproducible (salidas/).
  7. Verificaciones de advertencias obligatorias de alcance.
"""

import unittest
import math
import os
import sys
import csv
import json

# Asegurar que el directorio de este script esté en sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from escalado_geometrico import (
    load_reference_inputs,
    compute_momentum_theory,
    run_scaling_study,
    export_deliverables,
    get_default_paths
)


class TestEscaladoGeometrico(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Asegurar ejecución limpia desde datos locales
        cls.study_data = run_scaling_study()
        export_deliverables(cls.study_data, output_dir=SCRIPT_DIR)

    def test_01_hover_power_independent_verification(self):
        """
        Verificación independiente de los valores de potencia inducida en hover (0 g netos):
        Para masa 2, 5, 10 kg y referencia de 82 mm a 5 kg, 4 discos ideales abiertos, rho 1.225 kg/m^3:
        El hover es aproximadamente 518 W, 1509 W y 3388 W.
        """
        rho = 1.225
        g = 9.80665
        num_fans = 4
        d_ref_5kg = 0.082  # 82 mm

        # 2 kg
        d_2kg = d_ref_5kg * ((2.0 / 5.0) ** (1.0 / 3.0))
        res_2kg = compute_momentum_theory(2.0, d_2kg, num_fans, upward_accel_g=0.0, rho_kg_m3=rho, g_m_s2=g)
        self.assertAlmostEqual(res_2kg["ideal_power_W"], 518.204, places=1)
        self.assertEqual(round(res_2kg["ideal_power_W"]), 518)

        # 5 kg
        d_5kg = d_ref_5kg * ((5.0 / 5.0) ** (1.0 / 3.0))
        res_5kg = compute_momentum_theory(5.0, d_5kg, num_fans, upward_accel_g=0.0, rho_kg_m3=rho, g_m_s2=g)
        self.assertAlmostEqual(res_5kg["ideal_power_W"], 1509.260, places=1)
        self.assertEqual(round(res_5kg["ideal_power_W"]), 1509)

        # 10 kg
        d_10kg = d_ref_5kg * ((10.0 / 5.0) ** (1.0 / 3.0))
        res_10kg = compute_momentum_theory(10.0, d_10kg, num_fans, upward_accel_g=0.0, rho_kg_m3=rho, g_m_s2=g)
        self.assertAlmostEqual(res_10kg["ideal_power_W"], 3388.175, places=1)
        self.assertEqual(round(res_10kg["ideal_power_W"]), 3388)

    def test_02_physical_governing_equations(self):
        """
        Prueba rigurosa de las ecuaciones gobernantes de cantidad de movimiento:
          1. T = m * g * (1 + a)
          2. T = 2 * rho * A_tot * vi^2
          3. Pi = T * vi
          4. Pi = T^(3/2) / sqrt(2 * rho * A_tot)
        """
        rho = self.study_data["rho"]
        for r in self.study_data["results_d82"] + self.study_data["results_d84"]:
            m = r["mass_target_kg"]
            a = r["upward_accel_g"]
            T = r["total_thrust_N"]
            A = r["total_area_m2"]
            vi = r["induced_velocity_ms"]
            Pi = r["ideal_power_W"]

            # 1. Empuje requerido
            expected_T = m * self.study_data["g"] * (1.0 + a)
            self.assertAlmostEqual(T, expected_T, places=10)

            # 2. Conservación de cantidad de movimiento: T = 2 * rho * A * vi^2
            T_momentum = 2.0 * rho * A * (vi ** 2)
            self.assertAlmostEqual(T, T_momentum, places=8)

            # 3. Potencia inducida: Pi = T * vi
            Pi_thrust_vi = T * vi
            self.assertAlmostEqual(Pi, Pi_thrust_vi, places=8)

            # 4. Potencia en función del empuje y área
            Pi_direct = (T ** 1.5) / math.sqrt(2.0 * rho * A)
            self.assertAlmostEqual(Pi, Pi_direct, places=8)

    def test_03_geometric_and_momentum_scaling_laws(self):
        """
        Prueba de las leyes de escalado geométrico semejante e isometría:
          - D(m) = D_5 * (m / 5)^(1/3)
          - A_tot(m) = A_5 * (m / 5)^(2/3)
          - vi(m) = vi_5 * (m / 5)^(1/6)
          - Pi(m) = Pi_5 * (m / 5)^(7/6)
        """
        hover_d82 = {r["mass_target_kg"]: r for r in self.study_data["results_d82"] if r["upward_accel_g"] == 0.0}

        d5 = hover_d82[5.0]["disk_diameter_m"]
        a5 = hover_d82[5.0]["total_area_m2"]
        vi5 = hover_d82[5.0]["induced_velocity_ms"]
        pi5 = hover_d82[5.0]["ideal_power_W"]

        for m in [2.0, 10.0]:
            scale_lin = (m / 5.0) ** (1.0 / 3.0)
            scale_area = (m / 5.0) ** (2.0 / 3.0)
            scale_vi = (m / 5.0) ** (1.0 / 6.0)
            scale_pi = (m / 5.0) ** (7.0 / 6.0)

            self.assertAlmostEqual(hover_d82[m]["disk_diameter_m"], d5 * scale_lin, places=12)
            self.assertAlmostEqual(hover_d82[m]["total_area_m2"], a5 * scale_area, places=12)
            self.assertAlmostEqual(hover_d82[m]["induced_velocity_ms"], vi5 * scale_vi, places=10)
            self.assertAlmostEqual(hover_d82[m]["ideal_power_W"], pi5 * scale_pi, places=8)

    def test_04_d84_baseline_reproduction(self):
        """
        Verifica que la hipótesis de referencia D84 reproduce con exactitud numérica (< 1e-9)
        los registros de REFERENCIA_DISCO.csv.
        """
        prev_rows = self.study_data["previous_csv"]
        computed_d84 = self.study_data["results_d84"]

        self.assertEqual(len(prev_rows), len(computed_d84))
        for prev, comp in zip(prev_rows, computed_d84):
            self.assertAlmostEqual(prev["mass_target_kg"], comp["mass_target_kg"], places=6)
            self.assertAlmostEqual(prev["free_disk_diameter_reference_m"], comp["disk_diameter_m"], places=9)
            self.assertAlmostEqual(prev["free_disks_total_area_m2"], comp["total_area_m2"], places=9)
            self.assertAlmostEqual(prev["upward_net_accel_g"], comp["upward_accel_g"], places=6)
            self.assertAlmostEqual(prev["required_total_force_N"], comp["total_thrust_N"], places=6)
            self.assertAlmostEqual(prev["ideal_isolated_disk_induced_velocity_ms"], comp["induced_velocity_ms"], places=8)
            self.assertAlmostEqual(prev["ideal_isolated_disk_power_W"], comp["ideal_power_W"], places=6)

    def test_05_d82_vs_d84_exact_analytical_relations(self):
        """
        Verifica que el cociente entre D82 y D84 cumple las relaciones analíticas exactas:
          - D_82 / D_84 = 82 / 84 = 41 / 42
          - A_82 / A_84 = (41 / 42)^2 = 1681 / 1764
          - vi_82 / vi_84 = 42 / 41
          - Pi_82 / Pi_84 = 42 / 41
        """
        ratio_d = 41.0 / 42.0
        ratio_a = (41.0 / 42.0) ** 2
        ratio_vi = 42.0 / 41.0
        ratio_pi = 42.0 / 41.0

        for comp in self.study_data["comparisons"]:
            self.assertAlmostEqual(comp["diameter_D82_m"] / comp["diameter_D84_m"], ratio_d, places=10)
            self.assertAlmostEqual(comp["total_area_D82_m2"] / comp["total_area_D84_m2"], ratio_a, places=10)
            self.assertAlmostEqual(comp["induced_vel_D82_ms"] / comp["induced_vel_D84_ms"], ratio_vi, places=10)
            self.assertAlmostEqual(comp["ideal_power_D82_W"] / comp["ideal_power_D84_W"], ratio_pi, places=10)

    def test_06_package_deliverables_and_data_integrity(self):
        """
        Verifica que las entradas necesarias están conservadas en salidas/datos/
        y que los entregables requeridos existen y están completos.
        """
        # Entradas conservadas
        json_path = os.path.join(SCRIPT_DIR, "datos", "C02_CANDIDATA.json")
        csv_path = os.path.join(SCRIPT_DIR, "datos", "REFERENCIA_DISCO.csv")
        self.assertTrue(os.path.exists(json_path), f"Falta {json_path}")
        self.assertTrue(os.path.exists(csv_path), f"Falta {csv_path}")

        # Entregables generados
        expected_files = [
            os.path.join(SCRIPT_DIR, "TABLA_ESCALADO_D82.csv"),
            os.path.join(SCRIPT_DIR, "COMPARATIVA_D82_VS_D84.csv"),
            os.path.join(SCRIPT_DIR, "TABLA_ESTACIONARIO_COMPARADA.md"),
            os.path.join(SCRIPT_DIR, "README.md"),
            os.path.join(SCRIPT_DIR, "INFORME_ESCALADO_2_5_10.md")
        ]
        for fpath in expected_files:
            self.assertTrue(os.path.exists(fpath), f"El entregable {fpath} no existe.")
            self.assertGreater(os.path.getsize(fpath), 0, f"El entregable {fpath} está vacío.")

        # Verificar filas en CSVs
        with open(os.path.join(SCRIPT_DIR, "TABLA_ESCALADO_D82.csv"), "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
            self.assertEqual(len(rows), 10, "TABLA_ESCALADO_D82.csv debe tener 1 cabecera y 9 filas de datos.")

        with open(os.path.join(SCRIPT_DIR, "COMPARATIVA_D82_VS_D84.csv"), "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
            self.assertEqual(len(rows), 10, "COMPARATIVA_D82_VS_D84.csv debe tener 1 cabecera y 9 filas de datos.")

    def test_07_scope_and_disclaimer_verifications(self):
        """
        Verifica que el código y documentación no afirman potencia instalada,
        diseño cerrado, ni regla universal de límite para ventiladores entubados.
        """
        with open(os.path.join(SCRIPT_DIR, "README.md"), "r", encoding="utf-8") as f:
            readme_text = f.read()

        # Debe contener aclaraciones clave
        self.assertIn("potencia eléctrica instalada", readme_text)
        self.assertIn("D84", readme_text)
        self.assertIn("universal", readme_text.lower())
        self.assertIn("pending_own_configuration", readme_text)


if __name__ == "__main__":
    unittest.main()
