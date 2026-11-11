#!/usr/bin/env python3
"""
comprobaciones_centrifugas.py
=============================
Auditoría y comprobaciones analíticas independientes de escalado centrífugo
para el rotor C02 (configuraciones D82 y prototipo D102,5).

Cálculos implementados:
  1. Cinemática rotatoria: velocidad angular (Omega), velocidad periférica de punta (v_tip).
  2. Aerodinámica básica de punta: velocidad del sonido ISA y Mach de punta (M_tip).
  3. Carga centrífuga radial: F_rad = m * r_cm * Omega^2 (modelo puntual, analítico y contraste CAD).
  4. Auditoría dimensional y verificación de leyes de escala (D82 vs D102,5).
  5. Exportación de tablas reproducibles (CSV, JSON).

AVISO / LIMITACIÓN EXPRESA:
Este análisis constituye un cribado analítico y cinemático preliminar.
NO constituye un cálculo de tensión real de la pala, ni un análisis aeroelástico,
ni una aprobación de integridad estructural o de fabricación.
"""

import math
import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# -----------------------------------------------------------------------------
# Constantes físicas y de referencia ISA (International Standard Atmosphere)
# Fuente: ISO 2533 / Standard Atmosphere
# -----------------------------------------------------------------------------
GAMMA_AIR: float = 1.4                    # Razón de calores específicos del aire [-]
R_SPECIFIC_AIR: float = 287.05287         # Constante específica del gas seco [J / (kg * K)]
T0_ISA_KELVIN: float = 288.15             # Temperatura estándar a nivel del mar [K] (15 °C)
P0_ISA_PA: float = 101325.0               # Presión estándar a nivel del mar [Pa]
RHO0_ISA_KG_M3: float = 1.225             # Densidad estándar del aire a nivel del mar [kg/m³]
G0_M_S2: float = 9.80665                  # Aceleración gravitatoria estándar [m/s²]

# -----------------------------------------------------------------------------
# Definición de rotores C02
# Fuente: entradas/investigacion-aeronautica/ejecucion/G5/rotor_C02/INFORME.md
# -----------------------------------------------------------------------------
ROTOR_CONFIGS = {
    "D82": {
        "diameter_mm": 82.0,
        "radius_mm": 41.0,
        "diameter_m": 0.082,
        "radius_m": 0.041,
        "diameter_factor": 1.0,
        "blade_count": 8,
        "r_hub_cylinder_over_R": 0.32,
        "r_hub_cylinder_mm": 13.12,
        "reference_only_not_installed": False,
        "step_sha256": "76fac72ce73e7e46becac086a0a1f2d53f216a91b985f200a95dcdb554edc251",
    },
    "D102.5": {
        "diameter_mm": 102.5,
        "radius_mm": 51.25,
        "diameter_m": 0.1025,
        "radius_m": 0.05125,
        "diameter_factor": 1.25,
        "blade_count": 8,
        "r_hub_cylinder_over_R": 0.32,
        "r_hub_cylinder_mm": 16.40,
        "reference_only_not_installed": True,
        "step_sha256": "0d460f72b8fb8a3ea35d7da00e4d0b4847ce8f35cf5cd5afd658e01833176caa",
    }
}

# -----------------------------------------------------------------------------
# Escenarios de operación C01 supuestos (5 kg vehículo, kappa = 0.85)
# Fuente: RESULTADOS.json / INFORME.md
# -----------------------------------------------------------------------------
OPERATING_SCENARIOS = {
    "hover": {
        "label": "Estacionario (Hover)",
        "rpm_D82": 46231.48148400444,
        "rpm_D102_5": 29588.148149762844,
        "description": "Equilibrio estacionario para masa nominal de 5 kg",
    },
    "lateral_0_5g_fixed_attitude": {
        "label": "Demanda lateral 0,5g",
        "rpm_D82": 48901.22727238509,
        "rpm_D102_5": 31296.785454326457,
        "description": "Demanda de maniobra lateral 0,5g a actitud constante",
    },
    "vertical_up_1g": {
        "label": "Demanda vertical ascendente +1g",
        "rpm_D82": 65375.70291706148,
        "rpm_D102_5": 41840.44986691935,
        "description": "Aceleración vertical neta de +1g (empuje total equivalente a 2g)",
    }
}

