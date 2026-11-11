#!/usr/bin/env python3
"""Sensibilidad LP ideal a posición vertical de la fuerza efectiva en C02."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import calcular_autoridad as base


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "sensibilidad_brazo_r1"


def solve(centres, cg_x_m, relative_z_m, theta_deg, limit_N, roll_Nm, direction):
    """Maximiza fuerza en ±x con M=objetivo y Fz=mg; no es vuelo dinámico."""
    if direction not in (-1, 1):
        raise ValueError("La dirección debe ser +1 o -1.")
    centres = np.asarray(centres, dtype=float)
    if centres.shape != (4, 3):
        raise ValueError("Se requieren cuatro centros de fuerza.")
    cg = np.array([cg_x_m, 0.0, -relative_z_m])
    vectors = base.rays(theta_deg)
    forces, moments, groups = base.matrices(centres, cg, vectors)
    aeq = np.vstack([forces[1], forces[2], moments])
    beq = np.array([0.0, base.MASS * base.G, roll_Nm, 0.0, 0.0])
    result = linprog(-direction * forces[0], A_ub=groups, b_ub=np.full(4, limit_N),
                     A_eq=aeq, b_eq=beq, bounds=(0.0, None), method="highs")
    common = {
        "cg_x_m_supuesto": cg_x_m,
        "brazo_vertical_relativo_m_supuesto": relative_z_m,
        "cono_grados_supuesto": theta_deg,
        "limite_por_ventilador_N_supuesto": limit_N,
        "momento_alabeo_Nm_supuesto": roll_Nm,
        "direccion_x": direction,
        "estado_lp": int(result.status),
    }
    if not result.success:
        return {**common, "solucion_lp": False, "mensaje_lp": result.message}
    weights = result.x
    fan_forces = np.stack([
        vectors.T @ weights[i * len(vectors):(i + 1) * len(vectors)]
        for i in range(4)
    ])
    total_force = fan_forces.sum(axis=0)
    total_moment = np.cross(centres - cg, fan_forces).sum(axis=0)
    np.testing.assert_allclose(aeq @ weights, beq, atol=2e-7, rtol=0.0)
    np.testing.assert_allclose(total_moment, [roll_Nm, 0.0, 0.0], atol=2e-7, rtol=0.0)
    assert weights.min() >= -1e-9 and (groups @ weights).max() <= limit_N + 1e-7
    assert np.linalg.norm(fan_forces, axis=1).max() <= limit_N + 1e-7
    # Identidad independiente: My=0, con z común y fuerzas verticales que suman mg.
    np.testing.assert_allclose(np.dot(centres[:, 0], fan_forces[:, 2]),
        cg_x_m * base.MASS * base.G + relative_z_m * total_force[0], atol=2e-7, rtol=0.0)
    signed_accel = direction * total_force[0] / base.MASS
    return {
        **common,
        "solucion_lp": True,
        "aceleracion_en_direccion_g": float(signed_accel / base.G),
        "fuerza_total_N": total_force.tolist(),
        "momento_total_Nm": total_moment.tolist(),
        "fuerzas_modulos_N": fan_forces.tolist(),
        "solicitud_positiva_alcanzada": bool(signed_accel > 1e-9),
        "error_max_igualdad": float(np.max(np.abs(aeq @ weights - beq))),
    }


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads(base.CONFIG.read_text(encoding="utf-8"))
    xy = np.array(config["fan_reference"]["centres_xy_m"])
    centres = np.column_stack([xy, np.zeros(4)])
    np.testing.assert_allclose(np.sort(np.unique(xy[:, 0])), [-0.16, 0.16])
    np.testing.assert_allclose(np.sort(np.unique(xy[:, 1])), [-0.076, 0.076])
    scenarios = []
    for cg_x in (0.0, 0.04, 0.08, 0.096, 0.12):
        for relative_z in (-0.039, -0.02, 0.0, 0.02, 0.039):
            for theta in (35.0, 45.0):
                for limit in (20.58, 25.0):
                    for roll in (0.0, 0.5):
                        for direction in (-1, 1):
                            scenarios.append(solve(centres, cg_x, relative_z, theta, limit, roll, direction))
    assert len(scenarios) == 400
    OUTPUT.mkdir(exist_ok=False)
    compact = [
        {k: v for k, v in item.items() if k not in (
            "mensaje_lp", "fuerza_total_N", "momento_total_Nm", "fuerzas_modulos_N")}
        for item in scenarios
    ]
    with (OUTPUT / "ESCENARIOS.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=sorted(set().union(*(r.keys() for r in compact))))
        writer.writeheader()
        writer.writerows(compact)
    report = {
        "alcance": "Cribado estático de conos ideales; no predice capacidad instalada ni trayectoria.",
        "numero_escenarios": len(scenarios),
        "masa_kg_supuesta": base.MASS,
        "gravedad_m_s2": base.G,
        "centros_CAD_m": centres.tolist(),
        "convencion_brazo_vertical": "z del centro de fuerza efectivo menos z del CG; igual para todos los módulos",
        "cono_es_casco_interior_discretizado": True,
        "fuente_limites": "20,58/25 N y conos 35/45 grados son hipótesis no medidas para C02.",
        "efectos_no_modelados": ["rotor instalado", "par de reacción", "giroscopía", "planta dinámica", "aerodinámica exterior", "retardos", "Fz mínima"],
        "centroide_parcial_C02_no_es_cg_real": True,
        "capacidad_fisica_aceptada": False,
        "huellas_sha256": {"configuracion": sha256(base.CONFIG), "modulo_base": sha256(Path(base.__file__)), "codigo": sha256(Path(__file__))},
        "escenarios": scenarios,
    }
    (OUTPUT / "RESULTADOS.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{len(scenarios)} escenarios guardados en {OUTPUT}")


if __name__ == "__main__":
    main()
