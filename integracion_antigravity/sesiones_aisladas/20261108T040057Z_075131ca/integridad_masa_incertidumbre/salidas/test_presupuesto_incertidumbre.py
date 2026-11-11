#!/usr/bin/env python3
"""
test_presupuesto_incertidumbre.py - Suite de pruebas automatizadas para presupuesto e incertidumbre.

Ejecutable directamente con python3 estándar (unittest):
  python3 salidas/test_presupuesto_incertidumbre.py

Verifica:
  1. Inmutabilidad de los archivos de referencia en entradas/.
  2. Distinción estricta entre DESCONOCIDO (None / celda vacía) y CERO (0.0).
  3. Tratamiento epistémico de volúmenes reservados (pueden estar vacíos, no prueban masa cero ni positiva).
  4. Chequeo de unidades de masa (kg, g, mg, lb, oz) hacia el SI canónico (kg).
  5. Chequeo de unidades de volumen (mm3, cm3, m3) y densidad (kg/m3), y relación constitutiva m = V * rho.
  6. Consistencia y aritmética de intervalos de incertidumbre [m_min, m_max].
  7. Fidelidad de lectura/escritura CSV (roundtrip sin corrupción de nulos ni ceros).
  8. Propiedades del presupuesto de la candidata C02 de 5 kg (sensibilidades, reservas, remanente).
  9. Propiedades de los presupuestos expresamente hipotéticos de 2 kg y 10 kg (sin marcas ni mediciones inventadas).
  10. Presupuesto desglosado por los 10 roles funcionales auditados de la BOM C02.
  11. Principio de no inferencia de inexistencia por ausencia de copia y preservación de registros base.
"""

import csv
import hashlib
import os
import sys
import unittest
from pathlib import Path

# Asegurar importación del módulo de presupuesto en salidas/
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from presupuesto_incertidumbre import (
    UnitChecker,
    MassEntry,
    BudgetSummary,
    parse_cell_mass,
    format_cell_mass,
    read_budget_csv,
    write_budget_csv,
    aggregate_budget,
    create_template_entries,
    build_hypothetical_2kg_budget,
    build_c02_5kg_uncertainty_budget,
    build_hypothetical_10kg_budget,
    build_c02_roles_uncertainty_budget,
    CSV_HEADERS
)


