#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROCESAMIENTO INDEPENDIENTE DE ENSAYO DE HÉLICE ABIERTA UIUC (AVANCE Y ESTÁTICO)
Hélice: Micro Invent 3.2x2.2 @ 20.051 RPM (nominal en avance) / 2.950 - 19.923 RPM (estático)
Archivo fuente avance: mi_3.2x2.2_0544rd_20051.txt
Archivo fuente estático: mi_3.2x2.2_static_0519rd.txt
Fuente oficial: UIUC Propeller Data Site (Volume 2)
URL de referencia: https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html
===============================================================================
"""

import sys
import os
import math
import csv
import argparse
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Constantes físicas fundamentales
G_ACCEL = 9.80665      # Aceleración gravitacional estándar [m/s^2]
R_AIR = 287.058        # Constante específica del gas para aire seco [J/(kg·K)]
GAMMA_AIR = 1.40       # Coeficiente de dilatación adiabática del aire [-]
NU_AIR_ISA = 1.48e-5   # Viscosidad cinemática del aire a 15°C [m^2/s]


def find_workspace_root(start_dir: Optional[Path] = None) -> Path:
    """
    Localiza de forma robusta la raíz del espacio de trabajo que contiene 'entradas' y/o 'salidas'.
    Permite ejecutar el script desde cualquier subdirectorio sin sufrir FileNotFoundError.
    """
    current = (start_dir or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current] + list(current.parents):
        if (candidate / "entradas").exists() or (candidate / "salidas").exists():
            return candidate
    return current


class PropellerUIUCProcessor:
    """
    Procesador metrológico y aerodinámico de datos de ensayos de hélices en túnel de viento UIUC.
    
    Distingue rigurosamente entre:
    1. Datos medidos / registrados en el ensayo (tabulados por UIUC).
    2. Supuestos de ingeniería y condiciones de referencia (D, rho, n nominal).
    3. Cálculos analíticos derivados (V, T, P, Pout, eta_calc, Mach, Re).
    """

    def __init__(
        self,
        filepath_or_str: Optional[str] = None,
        static_filepath: Optional[str] = None,
        diameter_m: float = 0.08128,      # 3.2 pulgadas = 0.08128 m
        rho_kg_m3: float = 1.225,         # Densidad ISA a nivel del mar (15°C, 1013.25 hPa)
        nominal_rpm: float = 20051.0      # RPM nominal de la corrida de ensayo 0544rd
    ):
        self.root_dir = find_workspace_root()
        
        # Resolución de ruta de archivo de avance
        if filepath_or_str:
            self.filepath = Path(filepath_or_str)
            if not self.filepath.is_absolute() and not self.filepath.exists():
                alt = self.root_dir / filepath_or_str
                if alt.exists():
                    self.filepath = alt
        else:
            default_advance = (
                self.root_dir
                / "entradas"
                / "investigacion-aeronautica"
                / "fuentes"
                / "uiuc_propdb"
                / "mi_3.2x2.2_0544rd_20051.txt"
            )
            self.filepath = default_advance

        # Resolución de ruta de archivo estático
        if static_filepath:
            self.static_filepath = Path(static_filepath)
            if not self.static_filepath.is_absolute() and not self.static_filepath.exists():
                alt_static = self.root_dir / static_filepath
                if alt_static.exists():
                    self.static_filepath = alt_static
        else:
            default_static = (
                self.root_dir
                / "entradas"
                / "investigacion-aeronautica"
                / "fuentes"
                / "uiuc_propdb"
                / "mi_3.2x2.2_static_0519rd.txt"
            )
            self.static_filepath = default_static if default_static.exists() else None

        # -------------------------------------------------------------
        # SUPUESTOS (Assumptions)
        # -------------------------------------------------------------
        self.assumptions: Dict[str, Any] = {
            "D_m": float(diameter_m),
            "rho_kg_m3": float(rho_kg_m3),
            "nominal_rpm": float(nominal_rpm),
            "nominal_n_rev_s": float(nominal_rpm) / 60.0,
            "flow_regime": "Incompresible subsónico libre (sin conducto, sin interferencia de fuselaje)",
            "blade_condition": "Hélice rígida de microescala aislada en túnel de viento",
            "source_reference": "https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html",
            "propeller_pitch_m": 2.2 * 0.0254,  # 2.2 pulgadas = 0.05588 m
            "pitch_to_diameter_ratio": 2.2 / 3.2  # 0.6875
        }
        
        self.raw_data: List[Dict[str, float]] = []
        self.processed_data: List[Dict[str, Any]] = []
        self.static_raw_data: List[Dict[str, float]] = []
        self.static_processed_data: List[Dict[str, Any]] = []

    def load_data(self) -> None:
        """Carga y valida el archivo de datos de avance tabulados UIUC."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Archivo de entrada no encontrado: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            raise ValueError(f"El archivo {self.filepath} está vacío.")

        header = lines[0].split()
        expected_cols = ["J", "CT", "CP", "eta"]
        if header != expected_cols:
            raise ValueError(f"Encabezado inesperado en {self.filepath}: {header}. Se esperaba {expected_cols}")

        self.raw_data = []
        for idx, line in enumerate(lines[1:], start=1):
            parts = line.split()
            if len(parts) != 4:
                raise ValueError(f"Línea {idx+1} mal formada en {self.filepath}: {line}")
            
            # ---------------------------------------------------------
            # DATOS MEDIDOS / REGISTRADOS EN TABLA UIUC
            # ---------------------------------------------------------
            j_val = float(parts[0])
            ct_val = float(parts[1])
            cp_val = float(parts[2])
            eta_reg = float(parts[3])

            self.raw_data.append({
                "punto": idx,
                "J": j_val,
                "CT": ct_val,
                "CP": cp_val,
                "eta_reg": eta_reg
            })

    def load_static_data(self) -> List[Dict[str, float]]:
        """Carga y valida el archivo de datos estáticos UIUC (0519rd) si está disponible."""
        if not self.static_filepath or not self.static_filepath.exists():
            return []

        with open(self.static_filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return []

        header = lines[0].split()
        expected_cols = ["RPM", "CT", "CP"]
        if header != expected_cols:
            raise ValueError(f"Encabezado estático inesperado: {header}. Se esperaba {expected_cols}")

        D = self.assumptions["D_m"]
        rho = self.assumptions["rho_kg_m3"]
        self.static_raw_data = []
        self.static_processed_data = []

        for idx, line in enumerate(lines[1:], start=1):
            parts = line.split()
            if len(parts) != 3:
                continue
            rpm = float(parts[0])
            ct = float(parts[1])
            cp = float(parts[2])
            n_rev_s = rpm / 60.0

            thrust_n = ct * rho * (n_rev_s ** 2) * (D ** 4)
            power_w = cp * rho * (n_rev_s ** 3) * (D ** 5)
            thrust_to_power_gf_w = ((thrust_n / G_ACCEL) * 1000.0) / power_w if power_w > 0 else 0.0

            rec = {
                "punto": idx,
                "RPM": rpm,
                "n_rev_s": n_rev_s,
                "CT_static": ct,
                "CP_static": cp,
                "Empuje_N": thrust_n,
                "Empuje_gf": (thrust_n / G_ACCEL) * 1000.0,
                "Potencia_eje_W": power_w,
                "Relacion_gf_W": thrust_to_power_gf_w
            }
            self.static_raw_data.append({"RPM": rpm, "CT": ct, "CP": cp})
            self.static_processed_data.append(rec)

        return self.static_processed_data

    def process(self) -> List[Dict[str, Any]]:
        """
        Ejecuta las transformaciones físicas y los cálculos metrológicos.
        """
        if not self.raw_data:
            self.load_data()

        D = self.assumptions["D_m"]
        rho = self.assumptions["rho_kg_m3"]
        n = self.assumptions["nominal_n_rev_s"]
        eps_tab = 0.5e-6  # Semicifra de redondeo en tablas tabuladas a 6 decimales

        # Velocidad del sonido en aire a nivel del mar (ISA: T=288.15 K)
        t_kelvin = 288.15
        a_sound = math.sqrt(GAMMA_AIR * R_AIR * t_kelvin)  # ~340.29 m/s
        
        # Velocidad tangencial periférica de punta
        v_rot_tip = math.pi * n * D  # ~85.33 m/s
        
        # Cuerda estimada a 75% del radio (típica en microhélices 3.2": c ~ 0.08 D a 0.10 D)
        c_075 = 0.085 * D  # ~6.9 mm

        self.processed_data = []
        for pt in self.raw_data:
            j = pt["J"]
            ct = pt["CT"]
            cp = pt["CP"]
            eta_reg = pt["eta_reg"]

            # ---------------------------------------------------------
            # CÁLCULOS ANALÍTICOS DERIVADOS
            # ---------------------------------------------------------
            v_ms = j * n * D
            v_kmh = v_ms * 3.6

            thrust_n = ct * rho * (n ** 2) * (D ** 4)
            thrust_gf = (thrust_n / G_ACCEL) * 1000.0  # gramos-fuerza

            power_shaft_w = cp * rho * (n ** 3) * (D ** 5)
            power_thrust_w = thrust_n * v_ms

            eta_calc = (j * ct) / cp if cp != 0 else 0.0

            delta_eta = eta_reg - eta_calc
            rel_diff_pct = (abs(delta_eta) / eta_calc * 100.0) if eta_calc != 0 else 0.0

            rounding_prop_bound = (
                eta_calc * (eps_tab / j + eps_tab / ct + eps_tab / cp) + eps_tab
            )

            v_tip_total = math.sqrt(v_ms ** 2 + v_rot_tip ** 2)
            mach_tip = v_tip_total / a_sound

            v_075 = math.sqrt(v_ms ** 2 + (0.75 * v_rot_tip) ** 2)
            re_075 = (v_075 * c_075) / NU_AIR_ISA

            record = {
                "punto": pt["punto"],
                "J_medido": j,
                "CT_medido": ct,
                "CP_medido": cp,
                "eta_registrada": eta_reg,
                "D_m": D,
                "rho_kg_m3": rho,
                "n_rev_s": n,
                "rpm_nominal": self.assumptions["nominal_rpm"],
                "V_m_s": v_ms,
                "V_km_h": v_kmh,
                "Empuje_N": thrust_n,
                "Empuje_gf": thrust_gf,
                "Potencia_eje_W": power_shaft_w,
                "Potencia_traccion_W": power_thrust_w,
                "eta_calculada": eta_calc,
                "delta_eta_reg_menos_calc": delta_eta,
                "error_relativo_eta_pct": rel_diff_pct,
                "cota_redondeo_propagado": rounding_prop_bound,
                "es_atribuible_a_redondeo": abs(delta_eta) <= rounding_prop_bound,
                "V_punta_m_s": v_tip_total,
                "Mach_punta": mach_tip,
                "Re_cuerda_075": re_075
            }
            self.processed_data.append(record)

        if self.static_filepath and self.static_filepath.exists() and not self.static_processed_data:
            self.load_static_data()

        return self.processed_data

    def estimate_zero_thrust_advance_ratio(self) -> Dict[str, float]:
        """
        Estima analíticamente el coeficiente de avance de empuje nulo (J0 donde CT = 0)
        mediante extrapolación local sobre los últimos puntos ensayados.
        """
        if not self.processed_data:
            self.process()

        sub_pts = self.processed_data[-5:]
        x_vals = [p["J_medido"] for p in sub_pts]
        y_vals = [p["CT_medido"] for p in sub_pts]

        n = len(sub_pts)
        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n
        num = sum((x_vals[i] - mean_x) * (y_vals[i] - mean_y) for i in range(n))
        den = sum((x_vals[i] - mean_x) ** 2 for i in range(n))
        slope = num / den if den != 0 else 0.0
        intercept = mean_y - slope * mean_x

        j0_linear_5pts = -intercept / slope if slope != 0 else 0.0

        p_last = self.processed_data[-1]
        p_prev = self.processed_data[-2]
        slope_2pts = (p_last["CT_medido"] - p_prev["CT_medido"]) / (p_last["J_medido"] - p_prev["J_medido"])
        j0_linear_2pts = p_last["J_medido"] - p_last["CT_medido"] / slope_2pts

        return {
            "J0_estimado_5pts": j0_linear_5pts,
            "J0_estimado_2pts": j0_linear_2pts,
            "pendiente_dCT_dJ": slope,
            "pitch_to_diameter_ratio": self.assumptions["pitch_to_diameter_ratio"]
        }

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calcula métricas agregadas, comparaciones de rango y validaciones físicas."""
        if not self.processed_data:
            self.process()

        v_ms_vals = [r["V_m_s"] for r in self.processed_data]
        v_kmh_vals = [r["V_km_h"] for r in self.processed_data]
        j_vals = [r["J_medido"] for r in self.processed_data]
        t_vals = [r["Empuje_N"] for r in self.processed_data]
        p_vals = [r["Potencia_eje_W"] for r in self.processed_data]
        eta_reg_vals = [r["eta_registrada"] for r in self.processed_data]
        delta_eta_vals = [r["delta_eta_reg_menos_calc"] for r in self.processed_data]
        rel_diff_vals = [r["error_relativo_eta_pct"] for r in self.processed_data]
        mach_tip_vals = [r["Mach_punta"] for r in self.processed_data]
        re_vals = [r["Re_cuerda_075"] for r in self.processed_data]

        max_eta_idx = max(range(len(eta_reg_vals)), key=lambda i: eta_reg_vals[i])
        best_pt = self.processed_data[max_eta_idx]

        v_ref_kmh = 600.0
        v_ref_ms = v_ref_kmh / 3.6
        v_max_kmh = max(v_kmh_vals)
        v_max_ms = max(v_ms_vals)
        n = self.assumptions["nominal_n_rev_s"]
        D = self.assumptions["D_m"]

        j_hypothetical_600 = v_ref_ms / (n * D)
        j0_info = self.estimate_zero_thrust_advance_ratio()

        static_comparison = {}
        if self.static_processed_data:
            closest_static = max(self.static_processed_data, key=lambda s: s["RPM"])
            pt1 = self.processed_data[0]
            static_comparison = {
                "RPM_static": closest_static["RPM"],
                "CT_static": closest_static["CT_static"],
                "CP_static": closest_static["CP_static"],
                "Empuje_N_static": closest_static["Empuje_N"],
                "Empuje_gf_static": closest_static["Empuje_gf"],
                "Potencia_W_static": closest_static["Potencia_eje_W"],
                "diferencia_rel_CT_pt1_vs_static_pct": (
                    (pt1["CT_medido"] - closest_static["CT_static"]) / closest_static["CT_static"] * 100.0
                ),
                "diferencia_rel_CP_pt1_vs_static_pct": (
                    (pt1["CP_medido"] - closest_static["CP_static"]) / closest_static["CP_static"] * 100.0
                )
            }

        return {
            "n_puntos": len(self.processed_data),
            "J_min": min(j_vals),
            "J_max": max(j_vals),
            "V_min_m_s": min(v_ms_vals),
            "V_max_m_s": v_max_ms,
            "V_min_km_h": min(v_kmh_vals),
            "V_max_km_h": v_max_kmh,
            "T_min_N": min(t_vals),
            "T_max_N": max(t_vals),
            "P_min_W": min(p_vals),
            "P_max_W": max(p_vals),
            "eta_max": best_pt["eta_registrada"],
            "J_en_eta_max": best_pt["J_medido"],
            "V_kmh_en_eta_max": best_pt["V_km_h"],
            "max_abs_delta_eta": max(abs(d) for d in delta_eta_vals),
            "max_rel_diff_pct": max(rel_diff_vals),
            "all_within_rounding_bound": all(r["es_atribuible_a_redondeo"] for r in self.processed_data),
            "Mach_punta_min": min(mach_tip_vals),
            "Mach_punta_max": max(mach_tip_vals),
            "Re_cuerda_075_min": min(re_vals),
            "Re_cuerda_075_max": max(re_vals),
            "J0_estimado": j0_info["J0_estimado_5pts"],
            "V_ref_kmh": v_ref_kmh,
            "diferencia_kmh_con_600": v_ref_kmh - v_max_kmh,
            "diferencia_ms_con_600": v_ref_ms - v_max_ms,
            "factor_velocidad_600_vs_max": v_ref_kmh / v_max_kmh,
            "J_hipotetico_a_600kmh": j_hypothetical_600,
            "static_comparison": static_comparison
        }

    @staticmethod
    def _normalize_string(text: str) -> str:
        """Normaliza cadenas de texto eliminando tildes, mayúsculas y separadores especiales."""
        text = text.strip().lower()
        nfkd = unicodedata.normalize("NFKD", text)
        text = "".join([c for c in nfkd if not unicodedata.combining(c)])
        text = text.replace("-", "_").replace(" ", "_")
        return text

    def validate_application_limits(
        self,
        target_v_kmh: float,
        target_machine_type: str = "open_propeller",
        working_fluid: str = "air"
    ) -> Dict[str, Any]:
        """
        Valida si una condición operativa o maquinaria destino es físicamente válida
        con respecto a la base de datos ensayada.
        """
        if not self.processed_data:
            self.process()

        stats = self.get_summary_statistics()
        v_max_kmh = stats["V_max_km_h"]
        v_min_kmh = stats["V_min_km_h"]

        norm_machine = self._normalize_string(target_machine_type)
        norm_fluid = self._normalize_string(working_fluid)

        valid_machines = {
            "open_propeller", "helice_abierta", "helice", "propeller",
            "open_rotor", "micro_propeller"
        }
        valid_fluids = {"air", "aire", "aire_isa", "dry_air", "aire_seco"}

        machine_compatible = norm_machine in valid_machines
        fluid_compatible = norm_fluid in valid_fluids

        validations = {
            "target_v_kmh": target_v_kmh,
            "within_velocity_range": v_min_kmh <= target_v_kmh <= v_max_kmh,
            "extrapolation_factor": target_v_kmh / v_max_kmh if v_max_kmh > 0 else 0.0,
            "machine_type_compatible": machine_compatible,
            "fluid_compatible": fluid_compatible,
            "warnings": [],
            "errors": []
        }

        # Comprobación de velocidad
        if target_v_kmh > v_max_kmh:
            msg = (
                f"EXTRAPOLACIÓN INVÁLIDA: Velocidad objetivo {target_v_kmh:.1f} km/h "
                f"supera el máximo ensayado ({v_max_kmh:.2f} km/h) por un factor de "
                f"{validations['extrapolation_factor']:.2f}x. No es posible extrapolar "
                f"debido a régimen de freno molinillo (J >> J_cero_empuje ≈ {stats['J0_estimado']:.2f}), "
                f"compresibilidad de punta y sobrecargas dinámicas aeroelásticas."
            )
            validations["errors"].append(msg)
        elif target_v_kmh < v_min_kmh:
            msg = (
                f"SUB-RANGO DINÁMICO: Velocidad objetivo {target_v_kmh:.1f} km/h "
                f"es inferior al mínimo del ensayo de avance ({v_min_kmh:.2f} km/h). "
                f"Para condiciones estáticas (V=0), debe consultarse el banco estático '0519rd'."
            )
            validations["warnings"].append(msg)

        # Comprobación de máquina (ventilador / ducted fan)
        if not machine_compatible:
            msg = (
                f"TRANSFERENCIA INVÁLIDA DE DATOS: La maquinaria destino '{target_machine_type}' "
                f"no es físicamente equivalente a una hélice abierta libre. Los ventiladores "
                f"(como el 'ventilador C02') operan con conductos, holgura de punta de pala, "
                f"estatores, recuperación de presión interna y solidez elevada. Los datos "
                f"de hélices abiertas no pueden ser transferidos ni aplicados a ventiladores."
            )
            validations["errors"].append(msg)

        # Comprobación de fluido
        if not fluid_compatible:
            msg = (
                f"FLUIDO INCOMPATIBLE: El ensayo se realizó en aire atmosférico. El fluido "
                f"'{working_fluid}' posee densidad, viscosidad cinemática y velocidad del sonido "
                f"diferentes, invalidando los números de Reynolds y Mach del ensayo original."
            )
            validations["errors"].append(msg)

        validations["is_valid"] = len(validations["errors"]) == 0
        return validations

    def export_csv(self, output_path: str) -> None:
        """Exporta la tabla completa de datos procesados con metadatos descriptivos."""
        if not self.processed_data:
            self.process()

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        header_cols = [
            "punto [-]",
            "J_medido [-]",
            "CT_medido [-]",
            "CP_medido [-]",
            "eta_registrada [-]",
            "V_m_s [m/s]",
            "V_km_h [km/h]",
            "Empuje_N [N]",
            "Empuje_gf [gf]",
            "Potencia_eje_W [W]",
            "Potencia_traccion_W [W]",
            "eta_calculada [-]",
            "delta_eta [-]",
            "error_relativo_pct [%]",
            "cota_redondeo_propagado [-]",
            "es_atribuible_a_redondeo [bool]",
            "Mach_punta [-]",
            "Re_cuerda_075 [-]"
        ]

        with open(out_file, "w", newline="", encoding="utf-8") as f:
            f.write("# ENSAYO HÉLICE ABIERTA MICRO INVENT 3.2x2.2 - UIUC PROP DATABASE VOL 2\n")
            f.write("# Archivo origen avance: mi_3.2x2.2_0544rd_20051.txt\n")
            f.write("# Archivo origen estatico: mi_3.2x2.2_static_0519rd.txt\n")
            f.write(f"# Supuestos: D={self.assumptions['D_m']} m; rho={self.assumptions['rho_kg_m3']} kg/m3; RPM={self.assumptions['nominal_rpm']}\n")
            f.write("# Distincion metrologica: medido = tabulado UIUC; supuesto = referencia fija; calculado = transformacion fisica\n")
            
            writer = csv.writer(f)
            writer.writerow(header_cols)
            for r in self.processed_data:
                writer.writerow([
                    r["punto"],
                    f"{r['J_medido']:.6f}",
                    f"{r['CT_medido']:.6f}",
                    f"{r['CP_medido']:.6f}",
                    f"{r['eta_registrada']:.6f}",
                    f"{r['V_m_s']:.6f}",
                    f"{r['V_km_h']:.6f}",
                    f"{r['Empuje_N']:.6f}",
                    f"{r['Empuje_gf']:.4f}",
                    f"{r['Potencia_eje_W']:.6f}",
                    f"{r['Potencia_traccion_W']:.6f}",
                    f"{r['eta_calculada']:.6f}",
                    f"{r['delta_eta_reg_menos_calc']:+.6e}",
                    f"{r['error_relativo_eta_pct']:.6f}",
                    f"{r['cota_redondeo_propagado']:.6e}",
                    str(r["es_atribuible_a_redondeo"]),
                    f"{r['Mach_punta']:.4f}",
                    f"{r['Re_cuerda_075']:.1f}"
                ])


def parse_arguments() -> argparse.Namespace:
    """Configura y parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Procesamiento aerodinámico metrológico de ensayos de hélices UIUC."
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Ruta al archivo de datos de avance (e.g. mi_3.2x2.2_0544rd_20051.txt)"
    )
    parser.add_argument(
        "--static", "-s",
        type=str,
        default=None,
        help="Ruta al archivo de datos estáticos (e.g. mi_3.2x2.2_static_0519rd.txt)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Ruta de destino para el CSV procesado"
    )
    parser.add_argument(
        "--diameter", "-d",
        type=float,
        default=0.08128,
        help="Diámetro de la hélice en metros (defecto: 0.08128 m = 3.2 in)"
    )
    parser.add_argument(
        "--rpm",
        type=float,
        default=20051.0,
        help="Velocidad rotacional nominal en RPM (defecto: 20051.0)"
    )
    parser.add_argument(
        "--rho",
        type=float,
        default=1.225,
        help="Densidad atmosférica en kg/m3 (defecto: 1.225 kg/m3 ISA nivel del mar)"
    )
    return parser.parse_args()


