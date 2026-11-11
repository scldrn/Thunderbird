#!/usr/bin/env python3
"""Cribado eléctrico condicional con carga simultánea en avance para C02."""

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
EJECUCION = HERE.parents[1]
SOURCE = EJECUCION / "G1/decision_integrada_c02/INFORME.md"
MASS_SOURCE = EJECUCION / "G3/C02/integracion_x160/MASA_INERCIA_PARCIAL.json"
MASS_KG = 5.0
HOVER_W = 2968.8083465960835
MANEUVER_W = 3505.892708058721
HOVER_S = 30.0
MANEUVER_S = 3.0
CRUISE_S = 30.0
EFFICIENCY = 0.7
PACK_WH_KG = 150.0
PACK_W_KG = 5000.0


def evaluate(speed_kmh, drag_N, accel_s, support_W):
    """Energía y pico de batería con apoyo eléctrico constante supuesto."""
    if speed_kmh <= 0 or drag_N < 0 or accel_s <= 0 or support_W < 0:
        raise ValueError("Velocidad y tiempo positivos; arrastre y apoyo no negativos.")
    v = speed_kmh / 3.6
    kinetic_J = 0.5 * MASS_KG * v**2
    accel_drag_J = drag_N * v * accel_s / 4.0
    cruise_drag_J = drag_N * v * CRUISE_S
    hover_Wh = (HOVER_W * (HOVER_S - MANEUVER_S) + MANEUVER_W * MANEUVER_S) / 3600.0
    axial_Wh = (kinetic_J + accel_drag_J + cruise_drag_J) / (3600.0 * EFFICIENCY)
    support_Wh = support_W * (accel_s + CRUISE_S) / 3600.0
    axial_peak_W = (MASS_KG * v**2 / accel_s + drag_N * v) / EFFICIENCY
    pack_peak_W = max(MANEUVER_W, axial_peak_W + support_W)
    total_Wh = hover_Wh + axial_Wh + support_Wh
    return {
        "velocidad_kmh": speed_kmh,
        "arrastre_final_N_supuesto": drag_N,
        "tiempo_aceleracion_s": accel_s,
        "distancia_aceleracion_m": v * accel_s / 2.0,
        "potencia_apoyo_W_supuesta": support_W,
        "energia_estacionario_Wh": hover_Wh,
        "energia_axial_Wh": axial_Wh,
        "energia_apoyo_simultaneo_Wh": support_Wh,
        "energia_total_Wh": total_Wh,
        "pico_axial_W": axial_peak_W,
        "pico_bateria_W": pack_peak_W,
        "masa_bateria_energia_kg": total_Wh / PACK_WH_KG,
        "masa_bateria_potencia_kg": pack_peak_W / PACK_W_KG,
        "masa_bateria_minima_kg": max(total_Wh / PACK_WH_KG, pack_peak_W / PACK_W_KG),
    }


def best_time(speed_kmh, drag_N, support_W, time_min_s, time_max_s):
    """Minimiza max(masa por energía, masa por potencia) en el intervalo."""
    if not 0 < time_min_s <= time_max_s:
        raise ValueError("Intervalo de tiempos inválido.")

    def difference(t):
        row = evaluate(speed_kmh, drag_N, t, support_W)
        return row["masa_bateria_energia_kg"] - row["masa_bateria_potencia_kg"]

    low, high = time_min_s, time_max_s
    candidates = [low, high]
    # El pico puede quedar limitado por la maniobra previa. En ese tramo la
    # masa mínima puede ser plana: incluir el inicio de la meseta permite
    # elegir el tiempo más corto, además de la misma masa óptima.
    v = speed_kmh / 3.6
    available_for_inertia_W = MANEUVER_W - support_W - drag_N * v / EFFICIENCY
    if available_for_inertia_W > 0:
        plateau_start_s = MASS_KG * v**2 / (EFFICIENCY * available_for_inertia_W)
        if low <= plateau_start_s <= high:
            candidates.append(plateau_start_s)
    if difference(low) < 0.0 < difference(high):
        for _ in range(70):
            mid = (low + high) / 2.0
            if difference(mid) < 0:
                low = mid
            else:
                high = mid
        candidates.append((low + high) / 2.0)
    rows = [evaluate(speed_kmh, drag_N, t, support_W) for t in candidates]
    minimum_mass = min(row["masa_bateria_minima_kg"] for row in rows)
    return min(
        (row for row in rows if row["masa_bateria_minima_kg"] <= minimum_mass + 1e-10),
        key=lambda item: item["tiempo_aceleracion_s"],
    )


