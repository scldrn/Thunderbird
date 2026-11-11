#!/usr/bin/env python3
"""
===============================================================================
SUITE DE PRUEBAS AUTOMATIZADAS DE EQUILIBRIO VERTICAL C02
===============================================================================
Batería de pruebas analíticas independientes:
1. Simetría: invariancia en 4 cuadrantes, permutación por reflexión longitudinal
   (x -> -x: f1 <-> f3, f2 <-> f4) y lateral (y -> -y: f1 <-> f2, f3 <-> f4).
2. Masa nominal 5 kg con CG centrado (Fmax = 20.58 N y Fmax = 25.0 N).
3. CG en bordes y esquinas (longitudinal ±x, lateral ±y, esquinas extremas,
   y consistencia con INFORME-VERTICAL.md).
4. Falta de fuerza total (4 * Fmax < m * g, masa excesiva 10 kg).
5. Conversión CAD <-> FLU y consistencia física de actuadores.
6. Límites y singularidades analíticas (W = 0, saturación exacta W = 4*Fmax,
   puntos exteriores al polígono base, esquinas con masa reducida).
7. Espacio nulo y modo warp (ortogonalidad a matriz de equilibrio).
8. Comprobación exhaustiva de residuales numéricos (< 10^-11).
"""

import math
import unittest

from equilibrio_cg import (
    PropulsionGeometry,
    IntervalBounds,
    EquilibriumSolution,
    derivar_limites_f4,
    verificar_equilibrio,
    verificar_equilibrio_flu,
    cad_a_flu,
    flu_a_cad,
    max_fuerza_vertical_admisible,
    pseudo_inversa_sin_cotas,
)


