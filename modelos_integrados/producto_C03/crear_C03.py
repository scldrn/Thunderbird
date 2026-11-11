"""Create C03 conceptual FreeCAD/STEP assemblies from the C02 candidate.

Run with the FreeCAD command-line executable. All dimensions are millimetres.
This reuses the C02 solids and its conceptual door poses; no hardware, material,
installed-force map or vehicle mass is selected by this generator.
"""

from pathlib import Path
import gzip
import hashlib
import json
import math

import FreeCAD as App
import Import
import Part


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE = ROOT / "ejecucion/G3/C02/integracion_x160"
SOURCE = BASE / "C02_integracion_x160_5kg_cerrado_CANDIDATA.step"
RULES = BASE / "REGLAS_TAPAS_CONCEPTUALES.json"
EXPECTED_SOURCE_SHA256 = "c587381e42e5eba78454f9bc263a9db51b75114875ab281eaa4fbb33666b439e"
MESH_TOLERANCE_MM = 0.30


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def motion(shape, rule):
    """Apply the previously documented lift and rotation to one door."""
    result = shape.copy()
    lift = float(rule["lift_mm"])
    direction = float(rule["out"])
    axis = list(rule["axis_closed"])
    axis[2] += direction * lift
    result.translate(App.Vector(0, 0, direction * lift))
    result.rotate(App.Vector(*axis), App.Vector(1, 0, 0),
                  float(rule["sign"]) * float(rule["angle_deg"]))
    return result


def bounds_of_vertices(vertices):
    if not vertices:
        return None
    return [[min(getattr(v, a) for v in vertices),
             max(getattr(v, a) for v in vertices)] for a in ("x", "y", "z")]


def make_display_record(name, shape):
    vertices, triangles = shape.tessellate(MESH_TOLERANCE_MM)
    return {
        "name": name,
        "vertices_m": [[v.x * 0.001, v.y * 0.001, v.z * 0.001] for v in vertices],
        "triangles": [list(t) for t in triangles],
    }


def metadata(doc, mass_kg, factor, state, source_hash):
    note = doc.addObject("App::FeaturePython", "Alcance_conceptual")
    for name, value in (
        ("Revision", "C03"),
        ("Estado", state),
        ("MasaObjetivo", f"{mass_kg} kg; masa real sin cerrar"),
        ("Escalado", f"{factor:.12f} respecto a C02 de 5 kg"),
        ("ReferenciaSTEP_SHA256", source_hash),
        ("Alcance", "Candidato conceptual; solidos importados, sin historial de fabricacion."),
        ("Propulsion", "Cuatro rotores interiores; motores y mapas instalados no seleccionados."),
        ("Compuertas", "Poses geometricas; guias, bisagras y accionamientos no definidos."),
    ):
        note.addProperty("App::PropertyString", name, "Proyecto")
        setattr(note, name, value)
    note.addProperty("App::PropertyBool", "PrestacionesValidadas", "Proyecto")
    note.PrestacionesValidadas = False


