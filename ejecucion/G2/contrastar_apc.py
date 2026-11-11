"""Compare vendor simulation with independent UIUC tunnel data, without fitting.

This checks a published rotor reference, not our installed fan or our own solver.
"""
from pathlib import Path
import csv
import hashlib
import json
import re

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "benchmark_apc"


def main():
    measured = np.loadtxt(DATA / "apce_10x5_static_pg0819.txt", skiprows=1)
    geometry = np.loadtxt(DATA / "apce_10x5_geom.txt", skiprows=1)
    text = (DATA / "PER3_10x5E.dat").read_text()
    static = []
    for part in text.split("PROP RPM =")[1:]:
        rpm = float(part.splitlines()[0])
        for line in part.splitlines()[1:]:
            try:
                v = [float(x) for x in line.split()]
            except ValueError:
                continue
            if len(v) == 15 and v[0] == 0 and v[1] == 0:
                static.append([rpm, v[3], v[4]])
                break
    static = np.asarray(static)
    assert measured.shape == (16, 3) and geometry.shape == (18, 3)
    assert np.all(np.diff(measured[:, 0]) > 0) and np.all(measured[:, 1:] > 0)
    assert static.shape[0] > 3 and static[0, 0] <= measured[0, 0] and static[-1, 0] >= measured[-1, 0]
    rows = []
    for rpm, ct, cp in measured:
        ct_model = float(np.interp(rpm, static[:, 0], static[:, 1]))
        cp_model = float(np.interp(rpm, static[:, 0], static[:, 2]))
        # Conversion to SI is a recalculation at the declared reference density.
        # It is not raw thrust/torque measured at recorded tunnel ambient conditions.
        rho, diameter_m, n = 1.225, 0.254, rpm/60
        thrust = rho*n*n*diameter_m**4*ct
        shaft = rho*n**3*diameter_m**5*cp
        fom = np.sqrt(2/np.pi) * ct**1.5/cp
        ideal = thrust**1.5/np.sqrt(2*rho*np.pi*diameter_m**2/4)
        assert np.isclose(ideal/shaft, fom) and 0 < fom < 1
        rows.append(dict(rpm=rpm, CT_measured=ct, CP_measured=cp,
                         CT_vendor_model=ct_model, CP_vendor_model=cp_model,
                         relative_CT_error=(ct_model-ct)/ct,
                         relative_CP_error=(cp_model-cp)/cp,
                         recalculated_T_N_at_rho_1_225=thrust,
                         recalculated_shaft_W_at_rho_1_225=shaft,
                         free_propeller_FM_from_measured_coefficients=fom))
    with (DATA / "COMPARACION.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = {
        "status": "published_model_vs_experiment_compared_no_fit",
        "own_rotor_solver_validated": False,
        "data_sources": {
            "geometry": "https://m-selig.ae.illinois.edu/props/volume-1/data/apce_10x5_geom.txt",
            "static_experiment": "https://m-selig.ae.illinois.edu/props/volume-1/data/apce_10x5_static_pg0819.txt",
            "vendor_simulation": "https://www.apcprop.com/files/PER3_10x5E.dat",
            "methodology": "https://m-selig.ae.illinois.edu/props/volume-1/propDB-volume-1.html",
            "vendor_model_status": "https://www.apcprop.com/technical-information/performance-data/",
        },
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (DATA / "apce_10x5_geom.txt", DATA / "apce_10x5_static_pg0819.txt", DATA / "PER3_10x5E.dat")},
        "model_header": text.split("PROP RPM")[0].strip(),
        "static_samples": len(rows), "rpm_interval": [float(measured[0, 0]), float(measured[-1, 0])],
        "CT_measured_interval": [float(measured[:, 1].min()), float(measured[:, 1].max())],
        "CP_measured_interval": [float(measured[:, 2].min()), float(measured[:, 2].max())],
        "c75_m_approx": float(np.interp(.75, geometry[:, 0], geometry[:, 1])*.127),
        "Re75_reference_interval": [float(.75*np.pi*r/60*.254*(np.interp(.75, geometry[:, 0], geometry[:, 1])*.127)/1.46e-5) for r in measured[[0, -1], 0]],
        "Mach_tip_reference_interval": [float(np.pi*r/60*.254/340.3) for r in measured[[0, -1], 0]],
        "comparison": {key: {"min": min(r[key] for r in rows), "max": max(r[key] for r in rows), "mean_absolute": float(np.mean([abs(r[key]) for r in rows]))} for key in ("relative_CT_error", "relative_CP_error")},
        "limitations": [
            "UIUC geometry is approximate digitization of an off-the-shelf historical specimen; no exact airfoil/camber/sweep/thickness surface recovered.",
            "Vendor file is a computational 2022 prediction, not a second wind-tunnel experiment; revision identity with historical specimen is not established.",
            "Coefficient comparison is linear interpolation in RPM with no extrapolation or parameter fitting.",
            "Measured free two-blade rotor data do not transfer to a high-solidity ducted rotor or vectoring vanes.",
            "Vendor geometry archive download returned HTTP403; no complete 3D reproduction claimed.",
        ],
    }
    (DATA / "CONTRASTE.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("static_samples", "rpm_interval", "comparison", "Re75_reference_interval", "Mach_tip_reference_interval")}, indent=2))


if __name__ == "__main__":
    main()
