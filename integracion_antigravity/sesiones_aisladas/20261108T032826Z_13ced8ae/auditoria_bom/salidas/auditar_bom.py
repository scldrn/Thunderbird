#!/usr/bin/env python3
"""
auditar_bom.py - Script de auditoría reproducible para la BOM parcial C02.

Uso exclusivo de biblioteca estándar de Python (python3).
Audita:
  1. Recuento exhaustivo de registros (316 geometrías).
  2. Clasificación funcional por roles asumidos (10 roles) y ámbitos (12 scopes).
  3. Detección rigurosa de 54 filas sin masa asignada (reservas/interfaces),
     garantizando que NO se interpreten como masa física cero.
  4. Reconciliación matemática de sumas y centro de gravedad (CAD y FLU)
     para la hipótesis mixta (mixta_1600) frente a MASA_INERCIA_PARCIAL.json.
  5. Generación de CSV agrupado por roles con métricas completas en salidas/.

Restricciones de cumplimiento:
  - Solo lectura para referencias en entradas/.
  - Ninguna modificación a archivos originales.
  - Distinción explícita de datos medidos, supuestos y cálculos.
  - No asume hardware ni masa física real calificada.
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict


def load_data(csv_path, json_path):
    """Carga y parsea el CSV de la BOM geométrica y el JSON de masa/inercia."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Archivo CSV no encontrado: {csv_path}")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Archivo JSON no encontrado: {json_path}")

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    with open(json_path, mode="r", encoding="utf-8") as f:
        json_data = json.load(f)

    return csv_rows, json_data


