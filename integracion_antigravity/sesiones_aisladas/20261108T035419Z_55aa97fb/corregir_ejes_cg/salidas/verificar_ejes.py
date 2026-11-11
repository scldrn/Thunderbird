#!/usr/bin/env python3
"""
verificar_ejes.py
Verificación analítica y matricial de los sistemas de coordenadas CAD y FLU,
la matriz R_flight_from_CAD y el análisis de equilibrio 2D para la plataforma C02.

Pruebas ejecutadas:
1. Determinante y ortonormalidad de R_flight_from_CAD.
2. Quiralidad y regla de la mano derecha en FLU y CAD.
3. Transformación vectorial de ejes directores (+x, +y, +z).
4. Mapeo cinemático de los 4 módulos de propulsión CAD vs FLU.
5. Invarianza analítica de las ecuaciones de momento y sustentación.
6. Invarianza de la holgura de factibilidad Delta f4 y capacidad máxima Fz_max.
7. Comprobación de la permutación lateral exacta de fuerzas (f1 <-> f2, f3 <-> f4).
"""

import json
import math
import sys

def test_algebra_matricial(cfg_path):
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    R = cfg['flight_body_frame']['R_flight_from_CAD']
    
    # 1. Determinante de R (matriz 3x3)
    det = (
        R[0][0] * (R[1][1] * R[2][2] - R[1][2] * R[2][1])
        - R[0][1] * (R[1][0] * R[2][2] - R[1][2] * R[2][0])
        + R[0][2] * (R[1][0] * R[2][1] - R[1][1] * R[2][0])
    )
    assert abs(det - 1.0) < 1e-12, f"det(R) debe ser exactamente +1.0, obtenido: {det}"
    
    # 2. Ortonormalidad: R * R^T = I
    for i in range(3):
        for j in range(3):
            dot = sum(R[i][k] * R[j][k] for k in range(3))
            expected = 1.0 if i == j else 0.0
            assert abs(dot - expected) < 1e-12, f"Fallo de ortonormalidad en ({i}, {j})"
            
    # R es simétrica (R = R^T = R^-1)
    for i in range(3):
        for j in range(3):
            assert R[i][j] == R[j][i], f"R no es simétrica en ({i}, {j})"
            
    return R, cfg

def cross_product(u, v):
    return [
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    ]

def dot_product(u, v):
    return sum(a*b for a, b in zip(u, v))

