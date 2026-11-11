#!/usr/bin/env python3
"""
test_analitico_convergencia.py - Suite de pruebas analíticas y verificación
de convergencia numérica para el modelo de disco actuador en aceleración.

Ejecuta:
1. Demostración y test analítico de potencia finita en V = 0 y límite continuo.
2. Contraste de potencia en reposo frente al modelo previo (P_prev(0) = 0).
3. Verificación de la solución analítica cerrada frente a cuadratura numérica de alta precisión (D = 0).
4. Verificación de la solución analítica cerrada frente a cuadratura numérica con arrastre (D > 0).
5. Comprobación asintótica del límite de área infinita (A -> inf => W_ideal -> W_util).
6. Comprobación asintótica de empuje nulo (T -> 0 => W_ideal -> 0).
7. Acotamiento de la eficiencia de Froude: 0 <= eta_i < 1.
8. Estudio sistemático de convergencia numérica (Trapecio O(h^2) y Simpson O(h^4)) con refinamiento de malla.
9. Exportación de convergencia.csv y resultados_tests.json en salidas/.
"""

import math
import json
import csv
import unittest
from typing import List, Dict, Any

from modelo_disco import (
    induced_velocity,
    ideal_power,
    static_power,
    froude_efficiency,
    exact_work_accel,
    integrate_work_trapezoid,
    integrate_work_simpson,
    previous_model_work,
    evaluate_scenario,
    mach_number
)


