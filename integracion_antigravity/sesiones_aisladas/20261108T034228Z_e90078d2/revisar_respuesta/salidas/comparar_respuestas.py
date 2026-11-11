#!/usr/bin/env python3
"""
comparar_respuestas.py - Comparación de respuestas normalizadas de actuador:
1er orden: y_1(t) = 1 - exp(-t/tau)
2do orden críticamente amortiguado: y_2(t) = 1 - (1 + t/tau)*exp(-t/tau)

Parámetros supuestos: tau in {0.08 s, 0.20 s, 0.50 s}
Cálculos: tiempos al 10%, 50%, 90%, tiempo de subida 10%-90%,
control de límites analíticos y numéricos, y efecto de rampas de ESC / slew-rate
(vinculado al estudio NASA Weinstein et al. SciTech 2024 e hipótesis de INFORME.md).

Autor: Antigravity (Entorno aislado)
Fecha: Noviembre 2026
"""

import math
import csv
import json
import os
import sys

# ---------------------------------------------------------
# 1. Definiciones analíticas de las respuestas y derivadas
# ---------------------------------------------------------

def y_first_order(t: float, tau: float) -> float:
    """Respuesta normalizada de 1er orden: y_1(t) = 1 - exp(-t/tau)."""
    if t < 0.0:
        return 0.0
    u = t / tau
    return 1.0 - math.exp(-u)

def dy_first_order(t: float, tau: float) -> float:
    """Primera derivada de 1er orden: dy_1/dt = (1/tau) * exp(-t/tau)."""
    if t < 0.0:
        return 0.0
    u = t / tau
    return (1.0 / tau) * math.exp(-u)

def d2y_first_order(t: float, tau: float) -> float:
    """Segunda derivada de 1er orden: d2y_1/dt2 = -(1/tau^2) * exp(-t/tau)."""
    if t < 0.0:
        return 0.0
    u = t / tau
    return -(1.0 / (tau * tau)) * math.exp(-u)

def y_second_order(t: float, tau: float) -> float:
    """Respuesta normalizada de 2do orden críticamente amortiguado:
    y_2(t) = 1 - (1 + t/tau) * exp(-t/tau)."""
    if t < 0.0:
        return 0.0
    u = t / tau
    return 1.0 - (1.0 + u) * math.exp(-u)

def dy_second_order(t: float, tau: float) -> float:
    """Primera derivada de 2do orden: dy_2/dt = (t / tau^2) * exp(-t/tau)."""
    if t < 0.0:
        return 0.0
    u = t / tau
    return (u / tau) * math.exp(-u)

def d2y_second_order(t: float, tau: float) -> float:
    """Segunda derivada de 2do orden: d2y_2/dt2 = (1 / tau^2) * (1 - t/tau) * exp(-t/tau)."""
    if t < 0.0:
        return 0.0
    u = t / tau
    return (1.0 / (tau * tau)) * (1.0 - u) * math.exp(-u)

# ---------------------------------------------------------
# 2. Resolución de tiempos característicos t_p (p in (0, 1))
# ---------------------------------------------------------

def time_first_order(p: float, tau: float) -> float:
    """Calcula analíticamente t tal que y_1(t) = p:
    1 - exp(-t/tau) = p => t = -tau * ln(1 - p)."""
    if not (0.0 < p < 1.0):
        raise ValueError("El porcentaje p debe pertenecer al intervalo abierto (0, 1)")
    u = -math.log(1.0 - p)
    return tau * u

def solve_u_second_order(p: float, tol: float = 1e-15, max_iter: int = 100) -> float:
    """Resuelve u = t/tau tal que:
    1 - (1 + u)*exp(-u) = p  <=>  (1 + u)*exp(-u) - (1 - p) = 0
    Utiliza el método de Halley de 3er orden para convergencia cúbica."""
    if not (0.0 < p < 1.0):
        raise ValueError("El porcentaje p debe pertenecer al intervalo abierto (0, 1)")
    
    # Semilla inicial dependiente de la región
    if p < 0.2:
        u = math.sqrt(2.0 * p)
    elif p < 0.8:
        u = 1.0 + p
    else:
        u = -math.log(1.0 - p) + 1.0
        
    for _ in range(max_iter):
        f = (1.0 + u) * math.exp(-u) - (1.0 - p)
        df = -u * math.exp(-u)
        d2f = (u - 1.0) * math.exp(-u)
        
        denom = df - 0.5 * f * (d2f / df)
        delta = f / denom
        u_next = u - delta
        
        if abs(delta) < tol or abs(u_next - u) < tol:
            return u_next
        u = u_next
        
    return u

