from pathlib import Path
import numpy as np,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
import cadquery as cq
from PIL import Image
P=Path(__file__).resolve().parent;frames=P/'frames';frames.mkdir(exist_ok=True)
h=np.load(P/'5kg_nominal.npz')['history']
if (P/'malla_visual.npz').exists():
 cache=np.load(P/'malla_visual.npz');tri=cache['triangles'];colors=cache['colors']
 src=P.parent/'modelos_integrados/producto_A07/5kg/A07_abierto.step'
else:
 src=P.parent/'modelos_integrados/producto_A07/5kg/A07_abierto.step';meta=json.loads((src.parent/'manifest.json').read_text());names={v['name']:v for v in meta['parts']}
 tri=[];colors=[]
 for s,n,l,c in cq.Assembly.load(str(src)):
  n=n.split('/')[-1]
  if n.startswith('compuerta_'):continue
  if not (names[n]['exterior'] or 'base_rotor_' in n or n.startswith('conducto_')):continue
  v,f=s.moved(l).tessellate(1.5,angularTolerance=.45);v=np.array([a.toTuple() for a in v])/1000;tt=v[np.asarray(f)];tri.extend(tt)
  rgb=np.sqrt(np.asarray(names[n]['color']))*.8+.1
  normal=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
  shade=.5+.5*np.abs(normal@np.array([.2,-.5,.84]));colors.extend(np.clip(rgb[None,:]*shade[:,None],0,1))
 tri=np.array(tri);colors=np.array(colors);np.savez_compressed(P/'malla_visual.npz',triangles=tri,colors=colors)
plt.rcParams.update({'text.color':'#e3eaf2','axes.labelcolor':'#bccad8','xtick.color':'#aabacc','ytick.color':'#aabacc','font.size':8,'axes.edgecolor':'#506078'})
fig=plt.figure(figsize=(10.24,6.4),dpi=100,facecolor='#0b1017');ax=fig.add_axes([.02,.17,.63,.70],projection='3d',facecolor='#0b1017');ax.set(xlim=(-2,4),ylim=(-2,4),zlim=(0,5),xlabel='X (m)',ylabel='Y (m)',zlabel='Altura (m)');ax.set_box_aspect([6,6,5]);ax.view_init(elev=27,azim=-58)
for axis in (ax.xaxis,ax.yaxis,ax.zaxis):axis.set_pane_color((.06,.08,.11,1));axis._axinfo['grid']['color']=(.25,.3,.4,.3)
ax.plot(h[:,14],h[:,15],h[:,16],':',c='#758494',alpha=.35,lw=.7)
trail,=ax.plot([],[],[],c='#ffb454',lw=1.7);target,=ax.plot([],[],[],'+',c='#77e4ff',ms=10)
body=Poly3DCollection(tri,facecolors=colors,edgecolors='none',zsort='average');ax.add_collection3d(body)
fanxy=np.array([[-.2,-.076,0],[-.2,.076,0],[.2,-.076,0],[.2,.076,0]])
force_lines=[ax.plot([],[],[],c='#70d8bc',lw=1.2)[0] for _ in range(4)]
fig.text(.04,.94,'A / VENTILADORES INTERNOS',fontsize=15,weight='bold');fig.text(.04,.90,'Simulación condicional de cuerpo rígido · 5 kg supuestos · baja velocidad',fontsize=10,color='#b5c6d9')
tele=fig.text(.04,.08,'',fontsize=10);phase=fig.text(.68,.88,'',fontsize=10,color='#ffb454');fig.text(.04,.025,'Empuje vectorial ideal supuesto. Cubiertas omitidas en la vista. Sin CFD, energía ni validación física.',fontsize=8,color='#f0b5a6')
angles=R.from_quat(h[:,7:11]).as_euler('xyz',degrees=True);force=np.linalg.norm(h[:,17:29].reshape(-1,4,3),axis=2).max(axis=1)
sub=[]
for y,label in [(.62,'Altura (m)'),(.37,'Actitud (°)'),(.12,'Fuerza máx. / ventilador (N)')]:
 a=fig.add_axes([.71,y,.26,.18],facecolor='#101923');a.set_xlim(0,24);a.set_ylabel(label);a.grid(alpha=.14);sub.append(a)
sub[0].plot(h[:,0],h[:,3],c='#ffb454');sub[0].plot(h[:,0],h[:,16],':',c='#77e4ff');sub[0].set_ylim(1.7,3.8)
for j,c in enumerate(['#77e4ff','#f1a2e7','#70d8bc']):sub[1].plot(h[:,0],angles[:,j],c=c,lw=.7,label=['roll','pitch','yaw'][j])
sub[1].set_ylim(-2,8);sub[1].legend(fontsize=6,facecolor='#101923',labelcolor='white',loc='upper right')
sub[2].plot(h[:,0],force,c='#70d8bc');sub[2].axhline(21,c='#ee8890',ls='--',lw=.8);sub[2].set_ylim(0,23);sub[2].set_xlabel('Tiempo físico (s)')
cursors=[a.axvline(0,color='white',lw=.8) for a in sub]
phases=['Estacionario / recuperación','Desplazamiento +X','Desplazamiento +Y','Ascenso + perturbación','Cambio de dirección','Regreso / estabilización']
fps=15;indices=np.rint(np.arange(0,24,1/fps)/.005).astype(int)
for frame,i in enumerate(indices):
 row=h[i];t=row[0];pos=row[1:4];rot=R.from_quat(row[7:11]);vv=rot.apply(tri.reshape(-1,3)).reshape(tri.shape)+pos;body.set_verts(vv)
 trail.set_data(h[:i+1,1],h[:i+1,2]);trail.set_3d_properties(h[:i+1,3]);target.set_data([row[14]],[row[15]]);target.set_3d_properties([row[16]])
 ff=row[17:29].reshape(4,3)
 for line,origin,f in zip(force_lines,fanxy,ff):
  start=rot.apply(origin)+pos;end=start+rot.apply(f)/30;line.set_data([start[0],end[0]],[start[1],end[1]]);line.set_3d_properties([start[2],end[2]])
 for line in cursors:line.set_xdata([t,t])
 speed=np.linalg.norm(row[4:7]);acc=np.linalg.norm(row[29:32]);tele.set_text(f't = {t:05.2f} s     |     velocidad {speed:.2f} m/s     |     aceleración {acc/9.80665:.2f} g\nCono útil supuesto: 35°     ·     Empuje máximo supuesto: 21 N por ventilador')
 phase.set_text(phases[min(5,int(t//4))]);fig.canvas.draw();im=np.asarray(fig.canvas.buffer_rgba());Image.fromarray(im).convert('RGB').save(frames/f'{frame:04d}.png')
 if frame%60==0:print('FRAME',frame,'of',len(indices),'triangles',len(tri),flush=True)
(P/'VIDEO.json').write_text(json.dumps(dict(frames=len(indices),fps=fps,duration_seconds=len(indices)/fps,physical_duration_seconds=24,geometry_source=str(src),geometry_display='Actual selected exterior STEP tessellation; covers omitted; no deployment animation or CFD',state_source='5kg_nominal.npz',playback_rate=1),indent=2))
