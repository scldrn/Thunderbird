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
import unittest

from equilibrio_cg import (
    PropulsionGeometry,
    derivar_limites_f4,
    verificar_equilibrio,
    max_fuerza_vertical_admisible,
    pseudo_inversa_sin_cotas,
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


class TestAuditoriaSignosYConvenciones(unittest.TestCase):
    """Auditoría de signos, ejes coordenados y espacio nulo."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)

    def test_convencion_ejes_y_coordenadas_propulsores(self):
        """Verifica la coherencia entre el sistema CAD C02 y la matriz de propulsión."""
        pos = self.geom.positions
        # Modulo 1: (-Lx, -Ly) -> Nariz / Derecha
        self.assertEqual(pos[0], (-0.160, -0.076))
        # Modulo 2: (-Lx, +Ly) -> Nariz / Izquierda
        self.assertEqual(pos[1], (-0.160, +0.076))
        # Modulo 3: (+Lx, -Ly) -> Cola / Derecha
        self.assertEqual(pos[2], (+0.160, -0.076))
        # Modulo 4: (+Lx, +Ly) -> Cola / Izquierda
        self.assertEqual(pos[3], (+0.160, +0.076))

    def test_signo_momento_alabeo(self):
        """Un CG con y_cg > 0 (babor/izquierda) debe cargar los motores 2 y 4 (S_left > S_right)."""
        sol = verificar_equilibrio(5.0, 0.0, 0.020, 25.0, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertGreater(sol.S_left_N, sol.S_right_N)
        # La suma de f2 + f4 debe igualar S_left exactamente
        self.assertAlmostEqual(sol.f2_N + sol.f4_N, sol.S_left_N, places=7)
        self.assertAlmostEqual(sol.f1_N + sol.f3_N, sol.S_right_N, places=7)

    def test_signo_momento_cabeceo(self):
        """Un CG con x_cg > 0 (cola) debe cargar los motores 3 y 4 (S_rear > S_front)."""
        sol = verificar_equilibrio(5.0, 0.050, 0.0, 25.0, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertGreater(sol.S_rear_N, sol.S_front_N)
        self.assertAlmostEqual(sol.f3_N + sol.f4_N, sol.S_rear_N, places=7)
        self.assertAlmostEqual(sol.f1_N + sol.f2_N, sol.S_front_N, places=7)

    def test_modo_torsion_espacio_nulo(self):
        """
        El vector v_null = [+1, -1, -1, +1]^T pertenece al núcleo de A:
        A * v_null = 0 (cero fuerza vertical, cero cabeceo, cero alabeo).
        """
        v_null = [1.0, -1.0, -1.0, 1.0]
        # Suma de fuerzas verticales
        self.assertEqual(sum(v_null), 0.0)
        # Momento alabeo (sum y_i * v_i)
        pos = self.geom.positions
        m_x = sum(p[1] * v for p, v in zip(pos, v_null))
        self.assertAlmostEqual(m_x, 0.0, places=15)
        # Momento cabeceo (sum x_i * v_i)
        m_y = sum(p[0] * v for p, v in zip(pos, v_null))
        self.assertAlmostEqual(m_y, 0.0, places=15)


class TestAuditoriaCasosBordesAvanzados(unittest.TestCase):
    """Auditoría de casos en bordes geométricos, esquinas y límites de saturación."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)

    def test_cuatro_esquinas_aisladas(self):
        """
        En cada una de las 4 esquinas del rectángulo con m = 1.0 kg (W = 9.80665 N <= Fmax),
        únicamente el módulo de esa esquina debe suministrar todo el empuje (f_k = W),
        los otros tres deben ser idénticamente 0, y la holgura debe ser exactamente 0.
        """
        m = 1.0
        W = m * 9.80665
        Fmax = 20.58
        esquinas = [
            (-self.geom.lx, -self.geom.ly, 0),  # Módulo 1
            (-self.geom.lx, +self.geom.ly, 1),  # Módulo 2
            (+self.geom.lx, -self.geom.ly, 2),  # Módulo 3
            (+self.geom.lx, +self.geom.ly, 3),  # Módulo 4
        ]
        for x, y, idx in esquinas:
            sol = verificar_equilibrio(m, x, y, Fmax, geom=self.geom)
            self.assertTrue(sol.es_factible, f"Fallo en esquina ({x}, {y})")
            self.assertAlmostEqual(sol.intervalo.holgura, 0.0, places=10)
            fuerzas = [sol.f1_N, sol.f2_N, sol.f3_N, sol.f4_N]
            for i, f in enumerate(fuerzas):
                if i == idx:
                    self.assertAlmostEqual(f, W, places=7)
                else:
                    self.assertAlmostEqual(f, 0.0, places=7)

    def test_cuatro_bordes_rectangulares(self):
        """
        En los puntos medios de los 4 bordes para m = 2.0 kg (W = 19.61 N <= 2*Fmax),
        solo los dos módulos de ese borde deben empujar (W/2 cada uno), y holgura = 0.
        """
        m = 2.0
        W = m * 9.80665
        Fmax = 20.58
        # Borde trasero (+Lx, 0): f3 = f4 = W/2, f1 = f2 = 0
        sol_rear = verificar_equilibrio(m, self.geom.lx, 0.0, Fmax, geom=self.geom)
        self.assertTrue(sol_rear.es_factible)
        self.assertAlmostEqual(sol_rear.intervalo.holgura, 0.0, places=10)
        self.assertAlmostEqual(sol_rear.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol_rear.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol_rear.f3_N, W / 2.0, places=7)
        self.assertAlmostEqual(sol_rear.f4_N, W / 2.0, places=7)

        # Borde delantero (-Lx, 0): f1 = f2 = W/2, f3 = f4 = 0
        sol_front = verificar_equilibrio(m, -self.geom.lx, 0.0, Fmax, geom=self.geom)
        self.assertTrue(sol_front.es_factible)
        self.assertAlmostEqual(sol_front.intervalo.holgura, 0.0, places=10)
        self.assertAlmostEqual(sol_front.f1_N, W / 2.0, places=7)
        self.assertAlmostEqual(sol_front.f2_N, W / 2.0, places=7)
        self.assertAlmostEqual(sol_front.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol_front.f4_N, 0.0, places=7)

        # Borde izquierdo (0, +Ly): f2 = f4 = W/2, f1 = f3 = 0
        sol_left = verificar_equilibrio(m, 0.0, self.geom.ly, Fmax, geom=self.geom)
        self.assertTrue(sol_left.es_factible)
        self.assertAlmostEqual(sol_left.intervalo.holgura, 0.0, places=10)
        self.assertAlmostEqual(sol_left.f1_N, 0.0, places=7)
        self.assertAlmostEqual(sol_left.f3_N, 0.0, places=7)
        self.assertAlmostEqual(sol_left.f2_N, W / 2.0, places=7)
        self.assertAlmostEqual(sol_left.f4_N, W / 2.0, places=7)

        # Borde derecho (0, -Ly): f1 = f3 = W/2, f2 = f4 = 0
        sol_right = verificar_equilibrio(m, 0.0, -self.geom.ly, Fmax, geom=self.geom)
        self.assertTrue(sol_right.es_factible)
        self.assertAlmostEqual(sol_right.intervalo.holgura, 0.0, places=10)
        self.assertAlmostEqual(sol_right.f2_N, 0.0, places=7)
        self.assertAlmostEqual(sol_right.f4_N, 0.0, places=7)
        self.assertAlmostEqual(sol_right.f1_N, W / 2.0, places=7)
        self.assertAlmostEqual(sol_right.f3_N, W / 2.0, places=7)

    def test_puntos_fuera_del_rectangulo(self):
        """Cualquier posición de CG con |x| > Lx o |y| > Ly debe ser estrictamente no factible para W > 0."""
        Fmax = 25.0
        puntos_exteriores = [
            (self.geom.lx + 0.010, 0.0),
            (-self.geom.lx - 0.010, 0.0),
            (0.0, self.geom.ly + 0.010),
            (0.0, -self.geom.ly - 0.010),
            (self.geom.lx + 0.020, self.geom.ly + 0.020),
        ]
        for x, y in puntos_exteriores:
            sol = verificar_equilibrio(1.0, x, y, Fmax, geom=self.geom)
            self.assertFalse(sol.es_factible, f"Punto exterior ({x}, {y}) no fue rechazado")
            self.assertLess(sol.intervalo.holgura, 0.0)


class TestAuditoriaCasosDegeneradosYLimites(unittest.TestCase):
    """Auditoría de casos degenerados: W = 0, W < 0, Fmax <= 0, y capacidad límite 4*Fmax."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)

    def test_peso_cero(self):
        """Para W = 0, el reposo con f_i = 0 es admisible con holgura nula."""
        sol = verificar_equilibrio(0.0, 0.0, 0.0, 20.58, geom=self.geom)
        self.assertTrue(sol.es_factible)
        self.assertAlmostEqual(sol.f1_N, 0.0, places=10)
        self.assertAlmostEqual(sol.f2_N, 0.0, places=10)
        self.assertAlmostEqual(sol.f3_N, 0.0, places=10)
        self.assertAlmostEqual(sol.f4_N, 0.0, places=10)
        self.assertAlmostEqual(sol.intervalo.holgura, 0.0, places=10)

    def test_peso_negativo(self):
        """Un peso negativo (m < 0) debe rechazarse como no admisible."""
        sol = verificar_equilibrio(-2.0, 0.0, 0.0, 20.58, geom=self.geom)
        self.assertFalse(sol.es_factible)

    def test_fmax_nulo_o_negativo(self):
        """Con Fmax <= 0 y W > 0, debe ser imposible equilibrar."""
        sol_f0 = verificar_equilibrio(1.0, 0.0, 0.0, 0.0, geom=self.geom)
        self.assertFalse(sol_f0.es_factible)

        sol_fneg = verificar_equilibrio(1.0, 0.0, 0.0, -10.0, geom=self.geom)
        self.assertFalse(sol_fneg.es_factible)

    def test_peso_maximo_teorico_4fmax(self):
        """
        En el límite teórico W = 4 * Fmax con CG centrado (0, 0):
        Todos los propulsores operan al 100% (f_i = Fmax), la holgura es 0, y es factible.
        Con un incremento infinitesimal W = 4 * Fmax + epsilon, pasa a no factible.
        """
        Fmax = 20.0
        g = 9.80665
        m_exact = (4.0 * Fmax) / g

        sol_lim = verificar_equilibrio(m_exact, 0.0, 0.0, Fmax, g_m_s2=g, geom=self.geom)
        self.assertTrue(sol_lim.es_factible)
        self.assertAlmostEqual(sol_lim.intervalo.holgura, 0.0, places=7)
        self.assertAlmostEqual(sol_lim.f1_N, Fmax, places=5)
        self.assertAlmostEqual(sol_lim.f2_N, Fmax, places=5)
        self.assertAlmostEqual(sol_lim.f3_N, Fmax, places=5)
        self.assertAlmostEqual(sol_lim.f4_N, Fmax, places=5)

        # Exceso infinitesimal
        m_over = m_exact + 1e-4
        sol_over = verificar_equilibrio(m_over, 0.0, 0.0, Fmax, g_m_s2=g, geom=self.geom)
        self.assertFalse(sol_over.es_factible)
        self.assertLess(sol_over.intervalo.holgura, 0.0)


class TestAuditoriaConstruccionFuerzas(unittest.TestCase):
    """Auditoría de la construcción explícita de fuerzas y optimización euclídea."""

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)

    def test_propiedad_minima_norma_pseudo_inversa(self):
        """
        Cuando f_LS está dentro del intervalo de cotas, la solución de pseudo-inversa
        proyectada minimiza estrictamente la suma de cuadrados sum(f_i^2) respecto
        a cualquier otra asignación admisible, incluyendo el centro del intervalo.
        """
        m = 5.0
        sol_pi = verificar_equilibrio(m, 0.030, 0.015, 25.0, geom=self.geom, estrategia="pseudo_inversa_proyectada")
        sol_ci = verificar_equilibrio(m, 0.030, 0.015, 25.0, geom=self.geom, estrategia="centro_intervalo")

        norm_pi = sol_pi.f1_N**2 + sol_pi.f2_N**2 + sol_pi.f3_N**2 + sol_pi.f4_N**2
        norm_ci = sol_ci.f1_N**2 + sol_ci.f2_N**2 + sol_ci.f3_N**2 + sol_ci.f4_N**2

        self.assertLessEqual(norm_pi, norm_ci + 1e-12)

    def test_concordancia_en_holgura_cero(self):
        """Cuando la holgura es cero (solución única), ambas estrategias deben dar fuerzas idénticas."""
        sol_pi = verificar_equilibrio(5.0, 0.160, 0.0, 25.0, geom=self.geom, estrategia="pseudo_inversa_proyectada")
        sol_ci = verificar_equilibrio(5.0, 0.160, 0.0, 25.0, geom=self.geom, estrategia="centro_intervalo")

        self.assertAlmostEqual(sol_pi.f1_N, sol_ci.f1_N, places=7)
        self.assertAlmostEqual(sol_pi.f2_N, sol_ci.f2_N, places=7)
        self.assertAlmostEqual(sol_pi.f3_N, sol_ci.f3_N, places=7)
        self.assertAlmostEqual(sol_pi.f4_N, sol_ci.f4_N, places=7)


class TestAuditoriaRegimenesTopologicos(unittest.TestCase):
    """
    Auditoría de los 4 regímenes topológicos del dominio admisible según eta = W / Fmax:
    - Régimen 1 (eta <= 1): Rectángulo completo físico.
    - Régimen 2 (1 < eta <= 2): Octágono que toca los bordes físicos.
    - Régimen 3 (2 < eta < 3): Octágono contraído.
    - Régimen 4 (3 <= eta < 4): Rectángulo contraído (cortes diagonales inactivos).
    """

    def setUp(self):
        self.geom = PropulsionGeometry(lx=0.160, ly=0.076)
        self.Fmax = 20.0

    def test_regimen_1_esquinas_factibles(self):
        """Para eta = 0.8 (W = 16 N < Fmax), las esquinas físicas son factibles."""
        W = 0.8 * self.Fmax
        m = W / 9.80665
        sol = verificar_equilibrio(m, self.geom.lx, self.geom.ly, self.Fmax, geom=self.geom)
        self.assertTrue(sol.es_factible)

    def test_regimen_2_borde_factible_esquina_no_factible(self):
        """Para eta = 1.6 (W = 32 N), el borde longitudinal (Lx, 0) es factible pero la esquina no."""
        W = 1.6 * self.Fmax
        m = W / 9.80665
        sol_borde = verificar_equilibrio(m, self.geom.lx, 0.0, self.Fmax, geom=self.geom)
        self.assertTrue(sol_borde.es_factible)

        sol_esq = verificar_equilibrio(m, self.geom.lx, self.geom.ly, self.Fmax, geom=self.geom)
        self.assertFalse(sol_esq.es_factible)

    def test_regimen_3_borde_fisico_infeasible_interior_factible(self):
        """
        Para eta = 2.4 (W = 48 N, análogo a C02 nominal con Fmax=20.58 N):
        El borde físico x = Lx no es factible, pero u_max = (4/eta - 1) = 0.6667 * Lx sí lo es.
        """
        W = 2.4 * self.Fmax
        m = W / 9.80665
        sol_fisico = verificar_equilibrio(m, self.geom.lx, 0.0, self.Fmax, geom=self.geom)
        self.assertFalse(sol_fisico.es_factible)

        u_max = (4.0 / 2.4 - 1.0)  # 0.666667
        sol_lim = verificar_equilibrio(m, u_max * self.geom.lx, 0.0, self.Fmax, geom=self.geom)
        self.assertTrue(sol_lim.es_factible)
        self.assertAlmostEqual(sol_lim.intervalo.holgura, 0.0, places=6)

    def test_regimen_4_rectangulo_contraido_sin_corte_diagonal(self):
        """
        Para eta = 3.5 (W = 70 N):
        La región es un RECTÁNGULO puro de semiancho u_max = (4/eta - 1) = 1/7 = 0.142857.
        El punto de esquina de ese rectángulo (u_max*Lx, u_max*Ly) es FACTIBLE.
        """
        W = 3.5 * self.Fmax
        m = W / 9.80665
        u_max = 4.0 / 3.5 - 1.0  # 1/7
        sol_corner = verificar_equilibrio(
            m, u_max * self.geom.lx, u_max * self.geom.ly, self.Fmax, geom=self.geom
        )
        self.assertTrue(sol_corner.es_factible)
        self.assertAlmostEqual(sol_corner.intervalo.holgura, 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