def drag_threshold(speed_kmh, support_W, time_max_s, available_kg):
    """Máximo D admisible por batería en el escenario, o None si falla D=0."""
    def margin(drag_N):
        return available_kg - best_time(speed_kmh, drag_N, support_W, 10.0, time_max_s)["masa_bateria_minima_kg"]

    if margin(0.0) < -1e-12:
        return None
    low, high = 0.0, 1.0
    while margin(high) >= 0:
        high *= 2.0
        if high > 1e6:
            raise RuntimeError("No se encontró un límite finito de arrastre.")
    for _ in range(60):
        mid = (low + high) / 2.0
        if margin(mid) >= 0:
            low = mid
        else:
            high = mid
    return low


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # Los archivos de masa del CAD contienen hipótesis, no pesajes.
    data = json.loads(MASS_SOURCE.read_text(encoding="utf-8"))
    hypotheses = {
        item["hypothesis"]: item
        for item in data["hypotheses"]
        if item["hypothesis"] in ("ligera_1200", "mixta_1600")
    }
    assert len(hypotheses) == 2
    assert all(item["unidentified_part_records"] == 54 for item in hypotheses.values())
    rows = []
    thresholds = []
    for name, item in hypotheses.items():
        partial_kg = item["partial_assigned_mass_kg"]
        reserve_kg = item["provisional_reserve_kg"]
        for additional_kg in (0.0, 0.5):
            available_kg = MASS_KG - partial_kg - reserve_kg - additional_kg
            for speed in (600.0, 1000.0):
                for max_time in (60.0, 180.0):
                    for support in (0.0, 1000.0, HOVER_W):
                        threshold = drag_threshold(speed, support, max_time, available_kg)
                        thresholds.append({
                            "hipotesis_masa": name,
                            "masa_adicional_no_identificada_kg_supuesta": additional_kg,
                            "velocidad_kmh": speed,
                            "tiempo_maximo_aceleracion_s": max_time,
                            "potencia_apoyo_W_supuesta": support,
                            "masa_disponible_bateria_kg": available_kg,
                            "arrastre_maximo_N_condicional": threshold,
                            "ningun_arrastre_no_negativo_cumple": threshold is None,
                        })
                        for drag in (0.0, 10.0, 25.0, 50.0):
                            row = best_time(speed, drag, support, 10.0, max_time)
                            row.update({
                                "hipotesis_masa": name,
                                "masa_adicional_no_identificada_kg_supuesta": additional_kg,
                                "masa_disponible_bateria_kg": available_kg,
                                "tiempo_maximo_aceleracion_s": max_time,
                                "saldo_bateria_kg": available_kg - row["masa_bateria_minima_kg"],
                                "acepta_limites_de_este_escenario": row["masa_bateria_minima_kg"] <= available_kg,
                                "capacidad_real_demostrada": False,
                            })
                            rows.append(row)
    assert len(rows) == 192 and len(thresholds) == 48
    csv_path = HERE / "ESCENARIOS_r2.csv"
    result_path = HERE / "RESULTADOS_r2.json"
    if csv_path.exists() or result_path.exists():
        raise FileExistsError("Se conservan resultados previos; no se sobrescriben.")
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "alcance": "Sensibilidad condicional C02 de 5 kg; no valida hardware ni vuelo.",
        "cantidad_escenarios": len(rows),
        "cantidad_umbrales": len(thresholds),
        "umbral_arrastre": thresholds,
        "hipotesis": {
            "masa_vehiculo_kg": MASS_KG,
            "velocidades_kmh": [600.0, 1000.0],
            "estacionario_s_incluye_maniobra": HOVER_S,
            "maniobra_s": MANEUVER_S,
            "potencia_estacionario_W_exploratoria_C01": HOVER_W,
            "potencia_maniobra_W_exploratoria_C01": MANEUVER_W,
            "crucero_s": CRUISE_S,
            "eficiencia_axial": EFFICIENCY,
            "energia_pack_Wh_kg": PACK_WH_KG,
            "potencia_pack_W_kg": PACK_W_KG,
            "aceleracion_rectilinea_constante": True,
            "arrastre": "D(v)=D_final*(v/V)^2",
            "apoyo": "Potencia eléctrica constante hipotética añadida a aceleración y crucero; no mapa del ventilador.",
            "tiempos_aceleracion_s": "10–60 o 10–180, seleccionados como límites de escenario, no requisitos aprobados.",
        },
        "limitaciones": [
            "P_aux no es medición ni cota física universal de potencia de sustentación en avance.",
            "No modela fuerza vertical efectiva, trimado, transición, pérdida de sustentación ni dinámica.",
            "Potencia y energía específicas del pack no identifican una batería ni garantizan duración de pico.",
            "No modela voltaje, corriente, temperatura, resistencia interna, degradación o enfriamiento.",
            "No incluye frenado, ascenso, giros ni recuperación, ni masa real de hardware no identificado.",
            "La masa geométrica parcial no es cota inferior ni incluye toda la instalación.",
            "Los arrastres y eficiencias son escenarios; no resultados CFD aceptados ni ensayos.",
            "No se extrapola C02 a variantes físicas de 2 o 10 kg.",
        ],
        "fuentes_locales_sha256": {
            "informe_previo": sha256(SOURCE),
            "masa_parcial": sha256(MASS_SOURCE),
            "codigo": sha256(Path(__file__).resolve()),
        },
        "validacion_fisica": False,
    }
    result_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{len(rows)} escenarios; {len(thresholds)} umbrales guardados en {HERE}")


if __name__ == "__main__":
    main()
