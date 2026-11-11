#!/usr/bin/env python3
"""
auditar_reserva_control.py
==========================
Auditoría técnica independiente de los límites del análisis de reserva de fuerza estática.

Verifica:
1. Equilibrio vertical y suma de momentos de cabeceo a partir de geometría documentada y primeros principios.
2. Comprobación aritmética estricta del caso crítico:
   masa = 5.0 kg, x_cg = 0.096 m, x_fan = ±0.160 m, F_nom = 20.58 N, reserva = 10%.
   Fuerza requerida por módulo de par posterior: 19.6133 N > Límite utilizable 18.522 N.
   Conclusión: NO hay equilibrio vertical en ese modelo.
3. Revisión crítica y rechazo justificado de las columnas de aceleración horizontal (ax)
   y márgenes de momento (dMy, dMx) calculadas bajo desacoplamiento irreal o hipótesis no sustentadas.
4. Generación de tablas auditadas en CSV distinguiendo datos medidos, supuestos y calculados.
"""

import math
import csv
import os
import sys

# ==============================================================================
# 1. PARÁMETROS DOCUMENTADOS Y DISTINCIÓN EXPLÍCITA DE FUENTES
# ==============================================================================
# DATOS MEDIDOS:
#   Ninguno. En la referencia no existen ensayos instalados identificados, ni curvas de
#   empuje/potencia de ventiladores en conducto montados, ni centro de gravedad medido.
#
# DATOS SUPUESTOS (HIPÓTESIS DE MODELO PRELIMINAR):
#   - Masa de la candidata: m = 5.0 kg
#   - Aceleración gravitatoria estándar: g = 9.80665 m/s² (ISO 80000-3 / CODATA)
#   - Semibrazo longitudinal de módulos: L = 0.160 m (estaciones en x = ±0.160 m)
#   - Semibrazo transversal de módulos: b = 0.076 m (estaciones en y = ±0.076 m)
#   - Brazo vertical relativo fuerza-CG: z_rel = 0.0 m (coplanar supuesto en el informe)
#   - Posiciones longitudinales supuestas de CG: x_cg in {0.0, 0.040, 0.080, 0.096} m
#   - Límites nominales de empuje por módulo: F_nom in {20.58, 25.00} N
#   - Factores de reserva estática: r in {0.0, 0.10, 0.20} (0%, 10%, 20%)
#   - Semiconos teóricos de empuje: theta in {35°, 45°}

MASA_KG = 5.0
G_MS2 = 9.80665
PESO_N = MASA_KG * G_MS2  # 49.03325 N
L_M = 0.160
B_M = 0.076

XCG_VALORES_M = [0.0, 0.040, 0.080, 0.096]
FNOM_VALORES_N = [20.58, 25.00]
RESERVAS_FRAC = [0.0, 0.10, 0.20]


def verificar_caso_aritmetico_especifico():
    """
    Comprueba paso a paso la aritmética exacta solicitada en la auditoría:
    m = 5.0 kg, x_cg = +0.096 m, x_fan = ±0.160 m, F_nom = 20.58 N, reserva = 10%.
    """
    m = 5.0
    g = 9.80665
    w = m * g  # 49.03325 N
    xcg = 0.096
    l_arm = 0.160
    f_nom = 20.58
    reserva = 0.10
    
    # 1. Límite utilizable bajo reserva del 10%
    f_utilizable = f_nom * (1.0 - reserva)  # 18.5220 N
    
    # 2. Fuerza necesaria por módulo trasero para equilibrio vertical y momento de cabeceo nulo
    # Sum(Fz) = 2*fz_rear + 2*fz_front = W
    # Sum(My) = 2*L*fz_rear - 2*L*fz_front - xcg*W = 0
    # => fz_rear = (W/4) * (1 + xcg/L)
    ratio_cg = xcg / l_arm  # 0.096 / 0.160 = 0.600
    fz_rear_necesaria = (w / 4.0) * (1.0 + ratio_cg)
    fz_front_necesaria = (w / 4.0) * (1.0 - ratio_cg)
    
    # 3. Comparación y déficit
    deficit = f_utilizable - fz_rear_necesaria
    hay_equilibrio = fz_rear_necesaria <= f_utilizable
    
    return {
        "m_kg": m,
        "g_ms2": g,
        "W_N": w,
        "xcg_m": xcg,
        "L_m": l_arm,
        "ratio_xcg_L": ratio_cg,
        "Fnom_N": f_nom,
        "reserva_pct": reserva * 100.0,
        "Futilizable_N": f_utilizable,
        "fz_rear_necesaria_N": fz_rear_necesaria,
        "fz_front_necesaria_N": fz_front_necesaria,
        "deficit_N": deficit,
        "hay_equilibrio_vertical": hay_equilibrio,
    }


