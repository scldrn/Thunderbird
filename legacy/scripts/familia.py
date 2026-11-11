"""Independent size/engine screening. Conditional models, not validated designs."""
import csv,json,math
from cierre_masa import calc,TECH,OUT
from calcular import geometry,RHO
ENGINES={
'P20-SX_referencia_descatalogada':dict(mass=.350,fuel_kg_min=.09*.8,diameter=.060,length=.171,thrust=24),
'P100-RX-BL':dict(mass=1.080,fuel_kg_min=.390*.8,diameter=.097,length=.241,thrust=100),
'P250_referencia':dict(mass=2.155,fuel_kg_min=.820*.8,diameter=.121,length=.323,thrust=250)}
def main():
 rows=[]
 for target in [2.,5.,10.]:
  for name,spec in ENGINES.items():
   for tech in TECH.values():
    for fineness in [4.,6.,8.]:
     for diameter in [.2,.3,.4]:
      for ag in [.5,1.]:
       r,d=calc(target,diameter,2.,ag,30.,.5,tech,True,spec,fineness,extra_mass=.1*target)
       geo=geometry(target/200,fineness,'esferoide',n=400)
       L,D=geo['L_m'],geo['D_m'];end=.27*L+spec['length']/2
       localD=D*math.sqrt(max(0,1-(2*end/L)**2))
       fit=localD>=spec['diameter']+.02 # assumed radial 10mm allowance, no duct validation
       r.update(engine_name=name,fineness=fineness,L_m=L,D_m=D,extra_allowance_kg=.1*target,engine_envelope_fit=fit)
       for speed in [600,1000]:
        u=speed/3.6;re=1.225*u*L/1.7894e-5;ma=u/340.294
        cf=.455/math.log10(re)**2.58/(1+.144*ma*ma)**.65
        ff=max(1+1.5/fineness**1.5+7/fineness**3,1+60/fineness**3+.0025*fineness)
        drag=.5*RHO*u*u*geo['wet_m2']*cf*ff
        r[f'viscous_only_drag_{speed}_N']=drag
        r[f'static_thrust_over_viscous_drag_{speed}']=spec['thrust']/drag
       r['conditional_mass_geometry_pass']=r['mass_within_target'] and r['clearance_sufficient'] and fit
       rows.append(r)
 with (OUT/'familia_ESCENARIOS.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 selected=[]
 for target in [2.,5.,10.]:
  for tech in TECH:
   for ag in [.5,1.]:
    subset=[r for r in rows if r['target_kg']==target and r['technology']==tech and r['requested_acceleration_g']==ag and r['conditional_mass_geometry_pass']]
    # Screening preference, NOT high-speed feasibility: static thrust >=1.5x viscous-only estimate at600.
    screened=[r for r in subset if r['static_thrust_over_viscous_drag_600']>=1.5]
    best=min(screened,key=lambda r:r['equilibrium_mass_kg']) if screened else None
    selected.append(dict(target=target,technology=tech,ag=ag,passing=len(subset),screened=len(screened),candidate=best))
 (OUT/'familia_SELECCION_CONDICIONAL.json').write_text(json.dumps(selected,indent=2))
 print(json.dumps(selected,indent=2))
if __name__=='__main__':main()
