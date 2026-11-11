"""Preserve failed steady startup; prepare conservative physical-time diagnostic."""
from pathlib import Path
import shutil,json,re,hashlib
ROOT=Path(__file__).resolve().parent
src=ROOT/'avance_A_compresible_600kmh_diag';dst=ROOT/'avance_A_compresible_600kmh_Euler_diag_v3'
if dst.exists():raise FileExistsError(dst)
state=json.loads((src/'run_state.json').read_text());assert state['exit_code']!=0
dst.mkdir()
for name in ('0','constant','system'):shutil.copytree(src/name,dst/name)
p=dst/'system/fvSchemes';s=p.read_text().replace('default steadyState','default Euler').replace('bounded Gauss upwind','Gauss upwind');p.write_text(s)
p=dst/'system/fvSolution';s=p.read_text().split('relaxationFactors')[0]
s=s.replace('solvers {','solvers {pFinal {solver GAMG; smoother GaussSeidel; tolerance 1e-8; relTol 0;} "(U|h)Final" {solver PBiCGStab; preconditioner DILU; tolerance 1e-9; relTol 0;}')
s=s.replace('(U|h)','(rho|U|h)')
s=s.replace('PIMPLE {transonic yes;','PIMPLE {transonic yes; nOuterCorrectors 2; nCorrectors 2;');p.write_text(s)
p=dst/'system/controlDict';s=p.read_text();s=re.sub(r'endTime\s+[^;]+;','endTime 0.0001;',s);s=s.replace('deltaT 1;','deltaT 1e-7;').replace('writeControl timeStep; writeInterval 10;','writeControl adjustableRunTime; writeInterval 0.000025;')
s+='\nadjustTimeStep yes; maxCo 0.2; maxDeltaT 1e-6;\n';p.write_text(s)
meta=json.loads((src/'compressible_assumptions.json').read_text());meta.pop('target_steady_iterations',None)
meta.update(purpose='Physical-time startup diagnostic from uniform fields, after failed steady launch; not load acceptance',target_physical_time_s=.0001,time_counter_is_physical_seconds=True,initial_deltaT_s=1e-7,maxCo=.2,maxDeltaT_s=1e-6,
 initial_state='Uniform U,p,T; not developed flow; no fields from rejected steady iterations reused',
 failed_reference_case=str(src.resolve()),single_parameter_comparison=False,
 changes_from_failed_steady=['Euler time derivative','physical time and CFL-limited step','two outer/two pressure correctors','no steady field/equation relaxation','conservative upwind time-dependent advection'],
 preparation_correction='Explicit pFinal avoids a forward reference; rho is included in both solver patterns, following the installed transient aerofoil tutorial. Earlier preparation failures did not complete a timestep.')
meta['input_sha256']={str(p.relative_to(dst)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('0','system','constant') for p in (dst/folder).iterdir() if p.is_file()}
(dst/'compressible_assumptions.json').write_text(json.dumps(meta,indent=2));print(dst)