def auditar_escenario(fnom_n: float, r_frac: float, xcg_m: float):
    """
    Audita un escenario combinatorio separando rigurosamente:
    - Métricas verticales sustentadas por primeros principios y geometría documentada.
    - Métricas de momentos y aceleración horizontal evaluadas críticamente y rechazadas si carecen de sustento.
    """
    f_usable = fnom_n * (1.0 - r_frac)
    reserva_pct = round(r_frac * 100.0, 1)
    
    # --- A. EQUILIBRIO VERTICAL Y CABECEO (SUSTENTADO) ---
    # Primeros principios:
    # 2*fz_rear + 2*fz_front = W
    # 2*L*fz_rear - 2*L*fz_front = xcg*W
    fz_rear = (PESO_N / 4.0) * (1.0 + xcg_m / L_M)
    fz_front = (PESO_N / 4.0) * (1.0 - xcg_m / L_M)
    
    margen_crit_n = f_usable - fz_rear
    factible_estacionario = margen_crit_n >= -1e-9
    
    # Límite vertical máximo en trim de cabeceo:
    fz_max_trim_n = (4.0 * f_usable) / (1.0 + abs(xcg_m) / L_M)
    az_max_trim_g = (fz_max_trim_n / PESO_N) - 1.0
    
    # Umbral analítico crítico de CG para hover factible:
    xcg_crit_m = L_M * ((4.0 * f_usable / PESO_N) - 1.0)
    
    # --- B. MÁRGENES DE MOMENTO (EVALUACIÓN CRÍTICA) ---
    # En el informe previo se computaron bajo desacoplamiento unieje puro y empuje mínimo nulo:
    # dMy+ = 4*L*min(F_usable - fz_rear, fz_front)
    # dMy- = 4*L*min(fz_rear, F_usable - fz_front)
    # dMx  = 2*b*(min(fz_rear, F_usable - fz_rear) + min(fz_front, F_usable - fz_front))
    # DICTAMEN: NO SUSTENTADO para dinámica de vuelo multieje.
    # Razones:
    # 1. Ignora acoplamiento simultáneo (cabeceo consume alabeo y guiñada).
    # 2. Supone empuje mínimo nulo (f_min = 0), irreal para ventiladores en conducto.
    # 3. Omite par de reacción del rotor (torque aerodinámico Q) y momentos giroscópicos.
    if factible_estacionario:
        dmy_pos_desacoplado = 4.0 * L_M * min(f_usable - fz_rear, fz_front)
        dmy_neg_desacoplado = 4.0 * L_M * min(fz_rear, f_usable - fz_front)
        dmx_desacoplado = 2.0 * B_M * (min(fz_rear, f_usable - fz_rear) + min(fz_front, f_usable - fz_front))
    else:
        dmy_pos_desacoplado = 0.0
        dmy_neg_desacoplado = 0.0
        dmx_desacoplado = 0.0
    
    # --- C. ACELERACIÓN HORIZONTAL (EVALUACIÓN CRÍTICA) ---
    # En el informe previo se computó con: fx_i = min(fz_i * tan(theta), sqrt(F_usable^2 - fz_i^2))
    # DICTAMEN: RECHAZADO / NO SUSTENTADO.
    # Razones:
    # 1. Supone z_rel = 0.0 m (fuerzas coplanares con CG). En INFORME.md un z_rel de ±0.039 m
    #    altera ax de 0.731 g a 0.254 g (variación de casi 3:1). Asumir z_rel=0 no está sustentado.
    # 2. Asume cono esférico continuo ideal sin pérdidas, contradiciendo el modelo LP de 65 rayos
    #    de referencia (que da 0.441 g en vez de 0.454 g para 45° sin reserva).
    # 3. No existe mecanismo de vectorización modelado ni pérdidas de difusor/labio instaladas.
    # 4. Agota el 100% de la capacidad de reserva en empuje vectorial, dejando 0 margen para control.
    if factible_estacionario:
        th_rad = math.radians(45.0)
        tan_th = math.tan(th_rad)
        fx_r = min(fz_rear * tan_th, math.sqrt(max(0.0, f_usable**2 - fz_rear**2)))
        fx_f = min(fz_front * tan_th, math.sqrt(max(0.0, f_usable**2 - fz_front**2)))
        ax_45_desacoplado_g = (2.0 * (fx_r + fx_f)) / PESO_N
    else:
        ax_45_desacoplado_g = 0.0
        
    return {
        "Fnom_N": fnom_n,
        "reserva_pct": reserva_pct,
        "Fusable_N": round(f_usable, 4),
        "xcg_m": xcg_m,
        "xcg_over_L": round(xcg_m / L_M, 4),
        # Verificación estática vertical
        "factible_estacionario": factible_estacionario,
        "fz_rear_hover_N": round(fz_rear, 4),
        "fz_front_hover_N": round(fz_front, 4),
        "margen_crit_N": round(margen_crit_n, 4),
        "Fz_max_trim_N": round(fz_max_trim_n, 4),
        "az_max_trim_g": round(az_max_trim_g, 4),
        "xcg_crit_m": round(xcg_crit_m, 4),
        # Columnas auditadas críticamente (rechazadas / desacopladas)
        "dMy_encabritar_desacoplado_Nm": round(dmy_pos_desacoplado, 4),
        "dMy_picar_desacoplado_Nm": round(dmy_neg_desacoplado, 4),
        "dMx_roll_desacoplado_Nm": round(dmx_desacoplado, 4),
        "ax_45deg_desacoplado_g": round(ax_45_desacoplado_g, 4),
        "dictamen_vertical": "EQUILIBRIO FACTIBLE" if factible_estacionario else "INVIABLE / SIN EQUILIBRIO",
        "dictamen_horizontal_y_momentos": "NO SUSTENTADO PARA VUELO (RECHAZADO)",
    }


