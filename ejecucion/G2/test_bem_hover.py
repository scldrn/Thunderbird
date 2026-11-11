"""Equation verification, independent of installed hardware claims."""
import unittest
import numpy as np
from bem_hover import Polar, solve_design


class ConstantPolar:
    def lookup(self, alpha_deg, reynolds):
        return .6, .02, True


class RotorVerification(unittest.TestCase):
    def test_polar_exact_tabulated_values_and_flags(self):
        polar = Polar()
        for re, table in polar.blocks:
            for alpha, cl, cd in table:
                result = polar.lookup(alpha, re)
                np.testing.assert_allclose(result[:2], [cl, cd], atol=1e-14)
                self.assertTrue(result[2])
        self.assertFalse(polar.lookup(60, 100000)[2])
        self.assertFalse(polar.lookup(4, 100)[2])

    def test_momentum_energy_and_free_disk_reference(self):
        r = solve_design(.041, 200, cells=48, polar=ConstantPolar())
        self.assertTrue(r['all_annular_balances_converged'])
        self.assertLess(r['max_normalized_balance_residual'], 1e-6)
        self.assertLess(r['energy_identity_relative_residual'], 1e-12)
        self.assertGreater(r['shaft_model_W'], r['ideal_free_disk_W_same_T'])

    def test_dimensional_similarity_when_coefficients_are_constant(self):
        a = solve_design(.041, 180, cells=32, polar=ConstantPolar())
        b = solve_design(.082, 180, cells=32, polar=ConstantPolar())
        self.assertAlmostEqual(b['T_isolated_model_N']/a['T_isolated_model_N'], 4, places=6)
        self.assertAlmostEqual(b['shaft_model_W']/a['shaft_model_W'], 4, places=6)
        self.assertAlmostEqual(b['Q_isolated_model_Nm']/a['Q_isolated_model_Nm'], 8, places=6)
        self.assertAlmostEqual(b['rpm']/a['rpm'], .5, places=8)

    def test_inverse_twist_is_recovered_by_fixed_twist_solve(self):
        a = solve_design(.041, 190, cells=32)
        beta = np.array([r['beta_rad'] for r in a['annuli']])
        b = solve_design(.041, 190, cells=32, fixed_beta_rad=beta)
        self.assertTrue(b['all_annular_balances_converged'])
        self.assertLess(abs(a['T_isolated_model_N']/b['T_isolated_model_N']-1), 1e-6)
        self.assertLess(abs(a['shaft_model_W']/b['shaft_model_W']-1), 1e-6)

    def test_radial_quadrature_sensitivity(self):
        a = solve_design(.041, 200, cells=64)
        b = solve_design(.041, 200, cells=128)
        self.assertLess(abs(a['T_isolated_model_N']/b['T_isolated_model_N']-1), .005)
        self.assertLess(abs(a['shaft_model_W']/b['shaft_model_W']-1), .005)


if __name__ == '__main__':
    unittest.main(verbosity=2)
