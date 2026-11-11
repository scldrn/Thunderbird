#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analisis_cargas_compuerta.py
-------------------------------------------------------------------------------
Análisis paramétrico de cargas aerodinámicas ilustrativas sobre compuertas de
ventiladores internos en arquitectura de propulsión A.

Formulaciones utilizadas (simplificadas bajo supuestos explícitos):
  - Presión dinámica:
      q = 0.5 * rho * V^2
  - Presión diferencial uniforme supuesta:
      Delta_p = Cp_diferencial * q
  - Fuerza normal aerodinámica supuesta:
      F = Delta_p * A
  - Momento de charnela / vuelco supuesto:
      M = F * brazo

Escalado geométrico isomórfico según objetivo de masa:
  - Factor de escala lineal: lambda_L = (m / m_ref)^(1/3), con m_ref = 5.0 kg
  - Factor de escala de área: lambda_A = lambda_L^2 = (m / m_ref)^(2/3)
  - Factor de escala de brazo: lambda_arm = lambda_L = (m / m_ref)^(1/3)
  - Factor de momento: lambda_M = lambda_A * lambda_arm = m / m_ref

AVISO CRÍTICO:
  - Las presiones, fuerzas y momentos resultantes son PURAMENTE ILUSTRATIVOS E HIPOTÉTICOS.
  - La presión dinámica q NO representa una distribución real de presión diferencial uniforme.
  - Las tapas de conducto en la arquitectura A están concebidas EXCLUSIVAMENTE para baja velocidad.
  - Ninguna carga real ni mecanismo cinemático instalado ha sido validado físicamente.
