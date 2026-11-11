#!/usr/bin/env python3
"""
generar_tablas.py - Generación de tablas comparativas de escenarios hipotéticos
entre el modelo de disco actuador y el modelo previo de eficiencia constante.

Genera:
- salidas/comparacion_escenarios.csv: Matriz completa de escenarios variando
  velocidad, tiempo de aceleración y arrastre final.
- salidas/sensibilidad_area.csv: Estudio de sensibilidad al área y diámetro del disco.
- salidas/resumen_escenarios.json: Archivo estructurado con todos los casos y métricas.
"""

import math
import csv
import json
from typing import List, Dict, Any

from modelo_disco import evaluate_scenario, exact_work_accel, previous_model_work


def generar_matriz_escenarios() -> List[Dict[str, Any]]:
    """
    Genera la matriz principal de escenarios para la aeronave supuesta de m = 5.0 kg
    con disco de referencia de d = 0.25 m (A = 0.049087 m^2).
    """
    m = 5.0
    rho = 1.225
    d = 0.25
    A = math.pi * (d / 2.0) ** 2
    eta_prev = 0.70
    eta_disk_profile = 0.70

    velocidades_kmh = [100.0, 300.0, 600.0, 1000.0]
    tiempos_s = [10.0, 30.0, 60.0]
    arrastres_N = [0.0, 10.0, 25.0, 50.0]

    resultados = []
    for V_kmh in velocidades_kmh:
        V_mps = V_kmh / 3.6
        for t in tiempos_s:
            for D in arrastres_N:
                res = evaluate_scenario(
                    m=m,
                    V_final=V_mps,
                    t_accel=t,
                    D_final=D,
                    rho=rho,
                    A=A,
                    eta_prev=eta_prev,
                    eta_disk_profile=eta_disk_profile
                )
                resultados.append(res)
    return resultados


def generar_sensibilidad_area() -> List[Dict[str, Any]]:
    """
    Analiza la sensibilidad del trabajo y la potencia al diámetro del disco actuador
    para los casos emblemáticos a 600 km/h y 1000 km/h con t = 60 s y D = 50 N.
    """
    m = 5.0
    rho = 1.225
    eta_prev = 0.70
    eta_disk_profile = 0.70
    diametros_m = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]

    casos_emblematicos = [
        (600.0, 60.0, 50.0),
        (1000.0, 60.0, 50.0),
        (300.0, 30.0, 25.0),
        (100.0, 10.0, 10.0)
    ]

    registros = []
    for V_kmh, t, D in casos_emblematicos:
        V_mps = V_kmh / 3.6
        for d in diametros_m:
            A = math.pi * (d / 2.0) ** 2
            res = evaluate_scenario(
                m=m,
                V_final=V_mps,
                t_accel=t,
                D_final=D,
                rho=rho,
                A=A,
                eta_prev=eta_prev,
                eta_disk_profile=eta_disk_profile
            )
            registros.append(res)
    return registros


def exportar_csv_principal(registros: List[Dict[str, Any]], ruta: str):
    """Exporta los escenarios principales a formato CSV."""
    campos = [
        "V_final_kmh",
        "Mach_final",
        "t_accel_s",
        "D_final_N",
        "T_inicial_N",
        "T_final_N",
        "vi_estatica_mps",
        "vi_final_mps",
        "P_estatica_ideal_W",
        "P_estatica_prev_W",
        "P_final_ideal_kW",
        "P_final_prev_kW",
        "W_util_kJ",
        "W_prev_kJ",
        "W_disco_ideal_kJ",
        "W_inducido_kJ",
        "W_disco_real_kJ",
        "ratio_W_ideal_prev",
        "ratio_W_disco_real_prev",
        "eficiencia_Froude_final"
    ]

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(campos)
        for r in registros:
            writer.writerow([
                f"{r['V_final_kmh']:.1f}",
                f"{r['Mach_final']:.3f}",
                f"{r['t_accel_s']:.1f}",
                f"{r['D_final_N']:.1f}",
                f"{r['T_initial_N']:.2f}",
                f"{r['T_final_N']:.2f}",
                f"{r['vi_static_mps']:.2f}",
                f"{r['vi_final_mps']:.2f}",
                f"{r['P_static_ideal_W']:.1f}",
                f"{r['P_static_prev_W']:.1f}",
                f"{r['P_final_ideal_W'] / 1e3:.2f}",
                f"{r['P_final_prev_W'] / 1e3:.2f}",
                f"{r['W_useful_J'] / 1e3:.2f}",
                f"{r['W_prev_J'] / 1e3:.2f}",
                f"{r['W_ideal_exact_J'] / 1e3:.2f}",
                f"{r['W_induced_J'] / 1e3:.2f}",
                f"{r['W_disk_actual_J'] / 1e3:.2f}",
                f"{r['ratio_ideal_to_prev']:.3f}",
                f"{r['ratio_disk_actual_to_prev']:.3f}",
                f"{r['froude_efficiency_final']:.3f}"
            ])


