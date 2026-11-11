#!/usr/bin/env python3
"""
modelo_disco.py - Modelo de referencia de disco actuador aislado en flujo axial incompresible no ductado.

Implementa:
- Velocidad inducida: vi = (sqrt(V^2 + 2*T/(rho*A)) - V) / 2
- Potencia ideal instantánea en disco: P_ideal = T * (V + vi)
- Potencia finita en V = 0: P_static = T^(3/2) / sqrt(2*rho*A)
- Perfil de aceleración constante: v(tau) = V_final * (tau / t_accel)
- Ley de arrastre cuadrático: D(v) = D_final * (v / V_final)^2
- Empuje requerido: T(tau) = m * (V_final / t_accel) + D(v(tau))
- Solución analítica exacta de la integral de trabajo ideal W_ideal
- Métodos de integración numérica (Regla Trapezoidal, Regla de Simpson 1/3)
- Comparación con el modelo previo de eficiencia constante: W_prev = (0.5*m*V^2 + 0.25*D*V*t) / eta
"""

import math
from typing import Dict, Tuple, List, Any


def induced_velocity(V: float, T: float, rho: float, A: float) -> float:
    """
    Calcula la velocidad inducida vi según la teoría de cantidad de movimiento
    para un disco actuador aislado en flujo axial incompresible no ductado.
    
    vi = (sqrt(V^2 + 2*T / (rho*A)) - V) / 2
    """
    if T <= 0.0:
        return 0.0
    disk_loading_term = 2.0 * T / (rho * A)
    return (math.sqrt(V * V + disk_loading_term) - V) / 2.0


def ideal_power(V: float, T: float, rho: float, A: float) -> float:
    """
    Potencia ideal entregada al fluido en el disco actuador:
    P_ideal = T * (V + vi) = T * (V + sqrt(V^2 + 2*T/(rho*A))) / 2
    """
    if T <= 0.0:
        return 0.0
    vi = induced_velocity(V, T, rho, A)
    return T * (V + vi)


def static_power(T: float, rho: float, A: float) -> float:
    """
    Potencia ideal en reposo (V = 0):
    P_static = T * vi(0) = T^(3/2) / sqrt(2 * rho * A)
    """
    if T <= 0.0:
        return 0.0
    return math.pow(T, 1.5) / math.sqrt(2.0 * rho * A)


def froude_efficiency(V: float, T: float, rho: float, A: float) -> float:
    """
    Eficiencia propulsiva ideal de Froude:
    eta_i = (T * V) / P_ideal = V / (V + vi)
    En V = 0, eta_i = 0.
    """
    if T <= 0.0:
        return 1.0
    if V <= 0.0:
        return 0.0
    vi = induced_velocity(V, T, rho, A)
    return V / (V + vi)


def mach_number(V: float, a_sound: float = 340.294) -> float:
    """
    Número de Mach de vuelo: M = V / a_sound.
    """
    return V / a_sound


def exact_work_accel(m: float, V_final: float, t_accel: float, D_final: float, rho: float, A: float) -> float:
    """
    Solución analítica exacta de la integral de trabajo ideal en el disco durante
    aceleración constante v(tau) = a*tau con arrastre cuadrático D(tau) = beta*tau^2:
    
    W_ideal = int_0^t T(tau) * [v(tau) + vi(tau)] dtau
            = I1 + I2
    
    donde:
      I1 = 0.5 * int_0^t T(tau)*v(tau) dtau = 0.25 * m * V_final^2 + 0.125 * D_final * V_final * t_accel
      I2 = 0.5 * int_0^t T(tau) * sqrt(v(tau)^2 + 2*T(tau)/(rho*A)) dtau
    
    Usando la sustitución u = sqrt(K) * tau:
      K = (V_final^2 + 2*D_final / (rho*A)) / t_accel^2
      C = 2 * m * V_final / (rho * A * t_accel)
      u1 = sqrt(K) * t_accel = sqrt(V_final^2 + 2*D_final / (rho*A))
      beta = D_final / t_accel^2
      T0 = m * V_final / t_accel
      
      I2 = [ T0 / (2*sqrt(K)) ] * J0(u1) + [ beta / (2*K^(3/2)) ] * J2(u1)
      
      J0(u) = int_0^u sqrt(s^2 + C) ds
            = 0.5 * u * sqrt(u^2 + C) + 0.5 * C * asinh(u / sqrt(C))
            
      J2(u) = int_0^u s^2 * sqrt(s^2 + C) ds
            = (u / 8) * (2*u^2 + C) * sqrt(u^2 + C) - (C^2 / 8) * asinh(u / sqrt(C))
    """
    if t_accel <= 0.0 or V_final <= 0.0:
        return 0.0

    a = V_final / t_accel
    T0 = m * a
    beta = D_final / (t_accel * t_accel)
    
    if T0 <= 0.0 and beta <= 0.0:
        return 0.0

    # Término útil (la mitad del trabajo propulsivo útil)
    I1 = 0.25 * m * (V_final * V_final) + 0.125 * D_final * V_final * t_accel
    
    # Parámetros del radical
    K = (V_final * V_final + 2.0 * D_final / (rho * A)) / (t_accel * t_accel)
    C = 2.0 * T0 / (rho * A)
    sqrt_K = math.sqrt(K)
    u1 = math.sqrt(V_final * V_final + 2.0 * D_final / (rho * A))
    
    if C <= 0.0:
        # Límite cuando T0 = 0 (masa nula, sólo arrastre)
        J0 = 0.5 * u1 * u1
        J2 = 0.25 * (u1 ** 4)
        I2 = (beta / (2.0 * math.pow(K, 1.5))) * J2
    else:
        sqrt_C = math.sqrt(C)
        sqrt_u1_C = math.sqrt(u1 * u1 + C)
        asinh_term = math.asinh(u1 / sqrt_C)
        
        # Primitiva J0(u1) = int_0^u1 sqrt(s^2 + C) ds
        J0 = 0.5 * u1 * sqrt_u1_C + 0.5 * C * asinh_term
        
        # Primitiva J2(u1) = int_0^u1 s^2 sqrt(s^2 + C) ds
        J2 = (u1 / 8.0) * (2.0 * u1 * u1 + C) * sqrt_u1_C - (C * C / 8.0) * asinh_term
        
        I2 = (T0 / (2.0 * sqrt_K)) * J0 + (beta / (2.0 * math.pow(K, 1.5))) * J2
    
    return I1 + I2


