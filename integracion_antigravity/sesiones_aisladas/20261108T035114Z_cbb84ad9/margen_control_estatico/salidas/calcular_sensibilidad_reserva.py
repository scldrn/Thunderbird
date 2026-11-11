#!/usr/bin/env python3
"""
calcular_sensibilidad_reserva.py
================================
Cálculo de la sensibilidad estática ilustrativa de reservar 0%, 10% y 20%
del límite nominal de fuerza por módulo para maniobras/perturbaciones,
tratando la reserva como una reducción conservadora del límite utilizable
(F_usable = F_max_nom * (1 - r)) y no como una garantía dinámica.

Parámetros del estudio:
  - Masa nominal supuesta: m = 5.0 kg (candidata C02)
  - Gravedad estándar: g = 9.80665 m/s² (CODATA / ISO 80000-3)
  - Posiciones longitudinales de módulos: x = ±0.160 m (L = 0.160 m, 4 módulos: 2 frontales, 2 traseros)
  - Posiciones transversales de módulos: y = ±0.076 m (b = 0.076 m)
  - Posiciones de CG longitudinal: x_cg = [0.0, 0.040, 0.080, 0.096] m
  - Límites nominales de fuerza por módulo: F_max_nom = 20.58 N y 25.0 N
  - Fracciones de reserva: r = 0.0 (0%), 0.10 (10%), 0.20 (20%)

Salidas generadas:
  - salidas/sensibilidad_reserva_control.csv (tabla exhaustiva de sensibilidad)
  - salidas/resumen_sensibilidad_reserva.csv (tabla resumen ejecutivo)
"""

import math
import csv
import os

# ==============================================================================
# 1. PARÁMETROS FÍSICOS Y GEOMÉTRICOS (DISTINCIÓN EXPLÍCITA DE FUENTES Y TIPOS)
# ==============================================================================
# Datos medidos:
#   Ninguno. No existen ensayos instalados identificados ni mediciones reales de vuelo
#   para la candidata C02 en la referencia.
#
# Datos supuestos (hipótesis de diseño preliminar):
#   - Masa del vehículo: m = 5.0 kg
#   - Gravedad estándar: g = 9.80665 m/s²
#   - Semibrazo longitudinal de módulos: L = 0.160 m (estaciones en x = ±0.160 m)
#   - Semibrazo transversal de módulos: b = 0.076 m (estaciones en y = ±0.076 m)
#   - Número de módulos: N_mod = 4 (2 en x = +L, 2 en x = -L)
#   - Brazo vertical de aplicación de fuerza relativo al CG: z_rel = 0.0 m (coplanar)
#   - Semiconos ideales de empuje para análisis horizontal: theta = 35° y 45°
#   - Posiciones longitudinales supuestas de CG: x_cg in {0.0, 0.040, 0.080, 0.096} m
#   - Límites nominales de fuerza por módulo: F_max_nom in {20.58, 25.00} N
#   - Reservas estáticas de fuerza: r in {0.0, 0.10, 0.20} (0%, 10%, 20%)

MASA_KG = 5.0
G_MS2 = 9.80665
PESO_N = MASA_KG * G_MS2  # 49.03325 N
L_M = 0.160
B_M = 0.076
N_TOTAL_MODULOS = 4
MODULOS_POR_ESTACION = 2  # 2 traseros en +L, 2 frontales en -L

XCG_VALORES_M = [0.0, 0.040, 0.080, 0.096]
FNOM_VALORES_N = [20.58, 25.00]
RESERVAS_FRAC = [0.0, 0.10, 0.20]
CONOS_GRADOS = [35.0, 45.0]