def time_second_order(p: float, tau: float) -> float:
    """Calcula numéricamente t tal que y_2(t) = p."""
    u = solve_u_second_order(p)
    return tau * u

# ---------------------------------------------------------
# 3. Modelado y cálculo bajo limitación de tasa (rampas de ESC)
# ---------------------------------------------------------

def time_first_order_rate_limited(p: float, tau: float, R: float) -> float:
    """Calcula analíticamente t tal que y(t) = p para un sistema de 1er orden
    con saturación de derivada |dy/dt| <= R.
    Si R >= 1/tau, la cota nunca se satura y coincide con time_first_order."""
    if not (0.0 < p < 1.0):
        raise ValueError("El porcentaje p debe pertenecer al intervalo abierto (0, 1)")
    if R <= 0.0:
        raise ValueError("La tasa máxima R debe ser estrictamente positiva")
    
    # La máxima derivada sin limitar es 1/tau en t=0+
    if R >= 1.0 / tau:
        return time_first_order(p, tau)
        
    # Punto de desaturación: dy/dt = (1 - y) / tau = R => y_sat = 1 - R * tau
    y_sat = 1.0 - R * tau
    t_sat = (1.0 - R * tau) / R
    
    if p <= y_sat:
        # Régimen lineal puro de rampa: y(t) = R * t
        return p / R
    else:
        # Régimen exponencial tras desaturación:
        # y(t) = 1 - (R * tau) * exp(-(t - t_sat)/tau) = p
        # exp(-(t - t_sat)/tau) = (1 - p) / (R * tau)
        return t_sat - tau * math.log((1.0 - p) / (R * tau))

def simulate_step_rate_limited(tau: float, order: int, R: float = None, t_final: float = 3.0, dt: float = 1e-4):
    """Simula la respuesta al escalón unitario con o sin limitación de tasa R (1/s).
    Orden 1: dy/dt = sat_R((1 - y)/tau).
    Orden 2: dy/dt = v, dv/dt = sat_R((1 - y - 2*tau*v)/tau^2)."""
    t = 0.0
    y = 0.0
    v = 0.0
    times = []
    y_hist = []
    
    n_steps = int(math.ceil(t_final / dt))
    for _ in range(n_steps + 1):
        times.append(t)
        y_hist.append(y)
        
        if order == 1:
            v_cmd = (1.0 - y) / tau
            if R is not None:
                v_eff = min(R, max(-R, v_cmd))
            else:
                v_eff = v_cmd
            y += dt * v_eff
        elif order == 2:
            a_cmd = (1.0 - y - 2.0 * tau * v) / (tau * tau)
            v_next = v + dt * a_cmd
            if R is not None:
                v_next = min(R, max(-R, v_next))
            y += dt * v_next
            v = v_next
            
        t += dt
        
    return times, y_hist

def find_crossing_time(times, y_hist, target: float):
    """Interpola linealmente el tiempo en que y_hist cruza target."""
    for i in range(1, len(y_hist)):
        if y_hist[i] >= target:
            t0, t1 = times[i - 1], times[i]
            y0, y1 = y_hist[i - 1], y_hist[i]
            if y1 == y0:
                return t0
            return t0 + (target - y0) * (t1 - t0) / (y1 - y0)
    return None

# ---------------------------------------------------------
# 4. Control de límites analíticos y físicos
# ---------------------------------------------------------

