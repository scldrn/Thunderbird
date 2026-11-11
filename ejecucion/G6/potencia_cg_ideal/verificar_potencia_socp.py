import math
import unittest
from potencia_fuerzas_socp import ideal_power,battery_illustration,RHO,DIAMETER_M

class Tests(unittest.TestCase):
    def test_uniform_disks(self):
        t=12.5; a=math.pi*DIAMETER_M**2/4
        self.assertAlmostEqual(ideal_power([[0,0,t]]*4),4*t**1.5/math.sqrt(2*RHO*a))
    def test_permutation_and_scaling(self):
        f=[[1,2,3],[4,0,5],[0,1,1],[1,0,0]]
        self.assertAlmostEqual(ideal_power(f),ideal_power(list(reversed(f))))
        self.assertAlmostEqual(ideal_power([[2*x for x in v] for v in f])/ideal_power(f),2**1.5)
    def test_battery_units_and_dual_limits(self):
        r=battery_illustration(3000,120,.6,150,5000)
        self.assertAlmostEqual(r['energy_Wh'],5000/30)
        self.assertAlmostEqual(r['mass_power_kg'],1.)
        self.assertAlmostEqual(r['mass_lower_assumption_kg'],10/9)
    def test_invalid(self):
        with self.assertRaises(ValueError):ideal_power([[1,0,0]])
        with self.assertRaises(ValueError):battery_illustration(1,1,0)

if __name__=='__main__':unittest.main()