def test_quiralidad_y_vectores(R):
    # FLU canónico:
    # x_FLU: Adelante (Forward / Nariz) = [1, 0, 0]
    # y_FLU: Izquierda (Left / Babor)    = [0, 1, 0]
    # z_FLU: Arriba (Up)                = [0, 0, 1]
    x_flu = [1, 0, 0]
    y_flu = [0, 1, 0]
    z_flu = [0, 0, 1]
    
    # Regla de la mano derecha en FLU: x_FLU x y_FLU = z_FLU
    cross_flu = cross_product(x_flu, y_flu)
    assert cross_flu == z_flu, f"FLU no es dextrógiro: {cross_flu} != {z_flu}"
    
    # Transformación a CAD: v_CAD = R @ v_FLU (dado que R = R^-1)
    x_fwd_in_cad = [sum(R[i][j]*x_flu[j] for j in range(3)) for i in range(3)]
    y_left_in_cad = [sum(R[i][j]*y_flu[j] for j in range(3)) for i in range(3)]
    z_up_in_cad = [sum(R[i][j]*z_flu[j] for j in range(3)) for i in range(3)]
    
    # Adelante es -x en CAD; por ende +x en CAD apunta a la COLA
    assert x_fwd_in_cad == [-1, 0, 0], f"Adelante en CAD debería ser [-1, 0, 0], obtenido: {x_fwd_in_cad}"
    # Izquierda es -y en CAD; por ende +y en CAD corresponde a la DERECHA
    assert y_left_in_cad == [0, -1, 0], f"Izquierda en CAD debería ser [0, -1, 0], obtenido: {y_left_in_cad}"
    # Arriba es +z en CAD
    assert z_up_in_cad == [0, 0, 1], f"Arriba en CAD debería ser [0, 0, 1], obtenido: {z_up_in_cad}"
    
    # Verificación en dirección opuesta (ejes unitarios CAD expresados en FLU):
    # CAD +x: [1, 0, 0]
    cad_x = [1, 0, 0]
    cad_x_in_flu = [sum(R[i][j]*cad_x[j] for j in range(3)) for i in range(3)]
    assert cad_x_in_flu == [-1, 0, 0], f"CAD +x en FLU debe ser -x (cola/atrás)"
    
    # CAD +y: [0, 1, 0]
    cad_y = [0, 1, 0]
    cad_y_in_flu = [sum(R[i][j]*cad_y[j] for j in range(3)) for i in range(3)]
    assert cad_y_in_flu == [0, -1, 0], f"CAD +y en FLU debe ser -y (derecha/estribor)"
    
    # CAD +z: [0, 0, 1]
    cad_z = [0, 0, 1]
    cad_z_in_flu = [sum(R[i][j]*cad_z[j] for j in range(3)) for i in range(3)]
    assert cad_z_in_flu == [0, 0, 1], f"CAD +z en FLU debe ser +z (arriba)"
    
    # Quiralidad del sistema CAD:
    cross_cad = cross_product(cad_x, cad_y)
    assert cross_cad == cad_z, f"CAD no es dextrógiro: {cross_cad} != {cad_z}"
    
    # Si CAD +y fuese izquierda [0, -1, 0], el producto vectorial daría [0, 0, -1] (abajo), violando la regla
    cad_y_erroneo = [0, -1, 0]
    cross_erroneo = cross_product(cad_x, cad_y_erroneo)
    assert cross_erroneo == [0, 0, -1], "El producto vectorial del sistema erróneo debe dar -z (levógiro)"

def test_mapeo_modulos(R, cfg):
    centres_cad = cfg['fan_reference']['centres_xy_m']
    
    modulos_analisis = []
    for idx, (x_c, y_c) in enumerate(centres_cad, 1):
        # Mapeo a FLU:
        x_f = R[0][0]*x_c + R[0][1]*y_c
        y_f = R[1][0]*x_c + R[1][1]*y_c
        
        long_cad = "Nariz (-x)" if x_c < 0 else "Cola (+x)"
        lat_cad_real = "Derecha (+y)" if y_c > 0 else "Izquierda (-y)"
        
        long_flu = "Adelante/Nariz (+x)" if x_f > 0 else "Atrás/Cola (-x)"
        lat_flu = "Izquierda (+y)" if y_f > 0 else "Derecha (-y)"
        
        modulos_analisis.append({
            'modulo': idx,
            'cad': (x_c, y_c),
            'flu': (x_f, y_f),
            'long_cad': long_cad,
            'lat_cad_real': lat_cad_real,
            'pos_flu': f"{long_flu} / {lat_flu}"
        })
        
    # Módulo 1: CAD (-0.160, -0.076) -> FLU (+0.160, +0.076) = Nariz / Izquierda
    assert modulos_analisis[0]['flu'] == (0.16, 0.076)
    # Módulo 2: CAD (-0.160, +0.076) -> FLU (+0.160, -0.076) = Nariz / Derecha
    assert modulos_analisis[1]['flu'] == (0.16, -0.076)
    # Módulo 3: CAD (+0.160, -0.076) -> FLU (-0.160, +0.076) = Cola / Izquierda
    assert modulos_analisis[2]['flu'] == (-0.16, 0.076)
    # Módulo 4: CAD (+0.160, +0.076) -> FLU (-0.160, -0.076) = Cola / Derecha
    assert modulos_analisis[3]['flu'] == (-0.16, -0.076)
    
    return modulos_analisis