def calcular_caso(fnom_n: float, r_frac: float, xcg_m: float):
    """
    Calcula la asignación estática, márgenes de fuerza y autoridades de momento
    para una combinación dada de fuerza nominal, reserva y posición de CG.
    """
    f_usable = fnom_n * (1.0 - r_frac)
    reserva_pct = round(r_frac * 100.0, 1)
    
    # 1. Fuerza requerida por módulo en vuelo estacionario (hover)
    # Equilibrio vertical: 2*fz_rear + 2*fz_front = W
    # Equilibrio cabeceo: 2*L*fz_rear - 2*L*fz_front = xcg * W
    fz_rear_hover = (PESO_N / 4.0) * (1.0 + xcg_m / L_M)
    fz_front_hover = (PESO_N / 4.0) * (1.0 - xcg_m / L_M)
    
    # Módulo crítico (trasero si xcg >= 0)
    fz_crit_hover = max(fz_rear_hover, fz_front_hover)
    margen_fuerza_crit_n = f_usable - fz_crit_hover
    margen_fuerza_crit_pct_usable = (margen_fuerza_crit_n / f_usable) * 100.0
    margen_fuerza_crit_pct_nom = (margen_fuerza_crit_n / fnom_n) * 100.0
    
    # Factibilidad estática del estacionario bajo el límite utilizable
    factible_estacionario = margen_fuerza_crit_n >= -1e-9
    
    # 2. Capacidad vertical máxima analítica en equilibrio de cabeceo (My = 0)
    # Fz_max = 4 * F_usable / (1 + |xcg| / L)
    fz_max_analitico_n = (4.0 * f_usable) / (1.0 + abs(xcg_m) / L_M)
    az_max_g = (fz_max_analitico_n / PESO_N) - 1.0
    twr_utilizable = fz_max_analitico_n / PESO_N
    
    # Posición crítica analítica de CG para la cual el margen se hace exactamente cero
    xcg_crit_hover_m = L_M * ((4.0 * f_usable / PESO_N) - 1.0)
    
    # 3. Autoridades de momento a empuje constante de sustentación (Fz = W)
    if factible_estacionario:
        # Autoridad de cabeceo a picar (nariz abajo / cola arriba, dMy < 0 en convenio convencional):
        # Aumentar delanteros, reducir traseros:
        # delta_f_delantero <= F_usable - fz_front
        # delta_f_trasero <= fz_rear
        delta_picar = min(fz_rear_hover, f_usable - fz_front_hover)
        delta_my_picar_nm = 4.0 * L_M * delta_picar  # 2 módulos por estación
        
        # Autoridad de cabeceo a encabritar (nariz arriba / cola abajo, dMy > 0):
        # Aumentar traseros, reducir delanteros:
        # delta_f_trasero <= F_usable - fz_rear
        # delta_f_delantero <= fz_front
        delta_encabritar = min(f_usable - fz_rear_hover, fz_front_hover)
        delta_my_encabritar_nm = 4.0 * L_M * delta_encabritar
        
        # Autoridad de alabeo (dMx):
        # Diferencial entre módulo de babor y estribor en cada estación:
        # En traseros: delta_r = min(fz_rear, F_usable - fz_rear)
        # En delanteros: delta_f = min(fz_front, F_usable - fz_front)
        # dMx = 2 * b * (delta_r + delta_f)
        delta_roll_rear = min(fz_rear_hover, f_usable - fz_rear_hover)
        delta_roll_front = min(fz_front_hover, f_usable - fz_front_hover)
        delta_mx_nm = 2.0 * B_M * (delta_roll_rear + delta_roll_front)
        
        # 4. Autoridad de aceleración horizontal en estacionario vertical (az = 0, My = 0)
        # Para conos ideales de 35° y 45°
        ax_max_conos = {}
        for th_deg in CONOS_GRADOS:
            th_rad = math.radians(th_deg)
            tan_th = math.tan(th_rad)
            # Límite horizontal por módulo: min(fz * tan(theta), sqrt(F_usable^2 - fz^2))
            fx_rear = min(fz_rear_hover * tan_th, math.sqrt(max(0.0, f_usable**2 - fz_rear_hover**2)))
            fx_front = min(fz_front_hover * tan_th, math.sqrt(max(0.0, f_usable**2 - fz_front_hover**2)))
            fx_tot = 2.0 * (fx_rear + fx_front)
            ax_max_conos[th_deg] = fx_tot / PESO_N
    else:
        delta_my_picar_nm = 0.0
        delta_my_encabritar_nm = 0.0
        delta_mx_nm = 0.0
        ax_max_conos = {th: 0.0 for th in CONOS_GRADOS}
    
    return {
        "Fnom_N": fnom_n,
        "reserva_pct": reserva_pct,
        "reserva_frac": r_frac,
        "Fusable_N": round(f_usable, 4),
        "xcg_m": xcg_m,
        "xcg_over_L": round(xcg_m / L_M, 4),
        "factible_estacionario": factible_estacionario,
        "fz_rear_hover_N": round(fz_rear_hover, 4),
        "fz_front_hover_N": round(fz_front_hover, 4),
        "margen_crit_N": round(margen_fuerza_crit_n, 4),
        "margen_crit_pct_usable": round(margen_fuerza_crit_pct_usable, 2),
        "margen_crit_pct_nom": round(margen_fuerza_crit_pct_nom, 2),
        "Fz_max_analitico_N": round(fz_max_analitico_n, 4),
        "az_max_g": round(az_max_g, 4),
        "twr_utilizable": round(twr_utilizable, 4),
        "xcg_crit_hover_m": round(xcg_crit_hover_m, 4),
        "delta_My_encabritar_Nm": round(delta_my_encabritar_nm, 4),
        "delta_My_picar_Nm": round(delta_my_picar_nm, 4),
        "delta_Mx_roll_Nm": round(delta_mx_nm, 4),
        "ax_max_35deg_g": round(ax_max_conos[35.0], 4),
        "ax_max_45deg_g": round(ax_max_conos[45.0], 4),
    }


