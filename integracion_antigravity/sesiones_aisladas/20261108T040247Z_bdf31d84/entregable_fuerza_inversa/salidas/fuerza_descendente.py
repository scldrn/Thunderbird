#!/usr/bin/env python3
"""
fuerza_descendente.py
---------------------
Módulo de cálculo y verificación de la fuerza propulsora descendente
necesaria a actitud fija bajo gravedad constante y sin otras fuerzas externas.

Modelo analítico:
  Frev_total >= max(0.0, m * g * (n - 1.0))
  Frev_modulo = Frev_total / num_modulos

Unidades del Sistema Internacional (SI):
  Masa (m): kg
  Gravedad (g): m/s^2
  Aceleración neta descendente (a_desc): m/s^2 (a_desc = n * g)
  Factor de carga vertical (n): adimensional
  Fuerza (F): Newton (N)
"""

import sys
import os
import csv
import json
from typing import Dict, List, Tuple, Any

# Constantes físicas de referencia
G0_STANDARD = 9.80665   # m/s^2 (ISO 80000-3 / WGS-84, gravedad estándar de referencia)
G_APPROX = 9.81         # m/s^2 (aproximación didáctica de uso común)

# Conjuntos de parámetros del estudio
MASAS_KG = [2.0, 5.0, 10.0]
FACTORES_N = [1.2, 2.0, 5.0]
NUM_MODULOS_DEFAULT = 4

# Cotas geométricas de referencia previa (C02 / Arquitectura A)
DX_REF_M = 0.160  # m (semidistancia longitudinal de las estaciones propulsoras)
DY_REF_M = 0.076  # m (semidistancia transversal de las estaciones propulsoras)


def calcular_fuerza_descendente_total(m: float, n: float, g: float = G0_STANDARD) -> float:
    """
    Calcula la fuerza propulsora descendente total mínima requerida:
      Frev_total = max(0.0, m * g * (n - 1.0))

    Parámetros:
      m: Masa de la aeronave [kg] (m > 0)
      n: Factor de aceleración neta descendente [adimensional] (a_desc = n * g)
      g: Aceleración gravitatoria [m/s^2] (por defecto G0_STANDARD = 9.80665 m/s^2)

    Retorna:
      Fuerza propulsora descendente total Frev_total [N].
      Si n <= 1.0, la gravedad por sí sola iguala o excede la aceleración deseada,
      por lo que la fuerza descendente activa requerida es 0.0 N.
    """
    if m <= 0:
        raise ValueError(f"La masa debe ser estrictamente positiva (recibido m={m})")
    if g <= 0:
        raise ValueError(f"La aceleración de gravedad debe ser positiva (recibido g={g})")
    
    demanda = m * g * (n - 1.0)
    return max(0.0, demanda)


def calcular_fuerza_descendente_modulo(
    m: float,
    n: float,
    g: float = G0_STANDARD,
    num_modulos: int = NUM_MODULOS_DEFAULT
) -> float:
    """
    Calcula la fuerza propulsora descendente por módulo asumiendo reparto uniforme
    entre actuadores idénticos con CG simétrico:
      Frev_modulo = Frev_total / num_modulos

    Parámetros:
      m: Masa de la aeronave [kg]
      n: Factor de aceleración descendente [adimensional]
      g: Aceleración gravitatoria [m/s^2]
      num_modulos: Número de módulos propulsores (entero > 0, por defecto 4)

    Retorna:
      Fuerza descendente requerida por módulo [N].
    """
    if num_modulos <= 0:
        raise ValueError(f"num_modulos debe ser un entero positivo (recibido {num_modulos})")
    
    f_total = calcular_fuerza_descendente_total(m, n, g)
    return f_total / float(num_modulos)


def calcular_demanda_cg_excentrico(
    m: float,
    n: float,
    x_cg: float,
    y_cg: float,
    dx: float = DX_REF_M,
    dy: float = DY_REF_M,
    g: float = G0_STANDARD,
    num_modulos: int = NUM_MODULOS_DEFAULT
) -> Dict[str, float]:
    """
    Evalúa la amplificación de demanda sobre el módulo crítico ante un centro de gravedad
    excéntrico (x_cg, y_cg) en una disposición rectangular de 4 módulos en (+-dx, +-dy).

    Ecuación de asignación plana con momentos nulos:
      R_critico = (Frev_total / 4) * (1 + |x_cg| / dx + |y_cg| / dy)
    """
    f_tot = calcular_fuerza_descendente_total(m, n, g)
    r_sim = f_tot / float(num_modulos)
    factor_amplificacion = 1.0 + (abs(x_cg) / dx) + (abs(y_cg) / dy)
    r_critico = r_sim * factor_amplificacion
    
    return {
        "f_total_N": f_tot,
        "r_simetrico_N": r_sim,
        "factor_amplificacion": factor_amplificacion,
        "r_critico_N": r_critico,
        "x_cg_m": x_cg,
        "y_cg_m": y_cg,
        "dx_m": dx,
        "dy_m": dy
    }


