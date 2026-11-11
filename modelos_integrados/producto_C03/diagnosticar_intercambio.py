"""Investigate STEP/FCStd labels and volume deltas without changing either file."""

from pathlib import Path
import json
import re

import FreeCAD as App
import Import
import Part


HERE = Path(__file__).resolve().parent


def canonical(label):
    match = re.fullmatch(r"(carroceria_C02_(?:superior|inferior))\d*", label)
    return match.group(1) if match else label


def dictionary(items):
    out = {}
    for obj in items:
        key = canonical(obj.Label)
        if key in out:
            raise ValueError(f"Nonunique canonical label: {key}")
        out[key] = obj
    return out


def max_sample_vertex_distance(source, target, limit=40):
    vertices = source.Vertexes
    if not vertices:
        return None
    stride = max(1, len(vertices) // limit)
    samples = vertices[::stride][:limit]
    distances = [vertex.distToShape(target)[0] for vertex in samples]
    return {"sample_count": len(samples), "max_mm": max(distances)}


def center_of_shape(shape):
    """Use mass-weighted solid centroids for imported compound skin panels."""
    solids = shape.Solids
    total = sum(s.Volume for s in solids)
    if total <= 0:
        raise ValueError("Shape has no positive-volume solids")
    moment = App.Vector(0, 0, 0)
    for solid in solids:
        moment += solid.CenterOfMass * solid.Volume
    return moment * (1.0 / total)


step = HERE / "5kg/C03_5kg_cerrado.step"
native = HERE / "5kg/C03_5kg_cerrado.FCStd"
step_doc = App.newDocument("IntercambioSTEP")
Import.insert(str(step), step_doc.Name)
step_doc.recompute()
roots = [o for o in step_doc.Objects if o.TypeId == "App::Part" and not o.InList]
if len(roots) != 1:
    raise ValueError("Unexpected STEP root")
step_parts = dictionary(roots[0].Group)
native_doc = App.openDocument(str(native))
native_parts = dictionary(o for o in native_doc.Objects if o.Name.startswith("pieza_"))
if set(step_parts) != set(native_parts):
    raise ValueError(f"Missing mapping: STEP={sorted(set(step_parts)-set(native_parts))}; native={sorted(set(native_parts)-set(step_parts))}")

rows = []
for name in sorted(step_parts):
    s = step_parts[name].Shape
    n = native_parts[name].Shape
    rows.append({"part": name, "step_label": step_parts[name].Label,
                 "native_label": native_parts[name].Label,
                 "step_volume_mm3": s.Volume, "native_volume_mm3": n.Volume,
                 "absolute_volume_difference_mm3": abs(s.Volume - n.Volume),
                 "relative_volume_difference": abs(s.Volume - n.Volume) / max(abs(n.Volume), 1e-12),
                 "center_difference_mm": (center_of_shape(s) - center_of_shape(n)).Length,
                 "step_faces": len(s.Faces), "native_faces": len(n.Faces),
                 "step_solids": len(s.Solids), "native_solids": len(n.Solids)})
rows.sort(key=lambda r: -r["relative_volume_difference"])
(HERE / "DIAGNOSTICO_INTERCAMBIO_PARCIAL.json").write_text(
    json.dumps({"mapped_records": len(rows), "parts": rows}, indent=2) + "\n")
print("MAPEO_COMPLETO", len(rows), flush=True)
diagnostics = []
for name in ("junta_C02_0_inferior", "aro_C02_0_inferior", "modulo_C02_0_rotor_copa"):
    step_shape = step_parts[name].Shape
    native_shape = native_parts[name].Shape
    record = {"part": name, "step_vertices_to_native": max_sample_vertex_distance(step_shape, native_shape),
              "native_vertices_to_step": max_sample_vertex_distance(native_shape, step_shape)}
    for key, first, second in (("native_minus_step_mm3", native_shape, step_shape),
                               ("step_minus_native_mm3", step_shape, native_shape)):
        try:
            diff = first.cut(second)
            record[key] = diff.Volume
            record[key + "_valid"] = diff.isNull() or diff.isValid()
        except Exception as exc:
            record[key + "_error"] = str(exc)
    diagnostics.append(record)
    print("COMPARADA", name, flush=True)

report = {"scope": "5kg cerrado; canonical label matching and sampled vertices, not continuous Hausdorff nor manufacturing tolerance", "mapped_records": len(rows), "largest_relative_volume_differences": rows[:20], "parts": rows, "selected_geometry_checks": diagnostics}
(HERE / "DIAGNOSTICO_INTERCAMBIO.json").write_text(json.dumps(report, indent=2) + "\n")
App.closeDocument(native_doc.Name)
App.closeDocument(step_doc.Name)
print("DIAGNOSTICO_INTERCAMBIO_COMPLETO", flush=True)
