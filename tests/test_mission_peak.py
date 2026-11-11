import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'ejecucion/G1/decision_integrada_c02/calcular.py'
spec = importlib.util.spec_from_file_location('historical_mission', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MissionPeakTests(unittest.TestCase):
    def mission(self, hover_s, maneuver_s):
        return module.mission(1, 3.6, 0, 100, hover_s, 0,
                              1000, 100, maneuver_s, 1, 100, 1000)

    def test_partial_maneuver_includes_hover_peak(self):
        self.assertEqual(self.mission(10, 2)['pack_electric_peak_W'], 1000)

    def test_whole_hover_period_maneuver_excludes_hover_peak(self):
        self.assertEqual(self.mission(10, 10)['pack_electric_peak_W'], 100)

    def test_no_maneuver_and_no_hover(self):
        self.assertEqual(self.mission(10, 0)['pack_electric_peak_W'], 1000)
        self.assertAlmostEqual(self.mission(0, 0)['pack_electric_peak_W'], .01)


if __name__ == '__main__':
    unittest.main()
