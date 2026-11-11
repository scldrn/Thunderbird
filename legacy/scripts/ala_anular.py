"""TN4117 graphical readings + isolated low-speed ring sizing.
Reads are approximate manual digitization, not original numerical data.
Matched central-wing lift slope*area; NOT whole-vehicle trim validation.
"""
import math,json,csv
from pathlib import Path
from calcular import RHO,MU,G
from trimado_superficies import OUT

READINGS=[
 (1/3,.018,.024,4.7),
 (2/3,.034,.017,6.7),
 (1.,.049,.012,9.7),
 (1.5,.069,.028,11.0),
 (3.,.102,.035,12.3)]

def main():
    source=dict(url='https://ntrs.nasa.gov/citations/19930084906',report='NACA TN4117',
       mach=.13,Re_chord_range=[.704e6,2.11e6],
       method='Manual approximate readings of figures10,11,12 (printed18,19,20); no exact tabulated coefficients.',
       reading_uncertainty_NOT_measurement_error=dict(slope_per_degree=.002,CD0=.004,LDmax=.2),
       readings=[dict(aspect_ratio=a,slope_per_degree=s,CD0=c,LDmax=ld) for a,s,c,ld in READINGS])
    (OUT/'anular_lecturas_GRAFICAS.json').write_text(json.dumps(source,indent=2))
    prior=json.loads((OUT/'comparacion_integrada_RESUMEN.json').read_text())['selected_f6']
    rows=[]
    for baseline in prior:
      m=baseline['mass_kg'];sw=baseline['wing_oneplane_m2'];bodyd=baseline['D_m']
      required_slope_area=2*sw
      for ar,slope_deg,cd0,ldmax in READINGS:
        slope=slope_deg*180/math.pi;area=required_slope_area/slope
        d=math.sqrt(ar*area);c=math.sqrt(area/ar);section_t=.117*c
        sheet_area=math.pi*(d+section_t)*c # thin midsurface geometrical estimate
        q=.5*RHO*(150/3.6)**2;cl=slope_deg*8
        lift=q*area*cl;drag=q*area*(cd0+cl*cl/(2*math.pi*ar))
        # Readout sensitivity only, NOT physical confidence interval.
        area_lo=required_slope_area/((slope_deg+.002)*180/math.pi)
        area_hi=required_slope_area/((slope_deg-.002)*180/math.pi)
        central_target=q*sw*2*math.radians(8)
        annulus=math.pi*max(0,d*d-bodyd*bodyd)/4
        assert abs(lift-central_target)<1e-9
        rows.append(dict(mass_kg=m,aspect_ratio=ar,area_reference_m2=area,
           inner_diameter_m=d,outer_diameter_est_m=d+2*section_t,chord_m=c,
           radial_gap_to_body_m=(d-bodyd)/2,
           body_blockage_area_fraction=(bodyd/d)**2,
           annular_open_area_m2=annulus,
           ideal_hover_power_IF_annular_actuator_W=(m*G)**1.5/math.sqrt(2*RHO*annulus) if annulus>0 else None,
           fits_body_plus_10mm_radial=d>=bodyd+.02,
           ring_midsurface_m2=sheet_area,reference_cruciform_sheet_m2=2*sw,
           area_ratio_ring_to_cross=sheet_area/(2*sw),
           low_speed_lift_N=lift,low_speed_drag_est_N=drag,
           low_speed_LD_est=lift/drag,CL_est_at8deg=cl,
           Re_chord_150kmh=RHO*(150/3.6)*c/MU,
           Re_inside_global_experiment_range=.704e6<=RHO*(150/3.6)*c/MU<=2.11e6,
           area_readout_sensitivity_low_m2=area_lo,area_readout_sensitivity_high_m2=area_hi,
           parasitic_drag_1000kmh_IF_CD0_unchanged_N=.5*RHO*(1000/3.6)**2*area*cd0))
    with (OUT/'ala_anular_COMPARACION_CONDICIONAL.csv').open('w') as file:
      w=csv.DictWriter(file,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=dict(cases=len(rows),selected_AR15=[r for r in rows if r['aspect_ratio']==1.5],
       warnings=['Ring is isolated, no body/support interference, no own pitching moment.','High-speed drag column is a constant-coefficient sensitivity, NOT transonic data.','Projected area and midsurface are different quantities.','Global experimental Re range does not prove matching individual test Reynolds number.'])
    (OUT/'ala_anular_RESUMEN.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
