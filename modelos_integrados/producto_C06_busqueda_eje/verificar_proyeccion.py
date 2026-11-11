"""Analytical controls for silhouette rasterizer."""
import unittest
from proyeccion_apertura import raster_coverage

class TestProjection(unittest.TestCase):
 def test_empty(self):
  r,_,_=raster_coverage([],[],256,(0,0),1)
  self.assertEqual(r['covered_fraction'],0)
 def test_complete_circle(self):
  vertices=[(-2,-2),(2,-2),(2,2),(-2,2)]
  r,_,_=raster_coverage(vertices,[(0,1,2),(0,2,3)],512,(0,0),1)
  self.assertEqual(r['covered_fraction'],1)
 def test_half_circle(self):
  vertices=[(-2,-2),(0,-2),(0,2),(-2,2)]
  r,_,_=raster_coverage(vertices,[(0,1,2),(0,2,3)],1024,(0,0),1)
  self.assertAlmostEqual(r['covered_fraction'],.5,delta=.004)
 def test_circle_area(self):
  r,_,_=raster_coverage([],[],1024,(0,0),1)
  self.assertAlmostEqual(r['circle_raster_area_mm2']/r['analytic_circle_area_mm2'],1,delta=.005)

if __name__=='__main__':unittest.main()
