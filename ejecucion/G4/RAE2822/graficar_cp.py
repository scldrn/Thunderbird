"""Plot saved diagnostic comparisons; never labels startup as validation."""
from pathlib import Path
import argparse
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

parser=argparse.ArgumentParser()
parser.add_argument('--case',type=Path,required=True)
a=parser.parse_args();case=a.case.resolve()
d=np.loadtxt(case/'Cp_CONTRASTE_ARRANQUE.csv',delimiter=',',skiprows=1)
r=json.loads((case/'AUDITORIA_PILOTO.json').read_text())
le=int(np.argmin(d[:,0]))
fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained',sharey=True)
for ax,ids,label in ((axes[0],slice(None,le+1),'Cara superior'),(axes[1],slice(le,None),'Cara inferior')):
    x=d[ids]
    ax.plot(x[:,0],x[:,3],color='#C2410C',lw=1.8,label='Cálculo de arranque')
    ax.scatter(x[:,0],x[:,2],s=17,facecolors='none',edgecolors='#1F2937',label='Experimento NASA/RAE')
    ax.set(xlabel='x/c',ylabel='Cp',title=label,xlim=(0,1))
    ax.grid(alpha=.2);ax.legend(fontsize=8)
axes[0].invert_yaxis()
fig.suptitle(f"RAE2822 · contador {r['iteration_target']} · ARRANQUE NO CONVERGIDO\nMach 0,729 · α 2,31° · Re 6,5×10⁶ · error RMS Cp {r['Cp_startup_RMS_error']:.3f}",fontweight='bold')
fig.savefig(case/'Cp_ARRANQUE_NO_VALIDADO.png',dpi=160)
plt.close(fig)
