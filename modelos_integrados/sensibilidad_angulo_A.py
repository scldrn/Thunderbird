"""Necessary geometric bounds and sufficient continuous ideal control coverage.

Actual installed force cones remain unmeasured. No CFD snapshot sets delta.
"""
from pathlib import Path
import json,math,hashlib
import numpy as np
import reversibilidad_6dof_A as control

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'vectorizacion_A/sensibilidad_angulo'
if (OUT/'RESUMEN.json').exists():raise FileExistsError('Preserve completed study')
OUT.mkdir(exist_ok=True);control.OUT=OUT
results=[]
for mass in (2.,5.,10.):
 ratio=mass/5;scale=ratio**(1/3)
 for delta in (35.,40.):
  name=f'base_{mass:g}kg_cono_{delta:g}deg'
  try:
   r=control.certificate(name,mass=mass,scale=scale,z=.058*scale,
       lever_z_fx=-.040*scale,lever_z_fy=-.012*scale,
       upright_only=True,resolution=2,delta=delta,
       preload_z=ratio,torque_component=.5*ratio**(5/3))
   results.append(dict(status='sufficient_certificate',result=r))
  except RuntimeError as e:
   results.append(dict(status='no_certificate_not_impossibility_proof',mass_kg=mass,delta_deg=delta,error=str(e)))
 source=ROOT/f'vectorizacion_A/reversibilidad_6DOF/base_horizontal_{mass:g}kg.json'
 r=json.loads(source.read_text())
 assert r['mass_assumed_kg']==mass and r['effective_cone_half_angle_deg']==45
 results.append(dict(status='previous_verified_reference',source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),result=r))
# A ball of radius a*mg about hover must lie in the total positive cone.
# Its tangent half-angle is asin(a), not atan(a) for a horizontal-only slice.
geometric=[dict(delta_deg=d,horizontal_slice_acceleration_bound_g=math.tan(math.radians(d)),three_axis_ball_acceleration_bound_g=math.sin(math.radians(d))) for d in (10,15,20,25,30,35,40,45,60)]
summary=dict(results=results,geometric_necessary_bounds=geometric,
            target_ball_acceleration_g=.5,
            necessary_angle_for_horizontal_0p5g_deg=math.degrees(math.atan(.5)),
            necessary_angle_for_ball_0p5g_deg=math.degrees(math.asin(.5)),
            necessary_bounds_prove_sufficiency=False,
            torque_preload_and_capacity_may_require_larger_angle=True,
            assumptions=['all four useful force vectors have positive axial sign and same circular cone','body horizontal and CG at assumed origin','mass and station scale hypothetical','no measured force/power map or free actuator couples'],
            installed_hardware_validated=False)
(OUT/'RESUMEN.json').write_text(json.dumps(summary,indent=2));print('Angle sensitivity completed',flush=True)
