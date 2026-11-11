"""Documented hardware screening and schematic, not construction drawings."""
import os,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
os.environ['MPLCONFIGDIR']=str(OUT/'mpl-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse,Rectangle,Circle
from cierre_masa import calc,TECH
from familia import ENGINES
from control import guaranteed_force
r,d=calc(5,.3,2,1,30,.5,TECH['optimista_no_verificada'],True,ENGINES['P100-RX-BL'],4,.5)
peak=r['power_peak_upper_W'];packs=[]
for series in [6,12]:
 for current in [40,60]:
  parallel=math.ceil(peak/(series*3.0*current));n=series*parallel
  packs.append(dict(series=series,parallel=parallel,cell_current_A=current,loaded_voltage_per_cell_assumed=3.,cell_mass_kg=n*.071,pack_mass_assumed_kg=n*.071*1.15,cells=n,nominal_Wh=n*18))
L=d['L'];D=L/4;rotor=.4572;positions=np.array(d['positions'])
clear=min(np.linalg.norm(a-b) for i,a in enumerate(positions) for b in positions[i+1:])-rotor
F=guaranteed_force(np.array(d['B']),L,4.1*9.80665,2*np.linalg.eigvalsh(np.array(d['J']))[-1])
result=dict(previous_peak_W=peak,previous_motor_limits_N=d['limits'],packs=packs,engine_motor_fuel_cells_subtotal_kg=1.08+8*.128+.156+36*.071,optimistic_total_replacing_only_battery_kg=r['equilibrium_mass_kg']-r['battery_kg']+36*.071*1.15,rotor_diameter_m=rotor,pair_sphere_clearance_m=clear,deployed_radial_envelope_m=4*D+rotor,ideal_symmetric_thrust_only_acceleration_g=F/(r['equilibrium_mass_kg']*9.80665)-1,warning='No reverse-thrust evidence. Battery power frozen at old value; not a new equilibrium.')
(OUT/'componentes_5kg.json').write_text(json.dumps(result,indent=2))
fig,axs=plt.subplots(1,2,figsize=(13,7),gridspec_kw={'width_ratios':[1.2,1]})
a=axs[0];a.add_patch(Ellipse((0,0),L,D,fc='#e4edf3',ec='#243c50',lw=2))
for x in [-.2*L,.2*L]:
 for y in [-2*D/np.sqrt(2),2*D/np.sqrt(2)]:
  a.plot([x,x],[np.sign(y)*D/2,y],color='#536d7c',lw=3)
  a.add_patch(Circle((x,y),rotor/2,fill=False,ec='#d07135',ls='--'))
  a.plot(x,y,'o',color='#243c50')
a.text(0,.06,'Cuerpo 91 × 23 cm',ha='center',fontsize=10)
a.add_patch(Rectangle((.27*L-.241/2,-.097/2),.241,.097,fc='#c96656',alpha=.8))
a.text(.27*L,0,'Reactor',ha='center',fontsize=9)
a.text(-.21,-.05,'Zona central:\nbatería + depósito',ha='center',fontsize=9)
a.set_title('Vista superior · envolventes de rotores',fontsize=12)
a.text(0,-.72,'8 rotores: pares superpuestos en esta proyección.\nCírculos = envolventes; no planos reales de las hélices.\nSolapamiento proyectado no prueba colisión 3D.',ha='center',fontsize=10)
a.set_xlim(-.65,.65);a.set_ylim(-.85,.65);a.set_aspect('equal');a.set_xlabel('Metros');a.set_ylabel('Metros');a.grid(alpha=.15)
b=axs[1];b.add_patch(Circle((0,0),D/2,fc='#e4edf3',ec='#243c50',lw=2));b.add_patch(Circle((0,0),rotor/2,fill=False,ec='#d07135',ls='--',lw=2))
b.text(0,.27,'Sección del cuerpo: Ø23 cm\nRotor: Ø46 cm',ha='center',fontsize=12)
b.text(0,-.32,'No cabe transversalmente sin plegar.\nInclinarlo no resuelve por sí solo el empaquetado.\nPalas, brazos y bujes requieren mecanismos propios.',ha='center',fontsize=10)
b.set_xlim(-.4,.4);b.set_ylim(-.5,.45);b.set_aspect('equal');b.axis('off')
fig.suptitle('Versión de 5 kg · auditoría de espacio y componentes',fontsize=16)
fig.text(.5,.025,'Esquema de investigación: no valida retracción, conductos, resistencia ni vuelo.',ha='center',fontsize=11,color='#a33e30')
fig.tight_layout(rect=[0,.06,1,.94]);fig.savefig(OUT/'distribucion_5kg_preliminar.png',dpi=170)
assert result['engine_motor_fuel_cells_subtotal_kg']>4.8
print(json.dumps(result,indent=2))
