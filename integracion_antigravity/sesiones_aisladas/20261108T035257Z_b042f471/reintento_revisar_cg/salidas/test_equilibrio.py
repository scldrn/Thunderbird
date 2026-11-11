#!/usr/bin/env python3
"""
===============================================================================
SUITE DE PRUEBAS AUTOMATIZADAS DE EQUILIBRIO VERTICAL C02
===============================================================================
Ejecuta la batería de pruebas requerida:
1. Pruebas de simetría (reflexión longitudinal x -> -x, lateral y -> -y, e inversión).
2. Masa 5 kg con CG centrado (Fmax = 20.58 N y Fmax = 25.0 N).
3. CG en borde (bordes longitudinales, laterales, esquinas, y consistencia con INFORME-VERTICAL.md).
4. Falta de fuerza total (4 * Fmax < m * g, masa excesiva 10 kg).
5. Comprobación constructiva de fuerzas y residuales exactos.
"""

import math
import os
import sys
import unittest

# Asegurar importación de equilibrio_cg en salidas/
_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from equilibrio_cg import (
    PropulsionGeometry,
    derivar_limites_f4,
    verificar_equilibrio,
    max_fuerza_vertical_admisible,
    pseudo_inversa_sin_cotas,
    calcular_fuerzas_desde_f4,
)


