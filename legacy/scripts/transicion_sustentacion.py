"""Conditional closed-body screening, NOT a flight/transition simulation.
Allen & Perkins TR1048 eq14: closed pointed body Sb=0; uniform
crossflow coefficient and symmetric planform put viscous resultant at L/2.
No measured coefficients for our aircraft. All SI, sea-level atmosphere.
"""
import csv, json, math, os
from pathlib import Path
from calcular import geometry, G, RHO
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'resultados'
os.environ.setdefault('MPLCONFIGDIR',str(OUT/'mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def loads(mass, f, speed, angle, cross):
    geo=geometry(mass/200, f, 'esferoide',1000)
    a=math.radians(angle); q=.5*RHO*(speed/3.6)**2
    # Eq14 neglects small axial-drag contribution to lift, as original.
    lift=q*cross*geo['side_m2']*math.sin(a)**2*math.cos(a)
    moment=q*geo['volume_m3']*math.sin(2*a)*math.cos(a/2)
    return geo,q,lift,moment

def main():
    rows=[]
    for m in [2,5,10]:
      for f in [4,6,8]:
       for v in [100,200,300,600,1000]:
        for angle in [5,10,15]:
         for cross in [.3,.6,1.2]:
          geo,q,lift,moment=loads(m,f,v,angle,cross)
          rows.append(dict(mass_kg=m,fineness=f,speed_kmh=v,angle_deg=angle,
            crossflow_C_ASSUMED=cross,lift_N=lift,lift_over_weight=lift/(m*G),
            untrimmed_pitch_moment_Nm=moment,q_Pa=q,
            tail_force_magnitude_at_04L_N=abs(moment)/(.4*geo['L_m'])))
    with (OUT/'cuerpo_transicion_SENSIBILIDAD.csv').open('w') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    transition=[]
    for m in [2,5,10]:
      for f in [4,6,8]:
       for cross in [.3,.6,1.2]:
        geo,q,unitlift,_=loads(m,f,1,10,cross)
        speed=math.sqrt(m*G/unitlift)
        _,q,lift,moment=loads(m,f,speed,10,cross)
        assert abs(lift/(m*G)-1)<1e-10
        # Added effective lifting area at CL=.5, body lift ignored.
        wing_area=m*G/(.5*RHO*(150/3.6)**2*.5)
        transition.append(dict(mass_kg=m,fineness=f,crossflow_C_ASSUMED=cross,
          body_only_1g_speed_kmh=speed,moment_at_1g_Nm=moment,
          effective_wing_area_150kmh_CL05_m2=wing_area))
    # Necessary force-only hover support from an arbitrarily orientable jet;
    # does NOT provide omnidirectionality or independent torque control.
    jets=[]
    for m,t in [(2,24),(5,100),(10,100),(10,250)]:
        angle=math.degrees(math.asin(m*G/t)) if t>=m*G else None
        jets.append(dict(mass_kg=m,thrust_ASSUMED_N=t,
                        minimum_axis_elevation_deg=angle))
    checks=dict(count=len(rows),zero_speed=loads(5,6,0,10,.6)[2:]==(0.,0.),
        zero_angle=loads(5,6,100,0,.6)[2:]==(0.,0.),
        speed_squared=abs(loads(5,6,200,10,.6)[2]/loads(5,6,100,10,.6)[2]-4)<1e-12)
    assert all(v for k,v in checks.items() if k!='count')
    output=dict(assumptions='Closed symmetric spheroid; density 200kg/m3; crossflow coefficient is a sensitivity parameter, not measured. No trim/axial drag lift correction/transonic correction.',
      checks=checks,transition=transition,jets_force_only=jets)
    (OUT/'transicion_sustentacion_RESUMEN.json').write_text(json.dumps(output,indent=2))
    fig,axes=plt.subplots(1,2,figsize=(12,5.2))
    for m,color in [(2,'#32936f'),(5,'#1976b8'),(10,'#bc503b')]:
      speeds=list(range(0,401,5))
      vals=[loads(m,6,v,10,.6) for v in speeds]
      axes[0].plot(speeds,[x[2]/(m*G) for x in vals],label=f'{m} kg',color=color)
      axes[1].plot(speeds,[x[3] for x in vals],label=f'{m} kg',color=color)
    axes[0].axhline(1,color='black',ls='--',lw=1,label='Soporte del peso')
    axes[0].set_ylabel('Sustentación / peso (sin compensar)')
    axes[1].set_ylabel('Momento de cabeceo sin compensar (N·m)')
    for ax in axes:
      ax.set_xlabel('Velocidad (km/h)');ax.grid(alpha=.2);ax.legend()
    fig.suptitle('Sensibilidad del huso cerrado: la fuerza no basta para demostrar control',fontsize=13)
    fig.text(.5,.015,'Hipótesis: L/D = 6 · incidencia 10° · C transversal = 0,6 · densidad media 200 kg/m³. No son datos de vuelo.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.94));fig.savefig(OUT/'transicion_sustentacion.png',dpi=170);plt.close(fig)
    selected=[r for r in rows if r['fineness']==8 and r['angle_deg']==10 and r['speed_kmh']==1000]
    print(json.dumps(dict(checks=checks,highspeed=selected,transition_f6=[r for r in transition if r['fineness']==6],jets=jets),indent=2))
if __name__=='__main__':main()
