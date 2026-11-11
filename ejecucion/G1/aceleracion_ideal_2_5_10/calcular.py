"""Referencia cinemática condicional de aceleración rectilínea, no de vuelo."""

import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
G_MS2 = 9.80665


def escenario(masa_kg, velocidad_kmh, aceleracion_g, eficiencia, energia_wh_kg, potencia_w_kg):
    valores = (masa_kg, velocidad_kmh, aceleracion_g, eficiencia, energia_wh_kg, potencia_w_kg)
    if not all(math.isfinite(x) and x > 0 for x in valores) or eficiencia > 1:
        raise ValueError("Entradas finitas y positivas; eficiencia en (0, 1].")
    velocidad_ms = velocidad_kmh / 3.6
    aceleracion_ms2 = aceleracion_g * G_MS2
    tiempo_s = velocidad_ms / aceleracion_ms2
    distancia_m = velocidad_ms * tiempo_s / 2
    fuerza_n = masa_kg * aceleracion_ms2
    energia_util_wh = 0.5 * masa_kg * velocidad_ms ** 2 / 3600
    potencia_util_w = fuerza_n * velocidad_ms
    energia_bateria_wh = energia_util_wh / eficiencia
    potencia_bateria_w = potencia_util_w / eficiencia
    masa_bateria_energia_kg = energia_bateria_wh / energia_wh_kg
    masa_bateria_potencia_kg = potencia_bateria_w / potencia_w_kg
    return dict(masa_objetivo_kg=masa_kg, velocidad_kmh=velocidad_kmh,
                aceleracion_g=aceleracion_g, tiempo_s=tiempo_s, distancia_m=distancia_m,
                fuerza_horizontal_n=fuerza_n, energia_cinetica_wh=energia_util_wh,
                potencia_util_final_w=potencia_util_w, energia_bateria_wh=energia_bateria_wh,
                potencia_bateria_final_w=potencia_bateria_w,
                masa_bateria_energia_kg=masa_bateria_energia_kg,
                masa_bateria_potencia_kg=masa_bateria_potencia_kg,
                masa_bateria_hipotetica_kg=max(masa_bateria_energia_kg, masa_bateria_potencia_kg))


def main():
    # These pack properties are joint hypothetical inputs, not product data.
    eta, wh_kg, w_kg = .70, 150.0, 5000.0
    rows = [escenario(m, v, a, eta, wh_kg, w_kg)
            for m in (2.0, 5.0, 10.0) for v in (600.0, 1000.0) for a in (.5, 1.0, 2.0, 5.0)]
    with (HERE / "ESCENARIOS.csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    (HERE / "HIPOTESIS.json").write_text(json.dumps({
        "escenarios": len(rows), "eficiencia_supuesta": eta,
        "energia_util_pack_Wh_kg_supuesta": wh_kg,
        "potencia_pack_W_kg_supuesta": w_kg,
        "alcance": "Cinemática horizontal ideal; no predice prestaciones del vehículo.",
        "omite": ["arrastre", "sustentación", "estacionario", "transición", "frenado", "viento", "potencia estática", "temperatura", "masa real y hardware"],
        "validacion_fisica": False,
    }, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(f"{len(rows)} escenarios ideales generados")


if __name__ == "__main__":
    main()