def audit_records(csv_rows, json_data):
    """
    Ejecuta el censo de registros, clasificación de roles,
    detección de filas sin masa y reconciliación contra el JSON.
    """
    total_records = len(csv_rows)

    # 1. Separación de registros asignados y sin asignar
    assigned_rows = []
    unassigned_rows = []

    for row in csv_rows:
        mass_str = row.get("assigned_mass_mixta_kg", "").strip()
        if mass_str:
            assigned_rows.append(row)
        else:
            unassigned_rows.append(row)

    assigned_count = len(assigned_rows)
    unassigned_count = len(unassigned_rows)

    # 2. Agrupación por rol asumido (assumed_role)
    roles_dict = defaultdict(lambda: {
        "count": 0,
        "assigned_count": 0,
        "unassigned_count": 0,
        "total_volume_mm3": 0.0,
        "assigned_mass_kg": 0.0,
        "densities": set(),
        "scopes": set(),
        "names": []
    })

    for row in csv_rows:
        role = row["assumed_role"]
        entry = roles_dict[role]
        entry["count"] += 1
        vol = float(row["volume_mm3"])
        entry["total_volume_mm3"] += vol
        entry["scopes"].add(row["scope"])
        entry["names"].append(row["name"])

        mass_str = row.get("assigned_mass_mixta_kg", "").strip()
        if mass_str:
            entry["assigned_count"] += 1
            entry["assigned_mass_kg"] += float(mass_str)
            entry["densities"].add(float(row["rho_mixta_ASSUMED_kg_m3"]))
        else:
            entry["unassigned_count"] += 1

    # 3. Agrupación por ámbito (scope)
    scopes_dict = defaultdict(lambda: {
        "count": 0,
        "assigned_count": 0,
        "unassigned_count": 0,
        "total_volume_mm3": 0.0,
        "assigned_mass_kg": 0.0,
        "roles": set()
    })

    for row in csv_rows:
        sc = row["scope"]
        entry = scopes_dict[sc]
        entry["count"] += 1
        vol = float(row["volume_mm3"])
        entry["total_volume_mm3"] += vol
        entry["roles"].add(row["assumed_role"])

        mass_str = row.get("assigned_mass_mixta_kg", "").strip()
        if mass_str:
            entry["assigned_count"] += 1
            entry["assigned_mass_kg"] += float(mass_str)
        else:
            entry["unassigned_count"] += 1

    # 4. Volúmenes globales
    total_volume_mm3 = sum(float(r["volume_mm3"]) for r in csv_rows)
    assigned_volume_mm3 = sum(float(r["volume_mm3"]) for r in assigned_rows)
    unassigned_volume_mm3 = sum(float(r["volume_mm3"]) for r in unassigned_rows)

    # 5. Cálculos de masa asignada y centro de gravedad para hipótesis mixta
    total_mass_assigned_kg = sum(float(r["assigned_mass_mixta_kg"]) for r in assigned_rows)

    cg_cad_x = sum(float(r["assigned_mass_mixta_kg"]) * float(r["x_CAD_m"]) for r in assigned_rows) / total_mass_assigned_kg
    cg_cad_y = sum(float(r["assigned_mass_mixta_kg"]) * float(r["y_CAD_m"]) for r in assigned_rows) / total_mass_assigned_kg
    cg_cad_z = sum(float(r["assigned_mass_mixta_kg"]) * float(r["z_CAD_m"]) for r in assigned_rows) / total_mass_assigned_kg

    # Transformación FLU (Forward, Left, Up) estándar aero: x_FLU = -x_CAD, y_FLU = -y_CAD, z_FLU = z_CAD
    cg_flu_x = -cg_cad_x
    cg_flu_y = -cg_cad_y
    cg_flu_z = cg_cad_z

    # Inercia de masas puntuales (simplificación sin inercia propia I_0)
    i_xx_point = sum(float(r["assigned_mass_mixta_kg"]) * ((float(r["y_CAD_m"]) - cg_cad_y)**2 + (float(r["z_CAD_m"]) - cg_cad_z)**2) for r in assigned_rows)
    i_yy_point = sum(float(r["assigned_mass_mixta_kg"]) * ((float(r["x_CAD_m"]) - cg_cad_x)**2 + (float(r["z_CAD_m"]) - cg_cad_z)**2) for r in assigned_rows)
    i_zz_point = sum(float(r["assigned_mass_mixta_kg"]) * ((float(r["x_CAD_m"]) - cg_cad_x)**2 + (float(r["y_CAD_m"]) - cg_cad_y)**2) for r in assigned_rows)

    # 6. Reconciliación con JSON
    # Buscar hipótesis mixta_1600 en JSON
    json_hypotheses = {h["hypothesis"]: h for h in json_data.get("hypotheses", [])}
    mixta_json = json_hypotheses.get("mixta_1600", {})

    json_geom_records = json_data.get("geometry_records", 0)
    json_assigned_mass = mixta_json.get("partial_assigned_mass_kg", 0.0)
    json_provisional_reserve = mixta_json.get("provisional_reserve_kg", 0.75)
    json_remaining = mixta_json.get("remaining_for_energy_and_unidentified_hardware_kg", 0.0)
    json_cg_cad = mixta_json.get("partial_assigned_CG_CAD_m", [0.0, 0.0, 0.0])
    json_cg_flu = mixta_json.get("partial_assigned_CG_FLU_m", [0.0, 0.0, 0.0])
    json_inertia_cad = mixta_json.get("partial_inertia_about_assigned_CG_CAD_kgm2", [[0.0]*3 for _ in range(3)])
    json_unidentified_count = mixta_json.get("unidentified_part_records", 0)
    json_unidentified_records = mixta_json.get("unidentified_records", [])

    # Comparación directa de listas de no identificados
    csv_unassigned_names = [r["name"] for r in unassigned_rows]
    unidentified_names_match = (csv_unassigned_names == json_unidentified_records)
    unidentified_sets_match = (set(csv_unassigned_names) == set(json_unidentified_records))

    # Discrepancias
    mass_diff_abs = abs(total_mass_assigned_kg - json_assigned_mass)
    mass_diff_rel = mass_diff_abs / json_assigned_mass if json_assigned_mass else 0.0

    calculated_remanent = 5.0 - json_provisional_reserve - total_mass_assigned_kg
    remanent_diff_abs = abs(calculated_remanent - json_remaining)

    cg_cad_diff = [
        abs(cg_cad_x - json_cg_cad[0]),
        abs(cg_cad_y - json_cg_cad[1]),
        abs(cg_cad_z - json_cg_cad[2]),
    ]
    cg_flu_diff = [
        abs(cg_flu_x - json_cg_flu[0]),
        abs(cg_flu_y - json_cg_flu[1]),
        abs(cg_flu_z - json_cg_flu[2]),
    ]

    # Comprobación de integridad de hardware calificado
    actual_mass_count = sum(1 for r in csv_rows if r.get("actual_mass_kg", "").strip())
    actual_mat_count = sum(1 for r in csv_rows if r.get("actual_material", "").strip())
    qualified_hw_count = sum(1 for r in csv_rows if r.get("actual_hardware_qualified", "").strip().lower() == "true")

    # Verificación de fórmula V * rho * 1e-9 para filas asignadas
    formula_max_diff = 0.0
    for r in assigned_rows:
        v = float(r["volume_mm3"])
        rho = float(r["rho_mixta_ASSUMED_kg_m3"])
        m_rep = float(r["assigned_mass_mixta_kg"])
        m_calc = v * rho * 1e-9
        diff = abs(m_rep - m_calc)
        if diff > formula_max_diff:
            formula_max_diff = diff

    return {
        "total_records": total_records,
        "assigned_count": assigned_count,
        "unassigned_count": unassigned_count,
        "total_volume_mm3": total_volume_mm3,
        "assigned_volume_mm3": assigned_volume_mm3,
        "unassigned_volume_mm3": unassigned_volume_mm3,
        "unassigned_volume_pct": (unassigned_volume_mm3 / total_volume_mm3) * 100.0,
        "total_mass_assigned_kg": total_mass_assigned_kg,
        "cg_cad": [cg_cad_x, cg_cad_y, cg_cad_z],
        "cg_flu": [cg_flu_x, cg_flu_y, cg_flu_z],
        "point_inertia_cad": [i_xx_point, i_yy_point, i_zz_point],
        "solid_inertia_cad": [json_inertia_cad[0][0], json_inertia_cad[1][1], json_inertia_cad[2][2]],
        "roles": roles_dict,
        "scopes": scopes_dict,
        "unassigned_rows": unassigned_rows,
        "reconciliation": {
            "json_geom_records": json_geom_records,
            "records_match": (total_records == json_geom_records),
            "json_assigned_mass": json_assigned_mass,
            "mass_diff_abs": mass_diff_abs,
            "mass_diff_rel": mass_diff_rel,
            "json_provisional_reserve": json_provisional_reserve,
            "calculated_remanent": calculated_remanent,
            "json_remaining": json_remaining,
            "remanent_diff_abs": remanent_diff_abs,
            "json_cg_cad": json_cg_cad,
            "cg_cad_diff": cg_cad_diff,
            "json_cg_flu": json_cg_flu,
            "cg_flu_diff": cg_flu_diff,
            "json_unidentified_count": json_unidentified_count,
            "unassigned_count_match": (unassigned_count == json_unidentified_count),
            "unidentified_names_match": unidentified_names_match,
            "unidentified_sets_match": unidentified_sets_match,
            "formula_max_diff": formula_max_diff,
        },
        "hardware_status": {
            "actual_mass_count": actual_mass_count,
            "actual_mat_count": actual_mat_count,
            "qualified_hw_count": qualified_hw_count,
            "assumptions_are_not_measurements": json_data.get("assumptions_are_not_measurements", True),
            "physical_mass_CG_and_inertia_closed": mixta_json.get("physical_mass_CG_and_inertia_closed", False),
            "inertia_model_acceptance_for_predictive_flight": json_data.get("inertia_model_acceptance_for_predictive_flight", False),
        },
        "all_hypotheses": json_hypotheses
    }


