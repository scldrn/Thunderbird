import math,random,unittest
from modelo import allocate,scenario,Infeasible,G,RHO,D5_M
class Tests(unittest.TestCase):
 def test_centered(self):
  r=allocate(0,0)
  for x in r.weights:self.assertAlmostEqual(x,.25,places=10)
  self.assertAlmostEqual(r.weighted_power_factor,1,places=10)
 def test_offset_analytical(self):
  r=allocate(.6,0)
  for x,y in zip(r.weights,(.4,.4,.1,.1)):self.assertAlmostEqual(x,y,places=10)
  f=(2*.4**1.5+2*.1**1.5)/.5
  self.assertAlmostEqual(r.weighted_power_factor,f,places=10)
 def test_constraints_and_brute_force(self):
  rng=random.Random(129)
  for _ in range(30):
   x,y=rng.uniform(-.9,.9),rng.uniform(-.9,.9)
   r=allocate(x,y);w=r.weights
   self.assertAlmostEqual(sum(w),1,places=9)
   self.assertAlmostEqual(w[0]+w[1]-w[2]-w[3],x,places=9)
   self.assertAlmostEqual(w[0]+w[2]-w[1]-w[3],y,places=9)
   a=(1+x)/2;b=(1+y)/2;l=max(0,a+b-1);u=min(a,b)
   samples=[]
   for i in range(1001):
    t=l+(u-l)*i/1000;z=(t,a-t,b-t,1-a-b+t)
    samples.append(sum(max(0,v)**1.5 for v in z))
   self.assertLessEqual(sum(v**1.5 for v in w),min(samples)+1e-10)
 def test_capped_and_impossible(self):
  with self.assertRaises(Infeasible):allocate(.6,0,.35)
  r=allocate(.6,0,.41);self.assertLessEqual(max(r.weights),.41)
  self.assertAlmostEqual(sum(r.weights),1)
 def test_binding_cap_changes_optimum(self):
  unrestricted=allocate(.6,.4)
  cap=max(unrestricted.weights)-.01
  limited=allocate(.6,.4,cap)
  self.assertAlmostEqual(max(limited.weights),cap,places=9)
  self.assertGreater(limited.weighted_power_factor,unrestricted.weighted_power_factor)
  self.assertAlmostEqual(limited.weights[0]+limited.weights[1]-limited.weights[2]-limited.weights[3],.6)
  self.assertAlmostEqual(limited.weights[0]+limited.weights[2]-limited.weights[1]-limited.weights[3],.4)
 def test_baseline_and_cone(self):
  r=scenario(5,0,0,0)
  expected=(5*G)**1.5/math.sqrt(2*RHO*4*math.pi*D5_M**2/4)
  self.assertAlmostEqual(r['min_ideal_W'],expected,places=9)
  self.assertTrue(scenario(5,0,0,1,cone_deg=45)['cone_possible'])
  self.assertFalse(scenario(5,0,0,2,cone_deg=45)['cone_possible'])
 def test_mass_scale(self):
  a=scenario(2,0,0,0)['min_ideal_W'];b=scenario(10,0,0,0)['min_ideal_W']
  self.assertAlmostEqual(b/a,5**(7/6),places=9)
if __name__=='__main__':unittest.main()
