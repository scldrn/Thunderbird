"""Analytic rotating prism and beam-section references, not hardware approval."""
import unittest
import cadquery as cq
import numpy as np
from cargas_rotor import centrifugal_resultants, section_properties, normal_stress


class AnalyticChecks(unittest.TestCase):
    def test_radial_prism_force_matches_closed_form(self):
        shape = cq.Workplane('XY').box(20, 5, 2).val().translate((30, 0, 0))
        rho, omega, r0, r1, area = 1600, 1000, .02, .04, 10e-6
        force, moment, _ = centrifugal_resultants(shape, np.array([r0, 0, 0]), rho, omega)
        expected = rho*area*omega**2*(r1*r1-r0*r0)/2
        np.testing.assert_allclose(force, [expected, 0, 0], atol=1e-10)
        np.testing.assert_allclose(moment, [0, 0, 0], atol=1e-12)

    def test_rectangle_section_area_and_bending(self):
        shape = cq.Workplane('XY').box(20, 5, 2).val().translate((30, 0, 0))
        section = section_properties(shape, 30)
        np.testing.assert_allclose(section['A_m2'], 10e-6, rtol=1e-9)
        stress = normal_stress(section, 10., [1., 0.])
        expected_max = 10/10e-6+6/(.005*.002**2)
        np.testing.assert_allclose(stress['sampled_max_normal_Pa'], expected_max, rtol=1e-8)


if __name__ == '__main__':
    unittest.main(verbosity=2)
