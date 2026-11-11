#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
SUITE DE PRUEBAS UNITARIAS, METROLÓGICAS Y DE VALIDACIÓN FÍSICA AUDITADA
Ensayo UIUC Micro Invent 3.2x2.2 @ 20.051 RPM (avance) / 2.950 - 19.923 RPM (estático)
===============================================================================
"""

import sys
import os
import unittest
import tempfile
from pathlib import Path

# Agregar salidas/ al path para importar el procesador
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from procesar_uiuc_prop import (
    PropellerUIUCProcessor,
    find_workspace_root,
    G_ACCEL,
    GAMMA_AIR,
    R_AIR
)


class TestPropellerUIUCProcessor(unittest.TestCase):
    """Pruebas exhaustivas de integridad, física aerodinámica, metrología y límites operativos."""

    @classmethod
    def setUpClass(cls):
        cls.root_dir = find_workspace_root(current_dir)
        cls.input_path = (
            cls.root_dir
            / "entradas"
            / "investigacion-aeronautica"
            / "fuentes"
            / "uiuc_propdb"
            / "mi_3.2x2.2_0544rd_20051.txt"
        )
        cls.static_path = (
            cls.root_dir
            / "entradas"
            / "investigacion-aeronautica"
            / "fuentes"
            / "uiuc_propdb"
            / "mi_3.2x2.2_static_0519rd.txt"
        )
        cls.output_csv = cls.root_dir / "salidas" / "uiuc_mi_3.2x2.2_20051_procesado.csv"
        
        cls.processor = PropellerUIUCProcessor(
            filepath_or_str=str(cls.input_path),
            static_filepath=str(cls.static_path),
            diameter_m=0.08128,
            rho_kg_m3=1.225,
            nominal_rpm=20051.0
        )
        cls.data = cls.processor.process()
        cls.stats = cls.processor.get_summary_statistics()

    def test_01_input_file_integrity(self):
        """Verifica la existencia y formato del archivo original UIUC tanto en avance como estático."""
        self.assertTrue(self.input_path.exists(), f"El archivo de avance debe existir en {self.input_path}")
        self.assertTrue(self.static_path.exists(), f"El archivo estático debe existir en {self.static_path}")
        self.assertEqual(len(self.data), 19, "El ensayo UIUC 0544rd_20051 debe contener exactamente 19 puntos medidos.")
        self.assertEqual(len(self.processor.static_processed_data), 18, "El ensayo estático 0519rd debe contener 18 puntos medidos.")
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
        """Valida analíticamente el empuje T = CT * rho * n^2 * D^4 y gramos-fuerza."""
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
        """Valida potencia de eje P = CP * rho * n^3 * D^5 y balance de potencia útil Pout/P = eta."""
        n = 20051.0 / 60.0
        D = 0.08128
        rho = 1.225
        factor_p = rho * (n ** 3) * (D ** 5)
        for r in self.data:
            expected_p = r["CP_medido"] * factor_p
            self.assertAlmostEqual(r["Potencia_eje_W"], expected_p, places=9)
            p_out = r["Empuje_N"] * r["V_m_s"]
            self.assertAlmostEqual(r["Potencia_traccion_W"], p_out, places=9)
            eta_ratio = p_out / expected_p
            self.assertAlmostEqual(r["eta_calculada"], eta_ratio, places=9)

    def test_05_rounding_vs_measurement_error(self):
        """
        Compara eta registrada vs J*CT/CP demostrando que la discrepancia residual es
        estrictamente atribuible a truncamiento en la tabla ASCII (< 1.5e-5),
        mientras que el error experimental del túnel de viento es > 400 veces mayor (1% a 3%).
        """
        for r in self.data:
            diff = abs(r["delta_eta_reg_menos_calc"])
            bound = r["cota_redondeo_propagado"]
            self.assertLessEqual(
                diff, bound,
                f"Punto {r['punto']} supera la cota de redondeo: diff={diff}, cota={bound}"
            )
            self.assertLess(r["error_relativo_eta_pct"], 0.005)

        self.assertGreater(self.stats["max_abs_delta_eta"], 1e-7)
        self.assertLess(self.stats["max_abs_delta_eta"], 1.5e-5)

        typical_experimental_err_pct = 1.0  # 1%
        self.assertGreater(typical_experimental_err_pct / self.stats["max_rel_diff_pct"], 400.0)

    def test_06_static_dataset_continuity(self):
        """
        Valida que el ensayo estático (0519rd) empalma consistentemente con el primer
        punto de avance (0544rd @ J=0.044195), confirmando continuidad física en J -> 0.
        """
        static_data = self.processor.static_processed_data
        self.assertTrue(len(static_data) > 0, "Los datos estáticos deben haberse procesado.")
        
        # Punto estático a ~19923 RPM (más cercano a 20051 RPM)
        top_static = max(static_data, key=lambda s: s["RPM"])
        self.assertAlmostEqual(top_static["RPM"], 19923.333, places=2)
        
        # Comparación con punto 1 de avance (J = 0.044195)
        pt1 = self.data[0]
        # CT estático es 0.125828, CT pt1 es 0.124104 (diferencia < 1.5%)
        ct_diff_pct = abs(pt1["CT_medido"] - top_static["CT_static"]) / top_static["CT_static"] * 100.0
        self.assertLess(ct_diff_pct, 1.5, f"CT estático vs dinámico pt1 discrepa {ct_diff_pct:.2f}% (esperado < 1.5%)")

        # CP estático es 0.059879, CP pt1 es 0.058227 (diferencia < 3.0%)
        cp_diff_pct = abs(pt1["CP_medido"] - top_static["CP_static"]) / top_static["CP_static"] * 100.0
        self.assertLess(cp_diff_pct, 3.0, f"CP estático vs dinámico pt1 discrepa {cp_diff_pct:.2f}% (esperado < 3.0%)")

    def test_07_zero_thrust_advance_ratio(self):
        """Verifica la extrapolación analítica del avance de empuje nulo J0 (CT = 0)."""
        j0_info = self.processor.estimate_zero_thrust_advance_ratio()
        j0 = j0_info["J0_estimado_5pts"]
        # J0 debe situarse entre 0.58 y 0.63 para esta hélice con P/D = 0.6875
        self.assertGreater(j0, 0.58)
        self.assertLess(j0, 0.65)
        # La pendiente dCT/dJ debe ser fuertemente negativa
        self.assertLess(j0_info["pendiente_dCT_dJ"], -0.20)

    def test_08_measured_range_and_600kmh_comparison(self):
        """Evalúa cuantitativamente el rango ensayado y la incompatibilidad con 600 km/h."""
        v_min_kmh = self.stats["V_min_km_h"]
        v_max_kmh = self.stats["V_max_km_h"]
        self.assertAlmostEqual(v_min_kmh, 4.32, delta=0.05)
        self.assertAlmostEqual(v_max_kmh, 43.87, delta=0.05)

        deficit = self.stats["diferencia_kmh_con_600"]
        self.assertAlmostEqual(deficit, 600.0 - v_max_kmh, places=4)
        self.assertGreater(deficit, 550.0)

        factor = self.stats["factor_velocidad_600_vs_max"]
        self.assertGreater(factor, 13.0)

        j_hyp = self.stats["J_hipotetico_a_600kmh"]
        self.assertGreater(j_hyp, 6.0)

    def test_09_aerodynamic_regime_mach_and_reynolds(self):
        """Verifica que el ensayo operó en régimen estrictamente incompresible subsónico y Re laminar."""
        self.assertLess(self.stats["Mach_punta_max"], 0.30, "Mach en punta debe ser incompresible (M < 0.30)")
        self.assertGreater(self.stats["Mach_punta_min"], 0.24)
        # Re en torno a 30,000
        self.assertGreater(self.stats["Re_cuerda_075_min"], 20000.0)
        self.assertLess(self.stats["Re_cuerda_075_max"], 40000.0)

    def test_10_aerodynamic_monotonicity_and_peak(self):
        """Verifica monotonía física decreciente de CT y CP y posición del pico de eficiencia."""
        ct_vals = [r["CT_medido"] for r in self.data]
        cp_vals = [r["CP_medido"] for r in self.data]
        j_vals = [r["J_medido"] for r in self.data]
        eta_vals = [r["eta_registrada"] for r in self.data]

        for i in range(len(self.data) - 1):
            self.assertGreater(ct_vals[i], ct_vals[i + 1], f"CT debe decrecer con J en pt {i}")
            self.assertGreater(cp_vals[i], cp_vals[i + 1], f"CP debe decrecer con J en pt {i}")
            self.assertLess(j_vals[i], j_vals[i + 1], f"J debe ser estrictamente creciente en pt {i}")

        max_eta_idx = eta_vals.index(max(eta_vals))
        self.assertEqual(max_eta_idx, 15, "Punto 16 (índice 15) es el óptimo de eficiencia (J=0.380780, eta=56.21%)")

    def test_11_prohibition_rules_validation(self):
        """Valida que el sistema rechaza extrapolación a 600 km/h y ventilador C02, aceptando variantes válidas."""
        # Rechazo 600 km/h
        val_600 = self.processor.validate_application_limits(target_v_kmh=600.0)
        self.assertFalse(val_600["is_valid"])
        self.assertTrue(any("EXTRAPOLACIÓN INVÁLIDA" in err for err in val_600["errors"]))

        # Rechazo ventilador C02
        val_c02 = self.processor.validate_application_limits(
            target_v_kmh=20.0,
            target_machine_type="ventilador_C02",
            working_fluid="CO2"
        )
        self.assertFalse(val_c02["is_valid"])
        self.assertTrue(any("TRANSFERENCIA INVÁLIDA" in err for err in val_c02["errors"]))
        self.assertTrue(any("FLUIDO INCOMPATIBLE" in err for err in val_c02["errors"]))

        # Aceptación de sinónimos válidos con espacios o tildes
        val_syn = self.processor.validate_application_limits(
            target_v_kmh=25.0,
            target_machine_type="hélice abierta",
            working_fluid="aire"
        )
        self.assertTrue(val_syn["is_valid"], f"Debe aceptar 'hélice abierta' y 'aire': {val_syn['errors']}")

    def test_12_csv_file_generation_and_headers(self):
        """Verifica que el CSV exportado existe, tiene encabezados descriptivos con unidades y 19 registros."""
        self.processor.export_csv(str(self.output_csv))
        self.assertTrue(self.output_csv.exists(), "El archivo CSV de salida debe existir en salidas/")
        
        with open(self.output_csv, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

        data_lines = [l for l in lines if not l.startswith("#")]
        self.assertEqual(len(data_lines), 20, "Debe haber 1 fila de encabezado + 19 filas de datos.")
        
        header_cols = data_lines[0].split(",")
        self.assertIn("J_medido [-]", header_cols)
        self.assertIn("CT_medido [-]", header_cols)
        self.assertIn("CP_medido [-]", header_cols)
        self.assertIn("eta_registrada [-]", header_cols)
        self.assertIn("V_km_h [km/h]", header_cols)
        self.assertIn("Empuje_N [N]", header_cols)
        self.assertIn("Mach_punta [-]", header_cols)
        self.assertIn("Re_cuerda_075 [-]", header_cols)

    def test_13_robust_path_resolution(self):
        """Verifica que find_workspace_root resuelve correctamente desde subdirectorios."""
        nested = self.root_dir / "salidas"
        resolved = find_workspace_root(nested)
        self.assertEqual(resolved, self.root_dir)

    def test_14_error_handling_invalid_inputs(self):
        """Verifica manejo adecuado de excepciones ante archivos inexistentes o corruptos."""
        non_existent = self.root_dir / "entradas" / "inexistente.txt"
        proc_bad = PropellerUIUCProcessor(filepath_or_str=str(non_existent))
        with self.assertRaises(FileNotFoundError):
            proc_bad.load_data()

        # Archivo con encabezado inválido
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
            tf.write("Col1 Col2 Col3 Col4\n1 2 3 4\n")
            tf_path = tf.name

        try:
            proc_corrupt = PropellerUIUCProcessor(filepath_or_str=tf_path)
            with self.assertRaises(ValueError):
                proc_corrupt.load_data()
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
