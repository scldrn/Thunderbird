"""Static geometric audit figure; does not display a CFD flow solution."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2]/'fuentes/benchmark_RAE2822/raetaf.x.fmt'
raw = np.fromstring(SOURCE.read_text(), sep=' ')
g = raw[2:].reshape(2,65,369).transpose(1,2,0)
z = np.load(HERE/'piloto_r4_hibrido_resuelto/TOPOLOGIA_2D.npz')
xy = z['xy_chord']
fig, axes = plt.subplots(2,2,figsize=(13,7.5),layout='constrained')
windows = [(-.04,1.08,-.11,.13),(.985,1.035,-.012,.012)]
for col, window in enumerate(windows):
    x0,x1,y0,y1=window
    ax=axes[0,col]
    for curve in list(g)+list(g.transpose(1,0,2)):
        ax.plot(curve[:,0],curve[:,1],lw=.35,color='#155E75')
    ax=axes[1,col]
    for name in ('quads','triangles'):
        c=z[name]
        p=xy[c]
        mask=(p[...,0].max(axis=1)>=x0)&(p[...,0].min(axis=1)<=x1)&(p[...,1].max(axis=1)>=y0)&(p[...,1].min(axis=1)<=y1)
        p=p[mask]
        seg=np.stack((p,np.roll(p,-1,axis=1)),axis=2).reshape(-1,2,2)
        ax.add_collection(LineCollection(seg,linewidths=.22,colors='#155E75'))
    for row in (0,1):
        ax=axes[row,col]
        ax.fill(g[0,32:337,0],g[0,32:337,1],color='#1F2937',zorder=4)
        ax.set(xlim=(x0,x1),ylim=(y0,y1),xlabel='x/c',ylabel='y/c')
        ax.set_aspect('equal',adjustable='box')
        ax.grid(alpha=.15)
axes[0,0].set_title('NASA: malla original (conversión FV rechazada)')
axes[0,1].set_title('Detalle del borde de salida: original')
axes[1,0].set_title('Malla híbrida r4: geometría y capas conservadas, subdivididas')
axes[1,1].set_title('Detalle r4: interfaz y estela refinadas')
fig.suptitle('RAE2822 · Auditoría de malla, sin solución de flujo',fontweight='bold')
fig.savefig(HERE/'COMPARACION-MALLAS.png',dpi=170)
plt.close(fig)