def generar_tabla_escenarios(
    masas: List[float] = MASAS_KG,
    factores_n: List[float] = FACTORES_N,
    g: float = G0_STANDARD,
    g_comp: float = G_APPROX,
    num_modulos: int = NUM_MODULOS_DEFAULT
) -> List[Dict[str, Any]]:
    """
    Genera el conjunto sistemático de resultados para las combinaciones de masas
    y factores de carga vertical descendente.
    """
    filas = []
    for m in masas:
        peso_w = m * g
        for n in factores_n:
            n_minus_1 = n - 1.0
            a_desc = n * g
            f_tot = calcular_fuerza_descendente_total(m, n, g)
            f_mod = calcular_fuerza_descendente_modulo(m, n, g, num_modulos)
            f_mod_kgf = f_mod / g
            f_tot_kgf = f_tot / g
            
            # Valor comparativo con g = 9.81 m/s^2
            f_tot_comp = calcular_fuerza_descendente_total(m, n, g_comp)
            f_mod_comp = calcular_fuerza_descendente_modulo(m, n, g_comp, num_modulos)
            
            # Ratio respecto a la cuarta parte del peso estático (W / num_modulos)
            w_cuartos = peso_w / float(num_modulos)
            ratio_w = f_mod / w_cuartos if w_cuartos > 0 else 0.0
            
            filas.append({
                "m_kg": float(m),
                "n": float(n),
                "n_minus_1": round(n_minus_1, 4),
                "a_desc_ms2": round(a_desc, 5),
                "peso_W_N": round(peso_w, 5),
                "f_rev_total_N": round(f_tot, 5),
                "f_rev_total_kgf": round(f_tot_kgf, 5),
                "f_rev_modulo_N": round(f_mod, 6),
                "f_rev_modulo_redondeado_3dec": round(f_mod, 3),
                "f_rev_modulo_kgf": round(f_mod_kgf, 5),
                "f_rev_modulo_g981_N": round(f_mod_comp, 6),
                "ratio_f_mod_sobre_w_cuartos": round(ratio_w, 4)
            })
    return filas


def exportar_csv(ruta_csv: str, filas: List[Dict[str, Any]]) -> None:
    """Exporta las filas evaluadas a un archivo CSV."""
    if not filas:
        return
    campos = list(filas[0].keys())
    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for r in filas:
            writer.writerow(r)


def exportar_json(ruta_json: str, datos: Dict[str, Any]) -> None:
    """Exporta el reporte analítico completo a formato JSON."""
    with open(ruta_json, mode="w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def ejecutar_analisis_completo(directorio_salida: str = ".") -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Ejecuta el análisis completo y genera los archivos tabla_fuerza_descendente.csv
    y resultados_resumen.json dentro del directorio especificado (usando rutas relativas).
    """
    filas = generar_tabla_escenarios(MASAS_KG, FACTORES_N, G0_STANDARD, G_APPROX, NUM_MODULOS_DEFAULT)
    
    # Análisis del caso testigo específico: 5 kg, 2g
    f_tot_5kg_2g = calcular_fuerza_descendente_total(5.0, 2.0, G0_STANDARD)
    f_mod_5kg_2g = calcular_fuerza_descendente_modulo(5.0, 2.0, G0_STANDARD, 4)
    f_mod_5kg_2g_3dec = round(f_mod_5kg_2g, 3)
    
    # Análisis de sensibilidad de CG excéntrico
    escenario_cg = calcular_demanda_cg_excentrico(
        m=5.0, n=2.0, x_cg=0.040, y_cg=0.0, dx=DX_REF_M, dy=DY_REF_M, g=G0_STANDARD, num_modulos=4
    )
    
    resumen = {
        "metadatos": {
            "formula_fuerza_total": "Frev_total >= max(0.0, m * g * (n - 1.0))",
            "formula_fuerza_modulo": "Frev_modulo = Frev_total / 4",
            "g0_estandar_ms2": G0_STANDARD,
            "g_didactica_ms2": G_APPROX,
            "num_modulos": NUM_MODULOS_DEFAULT,
            "masas_evaluadas_kg": MASAS_KG,
            "factores_n_evaluados": FACTORES_N
        },
        "caso_testigo_5kg_2g": {
            "m_kg": 5.0,
            "n": 2.0,
            "f_rev_total_N": f_tot_5kg_2g,
            "f_rev_modulo_exacta_N": f_mod_5kg_2g,
            "f_rev_modulo_3dec_N": f_mod_5kg_2g_3dec,
            "verificacion_esperado_12_258": (f_mod_5kg_2g_3dec == 12.258)
        },
        "sensibilidad_cg_excentrico": escenario_cg,
        "tabla_escenarios": filas
    }
    
    ruta_csv = os.path.join(directorio_salida, "tabla_fuerza_descendente.csv")
    ruta_json = os.path.join(directorio_salida, "resultados_resumen.json")
    
    exportar_csv(ruta_csv, filas)
    exportar_json(ruta_json, resumen)
    
    return filas, resumen


if __name__ == "__main__":
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    filas, resumen = ejecutar_analisis_completo(dir_actual)
    
    print("=" * 80)
    print("VERIFICACIÓN DE FUERZA DESCENDENTE A ACTITUD FIJA")
    print(f"Gravedad estándar g0 = {G0_STANDARD} m/s^2 | Actuadores N = {NUM_MODULOS_DEFAULT}")
    print("=" * 80)
    print(f"{'Masa [kg]':<10} {'n':<6} {'a_desc [m/s²]':<15} {'Frev_tot [N]':<15} {'Frev_mod [N]':<15} {'Frev_mod [kgf]':<15}")
    print("-" * 80)
    for r in filas:
        print(f"{r['m_kg']:<10.1f} {r['n']:<6.1f} {r['a_desc_ms2']:<15.4f} {r['f_rev_total_N']:<15.4f} {r['f_rev_modulo_N']:<15.4f} ({r['f_rev_modulo_kgf']:<5.2f} kgf)")
    print("-" * 80)
    caso = resumen["caso_testigo_5kg_2g"]
    print(f"Caso testigo 5 kg, 2g: Frev_total = {caso['f_rev_total_N']:.5f} N | Por módulo = {caso['f_rev_modulo_exacta_N']:.6f} N -> Redondeado = {caso['f_rev_modulo_3dec_N']:.3f} N (Coincide con 12.258 N: {caso['verificacion_esperado_12_258']})")
    print("=" * 80)
