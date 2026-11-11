from pathlib import Path
import os,csv,math
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
os.environ.setdefault('MPLCONFIGDIR',str(OUT/'mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Circle,Ellipse
import numpy as np
rows=list(csv.DictReader((OUT/'comparacion_integrada_CONDICIONAL.csv').open()))
fig=plt.figure(figsize=(16,11),facecolor='#f4f7fb')
gs=fig.add_gridspec(2,2,left=.05,right=.95,top=.84,bottom=.18,hspace=.12,wspace=.12)
ink='#17334b';blue='#2783b5';green='#27846d';orange='#cf7438'
fig.text(.05,.955,'CONFIGURACIÓN CONCEPTUAL ACTUAL',fontsize=25,weight='bold',color=ink)
fig.text(.05,.92,'Familia de 5 y 10 kg · cuerpo circular L/D 6 · arquitectura híbrida en estudio',fontsize=14,color=ink)
fig.text(.05,.885,'Cotas del cuerpo de referencia. Integración, plegado y prestaciones todavía sin validar.',fontsize=11,color='#5b6d7d')

def label(ax,text,xy,xytext,color=ink,ha='center'):
    ax.annotate(text,xy=xy,xytext=xytext,ha=ha,va='center',fontsize=10,color=color,
                arrowprops=dict(arrowstyle='-',color=color,lw=1.1))

for col,m in enumerate([5,10]):
    row=next(r for r in rows if float(r['mass_kg'])==m and float(r['fineness'])==6)
    L=float(row['L_m']);D=float(row['D_m']);R=D/2
    ax=fig.add_subplot(gs[0,col]);ax.set_facecolor('#f4f7fb');ax.axis('off');ax.set_aspect('equal')
    ax.set_xlim(-.12*L,1.13*L);ax.set_ylim(-.32*L,.34*L)
    ax.set_title(f'{m} kg — objetivo de masa',loc='left',fontsize=19,weight='bold',color=ink,pad=8)
    # Smooth closed reference contour; entry/exit are schematic overlays.
    x=np.linspace(0,L,400);y=R*np.sqrt(np.clip(1-(2*x/L-1)**2,0,1))
    ax.fill_between(x,-y,y,color='#d7e7ee',edgecolor=ink,lw=1.8)
    ax.plot([-.04*L,1.08*L],[0,0],ls='-.',lw=.8,color='#8a9cab')
    sw=float(row['wing_oneplane_m2']);st=float(row['tail_oneplane_m2'])
    # Schematic projections: sweep/chord not selected for manufacturing.
    for station,span,chord in [(.5,.19,.13),(.84,.13,.10)]:
      for sign in [-1,1]:
        ax.add_patch(Polygon([(L*(station-chord),sign*R*.85),(L*(station+.06),sign*R*.8),
                            (L*(station+.04),sign*L*span),(L*(station-.03),sign*L*span)],
                            fc='#a9cbde',ec=blue,lw=1.4,alpha=.8))
    ax.add_patch(Rectangle((.34*L,-.23*D),.21*L,.46*D,fc='#b5dacf',ec=green,lw=1.4))
    engL,engD=(.241,.097) if m==5 else (.322,.121)
    ax.add_patch(Rectangle((.70*L-engL/2,-engD/2),engL,engD,fc='#f2c7a5',ec=orange,lw=1.5,hatch='///'))
    ax.plot([.05*L,.33*L],[0,0],color=blue,lw=5,alpha=.45)
    ax.annotate('',xy=(.29*L,0),xytext=(.08*L,0),arrowprops=dict(arrowstyle='->',color=blue,lw=2))
    ax.annotate('',xy=(1.065*L,0),xytext=(.90*L,0),arrowprops=dict(arrowstyle='->',color=orange,lw=3))
    ax.plot(.5*L,0,'+',color=ink,ms=13,mew=2)
    label(ax,'Toma / conducto\npor diseñar',(.16*L,0),(.13*L,.22*L),blue)
    label(ax,'Núcleo eléctrico\ny combustible',(.43*L,0),(.38*L,-.20*L),green)
    label(ax,'Superficies de transición\nretracción por resolver',(.5*L,.17*L),(.50*L,.29*L),blue)
    label(ax,'Cola de control',(.85*L,.11*L),(.88*L,.23*L),blue)
    label(ax,'Reactor axial de referencia\n'+('P100-RX-BL' if m==5 else 'P250-Pro-S histórico'),(.71*L,0),(.82*L,-.21*L),orange)
    dim=-.29*L
    ax.annotate('',xy=(L,dim),xytext=(0,dim),arrowprops=dict(arrowstyle='<->',color=ink,lw=1.1))
    for xx in [0,L]:ax.plot([xx,xx],[dim-.01*L,dim+.025*L],color=ink,lw=1)
    ax.text(L/2,dim+.012*L,f'Cuerpo: {L:.3f} m × Ø {D:.3f} m'.replace('.',','),ha='center',color=ink,fontsize=12,weight='bold')

    ax=fig.add_subplot(gs[1,col]);ax.axis('off');ax.set_aspect('equal');ax.set_xlim(-1.2,1.2);ax.set_ylim(-1.03,1.10)
    ax.text(-1.18,1.02,'ESTACIONARIO · ESQUEMA DE LOS MÓDULOS',fontsize=11,weight='bold',color=ink)
    ax.add_patch(Circle((0,0),.23,fc='#d7e7ee',ec=ink,lw=2))
    for i in range(8):
      a=2*math.pi*i/8+math.pi/8;cx=.65*math.cos(a);cy=.65*math.sin(a)
      ax.plot([.20*math.cos(a),cx],[.20*math.sin(a),cy],lw=3,color='#8499a8')
      ax.add_patch(Circle((cx,cy),.145,fc='#e7f2f8',ec=blue,lw=1.5))
      ax.plot([cx-.1, cx+.1],[cy-.035,cy+.035],color=blue,lw=2.5)
      ax.add_patch(Circle((cx,cy),.025,fc=ink))
      ax.text(cx,cy+.19,str(i+1),ha='center',fontsize=8,color=ink)
    ax.text(0,0,'CUERPO',ha='center',va='center',fontsize=9,color=ink,weight='bold')
    ax.text(0,-.93,'8 módulos de empuje reversible · representación topológica\nSin escala: posiciones, ejes y cinemática todavía por cerrar.',ha='center',va='center',fontsize=10,color='#536c80')

fig.text(.05,.125,'LECTURA DEL DIBUJO',fontsize=11,weight='bold',color=ink)
fig.text(.05,.095,'Azul: flujo y superficies aerodinámicas     Verde: volumen central reservado     Naranja: reactor y escape',fontsize=11,color=ink)
fig.text(.05,.060,'5 kg: el presupuesto integrado anterior excede la masa objetivo. 10 kg: cierre de componentes pendiente.',fontsize=11,color='#9b4c30',weight='bold')
fig.text(.05,.032,'No representa un montaje comprobado. El contorno, las superficies y los módulos pertenecen a una propuesta conceptual, no a un CAD integrado.',fontsize=10,color='#637789')
fig.savefig(OUT/'dibujo_estado_actual_5_y_10kg.png',dpi=180,facecolor=fig.get_facecolor())
fig.savefig(OUT/'dibujo_estado_actual_5_y_10kg.svg',facecolor=fig.get_facecolor())
