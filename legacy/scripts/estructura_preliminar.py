"""Linear tapered Euler-Bernoulli half-body beam + independent flat-bay study.
Neither a shell FE model nor a buckling/flutter/strength certification.
All material constants are hypothetical isotropic properties, not design allowables.
"""
import math,json,csv
import numpy as np
from scipy.linalg import eigh,solve
from trimado_superficies import hull,OUT
from calcular import G,RHO
E=70e9;DENSITY=2700.;ALLOWABLE=100e6

def beam(m,f,fraction,t,n=60,uniform=False):
    geo=hull(m,f);half=geo['L_m']/2;rmax=geo['D_m']/2
    dx=half/n;mu=fraction*m/geo['L_m']
    k=np.zeros((2*(n+1),)*2);mm=k.copy();force=np.zeros(len(k));radii=[]
    for i in range(n):
        x=(i+.5)*dx;r=rmax if uniform else rmax*math.sqrt(1-(x/half)**2)
        radii.append(r);I=math.pi*r**3*t
        ke=E*I/dx**3*np.array([[12,6*dx,-12,6*dx],[6*dx,4*dx**2,-6*dx,2*dx**2],[-12,-6*dx,12,-6*dx],[6*dx,2*dx**2,-6*dx,4*dx**2]])
        me=mu*dx/420*np.array([[156,22*dx,54,-13*dx],[22*dx,4*dx**2,13*dx,-3*dx**2],[54,13*dx,156,-22*dx],[-13*dx,-3*dx**2,-22*dx,4*dx**2]])
        idx=np.arange(2*i,2*i+4);k[np.ix_(idx,idx)]+=ke;mm[np.ix_(idx,idx)]+=me
        force[idx]+=mu*dx/12*np.array([6,dx,6,-dx]) # unit acceleration 1m/s2
    disp=solve(k[2:,2:],force[2:],assume_a='pos')
    eig=eigh(k[2:,2:],mm[2:,2:],subset_by_index=[0,0])[0][0]
    # Uniform inertial line load; equilibrium moment does not depend on stiffness.
    x=(np.arange(n)+.5)*dx;mom=mu*(half-x)**2/2
    stress=mom/(math.pi*np.array(radii)**2*t)
    return dict(tip_m_per_ms2=float(disp[-2]),peak_stress_Pa_per_ms2=float(max(stress)),
                frequency_Hz=math.sqrt(eig)/(2*math.pi),shell_mass_kg=geo['wet_m2']*DENSITY*t,
                length_m=geo['L_m'])

def main():
    # Verify discretization against prismatic cantilever analytical solution.
    ref=beam(5,6,.6,.0005,80,True);geo=hull(5,6);l=geo['L_m']/2
    mu=.6*5/geo['L_m'];I=math.pi*(geo['D_m']/2)**3*.0005
    delta=mu*l**4/(8*E*I);freq=1.8751040687**2/(2*math.pi*l*l)*math.sqrt(E*I/mu)
    checks=dict(prismatic_deflection_rel=abs(ref['tip_m_per_ms2']/delta-1),prismatic_frequency_rel=abs(ref['frequency_Hz']/freq-1))
    a=beam(5,6,.6,.0005,60);b=beam(5,6,.6,.0005,120)
    checks['taper_refinement_deflection_rel']=abs(a['tip_m_per_ms2']/b['tip_m_per_ms2']-1)
    checks['taper_refinement_frequency_rel']=abs(a['frequency_Hz']/b['frequency_Hz']-1)
    assert checks['prismatic_deflection_rel']<1e-5 and checks['prismatic_frequency_rel']<1e-5
    assert checks['taper_refinement_deflection_rel']<.005 and checks['taper_refinement_frequency_rel']<.005
    rows=[]
    for m in [2,5,10]:
     for f in [4,6,8,12]:
      for fraction in [.3,.6,1.]:
       base=beam(m,f,fraction,.0005)
       for t in [.0002,.0005,.001]:
        ratio=t/.0005
        for gload in [5,10,20]:
         acc=gload*G;stress=base['peak_stress_Pa_per_ms2']*acc/ratio
         tip=base['tip_m_per_ms2']*acc/ratio;shellmass=base['shell_mass_kg']*ratio
         rows.append(dict(mass_kg=m,fineness=f,distributed_mass_fraction=fraction,thickness_mm=t*1000,
           acceleration_g=gload,stress_MPa=stress/1e6,tip_deflection_mm=tip*1000,
           frequency_central_clamp_Hz=base['frequency_Hz']*math.sqrt(ratio),shell_mass_kg=shellmass,
           shell_mass_consistent_with_distributed_budget=shellmass<=fraction*m,
           below_ASSUMED_100MPa=stress<=ALLOWABLE,below_ASSUMED_05percent_length=tip<=.005*base['length_m']))
    pressure=[];q=.5*RHO*(1000/3.6)**2
    for cp in [.05,.2,1.]:
     for span in [.02,.05,.1]:
      for t in [.0002,.0005,.001]:
       p=cp*q;stress=.75*p*span**2/t**2;deflect=5*p*span**4/(32*E*t**3)
       pressure.append(dict(deltaCp_ASSUMED=cp,pressure_Pa=p,bay_span_mm=span*1000,thickness_mm=t*1000,
          flat_strip_stress_MPa=stress/1e6,flat_strip_deflection_mm=deflect*1000,
          deflection_over_thickness=deflect/t,
          small_deflection_filter=deflect/t<.5))
    for name,data in [('estructura_viga_CONDICIONAL.csv',rows),('estructura_panel_presion_CONDICIONAL.csv',pressure)]:
     with (OUT/name).open('w') as file:
      w=csv.DictWriter(file,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    result=dict(checks=checks,beam_cases=len(rows),panel_cases=len(pressure),
       selected=[r for r in rows if r['mass_kg']==5 and r['distributed_mass_fraction']==.6 and r['thickness_mm']==.5 and r['acceleration_g']==20],
       panel_selected=[r for r in pressure if r['thickness_mm']==.5 and r['bay_span_mm']==50],
       limitations='Central clamp is an inertial-load-path idealization; frequency is NOT a free-flight mode. Uniform mass includes shell. No local shell buckling, joints, openings, aerodynamic stiffness/damping or flutter.')
    (OUT/'estructura_preliminar_RESUMEN.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
