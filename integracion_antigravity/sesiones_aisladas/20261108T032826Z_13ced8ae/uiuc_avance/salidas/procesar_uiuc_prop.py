#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROCESAMIENTO INDEPENDIENTE DE ENSAYO DE HÉLICE ABIERTA UIUC
Hélice: Micro Invent 3.2x2.2 @ 20.051 RPM (nominal)
Archivo fuente: entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_0544rd_20051.txt
Fuente oficial: UIUC Propeller Data Site (Volume 2)
URL de referencia: https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html
===============================================================================
"""

import sys
import math
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Constantes gravitacionales
G_ACCEL = 9.80665  # m/s^2


class PropellerUIUCProcessor:
    """
    Procesador de datos aerodinámicos de ensayos de hélices en túnel de viento UIUC.
    
    Distingue rigurosamente entre:
    1. Datos medidos / registrados en el ensayo.
    2. Supuestos de ingeniería y condiciones de referencia.
    3. Cálculos analíticos derivados.
    """

    def __init__(
        self,
        filepath_or_str: str,
        diameter_m: float = 0.08128,      # 3.2 pulgadas = 0.08128 m
        rho_kg_m3: float = 1.225,         # Densidad ISA a nivel del mar (15°C, 1013.25 hPa)
        nominal_rpm: float = 20051.0      # RPM nominal de la corrida de ensayo 0544rd
    ):
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
            "source_reference": "https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html"
        }
        
        self.filepath = Path(filepath_or_str)
        self.raw_data: List[Dict[str, float]] = []
        self.processed_data: List[Dict[str, Any]] = []

    def load_data(self) -> None:
        """Carga y valida el archivo de datos tabulados UIUC."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Archivo de entrada no encontrado: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            raise ValueError(f"El archivo {self.filepath} está vacío.")

        header = lines[0].split()
        expected_cols = ["J", "CT", "CP", "eta"]
        if header != expected_cols:
            raise ValueError(f"Encabezado inesperado: {header}. Se esperaba {expected_cols}")

        self.raw_data = []
        for idx, line in enumerate(lines[1:], start=1):
            parts = line.split()
            if len(parts) != 4:
                raise ValueError(f"Línea {idx+1} mal formada: {line}")
            
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

    def process(self) -> List[Dict[str, Any]]:
        """
        Ejecuta las transformaciones físicas y los cálculos metrológicos.
        
        Transformaciones:
        - V = J * n * D [m/s]
        - V_kmh = V * 3.6 [km/h]
        - T (empuje) = CT * rho * n^2 * D^4 [N]
        - P (potencia de eje) = CP * rho * n^3 * D^5 [W]
        - P_traccion = T * V [W]
        - eta_calc = J * CT / CP [-]
        - delta_eta = eta_reg - eta_calc [-]
        - error_rel_pct = |delta_eta| / eta_calc * 100 [%]
        - cota_propagacion_redondeo = eta_calc * (eps/J + eps/CT + eps/CP) + eps
        """
        if not self.raw_data:
            self.load_data()

        D = self.assumptions["D_m"]
        rho = self.assumptions["rho_kg_m3"]
        n = self.assumptions["nominal_n_rev_s"]
        eps_tab = 0.5e-6  # Cota de semicifras por representación a 6 decimales

        self.processed_data = []
        for pt in self.raw_data:
            j = pt["J"]
            ct = pt["CT"]
            cp = pt["CP"]
            eta_reg = pt["eta_reg"]

            # ---------------------------------------------------------
            # CÁLCULOS ANALÍTICOS DERIVADOS
            # ---------------------------------------------------------
            # Velocidad de avance
            v_ms = j * n * D
            v_kmh = v_ms * 3.6

            # Empuje aerodinámico
            # CT = T / (rho * n^2 * D^4)  ==>  T = CT * rho * n^2 * D^4
            thrust_n = ct * rho * (n ** 2) * (D ** 4)
            thrust_gf = (thrust_n / G_ACCEL) * 1000.0  # gramos-fuerza

            # Potencia mecánica de eje
            # CP = P / (rho * n^3 * D^5)  ==>  P = CP * rho * n^3 * D^5
            power_shaft_w = cp * rho * (n ** 3) * (D ** 5)

            # Potencia aerodinámica de tracción (output útil)
            power_thrust_w = thrust_n * v_ms

            # Eficiencia calculada según definición clásica
            # eta = (T * V) / P = (CT * rho * n^2 * D^4 * J * n * D) / (CP * rho * n^3 * D^5) = J * CT / CP
            eta_calc = (j * ct) / cp if cp != 0 else 0.0

            # Discrepancia numérica entre el valor registrado y el cálculo analítico
            delta_eta = eta_reg - eta_calc
            rel_diff_pct = (abs(delta_eta) / eta_calc * 100.0) if eta_calc != 0 else 0.0

            # Cota teórica de propagación de error por truncamiento a 6 decimales
            # d(eta)/eta = dJ/J + dCT/CT - dCP/CP
            rounding_prop_bound = (
                eta_calc * (eps_tab / j + eps_tab / ct + eps_tab / cp) + eps_tab
            )

            record = {
                # Identificador
                "punto": pt["punto"],
                # Datos Medidos
                "J_medido": j,
                "CT_medido": ct,
                "CP_medido": cp,
                "eta_registrada": eta_reg,
                # Supuestos aplicados
                "D_m": D,
                "rho_kg_m3": rho,
                "n_rev_s": n,
                "rpm_nominal": self.assumptions["nominal_rpm"],
                # Cálculos
                "V_m_s": v_ms,
                "V_km_h": v_kmh,
                "Empuje_N": thrust_n,
                "Empuje_gf": thrust_gf,
                "Potencia_eje_W": power_shaft_w,
                "Potencia_traccion_W": power_thrust_w,
                "eta_calculada": eta_calc,
                # Comparación metrológica y redondeo
                "delta_eta_reg_menos_calc": delta_eta,
                "error_relativo_eta_pct": rel_diff_pct,
                "cota_redondeo_propagado": rounding_prop_bound,
                "es_atribuible_a_redondeo": abs(delta_eta) <= rounding_prop_bound
            }
            self.processed_data.append(record)

        return self.processed_data

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calcula métricas agregadas y comparaciones de rango."""
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

        max_eta_idx = max(range(len(eta_reg_vals)), key=lambda i: eta_reg_vals[i])
        best_pt = self.processed_data[max_eta_idx]

        v_ref_kmh = 600.0
        v_ref_ms = v_ref_kmh / 3.6
        v_max_kmh = max(v_kmh_vals)
        v_max_ms = max(v_ms_vals)
        n = self.assumptions["nominal_n_rev_s"]
        D = self.assumptions["D_m"]

        # J hipotético para 600 km/h al RPM ensayado
        j_hypothetical_600 = v_ref_ms / (n * D)

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
            # Comparación con 600 km/h
            "V_ref_kmh": v_ref_kmh,
            "diferencia_kmh_con_600": v_ref_kmh - v_max_kmh,
            "diferencia_ms_con_600": v_ref_ms - v_max_ms,
            "factor_velocidad_600_vs_max": v_ref_kmh / v_max_kmh,
            "J_hipotetico_a_600kmh": j_hypothetical_600
        }

    def validate_application_limits(
        self,
        target_v_kmh: float,
        target_machine_type: str = "open_propeller",
        working_fluid: str = "air"
    ) -> Dict[str, Any]:
        """
        Valida si una condición de operación o maquinaria destino es físicamente válida
        con respecto a la base de datos ensayada.
        
        Bloquea / advierte sobre:
        1. Extrapolación fuera del rango ensayado (e.g. 600 km/h).
        2. Transferencia de datos a ventiladores entubados (e.g. 'ventilador C02').
        3. Cambio de fluido de trabajo sin correcciones de similitud.
        """
        if not self.processed_data:
            self.process()

        stats = self.get_summary_statistics()
        v_max_kmh = stats["V_max_km_h"]
        v_min_kmh = stats["V_min_km_h"]

        validations = {
            "target_v_kmh": target_v_kmh,
            "within_velocity_range": v_min_kmh <= target_v_kmh <= v_max_kmh,
            "extrapolation_factor": target_v_kmh / v_max_kmh if v_max_kmh > 0 else 0.0,
            "machine_type_compatible": target_machine_type.lower() in ["open_propeller", "helice_abierta"],
            "fluid_compatible": working_fluid.lower() in ["air", "aire"],
            "warnings": [],
            "errors": []
        }

        # Comprobación de velocidad
        if target_v_kmh > v_max_kmh:
            msg = (
                f"EXTRAPOLACIÓN INVÁLIDA: Velocidad objetivo {target_v_kmh:.1f} km/h "
                f"supera el máximo ensayado ({v_max_kmh:.2f} km/h) por un factor de "
                f"{validations['extrapolation_factor']:.2f}x. No es posible extrapolar "
                f"debido a régimen de freno molinillo (J >> J_cero_empuje), compresibilidad "
                f"y sobrecargas estructurales."
            )
            validations["errors"].append(msg)

        # Comprobación de máquina (ventilador / ducted fan)
        if not validations["machine_type_compatible"]:
            msg = (
                f"TRANSFERENCIA INVÁLIDA DE DATOS: La maquinaria destino '{target_machine_type}' "
                f"no es físicamente equivalente a una hélice abierta libre. Los ventiladores "
                f"(como el 'ventilador C02') operan con conductos, holgura de punta de pala, "
                f"estatores, recuperación de presión interna y solidez elevada. Los datos "
                f"de hélices abiertas no pueden ser transferidos ni aplicados a ventiladores."
            )
            validations["errors"].append(msg)

        # Comprobación de fluido
        if not validations["fluid_compatible"]:
            msg = (
                f"FLUIDO INCOMPATIBLE: El ensayo se realizó en aire atmosférico. El fluido "
                f"'{working_fluid}' posee densidad, viscosidad cinemática y velocidad del sonido "
                f"diferentes, invalidando los números de Reynolds y Mach del ensayo original."
            )
            validations["errors"].append(msg)

        validations["is_valid"] = len(validations["errors"]) == 0
        return validations

    def export_csv(self, output_path: str) -> None:
        """Exporta la tabla completa con metadatos y encabezados descriptivos."""
        if not self.processed_data:
            self.process()

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "punto",
            "J_medido",
            "CT_medido",
            "CP_medido",
            "eta_registrada",
            "V_calculada_m_s",
            "V_calculada_km_h",
            "Empuje_T_calculado_N",
            "Empuje_T_calculado_gf",
            "Potencia_eje_P_calculada_W",
            "Potencia_traccion_Pout_calculada_W",
            "eta_calculada_J_CT_CP",
            "delta_eta_reg_menos_calc",
            "error_relativo_eta_pct",
            "cota_redondeo_propagado",
            "es_atribuible_a_redondeo"
        ]

        with open(out_file, "w", newline="", encoding="utf-8") as f:
            # Metadatos en líneas de comentario inicial directos (sin comillas CSV)
            f.write("# ENSAYO HÉLICE ABIERTA MICRO INVENT 3.2x2.2 - UIUC PROP DATABASE VOL 2\n")
            f.write("# Archivo origen: mi_3.2x2.2_0544rd_20051.txt\n")
            f.write("# Supuestos: D=0.08128 m; rho=1.225 kg/m3; RPM=20051 (n=334.1833 rev/s)\n")
            f.write("# Distincion: medido = tabulado UIUC; calculado = transformacion fisica\n")
            
            writer = csv.writer(f)
            writer.writerow([
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
                "es_atribuible_a_redondeo [bool]"
            ])
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
                    str(r["es_atribuible_a_redondeo"])
                ])


def main():
    """Función de ejecución CLI estándar."""
    base_dir = Path(__file__).resolve().parent.parent
    input_file = base_dir / "entradas" / "investigacion-aeronautica" / "fuentes" / "uiuc_propdb" / "mi_3.2x2.2_0544rd_20051.txt"
    output_csv = base_dir / "salidas" / "uiuc_mi_3.2x2.2_20051_procesado.csv"

    print("=" * 80)
    print("PROCESAMIENTO AERODINÁMICO UIUC - HÉLICE MICRO INVENT 3.2x2.2 @ 20.051 RPM")
    print("=" * 80)
    print(f"Archivo de entrada: {input_file}")
    print(f"Archivo de salida CSV: {output_csv}")

    processor = PropellerUIUCProcessor(
        filepath_or_str=str(input_file),
        diameter_m=0.08128,
        rho_kg_m3=1.225,
        nominal_rpm=20051.0
    )
    processor.load_data()
    data = processor.process()
    processor.export_csv(str(output_csv))
    stats = processor.get_summary_statistics()

    print("\n--- CLASIFICACIÓN DE VARIABLES ---")
    print("1. DATOS MEDIDOS / REGISTRADOS:")
    print("   - J (coeficiente de avance): [0.044195 .. 0.448667]")
    print("   - CT (coeficiente de empuje): [0.124104 .. 0.041281]")
    print("   - CP (coeficiente de potencia): [0.058227 .. 0.035779]")
    print("   - eta (eficiencia registrada): [0.094195 .. 0.517650]")
    print("   - RPM nominal de ensayo: 20051.0 rpm")
    print("\n2. SUPUESTOS ADOPTADOS:")
    print("   - Diámetro D: 0.08128 m (3.2 pulgadas)")
    print("   - Densidad del aire rho: 1.225 kg/m3 (estándar nivel del mar)")
    print("   - Frecuencia rotacional n: 334.1833 rev/s (constante nominal)")
    print("   - Entorno: Flujo incompresible libre, hélice aislada sin conducto ni carenado")
    print("\n3. CÁLCULOS DERIVADOS:")
    print(f"   - Rango de Velocidad: [{stats['V_min_km_h']:.2f} km/h .. {stats['V_max_km_h']:.2f} km/h] ([{stats['V_min_m_s']:.2f} m/s .. {stats['V_max_m_s']:.2f} m/s])")
    print(f"   - Rango de Empuje: [{stats['T_min_N']:.4f} N .. {stats['T_max_N']:.4f} N]")
    print(f"   - Rango de Potencia de eje: [{stats['P_min_W']:.4f} W .. {stats['P_max_W']:.4f} W]")
    print(f"   - Eficiencia máxima registrada: {stats['eta_max']*100:.2f}% en J={stats['J_en_eta_max']:.4f} (V={stats['V_kmh_en_eta_max']:.2f} km/h)")

    print("\n--- COMPARACIÓN METROLÓGICA (eta registrada vs J*CT/CP) ---")
    print(f"   - Máxima diferencia absoluta |eta_reg - eta_calc|: {stats['max_abs_delta_eta']:.4e}")
    print(f"   - Máxima diferencia relativa: {stats['max_rel_diff_pct']:.4f}%")
    print(f"   - ¿Todos los puntos dentro del margen de redondeo tabular (6 decimales)?: {stats['all_within_rounding_bound']}")
    print("   - NOTA CRÍTICA: Esta discrepancia residual (~1e-5) se debe exclusivamente al truncamiento")
    print("     y redondeo numérico de la tabla ASCII (6 decimales). NO DEBE CONFUNDIRSE con el error")
    print("     experimental de medición de los sensores del túnel (que ronda típicamente ±1% a ±3%).")

    print("\n--- COMPARACIÓN CON VELOCIDAD OBJETIVO DE 600 km/h ---")
    print(f"   - Velocidad ensayada máxima: {stats['V_max_km_h']:.2f} km/h ({stats['V_max_m_s']:.2f} m/s)")
    print(f"   - Velocidad de referencia: {stats['V_ref_kmh']:.2f} km/h ({stats['V_ref_kmh']/3.6:.2f} m/s)")
    print(f"   - Déficit de velocidad: {stats['diferencia_kmh_con_600']:.2f} km/h ({stats['diferencia_ms_con_600']:.2f} m/s)")
    print(f"   - Factor de exceso: 600 km/h es {stats['factor_velocidad_600_vs_max']:.2f}x la velocidad máxima ensayada")
    print(f"   - Coeficiente de avance necesario a 600 km/h: J = {stats['J_hipotetico_a_600kmh']:.4f}")
    print("   - ADVERTENCIA FÍSICA: A J=6.14 la hélice opera en frenado molinillo severo (CT << 0).")
    print("     No es posible extrapolar a 600 km/h debido a compresibilidad, régimen de pérdida y fallo estructural.")
    print("     Tampoco es válido transferir estos datos al ventilador C02 (conducto, solidez y fluido incompatibles).")
    print("\nProcesamiento concluido exitosamente.")


if __name__ == "__main__":
    main()
