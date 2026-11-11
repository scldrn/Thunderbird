#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
SUITE DE PRUEBAS UNITARIAS Y DE VALIDACIÓN FÍSICA
Ensayo UIUC Micro Invent 3.2x2.2 @ 20.051 RPM
===============================================================================
"""

import sys
import os
import unittest
from pathlib import Path

# Agregar salidas/ al path para importar el procesador
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from procesar_uiuc_prop import PropellerUIUCProcessor, G_ACCEL


class TestPropellerUIUCProcessor(unittest.TestCase):
    """Pruebas rigurosas de integridad, física, metrología y límites operativos."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = current_dir.parent
        cls.input_path = (
            cls.base_dir
            / "entradas"
            / "investigacion-aeronautica"
            / "fuentes"
            / "uiuc_propdb"
            / "mi_3.2x2.2_0544rd_20051.txt"
        )
        cls.output_csv = cls.base_dir / "salidas" / "uiuc_mi_3.2x2.2_20051_procesado.csv"
        
        cls.processor = PropellerUIUCProcessor(
            filepath_or_str=str(cls.input_path),
            diameter_m=0.08128,
            rho_kg_m3=1.225,
            nominal_rpm=20051.0
        )
        cls.data = cls.processor.process()
        cls.stats = cls.processor.get_summary_statistics()

    def test_01_input_file_integrity(self):
        """Verifica la existencia y formato del archivo original UIUC."""
        self.assertTrue(self.input_path.exists(), "El archivo de entrada debe existir en entradas/")
        self.assertEqual(len(self.data), 19, "El ensayo UIUC 0544rd_20051 debe contener exactamente 19 puntos medidos.")
        for r in self.data:
            self.assertGreater(r["J_medido"], 0.0)
            self.assertGreater(r["CT_medido"], 0.0)
            self.assertGreater(r["CP_medido"], 0.0)
            self.assertGreater(r["eta_registrada"], 0.0)

    def test_02_velocity_transformation(self):
        """Valida analíticamente la transformación V = J * n * D."""
        n = 20051.0 / 60.0
        D = 0.08128
        for r in self.data:
            expected_v = r["J_medido"] * n * D
            self.assertAlmostEqual(r["V_m_s"], expected_v, places=9)
            self.assertAlmostEqual(r["V_km_h"], expected_v * 3.6, places=9)

    def test_03_thrust_transformation(self):
        """Valida analíticamente el empuje T = CT * rho * n^2 * D^4."""
        n = 20051.0 / 60.0
        D = 0.08128
        rho = 1.225
        factor_t = rho * (n ** 2) * (D ** 4)
        for r in self.data:
            expected_t = r["CT_medido"] * factor_t
            self.assertAlmostEqual(r["Empuje_N"], expected_t, places=9)
            expected_gf = (expected_t / G_ACCEL) * 1000.0
            self.assertAlmostEqual(r["Empuje_gf"], expected_gf, places=6)

    def test_04_power_transformation_and_balance(self):
        """Valida potencia de eje P = CP * rho * n^3 * D^5 y balance de potencia útil."""
        n = 20051.0 / 60.0
        D = 0.08128
        rho = 1.225
        factor_p = rho * (n ** 3) * (D ** 5)
        for r in self.data:
            expected_p = r["CP_medido"] * factor_p
            self.assertAlmostEqual(r["Potencia_eje_W"], expected_p, places=9)
            
            # Balance de potencia útil: Pout = T * V
            p_out = r["Empuje_N"] * r["V_m_s"]
            self.assertAlmostEqual(r["Potencia_traccion_W"], p_out, places=9)
            
            # Comprobación de que Pout / P coincide con eta_calc
            eta_ratio = p_out / expected_p
            self.assertAlmostEqual(r["eta_calculada"], eta_ratio, places=9)

    def test_05_rounding_vs_measurement_error(self):
        """
        Compara eta registrada vs J*CT/CP sin suponer error de medición igual al redondeo.
        
        1. Confirma que la discrepancia residual es del orden de 1e-5 y se encuentra estrictamente
           dentro de la cota de propagación por el formato tabular de 6 decimales.
        2. Confirma que esta discrepancia de redondeo (< 0.0023%) es órdenes de magnitud menor
           que el error de medición experimental de los transductores (típicamente 1% a 3%).
        """
        for r in self.data:
            diff = abs(r["delta_eta_reg_menos_calc"])
            bound = r["cota_redondeo_propagado"]
            self.assertLessEqual(
                diff, bound,
                f"Punto {r['punto']} supera la cota de redondeo: diff={diff}, cota={bound}"
            )
            # El error relativo de redondeo numérico es minúsculo (< 0.003%)
            self.assertLess(r["error_relativo_eta_pct"], 0.005)

        # La máxima diferencia absoluta no es cero (hay efecto de truncamiento ASCII)
        self.assertGreater(self.stats["max_abs_delta_eta"], 1e-7)
        self.assertLess(self.stats["max_abs_delta_eta"], 1.5e-5)

        # Distinción fundamental: el error experimental típico del túnel (>= 1%) es al menos
        # 400 veces mayor que el mayor residuo de redondeo numérico observado (0.0023%).
        typical_experimental_err_pct = 1.0  # 1%
        self.assertGreater(typical_experimental_err_pct / self.stats["max_rel_diff_pct"], 400.0)

    def test_06_measured_range_and_600kmh_comparison(self):
        """
        Evalúa el rango ensayado y la enorme diferencia física con 600 km/h.
        """
        # Rango medido en velocidad
        v_min_kmh = self.stats["V_min_km_h"]
        v_max_kmh = self.stats["V_max_km_h"]
        self.assertAlmostEqual(v_min_kmh, 4.32, delta=0.05)
        self.assertAlmostEqual(v_max_kmh, 43.87, delta=0.05)

        # Comparación con 600 km/h
        v_ref = 600.0
        deficit = self.stats["diferencia_kmh_con_600"]
        self.assertAlmostEqual(deficit, v_ref - v_max_kmh, places=4)
        self.assertGreater(deficit, 550.0, "El déficit con respecto a 600 km/h debe superar 550 km/h.")

        # Factor de velocidad
        factor = self.stats["factor_velocidad_600_vs_max"]
        self.assertGreater(factor, 13.0, "600 km/h es más de 13 veces mayor que la máxima velocidad ensayada.")

        # J hipotético
        j_hyp = self.stats["J_hipotetico_a_600kmh"]
        self.assertGreater(j_hyp, 6.0, "A 600 km/h el J hipotético excede 6.0 (muy por encima del rango [0.04 .. 0.45]).")

    def test_07_csv_file_generation_and_headers(self):
        """Verifica que el CSV exportado existe y contiene todos los datos requeridos."""
        self.processor.export_csv(str(self.output_csv))
        self.assertTrue(self.output_csv.exists(), "El archivo CSV de salida debe existir en salidas/")
        
        with open(self.output_csv, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

        # Debe tener comentarios de metadatos, encabezado de columnas y 19 filas
        data_lines = [l for l in lines if not l.startswith("#")]
        self.assertEqual(len(data_lines), 20, "Debe haber 1 fila de encabezado + 19 filas de datos.")
        
        header_cols = data_lines[0].split(",")
        self.assertIn("J_medido [-]", header_cols)
        self.assertIn("CT_medido [-]", header_cols)
        self.assertIn("CP_medido [-]", header_cols)
        self.assertIn("eta_registrada [-]", header_cols)
        self.assertIn("V_km_h [km/h]", header_cols)
        self.assertIn("Empuje_N [N]", header_cols)
        self.assertIn("Potencia_eje_W [W]", header_cols)
        self.assertIn("eta_calculada [-]", header_cols)
        self.assertIn("delta_eta [-]", header_cols)

    def test_08_aerodynamic_monotonicity_and_peak(self):
        """Verifica comportamiento físico aerodinámico característico."""
        ct_vals = [r["CT_medido"] for r in self.data]
        cp_vals = [r["CP_medido"] for r in self.data]
        j_vals = [r["J_medido"] for r in self.data]
        eta_vals = [r["eta_registrada"] for r in self.data]

        # Monotonía decreciente de CT y CP con J
        for i in range(len(self.data) - 1):
            self.assertGreater(ct_vals[i], ct_vals[i + 1], f"CT debe decrecer con J en pt {i}")
            self.assertGreater(cp_vals[i], cp_vals[i + 1], f"CP debe decrecer con J en pt {i}")
            self.assertLess(j_vals[i], j_vals[i + 1], f"J debe ser estrictamente creciente en pt {i}")

        # Comportamiento de campana de la eficiencia: pico interior
        max_eta_idx = eta_vals.index(max(eta_vals))
        self.assertGreater(max_eta_idx, 0, "El pico de eficiencia no debe estar en J mínimo")
        self.assertLess(max_eta_idx, len(eta_vals) - 1, "El pico de eficiencia no debe estar en J máximo")
        self.assertEqual(max_eta_idx, 15, "Punto 16 (índice 15) es el óptimo de eficiencia (J=0.380780, eta=56.21%)")

    def test_09_prohibition_rules_validation(self):
        """Valida que el sistema rechaza extrapolación a 600 km/h y transferencia a ventilador C02."""
        # 1. Caso 600 km/h: debe ser rechazado
        val_600 = self.processor.validate_application_limits(target_v_kmh=600.0)
        self.assertFalse(val_600["is_valid"])
        self.assertTrue(any("EXTRAPOLACIÓN INVÁLIDA" in err for err in val_600["errors"]))

        # 2. Caso ventilador C02: debe ser rechazado
        val_c02 = self.processor.validate_application_limits(
            target_v_kmh=20.0,
            target_machine_type="ventilador_C02",
            working_fluid="CO2"
        )
        self.assertFalse(val_c02["is_valid"])
        self.assertTrue(any("TRANSFERENCIA INVÁLIDA" in err for err in val_c02["errors"]))
        self.assertTrue(any("FLUIDO INCOMPATIBLE" in err for err in val_c02["errors"]))

        # 3. Caso dentro de límites de hélice abierta: debe ser válido
        val_valid = self.processor.validate_application_limits(
            target_v_kmh=25.0,
            target_machine_type="open_propeller",
            working_fluid="air"
        )
        self.assertTrue(val_valid["is_valid"])
        self.assertEqual(len(val_valid["errors"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
