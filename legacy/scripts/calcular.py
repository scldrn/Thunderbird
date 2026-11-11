"""Screening reproducible; stdlib only. No CFD, no aircraft certification.
All SI. Closed reference hulls, not an integrated inlet/engine geometry.
"""
import math, csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'resultados'
G=9.80665; RHO=1.225; MU=1.7894e-5; TEMP=288.15; CP=1004.5

def simpson(fn,n=4000):
    h=math.pi/n
    return h/3*(fn(0)+fn(math.pi)+sum((4 if i%2 else 2)*fn(i*h) for i in range(1,n)))

def geometry(volume,f,family,n=4000):
    # x=L(1-cos(theta))/2; r=D/2 sin(theta)^p
    p={'esferoide':1.,'sears_haack':1.5}[family]
    coeff=math.pi/6 if p==1 else 3*math.pi**2/64
    D=(volume/(coeff*f))**(1/3); L=f*D
    def terms(t):
        sn=math.sin(t); co=math.cos(t)
        x=-L*co/2; r=D/2*max(0,sn)**p
        dx=L/2*sn
        dr=D/2*p*max(0,sn)**(p-1)*co
        da=2*math.pi*r*math.hypot(dx,dr)
        return x,r,dx,da
    area=simpson(lambda t:terms(t)[3],n)
    integvol=simpson(lambda t:math.pi*terms(t)[1]**2*terms(t)[2],n)
    lateral=simpson(lambda t:2*terms(t)[1]*terms(t)[2],n)
    ix=simpson(lambda t:terms(t)[1]**2*terms(t)[3],n)/area
    iy=simpson(lambda t:(terms(t)[0]**2+terms(t)[1]**2/2)*terms(t)[3],n)/area
    return dict(L_m=L,D_m=D,volume_m3=integvol,wet_m2=area,side_m2=lateral,frontal_m2=math.pi*D*D/4,shell_Ix_per_kg=ix,shell_Iy_per_kg=iy)

