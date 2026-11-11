"""Consistency checks on C08 evidence; not physical verification."""
from pathlib import Path
import hashlib,json,unittest
H=Path(__file__).resolve().parent

def read(name):return json.loads((H/name).read_text())

class EvidenceChecks(unittest.TestCase):
 def test_grid_and_nominal_rotor_containment(self):
  r=read('GUIAS.json');rows=r['candidates']
  self.assertEqual(len(rows),72)
  self.assertEqual(len({(a['y_mm'],a['z_mm']) for a in rows}),72)
  self.assertEqual(len(r['rotor_sweep_audit']),4)
  for q in r['rotor_sweep_audit']:self.assertLessEqual(q['outside_volume_mm3'],.001)
  for q in rows:
   if q['clear_closed']:
    self.assertTrue(q['roof_floor_sampled_ok'])
    self.assertEqual(q['tested_count'],320)
    self.assertNotIn('obstruction',q);self.assertNotIn('error',q)

 def test_moving_candidates(self):
  closed={(v['y_mm'],v['z_mm']) for v in read('GUIAS.json')['candidates'] if v['clear_closed']}
  moving=read('GUIAS_MOVIMIENTO.json')['candidates']
  self.assertEqual({(v['y_mm'],v['z_mm']) for v in moving},closed)
  for q in moving:self.assertEqual(q['pairs_screened'],48)

 def test_selected_pair_and_distances(self):
  best=read('COMPARACION_PARES.json')['pairs'][0]
  man=read('MANIFIESTO_ALT.json');pair=man['pair']
  self.assertEqual((pair['left_y_mm'],pair['left_z_mm']),(best['left']['y_mm'],best['left']['z_mm']))
  self.assertEqual((pair['right_y_mm'],pair['right_z_mm']),(best['right']['y_mm'],best['right']['z_mm']))
  for state,field in [('cerrado','distance_closed_mm'),('abierto','distance_open_mm')]:
   v=next(v for v in man['states'] if v['state']==state)
   for i,side in enumerate(('left','right')):
    self.assertAlmostEqual(v['rail_door_distances'][i]['distance_to_cover_mm'],best[side][field],places=6)
   for kind in ('fcstd','step'):
    h=hashlib.sha256((H/v[kind]).read_bytes()).hexdigest()
    self.assertEqual(h,v[kind+'_sha256'])

 def test_reported_link_cases(self):
  r=read('UNION_ALT.json');self.assertEqual(len(r['cases']),36)
  for q in r['cases']:
   self.assertGreater(q['door_contact_volume_mm3'],1e-5)
   self.assertIn('obstruction',q)
   self.assertFalse(q['clear_closed'])
   self.assertNotIn('error',q)

if __name__=='__main__':unittest.main()