def exportar_csv_sensibilidad(registros: List[Dict[str, Any]], ruta: str):
    """Exporta el análisis de sensibilidad a diámetro/área."""
    campos = [
        "V_final_kmh",
        "t_accel_s",
        "D_final_N",
        "diametro_m",
        "area_m2",
        "P_estatica_ideal_W",
        "vi_estatica_mps",
        "W_disco_ideal_kJ",
        "W_inducido_kJ",
        "W_prev_kJ",
        "ratio_ideal_prev"
    ]

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(campos)
        for r in registros:
            writer.writerow([
                f"{r['V_final_kmh']:.1f}",
                f"{r['t_accel_s']:.1f}",
                f"{r['D_final_N']:.1f}",
                f"{r['diameter_m']:.2f}",
                f"{r['A_m2']:.4f}",
                f"{r['P_static_ideal_W']:.1f}",
                f"{r['vi_static_mps']:.2f}",
                f"{r['W_ideal_exact_J'] / 1e3:.2f}",
                f"{r['W_induced_J'] / 1e3:.2f}",
                f"{r['W_prev_J'] / 1e3:.2f}",
                f"{r['ratio_ideal_to_prev']:.3f}"
            ])


def main():
    print("=== GENERACIÓN DE TABLAS Y ESCENARIOS COMPARATIVOS ===")
    escenarios = generar_matriz_escenarios()
    csv_principal = "salidas/comparacion_escenarios.csv"
    exportar_csv_principal(escenarios, csv_principal)
    print(f"Exportados {len(escenarios)} escenarios a {csv_principal}")

    sensibilidad = generar_sensibilidad_area()
    csv_sens = "salidas/sensibilidad_area.csv"
    exportar_csv_sensibilidad(sensibilidad, csv_sens)
    print(f"Exportados {len(sensibilidad)} casos de sensibilidad a {csv_sens}")

    # Exportar JSON estructurado
    json_path = "salidas/resumen_escenarios.json"
    resumen = {
        "descripcion": "Comparación paramétrica del modelo de disco actuador aislado no ductado vs modelo previo de eficiencia constante",
        "supuestos_fijos": {
            "masa_aeronave_kg": 5.0,
            "densidad_aire_ISA_kgm3": 1.225,
            "velocidad_sonido_ref_mps": 340.294,
            "diametro_disco_base_m": 0.25,
            "area_disco_base_m2": math.pi * (0.25 / 2.0) ** 2,
            "eficiencia_modelo_previo": 0.70,
            "eficiencia_perfil_disco_supuesta": 0.70,
            "fuente_modelo_previo": "entradas/investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/INFORME.md"
        },
        "total_escenarios": len(escenarios),
        "total_sensibilidad": len(sensibilidad),
        "muestras_destacadas": [
            r for r in escenarios if r["V_final_kmh"] in [600.0, 1000.0] and r["t_accel_s"] == 60.0 and r["D_final_N"] in [0.0, 50.0]
        ]
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2)
    print(f"Resumen estructurado exportado a {json_path}")


if __name__ == "__main__":
    main()
