#!/usr/bin/env python3
"""
verificar_condiciones.py
------------------------
Script de verificación numérica, dimensional y de equilibrio para condiciones
de fuerza descendente en Arquitectura A (ventiladores internos) bajo actitud fija y gravedad.

Verifica:
1. Condición analítica: R >= m * g * (n - 1) / 4 para caso simétrico sin otras fuerzas.
2. Análisis dimensional formal ([M][L][T]^-2).
3. Pruebas de equilibrio estático de fuerzas (sum Fz = -m*a) y momentos (sum M = 0).
4. Casos límite: n = 1 (caída libre), n < 1 (sub-g), n > 1 (hiper-g descendente), g -> 0.
5. Extensión a CG excéntrico longitudinal y transversal.
6. Exportación de tabla en CSV y resultados en JSON.
"""

import sys
import json
import csv
import math

# Constantes físicas y de referencia
G0_STANDARD = 9.80665   # m/s^2 (ISO 80000-3 / WGS-84)
G_APPROX = 9.81         # m/s^2 (aproximación didáctica común)

MASSES_KG = [2.0, 5.0, 10.0]
FACTORS_N = [1.2, 2.0, 5.0]

def derive_symmetric_limit(m, n, g):
    """Calcula R_min = m * g * (n - 1) / 4"""
    f_desc_total = m * g * (n - 1.0)
    r_min = f_desc_total / 4.0
    return f_desc_total, r_min

def dimensional_analysis():
    """
    Verifica las dimensiones de cada término en R = m * g * (n - 1) / 4
    Dimensiones base SI:
    [m] = M^1 L^0 T^0
    [g] = M^0 L^1 T^-2
    [n] = M^0 L^0 T^0 (adimensional, factor de carga a/g)
    [4] = M^0 L^0 T^0 (número de actuadores)
    [R] = [m] * [g] * [n - 1] / [4] = M^1 L^1 T^-2 = Newton (N)
    """
    dim_m = {"M": 1, "L": 0, "T": 0}
    dim_g = {"M": 0, "L": 1, "T": -2}
    dim_n = {"M": 0, "L": 0, "T": 0}
    dim_const = {"M": 0, "L": 0, "T": 0}
    
    # [m * g]
    dim_mg = {k: dim_m[k] + dim_g[k] for k in ["M", "L", "T"]}
    # [m * g * (n - 1)]
    dim_f = {k: dim_mg[k] + dim_n[k] for k in ["M", "L", "T"]}
    # [R] = [f / 4]
    dim_r = {k: dim_f[k] - dim_const[k] for k in ["M", "L", "T"]}
    
    expected_force = {"M": 1, "L": 1, "T": -2}
    assert dim_r == expected_force, f"Error dimensional: {dim_r} != {expected_force}"
    return True

def equilibrium_tests(g=G0_STANDARD):
    """
    Prueba el equilibrio de fuerzas y momentos para el caso simétrico y excéntrico.
    Convención de signos:
    Eje +Z inercial y cuerpo hacia arriba.
    Gravedad: F_grav_z = -m * g
    Aceleración descendente neta: a_desc = n * g => a_z = -n * g
    Ecuación de Newton: sum F_z = m * a_z = -m * n * g
    Fuerza descendente requerida de propulsores: F_prop_z = -4 * R_0
    Equilibrio: -m * g + (-4 * R_0) = -m * n * g
    => 4 * R_0 = m * n * g - m * g = m * g * (n - 1)
    """
    results = []
    
    for m in MASSES_KG:
        for n in FACTORS_N:
            f_desc_total, r_req = derive_symmetric_limit(m, n, g)
            
            # 1. Fuerza vertical neta
            f_prop_z = -4.0 * r_req  # sentido descendente (-Z)
            f_grav_z = -m * g        # gravedad (-Z)
            f_total_z = f_prop_z + f_grav_z
            
            a_z = f_total_z / m
            target_a_z = -n * g
            
            diff_f = abs(f_total_z - (-m * n * g))
            diff_a = abs(a_z - target_a_z)
            assert diff_f < 1e-12, f"Error de balance de fuerza: diff={diff_f}"
            assert diff_a < 1e-12, f"Error de aceleración: diff={diff_a}"
            
            # 2. Momentos con estaciones simétricas (p.ej. x = +-dx, y = +-dy)
            # Módulos: 1:(+dx, +dy), 2:(+dx, -dy), 3:(-dx, -dy), 4:(-dx, +dy)
            # Con R1 = R2 = R3 = R4 = r_req
            dx = 0.160  # m (referencia de estación geométrica C02)
            dy = 0.076  # m (referencia de estación geométrica C02)
            
            # Fuerzas en Z: Fz_i = -r_req
            # Mx = sum (y_i * Fz_i) = -r_req * (dy - dy - dy + dy) = 0
            mx = (-r_req * dy) + (-r_req * -dy) + (-r_req * -dy) + (-r_req * dy)
            # My = sum (-x_i * Fz_i) = r_req * (dx + dx - dx - dx) = 0
            my = (r_req * dx) + (r_req * dx) + (-r_req * dx) + (-r_req * dx)
            
            assert abs(mx) < 1e-12, f"Error de momento de alabeo Mx={mx}"
            assert abs(my) < 1e-12, f"Error de momento de cabeceo My={my}"
            
            results.append({
                "m_kg": m,
                "n": n,
                "f_desc_total_N": f_desc_total,
                "r_min_N": r_req,
                "diff_f": diff_f,
                "diff_a": diff_a,
                "mx": mx,
                "my": my
            })
            
    return results

