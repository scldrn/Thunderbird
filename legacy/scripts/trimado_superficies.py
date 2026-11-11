"""Conditional two-plane aerodynamic trim and surface deployment screening.
No wing-body interference, transonic correction, rotor inflow or flutter model.
Areas S refer to ONE plane's exposed pair; cruciform physical total is 2*S.
"""
import csv,json,math,os
from functools import lru_cache
from pathlib import Path
from scipy.optimize import brentq
from calcular import geometry,G,RHO
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
os.environ.setdefault('MPLCONFIGDIR',str(OUT/'mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

@lru_cache(maxsize=256)
def hull(mass,f):
    return geometry(mass/200,f,'esferoide',500)

def trim(mass,f,sw,st,speed,n=1,a_slope=3,cross=.6):
    geo=hull(mass,f)
    q=.5*RHO*(speed/3.6)**2;arm=.4*geo['L_m'];target=n*mass*G
    def components(alpha):
        lb=q*cross*geo['side_m2']*math.sin(alpha)**2*math.cos(alpha)
        mb=q*geo['volume_m3']*math.sin(2*alpha)*math.cos(alpha/2)
        lw=q*sw*a_slope*alpha
        lt=mb/(arm*math.cos(alpha))
        return lb,lw,lt,mb
    if sum(components(math.radians(60))[:3])<target:
        return dict(mass_kg=mass,fineness=f,speed_kmh=speed,load_factor=n,
            wing_oneplane_m2=sw,tail_oneplane_m2=st,
            within_ASSUMED_limits=False,status='no_root_in_0_to_60deg')
    alpha=brentq(lambda a:sum(components(a)[:3])-target,0,math.radians(60))
    lb,lw,lt,mb=components(alpha)
    clt=lt/(q*st);clw=a_slope*alpha if sw else 0.
    delta=clt/a_slope-alpha
    # Tail vertical lift moment arm; ignore force-drag moment coupling.
    force_error=lb+lw+lt-target;moment_error=mb-lt*arm*math.cos(alpha)
    assert abs(force_error)<1e-6 and abs(moment_error)<1e-6
    # Normalization by q rather than arbitrary reference area.
    # Fixed-control local derivative: body destabilizing, tail stabilizing.
    h=1e-6
    def moment_fixed(a):
        b=q*geo['volume_m3']*math.sin(2*a)*math.cos(a/2)
        t=q*st*a_slope*(a+delta)
        return b-arm*t*math.cos(a)
    dm=(moment_fixed(alpha+h)-moment_fixed(alpha-h))/(2*h)
    # Drag is surface-only sensitivity; zero-lift profile for both planes.
    # Only one plane lifting in this pitch trim; idle plane still has profile drag.
    ar=2.;eff=.7;cd0=.012
    drag_profile=q*2*(sw+st)*cd0
    drag_induced=(lw*lw/(q*sw*math.pi*ar*eff) if sw else 0)+lt*lt/(q*st*math.pi*ar*eff)
    return dict(status='root_found_not_validation',mass_kg=mass,fineness=f,speed_kmh=speed,load_factor=n,
        wing_oneplane_m2=sw,tail_oneplane_m2=st,alpha_deg=math.degrees(alpha),
        tail_delta_deg=math.degrees(delta),wing_CL=clw,tail_CL=clt,
        body_lift_N=lb,wing_lift_N=lw,tail_lift_N=lt,body_moment_Nm=mb,
        fixed_control_pitch_derivative_Nm_per_rad=dm,
        stable_pitch_model=dm<0,
        within_ASSUMED_limits=abs(math.degrees(alpha))<=10 and abs(math.degrees(delta))<=15 and abs(clw)<=.8 and abs(clt)<=.8,
        surface_profile_drag_N=drag_profile,surface_induced_drag_N=drag_induced,
        surface_drag_N=drag_profile+drag_induced,
        max_equilibrium_residual=max(abs(force_error),abs(moment_error)))

def mechanism(mass,f,sw,st,areal):
    geo=geometry(mass/200,f,'esferoide',500);r0=geo['D_m']/2
    out=dict(mass_kg=mass,fineness=f,areal_mass_ASSUMED_kgm2=areal,
             panel_mass_kg=0.,added_pitch_inertia_kgm2=0.,added_roll_inertia_kgm2=0.)
    for kind,s,x in [('wing',sw,0),('tail',st,.4*geo['L_m'])]:
        if s==0:continue
        # Four rectangular fins; exposed-pair equivalent aspect ratio 2.
        h=math.sqrt(2*s)/2;c=s/(2*h);mp=2*s*areal
        mean_r2=r0*r0+r0*h+h*h/3
        # Hypothetical folded mass at r0, same axial station: ignores actual linkage.
        dix=mp*(mean_r2-r0*r0);diy=dix/2
        out['panel_mass_kg']+=mp;out['added_pitch_inertia_kgm2']+=diy
        out['added_roll_inertia_kgm2']+=dix
        out[kind+'_semispan_exposed_m']=h;out[kind+'_chord_m']=c
        out[kind+'_outer_diameter_m']=2*(r0+h)
        # Full normal pressure differential 1*q47kPa on each panel, not a flight prediction.
        qmax=.5*RHO*(1000/3.6)**2
        out[kind+'_single_panel_hinge_Nm_at_deltaCp1']=qmax*(s/2)*h/2
    return out

def main():
    rows=[];mechanisms=[]
    configs={'solo_cola':(0,.04),'cruz_compacta':(.04,.04),'cruz_mayor':(.09,.04)}
    for m in [2,5,10]:
      scale=(m/5)**(2/3)
      for f in [4,6,8]:
       for name,(sw0,st0) in configs.items():
        sw,st=sw0*scale,st0*scale
        for v in [100,150,200,250,300,600,1000]:
         for n in [1,2,5,10,20]:
          rows.append(dict(config=name,**trim(m,f,sw,st,v,n)))
        for areal in [.5,1,2]:
          mechanisms.append(dict(config=name,**mechanism(m,f,sw,st,areal)))
    for name,data in [('trimado_superficies_CONDICIONAL.csv',rows),('mecanismos_superficies_CONDICIONAL.csv',mechanisms)]:
      fields=list(dict.fromkeys(k for r in data for k in r))
      with (OUT/name).open('w') as file:
       writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader();writer.writerows(data)
    schedules=[];slope_sensitivity=[]
    for m in [2,5,10]:
      scale=(m/5)**(2/3);sw0=.09*scale;st=.04*scale
      endpoint=brentq(lambda v:trim(m,6,0,st,v)['alpha_deg']-8,180,400)
      for v in range(150,401,10):
        if trim(m,6,sw0,st,v)['alpha_deg']>8:
          schedules.append(dict(mass_kg=m,speed_kmh=v,status='full_area_insufficient_for_8deg'))
          continue
        if trim(m,6,0,st,v)['alpha_deg']<=8:sw=0.
        else:sw=brentq(lambda area:trim(m,6,area,st,v)['alpha_deg']-8,0,sw0)
        r=trim(m,6,sw,st,v)
        schedules.append(dict(mass_kg=m,speed_kmh=v,status='algebraic_trim_only',
            wing_oneplane_m2=sw,wing_fraction=sw/sw0,alpha_deg=r['alpha_deg'],
            complete_reduction_speed_kmh=endpoint,
            within_ASSUMED_limits=r['within_ASSUMED_limits']))
      for slope in [2,3,4]:
        slope_sensitivity.append(dict(slope_per_rad=slope,
            **trim(m,6,sw0,st,150,a_slope=slope)))
    summary=dict(count=len(rows),mechanism_cases=len(mechanisms),
       max_residual=max(r.get('max_equilibrium_residual',0) for r in rows),
       no_root=sum(r['status']=='no_root_in_0_to_60deg' for r in rows),
       selected=[r for r in rows if r['mass_kg'] in [5,10] and r['fineness']==6 and r['load_factor']==1 and r['speed_kmh'] in [150,1000]],
       mechanisms=[r for r in mechanisms if r['mass_kg']==5 and r['fineness']==6 and r['areal_mass_ASSUMED_kgm2']==1],
       area_schedules=schedules,slope_sensitivity=slope_sensitivity)
    (OUT/'trimado_superficies_RESUMEN.json').write_text(json.dumps(summary,indent=2))
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    colors=['#597081','#e49b25','#227c9d']
    for (name,(sw,st)),color in zip(configs.items(),colors):
      vs=list(range(100,1001,10));rs=[trim(5,6,sw,st,v) for v in vs]
      valid=[r['within_ASSUMED_limits'] for r in rs]
      axes[0].plot(vs,[r['alpha_deg'] if ok else math.nan for r,ok in zip(rs,valid)],label=name.replace('_',' '),color=color)
      axes[0].plot(vs,[r['alpha_deg'] if not ok else math.nan for r,ok in zip(rs,valid)],ls=':',color=color)
      axes[1].plot(vs,[r['surface_drag_N'] if ok else math.nan for r,ok in zip(rs,valid)],color=color)
      axes[1].plot(vs,[r['surface_drag_N'] if not ok else math.nan for r,ok in zip(rs,valid)],ls=':',color=color)
    axes[0].axhline(10,ls='--',color='black',lw=1,label='Límite de estudio: 10°')
    axes[0].set_ylabel('Incidencia para equilibrar peso y momento (°)')
    axes[1].set_ylabel('Arrastre estimado de superficies (N)')
    for ax in axes:ax.set_xlabel('Velocidad (km/h)');ax.grid(alpha=.2)
    axes[0].legend();fig.suptitle('5 kg · L/D 6 · vuelo recto: beneficio y coste de añadir superficies')
    fig.text(.5,.015,'Punteado: fuera de límites supuestos. Sin interferencia ni corrección transónica. Arrastre solo de superficies.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.94));fig.savefig(OUT/'trimado_superficies.png',dpi=160);plt.close(fig)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
