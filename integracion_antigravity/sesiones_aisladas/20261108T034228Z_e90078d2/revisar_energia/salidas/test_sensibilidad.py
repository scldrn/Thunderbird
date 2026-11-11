#!/usr/bin/env python3
"""Suite de pruebas unitarias estándar para la sensibilidad de ley de arrastre en C02."""

import math
import sys
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
    power_profile,
    work_drag_accel_analytical,
    work_drag_accel_numerical,
    work_drag_accel_spatial_numerical,
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

    def test_drag_force_at_terminal_speed(self):
        """Verifica que para cualquier exponente p, la fuerza de arrastre a v=V sea D_final."""
        for v in [100.0, 166.67, 277.78]:
            for d in [10.0, 25.0, 50.0]:
                for p in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]:
                    f = drag_force(v, v, d, p)
                    self.assertAlmostEqual(f, d, places=9)

    def test_spatial_vs_temporal_drag_integral(self):
        """Verifica la identidad entre la integral espacial y temporal de arrastre.

        Nota numérica: En el dominio temporal el integrando es tau^(p+1), infinitamente diferenciable.
        En el dominio espacial el integrando es x^(p/2). Para p=1 (x^0.5), la derivada d/dx(sqrt(x))
        presenta singularidad en el origen (x=0), lo que reduce el orden de convergencia de Simpson a ~4.3e-8.
        Para p=2 y p=4, los integrandos espaciales son polinomios x y x^2, integrados a precisión de máquina.
        """
        test_cases = [
            (600.0, 50.0, 60.0, 1.0),
            (600.0, 50.0, 60.0, 2.0),
            (600.0, 50.0, 60.0, 4.0),
            (1000.0, 50.0, 60.0, 1.0),
            (1000.0, 50.0, 60.0, 2.0),
            (1000.0, 50.0, 60.0, 4.0),
        ]
        for speed, drag, t, p in test_cases:
            v_ms = speed / 3.6
            w_ana = work_drag_accel_analytical(drag, v_ms, t, p)
            w_num_x = work_drag_accel_spatial_numerical(drag, v_ms, t, p, n_intervals=20000)
            rel_err_x = abs(w_num_x - w_ana) / w_ana
            tol = 1e-6 if p == 1.0 else 1e-12
            self.assertLess(
                rel_err_x,
                tol,
                f"Error espacial excesivo para V={speed}, p={p}: err={rel_err_x}",
            )

    def test_power_profile_monotonicity(self):
        """Verifica que la potencia mecánica sea monótonamente creciente en tau in [0, t]."""
        for p in [1.0, 2.0, 4.0]:
            prof = power_profile(600.0, 50.0, 60.0, 0.0, p, n_steps=50)
            for i in range(len(prof) - 1):
                self.assertLess(
                    prof[i]["potencia_mecanica_W"],
                    prof[i + 1]["potencia_mecanica_W"],
                    f"Fallo de monotonía en paso {i} para p={p}",
                )
            # El pico máximo ocurre estrictamente en el último paso
            self.assertAlmostEqual(
                prof[-1]["potencia_mecanica_W"],
                (MASS_KG * (600.0 / 3.6)**2 / 60.0) + 50.0 * (600.0 / 3.6),
                places=7,
            )

    def test_cruise_work_invariance_with_p(self):
        """Verifica que el trabajo de crucero sea exactamente D_final * V * t_crucero, independiente de p."""
        for speed in [600.0, 1000.0]:
            v_ms = speed / 3.6
            for d in [25.0, 50.0]:
                expected_cruise = d * v_ms * CRUISE_S
                for p in [1.0, 2.0, 4.0]:
                    res = evaluate_mission(speed, d, 60.0, 0.0, p)
                    self.assertAlmostEqual(
                        res["trabajo_arrastre_crucero_J"], expected_cruise, places=7
                    )

    def test_negative_battery_margin_all_12_cases(self):
        """Verifica que en los 12 casos directos (50 N, 60 s) el saldo de batería sea negativo."""
        cases = generate_core_cases()
        for c in cases:
            self.assertFalse(
                c["cumple_presupuesto_ligero"],
                f"El caso V={c['velocidad_kmh']}, p={c['exponente_p']}, P_aux={c['potencia_apoyo_W']} no debió cumplir.",
            )
            self.assertLess(c["saldo_bateria_kg"], 0.0)


if __name__ == "__main__":
    unittest.main()
