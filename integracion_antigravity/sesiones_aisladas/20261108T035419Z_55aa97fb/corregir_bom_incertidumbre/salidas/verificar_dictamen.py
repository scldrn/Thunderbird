#!/usr/bin/env python3
"""
verificar_dictamen.py - Batería de Pruebas Automatizadas de Auditoría Aeronáutica

Verifica la integridad de datos, recuentos matemáticos, balances volumétricos,
reconciliación de hipótesis y estatus epistémico documentados en salidas/DICTAMEN.md.
Ejecuta exclusivamente sobre la biblioteca estándar de Python 3 en entorno aislado.
"""

import unittest
import csv
import json
import hashlib
from pathlib import Path


class TestDictamenBOM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Localización dinámica de directorios
        cls.base_dir = Path(__file__).resolve().parent.parent
        cls.entradas_dir = cls.base_dir / "entradas"
        cls.salidas_dir = cls.base_dir / "salidas"

        cls.csv_path = cls.entradas_dir / "investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/BOM_GEOMETRICA_PARCIAL.csv"
        cls.json_path = cls.entradas_dir / "investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/MASA_INERCIA_PARCIAL.json"
        cls.informe_previo_path = cls.entradas_dir / "investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_bom/salidas/INFORME_AUDITORIA_BOM.md"
        cls.revision_previa_path = cls.entradas_dir / "investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_bom/salidas/REVISION.md"

        # Carga de datos de referencia
        with open(cls.csv_path, "r", encoding="utf-8") as f:
            cls.bom_rows = list(csv.DictReader(f))

        with open(cls.json_path, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f)

        cls.assigned_rows = [r for r in cls.bom_rows if r["assigned_mass_mixta_kg"]]
        cls.unassigned_rows = [r for r in cls.bom_rows if not r["assigned_mass_mixta_kg"]]

    def test_01_referencias_sha256(self):
        """Comprueba la integridad criptográfica inmutable de las referencias maestras en entradas/."""
        expected_hashes = {
            self.csv_path: "36f5b043aed553d7484421bb45f9aa0e19c64d6989141d587f1fb4d1f0e9840b",
            self.json_path: "4b8df67e7161d2eed06bb21e97973f966a9ee34648a9f73661e915cf41be18f6",
            self.informe_previo_path: "9bd05035bb299ea4c8a1bc5a77c90407e2ca8507d8d197ae850b2a8a49e31795",
            self.revision_previa_path: "24b81ff5c31a1d6f453a4e30efb11a53bd264bba79db430b5b2a841165601d95",
        }
        for file_path, exp_sha in expected_hashes.items():
            self.assertTrue(file_path.exists(), f"El archivo {file_path} no existe.")
            with open(file_path, "rb") as f:
                sha = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(sha, exp_sha, f"Discrepancia SHA-256 en {file_path.name}")

    def test_02_censo_registros_totales(self):
        """Verifica que la BOM contiene exactamente 316 filas y que todos los nombres son únicos."""
        self.assertEqual(len(self.bom_rows), 316)
        names = [r["name"] for r in self.bom_rows]
        self.assertEqual(len(set(names)), 316, "Existen nombres de registros duplicados en la BOM")
        self.assertEqual(self.json_data["geometry_records"], 316)

    def test_03_recuento_asignados_y_sin_asignar(self):
        """Verifica exactamente 262 filas asignadas y 54 filas sin asignar en la BOM."""
        self.assertEqual(len(self.assigned_rows), 262)
        self.assertEqual(len(self.unassigned_rows), 54)
        self.assertEqual(len(self.assigned_rows) + len(self.unassigned_rows), 316)

    def test_04_balance_volumetrico(self):
        """Verifica el volumen geométrico total y los porcentajes asignados y sin asignar."""
        tot_vol = sum(float(r["volume_mm3"]) for r in self.bom_rows)
        assigned_vol = sum(float(r["volume_mm3"]) for r in self.assigned_rows)
        unassigned_vol = sum(float(r["volume_mm3"]) for r in self.unassigned_rows)

        self.assertAlmostEqual(tot_vol, 1999635.115676, places=5)
        self.assertAlmostEqual(assigned_vol, 1630696.689328, places=5)
        self.assertAlmostEqual(unassigned_vol, 368938.426348, places=5)

        pct_unassigned = (unassigned_vol / tot_vol) * 100.0
        self.assertAlmostEqual(pct_unassigned, 18.450287, places=4)

    def test_05_canal_axial_preponderancia(self):
        """Verifica que el canal axial representa el 79,02% del volumen sin asignar y 14,58% del vehículo."""
        canal = [r for r in self.unassigned_rows if r["name"] == "canal_axial_60_exterior_56_interior"][0]
        c_vol = float(canal["volume_mm3"])
        self.assertAlmostEqual(c_vol, 291539.798253, places=5)

        tot_vol = sum(float(r["volume_mm3"]) for r in self.bom_rows)
        unassigned_vol = sum(float(r["volume_mm3"]) for r in self.unassigned_rows)

        self.assertAlmostEqual((c_vol / unassigned_vol) * 100.0, 79.021262, places=4)
        self.assertAlmostEqual((c_vol / tot_vol) * 100.0, 14.579649, places=4)
        self.assertEqual(canal["scope"], "empty_axial_packaging_interface_not_propulsor")
        self.assertEqual(canal["assumed_role"], "unknown_hardware_or_empty_interface")

    def test_06_ambitos_y_roles_sin_asignar(self):
        """Verifica la distribución de los 54 registros sin asignar en 5 scopes y 2 assumed_roles."""
        scopes = {}
        roles = {}
        for r in self.unassigned_rows:
            scopes[r["scope"]] = scopes.get(r["scope"], 0) + 1
            roles[r["assumed_role"]] = roles.get(r["assumed_role"], 0) + 1

        expected_scopes = {
            "empty_axial_packaging_interface_not_propulsor": 1,
            "new_C02_geometry_unqualified": 44,
            "direct_drive_actuator_package_unselected": 4,
            "bearing_envelope_not_selected_hardware": 4,
            "rear_interface_not_sized_nozzle": 1,
        }
        self.assertEqual(scopes, expected_scopes)

        expected_roles = {
            "unknown_hardware_or_empty_interface": 10,
            "unknown_device_or_interface": 44,
        }
        self.assertEqual(roles, expected_roles)

    def test_07_coincidencia_con_json_unidentified(self):
        """Verifica la correspondencia unívoca uno a uno con unidentified_records del JSON."""
        unassigned_names_csv = [r["name"] for r in self.unassigned_rows]
        for h in self.json_data["hypotheses"]:
            self.assertEqual(h["unidentified_part_records"], 54)
            self.assertEqual(h["unidentified_records"], unassigned_names_csv)

    def test_08_reconciliacion_masa_mixta(self):
        """Verifica que la masa asignada bajo la hipótesis mixta coincide con el JSON a precisión IEEE-754."""
        assigned_mass_csv = sum(float(r["assigned_mass_mixta_kg"]) for r in self.assigned_rows)
        mixta_json = [h for h in self.json_data["hypotheses"] if h["hypothesis"] == "mixta_1600"][0]
        json_mass = mixta_json["partial_assigned_mass_kg"]

        self.assertAlmostEqual(assigned_mass_csv, json_mass, places=15)
        self.assertAlmostEqual(assigned_mass_csv, 2.783989739397547, places=15)

    def test_09_reconciliacion_remanente(self):
        """Verifica el remanente presupuestario para la hipótesis mixta frente al objetivo de 5,0 kg."""
        mixta_json = [h for h in self.json_data["hypotheses"] if h["hypothesis"] == "mixta_1600"][0]
        assigned_mass = mixta_json["partial_assigned_mass_kg"]
        reserve = mixta_json["provisional_reserve_kg"]
        rem_json = mixta_json["remaining_for_energy_and_unidentified_hardware_kg"]

        calculated_rem = 5.0 - reserve - assigned_mass
        self.assertAlmostEqual(calculated_rem, rem_json, places=15)
        self.assertAlmostEqual(calculated_rem, 1.4660102606024532, places=15)

    def test_10_reconciliacion_cg_cad_flu(self):
        """Verifica el Centro de Gravedad nominal en marcos CAD y FLU y la ley cinemática de transformación."""
        mixta_json = [h for h in self.json_data["hypotheses"] if h["hypothesis"] == "mixta_1600"][0]
        tot_mass = sum(float(r["assigned_mass_mixta_kg"]) for r in self.assigned_rows)

        cg_x = sum(float(r["assigned_mass_mixta_kg"]) * float(r["x_CAD_m"]) for r in self.assigned_rows) / tot_mass
        cg_y = sum(float(r["assigned_mass_mixta_kg"]) * float(r["y_CAD_m"]) for r in self.assigned_rows) / tot_mass
        cg_z = sum(float(r["assigned_mass_mixta_kg"]) * float(r["z_CAD_m"]) for r in self.assigned_rows) / tot_mass

        cg_cad_json = mixta_json["partial_assigned_CG_CAD_m"]
        cg_flu_json = mixta_json["partial_assigned_CG_FLU_m"]

        self.assertAlmostEqual(cg_x, cg_cad_json[0], places=15)
        self.assertAlmostEqual(cg_y, cg_cad_json[1], places=15)
        self.assertAlmostEqual(cg_z, cg_cad_json[2], places=15)

        # Cinemática FLU: X_FLU = -X_CAD, Y_FLU = -Y_CAD, Z_FLU = +Z_CAD
        self.assertAlmostEqual(cg_flu_json[0], -cg_cad_json[0], places=15)
        self.assertAlmostEqual(cg_flu_json[1], -cg_cad_json[1], places=15)
        self.assertAlmostEqual(cg_flu_json[2], cg_cad_json[2], places=15)

    def test_11_hipotesis_ligera_y_aluminio(self):
        """Verifica la reproducción matemática de las hipótesis Ligera y Aluminio y el déficit de aluminio."""
        def dens_lig(r):
            role = r["assumed_role"]
            if role in ("envelope_material_sensitivity", "rotor_or_carrier_material_sensitivity",
                        "integral_vane_linkage_material_sensitivity", "bushing_material_sensitivity",
                        "seal_or_clamp_density_assumption"):
                return 1200.0
            elif role == "frame_support_density_assumption":
                return 2700.0
            elif role in ("steel_density_assumption", "shaft_steel_density_assumption"):
                return 7800.0
            return 0.0

        def dens_alu(r):
            role = r["assumed_role"]
            if role in ("envelope_material_sensitivity", "rotor_or_carrier_material_sensitivity",
                        "integral_vane_linkage_material_sensitivity", "frame_support_density_assumption"):
                return 2700.0
            elif role == "bushing_material_sensitivity":
                return 8800.0
            elif role in ("steel_density_assumption", "shaft_steel_density_assumption"):
                return 7800.0
            elif role == "seal_or_clamp_density_assumption":
                return 1200.0
            return 0.0

        m_lig = sum(float(r["volume_mm3"]) * dens_lig(r) * 1e-9 for r in self.assigned_rows)
        m_alu = sum(float(r["volume_mm3"]) * dens_alu(r) * 1e-9 for r in self.assigned_rows)

        lig_json = [h for h in self.json_data["hypotheses"] if h["hypothesis"] == "ligera_1200"][0]
        alu_json = [h for h in self.json_data["hypotheses"] if h["hypothesis"] == "aluminio_2700"][0]

        self.assertAlmostEqual(m_lig, lig_json["partial_assigned_mass_kg"], places=14)
        self.assertAlmostEqual(m_alu, alu_json["partial_assigned_mass_kg"], places=14)

        # Verificación del déficit en hipótesis aluminio
        rem_alu = 5.0 - 0.75 - m_alu
        self.assertAlmostEqual(rem_alu, alu_json["remaining_for_energy_and_unidentified_hardware_kg"], places=14)
        self.assertTrue(rem_alu < 0.0, "La hipótesis aluminio debe arrojar déficit estructural")
        self.assertAlmostEqual(rem_alu, -0.17134223593621112, places=14)

    def test_12_estado_hardware_no_calificado(self):
        """Verifica que en el 100% de las filas no existe masa real medida ni hardware calificado."""
        for r in self.bom_rows:
            self.assertEqual(r["actual_mass_kg"], "", "La columna actual_mass_kg debe estar estrictamente vacía")
            self.assertEqual(r["actual_material"], "", "La columna actual_material debe estar estrictamente vacía")
            self.assertEqual(r["actual_hardware_qualified"], "False", "El hardware no debe estar calificado")

        self.assertFalse(self.json_data["hypotheses"][0]["physical_mass_CG_and_inertia_closed"])
        self.assertTrue(self.json_data["assumptions_are_not_measurements"])
        self.assertFalse(self.json_data["inertia_model_acceptance_for_predictive_flight"])

    def test_13_consistencia_censo_csv(self):
        """Verifica la existencia y consistencia del archivo generado salidas/censo_54_reservas.csv."""
        censo_csv = self.salidas_dir / "censo_54_reservas.csv"
        self.assertTrue(censo_csv.exists(), "El archivo salidas/censo_54_reservas.csv no fue generado")

        with open(censo_csv, "r", encoding="utf-8") as f:
            censo_rows = list(csv.DictReader(f))

        self.assertEqual(len(censo_rows), 54)
        self.assertEqual(censo_rows[0]["name"], "canal_axial_60_exterior_56_interior")
        self.assertIn("empty_axial_packaging_interface_not_propulsor", censo_rows[0]["scope"])
        self.assertIn("DESCONOCIDO", censo_rows[0]["uncertainty_state"])

    def test_14_preservacion_incertidumbre_no_nulidad(self):
        """Verifica computacionalmente que las fuentes no imponen m != 0 en reservas sin masa."""
        # Ninguna de las 54 filas posee densidad asignada
        for r in self.unassigned_rows:
            self.assertEqual(r["rho_mixta_ASSUMED_kg_m3"], "")
            self.assertEqual(r["assigned_mass_mixta_kg"], "")

        # La nota técnica ratifica que los sólidos nominales son brutos y pueden solapar material
        note = self.json_data["note"]
        self.assertIn("Gross nominal part volumes", note)
        self.assertIn("unresolved legacy joints may share material", note)


if __name__ == "__main__":
    unittest.main()
