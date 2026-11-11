from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
os.environ['MPLCONFIGDIR']=str(OUT/'mpl-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
coord=np.loadtxt(ROOT/'fuentes/uiuc/sd8020.dat',skiprows=1)
x=np.linspace(0,1,400);y=5*.12*(.2969*np.sqrt(x)-.126*x-.3516*x*x+.2843*x**3-.1036*x**4)
naca=np.column_stack([np.r_[x[::-1],x[1:]],np.r_[y[::-1],-y[1:]]])
fig,axs=plt.subplots(3,2,figsize=(16,12),gridspec_kw={'height_ratios':[1.3,1,1.2]})
colors=['#25789b','#ad6830']
for col,(name,c,profile,angle,power) in enumerate([('A · NACA 0012',35,naca,11.77,733),('B · SD8020',30,coord,12.86,611)]):
 color=colors[col];ax=axs[0,col]
 ax.set_title(name+' | referencia geométrica',loc='left',fontsize=17,fontweight='bold',color=color,pad=18)
 # plan: pitch axis y=0, leading edge -c/4, trailing edge +3c/4
 for s in [-1,1]:
  lo,hi=sorted([s*40,s*228.6]);ax.add_patch(Rectangle((lo,-c/4),hi-lo,c,fc=color,alpha=.22,ec=color,lw=2))
  ax.plot([s*16,s*40],[0,0],lw=6,color='#7c8790')
 ax.add_patch(Circle((0,0),16,fc='#d7dee2',ec='#40505c',lw=1.5))
 ax.plot([-235,235],[0,0],'--',color='#9d3f54',lw=1)
 ax.annotate('',xy=(-228.6,57),xytext=(228.6,57),arrowprops={'arrowstyle':'<->','color':'#40505c'})
 ax.text(0,63,'Diámetro de giro: 457,2 mm',ha='center',fontsize=11)
 ax.annotate('',xy=(40,-30),xytext=(228.6,-30),arrowprops={'arrowstyle':'<->'})
 ax.text(134,-41,'Tramo aerodinámico: 188,6 mm',ha='center',fontsize=9)
 ax.annotate('',xy=(245,-c/4),xytext=(245,3*c/4),arrowprops={'arrowstyle':'<->'})
 ax.text(253,8,f'{c} mm',rotation=90,va='center')
 ax.text(-220,-43,'Raíz aerodinámica: r = 40 mm\nPalas rectas · sin torsión',fontsize=10)
 ax.text(0,-70,'Buje y uniones esquemáticos: dimensiones no definidas',ha='center',fontsize=9,color='#6b737b')
 ax.set_xlim(-270,280);ax.set_ylim(-80,85);ax.set_aspect('equal');ax.axis('off')
 ax=axs[1,col];p=profile*c
 ax.fill(p[:,0],p[:,1],color=color,alpha=.22);ax.plot(p[:,0],p[:,1],color=color,lw=2)
 ax.axhline(0,color='#8d959b',ls=':',lw=1)
 ax.plot(c*.25,0,'o',color='#9d3f54',ms=6)
 ax.annotate('Eje de paso: 25 % de cuerda',xy=(c*.25,0),xytext=(c*.12,-6),arrowprops={'arrowstyle':'->','color':'#9d3f54'},color='#9d3f54',fontsize=10)
 ax.text(0,6,'Borde de ataque',fontsize=9);ax.text(c,6,'Borde de salida',ha='right',fontsize=9)
 ax.text(c/2,10,f'Sección a escala · cuerda {c} mm',ha='center',fontsize=12,fontweight='bold')
 thick=(p[:,1].max()-p[:,1].min())
 ax.text(c/2,-10,f'Espesor geométrico máx. ≈ {thick:.2f} mm · no es espesor de pared',ha='center',fontsize=10)
 ax.set_xlim(-3,c+3);ax.set_ylim(-13,13);ax.set_aspect('equal');ax.axis('off')
 ax=axs[2,col];ax.axis('off')
 text=(f'PUNTO DE CÁLCULO · 6.000 rpm\n\n'
       f'Empuje objetivo por rotor: 38,9 N\n'
       f'Paso colectivo estimado: +{angle:.2f}°\n'
       f'Potencia eléctrica estimada: {power} W\n'
       f'Masa de pala supuesta: 15 g (no conseguida ni verificada)\n\n')
 if col==0:text+='Polar sintética: no son ensayos del NACA 0012.\nPerfil geométrico calculado con borde de salida cerrado.'
 else:text+='CL/CD experimentales UIUC, con cobertura parcial.\n5 % del tramo queda fuera del dominio tabulado.\nCoordenadas reales SD8020: archivo original UIUC.'
 ax.text(.03,.93,text,transform=ax.transAxes,va='top',fontsize=12,linespacing=1.45)
fig.suptitle('DOS ALTERNATIVAS DE PALA REVERSIBLE',fontsize=22,fontweight='bold',y=.985)
fig.text(.5,.945,'Comparación de geometría · ambas para el vehículo de 5 kg · cotas en milímetros',ha='center',fontsize=12)
fig.text(.5,.035,'NO ES PLANO DE FABRICACIÓN · Material, laminado, retención, buje, rodamientos y bloqueo pendientes.',ha='center',fontsize=12,color='#a13737',fontweight='bold')
fig.text(.5,.015,'Potencias con 85 % de eficiencia supuesta; modelos distintos, sin prueba de superioridad. Inversión de empuje pendiente de ensayo.',ha='center',fontsize=10)
fig.subplots_adjust(top=.88,bottom=.08,hspace=.12,wspace=.18)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'comparacion_detallada_palas.{ext}',dpi=180)
print('Dibujo generado')
