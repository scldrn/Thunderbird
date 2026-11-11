"""Reference frames, units and provenance for new configuration consumers.

The CAD origin is a provisional datum, not an identified centre of mass.
Existing historical artifacts remain frozen and are not silently transformed.
"""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def load_baseline(path=None, verify_geometry=False):
    path = Path(path) if path is not None else Path(__file__).with_name('A07_BASE.json')
    data = json.loads(path.read_text())
    R = np.asarray(data['flight_body_frame']['R_flight_from_CAD'], dtype=float)
    if R.shape != (3, 3) or not np.allclose(R @ R.T, np.eye(3)) or not np.isclose(np.linalg.det(R), 1):
        raise ValueError('CAD-to-flight transform must be a proper orthonormal rotation')
    if data['architecture'] != 'A_internal_fans' or data['cad_to_SI_length_factor'] != .001:
        raise ValueError('Unexpected architecture or STEP unit conversion')
    if verify_geometry:
        for variant in data['geometry'].values():
            for record in variant['states'].values():
                geometry = ROOT / record['path']
                if hashlib.sha256(geometry.read_bytes()).hexdigest() != record['sha256']:
                    raise ValueError('Geometry changed: ' + record['path'])
    return data


def vectors_cad_to_flu(vectors, baseline=None):
    data = load_baseline() if baseline is None else baseline
    values = np.asarray(vectors, dtype=float)
    if values.ndim < 1 or values.shape[-1] != 3 or not np.all(np.isfinite(values)):
        raise ValueError('Expected finite (...,3) vectors in common units')
    R = np.asarray(data['flight_body_frame']['R_flight_from_CAD'])
    return values @ R.T


def points_mm_cad_to_flu_m(points, baseline=None):
    data = load_baseline() if baseline is None else baseline
    return vectors_cad_to_flu(points, data) * data['cad_to_SI_length_factor']


def inertia_cad_to_flu(inertia, baseline=None):
    data = load_baseline() if baseline is None else baseline
    tensor = np.asarray(inertia, dtype=float)
    if tensor.shape != (3, 3) or not np.all(np.isfinite(tensor)) or not np.allclose(tensor, tensor.T):
        raise ValueError('Expected finite symmetric inertia tensor in kg m^2')
    if np.linalg.eigvalsh(tensor).min() <= 0:
        raise ValueError('Inertia must be positive definite')
    R = np.asarray(data['flight_body_frame']['R_flight_from_CAD'])
    return R @ tensor @ R.T


def shift_moment_origin(moment_old, resultant_force, origin_old, origin_new):
    """All arguments in the same frame; moments N m, forces N, origins m."""
    values = [np.asarray(v, dtype=float) for v in (moment_old, resultant_force, origin_old, origin_new)]
    if any(v.shape != (3,) or not np.all(np.isfinite(v)) for v in values):
        raise ValueError('Expected finite 3-vectors with common frame and SI units')
    moment, force, old, new = values
    return moment + np.cross(old - new, force)
