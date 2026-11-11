#!/usr/bin/env python3
"""
Modelo Térmico Concentrado de Sensibilidad (1 Nodo)
===================================================

Ecuación diferencial gobernante:
    C * (dT/dt) = P_loss - (T - T_amb) / R

Solución analítica exacta (con T(0) = T_amb):
    T(t) = T_amb + R * P_loss * (1 - exp(-t / (R * C)))
    dT/dt = (P_loss / C) * exp(-t / (R * C))

Propósito:
    Análisis exploratorio de sensibilidad paramétrica para el alojamiento
    compacto del motor (escenario C01/C02), NO diseño térmico definitivo.

Variables y Unidades:
    C      : Capacidad calorífica concentrada [J/K]
    R      : Resistencia térmica concentrada hacia el ambiente [K/W]
    P_loss : Pérdida térmica disipada supuesta [W] (74.2 W, no validada)
    T_amb  : Temperatura ambiente [°C] (25.0 °C)
    t      : Tiempo transcurrido [s]
    tau    : Constante de tiempo térmica tau = R * C [s]
    T(t)   : Temperatura del nodo en el instante t [°C]
    T_ss   : Temperatura en régimen estacionario T_ss = T_amb + R * P_loss [°C]

Umbral ilustrativo de contraste:
    T_umbral = 80.0 °C, tomado exclusivamente como referencia metodológica
    de la fuente NASA (Weinstein et al., AIAA SciTech 2024,
    https://ntrs.nasa.gov/api/citations/20230017299/downloads/Weinstein_SciTech2024_Final.pdf?attachment=true).
    No representa un límite térmico universal para toda máquina eléctrica.
"""

from dataclasses import dataclass
import math
import csv
import os
from typing import List, Dict, Optional, Tuple, Any


