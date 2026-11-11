#!/usr/bin/env python3
"""
test_integrador_analitico_puro.py
=================================
Módulo de verificación analítica independiente en Python estándar (sin dependencias externas).

Propósito:
Verificar los fundamentos matemáticos de los tres casos requeridos:
1. Conservación de energía cinética rotacional y momento angular inercial en giro
   libre asimétrico con pasos temporales decrecientes.
2. Cinemática de cuaternión en giro constante comparado con solución analítica cerrada
   y comprobación de la propiedad espinorial de 360 grados (q -> -q).
3. Par de fuerzas opuestas (couples) y momento resultante r x F, verificando
   fuerza neta nula y aceleraciones traslacionales y angulares desacopladas.

AVISO DE RIGOR METODOLÓGICO:
Este script utiliza exclusivamente la biblioteca estándar de Python (math, json, sys)
para verificar las ecuaciones dinámicas. NO afirma éxito sobre 'salidas/simular.py',
el cual requiere numpy/scipy y permanece declarado formalmente como NO EJECUTADO
en el entorno actual por ausencia de dichas dependencias.
"""

import sys
import math
import json
from pathlib import Path

SALIDAS_DIR = Path(__file__).resolve().parent
G_CONST = 9.80665

# -----------------------------------------------------------------------------
# Funciones matemáticas auxiliares en Python estándar
# -----------------------------------------------------------------------------
def vec_add(a, b):
    return [x + y for x, y in zip(a, b)]

def vec_sub(a, b):
    return [x - y for x, y in zip(a, b)]

def vec_scale(v, s):
    return [x * s for x in v]

def vec_dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def vec_norm(v):
    return math.sqrt(sum(x * x for x in v))

def vec_cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ]

def quat_normalize(q):
    n = vec_norm(q)
    if n == 0.0:
        return [0.0, 0.0, 0.0, 1.0]
    return [x / n for x in q]

def quat_to_rot_matrix(q):
    """Matriz de rotación R(q) para transformar vector de cuerpo a inercial (convención SciPy)."""
    x, y, z, w = q
    return [
        [1.0 - 2.0*(y*y + z*z), 2.0*(x*y - w*z),       2.0*(x*z + w*y)],
        [2.0*(x*y + w*z),       1.0 - 2.0*(x*x + z*z), 2.0*(y*z - w*x)],
        [2.0*(x*z - w*y),       2.0*(y*z + w*x),       1.0 - 2.0*(x*x + y*y)]
    ]

def mat_vec_mul(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]

# -----------------------------------------------------------------------------
# Integrador rígido canónico 6DOF (equivalente exacto a simular.py)
# -----------------------------------------------------------------------------
def rigid_rhs_pure(y, F_list, A_mat, I_vec, mass, ext_vec, et_vec):
    """
    Evaluación de derivadas de la dinámica de cuerpo rígido.
    y: [r(3), v(3), q(4), om(3)] (longitud 13)
    """
    q = quat_normalize(y[6:10])
    om = y[10:13]
    R_mat = quat_to_rot_matrix(q)

    # Suma de fuerzas de actuadores
    F_sum = [0.0, 0.0, 0.0]
    for F_i in F_list:
        F_sum = vec_add(F_sum, F_i)

    # Aceleración lineal inercial: R * F_sum + ext) / mass - [0, 0, g]
    acc_thrust = mat_vec_mul(R_mat, F_sum)
    acc = [
        (acc_thrust[0] + ext_vec[0]) / mass,
        (acc_thrust[1] + ext_vec[1]) / mass,
        (acc_thrust[2] + ext_vec[2]) / mass - G_CONST
    ]

    # Par neto de actuadores: A @ F.ravel()
    F_ravel = []
    for F_i in F_list:
        F_ravel.extend(F_i)
    torque_thrust = [sum(A_mat[row][col] * F_ravel[col] for col in range(12)) for row in range(3, 6)]
    torque = vec_add(torque_thrust, et_vec)

    # Derivada del cuaternión: qdot = 0.5 * [qw*om + qv x om, -qv . om]
    qv = q[:3]
    qw = q[3]
    cross_qv_om = vec_cross(qv, om)
    qdot_v = [0.5 * (qw * om[i] + cross_qv_om[i]) for i in range(3)]
    qdot_w = -0.5 * vec_dot(qv, om)
    qdot = qdot_v + [qdot_w]

    # Dinámica de Euler: dot_om = (torque - om x (I * om)) / I
    I_om = [I_vec[i] * om[i] for i in range(3)]
    gyro = vec_cross(om, I_om)
    dot_om = [(torque[i] - gyro[i]) / I_vec[i] for i in range(3)]

    # Retorna [v(3), acc(3), qdot(4), dot_om(3)]
    return y[3:6] + acc + qdot + dot_om

