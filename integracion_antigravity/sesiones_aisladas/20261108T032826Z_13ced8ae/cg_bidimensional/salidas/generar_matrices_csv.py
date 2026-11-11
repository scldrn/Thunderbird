#!/usr/bin/env python3
"""
===============================================================================
GENERADOR DE MATRICES CSV DE POSICIONES HIPOTÉTICAS DE CG (5 kg)
===============================================================================
Genera las matrices tabulares de posiciones hipotéticas de CG para:
- Fmax = 20.58 N (caso ideal previo de referencia)
- Fmax = 25.00 N (hipótesis complementaria de dimensionamiento)
- Archivo comparativo consolidado

Masa de referencia: 5.0 kg
Brazos CAD: Lx = 0.160 m, Ly = 0.076 m
Sistema de coordenadas: CAD (+x hacia la cola, -x hacia la nariz, +y izquierda, +z arriba)
"""

import csv
import os
from typing import List, Tuple
from equilibrio_cg import (
    PropulsionGeometry,
    verificar_equilibrio,
    max_fuerza_vertical_admisible,
)


def crear_malla_cg(geom: PropulsionGeometry = PropulsionGeometry()) -> List[Tuple[float, float]]:
    """
    Construye una malla de posiciones hipotéticas de CG que incluye:
    1. Grilla uniforme de alta resolución en [-Lx, +Lx] x [-Ly, +Ly].
    2. Puntos singulares de referencia de INFORME-VERTICAL.md:
       x in {0.0, 0.040, 0.080, 0.096, 0.120, 0.160}.
    3. Puntos de simetría y bordes laterales exactos.
    """
    Lx = geom.lx
    Ly = geom.ly

    # Puntos longitudinales clave (positivos y negativos)
    x_base = [
        -0.160, -0.140, -0.120, -0.100, -0.096, -0.080, -0.060, -0.040, -0.020,
        0.0,
        0.020, 0.040, 0.060, 0.080, 0.096, 0.100, 0.120, 0.140, 0.160
    ]
    # Puntos laterales clave
    y_base = [
        -0.076, -0.060, -0.0456, -0.038, -0.020, -0.019,
        0.0,
        0.019, 0.020, 0.038, 0.0456, 0.060, 0.076
    ]

    # Añadir puntos intermedios regulares para cobertura suave
    nx_regular = 33
    for i in range(nx_regular):
        x_val = round(-Lx + i * (2.0 * Lx / (nx_regular - 1)), 4)
        if x_val not in x_base:
            x_base.append(x_val)

    ny_regular = 21
    for j in range(ny_regular):
        y_val = round(-Ly + j * (2.0 * Ly / (ny_regular - 1)), 4)
        if y_val not in y_base:
            y_base.append(y_val)

    x_base = sorted(list(set(round(x, 5) for x in x_base)))
    y_base = sorted(list(set(round(y, 5) for y in y_base)))

    puntos = []
    for x in x_base:
        for y in y_base:
            puntos.append((x, y))
    return puntos


def generar_archivo_csv(
    fmax: float,
    nombre_archivo: str,
    puntos: List[Tuple[float, float]],
    m_kg: float = 5.0,
    geom: PropulsionGeometry = PropulsionGeometry(),
):
    """Genera un archivo CSV con las evaluaciones analíticas para un valor de Fmax dado."""
    encabezados = [
        "x_cg_m",
        "y_cg_m",
        "m_kg",
        "Fmax_N",
        "W_N",
        "es_factible",
        "f4_min_N",
        "f4_max_N",
        "holgura_N",
        "f1_N",
        "f2_N",
        "f3_N",
        "f4_N",
        "f_total_N",
        "error_W_N",
        "error_Mx_Nm",
        "error_My_Nm",
        "f_max_actuador_N",
        "margen_fmax_N",
        "capacidad_max_Fz_N",
        "solucion_tipo",
    ]

    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(encabezados)

        for x, y in puntos:
            sol = verificar_equilibrio(
                m_kg=m_kg,
                xcg_m=x,
                ycg_m=y,
                Fmax_N=fmax,
                geom=geom,
                estrategia="centro_intervalo",
            )
            cap_max = max_fuerza_vertical_admisible(x, y, fmax, geom=geom)

            f1_str = f"{sol.f1_N:.6f}" if sol.f1_N is not None else ""
            f2_str = f"{sol.f2_N:.6f}" if sol.f2_N is not None else ""
            f3_str = f"{sol.f3_N:.6f}" if sol.f3_N is not None else ""
            f4_str = f"{sol.f4_N:.6f}" if sol.f4_N is not None else ""
            f_tot_str = f"{(sol.f1_N + sol.f2_N + sol.f3_N + sol.f4_N):.6f}" if sol.es_factible else ""
            err_W_str = f"{sol.res_fuerza_N:.2e}" if sol.es_factible else ""
            err_Mx_str = f"{sol.res_momento_x_Nm:.2e}" if sol.es_factible else ""
            err_My_str = f"{sol.res_momento_y_Nm:.2e}" if sol.es_factible else ""
            f_max_str = f"{sol.max_fuerza_N:.6f}" if sol.max_fuerza_N is not None else ""
            margen_str = f"{sol.margen_fmax_N:.6f}" if sol.margen_fmax_N is not None else ""

            fila = [
                f"{x:.5f}",
                f"{y:.5f}",
                f"{m_kg:.2f}",
                f"{fmax:.2f}",
                f"{sol.W_N:.5f}",
                "SI" if sol.es_factible else "NO",
                f"{sol.intervalo.f4_min:.6f}",
                f"{sol.intervalo.f4_max:.6f}",
                f"{sol.intervalo.holgura:.6f}",
                f1_str,
                f2_str,
                f3_str,
                f4_str,
                f_tot_str,
                err_W_str,
                err_Mx_str,
                err_My_str,
                f_max_str,
                margen_str,
                f"{cap_max:.4f}",
                sol.solucion_tipo,
            ]
            writer.writerow(fila)


