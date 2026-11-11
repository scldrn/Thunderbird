#!/usr/bin/env python3
"""
test_auditoria.py - Suite de pruebas unitarias y de integración para la auditoría de la BOM C02.

Ejecución con python3 estándar (unittest).
Verifica:
  - Censo de registros (316 totales, 262 asignados, 54 reservas).
  - Clasificación de los 10 roles funcionales.
  - Detección de filas sin masa asignada (tratamiento como reserva física, NO cero).
  - Coincidencia con lista de registros no identificados del JSON.
  - Reconciliación matemática de sumas de masa de la hipótesis mixta (error < 1e-12 kg).
  - Reconciliación del Centro de Gravedad en coordenadas CAD y FLU.
  - Integridad de densidades nominales (V * rho * 1e-9).
  - Consistencia del CSV agrupado generado.
  - Inmutabilidad de los archivos de referencia en entradas/.
"""

import csv
import hashlib
import json
import os
import unittest
from pathlib import Path

from auditar_bom import load_data, audit_records, write_grouped_csv


class TestAuditoriaBOM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_dir = Path(__file__).resolve().parent.parent
        cls.csv_path = cls.base_dir / "entradas/investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/BOM_GEOMETRICA_PARCIAL.csv"
        cls.json_path = cls.base_dir / "entradas/investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/MASA_INERCIA_PARCIAL.json"
        cls.informe_path = cls.base_dir / "entradas/investigacion-aeronautica/ejecucion/G3/C02/INFORME-C02.md"
        cls.out_csv_path = cls.base_dir / "salidas/bom_agrupada_roles.csv"

        # Hashes de referencia conocidos para verificar no alteración
        cls.known_hashes = {
            cls.informe_path: "2a3982a7315456faf143d1f0208cd6654668a2d72ff42c1649886b034dac5db1",
            cls.csv_path: "36f5b043aed553d7484421bb45f9aa0e19c64d6989141d587f1fb4d1f0e9840b",
            cls.json_path: "4b8df67e7161d2eed06bb21e97973f966a9ee34648a9f73661e915cf41be18f6"
        }

        cls.csv_rows, cls.json_data = load_data(str(cls.csv_path), str(cls.json_path))
        cls.results = audit_records(cls.csv_rows, cls.json_data)

    def test_01_immutability_of_reference_inputs(self):
        """Verifica que las referencias en entradas/ permanecen intactas y sin modificaciones."""
        for path, expected_hash in self.known_hashes.items():
            self.assertTrue(path.exists(), f"El archivo de referencia {path} no existe.")
            with open(path, "rb") as f:
                computed_hash = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                computed_hash,
                expected_hash,
                f"ALERTA: El archivo de referencia {path} fue alterado! Hash esperado {expected_hash}, obtenido {computed_hash}"
            )

    def test_02_total_records_count(self):
        """Verifica que la BOM contiene exactamente 316 registros geométricos."""
        self.assertEqual(self.results["total_records"], 316)
        self.assertEqual(self.results["reconciliation"]["json_geom_records"], 316)
        self.assertTrue(self.results["reconciliation"]["records_match"])

    def test_03_assigned_and_unassigned_counts(self):
        """Verifica el recuento de filas con masa asignada (262) y reservas sin masa asignada (54)."""
        self.assertEqual(self.results["assigned_count"], 262)
        self.assertEqual(self.results["unassigned_count"], 54)
        self.assertEqual(self.results["assigned_count"] + self.results["unassigned_count"], 316)

    def test_04_roles_classification(self):
        """Verifica la existencia y conteo exacto de los 10 roles funcionales asumidos."""
        roles = self.results["roles"]
        self.assertEqual(len(roles), 10)

        expected_counts = {
            "bushing_material_sensitivity": 96,
            "integral_vane_linkage_material_sensitivity": 80,
            "unknown_device_or_interface": 44,
            "envelope_material_sensitivity": 42,
            "seal_or_clamp_density_assumption": 11,
            "frame_support_density_assumption": 11,
            "unknown_hardware_or_empty_interface": 10,
            "steel_density_assumption": 10,
            "rotor_or_carrier_material_sensitivity": 8,
            "shaft_steel_density_assumption": 4,
        }

        for role, count in expected_counts.items():
            self.assertIn(role, roles)
            self.assertEqual(roles[role]["count"], count, f"Discrepancia en conteo del rol {role}")

    def test_05_unassigned_rows_not_treated_as_zero(self):
        """
        Verifica que las 54 filas sin masa asignada NO tienen asignado 0.0 kg ni se tratan
        como masa física nula. Verifican reservas volumétricas positivas no calificadas.
        """
        unassigned_rows = self.results["unassigned_rows"]
        self.assertEqual(len(unassigned_rows), 54)

        for row in unassigned_rows:
            # La masa asignada en el CSV debe estar vacía (no "0.0" ni "0")
            raw_mass = row.get("assigned_mass_mixta_kg", "")
            self.assertEqual(raw_mass.strip(), "", f"Fila {row['name']} tiene valor de masa inesperado: {raw_mass}")

            # La densidad debe estar vacía
            raw_rho = row.get("rho_mixta_ASSUMED_kg_m3", "")
            self.assertEqual(raw_rho.strip(), "", f"Fila {row['name']} tiene densidad inesperada: {raw_rho}")

            # El volumen debe ser estrictamente positivo (representa una reserva física)
            vol = float(row["volume_mm3"])
            self.assertGreater(vol, 0.0, f"Fila {row['name']} tiene volumen no positivo: {vol}")

            # Rol debe ser explícitamente desconocido
            self.assertIn(row["assumed_role"], ["unknown_device_or_interface", "unknown_hardware_or_empty_interface"])

        # Volumen de reservas debe ser significativo (~18.45% del total)
        self.assertAlmostEqual(self.results["unassigned_volume_pct"], 18.45028, places=3)

    def test_06_unassigned_names_match_json_unidentified_records(self):
        """Verifica que los 54 nombres de filas sin masa coinciden exactamente con el JSON."""
        rec = self.results["reconciliation"]
        self.assertEqual(rec["json_unidentified_count"], 54)
        self.assertTrue(rec["unassigned_count_match"])
        self.assertTrue(rec["unidentified_names_match"])
        self.assertTrue(rec["unidentified_sets_match"])

    def test_07_reconciliation_mixed_hypothesis_mass(self):
        """
        Verifica que la suma de masas asignadas en el CSV coincide con partial_assigned_mass_kg
        en el JSON para la hipótesis mixta_1600 (diferencia < 1e-12 kg).
        """
        rec = self.results["reconciliation"]
        self.assertLess(rec["mass_diff_abs"], 1e-12)
        self.assertAlmostEqual(self.results["total_mass_assigned_kg"], 2.783989739397547, places=12)

        # Verificación del remanente frente al objetivo de 5 kg
        self.assertLess(rec["remanent_diff_abs"], 1e-12)
        self.assertAlmostEqual(rec["calculated_remanent"], 1.4660102606024532, places=12)

    def test_08_reconciliation_center_of_gravity(self):
        """Verifica que el Centro de Gravedad calculado coincide con el JSON en CAD y FLU."""
        rec = self.results["reconciliation"]
        for diff in rec["cg_cad_diff"]:
            self.assertLess(diff, 1e-12)
        for diff in rec["cg_flu_diff"]:
            self.assertLess(diff, 1e-12)

        # Verificación de la ley de transformación CAD -> FLU (x_FLU = -x_CAD, y_FLU = -y_CAD, z_FLU = z_CAD)
        cg_cad = self.results["cg_cad"]
        cg_flu = self.results["cg_flu"]
        self.assertAlmostEqual(cg_flu[0], -cg_cad[0], places=15)
        self.assertAlmostEqual(cg_flu[1], -cg_cad[1], places=15)
        self.assertAlmostEqual(cg_flu[2], cg_cad[2], places=15)

    def test_09_density_formula_verification(self):
        """Verifica que para cada una de las 262 filas asignadas, masa = volumen * densidad * 1e-9."""
        rec = self.results["reconciliation"]
        self.assertLess(rec["formula_max_diff"], 1e-15)

    def test_10_hardware_unqualified_status(self):
        """Verifica que ninguna fila tiene masa real ni hardware calificado."""
        hw = self.results["hardware_status"]
        self.assertEqual(hw["actual_mass_count"], 0)
        self.assertEqual(hw["actual_mat_count"], 0)
        self.assertEqual(hw["qualified_hw_count"], 0)
        self.assertFalse(hw["physical_mass_CG_and_inertia_closed"])
        self.assertFalse(hw["inertia_model_acceptance_for_predictive_flight"])
        self.assertTrue(hw["assumptions_are_not_measurements"])

    def test_11_grouped_csv_generation_and_consistency(self):
        """Verifica que el CSV agrupado generado en salidas/ es válido y coherente."""
        out_csv = write_grouped_csv(self.results, str(self.out_csv_path))
        self.assertTrue(os.path.exists(out_csv))

        with open(out_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 10)  # 10 roles
        sum_total_records = sum(int(r["total_records"]) for r in rows)
        sum_assigned_records = sum(int(r["assigned_records"]) for r in rows)
        sum_unassigned_records = sum(int(r["unassigned_records"]) for r in rows)
        sum_volume_mm3 = sum(float(r["total_volume_mm3"]) for r in rows)

        self.assertEqual(sum_total_records, 316)
        self.assertEqual(sum_assigned_records, 262)
        self.assertEqual(sum_unassigned_records, 54)
        self.assertAlmostEqual(sum_volume_mm3, self.results["total_volume_mm3"], places=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
