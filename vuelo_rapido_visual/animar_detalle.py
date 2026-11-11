from pathlib import Path
import numpy as np,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
import cadquery as cq
P=Path(__file__).resolve().parent;frames=P/'frames';frames.mkdir(exist_ok=True)
if (P/'malla_cerrada.npz').exists():
 cache=np.load(P/'malla_cerrada.npz');tri=cache['triangles'];colors=cache['colors']
else:
 cache=np.load(P.parent/'simulacion_vuelo_A/malla_visual.npz');tri=cache['triangles'];colors=cache['colors']
 # Close all eight ports using the actual A06 cover solids, stationary in the body frame.
 extra=[];cc=[]
 for s,n,l,c in cq.Assembly.load(str(P.parent/'modelos_integrados/producto_A06/5kg/A06_integrado.step')):
  n=n.split('/')[-1]
  if not n.startswith('compuerta_'):continue
  v,f=s.moved(l).tessellate(.5,angularTolerance=.25);v=np.array([a.toTuple() for a in v])/1000;tt=v[np.array(f)];extra.extend(tt)
  normal=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12);shade=.55+.45*np.abs(normal@np.array([.2,-.5,.84]));cc.extend(np.array([.38,.40,.43])[None,:]*shade[:,None])
 tri=np.concatenate([tri,np.array(extra)]);colors=np.concatenate([colors,np.array(cc)]);np.savez_compressed(P/'malla_cerrada.npz',triangles=tri,colors=colors)
colors=np.clip(colors*1.15,0,1)
plt.rcParams.update({'text.color':'#edf2f7','axes.labelcolor':'#c5d4df','xtick.color':'#aabacc','ytick.color':'#aabacc','font.size':10,'axes.edgecolor':'#506078'})
fps=15;total=0
for speed in (600,1000):
 d=np.load(P/f'{speed}kmh.npz');t=d['time'];pos=d['position'];bank=d['bank_deg'];N=d['normal_force'];load=d['load_factor']
 fig=plt.figure(figsize=(19.2,10.8),dpi=100,facecolor='#0b1017');ax=fig.add_axes([-.1,.10,.93,.77],projection='3d',facecolor='#0b1017');ax.set(xlim=(-.72,.72),ylim=(-.41,.41),zlim=(-.37,.37));ax.set_box_aspect([1.44,.82,.74],zoom=1.15);ax.set_axis_off()
 model=Poly3DCollection(tri,facecolors=colors,edgecolors='none',zsort='average');ax.add_collection3d(model)
 fig.text(.035,.93,f'{speed} km/h',fontsize=39,weight='bold');fig.text(.035,.88,'VENTILADORES INTERNOS  /  INSPECCIÓN DEL CAD',fontsize=17,color='#b5c6d9')
 fig.text(.035,.835,'Cámara ligada a la velocidad con órbita de inspección · tapas cerradas',fontsize=12,color='#8aa1b8')
 phase=fig.text(.75,.89,'',fontsize=16,color='#ffb454');tele=fig.text(.035,.14,'',fontsize=16);fig.text(.035,.062,'ESCENARIO DE DEMANDA INVERSA · TRAYECTORIA IMPUESTA · PRESTACIONES NO VALIDADAS',fontsize=15,color='#f3b2a5',weight='bold')
 fig.text(.035,.025,'Las fuerzas indicadas son las que harían falta. No se ha demostrado que este vehículo pueda producirlas.',fontsize=13,color='#c5d4df')
 m=fig.add_axes([.77,.54,.20,.29],facecolor='#101923');m.plot(pos[:,0],pos[:,1],':',c='#7c8ea5',lw=1.3);line,=m.plot([],[],c='#ffb454',lw=2);dot,=m.plot([],[],'o',c='#77e4ff',ms=7);m.set_aspect('equal',adjustable='datalim');m.set_xlabel('X global (m)');m.set_ylabel('Y global (m)');m.set_title('Trayectoria · escala real');m.grid(alpha=.2)
 a=fig.add_axes([.77,.25,.20,.19],facecolor='#101923');a.plot(t,load,c='#70d8bc');cursor=a.axvline(0,c='white',lw=1);a.set_xlim(0,12);a.set_ylim(0,11.5);a.set_xlabel('Tiempo físico (s)');a.set_ylabel('Carga normal exigida (g)');a.grid(alpha=.2)
 for k,tt in enumerate(np.arange(0,12,1/fps)):
  i=int(round(tt/.002));ang=-np.deg2rad(bank[i]);rot=np.array([[1,0,0],[0,np.cos(ang),-np.sin(ang)],[0,np.sin(ang),np.cos(ang)]])
  model.set_verts(tri@rot.T)
  # Orbit smoothly around the detailed hull while following the velocity frame.
  az=-135+65*np.sin(np.pi*tt/12)**2;el=24+12*np.sin(np.pi*tt/12);ax.view_init(elev=el,azim=az)
  line.set_data(pos[:i+1,0],pos[:i+1,1]);dot.set_data([pos[i,0]],[pos[i,1]]);cursor.set_xdata([tt,tt])
  ay=d['lateral_g'][i];radius=np.sum(d['velocity'][i,:2]**2)/(abs(ay)*9.80665) if abs(ay)>1e-3 else np.inf
  rs=f'{radius:,.0f} m' if np.isfinite(radius) else 'recta'
  tele.set_text(f't = {tt:05.2f} s     |     Mach nominal {speed/3.6/340.3:.2f}     |     presión dinámica {float(d["q_Pa"])/1000:.1f} kPa\nCarga normal requerida {load[i]:.2f} g  ·  {N[i]:.0f} N     |     radio horizontal instantáneo aprox. {rs}\nAltura {pos[i,2]:.1f} m     |     masa supuesta 5 kg     |     alabeo mostrado {bank[i]:+.1f}°')
  phase.set_text('Recta / estabilizado' if tt<1 or tt>=11.5 else ('Giro izq. · pico 3 g' if tt<4 else ('Cambio a giro der. · 6 g' if tt<8.5 else 'Giro izq. · pico 10 g')))
  fig.canvas.draw();im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert('RGB');im.save(frames/f'{total:04d}.png');total+=1
  if k%45==0:print('FRAME',speed,k,'of 180',flush=True)
 plt.close(fig)
(P/'VIDEO.json').write_text(json.dumps(dict(frames=total,fps=fps,duration_s=24,resolution=[1920,1080],scenario_physical_seconds=12,scenarios_kmh=[600,1000],playback_rate=1,display_body_orientation='Bank relative to velocity-aligned chase frame; orbital camera not vehicle yaw',rendering='Matplotlib actual CAD tessellation, no CFD or generative imagery',type='Inverse-demand kinematic reconstruction, not forward validated aircraft simulation'),indent=2))
