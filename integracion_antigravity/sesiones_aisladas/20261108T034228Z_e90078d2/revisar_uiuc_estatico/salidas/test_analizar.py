#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_analizar.py - Pruebas Unitarias y de Integración para el Análisis Aerodinámico

Verifica:
1. Exactitud de las fórmulas de empuje, potencia, Mach de punta, Reynolds y Figura de Mérito.
2. Equivalencia exacta entre la formulación adimensional y dimensional de la Figura de Mérito.
3. Carga y consistencia de los archivos de ensayo estático y geometría UIUC.
4. Monotonía, acotación física y rangos de las variables calculadas.
5. Prohibición estricta de extrapolación fuera del rango de ensayo (2,950 a 19,923.333 RPM).
6. Integridad del archivo generado salidas/puntos.csv.
"""

import math
import os
import sys
import unittest

# Asegurar importación del módulo analizar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import analizar


class TestFormulasAerodinamicas(unittest.TestCase):
    """Pruebas unitarias de las relaciones aerodinámicas fundamentales."""

    def setUp(self):
        self.rho = 1.225
        self.a_sound = 340.3
        self.nu = 1.46e-5
        self.d = 0.08128
        self.c_over_r_075 = 0.1799

    def test_calcular_n(self):
        """Verifica la conversión de RPM a revoluciones por segundo (rev/s)."""
        self.assertAlmostEqual(analizar.calcular_n(0.0), 0.0)
        self.assertAlmostEqual(analizar.calcular_n(60.0), 1.0)
        self.assertAlmostEqual(analizar.calcular_n(3000.0), 50.0)
        self.assertAlmostEqual(analizar.calcular_n(2950.0), 49.1666667, places=5)
        with self.assertRaises(ValueError):
            analizar.calcular_n(-100.0)

    def test_calcular_empuje(self):
        """Verifica T = CT * rho * n^2 * D^4 y leyes de semejanza."""
        ct = 0.103654
        n = 2950.0 / 60.0
        t_esperado = ct * self.rho * (n ** 2) * (self.d ** 4)
        t_calculado = analizar.calcular_empuje(ct, self.rho, n, self.d)
        self.assertAlmostEqual(t_calculado, t_esperado, places=7)

        # Ley de semejanza: si n se duplica, T se cuadruplica (n^2)
        t_doble_n = analizar.calcular_empuje(ct, self.rho, 2.0 * n, self.d)
        self.assertAlmostEqual(t_doble_n, 4.0 * t_calculado, places=7)

        # Ley de semejanza: si D se duplica, T escala con 2^4 = 16
        t_doble_d = analizar.calcular_empuje(ct, self.rho, n, 2.0 * self.d)
        self.assertAlmostEqual(t_doble_d, 16.0 * t_calculado, places=7)

        # Validaciones de entrada
        with self.assertRaises(ValueError):
            analizar.calcular_empuje(ct, -1.0, n, self.d)
        with self.assertRaises(ValueError):
            analizar.calcular_empuje(ct, self.rho, -10.0, self.d)
        with self.assertRaises(ValueError):
            analizar.calcular_empuje(ct, self.rho, n, 0.0)

    def test_calcular_potencia(self):
        """Verifica P = CP * rho * n^3 * D^5 y leyes de semejanza."""
        cp = 0.051360
        n = 2950.0 / 60.0
        p_esperado = cp * self.rho * (n ** 3) * (self.d ** 5)
        p_calculado = analizar.calcular_potencia(cp, self.rho, n, self.d)
        self.assertAlmostEqual(p_calculado, p_esperado, places=7)

        # Ley de semejanza: si n se duplica, P escala con 2^3 = 8
        p_doble_n = analizar.calcular_potencia(cp, self.rho, 2.0 * n, self.d)
        self.assertAlmostEqual(p_doble_n, 8.0 * p_calculado, places=7)

        # Ley de semejanza: si D se duplica, P escala con 2^5 = 32
        p_doble_d = analizar.calcular_potencia(cp, self.rho, n, 2.0 * self.d)
        self.assertAlmostEqual(p_doble_d, 32.0 * p_calculado, places=7)

        # Validaciones de entrada
        with self.assertRaises(ValueError):
            analizar.calcular_potencia(cp, 0.0, n, self.d)
        with self.assertRaises(ValueError):
            analizar.calcular_potencia(cp, self.rho, -5.0, self.d)
        with self.assertRaises(ValueError):
            analizar.calcular_potencia(cp, self.rho, n, -0.05)

    def test_calcular_mach_punta(self):
        """Verifica M_tip = (pi * n * D) / a."""
        n = 10000.0 / 60.0
        v_tip = math.pi * n * self.d
        m_esperado = v_tip / self.a_sound
        m_calculado = analizar.calcular_mach_punta(n, self.d, self.a_sound)
        self.assertAlmostEqual(m_calculado, m_esperado, places=7)

        # n = 0 => M = 0
        self.assertEqual(analizar.calcular_mach_punta(0.0, self.d, self.a_sound), 0.0)

        # Validaciones
        with self.assertRaises(ValueError):
            analizar.calcular_mach_punta(n, self.d, 0.0)
        with self.assertRaises(ValueError):
            analizar.calcular_mach_punta(n, -self.d, self.a_sound)

    def test_calcular_reynolds_075(self):
        """Verifica Re_0.75R = (0.75 * pi * n * D * c_075) / nu."""
        n = 10000.0 / 60.0
        r = self.d / 2.0
        c_075 = self.c_over_r_075 * r
        v_075 = 0.75 * math.pi * n * self.d
        re_esperado = (v_075 * c_075) / self.nu
        re_calculado = analizar.calcular_reynolds_075(n, self.d, self.c_over_r_075, self.nu)
        self.assertAlmostEqual(re_calculado, re_esperado, places=5)

        # Linealidad con n
        re_doble_n = analizar.calcular_reynolds_075(2.0 * n, self.d, self.c_over_r_075, self.nu)
        self.assertAlmostEqual(re_doble_n, 2.0 * re_calculado, places=5)

        # Escalado cuadrático con D (V_075 propto D y c_075 propto D => Re propto D^2)
        re_doble_d = analizar.calcular_reynolds_075(n, 2.0 * self.d, self.c_over_r_075, self.nu)
        self.assertAlmostEqual(re_doble_d, 4.0 * re_calculado, places=5)

        # Validaciones
        with self.assertRaises(ValueError):
            analizar.calcular_reynolds_075(n, self.d, self.c_over_r_075, 0.0)
        with self.assertRaises(ValueError):
            analizar.calcular_reynolds_075(n, self.d, -0.1, self.nu)

    def test_calcular_figura_merito(self):
        """Verifica FM = sqrt(2/pi) * CT^(3/2) / CP."""
        ct = 0.103654
        cp = 0.051360
        fm_esperado = math.sqrt(2.0 / math.pi) * (ct ** 1.5) / cp
        fm_calculado = analizar.calcular_figura_merito(ct, cp)
        self.assertAlmostEqual(fm_calculado, fm_esperado, places=7)

        # Validaciones
        with self.assertRaises(ValueError):
            analizar.calcular_figura_merito(-0.1, cp)
        with self.assertRaises(ValueError):
            analizar.calcular_figura_merito(ct, 0.0)

    def test_equivalencia_figura_merito_dimensional(self):
        """Demuestra que FM adimensional es idéntica a P_ideal / P dimensional."""
        puntos_prueba = [
            (2950.0, 0.103654, 0.051360),
            (10056.667, 0.112185, 0.053441),
            (19923.333, 0.125828, 0.059879),
        ]
        for rpm, ct, cp in puntos_prueba:
            n = analizar.calcular_n(rpm)
            t = analizar.calcular_empuje(ct, self.rho, n, self.d)
            p = analizar.calcular_potencia(cp, self.rho, n, self.d)

            fm_adimensional = analizar.calcular_figura_merito(ct, cp)
            fm_dimensional = analizar.calcular_figura_merito_dimensional(t, p, self.rho, self.d)

            self.assertAlmostEqual(fm_adimensional, fm_dimensional, delta=1e-12)


class TestCargaDatos(unittest.TestCase):
    """Verifica la lectura de datos de entrada desde el directorio de referencia."""

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ruta_estaticos = os.path.join(
            self.base_dir, "entradas", "investigacion-aeronautica", "fuentes", "uiuc_propdb", "mi_3.2x2.2_static_0519rd.txt"
        )
        self.ruta_geom = os.path.join(
            self.base_dir, "entradas", "investigacion-aeronautica", "fuentes", "uiuc_propdb", "mi_3.2x2.2_geom.txt"
        )

    def test_cargar_datos_estaticos(self):
        """Verifica que se leen correctamente los 18 registros de ensayo estático."""
        puntos = analizar.cargar_datos_estaticos(self.ruta_estaticos)
        self.assertEqual(len(puntos), 18)

        # Primer punto
        rpm0, ct0, cp0 = puntos[0]
        self.assertAlmostEqual(rpm0, 2950.000, places=3)
        self.assertAlmostEqual(ct0, 0.103654, places=6)
        self.assertAlmostEqual(cp0, 0.051360, places=6)

        # Último punto
        rpm_fin, ct_fin, cp_fin = puntos[-1]
        self.assertAlmostEqual(rpm_fin, 19923.333, places=3)
        self.assertAlmostEqual(ct_fin, 0.125828, places=6)
        self.assertAlmostEqual(cp_fin, 0.059879, places=6)

    def test_cargar_geometria(self):
        """Verifica que c/R a r/R = 0.75 sea exactamente 0.1799."""
        c_over_r = analizar.cargar_c_over_r_075(self.ruta_geom)
        self.assertAlmostEqual(c_over_r, 0.1799, places=4)

    def test_archivo_inexistente(self):
        """Verifica que se lance FileNotFoundError si falta un archivo."""
        with self.assertRaises(FileNotFoundError):
            analizar.cargar_datos_estaticos("ruta/inexistente/datos.txt")
        with self.assertRaises(FileNotFoundError):
            analizar.cargar_c_over_r_075("ruta/inexistente/geom.txt")


class TestProcesamientoYRestricciones(unittest.TestCase):
    """Verifica las restricciones de extrapolación, monotonía y rangos físicos."""

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ruta_estaticos = os.path.join(
            self.base_dir, "entradas", "investigacion-aeronautica", "fuentes", "uiuc_propdb", "mi_3.2x2.2_static_0519rd.txt"
        )
        self.ruta_geom = os.path.join(
            self.base_dir, "entradas", "investigacion-aeronautica", "fuentes", "uiuc_propdb", "mi_3.2x2.2_geom.txt"
        )
        self.puntos_estaticos = analizar.cargar_datos_estaticos(self.ruta_estaticos)
        self.c_over_r = analizar.cargar_c_over_r_075(self.ruta_geom)
        self.resultados = analizar.procesar_datos(
            self.puntos_estaticos, c_over_r_075=self.c_over_r, permitir_extrapolacion=False
        )

    def test_numero_puntos(self):
        """El conjunto de resultados debe contener exactamente 18 puntos."""
        self.assertEqual(len(self.resultados), 18)

    def test_monotonia_rpm_empuje_potencia(self):
        """RPM, Empuje y Potencia deben ser monótonamente crecientes."""
        for i in range(len(self.resultados) - 1):
            curr_pt = self.resultados[i]
            next_pt = self.resultados[i + 1]

            # RPM creciente
            self.assertGreater(next_pt["rpm"], curr_pt["rpm"])
            # Frecuencia n creciente
            self.assertGreater(next_pt["n_rev_s"], curr_pt["n_rev_s"])
            # Empuje creciente
            self.assertGreater(next_pt["empuje_N"], curr_pt["empuje_N"])
            # Potencia de eje creciente
            self.assertGreater(next_pt["potencia_eje_W"], curr_pt["potencia_eje_W"])
            # Mach de punta creciente
            self.assertGreater(next_pt["mach_punta"], curr_pt["mach_punta"])
            # Reynolds creciente
            self.assertGreater(next_pt["re_075r"], curr_pt["re_075r"])

    def test_acotacion_fisica(self):
        """Verifica rangos físicos esperados."""
        for r in self.resultados:
            # Empuje positivo y del orden de micro-hélices (0.01 N a 0.8 N)
            self.assertGreater(r["empuje_N"], 0.01)
            self.assertLess(r["empuje_N"], 1.0)

            # Potencia positiva (0.02 W a 10 W)
            self.assertGreater(r["potencia_eje_W"], 0.02)
            self.assertLess(r["potencia_eje_W"], 12.0)

            # Mach de punta subsónico incompresible (< 0.3)
            self.assertGreater(r["mach_punta"], 0.03)
            self.assertLess(r["mach_punta"], 0.30)

            # Reynolds en régimen de micro-hélice (4,000 < Re < 35,000)
            self.assertGreater(r["re_075r"], 4000)
            self.assertLess(r["re_075r"], 35000)

            # Figura de mérito física en vuelo estacionario (0.50 < FM < 0.65)
            self.assertGreater(r["figura_merito"], 0.50)
            self.assertLess(r["figura_merito"], 0.65)

    def test_no_monotonia_estricta_ct_cp(self):
        """
        Verifica que los coeficientes experimentales CT y CP NO son estrictamente
        crecientes punto a punto, debido a efectos viscosos de capa límite y burbujas
        de separación laminar a bajo Reynolds, aun cuando el empuje T sí es monótono.
        """
        ct_vals = [r["ct"] for r in self.resultados]
        cp_vals = [r["cp"] for r in self.resultados]

        decrementos_ct = [ct_vals[i + 1] < ct_vals[i] for i in range(len(ct_vals) - 1)]
        self.assertTrue(any(decrementos_ct), "CT experimental debería presentar oscilaciones locales.")

        decrementos_cp = [cp_vals[i + 1] < cp_vals[i] for i in range(len(cp_vals) - 1)]
        self.assertTrue(any(decrementos_cp), "CP experimental debería presentar oscilaciones locales.")

        # A pesar de oscilaciones en CT, T = CT * rho * n^2 * D^4 crece estrictamente
        empuje_vals = [r["empuje_N"] for r in self.resultados]
        self.assertTrue(all(empuje_vals[i + 1] > empuje_vals[i] for i in range(len(empuje_vals) - 1)))

    def test_prohibicion_extrapolacion_rpm(self):
        """Verifica que el código bloquee la extrapolación si RPM está fuera de rango."""
        datos_baja_rpm = [(2000.0, 0.10, 0.05)]
        with self.assertRaises(ValueError):
            analizar.procesar_datos(datos_baja_rpm, permitir_extrapolacion=False)

        datos_alta_rpm = [(25000.0, 0.12, 0.06)]
        with self.assertRaises(ValueError):
            analizar.procesar_datos(datos_alta_rpm, permitir_extrapolacion=False)


class TestSalidaCSV(unittest.TestCase):
    """Verifica que el archivo salidas/puntos.csv cumpla con la estructura requerida."""

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ruta_csv = os.path.join(self.base_dir, "salidas", "puntos.csv")
        # Asegurar independencia del test si puntos.csv no ha sido generado aún
        if not os.path.isfile(self.ruta_csv):
            analizar.main()

    def test_existencia_y_contenido_csv(self):
        """El archivo salidas/puntos.csv debe existir, tener cabecera y 18 registros numéricos."""
        self.assertTrue(os.path.isfile(self.ruta_csv), f"No existe {self.ruta_csv}")

        columnas_esperadas = [
            "rpm",
            "n_rev_s",
            "ct",
            "cp",
            "empuje_N",
            "potencia_eje_W",
            "mach_punta",
            "re_075r",
            "figura_merito",
        ]

        with open(self.ruta_csv, "r", encoding="utf-8") as f:
            lineas = [l.strip() for l in f if l.strip()]

        # 1 fila cabecera + 18 filas datos = 19 filas
        self.assertEqual(len(lineas), 19)

        cabecera = lineas[0].split(",")
        self.assertEqual(cabecera, columnas_esperadas)

        for num_linea, fila in enumerate(lineas[1:], start=2):
            partes = fila.split(",")
            self.assertEqual(
                len(partes), len(columnas_esperadas), f"Línea {num_linea} tiene columnas incompletas."
            )
            # Todos los valores deben ser parseables a float y mayores a 0
            for col_nombre, val_str in zip(columnas_esperadas, partes):
                val = float(val_str)
                self.assertGreater(val, 0.0, f"Valor <= 0 en columna {col_nombre}, línea {num_linea}")


if __name__ == "__main__":
    unittest.main()
