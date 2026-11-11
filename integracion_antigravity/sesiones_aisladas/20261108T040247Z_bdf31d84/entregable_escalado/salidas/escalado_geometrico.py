#!/usr/bin/env python3
"""
escalado_geometrico.py
----------------------
Cálculo de escalado geométrico semejante (D proporcional a m^(1/3)) para
objetivos de masa condicionales de 2 kg, 5 kg y 10 kg, a partir del rotor
aerodinámico D82 (diámetro 82 mm, radio BEM nominal 41 mm) del caso de
referencia de 5 kg (C02_CANDIDATA).

Paquete autocontenido y reproducible:
  - Rutas resueltas respecto a __file__.
  - Fuentes de datos locales en datos/.

Modelo físico:
  - 4 discos actuadores abiertos ideales aislados con carga axial simétrica.
  - Teoría de cantidad de movimiento unidimensional (Rankine-Froude) en flujo incompresible cuasiestacionario.
  - Parámetros atmosféricos estándar de referencia: rho = 1.225 kg/m^3, g = 9.80665 m/s^2.
  - Estacionario puro (hover, aceleración neta 0 g) y aceleraciones dinámicas (0.5 g, 1.0 g).

ADVERTENCIAS Y DELIMITACIÓN DE ALCANCE:
  - Este modelo representa un escalado matemático condicional sobre discos ideales abiertos.
  - NO representa la potencia eléctrica instalada ni el consumo real del propulsor.
  - NO constituye un diseño aceptado o validado de ninguna escala (las variantes de 2 kg
    y 10 kg son 'pending_own_configuration' y 5 kg es 'partial_CAD_candidate' no calificado).
  - D84 (84 mm) es otra hipótesis de referencia que toma el diámetro del conducto (bore)
    en lugar del diámetro del rotor giratorio (D82 = 82 mm).
  - NO se declara regla universal de límite para ventiladores entubados (el conducto puede
    alterar la potencia inducida teórica mediante succión de labio y difusión, mientras que
    las pérdidas disipativas reales aumentan notablemente la potencia real demandada).
"""

import math
import json
import csv
import os
from typing import Dict, List, Any


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.join(SCRIPT_DIR, "datos")


def get_default_paths() -> Dict[str, str]:
    """Retorna las rutas canónicas locales relativas a __file__."""
    return {
        "json_path": os.path.join(DEFAULT_DATA_DIR, "C02_CANDIDATA.json"),
        "csv_path": os.path.join(DEFAULT_DATA_DIR, "REFERENCIA_DISCO.csv")
    }


def load_reference_inputs(
    json_path: str = None,
    csv_path: str = None
) -> Dict[str, Any]:
    """
    Carga los parámetros canónicos desde las copias locales en datos/
    usando rutas relativas a __file__.
    """
    defaults = get_default_paths()
    if json_path is None:
        json_path = defaults["json_path"]
    if csv_path is None:
        csv_path = defaults["csv_path"]

    # Fallback transparente si se ejecuta desde raíz sin datos locales copiados
    if not os.path.exists(json_path):
        alt_json = os.path.join(SCRIPT_DIR, "..", "entradas", "investigacion-aeronautica", "configuraciones", "C02_CANDIDATA.json")
        if os.path.exists(alt_json):
            json_path = os.path.abspath(alt_json)
    if not os.path.exists(csv_path):
        alt_csv = os.path.join(SCRIPT_DIR, "..", "entradas", "investigacion-aeronautica", "ejecucion", "G1", "REFERENCIA_DISCO.csv")
        if os.path.exists(alt_csv):
            csv_path = os.path.abspath(alt_csv)

    with open(json_path, "r", encoding="utf-8") as f:
        c02_data = json.load(f)

    previous_csv_rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            previous_csv_rows.append({
                "mass_target_kg": float(row["mass_target_kg"]),
                "free_disk_diameter_reference_m": float(row["free_disk_diameter_reference_m"]),
                "free_disks_total_area_m2": float(row["free_disks_total_area_m2"]),
                "upward_net_accel_g": float(row["upward_net_accel_g"]),
                "required_total_force_N": float(row["required_total_force_N"]),
                "ideal_isolated_disk_induced_velocity_ms": float(row["ideal_isolated_disk_induced_velocity_ms"]),
                "ideal_isolated_disk_power_W": float(row["ideal_isolated_disk_power_W"]),
                "scope": row["scope"]
            })

    return {
        "c02": c02_data,
        "previous_csv": previous_csv_rows,
        "json_source": json_path,
        "csv_source": csv_path
    }


