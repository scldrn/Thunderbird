"""1D inlet sizing and thrust bookkeeping. No installed engine performance map.
Published static mass flows held fixed in one sensitivity; constant corrected
flow used in another. Neither is a measured flight operating line.
"""
import math,json,csv
from calcular import RHO,TEMP
from trimado_superficies import OUT,hull
P0=101325.;R=287.05;GAMMA=1.4
ENGINES=[dict(name='P20-SX_reference',massflow=.05,static_thrust=24,mass=2,
 url='https://www.jetcat.de/changelang/de/en/productdetails/produkte/jetcat/produkte/Eingestellte%20Produkte%20Zubehoer/p20_sx'),
 dict(name='P100-RX-BL',massflow=.23,static_thrust=100,mass=5,
 url='https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/RC%20ENGINES/Engines/p100_rx-bl'),
 dict(name='P250-Pro-S_legacy_reference',massflow=.47,static_thrust=250,mass=10,
 url='https://www.jetcat.de/de/productdetails/produkte/jetcat/produkte/Eingestellte%20Produkte%20Zubehoer/p250%20pro%20s')]

def flux(pt,tt,mach):
 return pt/math.sqrt(tt)*math.sqrt(GAMMA/R)*mach*(1+.2*mach*mach)**(-3)

def main():
    prior=json.loads((OUT/'comparacion_integrada_RESUMEN.json').read_text())['selected_f6']
    rows=[];requirements=[]
    for engine in ENGINES:
     geo=hull(engine['mass'],6)
     for speed in [0,150,600,1000]:
      v=speed/3.6;mach=v/math.sqrt(GAMMA*R*TEMP)
      tau=1+.2*mach*mach;tt=TEMP*tau;ptideal=P0*tau**3.5
      for recovery in [.90,.95,1.]:
       pt=ptideal*recovery
       for flowmodel in ['fixed_published_flow','constant_corrected_flow']:
        mdot=engine['massflow'] if flowmodel=='fixed_published_flow' else engine['massflow']*(pt/P0)/math.sqrt(tt/TEMP)
        for face in [.15,.25,.4]:
         area=mdot/flux(pt,tt,face);critical=mdot/flux(pt,tt,1)
         assert area>=critical
         assert abs(area*flux(pt,tt,face)/mdot-1)<1e-12
         core=.5*geo['D_m'];annulus_outer=math.sqrt(core*core+4*area/math.pi)
         capture=mdot/(RHO*v) if speed else None
         rows.append(dict(engine=engine['name'],mass_kg=engine['mass'],speed_kmh=speed,
          freestream_Mach=mach,recovery_ASSUMED=recovery,flow_model=flowmodel,air_massflow_kgs=mdot,
          duct_Mach_ASSUMED=face,total_pressure_Pa=pt,total_temperature_K=tt,
          flow_area_m2=area,circular_equivalent_diameter_mm=math.sqrt(4*area/math.pi)*1000,
          critical_area_m2=critical,area_over_critical=area/critical,
          capture_streamtube_area_m2=capture,
          capture_streamtube_diameter_mm=math.sqrt(4*capture/math.pi)*1000 if capture else None,
          core_diameter_ASSUMED_mm=core*1000,annulus_outer_diameter_mm=annulus_outer*1000,
          annulus_gap_mm=(annulus_outer-core)*500,
          ram_momentum_term_N=mdot*v,
          net_thrust_IF_gross_unchanged_N=engine['static_thrust']-mdot*v))
        if speed in [600,1000]:
         aero=next(r for r in prior if r['mass_kg']==engine['mass'])
         requirements.append(dict(engine=engine['name'],mass_kg=engine['mass'],speed_kmh=speed,
          recovery_ASSUMED=recovery,flow_model=flowmodel,
          gross_required_partial_low_N=aero[f'drag_partial_low_{speed}_N']+mdot*v,
          gross_required_partial_high_N=aero[f'drag_partial_high_{speed}_N']+mdot*v,
          static_thrust_reference_N=engine['static_thrust']))
    for name,data in [('tomas_dimensionamiento_CONDICIONAL.csv',rows),('empuje_bruto_requerido_CONDICIONAL.csv',requirements)]:
      with (OUT/name).open('w') as file:
       w=csv.DictWriter(file,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    # Ideal mass flux peaks at Mach1, checked on both sides.
    assert flux(P0,TEMP,1)>flux(P0,TEMP,.99) and flux(P0,TEMP,1)>flux(P0,TEMP,1.01)
    result=dict(engine_references=ENGINES,duct_cases=len(rows),thrust_cases=len(requirements),
      selected=[r for r in rows if r['speed_kmh'] in [0,1000] and r['recovery_ASSUMED']==.95 and r['duct_Mach_ASSUMED']==.25 and r['flow_model']=='fixed_published_flow'],
      selected_requirements=[r for r in requirements if r['speed_kmh']==1000 and r['recovery_ASSUMED']==.95 and r['flow_model']=='fixed_published_flow'],
      limitations='No pressure distortion, boundary layer, lip/spillage drag, duct friction/bends, bleed, cooling, compressor map, combustion, nozzle or installed engine matching. Gross constant is sensitivity, not prediction.')
    (OUT/'tomas_y_empuje_RESUMEN.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
