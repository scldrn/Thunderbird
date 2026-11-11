from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import differential_evolution
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'legacy'/'scripts'))
from control import allocation,facets
models=[json.loads((ROOT/'salida'/f'{m}kg'/'mediciones_DIGITALES.json').read_text()) for m in [5,10]]
def evaluate(angles,detail=False):
 out=[]
 for d in models:
  _,_,u=allocation(d['L_m'],d['D_m'],2,*angles);p=np.array(d['rotor_centers_m']);cg=np.array(d['CG_geometric_components_only_m']);I=np.array(d['inertia_geometric_components_only_kgm2']);L=d['L_m'];m=d['total_budget_kg']
  B=np.vstack([u.T,np.cross(p-cg,u).T/L]);ns,h=facets(B)
  if ns is None:return 1e6
  t=float(np.max((2*m*9.80665*np.linalg.norm(ns[:,:3],axis=1)+2*np.linalg.norm(ns[:,3:]@I,axis=1)/L)/h))
  out.append(dict(target_mass_kg=d['target_mass_kg'],required_T_N=t,required_T_per_weight=t/(m*9.80665),condition=float(np.linalg.cond(B))))
 return out if detail else max(r['required_T_per_weight'] for r in out)
results=[]
for seed in [17,29,43]:
 opt=differential_evolution(evaluate,[(.1,np.pi-.1),(-np.pi,np.pi)],seed=seed,maxiter=90,popsize=10,tol=1e-6,polish=True)
 r=dict(seed=seed,angles_rad=opt.x.tolist(),score=float(opt.fun),converged=bool(opt.success),evaluations=opt.nfev,results=evaluate(opt.x,True));results.append(r);print(json.dumps(r),flush=True)
best=min(results,key=lambda r:r['score']);(ROOT/'ejes_candidatos.json').write_text(json.dumps(dict(best=best,runs=results,scope='Two-angle symmetric family, positions and provisional inertia frozen. No collision constraint in search; CAD check required.'),indent=2))
