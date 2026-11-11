import math
import unittest
from calculate import evaluate


class MissionSensitivityTests(unittest.TestCase):
    def test_energy_balance_and_peak(self):
        r = evaluate(5, 360, 1, 20, 30, 0.5, 100, 1000)
        expected_work = .5 * 5 * 100**2 + 20 * r['acceleration_distance_m'] + 20 * 100 * 30
        self.assertAlmostEqual(r['electrical_energy_wh'], expected_work / .5 / 3600)
        self.assertAlmostEqual(r['peak_electrical_power_w'], (5 * 9.80665 + 20) * 100 / .5)
        self.assertEqual(r['pack_mass_kg'], max(r['pack_energy_mass_kg'], r['pack_power_mass_kg']))

    def test_duration_increases_energy_not_peak(self):
        a = evaluate(2, 600, 1, 20, 30)
        b = evaluate(2, 600, 1, 20, 120)
        self.assertGreater(b['electrical_energy_wh'], a['electrical_energy_wh'])
        self.assertEqual(b['peak_electrical_power_w'], a['peak_electrical_power_w'])

    def test_rejects_invalid_inputs(self):
        for value in (0, -1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                evaluate(value, 600, 1, 20, 30)
        with self.assertRaises(ValueError):
            evaluate(2, 600, 1, 20, 30, efficiency=1.1)


if __name__ == '__main__':
    unittest.main()