class TestSimetria(unittest.TestCase):
    """Verifica propiedades de simetría en el plano XY para la configuración rectangular C02."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)
        self.m = 5.0
        self.Fmax = 20.58

    def test_simetria_factibilidad_cuadrantes(self):
        """La factibilidad y holgura deben ser estrictamente idénticas en los 4 cuadrantes (±x, ±y)."""
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
          f1(-x, y) = f3(x, y)  (Nariz/Izq <-> Cola/Izq)
          f2(-x, y) = f4(x, y)  (Nariz/Der <-> Cola/Der)
          f3(-x, y) = f1(x, y)
          f4(-x, y) = f2(x, y)

        Bajo reflexión lateral y -> -y:
          f1(x, -y) = f2(x, y)  (Nariz/Izq <-> Nariz/Der)
          f2(x, -y) = f1(x, y)
          f3(x, -y) = f4(x, y)  (Cola/Izq  <-> Cola/Der)
          f4(x, -y) = f3(x, y)
        """
        x, y = 0.050, 0.025
        sol_orig = verificar_equilibrio(self.m, x, y, self.Fmax, geom=self.geom, estrategia="centro_intervalo")
        sol_ref_x = verificar_equilibrio(self.m, -x, y, self.Fmax, geom=self.geom, estrategia="centro_intervalo")
        sol_ref_y = verificar_equilibrio(self.m, x, -y, self.Fmax, geom=self.geom, estrategia="centro_intervalo")

        self.assertTrue(sol_orig.es_factible)
        self.assertTrue(sol_ref_x.es_factible)
        self.assertTrue(sol_ref_y.es_factible)

        # Mapeo bajo reflexión X
        self.assertAlmostEqual(sol_ref_x.f1_N, sol_orig.f3_N, places=7)
        self.assertAlmostEqual(sol_ref_x.f2_N, sol_orig.f4_N, places=7)
        self.assertAlmostEqual(sol_ref_x.f3_N, sol_orig.f1_N, places=7)
        self.assertAlmostEqual(sol_ref_x.f4_N, sol_orig.f2_N, places=7)

        # Mapeo bajo reflexión Y
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

        # Totales marginales en CAD
        # S_rear = S_front = S_right = S_left = W/2 = 24.516625 N
        self.assertAlmostEqual(sol.S_rear_N, self.W_nominal / 2.0, places=7)
        self.assertAlmostEqual(sol.S_front_N, self.W_nominal / 2.0, places=7)
        self.assertAlmostEqual(sol.S_right_N, self.W_nominal / 2.0, places=7)
        self.assertAlmostEqual(sol.S_left_N, self.W_nominal / 2.0, places=7)

        # Intervalo de f4: f4_min = 24.516625 - 20.58 = 3.936625 N, f4_max = 20.58 N
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
    """Comprueba el comportamiento analítico en los límites del rectángulo de apoyo en CAD."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)
        self.m = 5.0
        self.W = self.m * 9.80665

    def test_borde_longitudinal_cola_5kg(self):
        """
        En x = +0.160 m (Cola CAD), y = 0: los módulos delanteros f1, f2 no pueden aportar.
        Los dos módulos traseros f3, f4 deben suministrar todo W = 49.03 N.
        - Fmax = 20.58 N: Capacidad trasera = 2 * 20.58 = 41.16 N < 49.03 N -> NO FACTIBLE.
        - Fmax = 25.00 N: Capacidad trasera = 2 * 25.00 = 50.00 N >= 49.03 N -> FACTIBLE.
        """
        sol_2058 = verificar_equilibrio(self.m, +0.160, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertFalse(sol_2058.es_factible)
        self.assertAlmostEqual(sol_2058.intervalo.holgura, 41.16 - self.W, places=5)

        sol_2500 = verificar_equilibrio(self.m, +0.160, 0.0, Fmax_N=25.00, geom=self.geom)
        self.assertTrue(sol_2500.es_factible)
        self.assertAlmostEqual(sol_2500.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f3_N, self.W / 2.0, places=7)
        self.assertAlmostEqual(sol_2500.f4_N, self.W / 2.0, places=7)

    def test_borde_longitudinal_nariz_5kg(self):
        """
        En x = -0.160 m (Nariz CAD), y = 0: análogo en la parte delantera.
        f3 = f4 = 0, f1 = f2 = W/2 = 24.5166 N.
        """
        sol_2500 = verificar_equilibrio(self.m, -0.160, 0.0, Fmax_N=25.00, geom=self.geom)
        self.assertTrue(sol_2500.es_factible)
        self.assertAlmostEqual(sol_2500.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f4_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f1_N, self.W / 2.0, places=7)
        self.assertAlmostEqual(sol_2500.f2_N, self.W / 2.0, places=7)

    def test_borde_lateral_derecha_5kg(self):
        """
        En y = +0.076 m (Derecha CAD, +y), x = 0:
        Los módulos de la izquierda f1, f3 son 0.
        Los módulos de la derecha f2, f4 soportan el peso W = 49.03 N.
        - Fmax = 20.58 N: 2 * 20.58 = 41.16 N < 49.03 N -> NO FACTIBLE.
        - Fmax = 25.00 N: f2 = f4 = W/2 = 24.5166 N -> FACTIBLE.
        """
        sol_2058 = verificar_equilibrio(self.m, 0.0, +0.076, Fmax_N=20.58, geom=self.geom)
        self.assertFalse(sol_2058.es_factible)

        sol_2500 = verificar_equilibrio(self.m, 0.0, +0.076, Fmax_N=25.00, geom=self.geom)
        self.assertTrue(sol_2500.es_factible)
        self.assertAlmostEqual(sol_2500.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f2_N, self.W / 2.0, places=7)
        self.assertAlmostEqual(sol_2500.f4_N, self.W / 2.0, places=7)

    def test_borde_lateral_izquierda_5kg(self):
        """
        En y = -0.076 m (Izquierda CAD, -y), x = 0:
        f2 = f4 = 0, f1 = f3 = W/2 = 24.5166 N.
        """
        sol_2500 = verificar_equilibrio(self.m, 0.0, -0.076, Fmax_N=25.00, geom=self.geom)
        self.assertTrue(sol_2500.es_factible)
        self.assertAlmostEqual(sol_2500.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f4_N, 0.0, places=7)
        self.assertAlmostEqual(sol_2500.f1_N, self.W / 2.0, places=7)
        self.assertAlmostEqual(sol_2500.f3_N, self.W / 2.0, places=7)

    def test_esquinas_5kg_no_factible(self):
        """
        En cada una de las 4 esquinas (±Lx, ±Ly), todo el peso W = 49.03 N recae
        sobre un único motor. Como Fmax <= 25.0 N, es no factible para 5 kg.
        """
        esquinas = [(0.160, 0.076), (0.160, -0.076), (-0.160, 0.076), (-0.160, -0.076)]
        for x, y in esquinas:
            sol_20 = verificar_equilibrio(self.m, x, y, Fmax_N=20.58, geom=self.geom)
            sol_25 = verificar_equilibrio(self.m, x, y, Fmax_N=25.00, geom=self.geom)
            self.assertFalse(sol_20.es_factible)
            self.assertFalse(sol_25.es_factible)

    def test_esquinas_masa_reducida_2kg(self):
        """
        Para m = 2.0 kg (W = 19.6133 N < 20.58 N), en cada esquina exactamente
        un motor provee W y los otros 3 son 0.
        """
        m_2kg = 2.0
        W_2kg = m_2kg * 9.80665

        # Esquina Cola/Derecha (+Lx, +Ly CAD) -> Motor 4
        sol_c_der = verificar_equilibrio(m_2kg, 0.160, 0.076, Fmax_N=20.58, geom=self.geom)
        self.assertTrue(sol_c_der.es_factible)
        self.assertAlmostEqual(sol_c_der.f4_N, W_2kg, places=7)
        self.assertAlmostEqual(sol_c_der.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol_c_der.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol_c_der.f3_N, 0.0, places=7)

        # Esquina Cola/Izquierda (+Lx, -Ly CAD) -> Motor 3
        sol_c_izq = verificar_equilibrio(m_2kg, 0.160, -0.076, Fmax_N=20.58, geom=self.geom)
        self.assertTrue(sol_c_izq.es_factible)
        self.assertAlmostEqual(sol_c_izq.f3_N, W_2kg, places=7)
        self.assertAlmostEqual(sol_c_izq.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol_c_izq.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol_c_izq.f4_N, 0.0, places=7)

        # Esquina Nariz/Derecha (-Lx, +Ly CAD) -> Motor 2
        sol_n_der = verificar_equilibrio(m_2kg, -0.160, 0.076, Fmax_N=20.58, geom=self.geom)
        self.assertTrue(sol_n_der.es_factible)
        self.assertAlmostEqual(sol_n_der.f2_N, W_2kg, places=7)
        self.assertAlmostEqual(sol_n_der.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol_n_der.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol_n_der.f4_N, 0.0, places=7)

        # Esquina Nariz/Izquierda (-Lx, -Ly CAD) -> Motor 1
        sol_n_izq = verificar_equilibrio(m_2kg, -0.160, -0.076, Fmax_N=20.58, geom=self.geom)
        self.assertTrue(sol_n_izq.es_factible)
        self.assertAlmostEqual(sol_n_izq.f1_N, W_2kg, places=7)
        self.assertAlmostEqual(sol_n_izq.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol_n_izq.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol_n_izq.f4_N, 0.0, places=7)

    def test_consistencia_informe_vertical(self):
        """
        Verifica los puntos longitudinales de INFORME-VERTICAL.md:
        - x = 0.096 m: Factible ('Sí, con poco margen ideal', Fz_max = 51.45 N > 49.03 N)
        - x = 0.120 m: No factible (Fz_max = 47.04 N < 49.03 N)
        """
        sol_096 = verificar_equilibrio(self.m, 0.096, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertTrue(sol_096.es_factible)
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
        """Si Fmax = 10.0 N, 4 * Fmax = 40.0 N < 49.03 N, imposible equilibrar."""
        sol = verificar_equilibrio(5.0, 0.0, 0.0, Fmax_N=10.0, geom=self.geom)
        self.assertFalse(sol.es_factible)
        self.assertLess(sol.intervalo.holgura, 0.0)

    def test_masa_10kg(self):
        """
        Para m = 10 kg (W = 98.07 N):
        - Fmax = 20.58 N: 4 * 20.58 = 82.32 N < 98.07 N -> Imposible en todo el dominio.
        - Fmax = 25.00 N: 4 * 25.0 = 100.0 N > 98.07 N -> Factible solo cerca de (0,0).
        """
        sol_10kg_2058 = verificar_equilibrio(10.0, 0.0, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertFalse(sol_10kg_2058.es_factible)

        sol_10kg_2500 = verificar_equilibrio(10.0, 0.0, 0.0, Fmax_N=25.00, geom=self.geom)
        self.assertTrue(sol_10kg_2500.es_factible)
        self.assertAlmostEqual(sol_10kg_2500.f1_N, 98.0665 / 4.0, places=5)
        self.assertLess(sol_10kg_2500.margen_fmax_N, 0.5)  # 25 - 24.516 = 0.48 N


class TestTransformacionFLU(unittest.TestCase):
    """Verifica la coherencia entre el sistema CAD oficial y el sistema de vuelo FLU."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)
        self.m = 5.0
        self.Fmax = 20.58

    def test_conversion_coordenadas(self):
        """x_FLU = -x_CAD, y_FLU = -y_CAD, z_FLU = +z_CAD."""
        x_cad, y_cad, z_cad = 0.120, -0.050, 0.010
        x_flu, y_flu, z_flu = cad_a_flu(x_cad, y_cad, z_cad)
        self.assertEqual(x_flu, -0.120)  # Cola CAD (+x) es Aft FLU (-x)
        self.assertEqual(y_flu, +0.050)  # Izquierda CAD (-y) es Left FLU (+y)
        self.assertEqual(z_flu, +0.010)

        # Inversión exacta
        rx, ry, rz = flu_a_cad(x_flu, y_flu, z_flu)
        self.assertEqual((rx, ry, rz), (x_cad, y_cad, z_cad))

    def test_consistencia_evaluacion_flu(self):
        """
        Evaluar en CAD (x_cad, y_cad) debe dar exactamente la misma solución
        que evaluar en FLU (x_flu, y_flu) = (-x_cad, -y_cad).
        """
        puntos = [(0.060, 0.030), (-0.080, 0.020), (0.096, 0.0), (-0.050, -0.025)]
        for x_cad, y_cad in puntos:
            x_flu = -x_cad
            y_flu = -y_cad

            sol_cad = verificar_equilibrio(self.m, x_cad, y_cad, self.Fmax, geom=self.geom)
            sol_flu = verificar_equilibrio_flu(self.m, x_flu, y_flu, self.Fmax, geom=self.geom)

            self.assertEqual(sol_cad.es_factible, sol_flu.es_factible)
            self.assertAlmostEqual(sol_cad.intervalo.holgura, sol_flu.intervalo.holgura, places=9)
            if sol_cad.es_factible:
                self.assertAlmostEqual(sol_cad.f1_N, sol_flu.f1_N, places=9)
                self.assertAlmostEqual(sol_cad.f2_N, sol_flu.f2_N, places=9)
                self.assertAlmostEqual(sol_cad.f3_N, sol_flu.f3_N, places=9)
                self.assertAlmostEqual(sol_cad.f4_N, sol_flu.f4_N, places=9)


