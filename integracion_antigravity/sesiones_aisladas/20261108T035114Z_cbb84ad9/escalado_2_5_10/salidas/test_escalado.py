#!/usr/bin/env python3
"""
test_escalado.py
----------------
Suite de pruebas unitarias y de verificación matemática para el escalado
geométrico 2, 5, 10 kg con base D82 y comparación con D84.

Verifica:
  1. Reproducción idéntica de REFERENCIA_DISCO.csv para el caso base D84.
  2. Cumplimiento estricto de las leyes de semejanza geométrica (D ~ m^(1/3), A ~ m^(2/3)).
  3. Cumplimiento de la teoría de cantidad de movimiento (vi ~ m^(1/6), Pi ~ m^(7/6)).
  4. Relaciones analíticas exactas entre D82 y D84 (41/42, (41/42)^2, 42/41).
  5. Consistencia física interna (T = 2*rho*A*vi^2, Pi = T*vi).
  6. Integridad de los archivos generados en salidas/.
"""

import unittest
import math
import os
import sys
import csv
import json

# Asegurar que el directorio de salidas esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from escalado_geometrico import (
    load_reference_inputs,
    compute_momentum_theory,
    run_scaling_study,
    export_deliverables
)


class TestEscaladoGeometrico(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.study_data = run_scaling_study()
        export_deliverables(cls.study_data)

    def test_01_reference_reproduction_d84(self):
        """Verifica que el modelo reproduce REFERENCIA_DISCO.csv para D84 con error < 1e-9."""
        previous_rows = self.study_data["previous_csv"]
        computed_d84 = self.study_data["results_d84"]
        
        self.assertEqual(len(previous_rows), len(computed_d84))
        
        for prev, comp in zip(previous_rows, computed_d84):
            self.assertAlmostEqual(prev["mass_target_kg"], comp["mass_target_kg"], places=6)
            self.assertAlmostEqual(prev["free_disk_diameter_reference_m"], comp["disk_diameter_m"], places=9)
            self.assertAlmostEqual(prev["free_disks_total_area_m2"], comp["total_area_m2"], places=9)
            self.assertAlmostEqual(prev["upward_net_accel_g"], comp["upward_accel_g"], places=6)
            self.assertAlmostEqual(prev["required_total_force_N"], comp["total_thrust_N"], places=6)
            self.assertAlmostEqual(prev["ideal_isolated_disk_induced_velocity_ms"], comp["induced_velocity_ms"], places=8)
            self.assertAlmostEqual(prev["ideal_isolated_disk_power_W"], comp["ideal_power_W"], places=6)

    def test_02_geometric_similarity_diameter(self):
        """Verifica que el diámetro escala exactamente como D(m) = D_5 * (m/5)^(1/3)."""
        d82_5kg = self.study_data["d82_ref_5kg"]  # 0.082 m
        self.assertEqual(d82_5kg, 0.082)
        
        # Filtrar resultados hover
        hover_d82 = {r["mass_target_kg"]: r for r in self.study_data["results_d82"] if r["upward_accel_g"] == 0.0}
        
        expected_d2 = d82_5kg * ((2.0 / 5.0) ** (1.0 / 3.0))
        expected_d5 = d82_5kg
        expected_d10 = d82_5kg * ((10.0 / 5.0) ** (1.0 / 3.0))
        
        self.assertAlmostEqual(hover_d82[2.0]["disk_diameter_m"], expected_d2, places=12)
        self.assertAlmostEqual(hover_d82[5.0]["disk_diameter_m"], expected_d5, places=12)
        self.assertAlmostEqual(hover_d82[10.0]["disk_diameter_m"], expected_d10, places=12)

    def test_03_geometric_similarity_area(self):
        """Verifica que el área total escala exactamente como A(m) = A_5 * (m/5)^(2/3)."""
        hover_d82 = {r["mass_target_kg"]: r for r in self.study_data["results_d82"] if r["upward_accel_g"] == 0.0}
        a5 = hover_d82[5.0]["total_area_m2"]
        
        expected_a2 = a5 * ((2.0 / 5.0) ** (2.0 / 3.0))
        expected_a10 = a5 * ((10.0 / 5.0) ** (2.0 / 3.0))
        
        self.assertAlmostEqual(hover_d82[2.0]["total_area_m2"], expected_a2, places=12)
        self.assertAlmostEqual(hover_d82[10.0]["total_area_m2"], expected_a10, places=12)
        
        # Para 4 rotores, Area_tot = 4 * (pi * (D/2)^2) = pi * D^2
        for m, r in hover_d82.items():
            expected_pi_d2 = math.pi * (r["disk_diameter_m"] ** 2)
            self.assertAlmostEqual(r["total_area_m2"], expected_pi_d2, places=12)

    def test_04_momentum_theory_induced_velocity_scaling(self):
        """Verifica que en hover la velocidad inducida escala exactamente como vi ~ m^(1/6)."""
        hover_d82 = {r["mass_target_kg"]: r for r in self.study_data["results_d82"] if r["upward_accel_g"] == 0.0}
        vi5 = hover_d82[5.0]["induced_velocity_ms"]
        
        expected_vi2 = vi5 * ((2.0 / 5.0) ** (1.0 / 6.0))
        expected_vi10 = vi5 * ((10.0 / 5.0) ** (1.0 / 6.0))
        
        self.assertAlmostEqual(hover_d82[2.0]["induced_velocity_ms"], expected_vi2, places=10)
        self.assertAlmostEqual(hover_d82[10.0]["induced_velocity_ms"], expected_vi10, places=10)

    def test_05_momentum_theory_power_scaling(self):
        """Verifica que en hover la potencia ideal escala exactamente como Pi ~ m^(7/6)."""
        hover_d82 = {r["mass_target_kg"]: r for r in self.study_data["results_d82"] if r["upward_accel_g"] == 0.0}
        pi5 = hover_d82[5.0]["ideal_power_W"]
        
        expected_pi2 = pi5 * ((2.0 / 5.0) ** (7.0 / 6.0))
        expected_pi10 = pi5 * ((10.0 / 5.0) ** (7.0 / 6.0))
        
        self.assertAlmostEqual(hover_d82[2.0]["ideal_power_W"], expected_pi2, places=8)
        self.assertAlmostEqual(hover_d82[10.0]["ideal_power_W"], expected_pi10, places=8)

    def test_06_d82_vs_d84_exact_analytical_relations(self):
        """Verifica las relaciones analíticas exactas derivadas de D82 / D84 = 41 / 42."""
        ratio_d = 41.0 / 42.0
        ratio_a = (41.0 / 42.0) ** 2
        ratio_vi = 42.0 / 41.0
        ratio_p = 42.0 / 41.0
        
        for comp in self.study_data["comparisons"]:
            actual_ratio_d = comp["diameter_D82_m"] / comp["diameter_D84_m"]
            actual_ratio_a = comp["total_area_D82_m2"] / comp["total_area_D84_m2"]
            actual_ratio_vi = comp["induced_vel_D82_ms"] / comp["induced_vel_D84_ms"]
            actual_ratio_p = comp["ideal_power_D82_W"] / comp["ideal_power_D84_W"]
            
            self.assertAlmostEqual(actual_ratio_d, ratio_d, places=10)
            self.assertAlmostEqual(actual_ratio_a, ratio_a, places=10)
            self.assertAlmostEqual(actual_ratio_vi, ratio_vi, places=10)
            self.assertAlmostEqual(actual_ratio_p, ratio_p, places=10)
            
            # Deltas porcentuales teóricos exactos
            self.assertAlmostEqual(comp["pct_delta_diameter"], (ratio_d - 1.0) * 100.0, places=4)
            self.assertAlmostEqual(comp["pct_delta_total_area"], (ratio_a - 1.0) * 100.0, places=4)
            self.assertAlmostEqual(comp["pct_delta_induced_vel"], (ratio_vi - 1.0) * 100.0, places=4)
            self.assertAlmostEqual(comp["pct_delta_ideal_power"], (ratio_p - 1.0) * 100.0, places=4)

    def test_07_physical_governing_equations(self):
        """Verifica que se cumplen rigurosamente las ecuaciones fundamentales de cantidad de movimiento."""
        rho = self.study_data["rho"]
        for r in self.study_data["results_d82"] + self.study_data["results_d84"]:
            T = r["total_thrust_N"]
            A = r["total_area_m2"]
            vi = r["induced_velocity_ms"]
            Pi = r["ideal_power_W"]
            
            # 1. T = 2 * rho * A * vi^2
            T_recovered = 2.0 * rho * A * (vi ** 2)
            self.assertAlmostEqual(T, T_recovered, places=8)
            
            # 2. Pi = T * vi
            Pi_recovered = T * vi
            self.assertAlmostEqual(Pi, Pi_recovered, places=8)
            
            # 3. Pi = T^(3/2) / sqrt(2 * rho * A)
            Pi_formula = (T ** 1.5) / math.sqrt(2.0 * rho * A)
            self.assertAlmostEqual(Pi, Pi_formula, places=8)

    def test_08_deliverable_files_integrity(self):
        """Verifica que todos los archivos entregables existen, son legibles y no tienen valores nulos."""
        files = [
            "salidas/TABLA_ESCALADO_D82.csv",
            "salidas/COMPARATIVA_D82_VS_D84.csv",
            "salidas/TABLA_ESTACIONARIO_COMPARADA.md"
        ]
        for fpath in files:
            self.assertTrue(os.path.exists(fpath), f"El archivo {fpath} no existe.")
            self.assertGreater(os.path.getsize(fpath), 0, f"El archivo {fpath} está vacío.")
            
        # Verificar que TABLA_ESCALADO_D82.csv tiene exactamente 9 filas de datos + 1 cabecera
        with open("salidas/TABLA_ESCALADO_D82.csv", "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            self.assertEqual(len(reader), 10)
            
        # Verificar que COMPARATIVA_D82_VS_D84.csv tiene 9 filas de datos + 1 cabecera
        with open("salidas/COMPARATIVA_D82_VS_D84.csv", "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            self.assertEqual(len(reader), 10)


if __name__ == "__main__":
    unittest.main()