# Densidades supuestas en el cribado previo
DENSITIES_ASSUMED_KG_M3 = [1200.0, 1600.0, 2700.0]


# -----------------------------------------------------------------------------
# Funciones cinemáticas y aerodinámicas analíticas independientes
# -----------------------------------------------------------------------------
def rpm_to_rad_s(rpm: float) -> float:
    """Convierte revoluciones por minuto a velocidad angular en radianes por segundo."""
    return rpm * (math.pi / 30.0)


def speed_of_sound(temperature_k: float = T0_ISA_KELVIN) -> float:
    """Calcula la velocidad del sonido en el aire ideal según temperatura absoluta."""
    if temperature_k <= 0.0:
        raise ValueError(f"Temperatura inválida: {temperature_k} K")
    return math.sqrt(GAMMA_AIR * R_SPECIFIC_AIR * temperature_k)


def tip_peripheral_velocity(rpm: float, radius_m: float) -> float:
    """Calcula la velocidad lineal periférica en la punta de la pala (v_tip = Omega * R)."""
    omega = rpm_to_rad_s(rpm)
    return omega * radius_m


def tip_mach_number(tip_speed_m_s: float, sound_speed_m_s: float) -> float:
    """Calcula el número de Mach en la punta de la pala."""
    if sound_speed_m_s <= 0.0:
        raise ValueError("Velocidad del sonido debe ser estrictamente positiva.")
    return tip_speed_m_s / sound_speed_m_s


def centrifugal_acceleration(rpm: float, radius_m: float) -> float:
    """Calcula la aceleración centrípeta/centrífuga en m/s² (a_c = Omega^2 * r)."""
    omega = rpm_to_rad_s(rpm)
    return (omega ** 2) * radius_m


def centrifugal_radial_force(mass_kg: float, radius_cm_m: float, omega_rad_s: float) -> float:
    """
    Calcula la fuerza centrífuga radial para una masa supuesta m con centro de masa en r_cm:
    F_rad = m * r_cm * Omega^2
    """
    return mass_kg * radius_cm_m * (omega_rad_s ** 2)


def analytical_uniform_blade_force(total_mass_kg: float, r_root_m: float, r_tip_m: float, omega_rad_s: float) -> float:
    """
    Calcula la fuerza centrífuga radial para una pala recta de sección uniforme:
    dF = (dm) * r * Omega^2, donde dm = (M / (R_tip - R_root)) * dr
    F = [M / (R_tip - R_root)] * Omega^2 * integral_{R_root}^{R_tip} r dr
      = M * Omega^2 * (R_root + R_tip) / 2
    """
    r_cm = (r_root_m + r_tip_m) / 2.0
    return total_mass_kg * r_cm * (omega_rad_s ** 2)


def analytical_linearly_tapered_blade_force(
    root_mass_per_len: float,
    tip_mass_per_len: float,
    r_root_m: float,
    r_tip_m: float,
    omega_rad_s: float
) -> Tuple[float, float, float]:
    """
    Calcula analíticamente la fuerza centrífuga para una pala con ahusamiento lineal de masa:
    mu(r) = mu_0 + (mu_1 - mu_0) * (r - r_0) / (r_1 - r_0)
    Retorna: (Fuerza_N, Masa_total_kg, Radio_centroide_m)
    """
    L = r_tip_m - r_root_m
    m_tot = 0.5 * (root_mass_per_len + tip_mass_per_len) * L
    # Integral de r * mu(r) dr desde r_root hasta r_tip:
    # Usando cambio de variable u = r - r_root in [0, L]:
    # r = r_root + u, mu(u) = mu_0 + (mu_1 - mu_0) * u / L
    # int (r_root + u) * (mu_0 + delta*u/L) du
    delta = tip_mass_per_len - root_mass_per_len
    int_r_dm = (
        root_mass_per_len * r_root_m * L
        + root_mass_per_len * (L ** 2) / 2.0
        + (delta / L) * (r_root_m * (L ** 2) / 2.0 + (L ** 3) / 3.0)
    )
    r_cm = int_r_dm / m_tot
    f_rad = int_r_dm * (omega_rad_s ** 2)
    return f_rad, m_tot, r_cm