class TestModeloDiscoAnalitico(unittest.TestCase):
    """Pruebas analíticas rigurosas del modelo de disco actuador."""

    def setUp(self):
        self.rho = 1.225
        self.d = 0.25
        self.A = math.pi * (self.d / 2.0) ** 2
        self.m = 5.0
        self.eta_prev = 0.70

    def test_potencia_finita_en_V0(self):
        """
        Demuestra analítica y computacionalmente que en V = 0:
        P_ideal(0) = T^(3/2) / sqrt(2*rho*A) > 0 y finita para todo T > 0, A > 0, rho > 0.
        Contrasta con el modelo previo que asigna P_prev(0) = 0.
        """
        for T in [0.5, 5.0, 13.89, 23.15, 50.0, 100.0]:
            p_stat = static_power(T, self.rho, self.A)
            p_ideal_v0 = ideal_power(0.0, T, self.rho, self.A)
            vi_v0 = induced_velocity(0.0, T, self.rho, self.A)

            # 1. Positividad y finitud
            self.assertTrue(math.isfinite(p_stat))
            self.assertTrue(math.isfinite(p_ideal_v0))
            self.assertGreater(p_stat, 0.0)
            self.assertAlmostEqual(p_stat, p_ideal_v0, places=10)

            # 2. Relación exacta P = T * vi en V=0
            self.assertAlmostEqual(p_stat, T * vi_v0, places=10)

            # 3. Fórmula cerrada exacta
            expected_p = math.pow(T, 1.5) / math.sqrt(2.0 * self.rho * self.A)
            self.assertAlmostEqual(p_stat, expected_p, places=10)

            # 4. Contraste con el modelo previo
            p_prev_v0 = (T * 0.0) / self.eta_prev
            self.assertEqual(p_prev_v0, 0.0)
            self.assertGreater(p_ideal_v0 - p_prev_v0, 0.0)

    def test_limite_continuo_V_hacia_cero(self):
        """
        Verifica que lim_{V -> 0+} P_ideal(V) = P_static.
        La función es continua y diferenciable en V = 0.
        """
        T = 20.0
        p_static = static_power(T, self.rho, self.A)
        for eps in [1e-2, 1e-4, 1e-6, 1e-8]:
            p_eps = ideal_power(eps, T, self.rho, self.A)
            rel_diff = abs(p_eps - p_static) / p_static
            # Expansión de Taylor: P(eps) = P_static + 0.5*T*eps + O(eps^2)
            # Por tanto rel_diff ~ 0.5 * T * eps / P_static = O(eps)
            self.assertLess(rel_diff, 10.0 * eps)

    def test_solucion_analitica_exacta_sin_arrastre_D0(self):
        """
        Compara la solución analítica exacta de W_ideal con integración
        numérica de ultra-alta precisión para D_final = 0 en diversos parámetros.
        """
        test_cases = [
            (5.0, 166.666667, 60.0),  # 600 km/h, 60 s
            (5.0, 277.777778, 60.0),  # 1000 km/h, 60 s
            (5.0, 83.333333, 30.0),   # 300 km/h, 30 s
            (2.0, 50.0, 15.0),        # Masa ligera
            (10.0, 200.0, 45.0),      # Masa pesada
        ]
        for m, V, t in test_cases:
            exact = exact_work_accel(m, V, t, 0.0, self.rho, self.A)
            numeric = integrate_work_simpson(m, V, t, 0.0, self.rho, self.A, N=20000)
            rel_err = abs(exact - numeric) / exact
            self.assertLess(rel_err, 1e-9, f"Fallo en m={m}, V={V}, t={t}: rel_err={rel_err}")

    def test_solucion_analitica_exacta_con_arrastre_D_positivo(self):
        """
        Compara la solución analítica exacta de W_ideal con integración
        numérica de ultra-alta precisión para D_final > 0.
        """
        test_cases = [
            (5.0, 166.666667, 60.0, 50.0),
            (5.0, 166.666667, 60.0, 25.0),
            (5.0, 166.666667, 60.0, 10.0),
            (5.0, 277.777778, 60.0, 50.0),
            (5.0, 83.333333, 30.0, 25.0),
            (2.0, 50.0, 15.0, 5.0),
            (10.0, 200.0, 45.0, 75.0),
        ]
        for m, V, t, D in test_cases:
            exact = exact_work_accel(m, V, t, D, self.rho, self.A)
            numeric = integrate_work_simpson(m, V, t, D, self.rho, self.A, N=20000)
            rel_err = abs(exact - numeric) / exact
            self.assertLess(rel_err, 1e-9, f"Fallo en m={m}, V={V}, t={t}, D={D}: rel_err={rel_err}")

    def test_limite_asintotico_area_infinita(self):
        """
        Demuestra que a medida que A -> inf, la velocidad inducida tiende a 0,
        y el trabajo ideal del disco converge exactamente al trabajo útil:
        lim_{A -> inf} W_ideal = W_util = 0.5*m*V^2 + 0.25*D*V*t.
        """
        m = 5.0
        V = 166.666667
        t = 60.0
        D = 50.0
        W_util, _ = previous_model_work(m, V, t, D, self.eta_prev)

        areas = [1e0, 1e2, 1e4, 1e6]
        diffs = []
        for A_large in areas:
            W_ideal = exact_work_accel(m, V, t, D, self.rho, A_large)
            diff = W_ideal - W_util
            self.assertGreater(diff, 0.0)  # W_ideal > W_util siempre
            diffs.append(diff)

        # Comprobar convergencia monótona decreciente hacia 0
        for i in range(len(diffs) - 1):
            self.assertLess(diffs[i + 1], diffs[i])

        # En A = 10^6 m^2, la diferencia relativa debe ser minúscula
        rel_diff_final = diffs[-1] / W_util
        self.assertLess(rel_diff_final, 1e-3)

    def test_limite_empuje_nulo(self):
        """
        Si la masa tiende a 0 y el arrastre tiende a 0, el empuje requerido
        es nulo y el trabajo ideal converge a 0.
        """
        V = 100.0
        t = 20.0
        # Caso puramente nulo
        W_exact_zero = exact_work_accel(0.0, V, t, 0.0, self.rho, self.A)
        self.assertEqual(W_exact_zero, 0.0)

        # Límite continuo cuando m -> 0 y D -> 0
        for eps in [1e-4, 1e-6, 1e-8]:
            W_eps = exact_work_accel(eps, V, t, eps, self.rho, self.A)
            self.assertLess(W_eps, 6000.0 * eps)

    def test_eficiencia_froude_acotada(self):
        """
        Verifica que 0 <= eta_i < 1 para cualquier condición con T > 0,
        y que crece monótonamente con la velocidad.
        """
        T = 30.0
        velocities = [0.0, 1.0, 10.0, 50.0, 150.0, 300.0]
        etas = [froude_efficiency(v, T, self.rho, self.A) for v in velocities]

        self.assertEqual(etas[0], 0.0)
        for i in range(len(etas) - 1):
            self.assertLess(etas[i], etas[i + 1])
            self.assertLess(etas[i + 1], 1.0)


def ejecutar_estudio_convergencia() -> List[Dict[str, Any]]:
    """
    Ejecuta un estudio sistemático de convergencia numérica duplicando el número
    de intervalos N desde 2 hasta 16384, comparando la regla Trapezoidal y Simpson
    contra la solución analítica cerrada exacta.
    
    Retorna la lista de métricas por nivel de malla.
    """
    m = 5.0
    V = 166.666667  # 600 km/h
    t = 60.0
    D = 50.0
    rho = 1.225
    d = 0.25
    A = math.pi * (d / 2.0) ** 2

    exact = exact_work_accel(m, V, t, D, rho, A)

    ns = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
    registros = []

    prev_err_trap = None
    prev_err_simp = None

    for N in ns:
        h = t / N
        val_trap = integrate_work_trapezoid(m, V, t, D, rho, A, N)
        val_simp = integrate_work_simpson(m, V, t, D, rho, A, N)

        err_trap = abs(val_trap - exact)
        err_simp = abs(val_simp - exact)

        rel_trap = err_trap / exact
        rel_simp = err_simp / exact

        rate_trap = (
            math.log2(prev_err_trap / err_trap)
            if (prev_err_trap is not None and err_trap > 0)
            else 0.0
        )
        rate_simp = (
            math.log2(prev_err_simp / err_simp)
            if (prev_err_simp is not None and err_simp > 0)
            else 0.0
        )

        prev_err_trap = err_trap
        prev_err_simp = err_simp

        registros.append({
            "N": N,
            "h_s": h,
            "val_trapezoid_J": val_trap,
            "err_trapezoid_J": err_trap,
            "rel_err_trapezoid": rel_trap,
            "order_trapezoid": rate_trap,
            "val_simpson_J": val_simp,
            "err_simpson_J": err_simp,
            "rel_err_simpson": rel_simp,
            "order_simpson": rate_simp,
        })

    return registros


