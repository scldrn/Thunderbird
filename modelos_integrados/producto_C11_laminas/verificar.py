"""C11 evidence consistency; not flight or mechanism validation."""
from pathlib import Path
import hashlib,json,unittest
H=Path(__file__).resolve().parent

def get(n):return json.loads((H/n).read_text())
class Checks(unittest.TestCase):
 def test_geometry_source_and_kerf(self):
  d=get('ELEVADAS.json');self.assertEqual(len(d['axes']),4)
  self.assertAlmostEqual(d['kerf_mm'],.3)
  self.assertGreater(d['closed_original_volume_mm3'],d['closed_leaves_volume_mm3'])
  self.assertEqual(hashlib.sha256(Path(d['source']).read_bytes()).hexdigest(),d['source_sha256'])
 def test_screen_coverage(self):
  for name,n,key in [('ELEVADAS.json',6,'angle_deg'),('ELEVACION_LINEAL.json',4,'lift_mm'),('RESULTADOS.json',12,'angle_deg')]:
   d=get(name);self.assertEqual(len(d['angles']),n)
   self.assertEqual(len({x[key] for x in d['angles']}),n)
   for x in d['angles']:
    self.assertEqual(x['checked_pairs'],1282)
    self.assertEqual(x['screened_ok'],not x['collisions'] and not x['errors'])
 def test_projection_sensitivity(self):
  r=get('PROYECCION.json')['states']['elevado_60'];self.assertEqual(len(r),3)
  for a in r:self.assertTrue(0<=a['covered_fraction']<=1)
  self.assertLess(max(a['covered_fraction'] for a in r)-min(a['covered_fraction'] for a in r),.005)
 def test_cad_audit(self):
  a=get('AUDITORIA_CAD.json');self.assertEqual(len(a['states']),2)
  self.assertTrue(all(v['native_count']==9 and v['step_count']==9 and not v['invalid_native'] and not v['invalid_step'] for v in a['states']))
  self.assertLess(max(a['center_errors_mm'].values()),1e-4)
if __name__=='__main__':unittest.main()