def compute_momentum_theory(
    mass_kg: float,
    disk_diameter_m: float,
    num_fans: int = 4,
    upward_accel_g: float = 0.0,
    rho_kg_m3: float = 1.225,
    g_m_s2: float = 9.80665
) -> Dict[str, float]:
    """
    Calcula los parámetros aerodinámicos de la teoría de cantidad de movimiento
    (Rankine-Froude) para un conjunto de rotores ideales abiertos.

    Ecuaciones gobernantes:
      - Empuje total: T = mass_kg * g_m_s2 * (1 + upward_accel_g)
      - Área de un disco: A_1 = pi * (D / 2)^2
      - Área total de N discos: A_tot = N * A_1  (si N=4, A_tot = pi * D^2)
      - Velocidad inducida ideal: vi = sqrt(T / (2 * rho * A_tot))
      - Potencia inducida ideal: Pi = T * vi = T^(3/2) / sqrt(2 * rho * A_tot)
      - Carga de disco: DL = T / A_tot
      - Carga de potencia: PL = T / Pi = 1 / vi
    """
    radius_m = disk_diameter_m / 2.0
    single_disk_area_m2 = math.pi * (radius_m ** 2)
    total_area_m2 = num_fans * single_disk_area_m2

    total_thrust_N = mass_kg * g_m_s2 * (1.0 + upward_accel_g)
    thrust_per_fan_N = total_thrust_N / num_fans

    induced_velocity_ms = math.sqrt(total_thrust_N / (2.0 * rho_kg_m3 * total_area_m2))
    ideal_power_W = total_thrust_N * induced_velocity_ms

    disk_loading_N_m2 = total_thrust_N / total_area_m2
    power_loading_N_W = total_thrust_N / ideal_power_W

    return {
        "mass_target_kg": mass_kg,
        "disk_diameter_m": disk_diameter_m,
        "single_disk_area_m2": single_disk_area_m2,
        "total_area_m2": total_area_m2,
        "upward_accel_g": upward_accel_g,
        "total_thrust_N": total_thrust_N,
        "thrust_per_fan_N": thrust_per_fan_N,
        "induced_velocity_ms": induced_velocity_ms,
        "ideal_power_W": ideal_power_W,
        "disk_loading_N_m2": disk_loading_N_m2,
        "power_loading_N_W": power_loading_N_W
    }


