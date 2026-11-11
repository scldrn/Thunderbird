"""Tessellate each CAD face separately so panel edges stay crisp in renders."""

from pathlib import Path
import gzip
import hashlib
import json

import FreeCAD as App


HERE = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


for state in ("cerrado", "abierto"):
    native = HERE / "5kg" / f"C03_5kg_{state}.FCStd"
    doc = App.openDocument(str(native))
    objects = [o for o in doc.Objects if o.Name.startswith("pieza_")]
    if len(objects) != 316:
        raise ValueError(f"Unexpected part count: {len(objects)}")
    parts = []
    for obj in objects:
        vertices = []
        triangles = []
        for face in obj.Shape.Faces:
            fv, ft = face.tessellate(0.30)
            offset = len(vertices)
            vertices.extend([[v.x * 0.001, v.y * 0.001, v.z * 0.001] for v in fv])
            triangles.extend([[offset + i for i in tri] for tri in ft])
        parts.append({"name": obj.Label, "vertices_m": vertices, "triangles": triangles})
    out = HERE / "5kg" / f"C03_5kg_{state}_mallas_caras.json.gz"
    data = {"revision": "C03", "state": state, "mass_reference_kg": 5,
            "source_native_sha256": digest(native), "source_step_sha256": "source recorded in MANIFIESTO.json",
            "method": "individual FreeCAD BRep face tessellation at 0.30 mm", "parts": parts}
    with gzip.open(out, "wt", encoding="utf-8") as stream:
        json.dump(data, stream, separators=(",", ":"))
    print("MALLA_CARAS", state, len(parts), sum(len(p["triangles"]) for p in parts), flush=True)
    App.closeDocument(doc.Name)
