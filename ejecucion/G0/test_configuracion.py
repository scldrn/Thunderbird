"""Analytic frame/unit checks, not validation of the aircraft."""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from configuraciones.base import load_baseline, vectors_cad_to_flu, points_mm_cad_to_flu_m, inertia_cad_to_flu, shift_moment_origin


class ConfigurationTests(unittest.TestCase):
    def test_current_geometry_fingerprints(self):
        self.assertEqual(load_baseline(verify_geometry=True)['architecture'], 'A_internal_fans')

    def test_nose_is_forward_and_mm_becomes_m(self):
        np.testing.assert_allclose(points_mm_cad_to_flu_m([-680, 0, 0]), [.680, 0, 0])

    def test_power_and_cross_product_are_frame_invariant(self):
        force = np.array([3., -2., 7.]); velocity = np.array([1., 4., -2.]); arm = np.array([.2, .076, -.039])
        transform = vectors_cad_to_flu
        self.assertAlmostEqual(force @ velocity, transform(force) @ transform(velocity))
        np.testing.assert_allclose(transform(np.cross(arm, force)), np.cross(transform(arm), transform(force)))

    def test_rotational_energy_preserved(self):
        inertia = np.array([[.2, .01, .02], [.01, .4, .03], [.02, .03, .5]])
        omega = np.array([1., 2., 3.]); new = vectors_cad_to_flu(omega)
        self.assertAlmostEqual(omega @ inertia @ omega, new @ inertia_cad_to_flu(inertia) @ new)

    def test_moment_about_new_origin(self):
        np.testing.assert_allclose(shift_moment_origin([0,0,0], [0,10,0], [0,0,0], [1,0,0]), [0,0,-10])

    def test_invalid_data_rejected(self):
        with self.assertRaises(ValueError): vectors_cad_to_flu([1,2])
        with self.assertRaises(ValueError): vectors_cad_to_flu([1,np.nan,3])
        with self.assertRaises(ValueError): inertia_cad_to_flu(np.diag([1,0,2]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
