#!/usr/bin/env python3
"""
Módulo de cálculo de matriz de sensibilidad para la condición cinemática:
    c_min = (Re_min * nu) / (M_lim * a)

Parámetros físicos supuestos:
    nu = 1.46e-5 m^2/s  (viscosidad cinemática del aire)
    a  = 340.3 m/s       (velocidad del sonido en aire)

Datos experimentales de entrada:
    Bloques combinados del archivo SD8020.DRG (UIUC LSAT Vol. 1)
    Reynolds medios: [61400, 101500, 203300, 304800]

Límites de Mach de cribado operacional:
    M_lim in [0.2, 0.3, 0.4]
"""

import os
import re
import csv
import json
from typing import List, Dict, Any, Tuple

DEFAULT_NU = 1.46e-5    # m^2/s
DEFAULT_A = 340.3       # m/s
DEFAULT_MACH_LIMITS = [0.2, 0.3, 0.4]
DEFAULT_RE_LIST = [61400, 101500, 203300, 304800]


def parse_reynolds_from_drg(file_path: str) -> List[int]:
    """
    Extrae los números de Reynolds medios reportados en los bloques de un archivo .DRG.
    
    Args:
        file_path: Ruta al archivo .DRG.
        
    Returns:
        Lista de enteros con los valores de Reynolds en orden de aparición.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
    re_values = []
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "Average Reynolds #:" in line:
            # El valor del Reynolds está en la línea siguiente (o a veces en la misma)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                val_str = lines[j].strip()
                # Extraer números
                match = re.search(r"(\d+)", val_str)
                if match:
                    re_values.append(int(match.group(1)))
            i = j
        i += 1
        
    if not re_values:
        raise ValueError(f"No se pudieron extraer números de Reynolds de {file_path}")
        
    return re_values


def compute_c_min(re_min: float, m_lim: float, nu: float = DEFAULT_NU, a: float = DEFAULT_A) -> float:
    """
    Calcula la cuerda mínima requerida por la condición cinemática combinada:
        Re >= Re_min  y  M <= M_lim
        => c >= (Re_min * nu) / (M_lim * a)
        
    Args:
        re_min: Número de Reynolds mínimo admisible [-]
        m_lim: Límite superior de número de Mach de cribado [-]
        nu: Viscosidad cinemática [m^2/s]
        a: Velocidad del sonido [m/s]
        
    Returns:
        c_min en metros [m]
    """
    if m_lim <= 0:
        raise ValueError("M_lim debe ser estrictamente positivo.")
    if re_min <= 0:
        raise ValueError("Re_min debe ser estrictamente positivo.")
    if nu <= 0 or a <= 0:
        raise ValueError("nu y a deben ser estrictamente positivos.")
        
    return (re_min * nu) / (m_lim * a)


def verify_benchmark_example(nu: float = DEFAULT_NU, a: float = DEFAULT_A) -> Dict[str, Any]:
    """
    Reproduce y valida el ejemplo canónico de referencia:
        Re = 61400, M_lim = 0.3
        Resultado esperado: 8.781 mm (0.008781 m)
    """
    c_m = compute_c_min(61400, 0.3, nu=nu, a=a)
    c_mm = c_m * 1000.0
    c_mm_rounded = round(c_mm, 3)
    matches_target = (c_mm_rounded == 8.781)
    
    return {
        "re_min": 61400,
        "m_lim": 0.3,
        "nu_m2_s": nu,
        "a_m_s": a,
        "c_min_m": c_m,
        "c_min_mm": c_mm,
        "c_min_mm_rounded_3dec": c_mm_rounded,
        "expected_mm": 8.781,
        "absolute_diff_mm": abs(c_mm - 8.781),
        "matches_expected_3dec": matches_target
    }


def compute_sensitivity_matrix(
    re_list: List[int],
    m_list: List[float],
    nu: float = DEFAULT_NU,
    a: float = DEFAULT_A
) -> List[Dict[str, Any]]:
    """
    Calcula la matriz completa de sensibilidad cinemática y sus derivadas analíticas.
    
    Derivadas y elasticidades:
        d(c_min)/d(Re) = nu / (M_lim * a)      [m / unit_Re]
        d(c_min)/d(M)  = - c_min / M_lim        [m / unit_M]
        Elasticidad E_Re = (d c_min / c_min) / (d Re / Re) = +1
        Elasticidad E_M  = (d c_min / c_min) / (d M / M)   = -1
    """
    records = []
    for re_val in re_list:
        for m_val in m_list:
            c_m = compute_c_min(re_val, m_val, nu=nu, a=a)
            c_mm = c_m * 1000.0
            w_max = m_val * a  # Velocidad relativa máxima admisible [m/s]
            
            # Sensibilidades analíticas
            dc_dre = nu / (m_val * a)              # [m / unit_Re]
            dc_dm = - c_m / m_val                  # [m / unit_M]
            dc_dre_mm = dc_dre * 1000.0            # [mm / unit_Re]
            dc_dm_mm = dc_dm * 1000.0              # [mm / unit_M]
            
            records.append({
                "re_min": re_val,
                "m_lim": m_val,
                "nu_m2_s": nu,
                "a_m_s": a,
                "w_max_m_s": round(w_max, 4),
                "c_min_m": c_m,
                "c_min_mm": round(c_mm, 4),
                "c_min_mm_display_3dec": round(c_mm, 3),
                "dc_dre_m": dc_dre,
                "dc_dre_mm": dc_dre_mm,
                "dc_dm_m": dc_dm,
                "dc_dm_mm": dc_dm_mm,
                "elasticidad_re": 1.0,
                "elasticidad_m": -1.0
            })
    return records


def export_csv_matrix(
    records: List[Dict[str, Any]],
    output_path: str,
    pivot_path: str = None
) -> None:
    """
    Exporta la matriz de sensibilidad en formato CSV detallado (tidy) y opcionalmente pivoteada.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # CSV detallado (formato ordenado/tidy para análisis)
    fieldnames = [
        "re_min",
        "m_lim",
        "nu_m2_s",
        "a_m_s",
        "w_max_m_s",
        "c_min_m",
        "c_min_mm",
        "c_min_mm_display_3dec",
        "dc_dre_m",
        "dc_dre_mm",
        "dc_dm_m",
        "dc_dm_mm",
        "elasticidad_re",
        "elasticidad_m"
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow(row)
            
    # Si se pide vista pivoteada en archivo separado
    if pivot_path:
        # Extraer filas (Re) y columnas (M)
        re_vals = sorted(list(set(r["re_min"] for r in records)))
        m_vals = sorted(list(set(r["m_lim"] for r in records)))
        
        lookup = {(r["re_min"], r["m_lim"]): r["c_min_mm_display_3dec"] for r in records}
        
        with open(pivot_path, 'w', newline='', encoding='utf-8') as f:
            pivot_writer = csv.writer(f)
            header = ["Re_min \\ M_lim"] + [f"M={m:.1f} (c_min [mm])" for m in m_vals]
            pivot_writer.writerow(header)
            for re_val in re_vals:
                row_data = [str(re_val)] + [f"{lookup[(re_val, m)]:.3f}" for m in m_vals]
                pivot_writer.writerow(row_data)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    drg_path = os.path.join(base_dir, "entradas", "investigacion-aeronautica", "fuentes", "uiuc", "SD8020.DRG")
    salidas_dir = os.path.join(base_dir, "salidas")
    os.makedirs(salidas_dir, exist_ok=True)
    
    # 1. Obtener Reynolds de los bloques DRG
    if os.path.exists(drg_path):
        re_list = parse_reynolds_from_drg(drg_path)
        print(f"[OK] Reynolds extraidos de SD8020.DRG: {re_list}")
    else:
        re_list = DEFAULT_RE_LIST
        print(f"[WARN] Archivo DRG no encontrado en {drg_path}, usando lista por defecto: {re_list}")
        
    mach_list = DEFAULT_MACH_LIMITS
    
    # 2. Verificar ejemplo de referencia
    bm = verify_benchmark_example(DEFAULT_NU, DEFAULT_A)
    print(f"[OK] Benchmark Re={bm['re_min']}, M={bm['m_lim']}: c_min={bm['c_min_mm_rounded_3dec']} mm (esperado: {bm['expected_mm']} mm, match={bm['matches_expected_3dec']})")
    
    # 3. Calcular matriz de sensibilidad
    records = compute_sensitivity_matrix(re_list, mach_list, nu=DEFAULT_NU, a=DEFAULT_A)
    
    # 4. Exportar CSV
    csv_tidy_path = os.path.join(salidas_dir, "matriz_sensibilidad_cmin.csv")
    csv_pivot_path = os.path.join(salidas_dir, "matriz_sensibilidad_cmin_tabla.csv")
    export_csv_matrix(records, csv_tidy_path, csv_pivot_path)
    print(f"[OK] CSV detallado generado en: {csv_tidy_path}")
    print(f"[OK] CSV tabla pivote generada en: {csv_pivot_path}")
    
    # 5. Exportar JSON de metadatos y resultados
    json_path = os.path.join(salidas_dir, "matriz_sensibilidad_resumen.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "parametros_supuestos": {
                "nu_m2_s": DEFAULT_NU,
                "a_m_s": DEFAULT_A,
                "descripcion": "Aire estándar ISA aproximado a nivel del mar"
            },
            "datos_medidos_fuente": {
                "archivo": "entradas/investigacion-aeronautica/fuentes/uiuc/SD8020.DRG",
                "perfil": "SD8020",
                "bloques_reynolds": re_list
            },
            "elecciones_mach": {
                "valores": mach_list,
                "naturaleza": "Criterio de cribado operacional de ingeniería (no límite físico universal)"
            },
            "benchmark_verificacion": bm,
            "matriz_sensibilidad": records
        }, f, indent=2, ensure_ascii=False)
    print(f"[OK] Resumen JSON generado en: {json_path}")


if __name__ == "__main__":
    main()
