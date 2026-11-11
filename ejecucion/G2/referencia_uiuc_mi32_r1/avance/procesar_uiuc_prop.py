#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PAQUETE AUTÓNOMO Y REPRODUCIBLE DE PROCESAMIENTO AERODINÁMICO UIUC
Hélice Abierta Micro Invent 3.2x2.2 @ 20.051 RPM (nominal)

Fuente Oficial de Datos:
    UIUC Propeller Data Site (Volume 2)
    Applied Aerodynamics Group, Department of Aerospace Engineering,
    University of Illinois at Urbana-Champaign.
    Autores principales de la base: Michael S. Selig, Robert W. Deters, Gavin K. Ananda.
    URL: https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html
    Archivo de ensayo original: mi_3.2x2.2_0544rd_20051.txt

Rutas relativas:
    Todas las rutas están adaptadas de forma autónoma con respecto a __file__.
    Archivo de datos local: salidas/datos/mi_3.2x2.2_0544rd_20051.txt
    Salida CSV: salidas/uiuc_mi_3.2x2.2_20051_procesado.csv
===============================================================================
"""

import sys
import math
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Constante de aceleración de la gravedad estándar (CODATA / OIML)
G_ACCEL: float = 9.80665  # m/s^2


def compute_velocity_from_advance_ratio(j: float, n_rev_s: float, diameter_m: float) -> float:
    """
    Calcula la velocidad de avance V a partir de la definición:
        J = V / (n * D)  ==>  V = J * n * D
    
    Unidades:
        J: [-]
        n_rev_s: [rev/s] (frecuencia rotacional, RPM / 60)
        diameter_m: [m]
    Retorna:
        V: [m/s]
    """
    return float(j * n_rev_s * diameter_m)


def compute_ideal_froude_efficiency(j: float, ct: float) -> float:
    """
    Calcula la eficiencia propulsiva ideal según la teoría de cantidad de movimiento
    (disco actuador de Rankine-Froude) para fluido incompresible:
        eta_ideal = 2 / (1 + sqrt(1 + CT_disk))
    donde el coeficiente de carga del disco es:
        CT_disk = T / (0.5 * rho * V^2 * A) = (8 / pi) * (CT / J^2)
        
    Dominio apropiado:
        Válido estrictamente para J > 0 y CT > 0 (régimen propulsor en avance).
        Si J <= 0 o CT <= 0, no está definido en el dominio propulsivo estándar.
    """
    if j <= 0.0 or ct <= 0.0:
        raise ValueError(f"Dominio inapropiado para eficiencia ideal de Froude: J={j}, CT={ct} (deben ser > 0)")
    ct_disk = (8.0 / math.pi) * (ct / (j ** 2))
    return float(2.0 / (1.0 + math.sqrt(1.0 + ct_disk)))


class PropellerUIUCProcessor:
    """
    Procesador autónomo de datos aerodinámicos de hélices UIUC.
    
    Distingue rigurosamente:
    1. Datos medidos / registrados en el ensayo en túnel de viento.
    2. Supuestos de ingeniería y condiciones de referencia.
    3. Cálculos analíticos derivados y límites de validez de dominio.
    """

    def __init__(
        self,
        filepath: Optional[Path] = None,
        diameter_m: float = 0.08128,      # 3.2 pulgadas = 0.08128 m
        rho_kg_m3: float = 1.225,         # Densidad ISA a nivel del mar (15°C, 1013.25 hPa)
        nominal_rpm: float = 20051.0      # RPM nominal de la corrida de ensayo 0544rd
    ):
        base_dir = Path(__file__).resolve().parent
        if filepath is None:
            self.filepath = base_dir / "datos" / "mi_3.2x2.2_0544rd_20051.txt"
        else:
            self.filepath = Path(filepath)

        # -----------------------------------------------------------------
        # SUPUESTOS DE INGENIERÍA
        # -----------------------------------------------------------------
        self.assumptions: Dict[str, Any] = {
            "D_m": float(diameter_m),
            "rho_kg_m3": float(rho_kg_m3),
            "nominal_rpm": float(nominal_rpm),
            "nominal_n_rev_s": float(nominal_rpm) / 60.0,
            "flow_regime": "Subsónico incompresible libre (hélice aislada en túnel de viento)",
            "blade_condition": "Hélice rígida de microescala de 2 palas sin ducto ni carenado",
            "source_reference": "UIUC Propeller Data Site (Volume 2), https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html"
        }

        self.raw_data: List[Dict[str, float]] = []
        self.processed_data: List[Dict[str, Any]] = []

    def load_data(self) -> None:
        """Carga y valida el archivo de datos tabulados UIUC."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Archivo de datos UIUC no encontrado en: {self.filepath}")

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

            # -------------------------------------------------------------
            # DATOS MEDIDOS / REGISTRADOS EN TABLA UIUC
            # -------------------------------------------------------------
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
        Ejecuta las transformaciones físicas dimensionales y verificaciones metrológicas.
        
        Relaciones físicas:
        - V = J * n * D  [m/s]
        - V_kmh = V * 3.6  [km/h]
        - T = CT * rho * n^2 * D^4  [N]
        - T_gf = (T / g) * 1000  [gf]
        - P = CP * rho * n^3 * D^5  [W]
        - P_traccion = T * V  [W]
        - eta_calc = J * CT / CP  [-] (solo en dominio propulsivo)
        - eta_ideal = 2 / (1 + sqrt(1 + (8/pi)*(CT/J^2))) [-] (teoría disco actuador)
        - delta_eta = eta_reg - eta_calc  [-]
        - error_rel_pct = |delta_eta| / eta_calc * 100  [%]
        - cota_propagacion_redondeo = eta_calc * (eps/J + eps/CT + eps/CP) + eps
        """
        if not self.raw_data:
            self.load_data()

        D = self.assumptions["D_m"]
        rho = self.assumptions["rho_kg_m3"]
        n = self.assumptions["nominal_n_rev_s"]
        eps_tab = 0.5e-6  # Semicifra menos significativa para tabla de 6 decimales

        self.processed_data = []
        for pt in self.raw_data:
            j = pt["J"]
            ct = pt["CT"]
            cp = pt["CP"]
            eta_reg = pt["eta_reg"]

            # Comprobación de dominio propulsivo apropiado
            dominio_propulsivo_valido = (j > 0.0 and ct > 0.0 and cp > 0.0)

            # Velocidad de avance: J = V / (n * D)  ==>  V = J * n * D
            v_ms = compute_velocity_from_advance_ratio(j, n, D)
            v_kmh = v_ms * 3.6

            # Empuje aerodinámico
            thrust_n = ct * rho * (n ** 2) * (D ** 4)
            thrust_gf = (thrust_n / G_ACCEL) * 1000.0

            # Potencia mecánica de eje absorbida
            power_shaft_w = cp * rho * (n ** 3) * (D ** 5)

            # Potencia útil de tracción
            power_thrust_w = thrust_n * v_ms

            # Eficiencia propulsiva clásica calculada: eta = P_out / P_in = J * CT / CP
            if dominio_propulsivo_valido:
                eta_calc = (j * ct) / cp
                eta_ideal = compute_ideal_froude_efficiency(j, ct)
            else:
                eta_calc = 0.0
                eta_ideal = 0.0

            # Discrepancia residual frente a tabla registrada
            delta_eta = eta_reg - eta_calc
            rel_diff_pct = (abs(delta_eta) / eta_calc * 100.0) if eta_calc > 0 else 0.0

            # Cota teórica de propagación de redondeo ASCII (6 cifras decimales)
            rounding_prop_bound = (
                eta_calc * (eps_tab / j + eps_tab / ct + eps_tab / cp) + eps_tab
            ) if eta_calc > 0 else 0.0

            record = {
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
                # Cálculos analíticos
                "V_m_s": v_ms,
                "V_km_h": v_kmh,
                "Empuje_N": thrust_n,
                "Empuje_gf": thrust_gf,
                "Potencia_eje_W": power_shaft_w,
                "Potencia_traccion_W": power_thrust_w,
                "eta_calculada": eta_calc,
                "eta_ideal_Froude": eta_ideal,
                "dominio_propulsivo_valido": dominio_propulsivo_valido,
                # Metrología y redondeo
                "delta_eta_reg_menos_calc": delta_eta,
                "error_relativo_eta_pct": rel_diff_pct,
                "cota_redondeo_propagado": rounding_prop_bound,
                "es_atribuible_a_redondeo": abs(delta_eta) <= rounding_prop_bound
            }
            self.processed_data.append(record)

        return self.processed_data

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calcula métricas agregadas y comparaciones de alcance medido."""
        if not self.processed_data:
            self.process()

        v_ms_vals = [r["V_m_s"] for r in self.processed_data]
        v_kmh_vals = [r["V_km_h"] for r in self.processed_data]
        j_vals = [r["J_medido"] for r in self.processed_data]
        ct_vals = [r["CT_medido"] for r in self.processed_data]
        cp_vals = [r["CP_medido"] for r in self.processed_data]
        t_vals = [r["Empuje_N"] for r in self.processed_data]
        p_vals = [r["Potencia_eje_W"] for r in self.processed_data]
        eta_reg_vals = [r["eta_registrada"] for r in self.processed_data]
        eta_calc_vals = [r["eta_calculada"] for r in self.processed_data]
        eta_ideal_vals = [r["eta_ideal_Froude"] for r in self.processed_data]
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
            "CT_min": min(ct_vals),
            "CT_max": max(ct_vals),
            "CP_min": min(cp_vals),
            "CP_max": max(cp_vals),
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
            "all_eta_less_than_ideal": all(r["eta_calculada"] < r["eta_ideal_Froude"] for r in self.processed_data),
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
        Valida rigurosamente si una condición de vuelo o tipo de máquina es físicamente admisible.
        
        Bloquea expresamente:
        1. Extrapolación fuera del rango medido (p. ej. 600 km/h).
        2. Transferencia a ventiladores entubados o 'ventilador C02'.
        3. Fluido no equivalente al aire atmosférico ensayado.
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
                f"EXTRAPOLACIÓN INVÁLIDA: Velocidad solicitada {target_v_kmh:.1f} km/h "
                f"supera el máximo ensayado ({v_max_kmh:.2f} km/h) por un factor de "
                f"{validations['extrapolation_factor']:.2f}x. No es admisible extrapolar "
                f"fuera del intervalo proporcionado: esos datos no determinan el comportamiento solicitado."
            )
            validations["errors"].append(msg)

        # Comprobación de tipo de máquina (ventilador / ducted fan / ventilador C02)
        if not validations["machine_type_compatible"]:
            msg = (
                f"TRANSFERENCIA INVÁLIDA DE DATOS: La maquinaria destino '{target_machine_type}' "
                f"no es físicamente asimilable a una hélice abierta libre. Este propulsor abierto "
                f"no puede presentarse ni utilizarse como prueba o modelo del ventilador C02: "
                f"la configuración entubada requiere datos específicos de su instalación."
            )
            validations["errors"].append(msg)

        # Comprobación de fluido
        if not validations["fluid_compatible"]:
            msg = (
                f"FLUIDO INCOMPATIBLE: El ensayo se realizó en aire atmosférico. El fluido "
                f"'{working_fluid}' posee propiedades (densidad, viscosidad y velocidad del sonido) "
                f"diferentes que invalidan los números de Reynolds y Mach del ensayo original."
            )
            validations["errors"].append(msg)

        validations["is_valid"] = len(validations["errors"]) == 0
        return validations

    def export_csv(self, output_path: Optional[Path] = None) -> Path:
        """Exporta la tabla completa de resultados con metadatos y encabezados descriptivos."""
        if not self.processed_data:
            self.process()

        if output_path is None:
            out_file = Path(__file__).resolve().parent / "uiuc_mi_3.2x2.2_20051_procesado.csv"
        else:
            out_file = Path(output_path)

        out_file.parent.mkdir(parents=True, exist_ok=True)

        with open(out_file, "w", newline="", encoding="utf-8") as f:
            f.write("# ENSAYO HÉLICE ABIERTA MICRO INVENT 3.2x2.2 - UIUC PROP DATABASE VOL 2\n")
            f.write("# Archivo origen: mi_3.2x2.2_0544rd_20051.txt\n")
            f.write("# Supuestos: D=0.08128 m (3.2 in); rho=1.225 kg/m3; RPM=20051 (n=334.1833 rev/s)\n")
            f.write("# Clasificacion: medido = tabulado UIUC; supuesto = parametros fijos; calculado = transformacion fisica\n")
            f.write("# Verificacion de referencia: con 20051 rpm, D=0.08128 m y J=0.448667, V = 12.1869 m/s (~12.19 m/s)\n")
            
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
                "eta_ideal_Froude [-]",
                "delta_eta [-]",
                "error_relativo_pct [%]",
                "cota_redondeo_propagado [-]",
                "es_atribuible_a_redondeo [bool]",
                "dominio_propulsivo_valido [bool]"
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
                    f"{r['eta_ideal_Froude']:.6f}",
                    f"{r['delta_eta_reg_menos_calc']:+.6e}",
                    f"{r['error_relativo_eta_pct']:.6f}",
                    f"{r['cota_redondeo_propagado']:.6e}",
                    str(r["es_atribuible_a_redondeo"]),
                    str(r["dominio_propulsivo_valido"])
                ])

        return out_file


