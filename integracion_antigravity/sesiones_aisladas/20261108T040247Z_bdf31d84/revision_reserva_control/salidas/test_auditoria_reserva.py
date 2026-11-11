#!/usr/bin/env python3
"""
test_auditoria_reserva.py
=========================
Suite de pruebas unitarias automatizadas para la auditoría de reserva estática de control.

Verifica:
1. Equilibrio vertical estricto (sum(Fz) = W) y momento de cabeceo (sum(My) = 0).
2. Comprobación aritmética exacta del caso solicitado:
   m = 5.0 kg, xcg = 0.096 m, xfan = ±0.160 m, Fmax = 20.58 N, reserva 10%.
   Fuerza requerida módulo trasero = 19.6133 N > Límite utilizable 18.5220 N.
   Inexistencia de equilibrio vertical en dicho modelo.
3. Reproducción exacta de los límites analíticos de referencia de INFORME-VERTICAL.md.
4. Escalado lineal estricto de la fuerza utilizable Fz_max(r) = (1 - r) * Fz_max(0).
5. Cálculo riguroso de umbrales críticos de CG (xcg_crit).
6. Demostración analítica de la asimetría y colapso de momento de cabeceo (dMy+).
7. Evaluación crítica y rechazo justificado de columnas desacopladas (ax, dMy, dMx).
8. Integridad y coherencia dimensional de los archivos CSV generados en salidas/.
"""

import unittest
import math
import os
import sys
import csv

# Asegurar path local
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auditar_reserva_control import (
    verificar_caso_aritmetico_especifico,
    auditar_escenario,
    ejecutar_auditoria,
    MASA_KG,
    G_MS2,
    PESO_N,
    L_M,
    B_M,
    XCG_VALORES_M,
    FNOM_VALORES_N,
    RESERVAS_FRAC,
)


