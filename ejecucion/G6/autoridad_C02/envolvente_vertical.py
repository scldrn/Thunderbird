#!/usr/bin/env python3
"""Autoridad vertical ideal de cuatro módulos unidireccionales de C02."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import calcular_autoridad as base


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "envolvente_vertical_r1"


def matrices_for(centres, cg_x_m, z_relative_m, cone_deg):
    centres = np.asarray(centres, dtype=float)
    if centres.shape != (4, 3) or not np.allclose(centres[:, 2], 0.0):
        raise ValueError("Se requieren cuatro centros en el plano nominal z=0.")
    cg = np.array([cg_x_m, 0.0, -z_relative_m])
    vectors = base.rays(cone_deg)
    forces, moments, groups = base.matrices(centres, cg, vectors)
    return forces, moments, groups


def horizontal_limit(centres, cg_x_m, z_relative_m, cone_deg, limit_N, az_g, direction):
    if direction not in (-1, 1):
        raise ValueError("Dirección horizontal debe ser +1 o -1.")
    f, moments, groups = matrices_for(centres, cg_x_m, z_relative_m, cone_deg)
    beq = np.array([0.0, base.MASS * base.G * (1.0 + az_g), 0.0, 0.0, 0.0])
    aeq = np.vstack([f[1], f[2], moments])
    result = linprog(-direction * f[0], A_ub=groups, b_ub=np.full(4, limit_N),
                     A_eq=aeq, b_eq=beq, bounds=(0.0, None), method="highs")
    row = {
        "cg_x_m_supuesto": cg_x_m,
        "brazo_vertical_m_supuesto": z_relative_m,
        "cono_grados_supuesto": cone_deg,
        "limite_modulo_N_supuesto": limit_N,
        "aceleracion_vertical_g_supuesta": az_g,
        "direccion_x": direction,
        "estado_lp": int(result.status),
        "solucion_lp": bool(result.success),
    }
    if result.success:
        residual = float(np.max(np.abs(aeq @ result.x - beq)))
        assert residual < 2e-7 and np.min(result.x) >= -1e-9
        assert np.max(groups @ result.x) <= limit_N + 1e-7
        row["aceleracion_horizontal_g"] = float(direction * (f[0] @ result.x) / (base.MASS * base.G))
        row["residuo_max_igualdad"] = residual
    else:
        row["mensaje_lp"] = result.message
    return row


def vertical_limit(centres, cg_x_m, z_relative_m, cone_deg, limit_N):
    f, moments, groups = matrices_for(centres, cg_x_m, z_relative_m, cone_deg)
    aeq = np.vstack([f[0], f[1], moments])
    result = linprog(-f[2], A_ub=groups, b_ub=np.full(4, limit_N),
                     A_eq=aeq, b_eq=np.zeros(5), bounds=(0.0, None), method="highs")
    assert result.success and np.max(np.abs(aeq @ result.x)) < 2e-7
    fz_max = float(f[2] @ result.x)
    return {"fuerza_vertical_total_max_N": fz_max,
            "aceleracion_vertical_max_g": fz_max / (base.MASS * base.G) - 1.0,
            "puede_equilibrar_peso_en_lp": fz_max >= base.MASS * base.G - 1e-8}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads(base.CONFIG.read_text(encoding="utf-8"))
    xy = np.array(config["fan_reference"]["centres_xy_m"])
    centres = np.column_stack([xy, np.zeros(4)])
    cases = []
    vertical = []
    for cg_x in (0.0, 0.04, 0.08, 0.096, 0.12):
        for z_relative in (0.0, 0.039):
            for cone in (35.0, 45.0):
                for limit in (20.58, 25.0):
                    bound = vertical_limit(centres, cg_x, z_relative, cone, limit)
                    bound.update({"cg_x_m_supuesto": cg_x, "brazo_vertical_m_supuesto": z_relative,
                                  "cono_grados_supuesto": cone, "limite_modulo_N_supuesto": limit})
                    vertical.append(bound)
                    for az in (-1.2, -1.0, -0.5, 0.0, 0.05, 0.2, 0.5):
                        for direction in (-1, 1):
                            cases.append(horizontal_limit(centres, cg_x, z_relative, cone, limit, az, direction))
    assert len(cases) == 560 and len(vertical) == 40
    OUTPUT.mkdir(exist_ok=False)
    compact = [{k: v for k, v in row.items() if k != "mensaje_lp"} for row in cases]
    with (OUTPUT / "ESCENARIOS.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=sorted(set().union(*(r.keys() for r in compact))))
        writer.writeheader()
        writer.writerows(compact)
    result = {
        "alcance": "Envolvente estática condicionada; gravedad y conos ideales unidireccionales, sin otras fuerzas.",
        "cantidad_escenarios": len(cases),
        "cantidad_limites_verticales": len(vertical),
        "masa_kg_supuesta": base.MASS,
        "casos": cases,
        "limites_verticales": vertical,
        "huellas_sha256": {"configuracion": sha(base.CONFIG), "modulo_base": sha(Path(base.__file__)), "codigo": sha(Path(__file__))},
        "limitaciones": [
            "Conos, magnitudes y centro de gravedad son supuestos; no hay mapa instalado ni motor identificado.",
            "El resultado no incluye sustentación o arrastre aerodinámicos, fuerza axial adicional ni empuje reversible.",
            "No hay dinámica, retardo, tasa, potencia, reacción, giroscopía ni control de actitud.",
            "La inviabilidad del poliedro interior no prueba inviabilidad de todo el cono continuo.",
        ],
        "capacidad_fisica_aceptada": False,
    }
    (OUTPUT / "RESULTADOS.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{len(cases)} escenarios y {len(vertical)} límites verticales guardados en {OUTPUT}")


if __name__ == "__main__":
    main()