def ejecutar_auditoria():
    """Genera la matriz completa de 24 escenarios auditados."""
    escenarios = []
    for fnom in FNOM_VALORES_N:
        for r in RESERVAS_FRAC:
            for xcg in XCG_VALORES_M:
                escenarios.append(auditar_escenario(fnom, r, xcg))
    return escenarios


def exportar_csv_auditado(escenarios, ruta_csv):
    """Exporta los resultados con anotaciones explícitas de auditoría."""
    campos = [
        "Fnom_N",
        "reserva_pct",
        "Fusable_N",
        "xcg_m",
        "xcg_over_L",
        "factible_estacionario",
        "dictamen_vertical",
        "fz_rear_hover_N",
        "fz_front_hover_N",
        "margen_crit_N",
        "Fz_max_trim_N",
        "az_max_trim_g",
        "xcg_crit_m",
        "dMy_encabritar_desacoplado_Nm",
        "dMy_picar_desacoplado_Nm",
        "dMx_roll_desacoplado_Nm",
        "ax_45deg_desacoplado_g",
        "dictamen_horizontal_y_momentos",
    ]
    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for esc in escenarios:
            writer.writerow(esc)


def exportar_resumen_auditoria(escenarios, ruta_csv):
    """Exporta tabla ejecutiva enfocada en la factibilidad vertical estricta."""
    campos = [
        "Fnom_N",
        "reserva_pct",
        "Fusable_N",
        "xcg_m",
        "dictamen_vertical",
        "fz_rear_hover_N",
        "margen_crit_N",
        "az_max_trim_g",
        "xcg_crit_m",
    ]
    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for esc in escenarios:
            writer.writerow({k: esc[k] for k in campos})


def main():
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    ruta_salidas = directorio_script if os.path.basename(directorio_script) == "salidas" else os.path.join(directorio_script, "salidas")
    os.makedirs(ruta_salidas, exist_ok=True)
    
    # 1. Comprobación del caso específico
    caso = verificar_caso_aritmetico_especifico()
    print("=" * 80)
    print("AUDITORÍA DE CASO CRÍTICO ESPECÍFICO")
    print("=" * 80)
    print(f"Masa nominal (supuesta):             {caso['m_kg']:.1f} kg")
    print(f"Gravedad estándar:                   {caso['g_ms2']:.5f} m/s²")
    print(f"Peso resultante (W):                 {caso['W_N']:.5f} N")
    print(f"Posición CG longitudinal (xcg):      +{caso['xcg_m']:.3f} m")
    print(f"Semibrazo longitudinal módulo (L):   ±{caso['L_m']:.3f} m (ratio xcg/L = {caso['ratio_xcg_L']:.3f})")
    print(f"Límite nominal por módulo (Fnom):    {caso['Fnom_N']:.2f} N")
    print(f"Reserva de fuerza estricta:          {caso['reserva_pct']:.0f}%")
    print(f"Límite utilizable (Fusable):         {caso['Futilizable_N']:.4f} N")
    print("-" * 80)
    print(f"Fuerza requerida módulo trasero:     {caso['fz_rear_necesaria_N']:.4f} N")
    print(f"Fuerza requerida módulo delantero:   {caso['fz_front_necesaria_N']:.4f} N")
    print(f"Balance de fuerza vertical:          2*(19.6133 N) + 2*(4.9033 N) = {2*caso['fz_rear_necesaria_N'] + 2*caso['fz_front_necesaria_N']:.4f} N == W")
    print(f"Margen residual en módulo trasero:   {caso['deficit_N']:+.4f} N (Déficit de {-caso['deficit_N']:.4f} N)")
    print(f"¿Existe equilibrio vertical estático?: {'SÍ' if caso['hay_equilibrio_vertical'] else 'NO (INVIABLE: fz_rear > Fusable)'}")
    print("=" * 80)
    
    # 2. Barrido completo y exportación
    escenarios = ejecutar_auditoria()
    ruta_csv_completo = os.path.join(ruta_salidas, "sensibilidad_reserva_auditada.csv")
    ruta_csv_resumen = os.path.join(ruta_salidas, "resumen_auditoria_estatica.csv")
    
    exportar_csv_auditado(escenarios, ruta_csv_completo)
    exportar_resumen_auditoria(escenarios, ruta_csv_resumen)
    
    print(f"\n[OK] CSV detallado de auditoría generado: {ruta_csv_completo}")
    print(f"[OK] CSV resumen de auditoría generado:   {ruta_csv_resumen}")


if __name__ == "__main__":
    main()