class TestAuditoriaReserva(unittest.TestCase):

    def test_01_equilibrio_fuerzas_verticales_hover(self):
        """Verifica que la suma de fuerzas verticales iguale exactamente al peso en equilibrio estático."""
        for fnom in FNOM_VALORES_N:
            for r in RESERVAS_FRAC:
                for xcg in XCG_VALORES_M:
                    res = auditar_escenario(fnom, r, xcg)
                    # Suma de fuerzas verticales de los 4 módulos: 2 traseros + 2 delanteros
                    fz_tot = 2.0 * res["fz_rear_hover_N"] + 2.0 * res["fz_front_hover_N"]
                    self.assertAlmostEqual(
                        fz_tot,
                        PESO_N,
                        places=3,
                        msg=f"Discrepancia en equilibrio vertical para Fnom={fnom}, r={r}, xcg={xcg}"
                    )

    def test_02_equilibrio_momento_cabeceo_hover(self):
        """Verifica que el momento de cabeceo generado coincida exactamente con xcg * W."""
        for fnom in FNOM_VALORES_N:
            for r in RESERVAS_FRAC:
                for xcg in XCG_VALORES_M:
                    res = auditar_escenario(fnom, r, xcg)
                    # Momento respecto a x=0: 2*L*fz_rear - 2*L*fz_front
                    my_generado = 2.0 * L_M * res["fz_rear_hover_N"] - 2.0 * L_M * res["fz_front_hover_N"]
                    my_peso = xcg * PESO_N
                    self.assertAlmostEqual(
                        my_generado,
                        my_peso,
                        places=3,
                        msg=f"Discrepancia en momento de cabeceo para Fnom={fnom}, r={r}, xcg={xcg}"
                    )

    def test_03_caso_critico_especifico_aritmetica_y_deficit(self):
        """
        Comprobación aritmética estricta del caso requerido:
        m = 5 kg, xcg = 0.096 m, xfan = ±0.16 m, Fmax = 20.58 N, reserva = 10%.
        Requerimiento: fz_rear = 19.6133 N > 18.522 N -> No hay equilibrio vertical.
        """
        caso = verificar_caso_aritmetico_especifico()
        
        # 1. Parámetros básicos
        self.assertEqual(caso["m_kg"], 5.0)
        self.assertAlmostEqual(caso["W_N"], 49.03325, places=5)
        self.assertEqual(caso["xcg_m"], 0.096)
        self.assertEqual(caso["L_m"], 0.160)
        self.assertEqual(caso["ratio_xcg_L"], 0.600)
        
        # 2. Límite utilizable bajo reserva 10%
        # Fusable = 20.58 * 0.90 = 18.5220 N
        self.assertAlmostEqual(caso["Futilizable_N"], 18.5220, places=4)
        
        # 3. Fuerza requerida en módulo trasero
        # fz_rear = (W/4) * (1 + 0.096/0.160) = 12.2583125 * 1.6 = 19.6133 N
        self.assertAlmostEqual(caso["fz_rear_necesaria_N"], 19.6133, places=4)
        
        # 4. Fuerza requerida en módulo delantero
        # fz_front = (W/4) * (1 - 0.096/0.160) = 12.2583125 * 0.4 = 4.9033 N
        self.assertAlmostEqual(caso["fz_front_necesaria_N"], 4.9033, places=4)
        
        # 5. Déficit numérico y comprobación de superación del límite
        # 19.6133 N > 18.5220 N
        self.assertGreater(caso["fz_rear_necesaria_N"], caso["Futilizable_N"])
        self.assertAlmostEqual(caso["deficit_N"], -1.0913, places=4)
        
        # 6. Conclusión de inexistencia de equilibrio vertical
        self.assertFalse(caso["hay_equilibrio_vertical"])

    def test_04_reproduccion_referencia_informe_vertical(self):
        """
        Verifica la reproducción exacta de los límites de referencia en INFORME-VERTICAL.md
        para Fnom = 20.58 N, reserva 0% (líneas 42-45).
        """
        esperados = {
            0.000: {"Fz_max": 82.32, "az_g": 0.679},
            0.040: {"Fz_max": 65.86, "az_g": 0.343},
            0.080: {"Fz_max": 54.88, "az_g": 0.119},
            0.096: {"Fz_max": 51.45, "az_g": 0.049},
        }
        for xcg, esp in esperados.items():
            res = auditar_escenario(20.58, 0.0, xcg)
            self.assertAlmostEqual(res["Fz_max_trim_N"], esp["Fz_max"], delta=0.01)
            self.assertAlmostEqual(res["az_max_trim_g"], esp["az_g"], delta=0.001)

    def test_05_escalado_lineal_fuerza_utilizable(self):
        """Verifica que Fz_max_trim escale linealmente con (1 - r)."""
        for fnom in FNOM_VALORES_N:
            for xcg in XCG_VALORES_M:
                base = auditar_escenario(fnom, 0.0, xcg)["Fz_max_trim_N"]
                for r in [0.10, 0.20]:
                    caso_r = auditar_escenario(fnom, r, xcg)["Fz_max_trim_N"]
                    esperado = base * (1.0 - r)
                    self.assertAlmostEqual(
                        caso_r,
                        esperado,
                        delta=1e-3,
                        msg=f"Fallo escalado lineal para Fnom={fnom}, xcg={xcg}, r={r}"
                    )

    def test_06_umbral_critico_cg(self):
        """Verifica la posición analítica crítica de CG (xcg_crit) para sustentación."""
        # Para Fnom = 20.58 N, r = 10%:
        # Fusable = 18.522 N -> xcg_crit = 0.160 * (4*18.522 / 49.03325 - 1) = 0.0818 m
        res_08 = auditar_escenario(20.58, 0.10, 0.080)
        res_096 = auditar_escenario(20.58, 0.10, 0.096)
        self.assertTrue(res_08["factible_estacionario"])
        self.assertFalse(res_096["factible_estacionario"])
        self.assertAlmostEqual(res_08["xcg_crit_m"], 0.0818, places=3)

        # Para Fnom = 20.58 N, r = 20%:
        # Fusable = 16.464 N -> xcg_crit = 0.160 * (4*16.464 / 49.03325 - 1) = 0.0549 m
        res_04 = auditar_escenario(20.58, 0.20, 0.040)
        res_08_20 = auditar_escenario(20.58, 0.20, 0.080)
        self.assertTrue(res_04["factible_estacionario"])
        self.assertFalse(res_08_20["factible_estacionario"])
        self.assertAlmostEqual(res_04["xcg_crit_m"], 0.0549, places=3)

    def test_07_demostracion_colapso_cabeceo_desacoplado(self):
        """
        Demuestra la extrema no linealidad entre reserva escalar y margen de momento de cabeceo:
        Para Fnom = 20.58 N, xcg = 0.080 m, un 10% de reserva escalar reduce dMy+ en más del 90%.
        """
        base = auditar_escenario(20.58, 0.0, 0.080)
        res10 = auditar_escenario(20.58, 0.10, 0.080)
        
        caida_pct = (1.0 - res10["dMy_encabritar_desacoplado_Nm"] / base["dMy_encabritar_desacoplado_Nm"]) * 100.0
        self.assertGreater(
            caida_pct,
            90.0,
            msg=f"La caída en autoridad de cabeceo ({caida_pct:.1f}%) debe superar el 90%"
        )

    def test_08_auditoria_critica_rechazo_columnas_desacopladas(self):
        """Verifica que las columnas no sustentadas (ax, dMy, dMx) queden explícitamente dictaminadas como rechazadas."""
        for fnom in FNOM_VALORES_N:
            for r in RESERVAS_FRAC:
                for xcg in XCG_VALORES_M:
                    res = auditar_escenario(fnom, r, xcg)
                    self.assertEqual(
                        res["dictamen_horizontal_y_momentos"],
                        "NO SUSTENTADO PARA VUELO (RECHAZADO)"
                    )

    def test_09_integridad_csv_auditados(self):
        """Verifica la existencia y formato de los archivos CSV generados en salidas/."""
        directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_csv = os.path.join(directorio, "sensibilidad_reserva_auditada.csv")
        ruta_resumen = os.path.join(directorio, "resumen_auditoria_estatica.csv")
        
        self.assertTrue(os.path.isfile(ruta_csv), "El archivo CSV auditado no existe")
        self.assertTrue(os.path.isfile(ruta_resumen), "El archivo CSV de resumen no existe")
        
        with open(ruta_csv, mode="r", encoding="utf-8") as f:
            filas = list(csv.reader(f))
            self.assertEqual(len(filas), 25, "El CSV auditado debe tener 25 filas (1 encabezado + 24 casos)")

        with open(ruta_resumen, mode="r", encoding="utf-8") as f:
            filas_res = list(csv.reader(f))
            self.assertEqual(len(filas_res), 25, "El CSV resumen debe tener 25 filas")


if __name__ == "__main__":
    unittest.main()
