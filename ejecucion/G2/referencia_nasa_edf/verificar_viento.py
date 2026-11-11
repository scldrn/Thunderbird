"""Analytical tests of dimensional conversion and fail-closed conditions."""
import math,unittest
from modelo_viento import (PSF_TO_PA,D_M,Rejected,ct_from_centered,power_w_from_centered,exploratory)
class Checks(unittest.TestCase):
 def test_polynomial_intercepts(self):
  self.assertAlmostEqual(ct_from_centered(0,0,0),1.248)
  self.assertAlmostEqual(power_w_from_centered(0,0),2552.)
 def test_consistency(self):
  e=exploratory(3*PSF_TO_PA,15,15000,1.225,340.3,75)
  self.assertAlmostEqual(e.jx**2+e.jz**2,e.advance_ratio**2,places=12)
  self.assertAlmostEqual(.5*1.225*e.velocity_m_s**2,e.q_pa,places=10)
  self.assertAlmostEqual(e.thrust_N,e.ct*1.225*(15000/60)**2*D_M**4,places=10)
  self.assertIn('NO_DEMOSTRADA',e.status)
 def test_bounds_and_conditions(self):
  for q,ang,rpm,rho,a,v in [(0,0,15000,1.225,340,75),(6.01*PSF_TO_PA,0,15000,1.225,340,75),(3*PSF_TO_PA,31,15000,1.225,340,75),(3*PSF_TO_PA,0,15000,1.225,340,74),(3*PSF_TO_PA,0,7999,1.225,340,75),(3*PSF_TO_PA,0,15000,0,340,75),(float('nan'),0,15000,1.225,340,75)]:
   with self.subTest(q=q,ang=ang,rpm=rpm,rho=rho,a=a,v=v):
    with self.assertRaises(Rejected):exploratory(q,ang,rpm,rho,a,v)
 def test_high_speed_rejected(self):
  for kmh in (600,1000):
   q=.5*1.225*(kmh/3.6)**2
   with self.assertRaises(Rejected):exploratory(q,0,15000,1.225,340.3,75)
if __name__=='__main__':unittest.main()
