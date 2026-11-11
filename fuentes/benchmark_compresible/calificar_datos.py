"""Audit recovered public benchmark inputs; does not run or validate a solver."""
from pathlib import Path
import hashlib
import json
import re

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent


def main():
    data = HERE / "case_2308.dat"
    blocks = re.split(r"(?=^ZONE )", data.read_text(), flags=re.M)[1:]
    sections = []
    eta = [0.2, 0.44, 0.65, 0.8, 0.9, 0.96, 0.99]
    for index, block in enumerate(blocks):
        header, body = block.split("\n", 1)
        expected = int(re.search(r"I=\s*(\d+)", header)[1])
        values = np.array([[float(x) for x in line.split()] for line in body.splitlines() if line.strip()])
        assert values.shape == (expected, 5) and np.isfinite(values).all()
        assert np.all(values[:, 0] == index+1)
        assert np.all((values[:, 2] >= 0) & (values[:, 2] <= 1.01))
        sections.append(dict(section=index+1, eta=eta[index], taps=expected,
                             original_header=header, Cp_range=[float(values[:, 4].min()), float(values[:, 4].max())]))
    assert len(sections) == 7 and sum(s["taps"] for s in sections) == 271
    step = HERE / "AileM6_with_sharp_TE.stp"
    shape = cq.importers.importStep(str(step)).val()
    assert shape.isValid()
    bbox = shape.BoundingBox()
    report = {
        "status": "inputs_recovered_and_parsed_no_solver_run",
        "primary_catalog": "https://tmbwg.github.io/turbmodels/onerawingnumerics_val.html",
        "catalog_migration_authority": "https://www.nasa.gov/nasa-turbulence-modeling-resource/",
        "source_urls": {
            step.name: "https://tmbwg.github.io/turbmodels/Onerawingnumerics_grids/AileM6_with_sharp_TE.stp",
            data.name: "https://tmbwg.github.io/turbmodels/Onerawingnumerics_val/case_2308.dat",
        },
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (step, data)},
        "sections": sections, "pressure_taps": 271,
        "CAD": {"valid": True, "units": "mm", "solids": len(shape.Solids()), "faces": len(shape.Faces()),
                "bbox_mm": {"x": [bbox.xmin, bbox.xmax], "y": [bbox.ymin, bbox.ymax], "z": [bbox.zmin, bbox.zmax]}},
        "proposed_TMR_case": {"Mach": 0.84, "alpha_deg": 3.06, "Re_root_sharp": 14.6e6, "T_K": 300},
        "must_preserve": [
            "Original data header Mach=.8395, Re_MAC=11.72e6; TMR exercise uses .84 and sharp-root Reynolds 14.6e6. Do not mix definitions.",
            "Downloaded geometry has sharp trailing edge; original experiment has finite trailing edge. Declare this geometry discrepancy.",
            "Sixth span station is eta=.96 in current TMR interpretation; not .95.",
            "Available comparison is experimental Cp, not measured total lift/drag/moments.",
            "This wing is a solver benchmark; no direct transfer to A07 or its critical Mach/drag.",
            "Mesh, wall treatment, turbulence model and convergence/cost pilot remain pending.",
        ],
    }
    (HERE / "CALIFICACION.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
