"""Independent unit and inverse consistency checks, not physical validation."""
import math,unittest
from modelo import predict,rpm_for_thrust,hypothetical_hover,LBF_TO_N
class Checks(unittest.TestCase):
 def test_centre(self):
  p=predict(285.94*60)
  self.assertAlmostEqual(p.thrust_N,9.806*LBF_TO_N,places=10)
  self.assertAlmostEqual(p.dc_power_W,1998.,places=9)
 def test_known_end_interpolations(self):
  self.assertAlmostEqual(predict(10000).thrust_N/LBF_TO_N,3.3,delta=.3)
  self.assertAlmostEqual(predict(20000).dc_power_W/1000,3.2,delta=.25)
 def test_inverse(self):
  for n in (8000,10000,16000,22000,24000):
   self.assertAlmostEqual(rpm_for_thrust(predict(n).thrust_N),n,places=6)
 def test_gates(self):
  for n in (7999,24001,float('nan'),float('inf')):
   with self.assertRaises(ValueError):predict(n)
  with self.assertRaises(ValueError):rpm_for_thrust(0)
 def test_mass_and_out_of_domain(self):
  self.assertEqual(hypothetical_hover(2)['status'],'fuera_intervalo_exploratorio')
  self.assertAlmostEqual(hypothetical_hover(5)['mass_left_before_other_components_kg'],.6)
  self.assertEqual(hypothetical_hover(10)['status'],'modelo_condicional')
if __name__=='__main__':unittest.main()
