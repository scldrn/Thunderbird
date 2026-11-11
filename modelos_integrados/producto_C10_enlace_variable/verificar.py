from pathlib import Path
import json,unittest
from resumir import classify
H=Path(__file__).resolve().parent
class Verification(unittest.TestCase):
 def test_independent_classification(self):
  self.assertEqual(classify({'sampled_ok':True,'poses':[]}), 'pasa_muestras')
  self.assertEqual(classify({'sampled_ok':False,'poses':[{'collision':{'name':'piel'}}]}),'colision')
  self.assertEqual(classify({'sampled_ok':False,'poses':[{'error':'no se obtuvo contacto volumetrico con tapa'}]}),'contacto_no_establecido')
  self.assertEqual(classify({'sampled_ok':False,'poses':[{'errors':[{'error':'kernel'}]}]}),'error_de_calculo')
 def test_cases_and_identity(self):
  a=json.loads((H/'BUSQUEDA.json').read_text())['cases'];b=json.loads((H/'BUSQUEDA_30.json').read_text())['cases']
  key=lambda v:(v['rail_y_mm'],tuple(v['target_mm']))
  self.assertEqual(len(a),20);self.assertEqual(len(b),20)
  self.assertEqual(len({key(v) for v in a}),20);self.assertEqual({key(v) for v in a},{key(v) for v in b})
  self.assertTrue(all(v['poses'] for v in a+b))
 def test_passing_cases_covered(self):
  for name,n in [('BUSQUEDA.json',7),('BUSQUEDA_30.json',8)]:
   for v in json.loads((H/name).read_text())['cases']:
    if v['sampled_ok']:
     self.assertEqual(len(v['poses']),n)
     self.assertTrue(all(not p.get('error') and not p.get('errors') and not p.get('collision') for p in v['poses']))
if __name__=='__main__':unittest.main()
