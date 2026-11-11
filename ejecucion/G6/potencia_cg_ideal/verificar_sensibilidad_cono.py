import math
import unittest
import numpy as np
from reserva_momentos import G, solve

class ConeTests(unittest.TestCase):
    def setUp(self):
        self.points=np.array([[x,y,0] for x in (-.2,.2) for y in (-.08,.08)])
        self.cg=np.zeros(3)

    def test_below_cone_fails_above_cone_passes(self):
        force=[5*G*math.tan(math.radians(35)),0,5*G]
        self.assertFalse(solve(self.points,self.cg,[0,0,0],angle_deg=30,force_N=force)['feasible'])
        self.assertTrue(solve(self.points,self.cg,[0,0,0],angle_deg=45,force_N=force)['feasible'])

    def test_zero_acceleration_symmetric(self):
        for angle in (35,40,45):
            result=solve(self.points,self.cg,[0,0,0],angle_deg=angle)
            self.assertAlmostEqual(result['capacity_N'],5*G/4,places=8)

if __name__=='__main__': unittest.main()