def main():
    """Función de ejecución CLI principal con descubrimiento robusto de rutas."""
    args = parse_arguments()
    root_dir = find_workspace_root()

    input_file = (
        Path(args.input) if args.input else
        root_dir / "entradas" / "investigacion-aeronautica" / "fuentes" / "uiuc_propdb" / "mi_3.2x2.2_0544rd_20051.txt"
    )
    static_file = (
        Path(args.static) if args.static else
        root_dir / "entradas" / "investigacion-aeronautica" / "fuentes" / "uiuc_propdb" / "mi_3.2x2.2_static_0519rd.txt"
    )
    output_csv = (
        Path(args.output) if args.output else
        root_dir / "salidas" / "uiuc_mi_3.2x2.2_20051_procesado.csv"
    )

    print("=" * 80)
    print("PROCESAMIENTO AERODINÁMICO UIUC - HÉLICE MICRO INVENT 3.2x2.2 @ 20.051 RPM")
    print("=" * 80)
    print(f"Raíz de trabajo detectada: {root_dir}")
    print(f"Archivo de entrada avance: {input_file}")
    print(f"Archivo de entrada estático: {static_file}")
    print(f"Archivo de salida CSV: {output_csv}")

    processor = PropellerUIUCProcessor(
        filepath_or_str=str(input_file),
        static_filepath=str(static_file) if static_file.exists() else None,
        diameter_m=args.diameter,
        rho_kg_m3=args.rho,
        nominal_rpm=args.rpm
    )
    processor.load_data()
    processor.process()
    processor.export_csv(str(output_csv))
    stats = processor.get_summary_statistics()

    print("\n--- CLASIFICACIÓN RIGUROSA DE VARIABLES ---")
    print("1. DATOS MEDIDOS / REGISTRADOS:")
    print("   - J (coeficiente de avance): [0.044195 .. 0.448667] (19 puntos)")
    print("   - CT (coeficiente de empuje): [0.124104 .. 0.041281]")
    print("   - CP (coeficiente de potencia): [0.058227 .. 0.035779]")
    print("   - eta (eficiencia registrada): [0.094195 .. 0.517650]")
    print(f"   - RPM nominal de ensayo: {args.rpm:.1f} rpm")
    if stats.get("static_comparison"):
        sc = stats["static_comparison"]
        print(f"   - Benchmark estático (0519rd @ {sc['RPM_static']:.0f} RPM): CT={sc['CT_static']:.6f}, CP={sc['CP_static']:.6f}")

    print("\n2. SUPUESTOS ADOPTADOS:")
    print(f"   - Diámetro D: {args.diameter} m (3.2 pulgadas)")
    print(f"   - Densidad del aire rho: {args.rho} kg/m3 (ISA a nivel del mar)")
    print(f"   - Frecuencia rotacional n: {args.rpm/60.0:.4f} rev/s (constante nominal)")
    print("   - Entorno: Flujo incompresible libre, hélice rígida aislada sin conducto ni carenado")

    print("\n3. CÁLCULOS ANALÍTICOS DERIVADOS:")
    print(f"   - Rango de Velocidad: [{stats['V_min_km_h']:.2f} km/h .. {stats['V_max_km_h']:.2f} km/h] ([{stats['V_min_m_s']:.2f} m/s .. {stats['V_max_m_s']:.2f} m/s])")
    print(f"   - Rango de Empuje: [{stats['T_min_N']:.4f} N .. {stats['T_max_N']:.4f} N] ([{stats['T_min_N']*1000/G_ACCEL:.2f} gf .. {stats['T_max_N']*1000/G_ACCEL:.2f} gf])")
    print(f"   - Rango de Potencia de eje: [{stats['P_min_W']:.4f} W .. {stats['P_max_W']:.4f} W]")
    print(f"   - Eficiencia máxima registrada: {stats['eta_max']*100:.2f}% en J={stats['J_en_eta_max']:.4f} (V={stats['V_kmh_en_eta_max']:.2f} km/h)")
    print(f"   - Mach en punta de pala: [{stats['Mach_punta_min']:.3f} .. {stats['Mach_punta_max']:.3f}] (régimen subsónico incompresible)")
    print(f"   - Reynolds seccional (0.75R): [{stats['Re_cuerda_075_min']:.0f} .. {stats['Re_cuerda_075_max']:.0f}] (régimen laminar de microescala)")
    print(f"   - Coeficiente de avance de empuje nulo estimado (J0): J0 ≈ {stats['J0_estimado']:.4f}")

    print("\n--- COMPARACIÓN METROLÓGICA (eta registrada vs J*CT/CP) ---")
    print(f"   - Máxima diferencia absoluta |eta_reg - eta_calc|: {stats['max_abs_delta_eta']:.4e}")
    print(f"   - Máxima diferencia relativa: {stats['max_rel_diff_pct']:.4f}%")
    print(f"   - ¿Todos los puntos dentro del margen de redondeo tabular (6 decimales)?: {stats['all_within_rounding_bound']}")
    print("   - NOTA CRÍTICA: La discrepancia residual (~1e-5) es un residuo de redondeo numérico ASCII.")
    print("     La incertidumbre experimental del banco (±1% a ±3%) es > 400 veces mayor.")

    print("\n--- COMPARACIÓN CON VELOCIDAD OBJETIVO DE 600 km/h ---")
    print(f"   - Velocidad ensayada máxima: {stats['V_max_km_h']:.2f} km/h ({stats['V_max_m_s']:.2f} m/s)")
    print(f"   - Velocidad de referencia: {stats['V_ref_kmh']:.2f} km/h ({stats['V_ref_kmh']/3.6:.2f} m/s)")
    print(f"   - Déficit de velocidad: {stats['diferencia_kmh_con_600']:.2f} km/h ({stats['diferencia_ms_con_600']:.2f} m/s)")
    print(f"   - Factor de exceso: 600 km/h es {stats['factor_velocidad_600_vs_max']:.2f}x la velocidad máxima ensayada")
    print(f"   - Coeficiente de avance necesario a 600 km/h: J = {stats['J_hipotetico_a_600kmh']:.4f}")
    print("   - ADVERTENCIAS FÍSICAS:")
    print(f"     1. A J = {stats['J_hipotetico_a_600kmh']:.2f} >> J0 ({stats['J0_estimado']:.2f}), la hélice opera en frenado molinillo severo (CT << 0).")
    print("     2. La presión dinámica a 600 km/h (17.0 kPa) supera en > 180x la máxima del ensayo (90 Pa),")
    print("        destruyendo mecánicamente la microhélice por flexión y flutter aeroelástico.")
    print("     3. Incompatibilidad de transferencia: El ventilador C02 (conducto, solidez, estatores, fluido CO2)")
    print("        no guarda relación física ni similitud dinámica con una hélice abierta libre.")
    print("\nProcesamiento concluido exitosamente.")


if __name__ == "__main__":
    main()