class TestPresupuestoIncertidumbre(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.workspace_dir = CURRENT_DIR.parent
        cls.entradas_dir = cls.workspace_dir / "entradas"
        cls.salidas_dir = cls.workspace_dir / "salidas"

        # Hashes SHA-256 de referencia para verificar inmutabilidad
        cls.reference_hashes = {
            cls.entradas_dir / "investigacion-aeronautica/configuraciones/C02_CANDIDATA.json":
                "4529d8530f0edd2faa8dddf1cd7c142d72969e5dc6166c232063b3c4db0d4bf3",
            cls.entradas_dir / "investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/INFORME.md":
                "d7b724afd7b48b7058a1d1969afa4b869f14629d709d72e30f3170f03ee1627a",
            cls.entradas_dir / "investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_bom/salidas/INFORME_AUDITORIA_BOM.md":
                "9bd05035bb299ea4c8a1bc5a77c90407e2ca8507d8d197ae850b2a8a49e31795",
            cls.entradas_dir / "investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_bom/salidas/auditar_bom.py":
                "26554c4119cf11f4703ceaff97695e04847dd1d604eed400364f868abc32185a",
            cls.entradas_dir / "investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_bom/salidas/bom_agrupada_roles.csv":
                "bb281aad64c0fdaaf760e1638caa0361c5ae6d5f32e5d7828335e98fd584bbfd",
            cls.entradas_dir / "investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_bom/salidas/test_auditoria.py":
                "3be0a1abd6df7f544da294c57b96e5c551caf5f599d7dd4e93b1f5c476b0ca7a"
        }

    def test_01_immutability_of_reference_inputs(self):
        """Verifica que todos los archivos de referencia en entradas/ permanecen inalterados."""
        for path, expected_hash in self.reference_hashes.items():
            self.assertTrue(path.exists(), f"El archivo de referencia {path} debe existir.")
            with open(path, "rb") as f:
                computed_hash = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                computed_hash,
                expected_hash,
                f"ALERTA: El archivo base {path} fue modificado! Hash esperado: {expected_hash}, obtenido: {computed_hash}"
            )

    def test_02_distinguish_unknown_from_zero(self):
        """
        Verifica la distinción estricta entre DESCONOCIDO (None / celda vacía) y CERO (0.0).
        En ningún caso un valor no medido o sin asignar debe evaluarse como 0.0 kg.
        """
        # Celdas desconocidas
        self.assertIsNone(parse_cell_mass(""))
        self.assertIsNone(parse_cell_mass("   "))
        self.assertIsNone(parse_cell_mass(None))
        self.assertIsNone(parse_cell_mass("DESCONOCIDO"))
        self.assertIsNone(parse_cell_mass("NULL"))
        self.assertIsNone(parse_cell_mass("N/A"))
        self.assertIsNone(parse_cell_mass("SIN_ASIGNAR"))

        # Celdas con cero explícito (medición nula o ausencia demostrada)
        zero_val = parse_cell_mass("0")
        self.assertIsNotNone(zero_val)
        self.assertEqual(zero_val, 0.0)
        self.assertEqual(parse_cell_mass("0.0"), 0.0)
        self.assertEqual(parse_cell_mass("0.000000"), 0.0)

        # Distinción en tipos y lógica de programación
        val_unknown = parse_cell_mass("")
        val_zero = parse_cell_mass("0.0")
        self.assertFalse(val_unknown == 0.0)
        self.assertTrue(val_unknown is None)
        self.assertTrue(val_zero == 0.0)
        self.assertFalse(val_zero is None)

        # Formato de celda para CSV
        self.assertEqual(format_cell_mass(None), "")
        self.assertEqual(format_cell_mass(0.0, decimals=4), "0.0000")
        self.assertEqual(format_cell_mass(2.5, decimals=3), "2.500")

    def test_03_reserved_volume_epistemic_rules(self):
        """
        Verifica que los volúmenes reservados pueden estar vacíos y no prueban masa cero ni positiva.
        Un volumen reservado sin hardware NO tiene masa medida, NO tiene masa supuesta forzada,
        su cota inferior física puede ser 0.0 kg (cavidad vacía) y su cota superior acota el hardware.
        """
        # Creación válida de reserva volumétrica incierta
        reserva = MassEntry(
            componente="reserva_tubo_axial_OD60",
            masa_medida=None,  # No medido
            masa_supuesta=None,  # Sin asignar
            intervalo_inferior=0.0,  # Puede estar vacío (m=0)
            intervalo_superior=0.55,  # Si aloja hardware (m>0)
            evidencia="Volumen reservado en CAD; no prueba masa cero ni positiva",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        )
        self.assertTrue(reserva.is_reserved_envelope)
        self.assertFalse(reserva.is_measured)
        self.assertFalse(reserva.is_assumed)
        self.assertEqual(reserva.intervalo_inferior, 0.0)
        self.assertEqual(reserva.intervalo_superior, 0.55)

        # Regla de restricción: una reserva NO puede tener masa medida asignada
        with self.assertRaises(ValueError):
            MassEntry(
                componente="reserva_invalida_con_medicion",
                masa_medida=0.25,  # Invención prohibida: hardware no seleccionado
                masa_supuesta=None,
                intervalo_inferior=0.0,
                intervalo_superior=0.55,
                evidencia="Prueba",
                estado="RESERVA_VOLUMETRICA_INCIERTA"
            )

    def test_04_unit_checker_mass_conversions(self):
        """Verifica la conversión exacta de unidades de masa hacia kg (SI canónico)."""
        self.assertEqual(UnitChecker.mass_to_kg(1.0, "kg"), 1.0)
        self.assertEqual(UnitChecker.mass_to_kg(2500.0, "g"), 2.5)
        self.assertEqual(UnitChecker.mass_to_kg(1000000.0, "mg"), 1.0)
        self.assertAlmostEqual(UnitChecker.mass_to_kg(1.0, "lb"), 0.45359237, places=8)
        self.assertAlmostEqual(UnitChecker.mass_to_kg(16.0, "oz"), 0.45359237, places=7)

        # Unidad no válida
        with self.assertRaises(ValueError):
            UnitChecker.mass_to_kg(1.0, "parsec")

    def test_05_unit_checker_volume_density_and_constitutive_relation(self):
        """Verifica conversiones de volumen/densidad y la relación constitutiva m = V * rho."""
        # Volúmenes
        self.assertEqual(UnitChecker.volume_to_m3(1.0, "m3"), 1.0)
        self.assertEqual(UnitChecker.volume_to_m3(1e9, "mm3"), 1.0)
        self.assertEqual(UnitChecker.volume_to_m3(1e6, "cm3"), 1.0)
        self.assertEqual(UnitChecker.volume_to_m3(1000.0, "dm3"), 1.0)
        self.assertEqual(UnitChecker.volume_to_m3(1000.0, "l"), 1.0)

        # Densidades
        self.assertEqual(UnitChecker.density_to_kg_m3(1600.0, "kg/m3"), 1600.0)
        self.assertEqual(UnitChecker.density_to_kg_m3(1.6, "g/cm3"), 1600.0)

        # Relación constitutiva m = V * rho
        # Cubo de aluminio de 100x100x100 mm = 1.000.000 mm3 a 2700 kg/m3 -> 2.7 kg
        self.assertTrue(
            UnitChecker.verify_density_volume_mass(1e6, "mm3", 2700.0, "kg/m3", 2.700000)
        )

        # Inconsistencia intencionada debe lanzar error
        with self.assertRaises(ValueError):
            UnitChecker.verify_density_volume_mass(1e6, "mm3", 2700.0, "kg/m3", 3.500000)

    def test_06_interval_arithmetic_consistency(self):
        """Verifica la coherencia de intervalos [inferior, superior] y agregación."""
        # Intervalo inferior > superior debe lanzar error
        with self.assertRaises(ValueError):
            MassEntry(
                componente="error_intervalo",
                masa_medida=None,
                masa_supuesta=1.0,
                intervalo_inferior=1.5,
                intervalo_superior=0.8,
                evidencia="Prueba",
                estado="SUPUESTO"
            )

        # Masa física negativa no permitida
        with self.assertRaises(ValueError):
            MassEntry(
                componente="error_negativo",
                masa_medida=None,
                masa_supuesta=1.0,
                intervalo_inferior=-0.1,
                intervalo_superior=1.2,
                evidencia="Prueba",
                estado="SUPUESTO"
            )

        # Agregación de intervalos
        entries = [
            MassEntry("e1", None, 1.0, 0.8, 1.2, "evi", "SUPUESTO"),
            MassEntry("e2", None, 2.0, 1.5, 2.7, "evi", "SUPUESTO"),
            MassEntry("res", None, None, 0.0, 0.5, "evi", "RESERVA_VOLUMETRICA_INCIERTA")
        ]
        summary = aggregate_budget(entries, target_mass_kg=3.5)
        self.assertAlmostEqual(summary.interval_lower_sum_kg, 2.3)  # 0.8 + 1.5 + 0.0
        self.assertAlmostEqual(summary.interval_upper_sum_kg, 4.4)  # 1.2 + 2.7 + 0.5
        self.assertAlmostEqual(summary.uncertainty_span_kg, 2.1)
        self.assertEqual(summary.closure_status, "OBJETIVO_DENTRO_DE_INTERVALO_DE_INCERTIDUMBRE")

    def test_07_csv_roundtrip_fidelity(self):
        """Verifica que la plantilla CSV generada conserva tipos, nulos y ceros en ciclo completo."""
        template_entries = create_template_entries()
        test_csv_path = self.salidas_dir / "test_roundtrip.csv"
        write_budget_csv(str(test_csv_path), template_entries)

        reloaded = read_budget_csv(str(test_csv_path))
        self.assertEqual(len(reloaded), len(template_entries))

        for orig, read in zip(template_entries, reloaded):
            self.assertEqual(orig.componente, read.componente)
            self.assertEqual(orig.masa_medida, read.masa_medida)
            self.assertEqual(orig.masa_supuesta, read.masa_supuesta)
            self.assertEqual(orig.intervalo_inferior, read.intervalo_inferior)
            self.assertEqual(orig.intervalo_superior, read.intervalo_superior)
            self.assertEqual(orig.evidencia, read.evidencia)
            self.assertEqual(orig.estado, read.estado)

        # Comprobación de que la fila 2 tiene None en masa_medida y masa_supuesta
        self.assertIsNone(reloaded[1].masa_medida)
        self.assertIsNone(reloaded[1].masa_supuesta)
        self.assertEqual(reloaded[1].intervalo_inferior, 0.0)

        # Comprobación de que la fila 3 tiene 0.0 explícito en masa_medida
        self.assertEqual(reloaded[2].masa_medida, 0.0)
        self.assertIsNotNone(reloaded[2].masa_medida)

    def test_08_c02_5kg_uncertainty_budget_properties(self):
        """Verifica la integridad del presupuesto de incertidumbre C02 5 kg."""
        entries = build_c02_5kg_uncertainty_budget()
        summary = aggregate_budget(entries, target_mass_kg=5.0)

        # 0 piezas medidas
        self.assertEqual(summary.measured_count, 0)
        self.assertIsNone(summary.total_measured_mass_kg)
        self.assertFalse(summary.physical_mass_closed)

        # Verificación de que las reservas tienen cota inferior 0.0 y masa supuesta None
        res_modulos = [e for e in entries if "Reservas_internas" in e.componente][0]
        self.assertIsNone(res_modulos.masa_medida)
        self.assertIsNone(res_modulos.masa_supuesta)
        self.assertEqual(res_modulos.intervalo_inferior, 0.0)

        res_vehiculares = [e for e in entries if "Reservas_interfaces" in e.componente][0]
        self.assertIsNone(res_vehiculares.masa_medida)
        self.assertIsNone(res_vehiculares.masa_supuesta)
        self.assertEqual(res_vehiculares.intervalo_inferior, 0.0)

        # Estructura asignada CAD
        struct = [e for e in entries if "Estructura_asignada" in e.componente][0]
        self.assertAlmostEqual(struct.masa_supuesta, 2.783990, places=5)
        self.assertAlmostEqual(struct.intervalo_inferior, 2.045841, places=5)
        self.assertAlmostEqual(struct.intervalo_superior, 4.421342, places=5)

    def test_09_hypothetical_2kg_and_10kg_properties(self):
        """Verifica que los modelos de 2 kg y 10 kg son estrictamente hipotéticos sin datos inventados."""
        for target, builder, filename in [
            (2.0, build_hypothetical_2kg_budget, "presupuesto_hipotetico_2kg.csv"),
            (10.0, build_hypothetical_10kg_budget, "presupuesto_hipotetico_10kg.csv")
        ]:
            entries = builder()
            summary = aggregate_budget(entries, target_mass_kg=target)

            self.assertEqual(summary.target_mass_kg, target)
            self.assertEqual(summary.measured_count, 0)
            self.assertIsNone(summary.total_measured_mass_kg)
            self.assertFalse(summary.physical_mass_closed)

            # Comprobar que todos los estados declaran condición hipotética o reserva
            for e in entries:
                self.assertTrue(
                    any(term in e.estado.upper() for term in ("HIPOTETICO", "RESERVA", "MARGEN")),
                    f"Fila {e.componente} en target {target} no declara condición hipotética: {e.estado}"
                )
                # Ninguna fila debe afirmar masa medida real
                self.assertIsNone(e.masa_medida)

            # Comprobar existencia del archivo CSV generado en salidas/
            csv_path = self.salidas_dir / filename
            self.assertTrue(csv_path.exists())

    def test_10_c02_roles_uncertainty_budget(self):
        """Verifica el presupuesto de 10 roles funcionales auditados de la BOM C02."""
        entries = build_c02_roles_uncertainty_budget()
        self.assertEqual(len(entries), 11)  # 10 roles + remanente/reserva provisional

        # Reconciliación de suma de masas asignadas (roles 0 a 7): 2.783989 kg
        sum_assigned = sum(e.masa_supuesta for e in entries[:8])
        self.assertAlmostEqual(sum_assigned, 2.7839897, places=5)

        # Filas 8 y 9 son reservas volumétricas (44 y 10 registros)
        self.assertIsNone(entries[8].masa_supuesta)
        self.assertEqual(entries[8].intervalo_inferior, 0.0)
        self.assertIsNone(entries[9].masa_supuesta)
        self.assertEqual(entries[9].intervalo_inferior, 0.0)

    def test_11_epistemic_assertion_non_inferred_absence(self):
        """
        Verifica el cumplimiento de la regla:
        'No infieras que un archivo no copiado no existe, ni que una reserva sin masa asignada
        tenga masa real nula o no nula.'
        """
        # 1. Comprobación sobre archivos: no asumir que un archivo ausente en entradas/ no existe en el proyecto
        uncopied_file = self.entradas_dir / "investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/BOM_GEOMETRICA_PARCIAL.csv"
        # El archivo no fue copiado a este directorio aislado
        self.assertFalse(uncopied_file.exists())
        # Pero el sistema no debe fallar ni inferir que no existe en el repositorio global

        # 2. Comprobación sobre reservas: una reserva no prueba m = 0 ni m > 0
        reserva = MassEntry(
            componente="reserva_indeterminada",
            masa_medida=None,
            masa_supuesta=None,
            intervalo_inferior=0.0,
            intervalo_superior=0.8,
            evidencia="Volumen de reserva; estado físico abierto",
            estado="RESERVA_VOLUMETRICA_INCIERTA"
        )
        # La masa medida y supuesta deben ser estrictamente None (indeterminada)
        self.assertIsNone(reserva.masa_medida)
        self.assertIsNone(reserva.masa_supuesta)
        # Su intervalo permite tanto el vacío (0.0) como masa positiva (hasta 0.8)
        self.assertEqual(reserva.intervalo_inferior, 0.0)
        self.assertGreater(reserva.intervalo_superior, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
