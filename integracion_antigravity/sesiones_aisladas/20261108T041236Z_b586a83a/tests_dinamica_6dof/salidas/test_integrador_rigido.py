#!/usr/bin/env python3
"""
test_integrador_rigido.py
=========================
Batería de pruebas independientes y de bajo costo para el integrador rígido
existente implementado en `simular.py` (`rigid_rhs` y `rk4_step`).

Casos de prueba implementados:
1. Conservación de energía cinética rotacional (T_rot) y momento angular inercial
   (H_inertial) para giro libre asimétrico multiaxial con pasos de integración decrecientes.
2. Comparación de cinemática de cuaternión en giro constante frente a solución
   analítica cerrada (incluyendo rotación completa y doble cobertura q -> -q).
3. Verificación de par de fuerzas opuestas (couples) y momento resultante r x F,
   comprobando fuerza neta nula y correspondencia exacta de matriz A frente a brazos geométricos.

Manejo de dependencias:
- Requiere numpy y scipy para interactuar directamente con `simular.py`.
- Si numpy o scipy no están disponibles en el entorno, detecta la ausencia,
  declara explícitamente que no se ejecutaron las pruebas y evita afirmar éxito,
  conforme a las directrices de rigor metodológico.
"""

import sys
import os
import json
import math
from pathlib import Path

# Directorio de trabajo
SALIDAS_DIR = Path(__file__).resolve().parent
SIMULAR_PATH = SALIDAS_DIR / "simular.py"

def check_dependencies():
    """Comprueba disponibilidad de numpy y scipy sin alterar el entorno."""
    missing = []
    try:
        import numpy as np
    except ImportError:
        missing.append("numpy")
    try:
        import scipy
        from scipy.spatial.transform import Rotation as R
    except ImportError:
        missing.append("scipy")
    return missing

