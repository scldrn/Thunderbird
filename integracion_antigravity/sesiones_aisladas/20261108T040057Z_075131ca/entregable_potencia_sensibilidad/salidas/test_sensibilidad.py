#!/usr/bin/env python3
"""Suite de pruebas unitarias estándar para la sensibilidad de ley de arrastre en C02.

Verifica:
1. Integridad de los supuestos y parámetros de C02 (5.0 kg).
2. Verificación analítica y numérica de la integral exacta W = D_final * V * t / (p + 2).
3. Cotejo exacto contra el modelo r2 de referencia bajo idénticos supuestos.
4. Distinción rigurosa entre potencia de pico simultánea y energía por etapa.
5. Verificación de NO doble conteo de la energía de aceleración.
6. Invariancia de la potencia pico terminal con el exponente p.
7. Régimen activo a 60 s gobernado por potencia y cálculo de tiempos de cruce t*.
8. Validación robusta de argumentos de entrada.
"""

import math
import sys
import unittest
from pathlib import Path

# Agregar directorio actual al path para importar el módulo de cálculo
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sensibilidad_ley_arrastre import (
    AVAILABLE_BATTERY_KG,
    CALCULAR_REF_REL,
    CRUISE_S,
    EFFICIENCY,
    HOVER_S,
    HOVER_W,
    MANEUVER_S,
    MANEUVER_W,
    MASS_KG,
    PACK_W_KG,
    PACK_WH_KG,
    cotejar_con_modelo_r2,
    drag_force,
    evaluate_mission,
    find_crossover_time,
    generate_core_cases,
    work_drag_accel_analytical,
    work_drag_accel_numerical,
)