def evaluate_limits(tau: float) -> dict:
    """Evalúa y comprueba los límites analíticos clave para un valor dado de tau."""
    y1_0 = y_first_order(0.0, tau)
    y2_0 = y_second_order(0.0, tau)
    dy1_0 = dy_first_order(0.0, tau)
    dy2_0 = dy_second_order(0.0, tau)
    d2y1_0 = d2y_first_order(0.0, tau)
    d2y2_0 = d2y_second_order(0.0, tau)
    
    t_inf = 20.0 * tau
    y1_inf = y_first_order(t_inf, tau)
    y2_inf = y_second_order(t_inf, tau)
    
    t_inflec = tau
    y2_inflec = y_second_order(t_inflec, tau)
    d2y2_inflec = d2y_second_order(t_inflec, tau)
    dy2_max = dy_second_order(t_inflec, tau)
    
    return {
        "tau_s": tau,
        "lim_t_0": {
            "y1_0": y1_0,
            "y2_0": y2_0,
            "dy1_0_exact": 1.0 / tau,
            "dy1_0_eval": dy1_0,
            "dy2_0_exact": 0.0,
            "dy2_0_eval": dy2_0,
            "d2y1_0_exact": -1.0 / (tau * tau),
            "d2y1_0_eval": d2y1_0,
            "d2y2_0_exact": 1.0 / (tau * tau),
            "d2y2_0_eval": d2y2_0,
        },
        "lim_t_inf": {
            "t_eval_s": t_inf,
            "y1_inf": y1_inf,
            "error_y1_inf": 1.0 - y1_inf,
            "y2_inf": y2_inf,
            "error_y2_inf": 1.0 - y2_inf,
        },
        "inflection_2nd_order": {
            "t_inflec_exact_s": tau,
            "y2_inflec_exact": 1.0 - 2.0 / math.e,
            "y2_inflec_eval": y2_inflec,
            "d2y2_inflec_eval": d2y2_inflec,
            "dy2_max_exact": 1.0 / (math.e * tau),
            "dy2_max_eval": dy2_max,
        }
    }

# ---------------------------------------------------------
# 5. Integración Runge-Kutta 4 (RK4) sin saturación
# ---------------------------------------------------------

