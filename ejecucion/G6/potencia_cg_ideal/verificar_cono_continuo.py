import math
import unittest
import numpy as np
from reserva_momentos import G,solve
from cono_continuo import solve_continuous

class Tests(unittest.TestCase):
    def setUp(self):
        self.p=np.array([[x,y,0.] for x in (-.2,.2) for y in (-.08,.08)])
        self.cg=np.zeros(3)

    def test_hover(self):
        r=solve_continuous(self.p,self.cg,[0,0,0])
        self.assertEqual(r['status'],'Solved')
        self.assertAlmostEqual(r['capacity_N'],5*G/4,places=5)

    def test_cone_condition(self):
        f=[5*G*math.tan(math.radians(35)),0,5*G]
        a=solve_continuous(self.p,self.cg,[0,0,0],force=f,angle_deg=30)
        b=solve_continuous(self.p,self.cg,[0,0,0],force=f,angle_deg=45)
        self.assertIn(a['status'],('PrimalInfeasible','AlmostPrimalInfeasible'))
        self.assertEqual(b['status'],'Solved')

    def test_relaxation_and_monotonicity(self):
        force=[.25*5*G,-.25*5*G,1.25*5*G]
        vals=[]
        for angle in (35,40,45):
            a=solve_continuous(self.p,self.cg,[.5,-.5,.5],force=force,angle_deg=angle)
            b=solve(self.p,self.cg,[.5,-.5,.5],force_N=force,angle_deg=angle)
            self.assertEqual(a['status'],'Solved')
            self.assertTrue(b['feasible'])
            self.assertLessEqual(a['capacity_N'],b['capacity_N']+1e-5)
            vals.append(a['capacity_N'])
        self.assertGreaterEqual(vals[0]+1e-6,vals[1])
        self.assertGreaterEqual(vals[1]+1e-6,vals[2])

if __name__=='__main__':unittest.main()