class TestSimetria(unittest.TestCase):
    """Verifica propiedades de simetría en el plano XY para la configuración rectangular."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)
        self.m = 5.0
        self.Fmax = 20.58

    def test_simetria_factibilidad_cuadrantes(self):
        """La factibilidad debe ser estrictamente idéntica en los 4 cuadrantes (±x, ±y)."""
        puntos_prueba = [
            (0.040, 0.020),
            (0.080, 0.030),
            (0.096, 0.010),
            (0.120, 0.040),
            (0.160, 0.076),
        ]
        for x, y in puntos_prueba:
            sol_pp = verificar_equilibrio(self.m, +x, +y, self.Fmax, geom=self.geom)
            sol_np = verificar_equilibrio(self.m, -x, +y, self.Fmax, geom=self.geom)
            sol_pn = verificar_equilibrio(self.m, +x, -y, self.Fmax, geom=self.geom)
            sol_nn = verificar_equilibrio(self.m, -x, -y, self.Fmax, geom=self.geom)

            # Todas las banderas de factibilidad deben coincidir
            self.assertEqual(
                sol_pp.es_factible, sol_np.es_factible,
                f"Discrepancia de factibilidad en reflexión X para ({x}, {y})"
            )
            self.assertEqual(
                sol_pp.es_factible, sol_pn.es_factible,
                f"Discrepancia de factibilidad en reflexión Y para ({x}, {y})"
            )
            self.assertEqual(
                sol_pp.es_factible, sol_nn.es_factible,
                f"Discrepancia de factibilidad en inversión para ({x}, {y})"
            )

            # Las holguras deben ser idénticas
            self.assertAlmostEqual(sol_pp.intervalo.holgura, sol_np.intervalo.holgura, places=9)
            self.assertAlmostEqual(sol_pp.intervalo.holgura, sol_pn.intervalo.holgura, places=9)
            self.assertAlmostEqual(sol_pp.intervalo.holgura, sol_nn.intervalo.holgura, places=9)

    def test_permutacion_fuerzas_por_reflexion(self):
        """
        Bajo reflexión longitudinal x -> -x:
          f1(-x, y) = f3(x, y)
          f2(-x, y) = f4(x, y)
          f3(-x, y) = f1(x, y)
          f4(-x, y) = f2(x, y)

        Bajo reflexión lateral y -> -y:
          f1(x, -y) = f2(x, y)
          f2(x, -y) = f1(x, y)
          f3(x, -y) = f4(x, y)
          f4(x, -y) = f3(x, y)
        """
        x, y = 0.050, 0.025
        sol_orig = verificar_equilibrio(self.m, x, y, self.Fmax, geom=self.geom, estrategia="centro_intervalo")
        sol_ref_x = verificar_equilibrio(self.m, -x, y, self.Fmax, geom=self.geom, estrategia="centro_intervalo")
        sol_ref_y = verificar_equilibrio(self.m, x, -y, self.Fmax, geom=self.geom, estrategia="centro_intervalo")

        self.assertTrue(sol_orig.es_factible)
        self.assertTrue(sol_ref_x.es_factible)
        self.assertTrue(sol_ref_y.es_factible)

        # Comprobación de mapeo bajo reflexión X
        self.assertAlmostEqual(sol_ref_x.f1_N, sol_orig.f3_N, places=7)
        self.assertAlmostEqual(sol_ref_x.f2_N, sol_orig.f4_N, places=7)
        self.assertAlmostEqual(sol_ref_x.f3_N, sol_orig.f1_N, places=7)
        self.assertAlmostEqual(sol_ref_x.f4_N, sol_orig.f2_N, places=7)

        # Comprobación de mapeo bajo reflexión Y
        self.assertAlmostEqual(sol_ref_y.f1_N, sol_orig.f2_N, places=7)
        self.assertAlmostEqual(sol_ref_y.f2_N, sol_orig.f1_N, places=7)
        self.assertAlmostEqual(sol_ref_y.f3_N, sol_orig.f4_N, places=7)
        self.assertAlmostEqual(sol_ref_y.f4_N, sol_orig.f3_N, places=7)


class TestMasa5kgCGCentrado(unittest.TestCase):
    """Comprueba el caso nominal de 5 kg con CG centrado (0, 0)."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)
        self.m = 5.0
        self.g = 9.80665
        self.W_nominal = self.m * self.g  # 49.03325 N
        self.f_simetrica = self.W_nominal / 4.0  # 12.2583125 N

    def test_centrado_Fmax_20_58(self):
        """Con Fmax = 20.58 N, 5 kg en (0,0) debe ser factible con f_i = W/4."""
        sol = verificar_equilibrio(self.m, 0.0, 0.0, Fmax_N=20.58, g_m_s2=self.g, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.W_N, 49.03325, places=5)

        # Fuerzas simétricas
        self.assertAlmostEqual(sol.f1_N, self.f_simetrica, places=7)
        self.assertAlmostEqual(sol.f2_N, self.f_simetrica, places=7)
        self.assertAlmostEqual(sol.f3_N, self.f_simetrica, places=7)
        self.assertAlmostEqual(sol.f4_N, self.f_simetrica, places=7)

        # Residuales numéricos nulos
        self.assertAlmostEqual(sol.res_fuerza_N, 0.0, places=10)
        self.assertAlmostEqual(sol.res_momento_x_Nm, 0.0, places=10)
        self.assertAlmostEqual(sol.res_momento_y_Nm, 0.0, places=10)

        # Margen positivo
        self.assertGreater(sol.margen_fmax_N, 8.0)  # 20.58 - 12.258 = 8.32 N

        # Intervalo de f4
        # S_rear = W/2 = 24.5166 N. S_rear - Fmax = 3.9366 N.
        self.assertAlmostEqual(sol.intervalo.f4_min, 24.516625 - 20.58, places=5)
        self.assertAlmostEqual(sol.intervalo.f4_max, 20.58, places=5)
        self.assertGreater(sol.intervalo.holgura, 0.0)

    def test_centrado_Fmax_25_00(self):
        """Con Fmax = 25.0 N, mayor margen de empuje."""
        sol = verificar_equilibrio(self.m, 0.0, 0.0, Fmax_N=25.00, g_m_s2=self.g, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.f1_N, self.f_simetrica, places=7)
        self.assertAlmostEqual(sol.margen_fmax_N, 25.0 - self.f_simetrica, places=7)
        self.assertAlmostEqual(sol.intervalo.f4_min, 0.0, places=5)
        self.assertAlmostEqual(sol.intervalo.f4_max, 24.516625, places=5)


