"""Reimport STEP and FCStd and check the C03 conceptual variants.

These checks cover validity, scaling, door endpoints and local rotor/door
clearance. They do not establish mechanism, flight or manufacturing validity.
"""

from pathlib import Path
import hashlib
import json
import math
import traceback

import FreeCAD as App
import Import
import Part


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RULES = ROOT / "ejecucion/G3/C02/integracion_x160/REGLAS_TAPAS_CONCEPTUALES.json"


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def as_list(v):
    return [v.x, v.y, v.z]


def match_prefix(parts, prefix):
    matches = [(name, obj) for name, obj in parts.items() if name.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f"Expected one {prefix}, got {[n for n, _ in matches]}")
    return matches[0][1]


def main():
    manifest = json.loads((HERE / "MANIFIESTO.json").read_text())
    rules = json.loads(RULES.read_text())
    errors = []
    results = []
    closed = {}
    for entry in manifest["variants"]:
        mass = entry["mass_target_kg"]
        state = entry["state"]
        factor = entry["scale_from_5kg"]
        stem = f"C03_{mass}kg_{state}"
        print("AUDIT_INICIO", stem, flush=True)
        step = HERE / entry["step_file"]
        native = HERE / entry["native_file"]
        if file_hash(step) != entry["step_sha256"] or file_hash(native) != entry["native_sha256"]:
            errors.append(f"{stem}: hash mismatch")
        doc = App.newDocument("Check_" + stem)
        Import.insert(str(step), doc.Name)
        doc.recompute()
        print("AUDIT_STEP_IMPORTADO", stem, flush=True)
        roots = [o for o in doc.Objects if o.TypeId == "App::Part" and not o.InList]
        if len(roots) != 1:
            raise ValueError(f"{stem}: unexpected STEP roots {len(roots)}")
        children = roots[0].Group
        parts = {obj.Label: obj for obj in children}
        if len(children) != 316 or len(parts) != 316:
            errors.append(f"{stem}: unexpected named records {len(children)}/{len(parts)}")
        invalid = [o.Label for o in children if o.Shape.isNull() or not o.Shape.isValid() or o.Shape.Volume <= 0]
        if invalid:
            errors.append(f"{stem}: invalid shapes {invalid}")
        rotor_records = {}
        for i in range(4):
            rotor = match_prefix(parts, f"modulo_C02_{i}_rotor_copa")
            rotor_records[str(i)] = {"center_mm": as_list(rotor.Shape.CenterOfMass), "volume_mm3": rotor.Shape.Volume}
        door_records = {}
        local_intersections = []
        for rule in rules:
            door = match_prefix(parts, rule["name"])
            center = door.Shape.CenterOfMass
            door_records[rule["name"]] = {"center_mm": as_list(center), "volume_mm3": door.Shape.Volume}
            index = rule["name"].split("_")[2]
            rotor = match_prefix(parts, f"modulo_C02_{index}_rotor_copa")
            overlap = door.Shape.common(rotor.Shape).Volume
            local_intersections.append({"door": rule["name"], "rotor": index, "overlap_mm3": overlap})
            if overlap > 1e-3:
                errors.append(f"{stem}: door {rule['name']} overlaps rotor by {overlap}")
        print("AUDIT_GEOMETRIA_LOCAL", stem, flush=True)
        position_errors = {}
        rotor_motion_errors = {}
        if state == "cerrado":
            closed[mass] = {"doors": door_records, "rotors": rotor_records}
        else:
            prev = closed[mass]
            for rule in rules:
                base = App.Vector(*prev["doors"][rule["name"]]["center_mm"])
                lift = rule["lift_mm"] * factor
                moved = base + App.Vector(0, 0, rule["out"] * lift)
                axis = App.Vector(*(coordinate * factor for coordinate in rule["axis_closed"]))
                axis.z += rule["out"] * lift
                expected = axis + App.Rotation(App.Vector(1, 0, 0), rule["sign"] * rule["angle_deg"]).multVec(moved - axis)
                actual = App.Vector(*door_records[rule["name"]]["center_mm"])
                delta = (actual - expected).Length
                position_errors[rule["name"]] = delta
                if delta > 1e-4:
                    errors.append(f"{stem}: wrong door center {rule['name']}: {delta} mm")
            for i in range(4):
                before = App.Vector(*prev["rotors"][str(i)]["center_mm"])
                after = App.Vector(*rotor_records[str(i)]["center_mm"])
                delta = (after - before).Length
                rotor_motion_errors[str(i)] = delta
                if delta > 1e-5:
                    errors.append(f"{stem}: rotor {i} moved {delta} mm")

        native_doc = App.openDocument(str(native))
        print("AUDIT_NATIVE_ABIERTO", stem, flush=True)
        native_parts = {o.Label: o for o in native_doc.Objects if o.Name.startswith("pieza_")}
        if len(native_parts) != 316:
            errors.append(f"{stem}: native document has {len(native_parts)} pieces")
        missing_native = sorted(set(parts) - set(native_parts))
        if missing_native:
            errors.append(f"{stem}: labels absent in native document {missing_native[:10]}")
        compare = []
        for name in sorted(set(parts) & set(native_parts)):
            a, b = parts[name].Shape.Volume, native_parts[name].Shape.Volume
            rel = abs(a - b) / max(abs(b), 1e-12)
            if rel > 2e-5:
                compare.append({"part": name, "relative_volume_error": rel})
        if compare:
            errors.append(f"{stem}: STEP/FCStd volume differences {compare[:5]}")
        App.closeDocument(native_doc.Name)
        results.append({"variant": stem, "step_records": len(children), "native_records": len(native_parts),
                        "invalid_shapes": invalid, "doors": door_records, "rotors": rotor_records,
                        "door_rotor_intersections": local_intersections,
                        "door_center_error_mm": position_errors,
                        "rotor_center_motion_mm": rotor_motion_errors,
                        "step_native_volume_differences": compare})
        (HERE / "AUDITORIA_PARCIAL.json").write_text(json.dumps({"variants": results, "errors": errors}, indent=2) + "\n")
        App.closeDocument(doc.Name)
        print("AUDITADA", stem, "invalidas", len(invalid), flush=True)

    # Independent similarity check on all four rotor centres and eight doors.
    similarity_errors = []
    factor = (10.0 / 5.0) ** (1.0 / 3.0)
    for kind in ("doors", "rotors"):
        for name, v5 in closed[5][kind].items():
            v10 = closed[10][kind][name]
            position_error = (App.Vector(*v10["center_mm"]) - App.Vector(*v5["center_mm"]) * factor).Length
            volume_error = abs(v10["volume_mm3"] / v5["volume_mm3"] - 2.0)
            if position_error > 1e-4 or volume_error > 2e-5:
                similarity_errors.append({"name": name, "position_mm": position_error, "volume_ratio_error": volume_error})
    if similarity_errors:
        errors.append(f"10kg similarity mismatch: {similarity_errors}")
    report = {"revision": "C03", "scope": "STEP reimport, FreeCAD reopen, part validity, door endpoints, door/rotor local checks, geometric scaling; no continuous clearance, loads, structural or flight validation", "variants": results, "similarity_errors": similarity_errors, "errors": errors}
    (HERE / "AUDITORIA.json").write_text(json.dumps(report, indent=2) + "\n")
    print("AUDITORIA_COMPLETA", "errores", len(errors), flush=True)
    if errors:
        raise RuntimeError("C03 audit found failures; see AUDITORIA.json")


try:
    main()
except Exception:
    failure = traceback.format_exc()
    (HERE / "AUDITORIA_ERROR.log").write_text(failure)
    print(failure, flush=True)
    raise
