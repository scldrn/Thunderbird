from pathlib import Path
import json,re,numpy as np
ROOT=Path(__file__).resolve().parent
num=re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
def table(folder,name):
 rows={}
 for p in sorted((folder/'postProcessing'/name).glob('*/surfaceFieldValue.dat'),key=lambda p:float(p.parent.name)):
  for line in p.read_text().splitlines():
   if line.strip() and not line.startswith('#'):
    v=[float(x) for x in num.findall(line)];rows[v[0]]=v
 return np.array([rows[t] for t in sorted(rows)])
def stats(v):return dict(last=float(v[-1]),mean_tail=float(np.mean(v[-50:])),min_tail=float(min(v[-50:])),max_tail=float(max(v[-50:])))
out=[]
for folder in sorted(ROOT.glob('conducto_*')):
 if not (folder/'postProcessing').exists():continue
 logs='\n'.join(p.read_text() for p in [folder/'log.foamRun',folder/'log.foamRun_continuacion'] if p.exists())
 residuals={}
 for key,val in re.findall(r'Solving for (\w+), Initial residual = ([\deE.+-]+)',logs):residuals[key]=float(val)
 thresholds={'p':1e-4,'Ux':1e-5,'Uy':1e-5,'Uz':1e-5,'k':1e-5,'omega':1e-5}
 # pressure is checked at FIRST pressure solve in the last iteration, not its final correction.
 chunks=re.split(r'\nTime = ',logs);last=chunks[-1]
 for key in ['p']:
  match=re.search(r'Solving for '+key+r', Initial residual = ([\deE.+-]+)',last)
  if match:residuals[key]=float(match.group(1))
 pi=table(folder,'p_inlet');po=table(folder,'p_outlet');qi=table(folder,'flow_inlet');qo=table(folder,'flow_outlet');assert len(qi)==len(qo)
 imbalance=abs(qi[:,1]+qo[:,1])/abs(qi[:,1]);forces=[]
 for f in sorted((folder/'postProcessing').glob('force_vane*')):
  data={}
  for path in sorted(f.glob('*/forces.dat'),key=lambda p:float(p.parent.name)):
   for line in path.read_text().splitlines():
    if line.strip() and not line.startswith('#'):
     v=np.array([float(x) for x in num.findall(line)]);assert len(v)==13;data[v[0]]=v
  a=np.array([data[t] for t in sorted(data)]);F=a[:,1:4]+a[:,4:7];M=a[:,7:10]+a[:,10:13];axis=0 if 'vaneX' in f.name else 1
  forces.append(dict(patch=f.name,last_force_N=F[-1].tolist(),last_moment_Nm=M[-1].tolist(),axis_moment_Nm=stats(M[:,axis]),force_tail_range_N=float(np.linalg.norm(np.ptp(F[-50:],axis=0)))))
 out.append(dict(case=folder.name,last_iteration=float(pi[-1,0]),residuals_last=residuals,all_declared_residual_targets_met=all(residuals.get(k,float('inf'))<v for k,v in thresholds.items()),solver_reported_convergence='solution converged' in logs.lower(),relative_flux_imbalance=stats(imbalance),static_pressure_difference_Pa_last=1.225*float(pi[-1,1]-po[-1,1]),area_mean_outlet_velocity_ms_last=po[-1,2:5].tolist(),forces=forces,interpretation='Diagnostic raw prototype CFD values; not installed thrust, electric power, validated vane effectiveness or servo sizing. Grid, wall treatment and outlet sensitivity unresolved.'))
(ROOT/'AUDITORIA_RESULTADOS.json').write_text(json.dumps(out,indent=2));print(json.dumps([{k:v for k,v in r.items() if k!='forces'} for r in out],indent=2))