def integrate_work_trapezoid(m: float, V_final: float, t_accel: float, D_final: float,
                             rho: float, A: float, N: int) -> float:
    """
    Integración numérica del trabajo ideal mediante la regla trapezoidal compuesta.
    Error teórico O(h^2).
    """
    if N < 1:
        raise ValueError("N debe ser >= 1")
    dt = t_accel / N
    a = V_final / t_accel
    T0 = m * a
    
    s = 0.0
    for i in range(N + 1):
        tau = i * dt
        v = a * tau
        drag = D_final * (tau / t_accel) ** 2
        T = T0 + drag
        p = ideal_power(v, T, rho, A)
        weight = 0.5 if (i == 0 or i == N) else 1.0
        s += weight * p
    return s * dt


def integrate_work_simpson(m: float, V_final: float, t_accel: float, D_final: float,
                           rho: float, A: float, N: int) -> float:
    """
    Integración numérica del trabajo ideal mediante la regla de Simpson 1/3 compuesta.
    Requiere N par. Error teórico O(h^4).
    """
    if N % 2 != 0:
        raise ValueError("N debe ser par para la regla de Simpson 1/3")
    dt = t_accel / N
    a = V_final / t_accel
    T0 = m * a
    
    s = 0.0
    for i in range(N + 1):
        tau = i * dt
        v = a * tau
        drag = D_final * (tau / t_accel) ** 2
        T = T0 + drag
        p = ideal_power(v, T, rho, A)
        if i == 0 or i == N:
            weight = 1.0
        elif i % 2 == 1:
            weight = 4.0
        else:
            weight = 2.0
        s += weight * p
    return s * (dt / 3.0)


def previous_model_work(m: float, V_final: float, t_accel: float, D_final: float, eta: float) -> Tuple[float, float]:
    """
    Calcula el trabajo mecánico útil y el trabajo axial del modelo previo
    según la formulación de INFORME.md:
      W_util = 0.5 * m * V_final^2 + 0.25 * D_final * V_final * t_accel
      W_prev = W_util / eta
    Retorna (W_util, W_prev).
    """
    W_util = 0.5 * m * (V_final * V_final) + 0.25 * D_final * V_final * t_accel
    W_prev = W_util / eta
    return W_util, W_prev


def evaluate_scenario(m: float, V_final: float, t_accel: float, D_final: float,
                      rho: float, A: float, eta_prev: float = 0.70,
                      eta_disk_profile: float = 0.70) -> Dict[str, Any]:
    """
    Evalúa integralmente un escenario hipotético comparando el modelo de disco
    con el modelo previo.
    """
    a = V_final / t_accel
    T_initial = m * a
    T_final = T_initial + D_final
    
    # Potencias instantáneas
    P_stat = static_power(T_initial, rho, A)
    vi_stat = induced_velocity(0.0, T_initial, rho, A)
    
    vi_final = induced_velocity(V_final, T_final, rho, A)
    P_final_ideal = ideal_power(V_final, T_final, rho, A)
    P_final_prev = (T_final * V_final) / eta_prev
    
    # Trabajos en aceleración
    W_useful, W_prev = previous_model_work(m, V_final, t_accel, D_final, eta_prev)
    W_ideal_exact = exact_work_accel(m, V_final, t_accel, D_final, rho, A)
    W_induced = W_ideal_exact - W_useful
    
    # Trabajo si el disco incluye una eficiencia interna de perfil/pala
    W_disk_actual = W_ideal_exact / eta_disk_profile
    
    # Mach
    M_final = mach_number(V_final)
    
    return {
        "m_kg": m,
        "V_final_mps": V_final,
        "V_final_kmh": V_final * 3.6,
        "t_accel_s": t_accel,
        "a_mps2": a,
        "D_final_N": D_final,
        "rho_kgm3": rho,
        "A_m2": A,
        "diameter_m": math.sqrt(4.0 * A / math.pi),
        "T_initial_N": T_initial,
        "T_final_N": T_final,
        "P_static_ideal_W": P_stat,
        "P_static_prev_W": 0.0,
        "vi_static_mps": vi_stat,
        "vi_final_mps": vi_final,
        "P_final_ideal_W": P_final_ideal,
        "P_final_prev_W": P_final_prev,
        "W_useful_J": W_useful,
        "W_prev_J": W_prev,
        "W_ideal_exact_J": W_ideal_exact,
        "W_induced_J": W_induced,
        "W_disk_actual_J": W_disk_actual,
        "ratio_ideal_to_prev": W_ideal_exact / W_prev if W_prev > 0 else 0.0,
        "ratio_disk_actual_to_prev": W_disk_actual / W_prev if W_prev > 0 else 0.0,
        "froude_efficiency_final": froude_efficiency(V_final, T_final, rho, A),
        "Mach_final": M_final,
    }
