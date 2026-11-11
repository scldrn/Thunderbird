"""Plot all experimental and warning-bearing XFOIL SD8020 comparison points."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent


def main():
    source=json.loads((HERE/'uiuc_61400_r1/RESULTADOS.json').read_text())
    points=source['points'];assert len(points)==10 and all(not p['accepted_numerical_point'] for p in points)
    alpha=np.array([p['alpha_deg'] for p in points])
    fig,axes=plt.subplots(1,2,figsize=(12,5.3),layout='constrained')
    for ax,key,unit,title in [(axes[0],'cl','Cl','Sustentación seccional'),(axes[1],'cd','Cd','Arrastre seccional')]:
        experiment=[p[key+'_experiment'] for p in points];calculation=[p[key+'_xfoil'] for p in points]
        ax.plot(alpha,experiment,'o-',color='#18597a',linewidth=1.7,markersize=5,label='UIUC: datos de túnel')
        ax.plot(alpha,calculation,'x--',color='#a34022',linewidth=1.4,markersize=6,label='XFOIL: con avisos de marcha')
        ax.set(xlabel='Ángulo de ataque [°]',ylabel=unit,title=title);ax.grid(alpha=.22)
    axes[0].legend(loc='upper left',fontsize=9)
    fig.suptitle('SD8020 · contraste inicial a Re medio 61.400',fontsize=14,fontweight='bold')
    fig.text(.5,-.015,'XFOIL: M=0, Ncrit=9 supuestos; condiciones experimentales no igualadas. No es validación del rotor.',
             ha='center',fontsize=9,color='#333333')
    for suffix in ('png','svg'):
        output=HERE/'uiuc_61400_r1'/('COMPARACION.'+suffix);assert not output.exists()
        fig.savefig(output,dpi=180,bbox_inches='tight')
    plt.close(fig)
    print('Saved PNG and SVG with all ten data points and warnings')


if __name__=='__main__':main()