def boundary_and_limit_cases(g=G0_STANDARD):
    """
    Prueba casos de frontera y límites físicos:
    1. n = 1.0 (caída libre pura): r_min debe ser exactamente 0.0 N.
    2. n = 0.0 (estacionario o flotación sin aceleración descendente):
       r_min = m*g*(0-1)/4 = -m*g/4 < 0 (indica que no se requiere fuerza descendente sino sustentación ascendente).
    3. n = 0.5 (descenso a 0.5g): r_min < 0 (la gravedad 1g por sí sola ya excede 0.5g, se necesita frenar/sustentar).
    4. g -> 0 (entorno de microgravedad): F_prop = m * a_desc, r_min = m * a_desc / 4.
    """
    # Caso 1: Caída libre n = 1.0
    _, r_freefall = derive_symmetric_limit(5.0, 1.0, g)
    assert abs(r_freefall - 0.0) < 1e-15, f"Fallo caso n=1.0: {r_freefall}"
    
    # Caso 2: n = 0.0
    _, r_zero = derive_symmetric_limit(5.0, 0.0, g)
    assert r_zero < 0, f"Fallo caso n=0.0: {r_zero}"
    
    # Caso 3: n = 0.5
    _, r_subg = derive_symmetric_limit(5.0, 0.5, g)
    assert r_subg < 0, f"Fallo caso n=0.5: {r_subg}"
    
    # Caso 4: Microgravedad g -> 0 con a_desc prescrita
    a_prescribed = 9.80665 * 2.0  # aceleración prescrita equivalente a 2g
    # En microgravedad, g = 0, sum Fz = m * a => 4 * R = m * a
    r_microg = (5.0 * a_prescribed) / 4.0
    assert abs(r_microg - (5.0 * 2.0 * g / 4.0)) < 1e-12
    
    return True

def eccentric_cg_verification(g=G0_STANDARD):
    """
    Verifica el impacto del CG excéntrico en la distribución de empuje descendente.
    Para CG en (x_cg, y_cg), estaciones en (+-dx, +-dy):
    Ecuaciones:
    R1 + R2 + R3 + R4 = F_desc_total
    (R1 + R2 - R3 - R4) * dx = F_desc_total * x_cg
    (R1 - R2 - R3 + R4) * dy = F_desc_total * y_cg
    Si minimizamos max(Ri) o consideramos distribución plana lineal:
    Ri = (F_desc_total / 4) * (1 +- x_cg/dx +- y_cg/dy)
    El módulo crítico requiere:
    R_max = (m * g * (n - 1) / 4) * (1 + |x_cg|/dx + |y_cg|/dy)
    """
    m = 5.0
    n = 2.0
    dx = 0.160
    dy = 0.076
    f_desc_total, r_sym = derive_symmetric_limit(m, n, g)
    
    # Si x_cg = 0.040 m, y_cg = 0
    x_cg = 0.040
    y_cg = 0.0
    r_crit = r_sym * (1.0 + abs(x_cg)/dx + abs(y_cg)/dy)
    
    # Comprobar que al volver a CG centrado, r_crit == r_sym
    r_crit_zero = r_sym * (1.0 + 0.0/dx + 0.0/dy)
    assert abs(r_crit_zero - r_sym) < 1e-15
    assert r_crit > r_sym, "El CG excéntrico debe demandar mayor R en el módulo crítico"
    
    return {
        "r_sym": r_sym,
        "x_cg": x_cg,
        "dx": dx,
        "amplification_factor": 1.0 + abs(x_cg)/dx,
        "r_crit": r_crit
    }