def generar_archivo_comparativo(
    nombre_archivo: str,
    puntos: List[Tuple[float, float]],
    m_kg: float = 5.0,
    geom: PropulsionGeometry = PropulsionGeometry(),
):
    """Genera una matriz comparativa con ambas hipótesis de empuje (20.58 N vs 25.00 N)."""
    encabezados = [
        "x_cg_m",
        "y_cg_m",
        "m_kg",
        "W_N",
        "factible_20_58N",
        "holgura_20_58N",
        "f_max_20_58N",
        "margen_20_58N",
        "capacidad_Fz_20_58N",
        "factible_25_00N",
        "holgura_25_00N",
        "f_max_25_00N",
        "margen_25_00N",
        "capacidad_Fz_25_00N",
        "diferencia_capacidad_N",
        "ganancia_factibilidad",
    ]

    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(encabezados)

        for x, y in puntos:
            sol_20 = verificar_equilibrio(m_kg=m_kg, xcg_m=x, ycg_m=y, Fmax_N=20.58, geom=geom)
            sol_25 = verificar_equilibrio(m_kg=m_kg, xcg_m=x, ycg_m=y, Fmax_N=25.00, geom=geom)

            cap_20 = max_fuerza_vertical_admisible(x, y, 20.58, geom=geom)
            cap_25 = max_fuerza_vertical_admisible(x, y, 25.00, geom=geom)

            f_max_20 = f"{sol_20.max_fuerza_N:.4f}" if sol_20.max_fuerza_N is not None else ""
            margen_20 = f"{sol_20.margen_fmax_N:.4f}" if sol_20.margen_fmax_N is not None else ""
            f_max_25 = f"{sol_25.max_fuerza_N:.4f}" if sol_25.max_fuerza_N is not None else ""
            margen_25 = f"{sol_25.margen_fmax_N:.4f}" if sol_25.margen_fmax_N is not None else ""

            ganancia = "INALTERADA"
            if not sol_20.es_factible and sol_25.es_factible:
                ganancia = "NUEVA_FACTIBLE"
            elif sol_20.es_factible and sol_25.es_factible:
                ganancia = "AMPLIA_MARGEN"
            elif not sol_20.es_factible and not sol_25.es_factible:
                ganancia = "AMBAS_NO_FACTIBLE"

            fila = [
                f"{x:.5f}",
                f"{y:.5f}",
                f"{m_kg:.2f}",
                f"{sol_20.W_N:.4f}",
                "SI" if sol_20.es_factible else "NO",
                f"{sol_20.intervalo.holgura:.4f}",
                f_max_20,
                margen_20,
                f"{cap_20:.2f}",
                "SI" if sol_25.es_factible else "NO",
                f"{sol_25.intervalo.holgura:.4f}",
                f_max_25,
                margen_25,
                f"{cap_25:.2f}",
                f"{(cap_25 - cap_20):.2f}",
                ganancia,
            ]
            writer.writerow(fila)


def main():
    directorio_salidas = os.path.dirname(os.path.abspath(__file__))
    geom = PropulsionGeometry(lx=0.160, ly=0.076)
    puntos = crear_malla_cg(geom)
    print(f"Malla generada con {len(puntos)} posiciones de CG evaluadas.")

    archivo_2058 = os.path.join(directorio_salidas, "matriz_posiciones_cg_Fmax20_58N.csv")
    archivo_2500 = os.path.join(directorio_salidas, "matriz_posiciones_cg_Fmax25_00N.csv")
    archivo_comp = os.path.join(directorio_salidas, "matriz_posiciones_cg_comparativa.csv")

    generar_archivo_csv(20.58, archivo_2058, puntos, m_kg=5.0, geom=geom)
    print(f"Generado: {archivo_2058}")

    generar_archivo_csv(25.00, archivo_2500, puntos, m_kg=5.0, geom=geom)
    print(f"Generado: {archivo_2500}")

    generar_archivo_comparativo(archivo_comp, puntos, m_kg=5.0, geom=geom)
    print(f"Generado: {archivo_comp}")


if __name__ == "__main__":
    main()
