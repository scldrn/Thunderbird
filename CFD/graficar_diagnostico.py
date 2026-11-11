from pathlib import Path
import os,re,json,numpy as np
ROOT=Path(__file__).resolve().parent;os.environ['MPLCONFIGDIR']=str(ROOT/'mpl-cache')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(12,4.3))
for ax,case,label in zip(axes,['conducto_X0_Y0_h0.006','conducto_X35_Y-35_h0.006'],['Neutro: 600 iteraciones','Desviado: 300 iteraciones']):
 data={}
 for filename in ['log.foamRun','log.foamRun_continuacion']:
  p=ROOT/case/filename
  if not p.exists():continue
  chunks=re.split(r'\nTime = ',p.read_text())
  for chunk in chunks[1:]:
   t=float(re.match(r'([\d.eE+-]+)',chunk)[1]);vals={}
   for key in ['Ux','Uy','Uz','p','k','omega']:
    m=re.search(r'Solving for '+key+r', Initial residual = ([\deE.+-]+)',chunk)
    if m:vals[key]=float(m[1])
   if len(vals)==6:data[t]=vals
 times=sorted(data)
 for key in ['Ux','Uz','p','k']:ax.semilogy(times,[data[t][key] for t in times],label=key,lw=1)
 ax.axhline(1e-5,color='gray',ls='--',lw=.8);ax.set(title=label,xlabel='Iteración SIMPLE',ylabel='Residuo inicial normalizado');ax.grid(alpha=.2);ax.legend(ncol=4,fontsize=8)
fig.suptitle('Diagnóstico CFD preliminar: no se cumplen todos los umbrales de convergencia')
fig.tight_layout();fig.savefig(ROOT/'diagnostico_convergencia.png',dpi=180)
