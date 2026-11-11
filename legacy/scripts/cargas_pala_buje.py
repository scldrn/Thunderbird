"""Preliminary rotor load envelope; all blade geometry/mass/material choices assumed."""
import math,json,csv
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'resultados'
rows=[]
for rpm in [5000,6000,7000]:
 for mass in [.010,.015,.020]:
  for chord in [.025,.035]:
   root=.025;tip=.2286;span=tip-root;omega=rpm*2*math.pi/60
   rc=(root+tip)/2
   centrifugal=mass*omega**2*rc
   # Uniform mass, planar blade. Principal inertia differences produce centrifugal pitch torque.
   pitch=math.radians(25);I_pitch=mass*chord**2/12
   centrifugal_pitch=omega**2*I_pitch*abs(math.sin(pitch)*math.cos(pitch))
   # Constant chord and assumed sectional moment coefficient. No inflow correction.
   moment_integral=.5*1.225*omega**2*chord**2*(tip**3-root**3)/3
   # Load distribution assumed proportional to r^2.
   lift_radius=.75*(tip**4-root**4)/(tip**3-root**3)
   bending=(38.9412701/2)*(lift_radius-root)
   # Uniform radial span inertia and pitch-transient acceleration of 50deg in70ms triangular speed.
   acceleration=4*math.radians(50)/.07**2
   dynamic_pitch=I_pitch*acceleration
   for cm in [.01,.05]:
    aero=moment_integral*cm
    offset=(38.9412701/2)*.002
    # Add magnitudes as screening, friction unknown hence independent allowance .02Nm each.
    total=2*(centrifugal_pitch+aero+offset+dynamic_pitch+.02)
    servo=total*.5/.8
    rows.append(dict(rpm=rpm,blade_mass_g=mass*1000,chord_mm=chord*1000,Cm_assumed=cm,tip_speed_ms=omega*tip,tip_Mach=omega*tip/340.3,centrifugal_per_blade_N=centrifugal,root_flap_moment_Nm=bending,centrifugal_pitch_per_blade_Nm=centrifugal_pitch,aero_pitch_per_blade_Nm=aero,pitch_inertia_per_blade_Nm=dynamic_pitch,total_two_blade_pitch_Nm=total,servo_required_Nm=servo,servo_travel_deg=100,kinematic_time_at_0_09s_per60deg=.15,blade_grip_bearing_couple_N_at_12mm=bending/.012))
with (OUT/'cargas_pala_buje_ESCENARIOS.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
base=[r for r in rows if r['rpm']==6000 and r['blade_mass_g']==15 and r['chord_mm']==25]
summary=dict(base=base,centrifugal_range_N=[min(r['centrifugal_per_blade_N'] for r in rows),max(r['centrifugal_per_blade_N'] for r in rows)],servo_range_Nm=[min(r['servo_required_Nm'] for r in rows),max(r['servo_required_Nm'] for r in rows)],budget_g=dict(servo=20,blades=30,ESC_assumed=20,remaining_for_hub_bearings_linkage=98.25-20-30-20),notes=['no material stress or fatigue approval','no aerodynamic thrust validation','Cm, mass, chord, offset, friction assumed','servo speed figure cannot be combined with rated torque as simultaneous performance'])
assert all(math.isfinite(r['servo_required_Nm']) for r in rows)
(OUT/'cargas_pala_buje_resumen.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
