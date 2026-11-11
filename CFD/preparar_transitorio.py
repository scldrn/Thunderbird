"""Transient continuation from saved RANS fields; does not inherit time convergence."""
from pathlib import Path
import shutil,re,json,hashlib
ROOT=Path(__file__).resolve().parent;src=ROOT/'conducto_X35_Y-35_h0.006';dst=ROOT/'transitorio_X35_Y-35_h0.006'
if dst.exists():raise RuntimeError('Transient case already exists: inspect it rather than overwriting a run.')
dst.mkdir()
for name in ['constant','system']:shutil.copytree(src/name,dst/name)
shutil.copytree(src/'300',dst/'0')
# Saved steady-time metadata must not override the new physical time origin.
time_state=dst/'0/uniform/time'
if time_state.exists():time_state.unlink()
for name in ['mesh_metadata.json','log.checkMesh']:shutil.copy2(src/name,dst/name)
p=dst/'system/controlDict';s=p.read_text();s=re.sub(r'startFrom\s+\w+;', 'startFrom startTime;',s);s=re.sub(r'endTime\s+[^;]+;','endTime 0.03;',s);s=re.sub(r'deltaT\s+[^;]+;','deltaT 2e-6;',s);s=s.replace('writeControl timeStep; writeInterval 100;','writeControl adjustableRunTime; writeInterval 0.001;').replace('purgeWrite 2','purgeWrite 3');s=s.replace('runTimeModifiable true;','runTimeModifiable true;\nadjustTimeStep yes; maxCo 0.8; maxDeltaT 2e-5; timePrecision 10;');p.write_text(s)
p=dst/'system/fvSchemes';s=p.read_text().replace('default steadyState','default backward').replace('div(phi,U) bounded Gauss linearUpwind grad(U)','div(phi,U) Gauss linearUpwind grad(U)').replace('div(phi,k) bounded Gauss upwind','div(phi,k) Gauss upwind').replace('div(phi,omega) bounded Gauss upwind','div(phi,omega) Gauss upwind');p.write_text(s)
p=dst/'system/fvSolution';p.write_text('''FoamFile {version 2.0; format ascii; class dictionary; object fvSolution;}
solvers
{
 p {solver GAMG; tolerance 1e-7; relTol 0.02; smoother GaussSeidel;}
 pFinal {$p; relTol 0;}
 "(U|k|omega)" {solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0.05;}
 "(U|k|omega)Final" {solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0;}
}
PIMPLE {nOuterCorrectors 1; nCorrectors 2; nNonOrthogonalCorrectors 1;}
''')
meshhash={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (dst/'constant/polyMesh').iterdir() if p.is_file()}
meta=dict(initial_field_source=str(src/'300'),initial_state_converged=False,end_time_s=.03,flow_through_time_s=.145/40,discard_before_s=2*.145/40,nominal_total_flow_through_times=.03/(.145/40),maxCo=.8,maxDeltaT=2e-5,initial_dt=2e-6,time_scheme='backward',model='URANS kOmegaSST, same spatial grid and boundary conditions as prototype RANS',mesh_sha256=meshhash,acceptance_plan=['Audit actual Courant numbers, time steps, mass balance and per-step pressure corrections','Discard initial transient; examine block means over flow-through-time intervals, drift and fluctuations of all vane moments','Require timestep, mesh and outlet/domain sensitivity before accepting physical loads','A successful process exit is not statistical convergence or physical validation'])
(dst/'transient_assumptions.json').write_text(json.dumps(meta,indent=2));print(dst)
