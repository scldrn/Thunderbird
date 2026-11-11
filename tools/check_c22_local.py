#!/usr/bin/env python3
"""Reproduce C22's recorded local-node screening in an isolated directory."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent
CAD = ROOT / "modelos_integrados"
INPUTS = {
    "producto_C22_nudos": ("cribar.py",),
    "producto_C13_ejes_cinematicos": ("cribar.py", "RESULTADOS.json"),
    "producto_C17_vastagos_radiales": ("C17_candidata_local.step", "AUDITORIA.json"),
}
FIELDS = ("leaf", "bearing", "radius_mm", "passes", "error", "first_collision", "checks")


def main():
    recorded = json.loads((CAD / "producto_C22_nudos/RESULTADOS.json").read_text())
    with tempfile.TemporaryDirectory(prefix="thunderbird-c22-") as name:
        scratch = Path(name)
        for area, files in INPUTS.items():
            (scratch / area).mkdir()
            for file in files:
                shutil.copy2(CAD / area / file, scratch / area / file)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["OPENBLAS_NUM_THREADS"] = "1"
        subprocess.run(
            [sys.executable, str(scratch / "producto_C22_nudos/cribar.py")],
            env=env, check=True,
        )
        actual = json.loads((scratch / "producto_C22_nudos/RESULTADOS.json").read_text())
    old, new = recorded["cases"], actual["cases"]
    if len(old) != 6 or len(new) != len(old):
        raise ValueError("Unexpected C22 case count")
    for expected, observed in zip(old, new):
        if any(expected[field] != observed[field] for field in FIELDS):
            raise ValueError(f"C22 case does not match recorded outcome: {expected}")
        if abs(expected["intentional_stem_overlap_mm3"] - observed["intentional_stem_overlap_mm3"]) >= 1e-7:
            raise ValueError("C22 overlap differs by at least 1e-7 mm³")
    print("Six recorded local C22 cases reproduced; not a mechanism validation.")


if __name__ == "__main__":
    main()