class TestCGenBorde(unittest.TestCase):
    """Comprueba el comportamiento analítico en los límites del rectángulo de apoyo."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)
        self.m = 5.0
        self.W = self.m * 9.80665

    def test_borde_longitudinal_5kg_Fmax20_58_no_factible(self):
        """
        En x = +0.160 m, y = 0: los módulos delanteros no pueden aportar.
        Los dos traseros deben suministrar todo W = 49.03 N.
        Capacidad trasera máxima = 2 * 20.58 = 41.16 N < 49.03 N.
        Debe resultar NO FACTIBLE con holgura negativa de -7.87 N.
        """
        sol = verificar_equilibrio(self.m, 0.160, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertFalse(sol.es_factible)
        self.assertLess(sol.intervalo.holgura, 0.0)
        # Falta exactamente: 41.16 - 49.03325 = -7.87325 N
        self.assertAlmostEqual(sol.intervalo.holgura, 41.16 - self.W, places=5)

    def test_borde_longitudinal_5kg_Fmax25_00_factible(self):
        """
        En x = +0.160 m, y = 0 con Fmax = 25.0 N:
        Capacidad trasera máxima = 2 * 25.0 = 50.0 N >= 49.033 N.
        Debe ser FACTIBLE con f1=f2=0 y f3=f4=W/2 = 24.517 N.
        """
        sol = verificar_equilibrio(self.m, 0.160, 0.0, Fmax_N=25.00, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol.f3_N, self.W / 2.0, places=7)
        self.assertAlmostEqual(sol.f4_N, self.W / 2.0, places=7)
        self.assertAlmostEqual(sol.res_fuerza_N, 0.0, places=10)
        self.assertAlmostEqual(sol.res_momento_y_Nm, 0.0, places=10)

    def test_borde_lateral_5kg(self):
        """En y = +0.076 m, x = 0: análogo al longitudinal."""
        sol_2058 = verificar_equilibrio(self.m, 0.0, 0.076, Fmax_N=20.58, geom=self.geom)
        self.assertFalse(sol_2058.es_factible)

        sol_2500 = verificar_equilibrio(self.m, 0.0, 0.076, Fmax_N=25.00, geom=self.geom)
        self.assertTrue(sol_2500.es_factible)
        self.assertAlmostEqual(sol_2500.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f2_N, self.W / 2.0, places=7)
        self.assertAlmostEqual(sol_2500.f4_N, self.W / 2.0, places=7)

    def test_esquina_5kg_no_factible_ambos_fmax(self):
        """
        En (0.160, 0.076), solo el ventilador 4 puede empujar (f4 = W = 49.03 N).
        Como Fmax es 20.58 N o 25.0 N, supera el límite de un solo motor.
        Debe ser NO FACTIBLE en ambos.
        """
        sol_2058 = verificar_equilibrio(self.m, 0.160, 0.076, Fmax_N=20.58, geom=self.geom)
        self.assertFalse(sol_2058.es_factible)

        sol_2500 = verificar_equilibrio(self.m, 0.160, 0.076, Fmax_N=25.00, geom=self.geom)
        self.assertFalse(sol_2500.es_factible)

    def test_borde_longitudinal_masa_reducida_3_5kg(self):
        """Con m = 3.5 kg (W = 34.32 N), el borde x = 0.160 m sí es factible con Fmax = 20.58 N."""
        m_red = 3.5
        W_red = m_red * 9.80665
        sol = verificar_equilibrio(m_red, 0.160, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.f3_N, W_red / 2.0, places=7)
        self.assertAlmostEqual(sol.f4_N, W_red / 2.0, places=7)
        self.assertLessEqual(sol.f3_N, 20.58)

    def test_consistencia_informe_vertical(self):
        """
        Verifica los puntos longitudinales de INFORME-VERTICAL.md:
        - x = 0.096 m: Factible ('Sí, con poco margen ideal')
        - x = 0.120 m: No factible (Fz_max = 47.04 N < 49.03 N)
        """
        sol_096 = verificar_equilibrio(self.m, 0.096, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertTrue(sol_096.es_factible)
        # Capacidad máxima según INFORME-VERTICAL = 51.45 N
        cap_096 = max_fuerza_vertical_admisible(0.096, 0.0, 20.58, geom=self.geom)
        self.assertAlmostEqual(cap_096, 51.45, places=2)
        self.assertGreater(cap_096, self.W)

        sol_120 = verificar_equilibrio(self.m, 0.120, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertFalse(sol_120.es_factible)
        cap_120 = max_fuerza_vertical_admisible(0.120, 0.0, 20.58, geom=self.geom)
        self.assertAlmostEqual(cap_120, 47.04, places=2)
        self.assertLess(cap_120, self.W)


class TestFaltaDeFuerzaTotal(unittest.TestCase):
    """Comprueba situaciones donde el empuje total disponible es insuficiente."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)

    def test_fmax_insuficiente_para_5kg(self):
        """Si Fmax = 10.0 N, 4 * Fmax = 40.0 N < 49.03 N, imposible equilibrar en cualquier CG."""
        sol = verificar_equilibrio(5.0, 0.0, 0.0, Fmax_N=10.0, geom=self.geom)
        self.assertFalse(sol.es_factible)
        self.assertLess(sol.intervalo.holgura, 0.0)

    def test_masa_10kg(self):
        """
        Para m = 10 kg (W = 98.07 N):
        - Fmax = 20.58 N: 4 * 20.58 = 82.32 N < 98.07 N -> Imposible en todo el dominio.
        - Fmax = 25.0 N: 4 * 25.0 = 100.0 N > 98.07 N -> Solo factible en un rango muy estrecho cerca de (0,0).
        """
        sol_10kg_2058 = verificar_equilibrio(10.0, 0.0, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertFalse(sol_10kg_2058.es_factible)

        sol_10kg_2500 = verificar_equilibrio(10.0, 0.0, 0.0, Fmax_N=25.0, geom=self.geom)
        self.assertTrue(sol_10kg_2500.es_factible)
        # Margen muy pequeño
        self.assertAlmostEqual(sol_10kg_2500.f1_N, 98.0665 / 4.0, places=5)
        self.assertLess(sol_10kg_2500.margen_fmax_N, 0.5)  # 25 - 24.516 = 0.48 N


class TestConstruccionYVerificacionNumerica(unittest.TestCase):
    """Comprueba que toda solución factible satisfaga las ecuaciones de equilibrio y cotas."""

    def test_barrido_interior_consistencia(self):
        geom = PropulsionGeometry()
        for x in [-0.08, -0.04, 0.0, 0.04, 0.08]:
            for y in [-0.038, 0.0, 0.038]:
                for fmax in [20.58, 25.0]:
                    for strat in ["centro_intervalo", "pseudo_inversa_proyectada"]:
                        sol = verificar_equilibrio(5.0, x, y, fmax, geom=geom, estrategia=strat)
                        if sol.es_factible:
                            # 1. Fuerza total
                            self.assertAlmostEqual(
                                sol.f1_N + sol.f2_N + sol.f3_N + sol.f4_N,
                                sol.W_N,
                                places=10,
                                msg=f"Error vertical en ({x}, {y}) con {strat}"
                            )
                            # 2. Residuales
                            self.assertAlmostEqual(sol.res_fuerza_N, 0.0, places=10)
                            self.assertAlmostEqual(sol.res_momento_x_Nm, 0.0, places=10)
                            self.assertAlmostEqual(sol.res_momento_y_Nm, 0.0, places=10)
                            # 3. Cotas individuales
                            for i, f in enumerate([sol.f1_N, sol.f2_N, sol.f3_N, sol.f4_N], start=1):
                                self.assertGreaterEqual(f, -1e-12, f"f{i} negativo en ({x}, {y})")
                                self.assertLessEqual(f, fmax + 1e-12, f"f{i} excede Fmax en ({x}, {y})")


class TestCasosBordeYPropiedadesAnaliticas(unittest.TestCase):
    """Auditoría de casos de borde extremos, signos y propiedades de optimización."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)
        self.Fmax = 20.58
        self.g = 9.80665

    def test_esquina_con_masa_baja_factible(self):
        """En una esquina (+Lx, +Ly) con peso W <= Fmax (p. ej. m=1 kg), es factible con solo f4=W."""
        m_baja = 1.0
        W_baja = m_baja * self.g  # 9.80665 N <= 20.58 N
        sol = verificar_equilibrio(m_baja, 0.160, 0.076, self.Fmax, g_m_s2=self.g, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol.f4_N, W_baja, places=7)
        self.assertAlmostEqual(sol.res_fuerza_N, 0.0, places=10)
        self.assertAlmostEqual(sol.res_momento_x_Nm, 0.0, places=10)
        self.assertAlmostEqual(sol.res_momento_y_Nm, 0.0, places=10)

    def test_peso_cero(self):
        """Con masa cero, el equilibrio trivial es f_i = 0."""
        sol = verificar_equilibrio(0.0, 0.0, 0.0, self.Fmax, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol.f4_N, 0.0, places=7)

    def test_peso_negativo_no_factible(self):
        """Masa o peso negativo debe ser rechazado como no factible."""
        sol = verificar_equilibrio(-1.0, 0.0, 0.0, self.Fmax, geom=self.geom)
        self.assertFalse(sol.es_factible)

    def test_fmax_negativo_no_factible(self):
        """Un Fmax no positivo no puede generar sustentación admisible."""
        sol = verificar_equilibrio(5.0, 0.0, 0.0, -10.0, geom=self.geom)
        self.assertFalse(sol.es_factible)

    def test_saturacion_exacta_cuatro_motores(self):
        """En (0,0), W = 4*Fmax debe dar solución única f_i = Fmax con holgura cero."""
        W_sat = 4.0 * self.Fmax
        m_sat = W_sat / self.g
        sol = verificar_equilibrio(m_sat, 0.0, 0.0, self.Fmax, g_m_s2=self.g, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.intervalo.holgura, 0.0, places=8)
        self.assertAlmostEqual(sol.f1_N, self.Fmax, places=7)
        self.assertAlmostEqual(sol.f2_N, self.Fmax, places=7)
        self.assertAlmostEqual(sol.f3_N, self.Fmax, places=7)
        self.assertAlmostEqual(sol.f4_N, self.Fmax, places=7)

        # Si supera por un diferencial, debe ser no factible
        sol_over = verificar_equilibrio(m_sat + 0.01, 0.0, 0.0, self.Fmax, g_m_s2=self.g, geom=self.geom)
        self.assertFalse(sol_over.es_factible)

    def test_puntos_fuera_del_rectangulo_geometrico(self):
        """Cualquier CG con |x| > Lx o |y| > Ly debe ser no factible con sustentación positiva."""
        puntos_fuera = [
            (0.161, 0.0),
            (-0.161, 0.0),
            (0.0, 0.077),
            (0.0, -0.077),
            (0.200, 0.100),
        ]
        for x, y in puntos_fuera:
            sol = verificar_equilibrio(5.0, x, y, self.Fmax, geom=self.geom)
            self.assertFalse(sol.es_factible, f"Punto fuera ({x}, {y}) resultó factible")
            cap = max_fuerza_vertical_admisible(x, y, self.Fmax, geom=self.geom)
            self.assertEqual(cap, 0.0)

    def test_optimizacion_norma_pseudoinversa_proyectada(self):
        """
        Verifica que en casos donde la solución LS sin cotas viola los límites [0, Fmax],
        la solución pseudo_inversa_proyectada minimice estrictamente la norma ||f||^2
        en comparación con una discretización fina de todo el intervalo admisible [f4_min, f4_max].
        """
        # Caso conocido donde f1_LS > Fmax
        sol_pi = verificar_equilibrio(5.0, -0.10, -0.01, self.Fmax, geom=self.geom, estrategia="pseudo_inversa_proyectada")
        self.assertTrue(sol_pi.es_factible)
        norm_pi = sol_pi.f1_N**2 + sol_pi.f2_N**2 + sol_pi.f3_N**2 + sol_pi.f4_N**2

        # Muestreo fino de 2000 puntos en el intervalo admisible
        f4_min = sol_pi.intervalo.f4_min
        f4_max = sol_pi.intervalo.f4_max
        min_norm_grid = float("inf")
        for i in range(2001):
            f4_test = f4_min + (f4_max - f4_min) * (i / 2000.0)
            f1, f2, f3, f4 = calcular_fuerzas_desde_f4(f4_test, sol_pi.S_rear_N, sol_pi.S_front_N, sol_pi.S_left_N)
            norm_test = f1**2 + f2**2 + f3**2 + f4**2
            if norm_test < min_norm_grid:
                min_norm_grid = norm_test

        self.assertAlmostEqual(norm_pi, min_norm_grid, places=6)


if __name__ == "__main__":
    unittest.main()