def ejecutar_barrido():
    """Ejecuta todas las combinaciones y guarda los entregables en CSV."""
    resultados = []
    for fnom in FNOM_VALORES_N:
        for r in RESERVAS_FRAC:
            for xcg in XCG_VALORES_M:
                res = calcular_caso(fnom, r, xcg)
                resultados.append(res)
    return resultados


def exportar_csv(resultados, ruta_csv):
    """Escribe los resultados a un archivo CSV exhaustivo."""
    campos = [
        "Fnom_N",
        "reserva_pct",
        "Fusable_N",
        "xcg_m",
        "xcg_over_L",
        "factible_estacionario",
        "fz_rear_hover_N",
        "fz_front_hover_N",
        "margen_crit_N",
        "margen_crit_pct_usable",
        "margen_crit_pct_nom",
        "Fz_max_analitico_N",
        "az_max_g",
        "twr_utilizable",
        "xcg_crit_hover_m",
        "delta_My_encabritar_Nm",
        "delta_My_picar_Nm",
        "delta_Mx_roll_Nm",
        "ax_max_35deg_g",
        "ax_max_45deg_g",
    ]
    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)


def exportar_resumen_csv(resultados, ruta_csv):
    """Escribe un resumen ejecutivo comparativo a CSV."""
    campos = [
        "Fnom_N",
        "reserva_pct",
        "Fusable_N",
        "xcg_m",
        "factible_estacionario",
        "margen_crit_N",
        "az_max_g",
        "delta_My_encabritar_Nm",
        "delta_Mx_roll_Nm",
        "ax_max_45deg_g",
    ]
    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for r in resultados:
            writer.writerow({k: r[k] for k in campos})


def imprimir_tablas(resultados):
    """Imprime tablas legibles en consola."""
    print("=" * 110)
    print(f"{'SENSIBILIDAD ESTÁTICA DE RESERVA DE FUERZA (CANDIDATA C02, 5.0 kg)':^110}")
    print("=" * 110)
    print(f"Masa = {MASA_KG:.1f} kg | Peso = {PESO_N:.3f} N | L = ±{L_M:.3f} m | b = ±{B_M:.3f} m | g = {G_MS2:.5f} m/s²")
    print("-" * 110)
    
    formato_encabezado = (
        f"{'Fnom':>6} | {'Res':>4} | {'Fusab':>6} | {'xcg':>5} | {'Fact?':>5} | "
        f"{'fz_rear':>7} | {'Margen':>7} | {'az_max':>7} | {'dMy+':>6} | {'dMy-':>6} | {'dMx':>6} | {'ax45':>6}"
    )
    print(formato_encabezado)
    print("-" * 110)
    
    for r in resultados:
        fact_str = "SÍ" if r["factible_estacionario"] else "NO"
        linea = (
            f"{r['Fnom_N']:6.2f} | {r['reserva_pct']:3.0f}% | {r['Fusable_N']:6.3f} | {r['xcg_m']:5.3f} | {fact_str:>5} | "
            f"{r['fz_rear_hover_N']:7.3f} | {r['margen_crit_N']:+7.3f} | {r['az_max_g']:+7.3f} | "
            f"{r['delta_My_encabritar_Nm']:6.3f} | {r['delta_My_picar_Nm']:6.3f} | "
            f"{r['delta_Mx_roll_Nm']:6.3f} | {r['ax_max_45deg_g']:6.3f}"
        )
        print(linea)
    print("=" * 110)


def main():
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    ruta_salidas = directorio_script if os.path.basename(directorio_script) == "salidas" else os.path.join(directorio_script, "salidas")
    os.makedirs(ruta_salidas, exist_ok=True)
    
    ruta_csv_completo = os.path.join(ruta_salidas, "sensibilidad_reserva_control.csv")
    ruta_csv_resumen = os.path.join(ruta_salidas, "resumen_sensibilidad_reserva.csv")
    
    resultados = ejecutar_barrido()
    exportar_csv(resultados, ruta_csv_completo)
    exportar_resumen_csv(resultados, ruta_csv_resumen)
    imprimir_tablas(resultados)
    print(f"\n[OK] CSV detallado generado en: {ruta_csv_completo}")
    print(f"[OK] CSV resumen generado en:   {ruta_csv_resumen}")


if __name__ == "__main__":
    main()
