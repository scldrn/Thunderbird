"""Analytical and sampling checks; numerical tests do not prove CAD fitness."""
import math
import random
import unittest
from envolvente import motion_bounds, trig_extrema


class BoundsChecks(unittest.TestCase):
    def test_known_trigonometric_extrema(self):
        self.assertEqual(trig_extrema(1,0,0,math.pi),( -1.0,1.0))
        a,b=trig_extrema(0,1,0,math.pi)
        self.assertAlmostEqual(a,0.0)
        self.assertAlmostEqual(b,1.0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): trig_extrema(1,1,1,0)
        with self.assertRaises(ValueError): motion_bounds((1,0,0,1,0,1),(0,0,0),10,110,'giro',0)
        with self.assertRaises(ValueError): motion_bounds((0,1,0,1,0,1),(0,0,0),10,110,'giro',-1)

    def test_rotated_and_lifted_points_contained(self):
        rng=random.Random(7211)
        for _ in range(60):
            bounds=(-5,7,-20,13,-12,18)
            axis=(0,rng.uniform(-30,30),rng.uniform(-30,30))
            lift=rng.uniform(0,20)
            angle=rng.uniform(-220,220)
            b=motion_bounds(bounds,axis,lift,angle,'giro',0.01)
            for _ in range(200):
                x=rng.uniform(bounds[0],bounds[1]); y=rng.uniform(bounds[2],bounds[3]); z=rng.uniform(bounds[4],bounds[5])
                t=math.radians(angle*rng.random())
                dy=y-axis[1]; dz=z-axis[2]
                v=(x,axis[1]+math.cos(t)*dy-math.sin(t)*dz,axis[2]+lift+math.sin(t)*dy+math.cos(t)*dz)
                for i in range(3):
                    self.assertLessEqual(b[2*i]-1e-9,v[i]); self.assertLessEqual(v[i],b[2*i+1]+1e-9)

    def test_fixed_translation(self):
        b=(1,2,3,4,5,6)
        self.assertEqual(motion_bounds(b,(0,0,0),10,110,'fijo',0),b)
        self.assertEqual(motion_bounds(b,(0,0,0),10,110,'traslacion',0),(1,2,3,4,5,16))

if __name__=='__main__': unittest.main()