def run_scaling_study(
    json_path: str = None,
    csv_path: str = None
) -> Dict[str, Any]:
    """
    Ejecuta el estudio de escalado geométrico semejante (D proporcional a m^(1/3))
    para 2, 5 y 10 kg, comparando la hipótesis D82 (rotor nominal BEM)
    frente a la hipótesis D84 (diámetro de conducto / bore).
    """
    inputs = load_reference_inputs(json_path=json_path, csv_path=csv_path)
    c02 = inputs["c02"]

    rho = float(c02["operating_reference"]["rho_kg_m3"])
    g = float(c02["operating_reference"]["g_m_s2"])
    num_fans = int(c02["fan_reference"]["count"])

    # Base 5 kg:
    # D82: radio BEM nominal de pala 41 mm * 2 = 82 mm = 0.082 m
    r_bem_nominal = float(c02["fan_reference"]["BEM_nominal_radius_m"])
    d82_ref_5kg = 2.0 * r_bem_nominal  # 0.082 m

    # D84: diámetro nominal de conducto / bore = 84 mm = 0.084 m
    d84_ref_5kg = float(c02["fan_reference"]["nominal_bore_diameter_m"])  # 0.084 m

    masses = [2.0, 5.0, 10.0]
    accels = [0.0, 0.5, 1.0]

    results_d82 = []
    results_d84 = []
    comparisons = []

    scope_tag = (
        "Conditional mathematical scaling (D ~ m^(1/3)) of reference D82 rotor, "
        "4 unshrouded ideal actuator disks in hover/climb; NOT a vehicle variant design "
        "nor universal ducted-fan lower bound."
    )

    for m in masses:
        # Factor de escala geométrico semejante (isometría m ~ L^3 => L ~ m^(1/3))
        lambda_m = (m / 5.0) ** (1.0 / 3.0)

        d_m_d82 = d82_ref_5kg * lambda_m
        d_m_d84 = d84_ref_5kg * lambda_m

        for a in accels:
            res_82 = compute_momentum_theory(m, d_m_d82, num_fans, a, rho, g)
            res_84 = compute_momentum_theory(m, d_m_d84, num_fans, a, rho, g)

            res_82["scope"] = scope_tag
            res_84["scope"] = scope_tag

            results_d82.append(res_82)
            results_d84.append(res_84)

            # Comparativa D82 vs D84
            delta_d = res_82["disk_diameter_m"] - res_84["disk_diameter_m"]
            pct_d = (res_82["disk_diameter_m"] / res_84["disk_diameter_m"] - 1.0) * 100.0

            delta_a = res_82["total_area_m2"] - res_84["total_area_m2"]
            pct_a = (res_82["total_area_m2"] / res_84["total_area_m2"] - 1.0) * 100.0

            delta_vi = res_82["induced_velocity_ms"] - res_84["induced_velocity_ms"]
            pct_vi = (res_82["induced_velocity_ms"] / res_84["induced_velocity_ms"] - 1.0) * 100.0

            delta_p = res_82["ideal_power_W"] - res_84["ideal_power_W"]
            pct_p = (res_82["ideal_power_W"] / res_84["ideal_power_W"] - 1.0) * 100.0

            comparisons.append({
                "mass_target_kg": m,
                "upward_accel_g": a,
                "total_thrust_N": res_82["total_thrust_N"],
                "diameter_D82_m": res_82["disk_diameter_m"],
                "diameter_D84_m": res_84["disk_diameter_m"],
                "delta_diameter_m": delta_d,
                "pct_delta_diameter": pct_d,
                "total_area_D82_m2": res_82["total_area_m2"],
                "total_area_D84_m2": res_84["total_area_m2"],
                "delta_total_area_m2": delta_a,
                "pct_delta_total_area": pct_a,
                "induced_vel_D82_ms": res_82["induced_velocity_ms"],
                "induced_vel_D84_ms": res_84["induced_velocity_ms"],
                "delta_induced_vel_ms": delta_vi,
                "pct_delta_induced_vel": pct_vi,
                "ideal_power_D82_W": res_82["ideal_power_W"],
                "ideal_power_D84_W": res_84["ideal_power_W"],
                "delta_ideal_power_W": delta_p,
                "pct_delta_ideal_power": pct_p,
            })

    return {
        "d82_ref_5kg": d82_ref_5kg,
        "d84_ref_5kg": d84_ref_5kg,
        "rho": rho,
        "g": g,
        "results_d82": results_d82,
        "results_d84": results_d84,
        "comparisons": comparisons,
        "previous_csv": inputs["previous_csv"],
        "json_source": inputs["json_source"],
        "csv_source": inputs["csv_source"]
    }