def solve_cg(xcg, ycg, W=49.03325, Lx=0.160, Ly=0.076, Fmax=20.58):
    S_rear = 0.5 * W * (1.0 + xcg / Lx)
    S_front = 0.5 * W * (1.0 - xcg / Lx)
    S_left = 0.5 * W * (1.0 + ycg / Ly)
    S_right = 0.5 * W * (1.0 - ycg / Ly)
    
    L1 = S_left - S_front
    L2 = S_left - Fmax
    L3 = S_rear - Fmax
    L4 = 0.0
    
    U1 = L1 + Fmax
    U2 = S_left
    U3 = S_rear
    U4 = Fmax
    
    f4_min = max(L1, L2, L3, L4)
    f4_max = min(U1, U2, U3, U4)
    delta_f4 = f4_max - f4_min
    feasible = delta_f4 >= -1e-12
    
    f4 = 0.5 * (f4_min + f4_max)
    f3 = S_rear - f4
    f2 = S_left - f4
    f1 = S_front - S_left + f4
    
    u = abs(xcg) / Lx
    v = abs(ycg) / Ly
    cap_vals = [4*Fmax, 4*Fmax/(1+u) if (1+u)>0 else 0, 4*Fmax/(1+v) if (1+v)>0 else 0]
    if (u + v) > 0:
        cap_vals.append(2*Fmax / (u + v))
    Fz_max = min(cap_vals)
    
    return {
        'feasible': feasible,
        'delta_f4': delta_f4,
        'f': (f1, f2, f3, f4),
        'Fz_max': Fz_max
    }

def test_simetria_magnitudes():
    # Evaluación de múltiples pares simétricos
    puntos = [
        (0.000, 0.000),
        (0.040, 0.000),
        (0.080, 0.000),
        (0.040, 0.020),
        (-0.050, 0.030),
        (0.096, 0.015),
        (0.120, -0.010),
    ]
    
    for xcg, ycg in puntos:
        res_pos = solve_cg(xcg, ycg)
        res_neg = solve_cg(xcg, -ycg)
        
        # 1. Factibilidad idéntica
        assert res_pos['feasible'] == res_neg['feasible']
        # 2. Holgura analítica idéntica
        assert abs(res_pos['delta_f4'] - res_neg['delta_f4']) < 1e-12
        # 3. Capacidad vertical máxima idéntica
        assert abs(res_pos['Fz_max'] - res_neg['Fz_max']) < 1e-12
        
        # 4. En simetría lateral pura (ycg = 0), f1 == f2 y f3 == f4
        if abs(ycg) < 1e-12:
            assert abs(res_pos['f'][0] - res_pos['f'][1]) < 1e-12
            assert abs(res_pos['f'][2] - res_pos['f'][3]) < 1e-12
            
        # 5. En asimetría lateral, las fuerzas permutadas son idénticas:
        # f1(+y) == f2(-y), f2(+y) == f1(-y), f3(+y) == f4(-y), f4(+y) == f3(-y)
        f_pos = res_pos['f']
        f_neg = res_neg['f']
        assert abs(f_pos[0] - f_neg[1]) < 1e-12
        assert abs(f_pos[1] - f_neg[0]) < 1e-12
        assert abs(f_pos[2] - f_neg[3]) < 1e-12
        assert abs(f_pos[3] - f_neg[2]) < 1e-12

def main():
    cfg_file = 'entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json'
    print("Iniciando verificación analítica y matricial...")
    
    R, cfg = test_algebra_matricial(cfg_file)
    print("[PASS] 1. Determinante (+1.0), ortonormalidad y simetría de R_flight_from_CAD.")
    
    test_quiralidad_y_vectores(R)
    print("[PASS] 2. Regla de la mano derecha (dextrógiro) y correspondencia de ejes directores.")
    
    modulos = test_mapeo_modulos(R, cfg)
    print("[PASS] 3. Mapeo cinemático de los 4 módulos propulsores CAD -> FLU.")
    
    test_simetria_magnitudes()
    print("[PASS] 4. Invarianza de magnitudes, capacidades e intercambio de fuerzas en modelo simétrico.")
    
    print("\nResumen cinemático de módulos:")
    for m in modulos:
        print(f"  Módulo {m['modulo']}: CAD {m['cad']} ({m['long_cad']} / {m['lat_cad_real']}) -> FLU {m['flu']} ({m['pos_flu']})")
        
    print("\nTodas las pruebas analíticas concluyeron satisfactoriamente.")

if __name__ == '__main__':
    main()
