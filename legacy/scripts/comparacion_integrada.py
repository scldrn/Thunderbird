"""Finite-domain sizing under assumed coefficient uncertainty, not global optimum.
Choose tail for 20% restoring derivative excess at zero alpha, worst slope=2.
Choose central wing for alpha<=8deg at150km/h, worst slope/crossflow corner.
Body and surface drag are incomplete screening models, not measured total drag.
"""
import math,json,csv
from scipy.optimize import brentq
from calcular import G,RHO,MU,TEMP
from trimado_superficies import trim,hull,mechanism,OUT

def body_drag(geo,v):
    u=v/3.6;mach=u/math.sqrt(1.4*287.05*TEMP);re=RHO*u*geo['L_m']/MU
    cf=.455/math.log10(re)**2.58/(1+.144*mach*mach)**.65
    f=geo['L_m']/geo['D_m'];q=.5*RHO*u*u
    return [q*geo['wet_m2']*cf*ff for ff in [1+1.5/f**1.5+7/f**3,1+60/f**3+.0025*f]]

def main():
    rows=[];corners=[]
    for m in [2,5,10]:
      for i in range(33):
        f=4+i*.25;geo=hull(m,f);arm=.4*geo['L_m']
        st=1.2*2*geo['volume_m3']/(arm*2.)
        # For central CG wing, weakest slope and crossflow maximize needed area.
        fun=lambda sw:trim(m,f,sw,st,150,a_slope=2,cross=.3)['alpha_deg']-8
        sw=0. if fun(0)<=0 else brentq(fun,0,2.)
        mech=mechanism(m,f,sw,st,1.)
        # Explicit structural proxies at areal mass1kg/m2; no actuators/core.
        shellmass=geo['wet_m2']
        proxy_iy=shellmass*geo['shell_Iy_per_kg']
        for area,x in [(sw,0),(st,arm)]:
            if area:
                h=math.sqrt(2*area)/2;c=area/(2*h);r=geo['D_m']/2
                proxy_iy+=2*area*(x*x+c*c/12+(r*r+r*h+h*h/3)/2)
        vals=[]
        for slope in [2,3,4]:
         for cross in [.3,.6,1.2]:
          for v,n,area in [(150,1,sw),(600,1,0),(1000,1,0),(1000,10,0),(1000,20,0)]:
            r=trim(m,f,area,st,v,n,a_slope=slope,cross=cross)
            r['slope_ASSUMED']=slope;r['cross_ASSUMED']=cross
            # Equality at8deg is expected; generic model limit is10deg.
            r['passes_static_filter']=r.get('within_ASSUMED_limits',False) and r.get('stable_pitch_model',False)
            vals.append(r);corners.append(r)
        limits={}
        for v in [600,1000]:
            subset=[r for r in vals if r['speed_kmh']==v and r['load_factor']==1]
            bd=body_drag(geo,v)
            # Profile uncertainty .006-.020; induced as prior AR/e model.
            q=.5*RHO*(v/3.6)**2
            dmin=min(bd)+min(r['surface_induced_drag_N'] for r in subset)+q*2*st*.006
            dmax=max(bd)+max(r['surface_induced_drag_N'] for r in subset)+q*2*st*.020
            limits[f'drag_partial_low_{v}_N']=dmin;limits[f'drag_partial_high_{v}_N']=dmax
        endpoint=brentq(lambda v:trim(m,f,0,st,v,a_slope=2,cross=.3).get('alpha_deg',60)-8,100,600)
        rows.append(dict(mass_kg=m,fineness=f,L_m=geo['L_m'],D_m=geo['D_m'],
            wing_oneplane_m2=sw,tail_oneplane_m2=st,
            panel_mass_ASSUMED_kg=mech['panel_mass_kg'],
            skin_plus_panel_mass_PROXY_kg=shellmass+mech['panel_mass_kg'],
            deployed_skin_panel_pitch_inertia_PROXY_kgm2=proxy_iy,
            added_pitch_inertia_kgm2=mech['added_pitch_inertia_kgm2'],
            added_roll_inertia_kgm2=mech['added_roll_inertia_kgm2'],
            area_zero_threshold_kmh=endpoint,
            passes_all_1g_corners=all(r['passes_static_filter'] for r in vals if r['load_factor']==1),
            passes_10g_corners=all(r['passes_static_filter'] for r in vals if r['load_factor']==10),
            passes_20g_corners=all(r['passes_static_filter'] for r in vals if r['load_factor']==20),
            **limits))
    for name,data in [('comparacion_integrada_CONDICIONAL.csv',rows),('comparacion_integrada_ESQUINAS.csv',corners)]:
        fields=list(dict.fromkeys(k for r in data for k in r))
        with (OUT/name).open('w') as file:
          writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader();writer.writerows(data)
    # Pareto only in defined sampled domain; incomplete structural proxies.
    pareto=[]
    for r in rows:
      peers=[p for p in rows if p['mass_kg']==r['mass_kg'] and p['passes_all_1g_corners']]
      keys=['drag_partial_high_1000_N','skin_plus_panel_mass_PROXY_kg','deployed_skin_panel_pitch_inertia_PROXY_kgm2']
      dominated=any(all(p[k]<=r[k] for k in keys) and any(p[k]<r[k] for k in keys) for p in peers)
      if r['passes_all_1g_corners'] and not dominated:pareto.append(r)
    summary=dict(geometry_count=len(rows),corner_count=len(corners),
      selected_f6=[r for r in rows if r['fineness']==6],pareto=pareto,
      lowest_partial_drag=[min([r for r in rows if r['mass_kg']==m],key=lambda r:r['drag_partial_high_1000_N']) for m in [2,5,10]],
      note='No intake/base/wave/interference/propulsion or mass closure. Tail sizing is static, not robust dynamic control. No global optimum claim.')
    (OUT/'comparacion_integrada_RESUMEN.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