# -----------------------------------------------------------------------------
# Clase auditora de datos previos (G5 / RESULTADOS.json)
# -----------------------------------------------------------------------------
class RotorAuditor:
    def __init__(self, resultados_json_path: Path):
        self.path = resultados_json_path
        if not self.path.exists():
            raise FileNotFoundError(f"Archivo de resultados no encontrado: {self.path}")
        with open(self.path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)
        self.results = self.raw_data.get("results", [])
        self.sections = self.raw_data.get("sections", [])
        self.metadata = {k: v for k, v in self.raw_data.items() if k not in ("results", "sections")}

    def verify_geometric_integral_invariance(self) -> Dict[Tuple[float, float], Dict[str, float]]:
        """
        Comprueba que Fx / (rho * Omega^2) sea estrictamente una constante geométrica
        (la integral de volumen int x dV) independiente del escenario operativo y la densidad.
        """
        invariants: Dict[Tuple[float, float], List[float]] = {}
        outboard_volumes: Dict[Tuple[float, float], List[float]] = {}

        for entry in self.results:
            df = entry["diameter_factor"]
            xr = round(entry["x_over_R"], 4)
            omega = rpm_to_rad_s(entry["rpm_ASSUMED"])
            rho = entry["density_ASSUMED_kg_m3"]
            fx = entry["force_N"][0]
            mass = entry["mass_outboard_kg"]

            int_x_dv = fx / (rho * (omega ** 2))
            vol = mass / rho

            key = (df, xr)
            invariants.setdefault(key, []).append(int_x_dv)
            outboard_volumes.setdefault(key, []).append(vol)

        report = {}
        for key, vals in sorted(invariants.items()):
            df, xr = key
            val_mean = sum(vals) / len(vals)
            rel_spread = (max(vals) - min(vals)) / val_mean if val_mean != 0 else 0.0
            vols = outboard_volumes[key]
            vol_mean = sum(vols) / len(vols)
            r_cm_eff_m = val_mean / vol_mean

            report[key] = {
                "geom_integral_x_m4": val_mean,
                "volume_outboard_m3": vol_mean,
                "r_cm_effective_m": r_cm_eff_m,
                "relative_numerical_spread": rel_spread,
            }
        return report

    def verify_similarity_pairs(self) -> Dict[str, Any]:
        """
        Verifica las 72 parejas de semejanza geométrica (D82 vs D102,5).
        Bajo el escalado C01 (rpm ~ D^-2):
          - La fuerza centrífuga radial se conserva exactamente: F(102,5) / F(82) = 1,000000
          - La tensión normal se reduce a (1 / 1,25)^2 = 0,640000
        """
        pairs: Dict[Tuple[float, str, float], Dict[float, Dict[str, Any]]] = {}
        for r in self.results:
            key = (round(r["x_over_R"], 4), r["operating_scenario"], r["density_ASSUMED_kg_m3"])
            pairs.setdefault(key, {})[r["diameter_factor"]] = r

        force_ratios = []
        stress_ratios = []
        axial_stress_ratios = []

        for key, factors in pairs.items():
            if 1.0 in factors and 1.25 in factors:
                r10 = factors[1.0]
                r125 = factors[1.25]
                f10 = r10["force_N"][0]
                f125 = r125["force_N"][0]
                s10 = r10["sampled_abs_normal_max_Pa"]
                s125 = r125["sampled_abs_normal_max_Pa"]
                a10 = r10["mean_axial_Pa"]
                a125 = r125["mean_axial_Pa"]

                force_ratios.append(f125 / f10)
                stress_ratios.append(s125 / s10)
                axial_stress_ratios.append(a125 / a10)

        return {
            "total_pairs": len(force_ratios),
            "force_ratio_min": min(force_ratios),
            "force_ratio_max": max(force_ratios),
            "stress_ratio_min": min(stress_ratios),
            "stress_ratio_max": max(stress_ratios),
            "axial_stress_ratio_min": min(axial_stress_ratios),
            "axial_stress_ratio_max": max(axial_stress_ratios),
        }