def exportar_convergencia_csv(registros: List[Dict[str, Any]], ruta: str):
    """Guarda la tabla de convergencia en formato CSV."""
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "N_intervalos",
            "paso_h_s",
            "W_trapecio_J",
            "error_abs_trapecio_J",
            "error_rel_trapecio",
            "orden_obs_trapecio",
            "W_simpson_J",
            "error_abs_simpson_J",
            "error_rel_simpson",
            "orden_obs_simpson"
        ])
        for r in registros:
            writer.writerow([
                r["N"],
                f"{r['h_s']:.6e}",
                f"{r['val_trapezoid_J']:.8f}",
                f"{r['err_trapezoid_J']:.6e}",
                f"{r['rel_err_trapezoid']:.6e}",
                f"{r['order_trapezoid']:.2f}" if r["order_trapezoid"] > 0 else "N/A",
                f"{r['val_simpson_J']:.8f}",
                f"{r['err_simpson_J']:.6e}",
                f"{r['rel_err_simpson']:.6e}",
                f"{r['order_simpson']:.2f}" if r["order_simpson"] > 0 else "N/A",
            ])


def main():
    print("=== EJECUCIÓN DE PRUEBAS ANALÍTICAS Y CONVERGENCIA NUMÉRICA ===")
    
    # 1. Ejecutar suite de pruebas unitarias
    suite = unittest.TestLoader().loadTestsFromTestCase(TestModeloDiscoAnalitico)
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    # 2. Ejecutar estudio de convergencia numérica
    print("\nCalculando estudio sistemático de convergencia numérica...")
    convergencia = ejecutar_estudio_convergencia()
    csv_path = "salidas/convergencia.csv"
    exportar_convergencia_csv(convergencia, csv_path)
    print(f"Estudio de convergencia guardado en {csv_path}")

    # Mostrar filas destacadas
    print("\nResumen de Convergencia Numérica (Muestra):")
    print(f"{'N':>6} {'Paso h (s)':>12} {'Err Trapecio (J)':>18} {'Ord Trap':>10} {'Err Simpson (J)':>18} {'Ord Simp':>10}")
    for row in convergencia:
        if row["N"] in [4, 16, 64, 256, 1024, 4096, 16384]:
            ot = f"{row['order_trapezoid']:.2f}" if row['order_trapezoid'] > 0 else "-"
            os = f"{row['order_simpson']:.2f}" if row['order_simpson'] > 0 else "-"
            print(f"{row['N']:6d} {row['h_s']:12.4e} {row['err_trapezoid_J']:18.4e} {ot:>10} {row['err_simpson_J']:18.4e} {os:>10}")

    # 3. Guardar resumen JSON
    json_path = "salidas/resultados_tests.json"
    resultados_json = {
        "tests_ejecutados": test_result.testsRun,
        "tests_exitosos": test_result.wasSuccessful(),
        "errores": len(test_result.errors),
        "fallos": len(test_result.failures),
        "demostracion_potencia_finita_V0": {
            "estado": "DEMOSTRADO",
            "formula_cerrada": "P_static = T^(3/2) / sqrt(2 * rho * A)",
            "observacion": "A diferencia del modelo previo donde P(0) = 0, el modelo de disco captura la potencia requerida para impartir cantidad de movimiento a la estela en reposo."
        },
        "convergencia_resumen": {
            "orden_asintotico_trapecio_esperado": 2.0,
            "orden_asintotico_trapecio_observado": convergencia[-1]["order_trapezoid"],
            "orden_asintotico_simpson_esperado": 4.0,
            "orden_asintotico_simpson_observado": convergencia[-1]["order_simpson"],
            "error_relativo_simpson_N16384": convergencia[-1]["rel_err_simpson"],
        }
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultados_json, f, indent=2)
    print(f"Resultados de verificación guardados en {json_path}")

    if not test_result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