def main():
    source_hash = sha256(SOURCE)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError("La huella del STEP C02 no coincide con la referencia documentada")
    rules = {rule["name"]: rule for rule in json.loads(RULES.read_text())}
    if len(rules) != 8:
        raise ValueError("Se esperaban ocho reglas de compuertas")

    source_doc = App.newDocument("C02_fuente")
    Import.insert(str(SOURCE), source_doc.Name)
    source_doc.recompute()
    roots = [o for o in source_doc.Objects if o.TypeId == "App::Part" and not o.InList]
    if len(roots) != 1 or len(roots[0].Group) != 316:
        raise ValueError("Jerarquia de referencia inesperada")
    source_parts = []
    for obj in roots[0].Group:
        if obj.Placement.Base.Length > 1e-9 or abs(obj.Placement.Rotation.Angle) > 1e-9:
            raise ValueError(f"Posicion local inesperada: {obj.Label}")
        shape = obj.Shape.copy()
        if shape.isNull() or not shape.isValid() or shape.Volume <= 0:
            raise ValueError(f"Pieza fuente invalida: {obj.Label}")
        source_parts.append((obj.Label, shape))
    names = {name for name, _ in source_parts}
    if not set(rules).issubset(names):
        raise ValueError("No se encuentran las ocho compuertas")
    if any(f"modulo_C02_{i}_rotor_copa" not in names for i in range(4)):
        raise ValueError("No se encuentran los cuatro rotores interiores")

    manifest = {
        "revision": "C03_concepto",
        "units_cad": "mm",
        "source_step": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "door_rules": str(RULES.relative_to(ROOT)),
        "architecture": "four internal fixed rotors, eight conceptual doors",
        "validated_performance": False,
        "manufacturing_release": False,
        "ten_kg_is_geometric_scale_only": True,
        "parts_per_variant": len(source_parts),
        "mesh_tolerance_mm": MESH_TOLERANCE_MM,
        "variants": [],
    }
    for mass_kg in (5, 10):
        factor = (mass_kg / 5.0) ** (1.0 / 3.0)
        for state in ("cerrado", "abierto"):
            destination = HERE / f"{mass_kg}kg"
            destination.mkdir(parents=True, exist_ok=True)
            stem = f"C03_{mass_kg}kg_{state}"
            doc = App.newDocument(stem)
            group = doc.addObject("App::Part", "Conjunto_C03")
            group.Label = stem
            shown = []
            invalid = []
            scale_errors = []
            door_displacements = {}
            for index, (name, original) in enumerate(source_parts):
                shape = motion(original, rules[name]) if state == "abierto" and name in rules else original.copy()
                if name in rules and state == "abierto":
                    door_displacements[name] = (shape.CenterOfMass - original.CenterOfMass).Length * factor
                if factor != 1:
                    shape.scale(factor, App.Vector(0, 0, 0))
                if shape.isNull() or not shape.isValid() or shape.Volume <= 0:
                    invalid.append(name)
                expected = original.Volume * factor ** 3
                if abs(shape.Volume - expected) > max(1e-5, abs(expected) * 2e-6):
                    scale_errors.append(name)
                obj = doc.addObject("Part::Feature", f"pieza_{index:03d}")
                obj.Label = name
                obj.Shape = shape
                group.addObject(obj)
                if mass_kg == 5:
                    shown.append(make_display_record(name, shape))
            if invalid or scale_errors:
                raise ValueError(f"{stem}: invalid={invalid}, scale_errors={scale_errors}")
            if state == "abierto" and (len(door_displacements) != 8 or min(door_displacements.values()) <= 1):
                raise ValueError(f"No se desplazan todas las compuertas en {stem}")
            metadata(doc, mass_kg, factor, state, source_hash)
            doc.recompute()
            native = destination / f"{stem}.FCStd"
            step = destination / f"{stem}.step"
            doc.saveAs(str(native))
            Import.export([group], str(step))
            print(f"EXPORTADO {stem} piezas={len(source_parts)}", flush=True)

            # Only the 5 kg meshes are stored; the comparative 10 kg render
            # applies the same similarity factor used for its CAD solids.
            display = None
            mesh_bounds = None
            if mass_kg == 5:
                vertices = [v for part in shown for v in part["vertices_m"]]
                mesh_bounds = [[min(v[i] for v in vertices), max(v[i] for v in vertices)] for i in range(3)]
                display = destination / f"{stem}_mallas.json.gz"
                with gzip.open(display, "wt", encoding="utf-8") as stream:
                    json.dump({"revision": "C03", "state": state, "mass_reference_kg": mass_kg,
                               "source_step_sha256": source_hash, "parts": shown}, stream,
                              separators=(",", ":"))
            entry = {
                "mass_target_kg": mass_kg, "state": state, "scale_from_5kg": factor,
                "native_file": str(native.relative_to(HERE)), "native_sha256": sha256(native),
                "step_file": str(step.relative_to(HERE)), "step_sha256": sha256(step),
                "records_created": len(source_parts), "invalid_shapes": invalid,
                "scale_volume_errors": scale_errors,
                "door_center_displacements_mm": door_displacements,
                "display_mesh": str(display.relative_to(HERE)) if display else None,
                "mesh_bounds_m": mesh_bounds,
            }
            manifest["variants"].append(entry)
            (HERE / "MANIFIESTO.json").write_text(json.dumps(manifest, indent=2) + "\n")
            App.closeDocument(doc.Name)
    App.closeDocument(source_doc.Name)
    print("C03_GENERACION_COMPLETA", flush=True)


main()