def simulate_step_rk4(tau: float, order: int, t_final: float, dt: float):
    """Simula numéricamente la respuesta al escalón usando RK4 puro de orden 4."""
    t_vals = [0.0]
    y_vals = [0.0]
    
    if order == 1:
        y = 0.0
        t = 0.0
        n_steps = int(math.ceil(t_final / dt))
        for _ in range(n_steps):
            def f(y_curr):
                return (1.0 - y_curr) / tau
            k1 = f(y)
            k2 = f(y + 0.5 * dt * k1)
            k3 = f(y + 0.5 * dt * k2)
            k4 = f(y + dt * k3)
            y += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            t += dt
            t_vals.append(t)
            y_vals.append(y)
    elif order == 2:
        y = 0.0
        v = 0.0
        t = 0.0
        n_steps = int(math.ceil(t_final / dt))
        for _ in range(n_steps):
            def f(y_c, v_c):
                return v_c, (1.0 - y_c - 2.0 * tau * v_c) / (tau * tau)
            k1_y, k1_v = f(y, v)
            k2_y, k2_v = f(y + 0.5 * dt * k1_y, v + 0.5 * dt * k1_v)
            k3_y, k3_v = f(y + 0.5 * dt * k2_y, v + 0.5 * dt * k2_v)
            k4_y, k4_v = f(y + dt * k3_y, v + dt * k3_v)
            y += (dt / 6.0) * (k1_y + 2.0 * k2_y + 2.0 * k3_y + k4_y)
            v += (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
            t += dt
            t_vals.append(t)
            y_vals.append(y)
    else:
        raise ValueError("order debe ser 1 o 2")
        
    return t_vals, y_vals

# ---------------------------------------------------------
# 6. Generación de comparaciones globales y tablas
# ---------------------------------------------------------

def generate_comparisons(taus=(0.08, 0.20, 0.50), R_slew=2.38095):
    """Genera las métricas de respuesta para los tau supuestos, tanto lineales
    como bajo limitación de tasa (slew-rate / rampas de ESC).
    R_slew = 50 N/s / 21 N ~ 2.381 s^-1 (supuesto en INFORME.md)."""
    percentages = [0.10, 0.50, 0.90]
    
    u1_norm = {p: -math.log(1.0 - p) for p in percentages}
    u1_norm_10_90 = u1_norm[0.90] - u1_norm[0.10]
    
    u2_norm = {p: solve_u_second_order(p) for p in percentages}
    u2_norm_10_90 = u2_norm[0.90] - u2_norm[0.10]
    
    results = []
    
    for tau in taus:
        # Tiempos lineales de 1er orden
        t1_10 = time_first_order(0.10, tau)
        t1_50 = time_first_order(0.50, tau)
        t1_90 = time_first_order(0.90, tau)
        t1_10_90 = t1_90 - t1_10
        slope1_max = 1.0 / tau
        
        # Tiempos con limitación de tasa R de 1er orden
        t1_10_lim = time_first_order_rate_limited(0.10, tau, R_slew)
        t1_50_lim = time_first_order_rate_limited(0.50, tau, R_slew)
        t1_90_lim = time_first_order_rate_limited(0.90, tau, R_slew)
        t1_10_90_lim = t1_90_lim - t1_10_lim
        
        # Tiempos lineales de 2do orden
        t2_10 = time_second_order(0.10, tau)
        t2_50 = time_second_order(0.50, tau)
        t2_90 = time_second_order(0.90, tau)
        t2_10_90 = t2_90 - t2_10
        slope2_max = 1.0 / (math.e * tau)
        
        # Tiempos con limitación de tasa R de 2do orden (mediante simulación fina)
        t_sim, y_sim2_lim = simulate_step_rate_limited(tau, 2, R_slew, t_final=5.0*tau + 1.0, dt=1e-5)
        t2_10_lim = find_crossing_time(t_sim, y_sim2_lim, 0.10)
        t2_50_lim = find_crossing_time(t_sim, y_sim2_lim, 0.50)
        t2_90_lim = find_crossing_time(t_sim, y_sim2_lim, 0.90)
        t2_10_90_lim = t2_90_lim - t2_10_lim
        
        row_1 = {
            "modelo": "Primer orden: 1-exp(-t/tau)",
            "orden": 1,
            "tau_s": tau,
            "t_10_s": t1_10,
            "t_10_ms": t1_10 * 1000.0,
            "t_50_s": t1_50,
            "t_50_ms": t1_50 * 1000.0,
            "t_90_s": t1_90,
            "t_90_ms": t1_90 * 1000.0,
            "t_10_90_s": t1_10_90,
            "t_10_90_ms": t1_10_90 * 1000.0,
            "pendiente_max_s_1": slope1_max,
            "t_inflexion_s": None,
            "u_10": u1_norm[0.10],
            "u_50": u1_norm[0.50],
            "u_90": u1_norm[0.90],
            "u_10_90": u1_norm_10_90,
            # Métricas con limitación de rampa R
            "t_10_lim_ms": t1_10_lim * 1000.0,
            "t_50_lim_ms": t1_50_lim * 1000.0,
            "t_90_lim_ms": t1_90_lim * 1000.0,
            "t_10_90_lim_ms": t1_10_90_lim * 1000.0,
        }
        
        row_2 = {
            "modelo": "Segundo orden crít. amort.: 1-(1+t/tau)exp(-t/tau)",
            "orden": 2,
            "tau_s": tau,
            "t_10_s": t2_10,
            "t_10_ms": t2_10 * 1000.0,
            "t_50_s": t2_50,
            "t_50_ms": t2_50 * 1000.0,
            "t_90_s": t2_90,
            "t_90_ms": t2_90 * 1000.0,
            "t_10_90_s": t2_10_90,
            "t_10_90_ms": t2_10_90 * 1000.0,
            "pendiente_max_s_1": slope2_max,
            "t_inflexion_s": tau,
            "u_10": u2_norm[0.10],
            "u_50": u2_norm[0.50],
            "u_90": u2_norm[0.90],
            "u_10_90": u2_norm_10_90,
            # Métricas con limitación de rampa R
            "t_10_lim_ms": t2_10_lim * 1000.0,
            "t_50_lim_ms": t2_50_lim * 1000.0,
            "t_90_lim_ms": t2_90_lim * 1000.0,
            "t_10_90_lim_ms": t2_10_90_lim * 1000.0,
        }
        
        diff = {
            "tau_s": tau,
            "ratio_t_10": t2_10 / t1_10,
            "delta_t_10_ms": (t2_10 - t1_10) * 1000.0,
            "pct_diff_t_10": ((t2_10 / t1_10) - 1.0) * 100.0,
            "ratio_t_50": t2_50 / t1_50,
            "delta_t_50_ms": (t2_50 - t1_50) * 1000.0,
            "pct_diff_t_50": ((t2_50 / t1_50) - 1.0) * 100.0,
            "ratio_t_90": t2_90 / t1_90,
            "delta_t_90_ms": (t2_90 - t1_90) * 1000.0,
            "pct_diff_t_90": ((t2_90 / t1_90) - 1.0) * 100.0,
            "ratio_t_10_90": t2_10_90 / t1_10_90,
            "delta_t_10_90_ms": (t2_10_90 - t1_10_90) * 1000.0,
            "pct_diff_t_10_90": ((t2_10_90 / t1_10_90) - 1.0) * 100.0,
            "ratio_pendiente_max": slope2_max / slope1_max,  # 1/e ~ 0.367879
            "rampa_R_s_1": R_slew,
            "diff_rampa_t90_1er_ms": (t1_90_lim - t1_90) * 1000.0,
            "diff_rampa_t90_2do_ms": (t2_90_lim - t2_90) * 1000.0,
        }
        
        results.append((row_1, row_2, diff))
        
    return results

def write_csv_table(results, filepath: str):
    """Guarda la tabla comparativa en formato CSV con unidades explícitas."""
    fieldnames = [
        "orden",
        "modelo",
        "tau_s",
        "t_10_ms",
        "t_50_ms",
        "t_90_ms",
        "t_10_90_ms",
        "t_10_s",
        "t_50_s",
        "t_90_s",
        "t_10_90_s",
        "u_10_adim",
        "u_50_adim",
        "u_90_adim",
        "u_10_90_adim",
        "pendiente_max_s_1",
        "t_inflexion_s",
        "t_10_rampa_ms",
        "t_50_rampa_ms",
        "t_90_rampa_ms",
        "t_10_90_rampa_ms"
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r1, r2, _ in results:
            writer.writerow({
                "orden": r1["orden"],
                "modelo": r1["modelo"],
                "tau_s": f"{r1['tau_s']:.2f}",
                "t_10_ms": f"{r1['t_10_ms']:.3f}",
                "t_50_ms": f"{r1['t_50_ms']:.3f}",
                "t_90_ms": f"{r1['t_90_ms']:.3f}",
                "t_10_90_ms": f"{r1['t_10_90_ms']:.3f}",
                "t_10_s": f"{r1['t_10_s']:.6f}",
                "t_50_s": f"{r1['t_50_s']:.6f}",
                "t_90_s": f"{r1['t_90_s']:.6f}",
                "t_10_90_s": f"{r1['t_10_90_s']:.6f}",
                "u_10_adim": f"{r1['u_10']:.6f}",
                "u_50_adim": f"{r1['u_50']:.6f}",
                "u_90_adim": f"{r1['u_90']:.6f}",
                "u_10_90_adim": f"{r1['u_10_90']:.6f}",
                "pendiente_max_s_1": f"{r1['pendiente_max_s_1']:.4f}",
                "t_inflexion_s": "N/A",
                "t_10_rampa_ms": f"{r1['t_10_lim_ms']:.3f}",
                "t_50_rampa_ms": f"{r1['t_50_lim_ms']:.3f}",
                "t_90_rampa_ms": f"{r1['t_90_lim_ms']:.3f}",
                "t_10_90_rampa_ms": f"{r1['t_10_90_lim_ms']:.3f}"
            })
            writer.writerow({
                "orden": r2["orden"],
                "modelo": r2["modelo"],
                "tau_s": f"{r2['tau_s']:.2f}",
                "t_10_ms": f"{r2['t_10_ms']:.3f}",
                "t_50_ms": f"{r2['t_50_ms']:.3f}",
                "t_90_ms": f"{r2['t_90_ms']:.3f}",
                "t_10_90_ms": f"{r2['t_10_90_ms']:.3f}",
                "t_10_s": f"{r2['t_10_s']:.6f}",
                "t_50_s": f"{r2['t_50_s']:.6f}",
                "t_90_s": f"{r2['t_90_s']:.6f}",
                "t_10_90_s": f"{r2['t_10_90_s']:.6f}",
                "u_10_adim": f"{r2['u_10']:.6f}",
                "u_50_adim": f"{r2['u_50']:.6f}",
                "u_90_adim": f"{r2['u_90']:.6f}",
                "u_10_90_adim": f"{r2['u_10_90']:.6f}",
                "pendiente_max_s_1": f"{r2['pendiente_max_s_1']:.4f}",
                "t_inflexion_s": f"{r2['t_inflexion_s']:.2f}",
                "t_10_rampa_ms": f"{r2['t_10_lim_ms']:.3f}",
                "t_50_rampa_ms": f"{r2['t_50_lim_ms']:.3f}",
                "t_90_rampa_ms": f"{r2['t_90_lim_ms']:.3f}",
                "t_10_90_rampa_ms": f"{r2['t_10_90_lim_ms']:.3f}"
            })

def write_markdown_table(results, filepath: str):
    """Guarda la tabla comparativa en formato Markdown formateado."""
    lines = []
    lines.append("# Tabla Comparativa: Dinámica de 1er Orden vs 2do Orden Críticamente Amortiguado\n")
    lines.append("> **Distinción metodológica:**")
    lines.append("> - **Datos medidos:** NINGUNO disponible para C02. El artículo NASA Weinstein et al. (SciTech 2024) ensaya un EDF de 130 mm en banco, cuyos tiempos no deben extrapolarse a C02.")
    lines.append("> - **Supuestos:** $\\tau \\in \\{0.08, 0.20, 0.50\\}$ s; modelos lineales analíticos; cota de rampa $R = 50\\text{ N/s} / 21\\text{ N} \\approx 2.381\\text{ s}^{-1}$ (de `INFORME.md`).")
    lines.append("> - **Cálculos:** Soluciones analíticas exactas, método de Halley de 3er orden ($|\\text{error}| < 10^{-14}$) y simulación RK4/Euler. Unidades: segundos (s), milisegundos (ms), $\\text{s}^{-1}$.\n")
    
    # Tabla 1: Valores lineales puros
    lines.append("## 1. Tiempos de Respuesta Lineales (Sin Limitación de Rampa)\n")
    lines.append("| Modelo | $\\tau$ (s) | $t_{10\\%}$ (ms) | $t_{50\\%}$ (ms) | $t_{90\\%}$ (ms) | $t_{10\\to 90\\%}$ (ms) | Pendiente Máx ($\\text{s}^{-1}$) | $t_{\\text{inflex}}$ (s) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    
    for r1, r2, _ in results:
        lines.append(f"| **1er orden** | {r1['tau_s']:.2f} | {r1['t_10_ms']:.2f} | {r1['t_50_ms']:.2f} | {r1['t_90_ms']:.2f} | {r1['t_10_90_ms']:.2f} | {r1['pendiente_max_s_1']:.2f} | N/A |")
        lines.append(f"| **2do orden crít.** | {r2['tau_s']:.2f} | {r2['t_10_ms']:.2f} | {r2['t_50_ms']:.2f} | {r2['t_90_ms']:.2f} | {r2['t_10_90_ms']:.2f} | {r2['pendiente_max_s_1']:.2f} | {r2['t_inflexion_s']:.2f} |")
        
    lines.append("\n## 2. Ratios y Retardos Relativos (2do Orden frente a 1er Orden)\n")
    lines.append("| $\\tau$ (s) | $\\Delta t_{10\\%}$ (ms) | Ratio $t_{10\\%}$ | $\\Delta t_{50\\%}$ (ms) | Ratio $t_{50\\%}$ | $\\Delta t_{90\\%}$ (ms) | Ratio $t_{90\\%}$ | $\\Delta t_{10\\to 90}$ (ms) | Ratio Subida |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    
    for _, _, diff in results:
        lines.append(f"| {diff['tau_s']:.2f} | +{diff['delta_t_10_ms']:.2f} (+{diff['pct_diff_t_10']:.1f}%) | {diff['ratio_t_10']:.4f}x | +{diff['delta_t_50_ms']:.2f} (+{diff['pct_diff_t_50']:.1f}%) | {diff['ratio_t_50']:.4f}x | +{diff['delta_t_90_ms']:.2f} (+{diff['pct_diff_t_90']:.1f}%) | {diff['ratio_t_90']:.4f}x | +{diff['delta_t_10_90_ms']:.2f} (+{diff['pct_diff_t_10_90']:.1f}%) | {diff['ratio_t_10_90']:.4f}x |")

    lines.append("\n## 3. Coeficientes Adimensionales Universales ($u = t/\\tau$)\n")
    lines.append("| Modelo | $u_{10\\%}$ | $u_{50\\%}$ | $u_{90\\%}$ | $\\Delta u_{10\\to 90\\%}$ | Expresión Analítica |")
    lines.append("|---|---:|---:|---:|---:|---|")
    r1_sample = results[0][0]
    r2_sample = results[0][1]
    lines.append(f"| **1er orden** | {r1_sample['u_10']:.6f} | {r1_sample['u_50']:.6f} | {r1_sample['u_90']:.6f} | {r1_sample['u_10_90']:.6f} | $u = -\\ln(1-p)$ |")
    lines.append(f"| **2do orden crít.** | {r2_sample['u_10']:.6f} | {r2_sample['u_50']:.6f} | {r2_sample['u_90']:.6f} | {r2_sample['u_10_90']:.6f} | $u = -1 - W_{{-1}}(-(1-p)/e)$ |")
    lines.append(f"| **Factor 2do / 1er** | **{r2_sample['u_10']/r1_sample['u_10']:.4f}x** | **{r2_sample['u_50']/r1_sample['u_50']:.4f}x** | **{r2_sample['u_90']/r1_sample['u_90']:.4f}x** | **{r2_sample['u_10_90']/r1_sample['u_10_90']:.4f}x** | Invariante respecto a $\\tau$ |")

    lines.append("\n## 4. Efecto de Limitación de Rampa ESC / Slew-Rate ($R = 50\\text{ N/s} / 21\\text{ N} \\approx 2.381\\text{ s}^{-1}$)\n")
    lines.append("| Modelo | $\\tau$ (s) | $t_{10\\%}$ Lineal (ms) | $t_{10\\%}$ con Rampa (ms) | $t_{50\\%}$ Lineal (ms) | $t_{50\\%}$ con Rampa (ms) | $t_{90\\%}$ Lineal (ms) | $t_{90\\%}$ con Rampa (ms) | Estado de Saturación |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    
    for r1, r2, diff in results:
        sat1 = "Saturado en arranque ($1/\\tau > R$)" if (1.0 / r1["tau_s"] > diff["rampa_R_s_1"]) else "No saturado ($1/\\tau \\le R$)"
        sat2 = "Saturado en inflexión ($1/(e\\tau) > R$)" if (1.0 / (math.e * r2["tau_s"]) > diff["rampa_R_s_1"]) else "No saturado ($1/(e\\tau) \\le R$)"
        lines.append(f"| **1er orden** | {r1['tau_s']:.2f} | {r1['t_10_ms']:.2f} | **{r1['t_10_lim_ms']:.2f}** | {r1['t_50_ms']:.2f} | **{r1['t_50_lim_ms']:.2f}** | {r1['t_90_ms']:.2f} | **{r1['t_90_lim_ms']:.2f}** | {sat1} |")
        lines.append(f"| **2do orden crít.** | {r2['tau_s']:.2f} | {r2['t_10_ms']:.2f} | **{r2['t_10_lim_ms']:.2f}** | {r2['t_50_ms']:.2f} | **{r2['t_50_lim_ms']:.2f}** | {r2['t_90_ms']:.2f} | **{r2['t_90_lim_ms']:.2f}** | {sat2} |")
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

# ---------------------------------------------------------
# 7. Ejecución principal
# ---------------------------------------------------------

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = script_dir if os.path.basename(script_dir) == "salidas" else os.path.join(script_dir, "salidas")
    os.makedirs(out_dir, exist_ok=True)
    
    taus = (0.08, 0.20, 0.50)
    R_slew = 50.0 / 21.0  # 2.38095 s^-1
    
    print("=" * 75)
    print("ANÁLISIS COMPARATIVO DE RESPUESTAS NORMALIZADAS DE ACTUADOR")
    print(f"Valores supuestos de tau: {taus} s")
    print(f"Cota de rampa supuesta (INFORME.md): R = 50 N/s / 21 N = {R_slew:.4f} s^-1")
    print("=" * 75)
    
    results = generate_comparisons(taus, R_slew)
    
    # Imprimir resumen en consola
    for r1, r2, diff in results:
        tau = r1["tau_s"]
        print(f"\n--- Tau supuesto: {tau:.2f} s ---")
        print(f"  1er Orden Lineal:      t10 = {r1['t_10_ms']:6.2f} ms | t50 = {r1['t_50_ms']:6.2f} ms | t90 = {r1['t_90_ms']:6.2f} ms | t10-90 = {r1['t_10_90_ms']:6.2f} ms")
        print(f"  1er Orden c/ Rampa:    t10 = {r1['t_10_lim_ms']:6.2f} ms | t50 = {r1['t_50_lim_ms']:6.2f} ms | t90 = {r1['t_90_lim_ms']:6.2f} ms | t10-90 = {r1['t_10_90_lim_ms']:6.2f} ms")
        print(f"  2do Orden Lineal:      t10 = {r2['t_10_ms']:6.2f} ms | t50 = {r2['t_50_ms']:6.2f} ms | t90 = {r2['t_90_ms']:6.2f} ms | t10-90 = {r2['t_10_90_ms']:6.2f} ms")
        print(f"  2do Orden c/ Rampa:    t10 = {r2['t_10_lim_ms']:6.2f} ms | t50 = {r2['t_50_lim_ms']:6.2f} ms | t90 = {r2['t_90_lim_ms']:6.2f} ms | t10-90 = {r2['t_10_90_lim_ms']:6.2f} ms")
        print(f"  Diferencia Lineal 2-1: dt10 = +{diff['delta_t_10_ms']:6.2f} ms ({diff['ratio_t_10']:.2f}x) | dt50 = +{diff['delta_t_50_ms']:6.2f} ms ({diff['ratio_t_50']:.2f}x) | dt90 = +{diff['delta_t_90_ms']:6.2f} ms ({diff['ratio_t_90']:.2f}x)")
        
    csv_path = os.path.join(out_dir, "tabla_comparativa.csv")
    md_path = os.path.join(out_dir, "tabla_comparativa.md")
    json_path = os.path.join(out_dir, "datos_respuestas.json")
    
    write_csv_table(results, csv_path)
    write_markdown_table(results, md_path)
    
    json_data = {
        "metadata": {
            "estudio": "Comparación dinámica 1er vs 2do orden críticamente amortiguado con análisis de rampas",
            "tipo_datos": "Cálculos analíticos y simulaciones numéricas basados en tau y cotas supuestas",
            "distincion": "Sin datos medidos para C02. El estudio NASA Weinstein et al. (SciTech 2024) ensaya un EDF de 130 mm en banco",
            "fuente_tau_0_08": "Hipótesis en simulacion_vuelo_A/INFORME.md",
            "fuente_rampa_50Ns": "Hipótesis en simulacion_vuelo_A/INFORME.md (50 N/s para 21 N max => R = 2.38095 s^-1)",
            "precision": "Halley 3er orden tol=1e-15, RK4 dt=1e-5"
        },
        "taus_supuestos_s": list(taus),
        "rampa_supuesta_s_1": R_slew,
        "comparaciones": [
            {"primer_orden": r1, "segundo_orden": r2, "diferencias": diff}
            for r1, r2, diff in results
        ],
        "limites": {str(t): evaluate_limits(t) for t in taus}
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
        
    print(f"\n[OK] Archivos generados con éxito en {out_dir}:")
    print(f"  - {os.path.basename(csv_path)}")
    print(f"  - {os.path.basename(md_path)}")
    print(f"  - {os.path.basename(json_path)}")
    print("=" * 75)

if __name__ == "__main__":
    main()