-------------------------------------------------------------------------------
"""

import sys
import math
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple


# =============================================================================
# CONSTANTES DE REFERENCIA Y PARÁMETROS BASE
# =============================================================================

# Datos de referencia estándar (ISA nivel del mar / C02_CANDIDATA.json)
RHO_STD_KG_M3 = 1.225         # Densidad del aire estándar ISA a nivel del mar [kg/m³]
KMH_TO_MS_FACTOR = 1.0 / 3.6   # Factor exacto de conversión km/h -> m/s

# Casos de velocidad requeridos [km/h]
VELOCITIES_KMH = [600.0, 1000.0]

# Masas objetivo del estudio [kg] (m_ref = 5.0 kg)
MASS_TARGETS_KG = [2.0, 5.0, 10.0]
REF_MASS_KG = 5.0

# Coeficientes de presión diferencial supuestos (barrido paramétrico representativo)
CP_DIFFERENTIAL_VALUES = [0.1, 0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0]

# Dimensiones explícitamente HIPOTÉTICAS de la compuerta para la variante de referencia (5 kg)
# Coherentes con el orden de magnitud del conducto de 84 mm de diámetro (bore = 0.084 m, área neto conducto ~ 0.00554 m²)
# y la distancia entre eje CAD (Y = +/-124 mm) y centro de conducto (Y = +/-76 mm) -> delta_Y = 48 mm = 0.048 m.
HIPOTETICO_AREA_REF_M2 = 0.0070       # Área de compuerta supuesta [m²] (70.0 cm²)
HIPOTETICO_ARM_REF_M = 0.048          # Brazo de palanca al centro de presiones supuesto [m] (48.0 mm)

# Diámetro de conducto documentado en C02_CANDIDATA.json para referencia geométrica
BORE_DIAMETER_REF_M = 0.084           # Diámetro nominal de conducto [m] (84 mm)


# =============================================================================
# FUNCIONES AERODINÁMICAS Y CINEMÁTICAS FUNDAMENTALES
# =============================================================================

def kmh_to_ms(v_kmh: float) -> float:
    """
    Convierte velocidad de km/h a m/s con factor exacto 1/3.6.
    """
    if v_kmh < 0.0:
        raise ValueError("La velocidad no puede ser negativa.")
    return v_kmh * KMH_TO_MS_FACTOR


def dynamic_pressure(rho: float, v_ms: float) -> float:
    """
    Calcula la presión dinámica incompresible estándar:
      q = 0.5 * rho * V^2 [Pa]
    """
    if rho <= 0.0:
        raise ValueError("La densidad debe ser estrictamente positiva.")
    if v_ms < 0.0:
        raise ValueError("La velocidad no puede ser negativa.")
    return 0.5 * rho * (v_ms ** 2)


def differential_pressure(q: float, cp_differential: float) -> float:
    """
    Calcula el salto de presión diferencial uniforme supuesto:
      Delta_p = Cp_diferencial * q [Pa]
    """
    return cp_differential * q


def geometric_scale_factors(mass_target_kg: float, ref_mass_kg: float = REF_MASS_KG) -> Dict[str, float]:
    """
    Calcula los factores de escala geométrica isomórfica basados en el objetivo de masa:
      lambda_L = (m / m_ref)^(1/3)
      lambda_A = lambda_L^2 = (m / m_ref)^(2/3)
      lambda_V = lambda_L^3 = m / m_ref
    """
    if mass_target_kg <= 0.0 or ref_mass_kg <= 0.0:
        raise ValueError("Las masas deben ser estrictamente positivas.")
    mass_ratio = mass_target_kg / ref_mass_kg
    lambda_L = mass_ratio ** (1.0 / 3.0)
    lambda_A = lambda_L ** 2.0
    lambda_V = mass_ratio
    return {
        "mass_ratio": mass_ratio,
        "lambda_L": lambda_L,
        "lambda_A": lambda_A,
        "lambda_V": lambda_V,
    }


def scale_hypothetical_area(area_ref_m2: float, lambda_A: float) -> float:
    """
    Escala el área supuesta de compuerta según el factor de área:
      A(m) = A_ref * lambda_A [m²]
    """
    return area_ref_m2 * lambda_A


def scale_hypothetical_arm(arm_ref_m: float, lambda_L: float) -> float:
    """
    Escala el brazo supuesto según el factor de longitud:
      brazo(m) = brazo_ref * lambda_L [m]
    """
    return arm_ref_m * lambda_L


def aerodynamic_force(delta_p: float, area: float) -> float:
    """
    Calcula la fuerza normal resultante bajo distribución uniforme supuesta:
      F = Delta_p * A [N]
    """
    return delta_p * area


def aerodynamic_moment(force: float, arm: float) -> float:
    """
    Calcula el momento de vuelco o charnela respecto al eje supuesto:
      M = F * brazo [N·m]
    """
    return force * arm


# =============================================================================
# MOTOR DE ANÁLISIS PARAMÉTRICO
# =============================================================================

def run_parametric_case(
    v_kmh: float,
    rho: float,
    mass_target_kg: float,
    cp_diff: float,
    area_ref_m2: float = HIPOTETICO_AREA_REF_M2,
    arm_ref_m: float = HIPOTETICO_ARM_REF_M,
    ref_mass_kg: float = REF_MASS_KG,
) -> Dict[str, Any]:
    """
    Ejecuta un punto individual del análisis paramétrico.
    """
    v_ms = kmh_to_ms(v_kmh)
    q_pa = dynamic_pressure(rho, v_ms)
    delta_p_pa = differential_pressure(q_pa, cp_diff)
    
    scales = geometric_scale_factors(mass_target_kg, ref_mass_kg)
    lambda_L = scales["lambda_L"]
    lambda_A = scales["lambda_A"]
    
    area_m2 = scale_hypothetical_area(area_ref_m2, lambda_A)
    arm_m = scale_hypothetical_arm(arm_ref_m, lambda_L)
    
    force_n = aerodynamic_force(delta_p_pa, area_m2)
    moment_nm = aerodynamic_moment(force_n, arm_m)
    
    return {
        "velocidad_kmh": v_kmh,
        "velocidad_ms": v_ms,
        "rho_kg_m3": rho,
        "q_pa": q_pa,
        "cp_diferencial": cp_diff,
        "delta_p_pa": delta_p_pa,
        "masa_objetivo_kg": mass_target_kg,
        "lambda_L": lambda_L,
        "lambda_A": lambda_A,
        "area_m2": area_m2,
        "area_cm2": area_m2 * 10000.0,
        "brazo_m": arm_m,
        "brazo_mm": arm_m * 1000.0,
        "fuerza_n": force_n,
        "momento_nm": moment_nm,
    }


def run_full_parametric_sweep(
    velocities_kmh: List[float] = VELOCITIES_KMH,
    rho: float = RHO_STD_KG_M3,
    mass_targets_kg: List[float] = MASS_TARGETS_KG,
    cp_values: List[float] = CP_DIFFERENTIAL_VALUES,
    area_ref_m2: float = HIPOTETICO_AREA_REF_M2,
    arm_ref_m: float = HIPOTETICO_ARM_REF_M,
    ref_mass_kg: float = REF_MASS_KG,
) -> List[Dict[str, Any]]:
    """
    Ejecuta el barrido paramétrico completo cruzando velocidades, masas objetivo y Cp.
    """
    results = []
    for v_kmh in velocities_kmh:
        for m_kg in mass_targets_kg:
            for cp in cp_values:
                record = run_parametric_case(
                    v_kmh=v_kmh,
                    rho=rho,
                    mass_target_kg=m_kg,
                    cp_diff=cp,
                    area_ref_m2=area_ref_m2,
                    arm_ref_m=arm_ref_m,
                    ref_mass_kg=ref_mass_kg,
                )
                results.append(record)
    return results


# =============================================================================
# EXPORTACIÓN DE TABLAS Y RESULTADOS
# =============================================================================

def export_to_csv(results: List[Dict[str, Any]], filepath: Path) -> None:
    """
    Exporta la lista de registros a archivo CSV.
    """
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def export_to_json(results: List[Dict[str, Any]], filepath: Path) -> None:
    """
    Exporta los resultados a formato JSON estructurado con metadatos explícitos.
    """
    output_data = {
        "estudio": "analisis_parametrico_cargas_compuerta",
        "descripcion": "Cargas aerodinámicas ilustrativas bajo distribución uniforme supuesta y escalado geométrico",
        "advertencia_critica": (
            "q no es presion diferencial uniforme. Las compuertas estan disenadas para baja velocidad. "
            "Ninguna carga real ni mecanismo instalado esta validado."
        ),
        "constantes_referencia": {
            "rho_kg_m3": RHO_STD_KG_M3,
            "masa_referencia_kg": REF_MASS_KG,
            "area_referencia_hipotetica_m2": HIPOTETICO_AREA_REF_M2,
            "brazo_referencia_hipotetico_m": HIPOTETICO_ARM_REF_M,
            "diametro_conducto_ref_m": BORE_DIAMETER_REF_M,
        },
        "conteo_casos": len(results),
        "casos": results,
    }
    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


def export_to_markdown_tables(results: List[Dict[str, Any]], filepath: Path) -> None:
    """
    Genera un archivo Markdown con tablas agrupadas por velocidad y masa.
    """
    lines = []
    lines.append("# Tablas de Análisis Paramétrico de Cargas en Compuerta")
    lines.append("")
    lines.append("> **NOTA METODOLÓGICA Y LIMITACIONES**:")
    lines.append("> 1. Los valores de fuerza $F$ y momento $M$ se obtienen asumiendo $\\Delta p = C_{p,\\text{dif}} \\cdot q$ **estrictamente uniforme** sobre toda el área.")
    lines.append("> 2. Las áreas $A$ y brazos $L$ son **EXPLÍCITAMENTE HIPOTÉTICOS** y están escalados geométricamente con $(m/5)^{1/3}$.")
    lines.append("> 3. La presión dinámica $q$ **NO** es una presión diferencial uniforme real.")
    lines.append("> 4. Las tapas son para **baja velocidad / despegue / transición**; no están validadas para vuelo a 600 ni a 1000 km/h.")
    lines.append("> 5. **Ningún actuador, soporte ni mecanismo instalado está resuelto ni validado.**")
    lines.append("")

    # Separar por velocidad
    velocities = sorted(list(set(r["velocidad_kmh"] for r in results)))
    masses = sorted(list(set(r["masa_objetivo_kg"] for r in results)))

    for v in velocities:
        v_ms = kmh_to_ms(v)
        q = dynamic_pressure(RHO_STD_KG_M3, v_ms)
        lines.append(f"## Condición de Vuelo Hipotética: $V = {v:.0f}$ km/h ({v_ms:.2f} m/s)")
        lines.append(f"- **Densidad $\\rho$**: {RHO_STD_KG_M3:.3f} kg/m³")
        lines.append(f"- **Presión dinámica $q$**: {q:.2f} Pa ({q/1000.0:.3f} kPa)")
        lines.append("")

        for m in masses:
            cases_vm = [r for r in results if r["velocidad_kmh"] == v and r["masa_objetivo_kg"] == m]
            if not cases_vm:
                continue
            first = cases_vm[0]
            lines.append(f"### Variante de Masa Objetivo: {m:.1f} kg")
            lines.append(f"- Factor lineal $\\lambda_L$: `{first['lambda_L']:.4f}` | Factor área $\\lambda_A$: `{first['lambda_A']:.4f}`")
            lines.append(f"- Área supuesta $A$: `{first['area_m2']:.6f}` m² ({first['area_cm2']:.2f} cm²)")
            lines.append(f"- Brazo supuesto $L$: `{first['brazo_m']:.4f}` m ({first['brazo_mm']:.2f} mm)")
            lines.append("")
            lines.append("| $C_{p,\\text{dif}}$ [-] | $\\Delta p$ [Pa] | $\\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |")
            lines.append("| :---: | :---: | :---: | :---: | :---: | :---: |")
            for r in cases_vm:
                cp = r["cp_diferencial"]
                dp_pa = r["delta_p_pa"]
                dp_kpa = dp_pa / 1000.0
                fn = r["fuerza_n"]
                f_kgf = fn / 9.80665
                mnm = r["momento_nm"]
                lines.append(f"| {cp:.2f} | {dp_pa:10.1f} | {dp_kpa:8.3f} | {fn:9.2f} | {f_kgf:7.2f} | {mnm:8.3f} |")
            lines.append("")

    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

def main():
    salidas_dir = Path(__file__).resolve().parent
    salidas_dir.mkdir(parents=True, exist_ok=True)

    print("===============================================================================")
    print("ANÁLISIS PARAMÉTRICO DE CARGAS DE COMPUERTA — ARQUITECTURA A")
    print("===============================================================================")
    print(f"Directorio de entrega: {salidas_dir}")
    print(f"Densidad de referencia: {RHO_STD_KG_M3} kg/m³")
    print(f"Velocidades analizadas: {VELOCITIES_KMH} km/h")
    print(f"Masas objetivo: {MASS_TARGETS_KG} kg (Referencia: {REF_MASS_KG} kg)")
    print(f"Área supuesta referencia (5 kg): {HIPOTETICO_AREA_REF_M2} m² ({HIPOTETICO_AREA_REF_M2 * 10000} cm²)")
    print(f"Brazo supuesto referencia (5 kg): {HIPOTETICO_ARM_REF_M} m ({HIPOTETICO_ARM_REF_M * 1000} mm)")
    print("-------------------------------------------------------------------------------")

    # Ejecutar barrido
    results = run_full_parametric_sweep()
    print(f"Total de casos calculados: {len(results)}")

    # Archivos de salida
    csv_path = salidas_dir / "tablas_cargas_compuerta.csv"
    json_path = salidas_dir / "resultados_cargas_compuerta.json"
    md_path = salidas_dir / "tablas_cargas_compuerta.md"

    export_to_csv(results, csv_path)
    print(f"Exportado CSV: {csv_path.name} ({len(results)} filas)")

    export_to_json(results, json_path)
    print(f"Exportado JSON: {json_path.name}")

    export_to_markdown_tables(results, md_path)
    print(f"Exportado Markdown: {md_path.name}")

    # Resumen rápido de q
    v600_ms = kmh_to_ms(600.0)
    q600 = dynamic_pressure(RHO_STD_KG_M3, v600_ms)
    v1000_ms = kmh_to_ms(1000.0)
    q1000 = dynamic_pressure(RHO_STD_KG_M3, v1000_ms)

    print("-------------------------------------------------------------------------------")
    print(f"Verificación q a 600 km/h:  V = {v600_ms:.4f} m/s  ->  q = {q600:.2f} Pa")
    print(f"Verificación q a 1000 km/h: V = {v1000_ms:.4f} m/s ->  q = {q1000:.2f} Pa (~47261 Pa)")
    print("===============================================================================")


if __name__ == "__main__":
    main()
