"""Create one checked delivery archive per C03 geometric variant."""

from pathlib import Path
import hashlib
import json
import zipfile


HERE = Path(__file__).resolve().parent


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


manifest = json.loads((HERE / "MANIFIESTO.json").read_text())
for variant in manifest["variants"]:
    for kind in ("native", "step"):
        path = HERE / variant[kind + "_file"]
        if sha256(path) != variant[kind + "_sha256"]:
            raise ValueError(f"CAD hash mismatch: {path}")

common = ["LEEME.md", "MANIFIESTO.json", "AUDITORIA.json", "DIAGNOSTICO_INTERCAMBIO.json",
          "crear_C03.py", "auditar_C03.py", "diagnosticar_intercambio.py",
          "regenerar_mallas_C03.py", "render_C03.py"]
archive_entries = []
for mass in (5, 10):
    files = common + [f"{mass}kg/C03_{mass}kg_{state}.{suffix}"
                      for state in ("cerrado", "abierto") for suffix in ("FCStd", "step", "png")]
    files.append(f"{mass}kg/C03_{mass}kg_interior.png")
    dest = HERE / f"C03_{mass}kg_kit_CAD.zip"
    temp = HERE / f"C03_{mass}kg_kit_CAD.zip.tmp"
    with zipfile.ZipFile(temp, "w", allowZip64=True) as archive:
        for relative in files:
            path = HERE / relative
            if not path.is_file():
                raise FileNotFoundError(path)
            compressed = zipfile.ZIP_STORED if path.suffix.lower() in (".fcstd", ".png") else zipfile.ZIP_DEFLATED
            archive.write(path, arcname=f"C03_{mass}kg/{relative}", compress_type=compressed, compresslevel=4)
    with zipfile.ZipFile(temp) as archive:
        failed = archive.testzip()
        if failed:
            raise ValueError(f"Archive failed CRC check: {failed}")
    temp.replace(dest)
    archive_entries.append({"mass_target_kg": mass, "file": dest.name, "sha256": sha256(dest),
                            "size_bytes": dest.stat().st_size, "entries": len(files)})
    print("KIT_VERIFICADO", mass, dest.stat().st_size, flush=True)

out = {"revision": "C03", "status": "conceptual", "archives": archive_entries,
       "audit": "AUDITORIA.json preserves STEP/FCStd volume discrepancies; see LEEME.md",
       "ten_kg_is_geometric_scale_only": True,
       "antigravity_review_task": "2840c029; independent recommendations, not physical validation"}
(HERE / "ENTREGA.json").write_text(json.dumps(out, indent=2) + "\n")