def write_csv(name,rows):
    with (OUT/name).open('w') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
    OUT.mkdir(exist_ok=True)
    checks=[]
    for family in ['esferoide','sears_haack']:
        a=geometry(.01,6,family,2000);b=geometry(.01,6,family,4000)
        assert abs(b['volume_m3']/.01-1)<1e-9
        assert abs(a['wet_m2']/b['wet_m2']-1)<1e-6
        checks.append(dict(check='integracion_'+family,volume_relative_error=abs(b['volume_m3']/.01-1),area_refinement_relative=abs(a['wet_m2']/b['wet_m2']-1)))
    sphere=geometry(.01,1,'esferoide')
    assert abs(sphere['wet_m2']/(math.pi*sphere['D_m']**2)-1)<1e-9
    assert abs(sphere['shell_Ix_per_kg']/sphere['shell_Iy_per_kg']-1)<1e-9
    rows=[];hulls=[]
    for mass in [2,5,10]:
      for family in ['esferoide','sears_haack']:
       for j in range(101):
        f=2+j*.1;geo=geometry(mass/200,f,family,1000)
        hulls.append(dict(mass_kg=mass,family=family,fineness=f,**geo))
        for speed in [600,1000]:
          u=speed/3.6;mach=u/math.sqrt(1.4*287.05*TEMP);q=.5*RHO*u*u;re=RHO*u*geo['L_m']/MU
          cf=.455/math.log10(re)**2.58/(1+.144*mach*mach)**.65
          # Alternative screening hypotheses, not verified profile-specific form drag.
          for model,ff in [('FF_A',1+1.5/f**1.5+7/f**3),('FF_B',1+60/f**3+.0025*f)]:
            drag=q*geo['wet_m2']*cf*ff
            rows.append(dict(mass_kg=mass,family=family,fineness=f,speed_kmh=speed,model=model,Mach=mach,Re=re,cf=cf,FF=ff,body_viscous_drag_N=drag,useful_power_W=drag*u,drag_weight=drag/(mass*G)))
    write_csv('geometrias.csv',hulls);write_csv('barrido_arrastre_APROXIMADO.csv',rows)
    opt=[]
    for mass in [2,5,10]:
     for family in ['esferoide','sears_haack']:
      for speed in [600,1000]:
       for model in ['FF_A','FF_B']:
        subset=[r for r in rows if r['mass_kg']==mass and r['family']==family and r['speed_kmh']==speed and r['model']==model]
        opt.append(min(subset,key=lambda r:r['body_viscous_drag_N']))
    write_csv('minimos_SOLO_modelo.csv',opt)
    mech=[]
    # Eight equal point masses on two axial stations and four azimuths per station.
    # Deployment changes radius only; independent of unresolved axis orientations.
    for mass in [2,5,10]:
     geo=geometry(mass/200,6,'esferoide')
     for fraction in [.1,.2,.3]:
      for rf in [1.5,2.,2.5]:
       mr=mass*fraction;r0=geo['D_m']/2;r1=rf*geo['D_m'];x=.2*geo['L_m']
       # Rest mass split equally between homogeneous skin and a compact solid sphere.
       rest=mass-mr;core_r=.35*geo['D_m'];base_y=.5*rest*geo['shell_Iy_per_kg']+.5*rest*.4*core_r**2
       base_x=.5*rest*geo['shell_Ix_per_kg']+.5*rest*.4*core_r**2
       i0=base_y+mr*(x*x+r0*r0/2);i1=base_y+mr*(x*x+r1*r1/2)
       for torque in [2.,5.,10.]:
        mech.append(dict(mass_kg=mass,module_mass_fraction=fraction,deployed_radius_D=rf,torque_Nm=torque,Iy_stowed=i0,Iy_deployed=i1,Ix_stowed=base_x+mr*r0*r0,Ix_deployed=base_x+mr*r1*r1,ideal_90deg_stowed_s=2*math.sqrt(i0*math.pi/2/torque),ideal_90deg_deployed_s=2*math.sqrt(i1*math.pi/2/torque),time_ratio=math.sqrt(i1/i0)))
    write_csv('mecanismos_inercia_ESCENARIOS.csv',mech)
    force=[]
    for mass in [2,5,10]:
     for ag in [.5,1,2]:
      force.append(dict(mass_kg=mass,acceleration_g=ag,hover_N=mass*G,lateral_resultant_N=mass*G*math.sqrt(1+ag*ag),upward_N=mass*G*(1+ag),isotropic_required_N=mass*G*(1+ag),stop_5ms_time_s=5/(ag*G),stop_5ms_distance_m=25/(2*ag*G),reverse_plus5_minus5_s=10/(ag*G)))
    write_csv('requisitos_fuerza.csv',force)
    hover=[]
    for mass in [2,5,10]:
     for area in [.05,.2,.4]:
      ideal=(mass*G)**1.5/math.sqrt(2*RHO*area)
      for multiplier in [1.5,2.,3.]:
       for seconds in [30,120,300]:
        p=ideal*multiplier;energy=p*seconds/3600
        hover.append(dict(mass_total_kg=mass,effective_area_m2=area,power_multiplier_HYPOTHESIS=multiplier,time_s=seconds,ideal_hover_W=ideal,electric_power_scenario_W=p,energy_Wh=energy,battery_kg_at_200usableWhkg=energy/200))
    write_csv('hover_energia_ESCENARIOS.csv',hover)
    response=[]
    for tau in [.03,.07,.081,.15]:
      response.append(dict(time_constant_s=tau,rise_10_90_s=math.log(9)*tau,time_to90_s=math.log(10)*tau,ideal_reversal_zero_crossing_s=math.log(2)*tau,model='first_order_no_saturation_not_rotor_reversal_validation'))
    write_csv('respuesta_actuador_IDEAL.csv',response)
    # Arithmetic audit of user's pasted report only.
    audit=dict(inertia_reduction=(.0715-.0501)/.0715,ring_wetted_m2=2*math.pi*.245*.230,area_5kg_from_2kg=.322*(5/2)**(2/3),reorientation_5kg_s=2*math.sqrt(.205*math.pi/2/(200*math.sin(math.radians(10))*.62)),reorientation_10kg_s=2*math.sqrt(.610*math.pi/2/(350*math.sin(math.radians(10))*.78)),report_buckling_expression_Pa=.92*60e9*(.001/.131)**2.5*(.131/.786))
    (OUT/'auditoria_aritmetica.json').write_text(json.dumps(audit,indent=2))
    (OUT/'verificacion_numerica.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps(dict(checks=checks,audit=audit,example_minima=[r for r in opt if r['mass_kg']==10 and r['speed_kmh']==1000]),indent=2))
if __name__=='__main__':main()