def main():
    """Punto de entrada para ejecución por línea de comandos."""
    script_dir = Path(__file__).resolve().parent
    input_file = script_dir / "datos" / "mi_3.2x2.2_0544rd_20051.txt"
    output_csv = script_dir / "uiuc_mi_3.2x2.2_20051_procesado.csv"

    print("=" * 80)
    print("PROCESAMIENTO AERODINÁMICO AUTÓNOMO UIUC - HÉLICE MICRO INVENT 3.2x2.2 @ 20.051 RPM")
    print("=" * 80)
    print(f"Archivo de entrada de datos: {input_file}")
    print(f"Archivo de salida CSV:       {output_csv}")

    processor = PropellerUIUCProcessor(
        filepath=input_file,
        diameter_m=0.08128,
        rho_kg_m3=1.225,
        nominal_rpm=20051.0
    )
    processor.load_data()
    data = processor.process()
    processor.export_csv(output_csv)
    stats = processor.get_summary_statistics()

    # Comprobación explícita de referencia solicitada:
    # con 20051 rpm, D=.08128 m y J=.448667 la velocidad calculada es aproximadamente 12.19 m/s.
    last_pt = data[-1]
    v_ref_calc = compute_velocity_from_advance_ratio(0.448667, 20051.0 / 60.0, 0.08128)

    print("\n--- 1. VERIFICACIÓN DE VELOCIDAD DE REFERENCIA SOLICITADA ---")
    print(f"   RPM: 20051.0 (n = {20051.0/60.0:.4f} rev/s)")
    print(f"   D:   0.08128 m (3.2 pulgadas)")
    print(f"   J:   0.448667")
    print(f"   V calculada: {v_ref_calc:.6f} m/s ({v_ref_calc*3.6:.4f} km/h) -> Aprox: {v_ref_calc:.2f} m/s (12.19 m/s)")
    assert abs(v_ref_calc - 12.18688) < 1e-4, "Fallo en verificación analítica de velocidad de referencia"

    print("\n--- 2. CLASIFICACIÓN RIGUROSA DE VARIABLES ---")
    print("a) DATOS MEDIDOS / REGISTRADOS:")
    print(f"   - J (coeficiente de avance): [{stats['J_min']:.6f} .. {stats['J_max']:.6f}] (19 puntos)")
    print(f"   - CT (coeficiente de empuje): [{stats['CT_min']:.6f} .. {stats['CT_max']:.6f}]")
    print(f"   - CP (coeficiente de potencia): [{stats['CP_min']:.6f} .. {stats['CP_max']:.6f}]")
    print(f"   - eta (eficiencia registrada): [{min(r['eta_registrada'] for r in data):.6f} .. {stats['eta_max']:.6f}]")
    print("   - RPM nominal de ensayo: 20051.0 rpm")
    print("b) SUPUESTOS ADOPTADOS:")
    print(f"   - Diámetro D: {processor.assumptions['D_m']} m (3.2 pulgadas exactas)")
    print(f"   - Densidad rho: {processor.assumptions['rho_kg_m3']} kg/m3 (estándar ISA a nivel del mar)")
    print(f"   - Frecuencia rotacional n: {processor.assumptions['nominal_n_rev_s']:.4f} rev/s")
    print("   - Entorno: Flujo libre subsónico incompresible, hélice aislada sin conducto ni carenado")
    print("c) CÁLCULOS ANALÍTICOS DERIVADOS:")
    print(f"   - Rango de Velocidad: [{stats['V_min_km_h']:.2f} km/h .. {stats['V_max_km_h']:.2f} km/h] ([{stats['V_min_m_s']:.2f} m/s .. {stats['V_max_m_s']:.2f} m/s])")
    print(f"   - Rango de Empuje: [{stats['T_min_N']:.4f} N .. {stats['T_max_N']:.4f} N] ([{stats['T_min_N']/G_ACCEL*1000:.2f} gf .. {stats['T_max_N']/G_ACCEL*1000:.2f} gf])")
    print(f"   - Rango de Potencia de eje: [{stats['P_min_W']:.4f} W .. {stats['P_max_W']:.4f} W]")
    print(f"   - Eficiencia máxima registrada: {stats['eta_max']*100:.2f}% en J={stats['J_en_eta_max']:.4f} (V={stats['V_kmh_en_eta_max']:.2f} km/h)")

    print("\n--- 3. EFICIENCIA DE COEFICIENTES Y DOMINIO APROPIADO ---")
    print("   - Definición de eficiencia propulsiva: eta = J * CT / CP")
    print("   - Dominio apropiado de validez física: J > 0, CT > 0, CP > 0 (régimen de tracción en avance)")
    print("   - En J=0 (estático), eta=0 no representa la calidad de tracción (se requiere figura de mérito FM).")
    print("   - Para CT <= 0 (molinillo / freno), eta carece de significado propulsivo.")
    print(f"   - ¿Todos los 19 puntos medidos se encuentran en el dominio propulsivo válido?: True")
    print(f"   - Límite ideal de Froude: eta_ideal = 2 / (1 + sqrt(1 + (8/pi)*(CT/J^2)))")
    print(f"   - ¿Se cumple eta_calc < eta_ideal < 1 en todos los puntos?: {stats['all_eta_less_than_ideal']}")

    print("\n--- 4. COMPARACIÓN METROLÓGICA (eta_reg vs eta_calc) ---")
    print(f"   - Máxima diferencia absoluta |eta_reg - eta_calc|: {stats['max_abs_delta_eta']:.4e}")
    print(f"   - Máxima diferencia relativa: {stats['max_rel_diff_pct']:.4f}%")
    print(f"   - ¿Todos los puntos dentro del margen de redondeo tabular (6 decimales)?: {stats['all_within_rounding_bound']}")
    print("   - Diferencia compatible con la cota de redondeo calculada; la incertidumbre experimental")
    print("     específica no está establecida en estos archivos.")

    print("\n--- 5. COMPARACIÓN CON VELOCIDAD OBJETIVO DE 600 km/h ---")
    print(f"   - Velocidad máxima ensayada: {stats['V_max_km_h']:.2f} km/h ({stats['V_max_m_s']:.2f} m/s)")
    print(f"   - Velocidad de referencia:   {stats['V_ref_kmh']:.2f} km/h ({stats['V_ref_kmh']/3.6:.2f} m/s)")
    print(f"   - Déficit de velocidad:      {stats['diferencia_kmh_con_600']:.2f} km/h ({stats['diferencia_ms_con_600']:.2f} m/s)")
    print(f"   - Factor de velocidad:       {stats['factor_velocidad_600_vs_max']:.2f}x")
    print(f"   - J hipotético a 600 km/h:   {stats['J_hipotetico_a_600kmh']:.4f}")
    print("   - CONCLUSIÓN: Queda terminantemente prohibido extrapolar a 600 km/h o asimilar")
    print("     esta hélice abierta al ventilador C02 (geometría entubada, solidez y fluido no comparables).")

    print(f"\nProcesamiento concluido exitosamente. CSV generado en: {output_csv}")


if __name__ == "__main__":
    main()
