"""Check C09 evidence consistency; not mechanical validation."""
from pathlib import Path
import json,unittest
P=Path(__file__).resolve().parent
class Audit(unittest.TestCase):
 def test_static(self):
  d=json.loads((P/'ENLACES.json').read_text());self.assertEqual(len(d['cases']),36)
  self.assertEqual(sum(c['only_combined_duct_interference'] for c in d['cases']),20)
  self.assertTrue(all(not c['errors'] for c in d['cases']))
 def test_motion_coverage(self):
  a=json.loads((P/'MOVIMIENTO_ENLACES.json').read_text())['cases']
  b=json.loads((P/'MOVIMIENTO_RESTO.json').read_text())['cases']
  self.assertEqual(len(a)+len(b),20)
  self.assertEqual(len({(c['rail_y_mm'],tuple(c['target_mm'])) for c in a+b}),20)
  self.assertTrue(all(not c['sampled_otherwise_clear'] for c in a+b))
  self.assertTrue(all(c['poses'][-1]['failure'] and not c['poses'][-1]['errors'] for c in a+b))
 def test_detailed(self):
  cases=json.loads((P/'RUTA_DETALLADA.json').read_text())['cases']
  self.assertEqual(len(cases),2)
  for c in cases:
   self.assertEqual(len(c['poses']),7)
   self.assertTrue(all(not x['errors'] for x in c['poses']))
if __name__=='__main__':unittest.main()
