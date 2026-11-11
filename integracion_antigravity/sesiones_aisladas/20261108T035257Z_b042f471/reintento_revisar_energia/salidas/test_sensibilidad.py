#!/usr/bin/env python3
"""Suite de pruebas unitarias estándar para la sensibilidad de ley de arrastre en C02."""

import math
import sys
import tempfile
import unittest
from pathlib import Path

# Agregar directorio salidas al path para importar el módulo bajo prueba
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sensibilidad_ley_arrastre import (
    AVAILABLE_BATTERY_KG,
    CRUISE_S,
    EFFICIENCY,
    HOVER_S,
    HOVER_W,
    MANEUVER_S,
    MANEUVER_W,
    MASS_KG,
    PACK_W_KG,
    PACK_WH_KG,
    drag_force,
    evaluate_mission,
    find_crossover_time,
    generate_core_cases,
    generate_extended_cases,
    work_drag_accel_analytical,
    work_drag_accel_numerical,
    write_csv,
)


class TestSensibilidadArrastre(unittest.TestCase):
    """Pruebas estándar de la formulación analítica, numérica y modelo de misión."""

    def test_c02_constants_integrity(self):
        """Verifica que los supuestos y parámetros de C02 se conserven exactamente."""
        self.assertEqual(MASS_KG, 5.0, "La masa de C02 debe ser exactamente 5.0 kg.")
        self.assertAlmostEqual(HOVER_W, 2968.8083465960835, places=7)
        self.assertAlmostEqual(MANEUVER_W, 3505.892708058721, places=7)
        self.assertEqual(HOVER_S, 30.0)
        self.assertEqual(MANEUVER_S, 3.0)
        self.assertEqual(CRUISE_S, 30.0)
        self.assertEqual(EFFICIENCY, 0.70)
        self.assertEqual(PACK_WH_KG, 150.0)
        self.assertEqual(PACK_W_KG, 5000.0)
        self.assertAlmostEqual(AVAILABLE_BATTERY_KG, 2.20416, places=5)

    def test_analytical_integral_formula(self):
        """Verifica la fórmula D_final * V * t / (p + 2) para p = 1, 2, 4."""
        d_final = 50.0
        v = 600.0 / 3.6  # 166.6667 m/s
        t = 60.0

        # Para p = 1: denominador es 3
        w_p1 = work_drag_accel_analytical(d_final, v, t, 1.0)
        self.assertAlmostEqual(w_p1, d_final * v * t / 3.0, places=9)
        self.assertAlmostEqual(w_p1, 50.0 * (600.0 / 3.6) * 60.0 / 3.0, places=9)

        # Para p = 2: denominador es 4
        w_p2 = work_drag_accel_analytical(d_final, v, t, 2.0)
        self.assertAlmostEqual(w_p2, d_final * v * t / 4.0, places=9)
        self.assertAlmostEqual(w_p2, 125000.0, places=9)

        # Para p = 4: denominador es 6
        w_p4 = work_drag_accel_analytical(d_final, v, t, 4.0)
        self.assertAlmostEqual(w_p4, d_final * v * t / 6.0, places=9)
        self.assertAlmostEqual(w_p4, 125000.0 * (4.0 / 6.0), places=9)

    def test_numerical_vs_analytical_quadrature(self):
        """Verifica convergencia de la cuadratura numérica con la fórmula analítica."""
        test_cases = [
            (600.0, 50.0, 60.0, 1.0),
            (600.0, 50.0, 60.0, 2.0),
            (600.0, 50.0, 60.0, 4.0),
            (1000.0, 50.0, 60.0, 1.0),
            (1000.0, 50.0, 60.0, 2.0),
            (1000.0, 50.0, 60.0, 4.0),
            (800.0, 25.0, 45.0, 3.0),
        ]
        for speed_kmh, drag_n, t_s, p_val in test_cases:
            v_ms = speed_kmh / 3.6
            w_ana = work_drag_accel_analytical(drag_n, v_ms, t_s, p_val)
            w_num = work_drag_accel_numerical(drag_n, v_ms, t_s, p_val, n_intervals=10000)
            rel_err = abs(w_num - w_ana) / w_ana
            self.assertLess(
                rel_err,
                1e-9,
                f"Error en cuadratura para V={speed_kmh}, p={p_val}: rel_err={rel_err}",
            )

    def test_drag_work_theoretical_ratios(self):
        """Verifica las razones teóricas exactas W(p) / W(p=2)."""
        d_final = 50.0
        v = 1000.0 / 3.6
        t = 60.0

        w_p1 = work_drag_accel_analytical(d_final, v, t, 1.0)
        w_p2 = work_drag_accel_analytical(d_final, v, t, 2.0)
        w_p4 = work_drag_accel_analytical(d_final, v, t, 4.0)

        # W(1) / W(2) = (1/3) / (1/4) = 4/3
        self.assertAlmostEqual(w_p1 / w_p2, 4.0 / 3.0, places=9)
        # W(4) / W(2) = (1/6) / (1/4) = 2/3
        self.assertAlmostEqual(w_p4 / w_p2, 2.0 / 3.0, places=9)
        # Monotonía estricta
        self.assertGreater(w_p1, w_p2)
        self.assertGreater(w_p2, w_p4)

    def test_reproduction_of_reference_cases_p2(self):
        """Verifica que para p=2 se reproduzcan fielmente los valores del informe de entrada."""
        # 600 km/h, 50 N, 60 s, 0 W
        r600_0 = evaluate_mission(600.0, 50.0, 60.0, 0.0, 2.0)
        self.assertAlmostEqual(r600_0["pico_bateria_kW"], 15.2116, places=2)
        self.assertAlmostEqual(r600_0["energia_total_Wh"], 201.5545, places=2)
        self.assertAlmostEqual(r600_0["masa_bateria_minima_kg"], 3.0423, places=2)
        self.assertAlmostEqual(r600_0["saldo_bateria_kg"], -0.8382, places=2)

        # 600 km/h, 50 N, 60 s, 1000 W
        r600_1k = evaluate_mission(600.0, 50.0, 60.0, 1000.0, 2.0)
        self.assertAlmostEqual(r600_1k["pico_bateria_kW"], 16.2116, places=2)
        self.assertAlmostEqual(r600_1k["energia_total_Wh"], 226.5545, places=2)
        self.assertAlmostEqual(r600_1k["masa_bateria_minima_kg"], 3.2423, places=2)
        self.assertAlmostEqual(r600_1k["saldo_bateria_kg"], -1.0382, places=2)

        # 1000 km/h, 50 N, 60 s, 0 W
        r1000_0 = evaluate_mission(1000.0, 50.0, 60.0, 0.0, 2.0)
        self.assertAlmostEqual(r1000_0["pico_bateria_kW"], 29.0270, places=2)
        self.assertAlmostEqual(r1000_0["energia_total_Wh"], 349.7516, places=2)
        self.assertAlmostEqual(r1000_0["masa_bateria_minima_kg"], 5.8054, places=2)
        self.assertAlmostEqual(r1000_0["saldo_bateria_kg"], -3.6012, places=2)

        # 1000 km/h, 50 N, 60 s, 1000 W
        r1000_1k = evaluate_mission(1000.0, 50.0, 60.0, 1000.0, 2.0)
        self.assertAlmostEqual(r1000_1k["pico_bateria_kW"], 30.0270, places=2)
        self.assertAlmostEqual(r1000_1k["energia_total_Wh"], 374.7516, places=2)
        self.assertAlmostEqual(r1000_1k["masa_bateria_minima_kg"], 6.0054, places=2)
        self.assertAlmostEqual(r1000_1k["saldo_bateria_kg"], -3.8012, places=2)

    def test_peak_power_invariance_with_p(self):
        """Demuestra que la potencia pico es estrictamente invariante con p para v=V."""
        for speed in [600.0, 1000.0]:
            for supp in [0.0, 1000.0]:
                res_p1 = evaluate_mission(speed, 50.0, 60.0, supp, 1.0)
                res_p2 = evaluate_mission(speed, 50.0, 60.0, supp, 2.0)
                res_p4 = evaluate_mission(speed, 50.0, 60.0, supp, 4.0)

                self.assertAlmostEqual(
                    res_p1["pico_axial_W"], res_p2["pico_axial_W"], places=9
                )
                self.assertAlmostEqual(
                    res_p2["pico_axial_W"], res_p4["pico_axial_W"], places=9
                )
                self.assertAlmostEqual(
                    res_p1["pico_bateria_W"], res_p2["pico_bateria_W"], places=9
                )
                self.assertAlmostEqual(
                    res_p2["pico_bateria_W"], res_p4["pico_bateria_W"], places=9
                )

    def test_energy_sensitivity_across_p(self):
        """Verifica que la energía de misión disminuye estrictamente con p."""
        for speed in [600.0, 1000.0]:
            for supp in [0.0, 1000.0]:
                res_p1 = evaluate_mission(speed, 50.0, 60.0, supp, 1.0)
                res_p2 = evaluate_mission(speed, 50.0, 60.0, supp, 2.0)
                res_p4 = evaluate_mission(speed, 50.0, 60.0, supp, 4.0)

                self.assertGreater(
                    res_p1["energia_total_Wh"], res_p2["energia_total_Wh"]
                )
                self.assertGreater(
                    res_p2["energia_total_Wh"], res_p4["energia_total_Wh"]
                )
                self.assertGreater(
                    res_p1["masa_bateria_energia_kg"],
                    res_p2["masa_bateria_energia_kg"],
                )
                self.assertGreater(
                    res_p2["masa_bateria_energia_kg"],
                    res_p4["masa_bateria_energia_kg"],
                )

    def test_active_constraint_at_60s(self):
        """Confirma que a 60 s la masa mínima siempre está limitada por potencia en los 12 casos."""
        cases = generate_core_cases()
        self.assertEqual(len(cases), 12)
        for c in cases:
            self.assertEqual(c["limitante_dimensionamiento"], "Potencia")
            self.assertGreater(
                c["masa_bateria_potencia_kg"], c["masa_bateria_energia_kg"]
            )
            # Como la potencia manda y es invariante con p, la masa mínima es invariante
            self.assertAlmostEqual(c["delta_masa_minima_vs_p2_kg"], 0.0, places=9)

    def test_crossover_time_existence(self):
        """Verifica que para tiempos suficientemente largos exista cruce donde energía mande."""
        t_star_p1 = find_crossover_time(600.0, 50.0, 0.0, 1.0)
        t_star_p2 = find_crossover_time(600.0, 50.0, 0.0, 2.0)
        t_star_p4 = find_crossover_time(600.0, 50.0, 0.0, 4.0)

        self.assertIsNotNone(t_star_p1)
        self.assertIsNotNone(t_star_p2)
        self.assertIsNotNone(t_star_p4)

        # Al aumentar p se consume menos energía, por lo que el cruce se desplaza a tiempos mayores
        self.assertLess(t_star_p1, t_star_p2)
        self.assertLess(t_star_p2, t_star_p4)

        # Verificar que en t > t_star, energía sea el limitante activo
        res_post_crossover = evaluate_mission(600.0, 50.0, 500.0, 0.0, 2.0)
        self.assertEqual(res_post_crossover["limitante_dimensionamiento"], "Energía")

    def test_input_validation(self):
        """Verifica el rechazo robusto de argumentos inválidos."""
        with self.assertRaises(ValueError):
            evaluate_mission(-600.0, 50.0, 60.0, 0.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_mission(600.0, -10.0, 60.0, 0.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_mission(600.0, 50.0, 0.0, 0.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_mission(600.0, 50.0, 60.0, -100.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_mission(600.0, 50.0, 60.0, 0.0, 0.0)

    def test_crossover_none_when_power_dominates_always(self):
        """Verifica que find_crossover_time retorne None si la potencia domina siempre."""
        t_star = find_crossover_time(600.0, 0.0, 0.0, 2.0)
        self.assertIsNone(t_star, "Sin arrastre ni apoyo, la potencia domina para todo t.")

    def test_extended_cases_count_and_columns(self):
        """Verifica la generación de la matriz extendida (90 casos)."""
        ext = generate_extended_cases()
        # 2 velocidades * 3 apoyos * 5 tiempos * 3 exponentes = 90
        self.assertEqual(len(ext), 90)
        required_keys = {
            "velocidad_kmh",
            "potencia_apoyo_W",
            "tiempo_aceleracion_s",
            "exponente_p",
            "energia_total_Wh",
            "masa_bateria_minima_kg",
        }
        self.assertTrue(required_keys.issubset(ext[0].keys()))

    def test_write_csv_in_temp_dir(self):
        """Verifica exportación CSV en carpeta temporal aislada sin tocar disco persistente."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / "test_export.csv"
            rows = [{"col_a": 1.23, "col_b": "valor_prueba"}]
            write_csv(tmp_path, rows)
            self.assertTrue(tmp_path.is_file())
            content = tmp_path.read_text(encoding="utf-8")
            self.assertIn("col_a,col_b", content)
            self.assertIn("1.23,valor_prueba", content)


if __name__ == "__main__":
    unittest.main()
