"""Audit immutable C02 field snapshots while leaving the source solver alone."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np

from localizar_picos import mesh_geometry, read_internal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', type=Path, required=True)
    args = parser.parse_args()
    case = args.snapshot.resolve()
    record = json.loads((case/'INSTANTANEA_GUARDADA.json').read_text())
    assert record['stage'] == 'saved_fields_snapshot'
    first, last = map(str, record['saved_counters'])
    assert record['source_completed_counter_observed'] > float(last)
    for name, digest in record['saved_fields_sha256'].items():
        assert hashlib.sha256((case/name).read_bytes()).hexdigest() == digest
    mesh = json.loads((case/'MALLA.json').read_text())
    centres, volumes = mesh_geometry(case/'constant/polyMesh', mesh['cells'])
    np.testing.assert_allclose(volumes.sum(), mesh['mesh_volume_m3'], rtol=1e-8)
    changes, ranges = {}, {}
    for name, components, units in [('U', 3, 'm/s'), ('p', 1, 'm2/s2 kinematic pressure'),
                                    ('k', 1, 'm2/s2'), ('omega', 1, '1/s'), ('nut', 1, 'm2/s')]:
        a = read_internal(case/first/name, mesh['cells'], components)
        b = read_internal(case/last/name, mesh['cells'], components)
        assert np.isfinite(a).all() and np.isfinite(b).all()
        if name in ('k', 'omega', 'nut'):
            assert a.min() >= 0 and b.min() >= 0
        delta = np.linalg.norm(b-a, axis=1) if components == 3 else abs(b-a)
        magnitude = np.linalg.norm(b, axis=1) if components == 3 else b
        at = int(np.argmax(delta))
        changes[name] = dict(units=units, max_abs=float(delta.max()),
            arithmetic_RMS=float(np.sqrt(np.mean(delta**2))),
            volume_weighted_RMS=float(np.sqrt(np.sum(delta**2*volumes)/volumes.sum())),
            largest_change_cell=at, largest_change_centre_m=centres[at].tolist(),
            largest_change_cell_volume_m3=float(volumes[at]),
            first_value_at_largest_change=np.asarray(a[at]).tolist(),
            last_value_at_largest_change=np.asarray(b[at]).tolist())
        if name == 'U':
            changes[name]['volume_fraction_deltaU_gt_1_m_s'] = float(volumes[delta > 1].sum()/volumes.sum())
            changes[name]['volume_fraction_deltaU_gt_0p1_m_s'] = float(volumes[delta > .1].sum()/volumes.sum())
        ranges[name] = [float(magnitude.min()), float(magnitude.max())]
    report = dict(scope='Saved passive-duct fields only; no terminal convergence, physical elapsed time or installed thrust/power claim',
        saved_counters=record['saved_counters'], source_completed_counter_observed=record['source_completed_counter_observed'],
        field_sha256_checks_passed=True, mesh_volume_m3=float(volumes.sum()),
        tetrahedral_topology_orientation_normal_closure_and_volume_verified=True,
        all_fields_finite=True, turbulence_nonnegative=True, ranges_at_last_counter=ranges,
        field_changes=changes, physical_loads_accepted=False,
        source_mesh_sha256={name:hashlib.sha256((case/'constant/polyMesh'/name).read_bytes()).hexdigest()
                           for name in ('points', 'faces', 'owner', 'neighbour')},
        snapshot_record_sha256=hashlib.sha256((case/'INSTANTANEA_GUARDADA.json').read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (case/'AUDITORIA_INSTANTANEA.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(changes_U=changes['U'], max_speed_m_s=ranges['U'][1],
        pressure_is_kinematic=True, physical_loads_accepted=False), indent=2))


if __name__ == '__main__':
    main()
