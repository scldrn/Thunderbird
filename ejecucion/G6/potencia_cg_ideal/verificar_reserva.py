import unittest
import numpy as np
from reserva_momentos import G, solve

class MomentTests(unittest.TestCase):
    def setUp(self):
        self.centres=np.array([[x,y,0] for x in (-.2,.2) for y in (-.08,.08)])
        self.cg=np.zeros(3)

    def test_symmetric_hover(self):
        r=solve(self.centres,self.cg,[0,0,0],angle_deg=0)
        self.assertTrue(r['feasible'])
        self.assertAlmostEqual(r['capacity_N'],5*G/4,places=8)

    def test_vertical_pitch_analytic(self):
        r=solve(self.centres,self.cg,[0,.5,0],angle_deg=0)
        self.assertAlmostEqual(r['capacity_N'],5*G/4+.5/(4*.2),places=8)

    def test_no_vertical_yaw_authority(self):
        self.assertFalse(solve(self.centres,self.cg,[0,0,.5],angle_deg=0)['feasible'])

    def test_pitch_symmetry(self):
        a=solve(self.centres,self.cg,[0,.5,0])
        b=solve(self.centres,self.cg,[0,-.5,0])
        self.assertAlmostEqual(a['capacity_N'],b['capacity_N'],places=8)

    def test_specified_vertical_acceleration(self):
        r=solve(self.centres,self.cg,[0,0,0],angle_deg=0,force_N=[0,0,1.25*5*G])
        self.assertAlmostEqual(r['capacity_N'],1.25*5*G/4,places=8)

    def test_horizontal_outside_cone(self):
        self.assertFalse(solve(self.centres,self.cg,[0,0,0],angle_deg=0,force_N=[1,0,5*G])['feasible'])

if __name__=='__main__': unittest.main()