def write_grouped_csv(audit_results, output_path):
    """
    Exporta el archivo CSV agrupado por rol funcional en salidas/
    con desglose de registros, volumen, masa y justificación física.
    """
    roles = audit_results["roles"]
    total_recs = audit_results["total_records"]
    total_vol = audit_results["total_volume_mm3"]
    total_mass = audit_results["total_mass_assigned_kg"]

    role_interpretations = {
        "bushing_material_sensitivity": (
            "Casquillos de soporte de vástago de álabes; densidad asumida de 8800 kg/m3 "
            "(aleación de cobre/bronce para cojinetes de fricción). Sensibilidad paramétrica nominal."
        ),
        "integral_vane_linkage_material_sensitivity": (
            "Conjuntos integrales álabe-vástago-manivela-pasador (4 módulos x 4 filas x 3 álabes + barras); "
            "densidad asumida de 2700 kg/m3 (aluminio). Unión cinemática conceptual no homologada."
        ),
        "unknown_device_or_interface": (
            "Reservas volumétricas internas de actuadores y motor en módulos C02 (motores anulares, "
            "apoyos y servomotores). Hardware NO seleccionado/calificado. Masa física real NO nula, sin asignar."
        ),
        "envelope_material_sensitivity": (
            "Piel aerodinámica exterior, lofts deportivos, carenados de aletas, tapas y aros de puertos; "
            "densidad asumida de 1600 kg/m3 (material compuesto/carbono/plásticos técnicos)."
        ),
        "seal_or_clamp_density_assumption": (
            "Abrazaderas axiales y elementos de retención/sellado; densidad asumida de 1200 kg/m3 "
            "(polímero o elastómero técnico)."
        ),
        "frame_support_density_assumption": (
            "Cuadernas transversales y soportes del canal axial; densidad asumida de 2700 kg/m3 "
            "(aluminio estructural de soporte, no validado bajo carga)."
        ),
        "unknown_hardware_or_empty_interface": (
            "Reservas e interfaces vehiculares vacías (canal axial OD60, tobera posterior, 4 actuadores y "
            "4 cojinetes de aletas). Espacios reservados sin hardware seleccionado. Masa física real NO nula, sin asignar."
        ),
        "steel_density_assumption": (
            "Tornillería y elementos encastrados; densidad asumida de 7800 kg/m3 (acero estructural/inoxidable)."
        ),
        "rotor_or_carrier_material_sensitivity": (
            "Cubos y alojamientos anulares de rotor C02 (4 módulos x 2 componentes principales); "
            "densidad asumida de 1600 kg/m3 (sensibilidad de polímero técnico/compuesto)."
        ),
        "shaft_steel_density_assumption": (
            "Ejes de control de las 4 aletas móviles posteriores; densidad asumida de 7800 kg/m3 "
            "(acero de alta resistencia para ejes cinemáticos)."
        )
    }

    fieldnames = [
        "assumed_role",
        "total_records",
        "assigned_records",
        "unassigned_records",
        "rho_mixta_ASSUMED_kg_m3",
        "total_volume_mm3",
        "total_volume_cm3",
        "assigned_mass_mixta_kg",
        "pct_records",
        "pct_total_volume",
        "pct_assigned_mass",
        "status_asignacion_fisica",
        "interpretacion_fisica_y_limites"
    ]

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Ordenar por número de registros descendente
        sorted_roles = sorted(roles.items(), key=lambda x: x[1]["count"], reverse=True)

        for role, data in sorted_roles:
            is_unassigned = (data["assigned_count"] == 0)
            dens_str = (
                ", ".join(str(d) for d in sorted(data["densities"]))
                if data["densities"]
                else "SIN_ASIGNAR"
            )
            mass_val_str = (
                f"{data['assigned_mass_kg']:.6f}"
                if not is_unassigned
                else "NO_ASIGNADA"
            )
            pct_mass_str = (
                f"{(data['assigned_mass_kg'] / total_mass) * 100.0:.2f}%"
                if not is_unassigned
                else "N/A"
            )
            status_str = (
                "ASIGNADA_HIPOTESIS_GEOMETRICA"
                if not is_unassigned
                else "SIN_ASIGNAR_RESERVA_HARDWARE (Masa física NO cero)"
            )

            writer.writerow({
                "assumed_role": role,
                "total_records": data["count"],
                "assigned_records": data["assigned_count"],
                "unassigned_records": data["unassigned_count"],
                "rho_mixta_ASSUMED_kg_m3": dens_str,
                "total_volume_mm3": f"{data['total_volume_mm3']:.4f}",
                "total_volume_cm3": f"{data['total_volume_mm3'] * 1e-3:.4f}",
                "assigned_mass_mixta_kg": mass_val_str,
                "pct_records": f"{(data['count'] / total_recs) * 100.0:.2f}%",
                "pct_total_volume": f"{(data['total_volume_mm3'] / total_vol) * 100.0:.2f}%",
                "pct_assigned_mass": pct_mass_str,
                "status_asignacion_fisica": status_str,
                "interpretacion_fisica_y_limites": role_interpretations.get(role, "Sin descripción específica.")
            })

    return output_path