def rk4_step_pure(state, dt, F_list, A_mat, I_vec, mass, ext_vec, et_vec):
    """Paso Runge-Kutta de 4to orden con normalización de cuaternión al finalizar."""
    def f(y_eval):
        return rigid_rhs_pure(y_eval, F_list, A_mat, I_vec, mass, ext_vec, et_vec)

    k1 = f(state)
    y2 = [state[i] + 0.5 * dt * k1[i] for i in range(13)]
    k2 = f(y2)
    y3 = [state[i] + 0.5 * dt * k2[i] for i in range(13)]
    k3 = f(y3)
    y4 = [state[i] + dt * k3[i] for i in range(13)]
    k4 = f(y4)

    new_state = [state[i] + (dt / 6.0) * (k1[i] + 2.0*k2[i] + 2.0*k3[i] + k4[i]) for i in range(13)]
    # Normalizar cuaternión
    q_norm = quat_normalize(new_state[6:10])
    new_state[6:10] = q_norm
    return new_state


def main():
    print("=" * 78)
    print("VERIFICACIÓN ANALÍTICA INDEPENDIENTE (PYTHON ESTÁNDAR)")
    print("=" * 78)
    print("Objetivo: Evaluar cuantitativamente los tres casos canónicos en el integrador RK4.")

    mass = 5.0
    scale = (mass / 5.0) ** (1.0 / 3.0)
    I_vec = [
        mass * (0.321821**2 + 0.194110**2) / 20.0 * scale**2,
        mass * (1.341**2 + 0.194110**2) / 20.0 * scale**2,
        mass * (1.341**2 + 0.321821**2) / 20.0 * scale**2
    ]
    xy = [
        [-0.2 * scale, -0.076 * scale],
        [-0.2 * scale,  0.076 * scale],
        [ 0.2 * scale, -0.076 * scale],
        [ 0.2 * scale,  0.076 * scale]
    ]

    # Construir matriz A de 6x12
    A_mat = [[0.0 for _ in range(12)] for _ in range(6)]
    for i, (x, y) in enumerate(xy):
        A_mat[0][3*i]     = 1.0
        A_mat[1][3*i + 1] = 1.0
        A_mat[2][3*i + 2] = 1.0
        A_mat[3][3*i + 1] = 0.021 * scale
        A_mat[3][3*i + 2] = y
        A_mat[4][3*i]     = -0.039 * scale
        A_mat[4][3*i + 2] = -x
        A_mat[5][3*i]     = -y
        A_mat[5][3*i + 1] = x

    F_zeros = [[0.0, 0.0, 0.0] for _ in range(4)]
    ext_zero = [0.0, 0.0, 0.0]
    et_zero = [0.0, 0.0, 0.0]

    resultados = {}

    # -------------------------------------------------------------------------
    # TEST 1: Conservación de energía cinética y momento angular
    # -------------------------------------------------------------------------
    print("\n--- CASO 1: Conservación de invariantes en giro libre asimétrico ---")
    omega_0 = [1.5, 3.0, 0.8]  # rad/s
    q_0 = [0.0, 0.0, 0.0, 1.0]
    state_0 = [0.0]*6 + q_0 + omega_0

    E0 = 0.5 * sum(I_vec[i] * omega_0[i]**2 for i in range(3))
    H0_body = [I_vec[i] * omega_0[i] for i in range(3)]
    H0_inertial = mat_vec_mul(quat_to_rot_matrix(q_0), H0_body)
    norm_H0 = vec_norm(H0_inertial)

    dt_series = [0.02, 0.01, 0.005, 0.0025]
    T_sim = 2.0
    res_t1 = {}
    prev_err_E = float("inf")
    prev_err_H = float("inf")
    monotonic = True

    for dt in dt_series:
        steps = int(round(T_sim / dt))
        state = list(state_0)
        max_err_E = 0.0
        max_err_H = 0.0

        for _ in range(steps):
            state = rk4_step_pure(state, dt, F_zeros, A_mat, I_vec, mass, ext_zero, et_zero)
            om_k = state[10:13]
            q_k = state[6:10]
            Ek = 0.5 * sum(I_vec[i] * om_k[i]**2 for i in range(3))
            err_E = abs(Ek - E0) / E0
            if err_E > max_err_E:
                max_err_E = err_E

            H_body_k = [I_vec[i] * om_k[i] for i in range(3)]
            H_iner_k = mat_vec_mul(quat_to_rot_matrix(q_k), H_body_k)
            err_H = vec_norm(vec_sub(H_iner_k, H0_inertial)) / norm_H0
            if err_H > max_err_H:
                max_err_H = err_H

        if max_err_E > prev_err_E or max_err_H > prev_err_H:
            monotonic = False
        prev_err_E = max_err_E
        prev_err_H = max_err_H

        res_t1[f"dt_{dt}"] = {
            "dt_s": dt,
            "pasos": steps,
            "max_rel_err_E": max_err_E,
            "max_rel_err_H": max_err_H
        }
        print(f"  dt={dt:.4f}s | Pasos={steps:4d} | Max Err E: {max_err_E:.3e} | Max Err H: {max_err_H:.3e}")

    # Justificación de tolerancias:
    # A dt = 0.005s, RK4 acumula < 1e-5 en T=2.0s para giro no lineal.
    pass_t1 = (res_t1["dt_0.005"]["max_rel_err_E"] < 1e-5 and
               res_t1["dt_0.005"]["max_rel_err_H"] < 1e-5 and
               monotonic)
    res_t1["aprobado"] = pass_t1
    res_t1["convergencia_monotona"] = monotonic
    print(f"  => Dictamen Caso 1: {'APROBADO' if pass_t1 else 'FALLIDO'} (Convergencia monótona: {monotonic})")

    # -------------------------------------------------------------------------
    # TEST 2: Cuaternión en giro constante vs solución analítica
    # -------------------------------------------------------------------------
    print("\n--- CASO 2: Cuaternión en giro constante vs solución analítica ---")
    # Elegimos Omega = pi rad/s (180 deg/s) de modo que una revolución completa (2*pi rad)
    # ocurra exactamente en T = 2.0 s, coincidiendo de forma entera con dt = 0.005 s (400 pasos).
    Omega = math.pi  # rad/s sobre Z
    u_axis = [0.0, 0.0, 1.0]
    q_init = [0.0, 0.0, 0.0, 1.0]
    omega_init = [0.0, 0.0, Omega]
    state_t2 = [0.0]*6 + q_init + omega_init

    T_rev = 2.0 * math.pi / Omega  # 2.0 s
    dt_t2 = 0.005
    steps_t2 = int(round(T_rev / dt_t2))  # 400 pasos exactos

    max_geo_err = 0.0
    for step in range(1, steps_t2 + 1):
        t_curr = step * dt_t2
        state_t2 = rk4_step_pure(state_t2, dt_t2, F_zeros, A_mat, I_vec, mass, ext_zero, et_zero)
        q_num = state_t2[6:10]

        half_ang = 0.5 * Omega * t_curr
        q_analyt = [u_axis[0] * math.sin(half_ang),
                    u_axis[1] * math.sin(half_ang),
                    u_axis[2] * math.sin(half_ang),
                    math.cos(half_ang)]

        dot_p = abs(vec_dot(q_num, q_analyt))
        dot_p = min(1.0, max(-1.0, dot_p))
        geo_err = 2.0 * math.acos(dot_p)
        if geo_err > max_geo_err:
            max_geo_err = geo_err

    # A 360 grados exactos (t = 2.0 s), q debe invertir signo respecto a q0 (propiedad espinorial de cuaterniones)
    q_final = state_t2[6:10]
    q_esperado_360 = [0.0, 0.0, 0.0, -1.0]
    diff_spinor = vec_norm(vec_sub(q_final, q_esperado_360))

    # Justificación de tolerancia:
    # A 200 Hz sobre 400 pasos de función suave, RK4 acumula un error < 1e-7 rad.
    pass_t2 = (max_geo_err < 1e-7 and diff_spinor < 1e-6)
    res_t2 = {
        "Omega_rad_s": Omega,
        "eje": u_axis,
        "periodo_s": T_rev,
        "pasos": steps_t2,
        "max_error_geodesico_rad": max_geo_err,
        "max_error_geodesico_deg": math.degrees(max_geo_err),
        "diferencia_espinor_360deg": diff_spinor,
        "tolerancia_rad": 1e-7,
        "aprobado": pass_t2
    }
    print(f"  Revolución completada: T={T_rev:.4f}s ({steps_t2} pasos)")
    print(f"  Max error geodésico: {max_geo_err:.3e} rad ({math.degrees(max_geo_err):.3e} deg)")
    print(f"  q_final: {[round(x, 6) for x in q_final]} vs esperado [0, 0, 0, -1]")
    print(f"  Diferencia norma frente a espinor -q0: {diff_spinor:.3e}")
    print(f"  => Dictamen Caso 2: {'APROBADO' if pass_t2 else 'FALLIDO'}")

    # -------------------------------------------------------------------------
    # TEST 3: Par de fuerzas opuestas y momento resultante r x F
    # -------------------------------------------------------------------------
    print("\n--- CASO 3: Par de fuerzas opuestas y momento resultante r x F ---")
    F_mag = 10.0  # N
    # Ventilador 0 (aft-left) y Ventilador 2 (fore-left)
    # F0 = [0, 0, +10], F2 = [0, 0, -10]
    F_couple_pitch = [
        [0.0, 0.0, +F_mag],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, -F_mag],
        [0.0, 0.0, 0.0]
    ]

    # Fuerza neta
    F_net = [0.0, 0.0, 0.0]
    for F_i in F_couple_pitch:
        F_net = vec_add(F_net, F_i)
    err_F_net = vec_norm(F_net)

    # Torque por matriz A
    F_ravel = []
    for F_i in F_couple_pitch:
        F_ravel.extend(F_i)
    torque_A = [sum(A_mat[r][c] * F_ravel[c] for c in range(12)) for r in range(3, 6)]

    # Torque por definición geométrica r x F
    r0 = [xy[0][0], xy[0][1], 0.0]
    r2 = [xy[2][0], xy[2][1], 0.0]
    tau0 = vec_cross(r0, F_couple_pitch[0])
    tau2 = vec_cross(r2, F_couple_pitch[2])
    torque_geom = vec_add(tau0, tau2)
    err_torque = vec_norm(vec_sub(torque_A, torque_geom))

    # Torque esperado en pitch: (x0 - x2) * (-F_mag) = (-0.2 - 0.2) * (-10) = 4.0 N*m
    expected_pitch = 4.0 * scale
    err_pitch_val = abs(torque_A[1] - expected_pitch)

    # Consistencia dinámica a nivel de derivadas (rigid_rhs)
    y_test3 = [0.0, 0.0, 10.0, 0.0, 0.0, 0.0] + q_init + [0.0, 0.0, 0.0]
    rhs_eval = rigid_rhs_pure(y_test3, F_couple_pitch, A_mat, I_vec, mass, ext_zero, et_zero)

    # Aceleración lineal debe ser puramente -g en Z
    acc_lin = rhs_eval[3:6]
    err_acc_lin = vec_norm(vec_sub(acc_lin, [0.0, 0.0, -G_CONST]))

    # Aceleración angular debe ser torque / I
    acc_ang = rhs_eval[10:13]
    acc_ang_expected = [torque_A[i] / I_vec[i] for i in range(3)]
    err_acc_ang = vec_norm(vec_sub(acc_ang, acc_ang_expected))

    pass_t3 = (err_F_net < 1e-14 and
               err_torque < 1e-14 and
               err_pitch_val < 1e-14 and
               err_acc_lin < 1e-14 and
               err_acc_ang < 1e-14)

    res_t3 = {
        "F_magnitud_N": F_mag,
        "error_fuerza_neta_N": err_F_net,
        "torque_A_Nm": torque_A,
        "torque_geom_Nm": torque_geom,
        "error_torque_vs_rxF_Nm": err_torque,
        "error_aceleracion_lineal_vs_gravedad_ms2": err_acc_lin,
        "error_aceleracion_angular_vs_tau_sobre_I_rads2": err_acc_ang,
        "aprobado": pass_t3
    }
    print(f"  Fuerza neta resultante: {err_F_net:.2e} N (esperado 0.0)")
    print(f"  Torque matriz A: {[round(x, 4) for x in torque_A]} N*m")
    print(f"  Torque geométrico sum(r x F): {[round(x, 4) for x in torque_geom]} N*m")
    print(f"  Discrepancia matriz A vs r x F: {err_torque:.2e} N*m")
    print(f"  Error aceleración lineal vs -g: {err_acc_lin:.2e} m/s^2")
    print(f"  Error aceleración angular vs tau/I: {err_acc_ang:.2e} rad/s^2")
    print(f"  => Dictamen Caso 3: {'APROBADO' if pass_t3 else 'FALLIDO'}")

    resultados["pruebas_analiticas_puras"] = {
        "caso1_conservacion": res_t1,
        "caso2_cuaternion_analitico": res_t2,
        "caso3_par_fuerzas_rxF": res_t3
    }
    resultados["alcance_metodologico"] = {
        "tipo": "Verificacion analitica pura en Python estandar",
        "dependencias_externas_utilizadas": None,
        "relacion_con_simular_py": "Valida las ecuaciones matematicas identicas implementadas en simular.py sin importar numpy/scipy. El archivo simular.py no fue modificado.",
        "afirmacion_exito_sobre_simular_py": False,
        "validacion_fisica_afirmada": False
    }

    out_json = SALIDAS_DIR / "REPORTE_VERIFICACION_ANALITICA.json"
    out_json.write_text(json.dumps(resultados, indent=2))
    print("\n" + "=" * 78)
    print(f"Resultados de verificación analítica pura guardados en: {out_json}")
    print("=" * 78)
    return 0

if __name__ == "__main__":
    sys.exit(main())
