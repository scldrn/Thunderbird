#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
SUITE DE PRUEBAS UNITARIAS Y DE VALIDACIÓN FÍSICA
Paquete Autónomo Reproducible UIUC - Hélice mi_3.2x2.2 @ 20.051 RPM
===============================================================================
"""

import sys
import math
import unittest
from pathlib import Path

# Configurar importación autónoma relativa a __file__
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from procesar_uiuc_prop import (
    PropellerUIUCProcessor,
    compute_velocity_from_advance_ratio,
    compute_ideal_froude_efficiency,
    G_ACCEL
)


class TestPropellerUIUCProcessor(unittest.TestCase):
    """Pruebas rigurosas de reproducibilidad, metrología y restricciones físicas."""

    @classmethod
    def setUpClass(cls):
        cls.script_dir = current_dir
        cls.input_path = cls.script_dir / "datos" / "mi_3.2x2.2_0544rd_20051.txt"
        cls.output_csv = cls.script_dir / "uiuc_mi_3.2x2.2_20051_procesado.csv"

        cls.processor = PropellerUIUCProcessor(
            filepath=cls.input_path,
            diameter_m=0.08128,
            rho_kg_m3=1.225,
            nominal_rpm=20051.0
        )
        cls.data = cls.processor.process()
        cls.stats = cls.processor.get_summary_statistics()

    def test_01_input_file_integrity(self):
        """Verifica la existencia y formato del archivo local conservado en salidas/datos/."""
        self.assertTrue(self.input_path.exists(), f"El archivo de datos debe existir en: {self.input_path}")
        self.assertEqual(len(self.data), 19, "El ensayo UIUC 0544rd_20051 debe contener exactamente 19 puntos medidos.")
        for r in self.data:
            self.assertGreater(r["J_medido"], 0.0)
            self.assertGreater(r["CT_medido"], 0.0)
            self.assertGreater(r["CP_medido"], 0.0)
            self.assertGreater(r["eta_registrada"], 0.0)

    def test_02_velocity_transformation_and_reference_check(self):
        """
        Valida la relación J = V / (n * D) ==> V = J * n * D.
        Verifica específicamente el caso de referencia:
        con 20051 rpm, D = 0.08128 m y J = 0.448667 la velocidad calculada es aprox 12.19 m/s.
        """
        n = 20051.0 / 60.0
        D = 0.08128

        # 1. Verificación para todos los puntos
        for r in self.data:
            expected_v = r["J_medido"] * n * D
            self.assertAlmostEqual(r["V_m_s"], expected_v, places=9)
            self.assertAlmostEqual(r["V_km_h"], expected_v * 3.6, places=9)

        # 2. Verificación explícita de referencia requerida
        j_ref = 0.448667
        v_ref = compute_velocity_from_advance_ratio(j_ref, n, D)
        # V = 0.448667 * (20051 / 60) * 0.08128 = 12.1868843952... m/s
        self.assertAlmostEqual(v_ref, 12.186884, places=5)
        self.assertAlmostEqual(round(v_ref, 2), 12.19, places=2)
        self.assertLess(abs(v_ref - 12.19), 0.01)

    def test_03_thrust_transformation(self):
        """Valida el cálculo del empuje T = CT * rho * n^2 * D^4 y conversión a gramos-fuerza."""
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
        """Valida potencia de eje P = CP * rho * n^3 * D^5 y balance de potencia útil Pout = T * V."""
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

    def test_05_efficiency_appropriate_domain_and_froude(self):
        """
        Valida que la eficiencia de coeficientes eta = J * CT / CP y la eficiencia ideal
        solo se evalúan y son físicamente representativas en el dominio apropiado:
        J > 0, CT > 0, CP > 0.
        Además verifica que eta_calc < eta_ideal < 1.0 en todo el dominio medido.
        """
        # Todos los puntos medidos deben estar en el dominio propulsivo válido
        for r in self.data:
            self.assertTrue(r["dominio_propulsivo_valido"])
            self.assertGreater(r["eta_calculada"], 0.0)
            self.assertGreater(r["eta_ideal_Froude"], r["eta_calculada"])
            self.assertLess(r["eta_ideal_Froude"], 1.0)

        # Fuera de dominio: J <= 0 o CT <= 0 debe arrojar ValueError en compute_ideal_froude_efficiency
        with self.assertRaises(ValueError):
            compute_ideal_froude_efficiency(0.0, 0.10)
        with self.assertRaises(ValueError):
            compute_ideal_froude_efficiency(-0.1, 0.10)
        with self.assertRaises(ValueError):
            compute_ideal_froude_efficiency(0.2, 0.0)
        with self.assertRaises(ValueError):
            compute_ideal_froude_efficiency(0.2, -0.05)

    def test_06_rounding_vs_measurement_error(self):
        """
        Distingue rigurosamente la cota de redondeo tabular (~1e-5)
        frente a la precisión numérica de los datos reportados.
        """
        for r in self.data:
            diff = abs(r["delta_eta_reg_menos_calc"])
            bound = r["cota_redondeo_propagado"]
            self.assertLessEqual(
                diff, bound,
                f"Punto {r['punto']} excede la cota de redondeo: diff={diff}, cota={bound}"
            )
            self.assertLess(r["error_relativo_eta_pct"], 0.003)

        self.assertGreater(self.stats["max_abs_delta_eta"], 1e-7)
        self.assertLess(self.stats["max_abs_delta_eta"], 1.5e-5)

    def test_07_measured_range_and_units(self):
        """Verifica el alcance medido de las variables dimensionales y adimensionales."""
        # Alcance en avance J
        self.assertAlmostEqual(self.stats["J_min"], 0.044195, places=6)
        self.assertAlmostEqual(self.stats["J_max"], 0.448667, places=6)

        # Alcance en velocidad
        self.assertAlmostEqual(self.stats["V_min_m_s"], 1.2004, delta=0.01)
        self.assertAlmostEqual(self.stats["V_max_m_s"], 12.1869, delta=0.01)
        self.assertAlmostEqual(self.stats["V_min_km_h"], 4.3216, delta=0.05)
        self.assertAlmostEqual(self.stats["V_max_km_h"], 43.8728, delta=0.05)

        # Alcance en empuje y potencia
        self.assertAlmostEqual(self.stats["T_max_N"], 0.7410, delta=0.01)
        self.assertAlmostEqual(self.stats["T_min_N"], 0.2465, delta=0.01)
        self.assertAlmostEqual(self.stats["P_max_W"], 9.4435, delta=0.02)
        self.assertAlmostEqual(self.stats["P_min_W"], 5.8028, delta=0.02)

    def test_08_prohibition_extrapolation_600kmh(self):
        """Valida que el sistema rechaza formalmente la extrapolación a 600 km/h."""
        val_600 = self.processor.validate_application_limits(target_v_kmh=600.0)
        self.assertFalse(val_600["is_valid"])
        self.assertTrue(any("EXTRAPOLACIÓN INVÁLIDA" in err for err in val_600["errors"]))
        self.assertGreater(self.stats["diferencia_kmh_con_600"], 550.0)
        self.assertGreater(self.stats["factor_velocidad_600_vs_max"], 13.0)
        self.assertGreater(self.stats["J_hipotetico_a_600kmh"], 6.0)

    def test_09_prohibition_c02_ventilator_transfer(self):
        """Valida que este propulsor abierto no puede presentarse como modelo o prueba de ventilador C02."""
        val_c02 = self.processor.validate_application_limits(
            target_v_kmh=20.0,
            target_machine_type="ventilador_C02",
            working_fluid="CO2"
        )
        self.assertFalse(val_c02["is_valid"])
        self.assertTrue(any("TRANSFERENCIA INVÁLIDA" in err for err in val_c02["errors"]))
        self.assertTrue(any("FLUIDO INCOMPATIBLE" in err for err in val_c02["errors"]))

    def test_10_csv_file_generation_and_headers(self):
        """Verifica la exportación del CSV y la coherencia de columnas y metadatos."""
        out_csv = self.processor.export_csv(self.output_csv)
        self.assertTrue(out_csv.exists(), f"El archivo CSV generado debe existir en: {out_csv}")

        with open(out_csv, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

        data_lines = [l for l in lines if not l.startswith("#")]
        self.assertEqual(len(data_lines), 20, "Debe contener 1 fila de encabezado + 19 filas de datos.")

        header_cols = data_lines[0].split(",")
        expected_cols = [
            "punto [-]", "J_medido [-]", "CT_medido [-]", "CP_medido [-]", "eta_registrada [-]",
            "V_m_s [m/s]", "V_km_h [km/h]", "Empuje_N [N]", "Empuje_gf [gf]", "Potencia_eje_W [W]",
            "Potencia_traccion_W [W]", "eta_calculada [-]", "eta_ideal_Froude [-]", "delta_eta [-]",
            "error_relativo_pct [%]", "cota_redondeo_propagado [-]", "es_atribuible_a_redondeo [bool]",
            "dominio_propulsivo_valido [bool]"
        ]
        for col in expected_cols:
            self.assertIn(col, header_cols)

    def test_11_aerodynamic_monotonicity_and_peak(self):
        """Valida monotonía aerodinámica y posición del pico de eficiencia."""
        ct_vals = [r["CT_medido"] for r in self.data]
        cp_vals = [r["CP_medido"] for r in self.data]
        j_vals = [r["J_medido"] for r in self.data]
        eta_vals = [r["eta_registrada"] for r in self.data]

        for i in range(len(self.data) - 1):
            self.assertGreater(ct_vals[i], ct_vals[i + 1])
            self.assertGreater(cp_vals[i], cp_vals[i + 1])
            self.assertLess(j_vals[i], j_vals[i + 1])

        max_eta_idx = eta_vals.index(max(eta_vals))
        self.assertEqual(max_eta_idx, 15, "El pico de eficiencia debe estar en el punto 16 (índice 15).")
        self.assertAlmostEqual(eta_vals[15], 0.562131, places=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