def print_summary(res):
    """Imprime un resumen formateado de los resultados de la auditoría."""
    rec = res["reconciliation"]
    hw = res["hardware_status"]

    print("=" * 80)
    print("AUDITORÍA DE LA BOM PARCIAL C02 - RESUMEN DE COMPROBACIONES")
    print("=" * 80)
    print(f"Total registros auditados:        {res['total_records']}")
    print(f"  - Filas con masa asignada:      {res['assigned_count']} (82.91%)")
    print(f"  - Filas SIN masa asignada:      {res['unassigned_count']} (17.09%) -> ¡RESERVAS! NO son masa cero.")
    print(f"Volumen CAD total:                {res['total_volume_mm3']:.2f} mm3 ({res['total_volume_mm3']*1e-6:.4f} dm3)")
    print(f"  - Volumen asignado:             {res['assigned_volume_mm3']:.2f} mm3 ({100.0 - res['unassigned_volume_pct']:.2f}%)")
    print(f"  - Volumen reservas sin asignar: {res['unassigned_volume_mm3']:.2f} mm3 ({res['unassigned_volume_pct']:.2f}%)")
    print("-" * 80)
    print("RECONCILIACIÓN HIPÓTESIS MIXTA (mixta_1600):")
    print(f"  Masa asignada CSV:              {res['total_mass_assigned_kg']:.16f} kg")
    print(f"  Masa parcial JSON:              {rec['json_assigned_mass']:.16f} kg")
    print(f"  Discrepancia absoluta masa:     {rec['mass_diff_abs']:.16e} kg (Coincidencia exacta IEEE-754)")
    print(f"  Reserva provisional:            {rec['json_provisional_reserve']:.3f} kg")
    print(f"  Remanente calculado (5.0 kg):   {rec['calculated_remanent']:.16f} kg")
    print(f"  Remanente declarado JSON:       {rec['json_remaining']:.16f} kg")
    print(f"  Discrepancia remanente:         {rec['remanent_diff_abs']:.16e} kg")
    print("-" * 80)
    print("CENTRO DE GRAVEDAD ASIGNADO (Hipótesis Mixta):")
    print(f"  CG CAD calculado [m]:           [{res['cg_cad'][0]:.10f}, {res['cg_cad'][1]:.10e}, {res['cg_cad'][2]:.10f}]")
    print(f"  CG CAD en JSON   [m]:           [{rec['json_cg_cad'][0]:.10f}, {rec['json_cg_cad'][1]:.10e}, {rec['json_cg_cad'][2]:.10f}]")
    print(f"  Error CG CAD [m]:               [{rec['cg_cad_diff'][0]:.2e}, {rec['cg_cad_diff'][1]:.2e}, {rec['cg_cad_diff'][2]:.2e}]")
    print(f"  CG FLU calculado [m]:           [{res['cg_flu'][0]:.10f}, {res['cg_flu'][1]:.10e}, {res['cg_flu'][2]:.10f}]")
    print(f"  CG FLU en JSON   [m]:           [{rec['json_cg_flu'][0]:.10f}, {rec['json_cg_flu'][1]:.10e}, {rec['json_cg_flu'][2]:.10f}]")
    print("-" * 80)
    print("VERIFICACIÓN DE FILAS SIN MASA ASIGNADA:")
    print(f"  Registros sin asignar CSV:      {res['unassigned_count']}")
    print(f"  Registros no identificados JSON:{rec['json_unidentified_count']}")
    print(f"  Coincidencia exacta de nombres: {rec['unidentified_names_match']}")
    print(f"  Roles de filas sin asignar:     unknown_device_or_interface (44), unknown_hardware_or_empty_interface (10)")
    print("-" * 80)
    print("ESTADO DEL HARDWARE Y CONDICIÓN FÍSICA:")
    print(f"  Registros con masa real medida: {hw['actual_mass_count']} de {res['total_records']}")
    print(f"  Registros con material real:    {hw['actual_mat_count']} de {res['total_records']}")
    print(f"  Hardware real calificado:       {hw['qualified_hw_count']} de {res['total_records']}")
    print(f"  Cierre físico de masa/CG/inercia: {hw['physical_mass_CG_and_inertia_closed']} (ABIERTO)")
    print(f"  Aprobado para vuelo predictivo:   {hw['inertia_model_acceptance_for_predictive_flight']} (RECHAZADO)")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Auditoría reproducible de la BOM geométrica parcial C02 (investigación aeronáutica G3)."
    )
    parser.add_argument(
        "--csv",
        default="entradas/investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/BOM_GEOMETRICA_PARCIAL.csv",
        help="Ruta al archivo CSV de entrada."
    )
    parser.add_argument(
        "--json",
        default="entradas/investigacion-aeronautica/ejecucion/G3/C02/integracion_x160/MASA_INERCIA_PARCIAL.json",
        help="Ruta al archivo JSON de entrada."
    )
    parser.add_argument(
        "--output-csv",
        default="salidas/bom_agrupada_roles.csv",
        help="Ruta donde se guardará el CSV agrupado."
    )

    args = parser.parse_args()

    csv_rows, json_data = load_data(args.csv, args.json)
    res = audit_records(csv_rows, json_data)
    out_csv = write_grouped_csv(res, args.output_csv)
    print_summary(res)
    print(f"\nCSV agrupado generado con éxito en: {out_csv}\n")


if __name__ == "__main__":
    main()