class TestSensibilidadArrastre(unittest.TestCase):
    """Pruebas unitarias de formulación analítica, consistencia física y cotejo con r2."""

    def test_c02_constants_integrity(self):
        """Verifica que los supuestos y parámetros de C02 se conserven fielmente."""
        self.assertEqual(MASS_KG, 5.0, "La masa nominal de C02 debe ser 5.0 kg.")
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
        """Verifica la fórmula exacta W = D_final * V * t / (p + 2) para p = 1, 2, 4."""
        d_final = 50.0
        v = 600.0 / 3.6  # 166.6667 m/s
        t = 60.0

        # Para p = 1: divisor es 3
        w_p1 = work_drag_accel_analytical(d_final, v, t, 1.0)
        self.assertAlmostEqual(w_p1, (d_final * v * t) / 3.0, places=9)
        self.assertAlmostEqual(w_p1, 50.0 * (600.0 / 3.6) * 60.0 / 3.0, places=9)

        # Para p = 2: divisor es 4
        w_p2 = work_drag_accel_analytical(d_final, v, t, 2.0)
        self.assertAlmostEqual(w_p2, (d_final * v * t) / 4.0, places=9)
        self.assertAlmostEqual(w_p2, 125000.0, places=9)

        # Para p = 4: divisor es 6
        w_p4 = work_drag_accel_analytical(d_final, v, t, 4.0)
        self.assertAlmostEqual(w_p4, (d_final * v * t) / 6.0, places=9)
        self.assertAlmostEqual(w_p4, 125000.0 * (4.0 / 6.0), places=9)

    def test_numerical_vs_analytical_quadrature(self):
        """Verifica que la cuadratura numérica de Simpson converja a la solución analítica."""
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
            w_num = work_drag_accel_numerical(
                drag_n, v_ms, t_s, p_val, n_intervals=10000
            )
            rel_err = abs(w_num - w_ana) / w_ana
            self.assertLess(
                rel_err,
                1e-9,
                f"Error excesivo en cuadratura para V={speed_kmh}, p={p_val}: rel_err={rel_err}",
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
        """Verifica que para p=2 se reproduzcan con exactitud los valores de la tabla de entrada."""
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

        # 600 km/h, 50 N, 60 s, 2968.81 W (estacionario C01)
        r600_hov = evaluate_mission(600.0, 50.0, 60.0, HOVER_W, 2.0)
        self.assertAlmostEqual(r600_hov["pico_bateria_kW"], 18.1804, places=2)
        self.assertAlmostEqual(r600_hov["energia_total_Wh"], 275.7747, places=2)
        self.assertAlmostEqual(r600_hov["masa_bateria_minima_kg"], 3.6361, places=2)
        self.assertAlmostEqual(r600_hov["saldo_bateria_kg"], -1.4319, places=2)

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

        # 1000 km/h, 50 N, 60 s, 2968.81 W
        r1000_hov = evaluate_mission(1000.0, 50.0, 60.0, HOVER_W, 2.0)
        self.assertAlmostEqual(r1000_hov["pico_bateria_kW"], 31.9958, places=2)
        self.assertAlmostEqual(r1000_hov["energia_total_Wh"], 423.9718, places=2)
        self.assertAlmostEqual(r1000_hov["masa_bateria_minima_kg"], 6.3992, places=2)
        self.assertAlmostEqual(r1000_hov["saldo_bateria_kg"], -4.1950, places=2)

    def test_cotejo_exacto_modelo_r2(self):
        """Coteja numéricamente contra calcular_r2.py en múltiples combinaciones."""
        if not CALCULAR_REF_REL.is_file():
            self.skipTest("calcular_r2.py no está en la ruta relativa de referencia.")

        sys.path.insert(0, str(CALCULAR_REF_REL.parent))
        import calcular_r2  # type: ignore

        speeds = [600.0, 1000.0]
        drags = [0.0, 10.0, 25.0, 50.0]
        supports = [0.0, 1000.0, HOVER_W]
        times = [10.0, 30.0, 60.0, 180.0]

        for s in speeds:
            for d in drags:
                for supp in supports:
                    for t in times:
                        res_p2 = evaluate_mission(s, d, t, supp, 2.0)
                        res_r2 = calcular_r2.evaluate(s, d, t, supp)

                        # Coincidencia rigurosa a nivel de flotante
                        self.assertAlmostEqual(
                            res_p2["pico_axial_W"], res_r2["pico_axial_W"], places=9
                        )
                        self.assertAlmostEqual(
                            res_p2["pico_bateria_W"],
                            res_r2["pico_bateria_W"],
                            places=9,
                        )
                        self.assertAlmostEqual(
                            res_p2["energia_estacionario_Wh"],
                            res_r2["energia_estacionario_Wh"],
                            places=9,
                        )
                        self.assertAlmostEqual(
                            res_p2["energia_axial_Wh"],
                            res_r2["energia_axial_Wh"],
                            places=9,
                        )
                        self.assertAlmostEqual(
                            res_p2["energia_apoyo_total_Wh"],
                            res_r2["energia_apoyo_simultaneo_Wh"],
                            places=9,
                        )
                        self.assertAlmostEqual(
                            res_p2["energia_total_Wh"],
                            res_r2["energia_total_Wh"],
                            places=9,
                        )
                        self.assertAlmostEqual(
                            res_p2["masa_bateria_minima_kg"],
                            res_r2["masa_bateria_minima_kg"],
                            places=9,
                        )

    def test_simultaneous_peak_power_vs_stage_energy(self):
        """Distingue formalmente la potencia pico simultánea de la energía por etapa."""
        for speed in [600.0, 1000.0]:
            for supp in [0.0, 1000.0]:
                res_p1 = evaluate_mission(speed, 50.0, 60.0, supp, 1.0)
                res_p2 = evaluate_mission(speed, 50.0, 60.0, supp, 2.0)
                res_p4 = evaluate_mission(speed, 50.0, 60.0, supp, 4.0)

                # 1. La potencia pico ocurre en v = V y es INVARIANTE con p
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

                # 2. Las energías por etapa son distintas y varían con p
                self.assertGreater(
                    res_p1["energia_etapa_aceleracion_Wh"],
                    res_p2["energia_etapa_aceleracion_Wh"],
                )
                self.assertGreater(
                    res_p2["energia_etapa_aceleracion_Wh"],
                    res_p4["energia_etapa_aceleracion_Wh"],
                )
                # La energía de crucero es independiente de p (v = V constante)
                self.assertAlmostEqual(
                    res_p1["energia_etapa_crucero_Wh"],
                    res_p2["energia_etapa_crucero_Wh"],
                    places=9,
                )

    def test_no_double_counting_acceleration_energy(self):
        """Comprueba exhaustivamente que no se cuente dos veces la energía de aceleración."""
        for speed in [600.0, 1000.0]:
            v = speed / 3.6
            for supp in [0.0, 1000.0]:
                for p in [1.0, 2.0, 4.0]:
                    t_acc = 60.0
                    res = evaluate_mission(speed, 50.0, t_acc, supp, p)

                    # 1. Comprobación de suma exacta por etapas disjuntas
                    e_sum_etapas = (
                        res["energia_etapa_estacionario_Wh"]
                        + res["energia_etapa_aceleracion_Wh"]
                        + res["energia_etapa_crucero_Wh"]
                    )
                    self.assertAlmostEqual(
                        e_sum_etapas, res["energia_total_Wh"], places=11
                    )

                    # 2. Verificación del trabajo de aceleración:
                    # Debe contener ÚNICAMENTE la energía cinética (1/2*m*v^2) y el arrastre en aceleración
                    expected_mech_accel_J = (
                        0.5 * MASS_KG * v**2
                        + work_drag_accel_analytical(50.0, v, t_acc, p)
                    )
                    self.assertAlmostEqual(
                        res["trabajo_mecanico_aceleracion_J"],
                        expected_mech_accel_J,
                        places=11,
                    )

                    # 3. Verificación de que en crucero NO se duplica la energía cinética
                    expected_mech_cruise_J = 50.0 * v * CRUISE_S
                    self.assertAlmostEqual(
                        res["trabajo_arrastre_crucero_J"],
                        expected_mech_cruise_J,
                        places=11,
                    )

                    # 4. Verificación de que la potencia pico NO es integrada como si fuera energía
                    # P_pico * t sería mucho mayor que la energía de aceleración real
                    pico_times_t_Wh = (res["pico_axial_W"] * t_acc) / 3600.0
                    self.assertGreater(
                        pico_times_t_Wh,
                        res["energia_arrastre_aceleracion_Wh"]
                        + res["energia_cinetica_Wh"],
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
            # Como la potencia es invariante con p, la masa mínima de batería resulta idéntica
            self.assertAlmostEqual(c["delta_masa_minima_vs_p2_kg"], 0.0, places=9)

    def test_crossover_behavior(self):
        """Verifica la existencia y ordenamiento de los tiempos de cruce t* (Potencia vs Energía)."""
        t_star_p1 = find_crossover_time(600.0, 50.0, 0.0, 1.0)
        t_star_p2 = find_crossover_time(600.0, 50.0, 0.0, 2.0)
        t_star_p4 = find_crossover_time(600.0, 50.0, 0.0, 4.0)

        self.assertIsNotNone(t_star_p1)
        self.assertIsNotNone(t_star_p2)
        self.assertIsNotNone(t_star_p4)

        # Como a mayor p se disipa menos energía en aceleración, el cruce se desplaza a t* mayores
        self.assertLess(t_star_p1, t_star_p2)
        self.assertLess(t_star_p2, t_star_p4)

        # En t > t_star, la energía es la restricción activa y el exponente p altera la masa
        res_p1_long = evaluate_mission(600.0, 50.0, 500.0, 0.0, 1.0)
        res_p4_long = evaluate_mission(600.0, 50.0, 500.0, 0.0, 4.0)
        self.assertEqual(res_p1_long["limitante_dimensionamiento"], "Energía")
        self.assertEqual(res_p4_long["limitante_dimensionamiento"], "Energía")
        self.assertGreater(
            res_p1_long["masa_bateria_minima_kg"], res_p4_long["masa_bateria_minima_kg"]
        )

    def test_input_validation(self):
        """Verifica el rechazo robusto de argumentos de entrada no admisibles."""
        with self.assertRaises(ValueError):
            evaluate_mission(-600.0, 50.0, 60.0, 0.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_mission(600.0, -10.0, 60.0, 0.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_mission(600.0, 50.0, 0.0, 0.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_mission(600.0, 50.0, 60.0, -50.0, 2.0)
        with self.assertRaises(ValueError):
            evaluate_mission(600.0, 50.0, 60.0, 0.0, 0.0)


if __name__ == "__main__":
    unittest.main()
