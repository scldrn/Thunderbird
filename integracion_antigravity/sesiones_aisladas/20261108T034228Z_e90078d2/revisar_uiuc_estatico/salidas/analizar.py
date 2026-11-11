#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizar.py - Análisis Aerodinámico Estático de la Hélice Micro Invent 3.2x2.2 (UIUC)

Este script procesa datos experimentales de tracción y potencia estática de la
hélice abierta Micro Invent 3.2x2.2 del banco de pruebas UIUC (Volumen 2).

Fuentes primarias:
- UIUC Propeller Database (Volume 2):
  https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html
- Deters, R. W., Ananda, G. K., & Selig, M. S. (2014).
  "Reynolds Number Effects on the Performance of Small-Scale Propellers."
  AIAA 2014-2151. https://m-selig.ae.illinois.edu/pubs/DetersAnandaSelig-2014-AIAA-2014-2151.pdf

Restricciones y alcance:
- Hélice abierta de 2 palas en condición estática (V_inf = 0).
- No extrapolar fuera del rango medido de RPM (2,950 a 19,923.333 RPM).
- Los datos de potencia corresponden a potencia mecánica de eje, NO potencia eléctrica.
- La hélice abierta de 2 palas NO es transferible ni valida el ventilador entubado (EDF) C02 de 8 palas.
"""

import csv
import math
import os
import sys
from typing import Dict, List, Optional, Tuple

# ==============================================================================
# CONSTANTES Y PARÁMETROS SUPUESTOS / MEDIDOS
# ==============================================================================

# Supuestos atmosféricos estándar (ISA a nivel del mar)
RHO_DEFAULT: float = 1.225         # Densidad del aire, rho [kg/m^3] (supuesto)
A_SPEED_SOUND_DEFAULT: float = 340.3 # Velocidad del sonido, a [m/s] (supuesto)
NU_DEFAULT: float = 1.46e-5        # Viscosidad cinemática, nu [m^2/s] (supuesto)

# Datos medidos / catálogo de la hélice Micro Invent 3.2x2.2
DIAMETER_INCHES: float = 3.2       # Diámetro real en pulgadas (gráfico fuente / catálogo)
DIAMETER_M: float = 0.08128        # Diámetro real D [m] (3.2 * 0.0254 m)
RADIUS_M: float = DIAMETER_M / 2.0 # Radio R [m] = 0.04064 m
NUM_BLADES: int = 2                # Número de palas (catálogo Micro Invent)

# Cuerda relativa c/R a r/R = 0.75 (archivo mi_3.2x2.2_geom.txt)
C_OVER_R_075_DEFAULT: float = 0.1799

# Límites de RPM medidos experimentalmente (no extrapolar)
RPM_MIN_MEDIDO: float = 2950.000
RPM_MAX_MEDIDO: float = 19923.333


# ==============================================================================
# FUNCIONES DE CÁLCULO AERODINÁMICO
# ==============================================================================

def calcular_n(rpm: float) -> float:
    """
    Calcula la frecuencia de rotación n en revoluciones por segundo.

    Parámetros:
        rpm: Revoluciones por minuto [rev/min]

    Retorna:
        n: Frecuencia de rotación [rev/s]
    """
    if rpm < 0:
        raise ValueError(f"RPM no puede ser negativo: {rpm}")
    return rpm / 60.0


def calcular_empuje(ct: float, rho: float, n: float, d: float) -> float:
    """
    Calcula el empuje estático T a partir del coeficiente experimental CT.
    Definición: CT = T / (rho * n^2 * D^4)  =>  T = CT * rho * n^2 * D^4

    Parámetros:
        ct: Coeficiente de empuje experimental [-]
        rho: Densidad del aire [kg/m^3]
        n: Frecuencia de rotación [rev/s]
        d: Diámetro de la hélice [m]

    Retorna:
        T: Empuje estático [N]
    """
    if rho <= 0:
        raise ValueError(f"La densidad rho debe ser positiva: {rho}")
    if d <= 0:
        raise ValueError(f"El diámetro D debe ser positivo: {d}")
    if n < 0:
        raise ValueError(f"La frecuencia n no puede ser negativa: {n}")
    return ct * rho * (n ** 2) * (d ** 4)


def calcular_potencia(cp: float, rho: float, n: float, d: float) -> float:
    """
    Calcula la potencia mecánica de eje P a partir del coeficiente experimental CP.
    Definición: CP = P / (rho * n^3 * D^5)  =>  P = CP * rho * n^3 * D^5

    Nota: Representa la potencia mecánica absorbida por el eje (torque * omega).
    NO es potencia eléctrica de entrada al motor.

    Parámetros:
        cp: Coeficiente de potencia experimental [-]
        rho: Densidad del aire [kg/m^3]
        n: Frecuencia de rotación [rev/s]
        d: Diámetro de la hélice [m]

    Retorna:
        P: Potencia mecánica de eje [W]
    """
    if rho <= 0:
        raise ValueError(f"La densidad rho debe ser positiva: {rho}")
    if d <= 0:
        raise ValueError(f"El diámetro D debe ser positivo: {d}")
    if n < 0:
        raise ValueError(f"La frecuencia n no puede ser negativa: {n}")
    return cp * rho * (n ** 3) * (d ** 5)


def calcular_mach_punta(n: float, d: float, a: float) -> float:
    """
    Calcula el número de Mach en la punta de la pala.
    V_tip = omega * R = 2 * pi * n * (D / 2) = pi * n * D
    M_tip = V_tip / a

    Parámetros:
        n: Frecuencia de rotación [rev/s]
        d: Diámetro de la hélice [m]
        a: Velocidad del sonido en el medio [m/s]

    Retorna:
        M_tip: Número de Mach de punta [-]
    """
    if a <= 0:
        raise ValueError(f"La velocidad del sonido a debe ser positiva: {a}")
    if d <= 0:
        raise ValueError(f"El diámetro D debe ser positivo: {d}")
    if n < 0:
        raise ValueError(f"La frecuencia n no puede ser negativa: {n}")
    v_tip = math.pi * n * d
    return v_tip / a


def calcular_reynolds_075(
    n: float,
    d: float,
    c_over_r_075: float,
    nu: float
) -> float:
    """
    Calcula el número de Reynolds característico de la pala a 0.75R en condición estática.
    En hover / static (V_inf = 0), la velocidad de flujo incidente en la sección
    es esencialmente la velocidad de rotación tangencial:
        V_075 = omega * (0.75 * R) = 2 * pi * n * (0.75 * D / 2) = 0.75 * pi * n * D
    La cuerda local es:
        c_075 = (c / R)_075 * R = (c / R)_075 * (D / 2)
    El número de Reynolds es:
        Re_075R = (V_075 * c_075) / nu

    Parámetros:
        n: Frecuencia de rotación [rev/s]
        d: Diámetro de la hélice [m]
        c_over_r_075: Cuerda normalizada c/R a 0.75R [-]
        nu: Viscosidad cinemática [m^2/s]

    Retorna:
        Re_075R: Número de Reynolds a 0.75R [-]
    """
    if nu <= 0:
        raise ValueError(f"La viscosidad cinemática nu debe ser positiva: {nu}")
    if d <= 0:
        raise ValueError(f"El diámetro D debe ser positivo: {d}")
    if c_over_r_075 <= 0:
        raise ValueError(f"c/R a 0.75R debe ser positivo: {c_over_r_075}")
    if n < 0:
        raise ValueError(f"La frecuencia n no puede ser negativa: {n}")

    r = d / 2.0
    c_075 = c_over_r_075 * r
    v_075 = 0.75 * math.pi * n * d
    return (v_075 * c_075) / nu


def calcular_figura_merito(ct: float, cp: float) -> float:
    """
    Calcula la Figura de Mérito ideal (FM) en sustentación estática / hover.
    Basada en la teoría de cantidad de movimiento ideal de Rankine-Froude:
        P_ideal = T * v_i = T * sqrt(T / (2 * rho * A)) = T^(3/2) / sqrt(2 * rho * A)
    Expresada en función de los coeficientes estándar de hélice (CT y CP):
        T = CT * rho * n^2 * D^4
        P = CP * rho * n^3 * D^5
        A = (pi / 4) * D^2
        FM = P_ideal / P = (CT^(3/2) / CP) * sqrt(2 / pi) = CT^(3/2) / (CP * sqrt(pi / 2))

    Parámetros:
        ct: Coeficiente de empuje experimental [-]
        cp: Coeficiente de potencia experimental [-]

    Retorna:
        FM: Figura de mérito ideal [-]
    """
    if ct <= 0:
        raise ValueError(f"CT debe ser positivo para calcular la Figura de Mérito: {ct}")
    if cp <= 0:
        raise ValueError(f"CP debe ser positivo para calcular la Figura de Mérito: {cp}")
    return math.sqrt(2.0 / math.pi) * (ct ** 1.5) / cp


def calcular_figura_merito_dimensional(
    empuje: float,
    potencia: float,
    rho: float,
    d: float
) -> float:
    """
    Calcula la Figura de Mérito ideal a partir de magnitudes dimensionales (T, P, rho, D).
    Permite verificar la equivalencia exacta con la formulación adimensional.

    FM = (T^(3/2) / sqrt(2 * rho * A)) / P
    donde A = pi * D^2 / 4.
    """
    if empuje <= 0:
        raise ValueError(f"El empuje debe ser positivo: {empuje}")
    if potencia <= 0:
        raise ValueError(f"La potencia debe ser positiva: {potencia}")
    if rho <= 0:
        raise ValueError(f"La densidad debe ser positiva: {rho}")
    if d <= 0:
        raise ValueError(f"El diámetro debe ser positivo: {d}")

    area_disco = math.pi * (d ** 2) / 4.0
    potencia_ideal = (empuje ** 1.5) / math.sqrt(2.0 * rho * area_disco)
    return potencia_ideal / potencia


# ==============================================================================
# CARGA Y PROCESAMIENTO DE ARCHIVOS DE DATOS
# ==============================================================================

def cargar_datos_estaticos(ruta_archivo: str) -> List[Tuple[float, float, float]]:
    """
    Carga los puntos de ensayo estático (RPM, CT, CP) del archivo de texto UIUC.

    Retorna:
        Lista de tuplas (rpm, ct, cp)
    """
    if not os.path.isfile(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo estático: {ruta_archivo}")

    puntos: List[Tuple[float, float, float]] = []
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea_num, linea in enumerate(f, start=1):
            linea_limpia = linea.strip()
            if not linea_limpia or linea_limpia.startswith("RPM") or linea_limpia.startswith("#"):
                continue
            partes = linea_limpia.split()
            if len(partes) < 3:
                continue
            try:
                rpm = float(partes[0])
                ct = float(partes[1])
                cp = float(partes[2])
                puntos.append((rpm, ct, cp))
            except ValueError as e:
                raise ValueError(f"Error de formato numérico en línea {linea_num} de {ruta_archivo}: {linea}") from e

    if not puntos:
        raise ValueError(f"El archivo {ruta_archivo} no contiene registros válidos.")
    return puntos


def cargar_c_over_r_075(ruta_geometria: str) -> float:
    """
    Carga el valor de c/R a r/R = 0.75 del archivo de geometría UIUC.
    Si no encuentra la fila exacta 0.75, realiza interpolación lineal.
    """
    if not os.path.isfile(ruta_geometria):
        raise FileNotFoundError(f"No se encontró el archivo de geometría: {ruta_geometria}")

    datos_geom: List[Tuple[float, float, float]] = []
    with open(ruta_geometria, "r", encoding="utf-8") as f:
        for linea in f:
            linea_limpia = linea.strip()
            if not linea_limpia or linea_limpia.startswith("r/R") or linea_limpia.startswith("#"):
                continue
            partes = linea_limpia.split()
            if len(partes) >= 3:
                try:
                    r_over_r = float(partes[0])
                    c_over_r = float(partes[1])
                    beta = float(partes[2])
                    datos_geom.append((r_over_r, c_over_r, beta))
                except ValueError:
                    continue

    for r_over_r, c_over_r, _ in datos_geom:
        if abs(r_over_r - 0.75) < 1e-4:
            return c_over_r

    # Si no es exacto, interpolación lineal
    datos_geom.sort(key=lambda x: x[0])
    for i in range(len(datos_geom) - 1):
        r1, c1, _ = datos_geom[i]
        r2, c2, _ = datos_geom[i + 1]
        if r1 <= 0.75 <= r2:
            frac = (0.75 - r1) / (r2 - r1)
            return c1 + frac * (c2 - c1)

    return C_OVER_R_075_DEFAULT


def procesar_datos(
    puntos_estaticos: List[Tuple[float, float, float]],
    rho: float = RHO_DEFAULT,
    a_sound: float = A_SPEED_SOUND_DEFAULT,
    nu: float = NU_DEFAULT,
    d: float = DIAMETER_M,
    c_over_r_075: float = C_OVER_R_075_DEFAULT,
    permitir_extrapolacion: bool = False
) -> List[Dict[str, float]]:
    """
    Ejecuta el análisis aerodinámico punto por punto para toda la serie.

    Valida que los datos estén dentro del rango experimental para evitar
    extrapolación no física.
    """
    resultados: List[Dict[str, float]] = []

    for rpm, ct, cp in puntos_estaticos:
        if not permitir_extrapolacion:
            if rpm < (RPM_MIN_MEDIDO - 1e-2) or rpm > (RPM_MAX_MEDIDO + 1e-2):
                raise ValueError(
                    f"RPM {rpm} fuera del rango experimental medido [{RPM_MIN_MEDIDO}, {RPM_MAX_MEDIDO}]. "
                    "La extrapolación no está permitida."
                )

        n = calcular_n(rpm)
        empuje = calcular_empuje(ct, rho, n, d)
        potencia = calcular_potencia(cp, rho, n, d)
        mach_punta = calcular_mach_punta(n, d, a_sound)
        re_075 = calcular_reynolds_075(n, d, c_over_r_075, nu)
        fm = calcular_figura_merito(ct, cp)

        registro = {
            "rpm": rpm,
            "n_rev_s": n,
            "ct": ct,
            "cp": cp,
            "empuje_N": empuje,
            "potencia_eje_W": potencia,
            "mach_punta": mach_punta,
            "re_075r": re_075,
            "figura_merito": fm,
        }
        resultados.append(registro)

    return resultados


def guardar_csv(resultados: List[Dict[str, float]], ruta_csv: str) -> None:
    """
    Escribe los resultados procesados en formato CSV.
    """
    os.makedirs(os.path.dirname(os.path.abspath(ruta_csv)), exist_ok=True)
    columnas = [
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
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        for r in resultados:
            writer.writerow({
                "rpm": f"{r['rpm']:.3f}",
                "n_rev_s": f"{r['n_rev_s']:.6f}",
                "ct": f"{r['ct']:.6f}",
                "cp": f"{r['cp']:.6f}",
                "empuje_N": f"{r['empuje_N']:.6f}",
                "potencia_eje_W": f"{r['potencia_eje_W']:.6f}",
                "mach_punta": f"{r['mach_punta']:.6f}",
                "re_075r": f"{r['re_075r']:.2f}",
                "figura_merito": f"{r['figura_merito']:.6f}",
            })


def imprimir_tabla(resultados: List[Dict[str, float]]) -> None:
    """
    Imprime en consola una tabla formateada con los resultados calculados.
    """
    print("=" * 110)
    print(f"{'ANÁLISIS ESTÁTICO DE LA HÉLICE MICRO INVENT 3.2x2.2 (UIUC PropDB)':^110}")
    print("=" * 110)
    print(f"Parámetros: D = {DIAMETER_M:.5f} m ({DIAMETER_INCHES}\"), rho = {RHO_DEFAULT} kg/m3, a = {A_SPEED_SOUND_DEFAULT} m/s, nu = {NU_DEFAULT:.2e} m2/s")
    print("-" * 110)
    header = (
        f"{'RPM':>9} | {'n [rev/s]':>9} | {'CT [-]':>8} | {'CP [-]':>8} | "
        f"{'Empuje [N]':>10} | {'Pot.Eje [W]':>11} | {'M_tip [-]':>9} | {'Re_0.75R':>9} | {'FM [-]':>7}"
    )
    print(header)
    print("-" * 110)
    for r in resultados:
        linea = (
            f"{r['rpm']:9.3f} | {r['n_rev_s']:9.3f} | {r['ct']:8.6f} | {r['cp']:8.6f} | "
            f"{r['empuje_N']:10.6f} | {r['potencia_eje_W']:11.6f} | {r['mach_punta']:9.4f} | "
            f"{r['re_075r']:9.1f} | {r['figura_merito']:7.4f}"
        )
        print(linea)
    print("=" * 110)


# ==============================================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================================

def main() -> int:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_estaticos = os.path.join(
        base_dir, "entradas", "investigacion-aeronautica", "fuentes", "uiuc_propdb", "mi_3.2x2.2_static_0519rd.txt"
    )
    ruta_geom = os.path.join(
        base_dir, "entradas", "investigacion-aeronautica", "fuentes", "uiuc_propdb", "mi_3.2x2.2_geom.txt"
    )
    ruta_csv_salida = os.path.join(base_dir, "salidas", "puntos.csv")

    if not os.path.isfile(ruta_estaticos):
        print(f"Error: no se encontró archivo de datos estáticos en {ruta_estaticos}", file=sys.stderr)
        return 1

    c_over_r_075 = C_OVER_R_075_DEFAULT
    if os.path.isfile(ruta_geom):
        c_over_r_075 = cargar_c_over_r_075(ruta_geom)

    puntos_estaticos = cargar_datos_estaticos(ruta_estaticos)
    resultados = procesar_datos(
        puntos_estaticos=puntos_estaticos,
        rho=RHO_DEFAULT,
        a_sound=A_SPEED_SOUND_DEFAULT,
        nu=NU_DEFAULT,
        d=DIAMETER_M,
        c_over_r_075=c_over_r_075,
        permitir_extrapolacion=False,
    )

    guardar_csv(resultados, ruta_csv_salida)
    imprimir_tabla(resultados)
    print(f"\n[OK] Se procesaron {len(resultados)} puntos experimentales exitosamente.")
    print(f"[OK] Archivo CSV generado en: {ruta_csv_salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