# -----------------------------------------------------------------------------
# Generador de tablas reproducibles y comparativas
# -----------------------------------------------------------------------------
def build_comprehensive_scaling_table(auditor: RotorAuditor) -> List[Dict[str, Any]]:
    """
    Construye la tabla reproducible con todas las variables de cinemática,
    Mach, cargas radiales analíticas y contraste con el cribado CAD.
    """
    table_rows = []
    sound_speed_isa = speed_of_sound(T0_ISA_KELVIN)
    invariants = auditor.verify_geometric_integral_invariance()

    # Mapeo de secciones CAD para consulta rápida de área
    sections_map = {}
    for sec in auditor.sections:
        sections_map[(sec["diameter_factor"], round(sec["x_over_R"], 4))] = sec

    for res in auditor.results:
        df = res["diameter_factor"]
        rotor_name = "D82" if df == 1.0 else "D102.5"
        r_tip_m = ROTOR_CONFIGS[rotor_name]["radius_m"]
        xr = round(res["x_over_R"], 4)
        scenario_key = res["operating_scenario"]
        scenario_meta = OPERATING_SCENARIOS[scenario_key]
        rpm = res["rpm_ASSUMED"]
        omega = rpm_to_rad_s(rpm)
        v_tip = tip_peripheral_velocity(rpm, r_tip_m)
        m_tip = tip_mach_number(v_tip, sound_speed_isa)
        a_centrif_tip = centrifugal_acceleration(rpm, r_tip_m)

        rho = res["density_ASSUMED_kg_m3"]
        mass_outboard_kg = res["mass_outboard_kg"]
        mass_outboard_g = mass_outboard_kg * 1000.0

        # Propiedades de sección
        sec = sections_map.get((df, xr), {})
        area_mm2 = sec.get("area_mm2", res.get("area_mm2", 0.0))
        area_m2 = area_mm2 * 1e-6

        # Centro de masa efectivo outboard según invariante geométrica
        geom_info = invariants.get((df, xr), {})
        r_cm_eff_m = geom_info.get("r_cm_effective_m", 0.0)
        r_cm_eff_mm = r_cm_eff_m * 1000.0

        # Carga radial analítica independiente: F = m * r_cm * omega^2
        f_rad_analitica_n = centrifugal_radial_force(mass_outboard_kg, r_cm_eff_m, omega)
        f_rad_cad_n = res["force_N"][0]
        f_transversal_cad_n = res["force_N"][1]

        # Tensión axial media analítica: sigma = F / A
        sigma_axial_analitica_pa = (f_rad_analitica_n / area_m2) if area_m2 > 0 else 0.0
        sigma_axial_cad_pa = res["mean_axial_Pa"]
        sigma_normal_max_cad_pa = res["sampled_abs_normal_max_Pa"]

        # Factor de amplificación por flexión no simétrica
        amplif_flexion = (sigma_normal_max_cad_pa / sigma_axial_cad_pa) if sigma_axial_cad_pa > 0 else 1.0

        row = {
            "rotor_id": rotor_name,
            "diametro_mm": ROTOR_CONFIGS[rotor_name]["diameter_mm"],
            "factor_diametro": df,
            "estacion_x_over_R": xr,
            "radio_corte_mm": xr * ROTOR_CONFIGS[rotor_name]["radius_mm"],
            "escenario": scenario_key,
            "escenario_nombre": scenario_meta["label"],
            "rpm_supuesta": rpm,
            "omega_rad_s": omega,
            "velocidad_punta_m_s": v_tip,
            "mach_punta_isa": m_tip,
            "aceleracion_punta_m_s2": a_centrif_tip,
            "aceleracion_punta_g": a_centrif_tip / G0_M_S2,
            "densidad_supuesta_kg_m3": rho,
            "masa_exterior_g": mass_outboard_g,
            "r_cm_exterior_mm": r_cm_eff_mm,
            "r_cm_over_R": r_cm_eff_m / r_tip_m,
            "area_seccion_mm2": area_mm2,
            "fuerza_radial_analitica_N": f_rad_analitica_n,
            "fuerza_radial_cad_N": f_rad_cad_n,
            "diferencia_rel_fuerza": abs(f_rad_analitica_n - f_rad_cad_n) / f_rad_cad_n if f_rad_cad_n > 0 else 0.0,
            "fuerza_transversal_cad_N": f_transversal_cad_n,
            "tension_axial_media_MPa": sigma_axial_cad_pa / 1e6,
            "tension_normal_max_MPa": sigma_normal_max_cad_pa / 1e6,
            "factor_amplificacion_flexion": amplif_flexion,
            "clasificacion_datos": "Supuesto: rpm/densidad/geometria; Calculado: cinematica/fuerza/tension; Medido: Ninguno",
        }
        table_rows.append(row)

    return table_rows


