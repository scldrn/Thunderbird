#!/usr/bin/env python3
"""
test_sensibilidad.py
====================
Conjunto de pruebas automatizadas para verificar el equilibrio estático,
los límites analíticos y la consistencia física de la sensibilidad de reserva.

Ejecución:
    python3 salidas/test_sensibilidad.py
"""

import unittest
import math
import os
import sys
import csv

# Asegurar que el directorio de este script esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calcular_sensibilidad_reserva import (
    calcular_caso,
    ejecutar_barrido,
    MASA_KG,
    G_MS2,
    PESO_N,
    L_M,
    B_M,
    XCG_VALORES_M,
    FNOM_VALORES_N,
    RESERVAS_FRAC,
)


class TestSensibilidadReserva(unittest.TestCase):

    def test_01_equilibrio_fuerzas_verticales_hover(self):
        """Verifica que la suma de fuerzas en hover sea exactamente igual al peso (W = mg)."""
        for fnom in FNOM_VALORES_N:
            for r in RESERVAS_FRAC:
                for xcg in XCG_VALORES_M:
                    res = calcular_caso(fnom, r, xcg)
                    # Suma de fuerzas de 4 módulos (2 traseros + 2 delanteros)
                    f_total = 2.0 * res["fz_rear_hover_N"] + 2.0 * res["fz_front_hover_N"]
                    self.assertAlmostEqual(
                        f_total,
                        PESO_N,
                        places=3,
                        msg=f"Fallo de equilibrio vertical para Fnom={fnom}, r={r}, xcg={xcg}"
                    )

    def test_02_equilibrio_momento_cabeceo_hover(self):
        """Verifica que el momento de cabeceo respecto al origen coincida con xcg * W."""
        for fnom in FNOM_VALORES_N:
            for r in RESERVAS_FRAC:
                for xcg in XCG_VALORES_M:
                    res = calcular_caso(fnom, r, xcg)
                    # Momento generado respecto a x=0: 2*L*fz_rear - 2*L*fz_front
                    momento_origen = 2.0 * L_M * res["fz_rear_hover_N"] - 2.0 * L_M * res["fz_front_hover_N"]
                    momento_peso = xcg * PESO_N
                    self.assertAlmostEqual(
                        momento_origen,
                        momento_peso,
                        places=3,
                        msg=f"Fallo de equilibrio de cabeceo para Fnom={fnom}, r={r}, xcg={xcg}"
                    )

    def test_03_reproduccion_referencia_informe_vertical(self):
        """
        Contrasta los valores de Fz_max y az_max calculados con la tabla del
        INFORME-VERTICAL.md (Fnom=20.58 N, reserva=0%, líneas 42-45).
        """
        esperados = {
            0.000: {"Fz_max": 82.32, "az_g": 0.679},
            0.040: {"Fz_max": 65.86, "az_g": 0.343},
            0.080: {"Fz_max": 54.88, "az_g": 0.119},
            0.096: {"Fz_max": 51.45, "az_g": 0.049},
        }
        for xcg, esp in esperados.items():
            res = calcular_caso(20.58, 0.0, xcg)
            self.assertAlmostEqual(res["Fz_max_analitico_N"], esp["Fz_max"], delta=0.01)
            self.assertAlmostEqual(res["az_max_g"], esp["az_g"], delta=0.001)

    def test_04_escalado_lineal_fuerza_utilizable(self):
        """Verifica que Fz_max escale exactamente de forma lineal con (1 - r)."""
        for fnom in FNOM_VALORES_N:
            for xcg in XCG_VALORES_M:
                base = calcular_caso(fnom, 0.0, xcg)["Fz_max_analitico_N"]
                for r in [0.10, 0.20]:
                    caso_r = calcular_caso(fnom, r, xcg)["Fz_max_analitico_N"]
                    esperado = base * (1.0 - r)
                    self.assertAlmostEqual(
                        caso_r,
                        esperado,
                        delta=1e-3,
                        msg=f"Fallo escalado lineal para Fnom={fnom}, xcg={xcg}, r={r}"
                    )

    def test_05_frontera_factibilidad_xcg_critico(self):
        """
        Verifica el umbral analítico exacto de xcg crítico:
        xcg_crit = L * (4*F_usable / W - 1)
        """
        # Para Fnom=20.58 N y reserva=10%:
        # F_usable = 18.522 N -> 4*18.522 = 74.088 N
        # xcg_crit = 0.160 * (74.088 / 49.03325 - 1) = 0.160 * (1.51097 - 1) = 0.08175 m
        res_08 = calcular_caso(20.58, 0.10, 0.080)
        res_096 = calcular_caso(20.58, 0.10, 0.096)
        self.assertTrue(res_08["factible_estacionario"])
        self.assertFalse(res_096["factible_estacionario"])
        self.assertAlmostEqual(res_08["xcg_crit_hover_m"], 0.0818, places=3)

        # Para Fnom=20.58 N y reserva=20%:
        # F_usable = 16.464 N -> 4*16.464 = 65.856 N
        # xcg_crit = 0.160 * (65.856 / 49.03325 - 1) = 0.160 * (1.34308 - 1) = 0.05489 m
        res_04 = calcular_caso(20.58, 0.20, 0.040)
        res_08_20 = calcular_caso(20.58, 0.20, 0.080)
        self.assertTrue(res_04["factible_estacionario"])
        self.assertFalse(res_08_20["factible_estacionario"])
        self.assertAlmostEqual(res_04["xcg_crit_hover_m"], 0.0549, places=3)

    def test_06_simetria_y_asimetria_de_momentos(self):
        """
        Verifica que en xcg=0 las autoridades de cabeceo a picar y encabritar sean simétricas,
        y que para xcg > 0 la autoridad a encabritar sea estrictamente menor que a picar.
        """
        for fnom in FNOM_VALORES_N:
            for r in RESERVAS_FRAC:
                res_sim = calcular_caso(fnom, r, 0.0)
                self.assertAlmostEqual(
                    res_sim["delta_My_encabritar_Nm"],
                    res_sim["delta_My_picar_Nm"],
                    places=3
                )
                
                for xcg in [0.040, 0.080]:
                    res_asym = calcular_caso(fnom, r, xcg)
                    if res_asym["factible_estacionario"]:
                        self.assertLess(
                            res_asym["delta_My_encabritar_Nm"],
                            res_asym["delta_My_picar_Nm"],
                            msg=f"dMy+ debe ser menor que dMy- para xcg={xcg}"
                        )

    def test_07_no_equivalencia_reserva_fuerza_con_margen_cabeceo(self):
        """
        Demuestra numéricamente que reservar 10% de fuerza escalar NO equivale
        a conservar 10% de margen de cabeceo:
        Para Fnom=20.58 N, xcg=0.08 m, la reserva del 10% causa un colapso >90% en dMy+.
        """
        caso_base = calcular_caso(20.58, 0.0, 0.080)
        caso_res10 = calcular_caso(20.58, 0.10, 0.080)
        
        caida_my_pct = (1.0 - caso_res10["delta_My_encabritar_Nm"] / caso_base["delta_My_encabritar_Nm"]) * 100.0
        # Debe caer más del 90%:
        self.assertGreater(
            caida_my_pct,
            90.0,
            msg=f"La caída en dMy+ ({caida_my_pct:.1f}%) debe superar con creces el 10% nominal"
        )

    def test_08_integridad_csv_generados(self):
        """Verifica existencia, encabezados y número de filas de los CSVs generados."""
        directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_csv = os.path.join(directorio, "sensibilidad_reserva_control.csv")
        ruta_resumen = os.path.join(directorio, "resumen_sensibilidad_reserva.csv")
        
        self.assertTrue(os.path.isfile(ruta_csv), "El archivo CSV completo no existe")
        self.assertTrue(os.path.isfile(ruta_resumen), "El archivo CSV resumen no existe")
        
        with open(ruta_csv, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            filas = list(reader)
            # 1 cabecera + 24 casos (2 Fnom * 3 reservas * 4 xcg)
            self.assertEqual(len(filas), 25, f"Se esperaban 25 filas en el CSV, se encontraron {len(filas)}")

        with open(ruta_resumen, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            filas_resumen = list(reader)
            self.assertEqual(len(filas_resumen), 25)


if __name__ == "__main__":
    unittest.main()