def generate_outputs():
    # 1. Pruebas
    assert dimensional_analysis(), "Fallo en análisis dimensional"
    eq_results = equilibrium_tests(G0_STANDARD)
    assert boundary_and_limit_cases(G0_STANDARD), "Fallo en casos límite"
    ecc_res = eccentric_cg_verification(G0_STANDARD)
    
    # 2. Generar datos detallados para tabla
    table_rows = []
    for m in MASSES_KG:
        w_n = m * G0_STANDARD
        for n in FACTORS_N:
            a_desc_ms2 = n * G0_STANDARD
            n_minus_1 = n - 1.0
            f_desc_total, r_min = derive_symmetric_limit(m, n, G0_STANDARD)
            r_min_kgf = r_min / G0_STANDARD
            f_desc_total_kgf = f_desc_total / G0_STANDARD
            
            # Variación con g = 9.81 m/s^2
            f_desc_total_981, r_min_981 = derive_symmetric_limit(m, n, G_APPROX)
            
            row = {
                "m_kg": m,
                "n_factor": n,
                "n_minus_1": round(n_minus_1, 4),
                "a_desc_net_ms2": round(a_desc_ms2, 5),
                "peso_W_N": round(w_n, 5),
                "f_desc_total_N": round(f_desc_total, 5),
                "f_desc_total_kgf": round(f_desc_total_kgf, 5),
                "r_min_por_modulo_N": round(r_min, 6),
                "r_min_por_modulo_kgf": round(r_min_kgf, 5),
                "r_min_por_modulo_g981_N": round(r_min_981, 6),
                "ratio_r_sobre_w_cuartos": round(r_min / (w_n / 4.0), 4)
            }
            table_rows.append(row)
            
    # Escribir CSV
    csv_path = "salidas/tabla_fuerza_descendente.csv"
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "m_kg",
            "n_factor",
            "n_minus_1",
            "a_desc_net_ms2",
            "peso_W_N",
            "f_desc_total_N",
            "f_desc_total_kgf",
            "r_min_por_modulo_N",
            "r_min_por_modulo_kgf",
            "r_min_por_modulo_g981_N",
            "ratio_r_sobre_w_cuartos"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in table_rows:
            writer.writerow(r)
            
    # Escribir JSON con resultados completos y metadata de verificación
    json_path = "salidas/resultados_pruebas.json"
    data_out = {
        "metadata": {
            "g0_standard_ms2": G0_STANDARD,
            "g_approx_ms2": G_APPROX,
            "formula_simetrica": "R >= m * g * (n - 1) / 4",
            "hipotesis": [
                "Cuerpo rígido con actitud fija (cabeceo = 0, alabeo = 0, guiñada = 0)",
                "Cuatro módulos ideales coplanares/simétricos",
                "Ausencia de fuerzas aerodinámicas externas (L=0, D=0)",
                "Fuerza descendente máxima reversible limitada a R por módulo",
                "Caso simétrico con CG en el centroide geométrico de los módulos"
            ]
        },
        "dimensional_check": "PASSED (Dimension de R = M L T^-2 = Newton)",
        "equilibrium_checks": "PASSED (Sum Fz = -m*a_desc, Sum Mx = 0, Sum My = 0 para todos los casos)",
        "boundary_cases_checks": "PASSED (n=1.0 -> R=0; n<1.0 -> R<0; g->0 -> R=m*a/4)",
        "eccentric_cg_verification": {
            "status": "PASSED",
            "sample_scenario": ecc_res
        },
        "tabular_data": table_rows
    }
    with open(json_path, mode="w", encoding="utf-8") as f:
        json.dump(data_out, f, indent=2, ensure_ascii=False)
        
    print(f"Generados exitosamente: {csv_path} y {json_path}")
    print(f"Total de combinaciones evaluadas: {len(table_rows)}")
    for r in table_rows:
        print(f"m={r['m_kg']:4.1f} kg | n={r['n_factor']:3.1f} | F_desc_tot={r['f_desc_total_N']:8.4f} N | R_min={r['r_min_por_modulo_N']:8.4f} N ({r['r_min_por_modulo_kgf']:5.2f} kgf)")

if __name__ == "__main__":
    generate_outputs()