class TestLimitesYSingularidades(unittest.TestCase):
    """Pruebas analíticas de singularidades, límites teóricos y dominios admisibles."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)

    def test_peso_cero(self):
        """Con m = 0 (W = 0), todas las fuerzas requeridas deben ser 0 y la holgura es 0 (solución única [0, 0])."""
        sol = verificar_equilibrio(0.0, 0.0, 0.0, Fmax_N=20.58, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.W_N, 0.0, places=9)
        self.assertAlmostEqual(sol.f1_N, 0.0, places=9)
        self.assertAlmostEqual(sol.f2_N, 0.0, places=9)
        self.assertAlmostEqual(sol.f3_N, 0.0, places=9)
        self.assertAlmostEqual(sol.f4_N, 0.0, places=9)
        self.assertAlmostEqual(sol.intervalo.holgura, 0.0, places=7)

    def test_saturacion_exacta_hover_4Fmax(self):
        """
        Con W = 4 * Fmax exactamente en (0,0), existe una solución única:
        f_i = Fmax, holgura = 0.
        """
        fmax = 20.0
        m_hover = (4.0 * fmax) / 9.80665
        sol = verificar_equilibrio(m_hover, 0.0, 0.0, Fmax_N=fmax, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.intervalo.holgura, 0.0, places=7)
        self.assertAlmostEqual(sol.f1_N, fmax, places=7)
        self.assertAlmostEqual(sol.f2_N, fmax, places=7)
        self.assertAlmostEqual(sol.f3_N, fmax, places=7)
        self.assertAlmostEqual(sol.f4_N, fmax, places=7)
        self.assertAlmostEqual(sol.res_fuerza_N, 0.0, places=9)

    def test_fuera_del_poligono_soporte(self):
        """Cualquier CG con |x| > Lx o |y| > Ly debe tener capacidad Fz_max = 0."""
        self.assertEqual(max_fuerza_vertical_admisible(0.200, 0.0, 20.58, geom=self.geom), 0.0)
        self.assertEqual(max_fuerza_vertical_admisible(-0.180, 0.0, 20.58, geom=self.geom), 0.0)
        self.assertEqual(max_fuerza_vertical_admisible(0.0, 0.100, 20.58, geom=self.geom), 0.0)
        self.assertEqual(max_fuerza_vertical_admisible(0.0, -0.090, 20.58, geom=self.geom), 0.0)

        # En verificar_equilibrio debe ser no factible
        sol_ext = verificar_equilibrio(5.0, 0.200, 0.0, Fmax_N=25.0, geom=self.geom)
        self.assertFalse(sol_ext.es_factible)


class TestEspacioNuloYWarpMode(unittest.TestCase):
    """Verifica que el modo warp (espacio nulo) conserve rigurosamente las ecuaciones de equilibrio."""

    def test_ortogonalidad_modo_warp(self):
        """
        El vector v_null = [1, -1, -1, 1]^T satisface:
          A * v_null = [0, 0, 0]^T
        donde A es la matriz de suma vertical, cabeceo y alabeo.
        """
        geom = PropulsionGeometry(lx=0.160, ly=0.076)
        Lx = geom.lx
        Ly = geom.ly

        v_null = [1.0, -1.0, -1.0, 1.0]

        # 1. Suma vertical
        suma_v = sum(v_null)
        self.assertAlmostEqual(suma_v, 0.0, places=12)

        # 2. Cabeceo CAD: -Lx*v1 - Lx*v2 + Lx*v3 + Lx*v4
        mom_pitch = -Lx * v_null[0] - Lx * v_null[1] + Lx * v_null[2] + Lx * v_null[3]
        self.assertAlmostEqual(mom_pitch, 0.0, places=12)

        # 3. Alabeo CAD: -Ly*v1 + Ly*v2 - Ly*v3 + Ly*v4
        mom_roll = -Ly * v_null[0] + Ly * v_null[1] - Ly * v_null[2] + Ly * v_null[3]
        self.assertAlmostEqual(mom_roll, 0.0, places=12)

    def test_perturbacion_solucion_conserva_equilibrio(self):
        """Cualquier perturbación delta a lo largo de v_null preserva residuales idénticos a 0."""
        geom = PropulsionGeometry()
        sol = verificar_equilibrio(5.0, 0.040, 0.020, Fmax_N=20.58, geom=geom)
        self.assertTrue(sol.es_factible)

        f_base = [sol.f1_N, sol.f2_N, sol.f3_N, sol.f4_N]
        v_null = [1.0, -1.0, -1.0, 1.0]

        for delta in [-1.5, -0.5, 0.0, 0.5, 1.2]:
            f_pert = [f_base[i] + delta * v_null[i] for i in range(4)]
            # Comprobación de suma de fuerzas
            self.assertAlmostEqual(sum(f_pert), sol.W_N, places=10)
            # Comprobación de alabeo
            mx = -geom.ly * f_pert[0] + geom.ly * f_pert[1] - geom.ly * f_pert[2] + geom.ly * f_pert[3]
            self.assertAlmostEqual(mx, 0.020 * sol.W_N, places=10)
            # Comprobación de cabeceo
            my = -geom.lx * f_pert[0] - geom.lx * f_pert[1] + geom.lx * f_pert[2] + geom.lx * f_pert[3]
            self.assertAlmostEqual(my, 0.040 * sol.W_N, places=10)


class TestComprobacionExhaustivaResiduales(unittest.TestCase):
    """Comprueba en una malla fina que todas las soluciones factibles satisfagan residuales < 10^-11."""

    def test_barrido_malla_fina_residuales(self):
        geom = PropulsionGeometry()
        m = 5.0
        for x in [-0.10, -0.05, 0.0, 0.05, 0.10]:
            for y in [-0.04, -0.02, 0.0, 0.02, 0.04]:
                for fmax in [20.58, 25.00]:
                    for strat in ["centro_intervalo", "pseudo_inversa_proyectada"]:
                        sol = verificar_equilibrio(m, x, y, fmax, geom=geom, estrategia=strat)
                        if sol.es_factible:
                            self.assertAlmostEqual(sol.res_fuerza_N, 0.0, places=10)
                            self.assertAlmostEqual(sol.res_momento_x_Nm, 0.0, places=10)
                            self.assertAlmostEqual(sol.res_momento_y_Nm, 0.0, places=10)
                            for fi in [sol.f1_N, sol.f2_N, sol.f3_N, sol.f4_N]:
                                self.assertGreaterEqual(fi, -1e-11)
                                self.assertLessEqual(fi, fmax + 1e-11)


if __name__ == "__main__":
    unittest.main()
