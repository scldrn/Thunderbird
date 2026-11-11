#!/usr/bin/env python3
"""
test_auditoria.py - Suite de pruebas unitarias y de integración para la auditoría de la BOM C02.

Ejecución reproducible con python3 estándar (unittest) sobre entradas copiadas en salidas/.
Verifica:
  1. Inmutabilidad de referencias maestras en entradas/.
  2. Integridad criptográfica de entradas copiadas en salidas/entradas/.
  3. Censo riguroso de registros (316 totales, 0 nombres duplicados).
  4. Conteo exacto de asignados (262) y reservas físicas sin asignar (54).
  5. Clasificación funcional de los 10 roles asumidos y 12 scopes.
  6. Tratamiento estricto de reservas: NO se convierten a cero (masa vacía, volumen > 0).
  7. Coincidencia unívoca con la lista de piezas no identificadas del JSON.
  8. Reconciliación matemática exacta de las 3 hipótesis (mixta_1600, ligera_1200, aluminio_2700).
  9. Reconciliación del Centro de Gravedad en coordenadas CAD y FLU (inversión de signos X, Y).
 10. Integridad de la ley volumétrica nominal (V * rho * 1e-9) para todas las filas asignadas.
 11. Simetría bilateral estricta (Y -> -Y) en módulos de proa (0 vs 1) y popa (2 vs 3).
 12. Detección y cuantificación de diferencias longitudinales proa/popa (camisa_cuna y puertos).
 13. Verificación de componentes geométricos repetidos (96 casquillos, 16 servos, 80 álabes/enlaces).
 14. Estado de no homologación física (sin masa real, modelo abierto para simulación predictiva).
 15. Generación y coherencia del CSV agregado por roles en salidas/.
"""

import csv
import hashlib
import json
import os
import unittest
from pathlib import Path

from auditar_bom import load_data, audit_records, write_grouped_csv, resolve_default_paths


