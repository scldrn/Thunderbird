#!/usr/bin/env python3
"""
test_fuerza_descendente.py
--------------------------
Suite de pruebas unitarias e independientes para la verificación
de las condiciones de fuerza descendente a actitud fija.

Ejecución independiente:
  python3 -m unittest salidas/test_fuerza_descendente.py
  (o dentro del directorio salidas/: python3 -m unittest test_fuerza_descendente.py)
"""

import unittest
import math
import os
import sys

# Permitir importación directa tanto si se ejecuta desde la raíz como desde salidas/
dir_script = os.path.dirname(os.path.abspath(__file__))
if dir_script not in sys.path:
    sys.path.insert(0, dir_script)

from fuerza_descendente import (
    calcular_fuerza_descendente_total,
    calcular_fuerza_descendente_modulo,
    calcular_demanda_cg_excentrico,
    generar_tabla_escenarios,
    G0_STANDARD,
    G_APPROX,
    MASAS_KG,
    FACTORES_N,
    DX_REF_M,
    DY_REF_M
)


class TestFuerzaDescendente(unittest.TestCase):
    """Pruebas algebraicas, numéricas, dimensionales y de consistencia física."""

    def test_verificacion_algebraica_formula_general(self):
        """
        Verifica algebraicamente que Frev_total >= max(0, m * g * (n - 1)).
        Para n > 1: Frev_total = m * g * (n - 1) > 0.
        Para n = 1: Frev_total = 0.
        Para n < 1: Frev_total = 0 (la gravedad por sí sola ya supera la aceleración deseada).
        """
        g = G0_STANDARD
        for m in [1.0, 2.5, 5.0, 10.0]:
            # Caso n > 1
            for n in [1.1, 1.5, 2.0, 3.0, 5.0]:
                f_calc = calcular_fuerza_descendente_total(m, n, g)
                f_teorica = m * g * (n - 1.0)
                self.assertAlmostEqual(f_calc, f_teorica, places=9)
                self.assertGreater(f_calc, 0.0)
                self.assertGreaterEqual(f_calc, max(0.0, f_teorica))
            
            # Caso n = 1.0 (caída libre)
            f_n1 = calcular_fuerza_descendente_total(m, 1.0, g)
            self.assertEqual(f_n1, 0.0)
            
            # Caso n < 1.0 (sub-g)
            for n_sub in [0.0, 0.2, 0.5, 0.8, 0.99]:
                f_sub = calcular_fuerza_descendente_total(m, n_sub, g)
                self.assertEqual(f_sub, 0.0)
                # La demanda bruta sin max(0,...) es negativa
                demanda_bruta = m * g * (n_sub - 1.0)
                self.assertLess(demanda_bruta, 0.0)
                self.assertEqual(f_sub, max(0.0, demanda_bruta))

    def test_reparto_simetrico_cuatro_modulos(self):
        """
        Verifica que el reparto simétrico entre cuatro módulos es exactamente 1/4
        del empuje descendente total: Frev_modulo = Frev_total / 4.
        """
        for m in MASAS_KG:
            for n in FACTORES_N:
                f_tot = calcular_fuerza_descendente_total(m, n, G0_STANDARD)
                f_mod = calcular_fuerza_descendente_modulo(m, n, G0_STANDARD, num_modulos=4)
                
                # Cada módulo es un cuarto exacto
                self.assertAlmostEqual(f_mod, f_tot / 4.0, places=12)
                # La suma de los 4 módulos reconstruye la fuerza total requerida
                self.assertAlmostEqual(4.0 * f_mod, f_tot, places=12)

    def test_caso_especifico_5kg_2g(self):
        """
        Prueba mandataria del caso testigo:
        Para m = 5.0 kg y n = 2.0 (aceleración 2g):
        Frev_total = 5.0 * 9.80665 * (2 - 1) = 49.03325 N
        Frev_modulo = 49.03325 / 4 = 12.2583125 N
        Redondeado a tres cifras decimales debe ser exactamente 12.258 N.
        """
        m = 5.0
        n = 2.0
        g = G0_STANDARD  # 9.80665 m/s^2
        
        f_tot = calcular_fuerza_descendente_total(m, n, g)
        f_mod = calcular_fuerza_descendente_modulo(m, n, g, 4)
        
        self.assertAlmostEqual(f_tot, 49.03325, places=5)
        self.assertAlmostEqual(f_mod, 12.2583125, places=6)
        
        # Comprobación de valor redondeado a 3 decimales
        f_mod_3dec = round(f_mod, 3)
        self.assertEqual(f_mod_3dec, 12.258)
        self.assertTrue(abs(f_mod - 12.258) < 1e-3)

    def test_todas_las_combinaciones_prescritas(self):
        """
        Verifica exhaustivamente las 9 combinaciones requeridas:
        m in {2.0, 5.0, 10.0} kg y n in {1.2, 2.0, 5.0}.
        """
        esperados = {
            # (m, n): (F_tot_N, F_mod_N)
            (2.0, 1.2): (3.92266, 0.980665),
            (2.0, 2.0): (19.6133, 4.903325),
            (2.0, 5.0): (78.4532, 19.6133),
            (5.0, 1.2): (9.80665, 2.4516625),
            (5.0, 2.0): (49.03325, 12.2583125),
            (5.0, 5.0): (196.133, 49.03325),
            (10.0, 1.2): (19.6133, 4.903325),
            (10.0, 2.0): (98.0665, 24.516625),
            (10.0, 5.0): (392.266, 98.0665),
        }
        
        for (m, n), (exp_tot, exp_mod) in esperados.items():
            f_tot = calcular_fuerza_descendente_total(m, n, G0_STANDARD)
            f_mod = calcular_fuerza_descendente_modulo(m, n, G0_STANDARD, 4)
            
            self.assertAlmostEqual(f_tot, exp_tot, places=4, msg=f"Fallo en F_tot para m={m}, n={n}")
            self.assertAlmostEqual(f_mod, exp_mod, places=4, msg=f"Fallo en F_mod para m={m}, n={n}")

    def test_analisis_dimensional(self):
        """
        Verificación dimensional formal de Frev_total = m * g * (n - 1):
          [m] = M
          [g] = L * T^-2
          [n] = 1 (adimensional)
          [m * g * (n - 1)] = M * L * T^-2 = Newton (N)
        Y al dividir por 4 (escalar adimensional de número de actuadores):
          [Frev_modulo] = [Frev_total] / [4] = M * L * T^-2 = Newton (N)
        """
        dim_m = {"M": 1, "L": 0, "T": 0}
        dim_g = {"M": 0, "L": 1, "T": -2}
        dim_n = {"M": 0, "L": 0, "T": 0}
        dim_4 = {"M": 0, "L": 0, "T": 0}
        
        # Producto [m * g]
        dim_mg = {k: dim_m[k] + dim_g[k] for k in dim_m}
        # Producto con (n - 1)
        dim_f_tot = {k: dim_mg[k] + dim_n[k] for k in dim_m}
        # Cociente sobre 4
        dim_f_mod = {k: dim_f_tot[k] - dim_4[k] for k in dim_m}
        
        dim_fuerza_si = {"M": 1, "L": 1, "T": -2}
        self.assertEqual(dim_f_tot, dim_fuerza_si)
        self.assertEqual(dim_f_mod, dim_fuerza_si)

    def test_equilibrio_fuerzas_y_momentos(self):
        """
        Verifica el equilibrio de cuerpo rígido bajo la 2ª ley de Newton:
          Eje +Z hacia el cenit.
          F_grav_z = -m * g
          F_prop_z = -4 * Frev_mod = -Frev_total
          F_neta_z = F_grav_z + F_prop_z
          Objetivo inercial: m * a_z = -m * n * g
          Residuo: |F_neta_z - (-m * n * g)| < 1e-12 N
          Momentos en CG simétrico: Mx = 0, My = 0
        """
        dx = DX_REF_M
        dy = DY_REF_M
        for m in MASAS_KG:
            for n in FACTORES_N:
                f_mod = calcular_fuerza_descendente_modulo(m, n, G0_STANDARD, 4)
                
                # Balance de fuerzas vertical
                f_grav_z = -m * G0_STANDARD
                f_prop_z = -4.0 * f_mod
                f_neta_z = f_grav_z + f_prop_z
                objetivo_m_az = -m * n * G0_STANDARD
                
                residuo_fuerza = abs(f_neta_z - objetivo_m_az)
                self.assertLess(residuo_fuerza, 1e-12, f"Residuo de fuerza no nulo: {residuo_fuerza}")
                
                # Momentos de cabeceo y alabeo
                # Estaciones: 1 (+dx, +dy), 2 (+dx, -dy), 3 (-dx, -dy), 4 (-dx, +dy)
                # Fuerzas verticales: Fz_i = -f_mod para cada modulo
                mx = (-f_mod * dy) + (-f_mod * -dy) + (-f_mod * -dy) + (-f_mod * dy)
                my = (f_mod * dx) + (f_mod * dx) + (-f_mod * dx) + (-f_mod * dx)
                
                self.assertLess(abs(mx), 1e-12, f"Momento alabeo residual: {mx}")
                self.assertLess(abs(my), 1e-12, f"Momento cabeceo residual: {my}")

    def test_casos_limite_fisicos(self):
        """
        Prueba los casos límite de relevancia física:
        1. n = 1.0: Caída libre pura -> Frev_total = 0 N.
        2. n = 0.0: Vuelo estacionario -> Frev_total = 0 N (se requiere sustentación hacia arriba m*g).
        3. n = 0.5: Caída frenada -> Frev_total = 0 N (se requiere sustentación hacia arriba 0.5*m*g).
        4. g -> 0: Microgravedad -> Frev_total = m * a_desc.
        """
        # Caso 1: Caída libre n = 1.0
        self.assertEqual(calcular_fuerza_descendente_total(5.0, 1.0, G0_STANDARD), 0.0)
        
        # Caso 2 y 3: Sub-g
        self.assertEqual(calcular_fuerza_descendente_total(5.0, 0.0, G0_STANDARD), 0.0)
        self.assertEqual(calcular_fuerza_descendente_total(5.0, 0.5, G0_STANDARD), 0.0)
        
        # Demostración del empuje de sustentación requerido en sub-g:
        # F_grav_z + F_sust_z = -m * n * g  =>  -m*g + F_sust = -m*n*g  =>  F_sust = m*g*(1 - n)
        for n_sub in [0.0, 0.5]:
            f_sust_requerida = 5.0 * G0_STANDARD * (1.0 - n_sub)
            self.assertGreater(f_sust_requerida, 0.0)
        
        # Caso 4: Microgravedad g -> 0
        g_micro = 1e-8
        a_desc_deseada = 2.0 * G0_STANDARD  # aceleración prescrita equivalente a 2g terrestres
        n_equivalente = a_desc_deseada / g_micro
        f_micro = calcular_fuerza_descendente_total(5.0, n_equivalente, g_micro)
        f_newton_pura = 5.0 * a_desc_deseada
        self.assertAlmostEqual(f_micro, f_newton_pura, places=5)

    def test_sensibilidad_cg_excentrico(self):
        """
        Verifica que ante un desplazamiento del CG, el reparto no es uniforme (1/4)
        y la demanda sobre el módulo crítico aumenta por (1 + |xcg|/dx + |ycg|/dy).
        """
        res_centrado = calcular_demanda_cg_excentrico(5.0, 2.0, x_cg=0.0, y_cg=0.0)
        self.assertEqual(res_centrado["factor_amplificacion"], 1.0)
        self.assertAlmostEqual(res_centrado["r_critico_N"], res_centrado["r_simetrico_N"], places=9)
        
        # Con x_cg = 0.040 m (25% de dx = 0.160 m)
        res_excentrico = calcular_demanda_cg_excentrico(5.0, 2.0, x_cg=0.040, y_cg=0.0)
        self.assertEqual(res_excentrico["factor_amplificacion"], 1.25)
        self.assertAlmostEqual(res_excentrico["r_critico_N"], 1.25 * res_excentrico["r_simetrico_N"], places=9)
        self.assertGreater(res_excentrico["r_critico_N"], res_excentrico["r_simetrico_N"])

    def test_sin_rutas_absolutas_en_entregables(self):
        """
        Verifica que en los archivos entregables de salidas/ no existan rutas absolutas temporales.
        """
        archivos_a_inspeccionar = [
            "fuerza_descendente.py",
            "tabla_fuerza_descendente.csv",
            "resultados_resumen.json"
        ]
        # Construir prefijos prohibidos sin escribir la cadena literal continua
        prefijo_tmp = "/" + "tmp"
        prefijo_priv = "/" + "private" + "/" + "tmp"
        
        for nom in archivos_a_inspeccionar:
            ruta = os.path.join(dir_script, nom)
            if os.path.exists(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    self.assertNotIn(
                        prefijo_priv,
                        contenido,
                        f"Se detectó la ruta temporal absoluta prohibida '{prefijo_priv}' en {nom}"
                    )
                    self.assertNotIn(
                        prefijo_tmp,
                        contenido,
                        f"Se detectó la ruta temporal absoluta prohibida '{prefijo_tmp}' en {nom}"
                    )

    def test_manejo_errores_entradas_invalidas(self):
        """Verifica que entradas físicamente inválidas lancen excepciones apropiadas."""
        with self.assertRaises(ValueError):
            calcular_fuerza_descendente_total(m=-5.0, n=2.0)
        with self.assertRaises(ValueError):
            calcular_fuerza_descendente_total(m=0.0, n=2.0)
        with self.assertRaises(ValueError):
            calcular_fuerza_descendente_total(m=5.0, n=2.0, g=-9.8)
        with self.assertRaises(ValueError):
            calcular_fuerza_descendente_modulo(m=5.0, n=2.0, num_modulos=0)


if __name__ == "__main__":
    unittest.main()