@dataclass(frozen=True)
class LumpedThermalModel:
    """
    Modelo de parámetros concentrados de 1 nodo térmico.
    """
    C: float       # Capacidad térmica [J/K]
    R: float       # Resistencia térmica [K/W]
    P_loss: float  # Potencia disipada en forma de calor [W]
    T_amb: float   # Temperatura ambiente [°C]

    def __post_init__(self):
        if self.C <= 0.0:
            raise ValueError(f"La capacidad térmica C debe ser positiva (C={self.C})")
        if self.R <= 0.0:
            raise ValueError(f"La resistencia térmica R debe ser positiva (R={self.R})")
        if self.P_loss < 0.0:
            raise ValueError(f"La pérdida P_loss debe ser no negativa (P_loss={self.P_loss})")

    @property
    def tau(self) -> float:
        """Constante de tiempo térmica tau = R * C [s]."""
        return self.R * self.C

    @property
    def delta_T_ss(self) -> float:
        """Sobretemperatura en régimen permanente: Delta T_ss = R * P_loss [K]."""
        return self.R * self.P_loss

    @property
    def T_ss(self) -> float:
        """Temperatura asintótica en régimen permanente: T_ss = T_amb + R * P_loss [°C]."""
        return self.T_amb + self.delta_T_ss

    @property
    def initial_dT_dt(self) -> float:
        """Tasa inicial de calentamiento (t=0): dT/dt = P_loss / C [K/s]."""
        return self.P_loss / self.C

    def temperature(self, t: float) -> float:
        """
        Calcula la temperatura analítica en el instante t [s], con T(0) = T_amb.
        T(t) = T_amb + R * P_loss * (1 - exp(-t / tau)) [°C]
        """
        if t < 0.0:
            raise ValueError(f"El tiempo t debe ser no negativo (t={t})")
        return self.T_amb + self.delta_T_ss * (1.0 - math.exp(-t / self.tau))

    def delta_temperature(self, t: float) -> float:
        """
        Calcula el incremento de temperatura respecto a T_amb en el instante t [s].
        Delta T(t) = R * P_loss * (1 - exp(-t / tau)) [K]
        """
        if t < 0.0:
            raise ValueError(f"El tiempo t debe ser no negativo (t={t})")
        return self.delta_T_ss * (1.0 - math.exp(-t / self.tau))

    def dT_dt(self, t: float) -> float:
        """
        Derivada temporal analítica de la temperatura en el instante t [s].
        dT/dt(t) = (P_loss / C) * exp(-t / tau) [K/s]
        """
        if t < 0.0:
            raise ValueError(f"El tiempo t debe ser no negativo (t={t})")
        return (self.P_loss / self.C) * math.exp(-t / self.tau)

    def time_to_temperature(self, T_target: float) -> Optional[float]:
        """
        Calcula el tiempo necesario para alcanzar una temperatura objetivo T_target [°C].
        Retorna:
            - t en segundos si T_amb <= T_target < T_ss
            - 0.0 si T_target <= T_amb
            - None si T_target >= T_ss (temperatura inalcanzable asintóticamente)
        """
        if T_target <= self.T_amb:
            return 0.0
        if T_target >= self.T_ss:
            return None  # Asintóticamente inalcanzable
        
        fraction = (T_target - self.T_amb) / self.delta_T_ss
        return -self.tau * math.log(1.0 - fraction)

    def solve_rk4(self, t_eval: List[float], dt: float = 0.005) -> Dict[float, float]:
        """
        Integra numéricamente la EDO mediante Runge-Kutta de orden 4 (RK4)
        para verificación cruzada contra la solución analítica.
        """
        if not t_eval:
            return {}
        
        sorted_times = sorted(t_eval)
        t_max = sorted_times[-1]
        
        # Función derivada: dT/dt = f(t, T) = (P_loss - (T - T_amb)/R) / C
        def f(_t: float, temp: float) -> float:
            return (self.P_loss - (temp - self.T_amb) / self.R) / self.C

        results = {}
        t_curr = 0.0
        T_curr = self.T_amb
        
        # Almacenar t=0 si está solicitado
        if 0.0 in t_eval:
            results[0.0] = T_curr
            
        time_idx = 0
        while time_idx < len(sorted_times) and sorted_times[time_idx] <= 0.0:
            time_idx += 1

        while t_curr < t_max and time_idx < len(sorted_times):
            target_t = sorted_times[time_idx]
            step = min(dt, target_t - t_curr)
            
            # Pasos RK4
            k1 = f(t_curr, T_curr)
            k2 = f(t_curr + 0.5 * step, T_curr + 0.5 * step * k1)
            k3 = f(t_curr + 0.5 * step, T_curr + 0.5 * step * k2)
            k4 = f(t_curr + step, T_curr + step * k3)
            
            T_curr += (step / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            t_curr += step
            
            if math.isclose(t_curr, target_t, abs_tol=1e-9):
                results[target_t] = T_curr
                time_idx += 1
                
        return results


def run_parametric_study(
    C_values: List[float] = [10.0, 50.0, 100.0],
    R_values: List[float] = [1.0, 3.0, 10.0],
    t_values: List[float] = [10.0, 30.0, 120.0],
    P_loss: float = 74.2,
    T_amb: float = 25.0,
    T_illustrative: float = 80.0
) -> List[Dict[str, Any]]:
    """
    Ejecuta la matriz completa de combinaciones de C, R y t.
    Devuelve una lista de diccionarios estructurados con todas las métricas,
    unidades y clasificaciones epistemológicas.
    """
    records = []
    
    for C in C_values:
        for R in R_values:
            model = LumpedThermalModel(C=C, R=R, P_loss=P_loss, T_amb=T_amb)
            t_80 = model.time_to_temperature(T_illustrative)
            
            # Comprobación numérica RK4 para los tiempos evaluados
            rk4_results = model.solve_rk4(t_values, dt=0.005)
            
            for t in t_values:
                T_analytic = model.temperature(t)
                delta_T = model.delta_temperature(t)
                rate_dT_dt = model.dT_dt(t)
                T_rk4 = rk4_results.get(t, float('nan'))
                abs_rk4_diff = abs(T_analytic - T_rk4) if not math.isnan(T_rk4) else float('nan')
                
                exceeds_80C = T_analytic >= T_illustrative
                margin_to_80C = T_illustrative - T_analytic
                
                # Clasificación de régimen térmico aproximado según t / tau
                ratio_t_tau = t / model.tau
                if ratio_t_tau < 0.2:
                    regime = "Casi adiabático (dominado por C)"
                elif ratio_t_tau > 2.5:
                    regime = "Cuasi estacionario (dominado por R)"
                else:
                    regime = "Transitorio acoplado (C y R)"

                records.append({
                    "id_caso": f"C{int(C)}_R{int(R)}_t{int(t)}",
                    "C_J_K": C,
                    "R_K_W": R,
                    "P_loss_W": P_loss,
                    "T_amb_degC": T_amb,
                    "tau_s": model.tau,
                    "t_eval_s": t,
                    "t_over_tau": round(ratio_t_tau, 4),
                    "regimen_dinamico": regime,
                    "dT_dt_inicial_K_s": round(model.initial_dT_dt, 4),
                    "dT_dt_actual_K_s": round(rate_dT_dt, 4),
                    "T_analitica_degC": round(T_analytic, 3),
                    "delta_T_K": round(delta_T, 3),
                    "T_rk4_degC": round(T_rk4, 3),
                    "error_rk4_K": round(abs_rk4_diff, 10),
                    "T_estacionaria_degC": round(model.T_ss, 3),
                    "delta_T_estacionaria_K": round(model.delta_T_ss, 3),
                    "umbral_ilustrativo_degC": T_illustrative,
                    "supera_umbral_80C": exceeds_80C,
                    "margen_seguridad_80C_K": round(margin_to_80C, 3),
                    "t_alcance_80C_s": round(t_80, 3) if t_80 is not None else "Inalcanzable",
                    "categoria_epistemica_temperatura": "Calculo analitico de sensibilidad (no medicion)",
                    "fuente_potencia_perdida": "Supuesto de disipacion C01/C02 (668 W eje, eta=0.90, no validado)",
                    "fuente_umbral_referencia": "NASA SciTech 2024 Weinstein et al. (referencia ilustrativa)"
                })
                
    return records


def export_to_csv(records: List[Dict[str, Any]], output_path: str) -> None:
    """
    Exporta la lista de resultados a un archivo CSV estructurado.
    """
    if not records:
        return
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fieldnames = list(records[0].keys())
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def print_summary_table(records: List[Dict[str, Any]]) -> None:
    """
    Imprime por consola una tabla resumen formateada.
    """
    header = (
        f"{'Caso':16} | {'C [J/K]':7} | {'R [K/W]':7} | {'tau [s]':7} | "
        f"{'t [s]':5} | {'T(t) [°C]':9} | {'dT/dt [K/s]':12} | "
        f"{'>=80°C':6} | {'Margen 80°C':11} | {'t_80C [s]':10} | {'T_ss [°C]':9}"
    )
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)
    for r in records:
        t_80_str = f"{r['t_alcance_80C_s']:.2f}" if isinstance(r['t_alcance_80C_s'], float) else str(r['t_alcance_80C_s'])
        print(
            f"{r['id_caso']:16} | {r['C_J_K']:7.1f} | {r['R_K_W']:7.1f} | {r['tau_s']:7.1f} | "
            f"{r['t_eval_s']:5.1f} | {r['T_analitica_degC']:9.2f} | {r['dT_dt_actual_K_s']:12.3f} | "
            f"{str(r['supera_umbral_80C']):6} | {r['margen_seguridad_80C_K']:11.2f} | {t_80_str:10} | {r['T_estacionaria_degC']:9.2f}"
        )
    print(separator)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "sensibilidad_termica.csv")
    
    print("================================================================================")
    print("MODELO TÉRMICO CONCENTRADO DE SENSIBILIDAD - MOTOR ESCENARIO C01/C02")
    print("Parámetros base: Tamb = 25.0 °C, P_loss = 74.2 W (hipotética, no validada)")
    print("Umbral de referencia ilustrativo: 80.0 °C (NASA SciTech 2024)")
    print("================================================================================")
    
    records = run_parametric_study()
    print_summary_table(records)
    export_to_csv(records, csv_path)
    print(f"\n[OK] Resultados exportados exitosamente a: {csv_path}")
    print(f"[OK] Total de casos evaluados: {len(records)} registros.")


if __name__ == "__main__":
    main()
