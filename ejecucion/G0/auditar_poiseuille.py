"""Compare saved OpenFOAM fields with the PDE and semi-discrete solutions.

No solvers are started. Rejected sensitivity results are retained in the report.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

import numpy as np
from scipy.linalg import expm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "CFD"))
from foam_fields import read_internal


def transient(y, time_s, terms=1000):
    k = (np.arange(terms) + 0.5) * np.pi
    steady = 50 * (y - y * y / 2)
    return steady - np.sin(y[:, None] * k) @ (100 / k**3 * np.exp(-0.1 * k*k*time_s))


def main():
    cases = sorted(p for p in HERE.glob("poiseuille_*") if (p / "4/U").is_file())
    rows = []
    for case in cases:
        meta = json.loads((case / "benchmark_inputs.json").read_text())
        n, dt = meta["Ny"], meta["dt_s"]
        control = (case / "system/controlDict").read_text()
        solution = (case / "system/fvSolution").read_text()
        outer = int(re.search(r"nOuterCorrectors\s+(\d+)", solution)[1])
        assert float(re.search(r"deltaT\s+([^;]+)", control)[1]) == dt
        mesh = (case / "system/blockMeshDict").read_text()
        assert re.search(rf"\(1\s+{n}\s+1\)\s+simpleGrading\s+\(1\s+1\s+1\)", mesh)
        # Inspect the mesh that actually ran, not only its requested cell count.
        point_text = (case / "constant/polyMesh/points").read_text()
        points = np.array(re.findall(r"\(\s*([-+.\deE]+)\s+([-+.\deE]+)\s+([-+.\deE]+)\s*\)", point_text), float)
        y_faces = np.unique(points[:, 1])
        assert len(y_faces) == n + 1 and np.allclose(y_faces, np.linspace(0, 1, n+1))
        y = (y_faces[1:] + y_faces[:-1]) / 2
        u = read_internal(case / "4/U", n, 3)
        reference = transient(y, 4)
        assert np.max(np.abs(transient(y, 4, 2000) - reference)) < 1e-12
        # Cell-centred FV diffusion operator: no-slip at y=0, symmetry at y=1.
        lap = np.diag(np.full(n, -2.0)) + np.diag(np.ones(n-1), 1) + np.diag(np.ones(n-1), -1)
        lap[0, 0], lap[-1, -1] = -3, -1
        operator = 0.1 * n*n * lap
        mol = np.linalg.solve(operator, (expm(4*operator) - np.eye(n)) @ np.full(n, 5.0))
        log = (case / "log.foamRun").read_text()
        assert log.rstrip().endswith("End") and "Selecting laminar stress model Stokes" in log
        times = re.findall(r"^Time = ([\d.eE+-]+)s?\s*$", log, re.M)
        assert abs(float(times[-1]) - 4) < 1e-10
        runtime = re.findall(r"ExecutionTime = ([\d.eE+-]+) s\s+ClockTime = ([\d.eE+-]+) s", log)[-1]
        def hashes(paths):
            return {str(p.relative_to(case)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
        inputs = [p for folder in ("0", "constant", "system") for p in (case / folder).rglob("*") if p.is_file() and "polyMesh" not in p.parts]
        record = {
            "case": case.name, "Ny": n, "dt_s": dt, "outer_correctors": outer,
            "steps_in_log": len(times), "final_time_s": float(times[-1]),
            "execution_cpu_s": float(runtime[0]), "clock_s": float(runtime[1]),
            "max_abs_error_m_s": float(np.max(np.abs(u[:, 0]-reference))),
            "relative_Linf_PDE": float(np.max(np.abs(u[:, 0]-reference)) / np.max(reference)),
            "relative_L2_PDE": float(np.linalg.norm(u[:, 0]-reference)/np.linalg.norm(reference)),
            "relative_Linf_MOL": float(np.max(np.abs(u[:, 0]-mol)) / np.max(mol)),
            "max_transverse_velocity_m_s": float(np.max(np.abs(u[:, 1:]))),
            "input_sha256_reconstructed_after_run": hashes(inputs),
            "actual_mesh_sha256": hashes([p for p in (case / "constant/polyMesh").iterdir() if p.is_file()]),
            "result_and_log_sha256": hashes([case / "4/U", case / "log.foamRun", case / "log.blockMesh"]),
        }
        rows.append(record)
        profile = np.column_stack((y, u[:, 0], reference, mol))
        np.savetxt(case / "COMPARACION.csv", profile, delimiter=",", header="y_m,Ux_OpenFOAM_m_s,Ux_PDE_m_s,Ux_MOL_m_s", comments="")
    assert len(rows) == 10, len(rows)
    chosen = next(r for r in rows if r["case"] == "poiseuille_80_outer50_dt_half")
    assert chosen["relative_Linf_PDE"] < 0.0002
    report = {
        "scope": "Numerical verification of one Newtonian channel transient, not installed fan or vehicle validation",
        "reference": {"H_m": 1, "nu_m2_s": 0.1, "G_m_s2": 5, "time_s": 4, "series_terms": 1000},
        "normalization": "Linf error divided by maximum analytic cell-centre velocity; L2 Euclidean ratio",
        "cases": rows,
        "selection_for_app_integration": chosen["case"],
        "decisions": [
            "Two-outer-corrector family rejected for grid convergence: error rises with refinement.",
            "50-corrector cases closely reproduce this endpoint; halving dt reduces MOL error about twofold.",
            "No formal second-order temporal or spatial convergence established; no GCI reported.",
            "Residuals alone do not certify equation/time-discretization accuracy.",
            "Input hashes reconstructed now from retained files; not an immutable pre-run execution attestation.",
            "CPU/wall times are observed for this tiny case, not a vehicle campaign cost forecast.",
        ],
    }
    (HERE / "AUDITORIA-POISEUILLE.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps([{k: r[k] for k in ("case", "relative_Linf_PDE", "relative_Linf_MOL", "max_transverse_velocity_m_s", "execution_cpu_s")} for r in rows], indent=2))


if __name__ == "__main__":
    main()
