import math
import unittest
import cadquery as cq
from barrido import shaft,swept_shaft

class Tests(unittest.TestCase):
    def test_zero_height(self):
        a=shaft(0,0,0,1,10);b=swept_shaft(0,0,0,1,10,0)
        self.assertAlmostEqual(a.Volume(),b.Volume(),places=8)
    def test_volume_and_containment(self):
        s=swept_shaft(0,0,0,1,10,20)
        self.assertAlmostEqual(s.Volume(),10*(math.pi+40),places=6)
        for h in (0,1.3,10,19.7,20):
            c=shaft(0,0,h,1,10)
            self.assertLess(c.cut(s).Volume(),1e-6)
    def test_outside(self):
        s=swept_shaft(0,0,0,1,10,20)
        probe=cq.Solid.makeBox(1,1,1,cq.Vector(2,3,10))
        self.assertLess(s.intersect(probe).Volume(),1e-8)

if __name__=='__main__':unittest.main()