def export_deliverables(data: Dict[str, Any], output_dir: str = None) -> None:
    """
    Exporta las tablas de datos y comparativa a output_dir (por defecto el directorio del script).
    """
    if output_dir is None:
        output_dir = SCRIPT_DIR
    os.makedirs(output_dir, exist_ok=True)

    # 1. TABLA_ESCALADO_D82.csv
    csv_d82_path = os.path.join(output_dir, "TABLA_ESCALADO_D82.csv")
    with open(csv_d82_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "mass_target_kg",
            "free_disk_diameter_reference_m",
            "free_disks_total_area_m2",
            "upward_net_accel_g",
            "required_total_force_N",
            "ideal_isolated_disk_induced_velocity_ms",
            "ideal_isolated_disk_power_W",
            "scope"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in data["results_d82"]:
            writer.writerow({
                "mass_target_kg": int(r["mass_target_kg"]) if r["mass_target_kg"].is_integer() else r["mass_target_kg"],
                "free_disk_diameter_reference_m": f"{r['disk_diameter_m']:.17f}",
                "free_disks_total_area_m2": f"{r['total_area_m2']:.17f}",
                "upward_net_accel_g": int(r["upward_accel_g"]) if r["upward_accel_g"].is_integer() else r["upward_accel_g"],
                "required_total_force_N": f"{r['total_thrust_N']:.15f}",
                "ideal_isolated_disk_induced_velocity_ms": f"{r['induced_velocity_ms']:.15f}",
                "ideal_isolated_disk_power_W": f"{r['ideal_power_W']:.14f}",
                "scope": r["scope"]
            })

    # 2. COMPARATIVA_D82_VS_D84.csv
    comp_csv_path = os.path.join(output_dir, "COMPARATIVA_D82_VS_D84.csv")
    with open(comp_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "mass_target_kg",
            "upward_accel_g",
            "total_thrust_N",
            "diameter_D82_m",
            "diameter_D84_m",
            "delta_diameter_m",
            "pct_delta_diameter",
            "total_area_D82_m2",
            "total_area_D84_m2",
            "delta_total_area_m2",
            "pct_delta_total_area",
            "induced_vel_D82_ms",
            "induced_vel_D84_ms",
            "delta_induced_vel_ms",
            "pct_delta_induced_vel",
            "ideal_power_D82_W",
            "ideal_power_D84_W",
            "delta_ideal_power_W",
            "pct_delta_ideal_power"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in data["comparisons"]:
            writer.writerow({
                "mass_target_kg": r["mass_target_kg"],
                "upward_accel_g": r["upward_accel_g"],
                "total_thrust_N": f"{r['total_thrust_N']:.5f}",
                "diameter_D82_m": f"{r['diameter_D82_m']:.6f}",
                "diameter_D84_m": f"{r['diameter_D84_m']:.6f}",
                "delta_diameter_m": f"{r['delta_diameter_m']:.6f}",
                "pct_delta_diameter": f"{r['pct_delta_diameter']:.4f}",
                "total_area_D82_m2": f"{r['total_area_D82_m2']:.8f}",
                "total_area_D84_m2": f"{r['total_area_D84_m2']:.8f}",
                "delta_total_area_m2": f"{r['delta_total_area_m2']:.8f}",
                "pct_delta_total_area": f"{r['pct_delta_total_area']:.4f}",
                "induced_vel_D82_ms": f"{r['induced_vel_D82_ms']:.6f}",
                "induced_vel_D84_ms": f"{r['induced_vel_D84_ms']:.6f}",
                "delta_induced_vel_ms": f"{r['delta_induced_vel_ms']:.6f}",
                "pct_delta_induced_vel": f"{r['pct_delta_induced_vel']:.4f}",
                "ideal_power_D82_W": f"{r['ideal_power_D82_W']:.4f}",
                "ideal_power_D84_W": f"{r['ideal_power_D84_W']:.4f}",
                "delta_ideal_power_W": f"{r['delta_ideal_power_W']:.4f}",
                "pct_delta_ideal_power": f"{r['pct_delta_ideal_power']:.4f}"
            })

    # 3. TABLA_ESTACIONARIO_COMPARADA.md
    md_table_path = os.path.join(output_dir, "TABLA_ESTACIONARIO_COMPARADA.md")
    hover_comps = [c for c in data["comparisons"] if c["upward_accel_g"] == 0.0]

    with open(md_table_path, "w", encoding="utf-8") as f:
        f.write("# Tabla Comparativa de Estacionario (Hover, 0 g netos): Base D82 vs Base D84\n\n")
        f.write("Condiciones: rho = 1.225 kg/m^3, g = 9.80665 m/s^2, 4 discos ideales abiertos.\n\n")
        f.write("| Masa (kg) | Empuje (N) | D82 (mm) | D84 (mm) | Delta D (%) | Area D82 (cm^2) | Area D84 (cm^2) | Delta Area (%) | vi D82 (m/s) | vi D84 (m/s) | Delta vi (%) | Pi D82 (W) | Pi D84 (W) | Delta Pi (W) | Delta Pi (%) |\n")
        f.write("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for c in hover_comps:
            m = c["mass_target_kg"]
            T = c["total_thrust_N"]
            d82_mm = c["diameter_D82_m"] * 1000.0
            d84_mm = c["diameter_D84_m"] * 1000.0
            pct_d = c["pct_delta_diameter"]
            a82_cm2 = c["total_area_D82_m2"] * 10000.0
            a84_cm2 = c["total_area_D84_m2"] * 10000.0
            pct_a = c["pct_delta_total_area"]
            vi82 = c["induced_vel_D82_ms"]
            vi84 = c["induced_vel_D84_ms"]
            pct_vi = c["pct_delta_induced_vel"]
            pi82 = c["ideal_power_D82_W"]
            pi84 = c["ideal_power_D84_W"]
            dpi = c["delta_ideal_power_W"]
            pct_pi = c["pct_delta_ideal_power"]
            f.write(
                f"| {m:.0f} | {T:.3f} | {d82_mm:.2f} | {d84_mm:.2f} | {pct_d:+.2f}% | "
                f"{a82_cm2:.2f} | {a84_cm2:.2f} | {pct_a:+.2f}% | "
                f"{vi82:.2f} | {vi84:.2f} | {pct_vi:+.2f}% | "
                f"{pi82:.2f} | {pi84:.2f} | {dpi:+.2f} | {pct_pi:+.2f}% |\n"
            )
        f.write("\n> **Nota de alcance y delimitación técnica**:\n")
        f.write("> 1. Resultados puramente teóricos de discos actuadores ideales abiertos (teoría de cantidad de movimiento 1D).\n")
        f.write("> 2. NO constituye la potencia eléctrica instalada ni el consumo del vehículo (el consumo real es típicamente 1.8x a 2.5x mayor por arrastre de perfil, pérdidas de huelgo, bloqueo y eficiencias motrices).\n")
        f.write("> 3. NO constituye un diseño validado ni aceptado de ninguna escala (2 kg y 10 kg están 'pending_own_configuration', y 5 kg es 'partial_CAD_candidate' con rotor no calificado).\n")
        f.write("> 4. D84 (84 mm) es otra hipótesis de referencia que toma el diámetro del conducto / bore en vez del rotor giratorio (D82 = 82 mm, radio BEM 41 mm).\n")
        f.write("> 5. NO declara una regla universal de límite para ventiladores entubados (el conducto puede alterar la potencia inducida teórica favorablemente, y las pérdidas reales desfavorables contrarrestan este efecto).\n")


def print_summary(data: Dict[str, Any]) -> None:
    """Imprime un resumen formateado por consola."""
    print("=" * 80)
    print("ESTUDIO DE ESCALADO GEOMÉTRICO SEMEJANTE (D ~ m^(1/3)) - 2, 5, 10 kg")
    print("Base Rotor D82 (R=41 mm) vs Base Conducto D84 (R=42 mm)")
    print("=" * 80)
    print(f"Condiciones de referencia: rho = {data['rho']} kg/m^3, g = {data['g']} m/s^2, 4 rotores")
    print(f"Rotor D82 (nominal BEM) a 5 kg: {data['d82_ref_5kg']*1000:.1f} mm")
    print(f"Conducto D84 (nominal bore) a 5 kg: {data['d84_ref_5kg']*1000:.1f} mm")
    print("-" * 80)
    print(f"{'Masa':<6} {'D_rotor (mm)':<14} {'Area_tot (cm2)':<16} {'Empuje (N)':<12} {'vi (m/s)':<10} {'Pi_ideal (W)':<14} {'P_D84 (W)':<12} {'Delta Pi (%)'}")
    print("-" * 80)

    hover_comps = [c for c in data["comparisons"] if c["upward_accel_g"] == 0.0]
    for c in hover_comps:
        m = c["mass_target_kg"]
        d = c["diameter_D82_m"] * 1000.0
        a = c["total_area_D82_m2"] * 10000.0
        t = c["total_thrust_N"]
        vi = c["induced_vel_D82_ms"]
        pi82 = c["ideal_power_D82_W"]
        pi84 = c["ideal_power_D84_W"]
        pct_pi = c["pct_delta_ideal_power"]
        print(f"{m:<6.0f} {d:<14.2f} {a:<16.2f} {t:<12.3f} {vi:<10.2f} {pi82:<14.2f} {pi84:<12.2f} {pct_pi:+.2f}%")
    print("-" * 80)
    print("Relaciones analíticas exactas D82 vs D84:")
    print("  D82 / D84 = 82 / 84 = 41 / 42 ~= 0.97619 (-2.381%)")
    print("  A82 / A84 = (41 / 42)^2 = 1681 / 1764 ~= 0.95295 (-4.705%)")
    print("  vi_82 / vi_84 = 42 / 41 ~= 1.02439 (+2.439%)")
    print("  Pi_82 / Pi_84 = 42 / 41 ~= 1.02439 (+2.439%)")
    print("=" * 80)


if __name__ == "__main__":
    study_data = run_scaling_study()
    export_deliverables(study_data)
    print_summary(study_data)
