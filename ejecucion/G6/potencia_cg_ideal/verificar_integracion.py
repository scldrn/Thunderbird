import json
import unittest
from integrar_masas import compute, SOURCE

class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = compute(json.loads(SOURCE.read_text()))

    def test_coverage(self):
        self.assertEqual(len(self.rows), 36)
        self.assertEqual({r['source_index'] for r in self.rows}, set(range(36)))

    def test_asymmetric_station_midpoint(self):
        r = next(r for r in self.rows if r['reserve_mm'] == 38 and r['mode'] == 'x_CG_balanced')
        self.assertAlmostEqual(r['station_midpoint_x_m'], -.0125)
        self.assertAlmostEqual(r['scenario']['cx_fraction'], .0125/.2875)

    def test_case_near_station_edge(self):
        r = next(r for r in self.rows if r['reserve_mm'] == 80 and r['mode'] == 'remaining_equipment_at_x0')
        self.assertGreater(r['scenario']['max_individual_thrust_N'], 21)
        self.assertFalse(r['scenario']['cap_feasible_common_direction'])

    def test_equipment_zone_is_not_ignored(self):
        for reserve in (38, 60, 80):
            cases = [r for r in self.rows if r['reserve_mm'] == reserve and r['mode'] == 'x_CG_balanced']
            self.assertEqual(sum(not r['remaining_equipment_within_assumed_zone'] for r in cases), 1)

if __name__ == '__main__':
    unittest.main()