class TestAuditoriaBOM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.csv_path, cls.json_path, cls.out_csv_path = resolve_default_paths()

        # Rutas absolutas para verificación de inmutabilidad
        cls.ws_dir = Path(__file__).resolve().parent.parent
        cls.ref_csv = cls.ws_dir / "entradas/investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/BOM_GEOMETRICA_PARCIAL.csv"
        cls.ref_json = cls.ws_dir / "entradas/investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/MASA_INERCIA_PARCIAL.json"

        cls.copied_csv = Path(cls.csv_path)
        cls.copied_json = Path(cls.json_path)

        cls.expected_hashes = {
            "csv": "36f5b043aed553d7484421bb45f9aa0e19c64d6989141d587f1fb4d1f0e9840b",
            "json": "4b8df67e7161d2eed06bb21e97973f966a9ee34648a9f73661e915cf41be18f6"
        }

        cls.csv_rows, cls.json_data = load_data(str(cls.copied_csv), str(cls.copied_json))
        cls.results = audit_records(cls.csv_rows, cls.json_data)

    def test_01_immutability_of_reference_inputs(self):
        """Verifica que las referencias maestras en entradas/ permanecen intactas y sin modificaciones."""
        self.assertTrue(self.ref_csv.exists(), f"El archivo de referencia {self.ref_csv} no existe.")
        self.assertTrue(self.ref_json.exists(), f"El archivo de referencia {self.ref_json} no existe.")

        with open(self.ref_csv, "rb") as f:
            h_csv = hashlib.sha256(f.read()).hexdigest()
        with open(self.ref_json, "rb") as f:
            h_json = hashlib.sha256(f.read()).hexdigest()

        self.assertEqual(h_csv, self.expected_hashes["csv"], "ALERTA: BOM_GEOMETRICA_PARCIAL.csv en entradas/ fue modificado.")
        self.assertEqual(h_json, self.expected_hashes["json"], "ALERTA: MASA_INERCIA_PARCIAL.json en entradas/ fue modificado.")

    def test_02_copied_inputs_integrity(self):
        """Verifica que las entradas copiadas en salidas/ son réplicas bit a bit exactas de las referencias."""
        self.assertTrue(self.copied_csv.exists(), f"La entrada copiada {self.copied_csv} no existe.")
        self.assertTrue(self.copied_json.exists(), f"La entrada copiada {self.copied_json} no existe.")

        with open(self.copied_csv, "rb") as f:
            h_csv = hashlib.sha256(f.read()).hexdigest()
        with open(self.copied_json, "rb") as f:
            h_json = hashlib.sha256(f.read()).hexdigest()

        self.assertEqual(h_csv, self.expected_hashes["csv"], "Discrepancia en hash de entrada copiada CSV.")
        self.assertEqual(h_json, self.expected_hashes["json"], "Discrepancia en hash de entrada copiada JSON.")

    def test_03_total_records_count_and_no_duplicate_names(self):
        """Verifica que la BOM contiene exactamente 316 registros y ningún nombre duplicado."""
        self.assertEqual(self.results["total_records"], 316)
        self.assertEqual(self.results["reconciliation"]["json_geom_records"], 316)
        self.assertTrue(self.results["reconciliation"]["records_match"])
        self.assertEqual(len(self.results["duplicate_names"]), 0, f"Se hallaron nombres duplicados: {self.results['duplicate_names']}")

    def test_04_assigned_and_unassigned_counts(self):
        """Verifica el recuento exacto de filas asignadas (262) y reservas sin masa asignada (54)."""
        self.assertEqual(self.results["assigned_count"], 262)
        self.assertEqual(self.results["unassigned_count"], 54)
        self.assertEqual(self.results["assigned_count"] + self.results["unassigned_count"], 316)

    def test_05_roles_and_scopes_classification(self):
        """Verifica la existencia y conteo exacto de los 10 roles asumidos y 12 scopes."""
        roles = self.results["roles"]
        scopes = self.results["scopes"]

        self.assertEqual(len(roles), 10)
        self.assertEqual(len(scopes), 12)

        expected_roles = {
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

        for role, count in expected_roles.items():
            self.assertIn(role, roles)
            self.assertEqual(roles[role]["count"], count, f"Discrepancia en el conteo del rol {role}")

    def test_06_unassigned_rows_not_treated_as_zero(self):
        """
        Verifica que las 54 filas sin masa asignada NO tienen valor cero, sino vacío,
        y representan reservas de hardware con volumen estrictamente positivo (18,45% del total).
        """
        unassigned_rows = self.results["unassigned_rows"]
        self.assertEqual(len(unassigned_rows), 54)

        for row in unassigned_rows:
            raw_mass = row.get("assigned_mass_mixta_kg", "")
            self.assertEqual(raw_mass.strip(), "", f"Fila {row['name']} contiene masa espuria: {raw_mass}")

            raw_rho = row.get("rho_mixta_ASSUMED_kg_m3", "")
            self.assertEqual(raw_rho.strip(), "", f"Fila {row['name']} contiene densidad espuria: {raw_rho}")

            vol = float(row["volume_mm3"])
            self.assertGreater(vol, 0.0, f"Fila {row['name']} tiene volumen no positivo: {vol}")

            self.assertIn(row["assumed_role"], ["unknown_device_or_interface", "unknown_hardware_or_empty_interface"])

        self.assertAlmostEqual(self.results["unassigned_volume_pct"], 18.45028, places=3)

    def test_07_unassigned_names_match_json_unidentified_records(self):
        """Verifica que los 54 nombres de reservas coinciden biunívocamente con el JSON."""
        rec = self.results["reconciliation"]
        self.assertTrue(rec["unassigned_count_match"])
        self.assertTrue(rec["unidentified_names_match"])
        self.assertTrue(rec["unidentified_sets_match"])

    def test_08_reconciliation_mixed_hypothesis(self):
        """Verifica que la hipótesis mixta_1600 coincide con el JSON a precisión de máquina IEEE-754."""
        hyp = self.results["hypotheses"]["mixta_1600"]
        self.assertLess(hyp["mass_diff_abs"], 1e-12)
        self.assertAlmostEqual(hyp["calculated_mass_kg"], 2.783989739397547, places=12)

        self.assertLess(hyp["remaining_diff_abs"], 1e-12)
        self.assertAlmostEqual(hyp["calculated_remaining_kg"], 1.4660102606024532, places=12)

        for d in hyp["cg_cad_diff"]:
            self.assertLess(d, 1e-12)
        for d in hyp["cg_flu_diff"]:
            self.assertLess(d, 1e-12)

        # Inversión de signos CAD -> FLU
        cg_cad = hyp["calculated_cg_cad"]
        cg_flu = hyp["calculated_cg_flu"]
        self.assertAlmostEqual(cg_flu[0], -cg_cad[0], places=14)
        self.assertAlmostEqual(cg_flu[1], -cg_cad[1], places=14)
        self.assertAlmostEqual(cg_flu[2], cg_cad[2], places=14)

    def test_09_reconciliation_lightweight_hypothesis(self):
        """Verifica que la hipótesis ligera_1200 coincide exactamente con el JSON."""
        hyp = self.results["hypotheses"]["ligera_1200"]
        self.assertLess(hyp["mass_diff_abs"], 1e-12)
        self.assertAlmostEqual(hyp["calculated_mass_kg"], 2.045840504993601, places=12)
        self.assertAlmostEqual(hyp["calculated_remaining_kg"], 2.204159495006399, places=12)

        for d in hyp["cg_cad_diff"]:
            self.assertLess(d, 1e-12)
        for d in hyp["cg_flu_diff"]:
            self.assertLess(d, 1e-12)

    def test_10_reconciliation_aluminium_hypothesis_and_deficit(self):
        """Verifica que la hipótesis aluminio_2700 coincide con el JSON y evidencia déficit estructural."""
        hyp = self.results["hypotheses"]["aluminio_2700"]
        self.assertLess(hyp["mass_diff_abs"], 1e-12)
        self.assertAlmostEqual(hyp["calculated_mass_kg"], 4.421342235936211, places=12)

        # Déficit de -171,34 g frente al presupuesto de 5 kg
        self.assertLess(hyp["remaining_diff_abs"], 1e-12)
        self.assertAlmostEqual(hyp["calculated_remaining_kg"], -0.17134223593621112, places=12)
        self.assertLess(hyp["calculated_remaining_kg"], 0.0)

        for d in hyp["cg_cad_diff"]:
            self.assertLess(d, 1e-12)
        for d in hyp["cg_flu_diff"]:
            self.assertLess(d, 1e-12)

    def test_11_density_formula_verification(self):
        """Verifica que para cada una de las 262 filas asignadas, m = V * rho * 1e-9 (residuo < 1e-15)."""
        self.assertLess(self.results["reconciliation"]["formula_max_diff"], 1e-15)

    def test_12_bilateral_symmetry_y_axis(self):
        """Verifica la simetría geométrica bilateral perfecta (Y -> -Y) entre módulos port y starboard."""
        sym = self.results["symmetry"]
        self.assertEqual(len(sym["sym_0_1_diffs"]), 0, f"Discrepancia en simetría proa (0 vs 1): {sym['sym_0_1_diffs']}")
        self.assertEqual(len(sym["sym_2_3_diffs"]), 0, f"Discrepancia en simetría popa (2 vs 3): {sym['sym_2_3_diffs']}")

    def test_13_longitudinal_differences_forward_aft(self):
        """
        Verifica y cuantifica la asimetría física proa vs popa (módulos 0 vs 2):
        la camisa_cuna varía en 5154,92 mm3 y los puertos difieren por estrechamiento del fuselaje.
        """
        diff = self.results["symmetry"]["diff_0_2"]
        self.assertEqual(len(diff), 1)
        part_name, v0, v2, dv = diff[0]
        self.assertEqual(part_name, "camisa_cuna_y_soportes")
        self.assertAlmostEqual(v0, 93182.1364, places=3)
        self.assertAlmostEqual(v2, 88027.2199, places=3)
        self.assertAlmostEqual(dv, 5154.9164, places=3)

    def test_14_hardware_unqualified_status(self):
        """Verifica que ningún registro posee masa real calificada y el modelo no está cerrado físicamente."""
        hw = self.results["hardware_status"]
        self.assertEqual(hw["actual_mass_count"], 0)
        self.assertEqual(hw["actual_mat_count"], 0)
        self.assertEqual(hw["qualified_hw_count"], 0)
        self.assertFalse(hw["physical_mass_CG_and_inertia_closed"])
        self.assertFalse(hw["inertia_model_acceptance_for_predictive_flight"])
        self.assertTrue(hw["assumptions_are_not_measurements"])

    def test_15_grouped_csv_generation_and_consistency(self):
        """Verifica que el CSV agrupado en salidas/ se genera correctamente y mantiene balance total."""
        out_csv = write_grouped_csv(self.results, str(self.out_csv_path))
        self.assertTrue(os.path.exists(out_csv))

        with open(out_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 10)
        self.assertEqual(sum(int(r["total_records"]) for r in rows), 316)
        self.assertEqual(sum(int(r["assigned_records"]) for r in rows), 262)
        self.assertEqual(sum(int(r["unassigned_records"]) for r in rows), 54)
        self.assertAlmostEqual(sum(float(r["total_volume_mm3"]) for r in rows), self.results["total_volume_mm3"], places=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