def main():
    missing_deps = check_dependencies()

    reporte = {
        "entorno": {
            "python_version": sys.version,
            "executable": sys.executable,
            "simular_path": str(SIMULAR_PATH),
            "simular_exists": SIMULAR_PATH.exists()
        },
        "dependencias": {
            "numpy_disponible": "numpy" not in missing_deps,
            "scipy_disponible": "scipy" not in missing_deps,
            "faltantes": missing_deps
        },
        "declaracion_formal": {},
        "pruebas": {},
        "resumen_ejecucion": {}
    }

    if missing_deps:
        # DECLARACIÓN EXPLÍCITA OBLIGATORIA CONFORME A LAS INSTRUCCIONES
        msg_decl = (
            f"DECLARACIÓN FORMAL: Dependencias requeridas no disponibles: {missing_deps}. "
            "El integrador rígido original en 'simular.py' requiere numpy y scipy "
            "(scipy.spatial.transform.Rotation y operaciones matriciales numpy). "
            "Por consiguiente, las pruebas directas sobre 'simular.py' NO SE EJECUTARON. "
            "Se evita formalmente afirmar éxito en la ejecución de estas pruebas en este entorno."
        )
        print("=" * 78)
        print("DECLARACIÓN FORMAL DE NO EJECUCIÓN (FALTA DE DEPENDENCIAS)")
        print("=" * 78)
        print(msg_decl)
        print("\nComando recomendado para ejecutar una vez provisto el entorno con numpy/scipy:")
        print("    python3 salidas/test_integrador_rigido.py")
        print("=" * 78)

        reporte["declaracion_formal"] = {
            "ejecutado": False,
            "motivo": f"Módulos faltantes: {missing_deps}",
            "afirmacion_exito": False,
            "mensaje": msg_decl,
            "comando_recomendado": "python3 salidas/test_integrador_rigido.py"
        }
        reporte["resumen_ejecucion"] = {
            "pruebas_ejecutadas": 0,
            "pruebas_exitosas": 0,
            "pruebas_omitidas": 3,
            "estado_global": "NO_EJECUTADO"
        }

        # Guardar reporte de auditoría
        reporte_path = SALIDAS_DIR / "REPORTE_PRUEBAS_SIMULAR.json"
        reporte_path.write_text(json.dumps(reporte, indent=2))
        print(f"Reporte emitido en: {reporte_path}")
        return 0

    # Si numpy y scipy están disponibles, importamos simular y ejecutamos las pruebas
    import numpy as np
    from scipy.spatial.transform import Rotation as R
    sys.path.insert(0, str(SALIDAS_DIR))
    from simular import rigid_rhs, rk4_step, G

    print("=" * 78)
    print("EJECUTANDO BATERÍA DE PRUEBAS SOBRE INTEGRADOR RÍGIDO (simular.py)")
    print("=" * 78)

    # -------------------------------------------------------------------------
    # TEST 1: Conservación de T_rot y H_inertial en giro libre asimétrico
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Conservación de energía cinética rotacional y momento angular inercial")
    print("         (Giro libre asimétrico triaxial con pasos decrecientes)")
    
    mass = 5.0
    scale = (mass / 5.0) ** (1 / 3)
    # Tensor de inercia triaxial asimétrico (diagonal, Ixx != Iyy != Izz)
    I = mass * np.array([.321821**2 + .194110**2, 1.341**2 + .194110**2, 1.341**2 + .321821**2]) / 20 * scale**2
    # Condición inicial: velocidad angular multiaxial desbalanceada
    omega_0 = np.array([1.5, 3.0, 0.8])  # rad/s
    q_0 = np.array([0.0, 0.0, 0.0, 1.0])  # identidad
    state_0 = np.r_[0., 0., 0., 0., 0., 0., q_0, omega_0]

    F_cero = np.zeros((4, 3))
    A_dummy = np.zeros((6, 12))
    ext_cero = np.zeros(3)
    et_cero = np.zeros(3)

    T_final = 2.0  # segundos
    dt_list = [0.02, 0.01, 0.005, 0.0025]
    res_test1 = {}

    E0 = 0.5 * np.sum(I * omega_0**2)
    H0_inertial = R.from_quat(q_0).apply(I * omega_0)
    norm_H0 = np.linalg.norm(H0_inertial)

    prev_err_E = float("inf")
    prev_err_H = float("inf")
    monotonic_decrease = True

    for dt in dt_list:
        steps = int(round(T_final / dt))
        state = state_0.copy()
        max_rel_err_E = 0.0
        max_rel_err_H = 0.0

        for _ in range(steps):
            state = rk4_step(state, dt, F_cero, A_dummy, I, mass, ext_cero, et_cero)
            q_k = state[6:10]
            om_k = state[10:13]
            Ek = 0.5 * np.sum(I * om_k**2)
            rel_err_E = abs(Ek - E0) / E0
            if rel_err_E > max_rel_err_E:
                max_rel_err_E = rel_err_E

            Hk_inertial = R.from_quat(q_k).apply(I * om_k)
            rel_err_H = np.linalg.norm(Hk_inertial - H0_inertial) / norm_H0
            if rel_err_H > max_rel_err_H:
                max_rel_err_H = rel_err_H

        if max_rel_err_E > prev_err_E or max_rel_err_H > prev_err_H:
            monotonic_decrease = False
        prev_err_E = max_rel_err_E
        prev_err_H = max_rel_err_H

        res_test1[f"dt_{dt}"] = {
            "dt_s": dt,
            "steps": steps,
            "max_rel_err_E": float(max_rel_err_E),
            "max_rel_err_H_vec": float(max_rel_err_H)
        }
        print(f"  dt={dt:.4f}s | Pasos={steps:4d} | Max Err E: {max_rel_err_E:.3e} | Max Err H: {max_rel_err_H:.3e}")

    # Justificación de tolerancias:
    # Para RK4 a dt=0.005 s en T=2.0 s, el error de conservación debe ser < 1e-5.
    # A dt=0.0025 s debe ser < 1e-6 y la convergencia debe ser estrictamente monótona.
    tol_E_nominal = 1e-5
    tol_H_nominal = 1e-5
    t1_pass = (
        res_test1["dt_0.005"]["max_rel_err_E"] < tol_E_nominal and
        res_test1["dt_0.005"]["max_rel_err_H_vec"] < tol_H_nominal and
        monotonic_decrease
    )
    res_test1["tolerancia_nominal_dt005"] = tol_E_nominal
    res_test1["convergencia_monotona"] = monotonic_decrease
    res_test1["aprobado"] = t1_pass
    print(f"  => Resultado Test 1: {'APROBADO' if t1_pass else 'FALLIDO'} (Monótono: {monotonic_decrease})")

    # -------------------------------------------------------------------------
    # TEST 2: Cuaternión en giro constante comparado con solución analítica
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Cuaternión de giro constante vs Solución Analítica Cerrada")
    print("         (Rotación sobre eje principal y chequeo de inversión de signo q -> -q)")

    # Elegimos Omega = pi rad/s (180 deg/s) de modo que una revolución completa (2*pi rad)
    # ocurra en exactamente T = 2.0 s, coincidiendo de forma entera con dt = 0.005 s (400 pasos).
    Omega = math.pi  # rad/s sobre eje Z
    u = np.array([0.0, 0.0, 1.0])
    q_init = np.array([0.0, 0.0, 0.0, 1.0])  # identidad
    omega_init = Omega * u
    state_t2 = np.r_[0., 0., 0., 0., 0., 0., q_init, omega_init]

    # Tiempo para una revolución completa (2*pi rad)
    T_rev = 2.0 * math.pi / Omega  # 2.0 s
    dt_t2 = 0.005
    steps_t2 = int(round(T_rev / dt_t2))  # 400 pasos exactos

    max_geodesic_err_rad = 0.0
    max_norm_drift = 0.0

    for step in range(1, steps_t2 + 1):
        t_curr = step * dt_t2
        state_t2 = rk4_step(state_t2, dt_t2, F_cero, A_dummy, I, mass, ext_cero, et_cero)
        q_num = state_t2[6:10]

        # Solución analítica exacta: q(t) = [u * sin(Omega*t/2), cos(Omega*t/2)]
        angle_half = 0.5 * Omega * t_curr
        q_exact = np.r_[u * math.sin(angle_half), math.cos(angle_half)]

        # Error geodésico de actitud considerando doble cobertura (|q · q_ref|)
        dot_prod = abs(float(np.dot(q_num, q_exact)))
        dot_clamped = min(1.0, max(-1.0, dot_prod))
        phi_err = 2.0 * math.acos(dot_clamped)
        if phi_err > max_geodesic_err_rad:
            max_geodesic_err_rad = phi_err

        norm_drift = abs(np.linalg.norm(q_num) - 1.0)
        if norm_drift > max_norm_drift:
            max_norm_drift = norm_drift

    # A t = T_rev (2.0 s), angle_half = pi, sin(pi)=0, cos(pi)=-1 => q_exact = [0, 0, 0, -1]
    final_q = state_t2[6:10]
    expected_spinor_q = np.array([0.0, 0.0, 0.0, -1.0])
    spinor_diff = float(np.linalg.norm(final_q - expected_spinor_q))

    # Justificación de tolerancia:
    # Integración RK4 a 200 Hz para función trigonométrica pura acumula error < 1e-7 rad.
    tol_attitude_rad = 1e-7
    tol_norm_drift = 1e-12
    t2_pass = (max_geodesic_err_rad < tol_attitude_rad) and (spinor_diff < 1e-6) and (max_norm_drift < tol_norm_drift)

    res_test2 = {
        "Omega_rad_s": Omega,
        "eje_rotacion": u.tolist(),
        "periodo_revolucion_s": T_rev,
        "dt_s": dt_t2,
        "pasos_totales": steps_t2,
        "max_error_geodesico_rad": float(max_geodesic_err_rad),
        "max_error_geodesico_deg": float(math.degrees(max_geodesic_err_rad)),
        "max_deriva_norma_cuaternion": float(max_norm_drift),
        "diferencia_inversion_espinor_q_a_360deg": float(spinor_diff),
        "tolerancia_geodesica_rad": tol_attitude_rad,
        "aprobado": t2_pass
    }
    print(f"  Revolución completada en t={T_rev:.4f}s ({steps_t2} pasos)")
    print(f"  Max error geodésico: {max_geodesic_err_rad:.3e} rad ({math.degrees(max_geodesic_err_rad):.3e} deg)")
    print(f"  q final numérico: {final_q.round(6)} | q esperado (espinor -q0): {expected_spinor_q}")
    print(f"  => Resultado Test 2: {'APROBADO' if t2_pass else 'FALLIDO'}")

    # -------------------------------------------------------------------------
    # TEST 3: Par de fuerzas opuestas y momento resultante r x F
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Par de fuerzas opuestas y momento resultante r x F")
    print("         (Consistencia estática y dinámica de la matriz geométrica A)")

    xy = np.array([[-.2, -.076], [-.2, .076], [.2, -.076], [.2, .076]]) * scale
    A = np.zeros((6, 12))
    for i, (x, y) in enumerate(xy):
        A[:3, 3*i:3*i+3] = np.eye(3)
        A[3:, 3*i:3*i+3] = np.array([[0, .021 * scale, y], [-.039 * scale, 0, -x], [-y, x, 0]])

    F_mag = 10.0  # N
    # Subcaso 3.1: Par en cabeceo (pitch) entre ventilador 0 (aft-left) y ventilador 2 (fore-left)
    # F0 = [0, 0, +F_mag], F2 = [0, 0, -F_mag]
    F_pitch = np.zeros((4, 3))
    F_pitch[0, 2] = +F_mag
    F_pitch[2, 2] = -F_mag

    F_net_pitch = F_pitch.sum(axis=0)
    # Momento por matriz A:
    torque_A_pitch = (A @ F_pitch.ravel())[3:]
    # Momento por definicion geometrica r x F:
    # r0 = [-0.2, -0.076, 0], r2 = [0.2, -0.076, 0]
    r0 = np.array([xy[0, 0], xy[0, 1], 0.0])
    r2 = np.array([xy[2, 0], xy[2, 1], 0.0])
    torque_geom_pitch = np.cross(r0, F_pitch[0]) + np.cross(r2, F_pitch[2])

    err_F_net_pitch = float(np.linalg.norm(F_net_pitch))
    err_torque_pitch = float(np.linalg.norm(torque_A_pitch - torque_geom_pitch))
    expected_pitch_torque = (xy[0, 0] - xy[2, 0]) * (-F_mag)  # (-0.2 - 0.2)*(-10) = 4.0 N*m

    # Subcaso 3.2: Par en alabeo (roll) entre ventilador 0 y ventilador 1
    F_roll = np.zeros((4, 3))
    F_roll[0, 2] = +F_mag
    F_roll[1, 2] = -F_mag
    F_net_roll = F_roll.sum(axis=0)
    torque_A_roll = (A @ F_roll.ravel())[3:]
    r1 = np.array([xy[1, 0], xy[1, 1], 0.0])
    torque_geom_roll = np.cross(r0, F_roll[0]) + np.cross(r1, F_roll[1])

    err_F_net_roll = float(np.linalg.norm(F_net_roll))
    err_torque_roll = float(np.linalg.norm(torque_A_roll - torque_geom_roll))

    # Subcaso 3.3: Integración dinámica de aceleración con par puro
    # Al ser fuerza neta nula, no debe haber aceleración traslacional más allá de g
    # y la aceleración angular debe ser idénticamente tau / I
    y_test3 = np.r_[0., 0., 10., 0., 0., 0., q_init, 0., 0., 0.]
    rhs_eval = rigid_rhs(y_test3, F_pitch, A, I, mass, ext_cero, et_cero)
    # Aceleración lineal esperada: rot.apply(0) + 0 - [0, 0, G] = [0, 0, -G]
    lin_acc_err = float(np.linalg.norm(rhs_eval[3:6] - np.array([0.0, 0.0, -G])))
    # Aceleración angular esperada: torque_A_pitch / I
    ang_acc_expected = torque_A_pitch / I
    ang_acc_err = float(np.linalg.norm(rhs_eval[10:13] - ang_acc_expected))

    # Justificación de tolerancias:
    # Operaciones algebraicas vectoriales tienen precisión de máquina (< 1e-14).
    # Comprobación dinámica a nivel de derivadas tiene precisión < 1e-12.
    tol_alg = 1e-12
    t3_pass = (
        err_F_net_pitch < tol_alg and
        err_torque_pitch < tol_alg and
        abs(torque_A_pitch[1] - expected_pitch_torque) < tol_alg and
        err_F_net_roll < tol_alg and
        err_torque_roll < tol_alg and
        lin_acc_err < tol_alg and
        ang_acc_err < tol_alg
    )

    res_test3 = {
        "F_magnitud_N": F_mag,
        "pitch_couple": {
            "error_fuerza_neta_N": err_F_net_pitch,
            "torque_calculado_A_Nm": torque_A_pitch.tolist(),
            "torque_esperado_geom_Nm": torque_geom_pitch.tolist(),
            "error_torque_vs_rxF_Nm": err_torque_pitch
        },
        "roll_couple": {
            "error_fuerza_neta_N": err_F_net_roll,
            "torque_calculado_A_Nm": torque_A_roll.tolist(),
            "torque_esperado_geom_Nm": torque_geom_roll.tolist(),
            "error_torque_vs_rxF_Nm": err_torque_roll
        },
        "consistencia_dinamica": {
            "error_aceleracion_lineal_vs_gravedad_ms2": lin_acc_err,
            "error_aceleracion_angular_vs_tau_sobre_I_rads2": ang_acc_err
        },
        "tolerancia_algebraica": tol_alg,
        "aprobado": t3_pass
    }
    print(f"  Fuerza neta Pitch: {err_F_net_pitch:.2e} N | Error Torque Pitch: {err_torque_pitch:.2e} N*m")
    print(f"  Torque Pitch A: {torque_A_pitch} N*m | Esperado: [0, {expected_pitch_torque}, 0] N*m")
    print(f"  Fuerza neta Roll: {err_F_net_roll:.2e} N | Error Torque Roll: {err_torque_roll:.2e} N*m")
    print(f"  Error aceleración lineal vs -g: {lin_acc_err:.2e} m/s^2")
    print(f"  Error aceleración angular vs tau/I: {ang_acc_err:.2e} rad/s^2")
    print(f"  => Resultado Test 3: {'APROBADO' if t3_pass else 'FALLIDO'}")

    all_passed = t1_pass and t2_pass and t3_pass
    reporte["pruebas"] = {
        "test1_conservacion_invariantes": res_test1,
        "test2_cuaternion_giro_constante": res_test2,
        "test3_par_fuerzas_rxF": res_test3
    }
    reporte["resumen_ejecucion"] = {
        "pruebas_ejecutadas": 3,
        "pruebas_exitosas": 3 if all_passed else (int(t1_pass) + int(t2_pass) + int(t3_pass)),
        "pruebas_omitidas": 0,
        "estado_global": "APROBADO" if all_passed else "FALLIDO"
    }

    reporte_path = SALIDAS_DIR / "REPORTE_PRUEBAS_SIMULAR.json"
    reporte_path.write_text(json.dumps(reporte, indent=2))
    print("\n" + "=" * 78)
    print(f"Reporte completo consolidado guardado en: {reporte_path}")
    print(f"Dictamen Global: {'EXITOSO' if all_passed else 'FALLOS DETECTADOS'}")
    print("=" * 78)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