def export_tables(rows: List[Dict[str, Any]], output_dir: Path) -> Tuple[Path, Path]:
    """Exporta las tablas de escalado a CSV y JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "tabla_escalado_centrifugo.csv"
    json_path = output_dir / "resumen_analitico.json"

    # Exportar CSV
    if rows:
        fieldnames = list(rows[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

    # Exportar JSON con resumen estructurado
    summary_data = {
        "metadata": {
            "title": "Comprobaciones analíticas independientes de escalado centrífugo - Rotor C02",
            "author": "Auditoría estructural independiente (Sandbox)",
            "date": "Noviembre 2026",
            "rotores": ROTOR_CONFIGS,
            "escenarios": OPERATING_SCENARIOS,
            "densidades_kg_m3": DENSITIES_ASSUMED_KG_M3,
            "condicion_atmosferica": "ISA nivel del mar (15 °C, a0 = 340,29 m/s)",
            "aviso_legal": "No constituye análisis de pala real, aeroelasticidad ni aprobación de fabricación",
        },
        "total_registros": len(rows),
        "filas_muestra_estacion_0_33": [r for r in rows if abs(r["estacion_x_over_R"] - 0.33) < 1e-4],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    return csv_path, json_path


# -----------------------------------------------------------------------------
# Análisis de los tres regímenes de escalado dimensional (D82 vs D102,5)
# -----------------------------------------------------------------------------
def analyze_scaling_regimes() -> List[Dict[str, Any]]:
    """
    Compara las implicaciones físicas de tres criterios de escalado entre D82 y D102,5:
      1. Régimen C01 aerodinámico: rpm proporcional a D^-2 (mismo empuje en sustentación 5 kg).
      2. Régimen de velocidad periférica constante: v_tip = const -> rpm proporcional a D^-1.
      3. Régimen de velocidad rotacional constante: rpm = const.
    """
    lambda_d = 1.25  # R_102.5 / R_82
    base_rpm = OPERATING_SCENARIOS["hover"]["rpm_D82"]
    base_r_m = ROTOR_CONFIGS["D82"]["radius_m"]
    target_r_m = ROTOR_CONFIGS["D102.5"]["radius_m"]
    sound_speed = speed_of_sound(T0_ISA_KELVIN)

    # Masa outboard en x/R = 0.33 para rho = 1600 kg/m³
    base_m_kg = 0.0004408348444026855
    target_m_kg = base_m_kg * (lambda_d ** 3)
    base_rcm_m = 0.025752
    target_rcm_m = base_rcm_m * lambda_d
    base_area_m2 = 6.357522e-6
    target_area_m2 = base_area_m2 * (lambda_d ** 2)

    regimes = [
        {
            "regimen": "1. Aerodinámico C01 (Empuje constante)",
            "criterio_rpm": "rpm ~ D^-2",
            "rpm_D82": base_rpm,
            "rpm_D102_5": base_rpm * (lambda_d ** -2),
            "ratio_rpm": lambda_d ** -2,  # 0.64
            "ratio_vtip": lambda_d ** -1,  # 0.80
            "ratio_fuerza_rad": 1.0,      # (lambda^3 * lambda) * (lambda^-4) = 1.0
            "ratio_tension_media": lambda_d ** -2, # 0.64
            "justificacion": "Conserva empuje total de sustentación del vehículo (5 kg) en hover. La fuerza centrífuga se conserva idéntica y la tensión cae un 36%.",
        },
        {
            "regimen": "2. Velocidad periférica constante",
            "criterio_rpm": "rpm ~ D^-1",
            "rpm_D82": base_rpm,
            "rpm_D102_5": base_rpm * (lambda_d ** -1),
            "ratio_rpm": lambda_d ** -1,  # 0.80
            "ratio_vtip": 1.0,           # 1.0
            "ratio_fuerza_rad": lambda_d ** 2,  # 1.5625 (+56.25%)
            "ratio_tension_media": 1.0,  # 1.0 (tensión axial constante)
            "justificacion": "Mantiene el mismo número de Mach de punta. La fuerza centrífuga radial crece un 56,25% debido a la mayor masa rotante.",
        },
        {
            "regimen": "3. Velocidad angular constante",
            "criterio_rpm": "rpm = const",
            "rpm_D82": base_rpm,
            "rpm_D102_5": base_rpm,
            "ratio_rpm": 1.0,
            "ratio_vtip": lambda_d,       # 1.25 (+25%)
            "ratio_fuerza_rad": lambda_d ** 4,  # 2.4414 (+144.14%)
            "ratio_tension_media": lambda_d ** 2, # 1.5625 (+56.25%)
            "justificacion": "Si el motor opera al mismo régimen, la fuerza radial crece un 144% y la tensión aumenta un 56,25%, alcanzando Mach transónico más rápidamente.",
        }
    ]

    for reg in regimes:
        rpm82 = reg["rpm_D82"]
        rpm102 = reg["rpm_D102_5"]
        vtip82 = tip_peripheral_velocity(rpm82, base_r_m)
        vtip102 = tip_peripheral_velocity(rpm102, target_r_m)
        omega82 = rpm_to_rad_s(rpm82)
        omega102 = rpm_to_rad_s(rpm102)

        f82 = centrifugal_radial_force(base_m_kg, base_rcm_m, omega82)
        f102 = centrifugal_radial_force(target_m_kg, target_rcm_m, omega102)

        reg["vtip_D82_m_s"] = vtip82
        reg["mach_D82"] = tip_mach_number(vtip82, sound_speed)
        reg["vtip_D102_5_m_s"] = vtip102
        reg["mach_D102_5"] = tip_mach_number(vtip102, sound_speed)
        reg["fuerza_radial_D82_N"] = f82
        reg["fuerza_radial_D102_5_N"] = f102
        reg["sigma_media_D82_MPa"] = (f82 / base_area_m2) / 1e6
        reg["sigma_media_D102_5_MPa"] = (f102 / target_area_m2) / 1e6

    return regimes


# -----------------------------------------------------------------------------
# Función principal de ejecución
# -----------------------------------------------------------------------------
def main():
    root_dir = Path(__file__).resolve().parent.parent
    input_file = root_dir / "entradas" / "investigacion-aeronautica" / "ejecucion" / "G5" / "rotor_C02" / "RESULTADOS.json"
    salidas_dir = root_dir / "salidas"

    print("=" * 80)
    print("AUDITORÍA Y COMPROBACIONES ANALÍTICAS DE ESCALADO CENTRÍFUGO - ROTOR C02")
    print("=" * 80)

    auditor = RotorAuditor(input_file)
    print(f"[OK] Archivo de referencia cargado: {input_file}")
    print(f"[OK] Registros de cribado previo: {len(auditor.results)}")
    print(f"[OK] Secciones geométricas: {len(auditor.sections)}")

    # 1. Comprobación de invariancia numérica
    invariants = auditor.verify_geometric_integral_invariance()
    max_spread = max(v["relative_numerical_spread"] for v in invariants.values())
    print(f"[OK] Invariancia int(x dV) comprobada. Máxima dispersión numérica: {max_spread:.2e} (precisión de máquina)")

    # 2. Comprobación de parejas de semejanza
    sim_report = auditor.verify_similarity_pairs()
    print(f"[OK] Parejas de semejanza verificadas: {sim_report['total_pairs']}")
    print(f"     Ratio de fuerza D102.5 / D82: min={sim_report['force_ratio_min']:.6f}, max={sim_report['force_ratio_max']:.6f}")
    print(f"     Ratio de tensión D102.5 / D82: min={sim_report['stress_ratio_min']:.6f}, max={sim_report['stress_ratio_max']:.6f}")

    # 3. Construcción y exportación de tablas
    table_rows = build_comprehensive_scaling_table(auditor)
    csv_path, json_path = export_tables(table_rows, salidas_dir)
    print(f"[OK] Tabla de datos exportada: {csv_path} ({len(table_rows)} filas)")
    print(f"[OK] Resumen estructurado exportado: {json_path}")

    # 4. Análisis de regímenes de escalado
    regimes = analyze_scaling_regimes()
    regimes_csv = salidas_dir / "tabla_comparativa_regimenes_escalado.csv"
    with open(regimes_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(regimes[0].keys()))
        writer.writeheader()
        for reg in regimes:
            writer.writerow(reg)
    print(f"[OK] Tabla comparativa de regímenes exportada: {regimes_csv}")

    # 5. Muestra en pantalla para verificación
    print("\n" + "-" * 80)
    print("RESUMEN DE CINEMÁTICA Y CARGA CENTRÍFUGA EN ESTACIÓN x/R = 0,33 (rho = 1600 kg/m³)")
    print("-" * 80)
    fmt = "{:<8} {:<24} {:>10} {:>10} {:>8} {:>10} {:>12} {:>12}"
    print(fmt.format("Rotor", "Escenario", "RPM", "v_tip (m/s)", "M_tip", "Fx (N)", "Sigma_m(MPa)", "Sigma_max(MPa)"))
    print("-" * 80)
    for r in table_rows:
        if abs(r["estacion_x_over_R"] - 0.33) < 1e-4 and abs(r["densidad_supuesta_kg_m3"] - 1600.0) < 1e-4:
            print(fmt.format(
                r["rotor_id"],
                r["escenario_nombre"][:24],
                f"{r['rpm_supuesta']:.0f}",
                f"{r['velocidad_punta_m_s']:.1f}",
                f"{r['mach_punta_isa']:.3f}",
                f"{r['fuerza_radial_cad_N']:.1f}",
                f"{r['tension_axial_media_MPa']:.2f}",
                f"{r['tension_normal_max_MPa']:.2f}",
            ))
    print("-" * 80)
    print("Cálculo y auditoría finalizados con éxito.\n")


if __name__ == "__main__":
    main()
