"""Seed a bounded local-pseudotime diagnostic from finite physical-time fields."""
from pathlib import Path
import json,shutil,re,hashlib
ROOT=Path(__file__).resolve().parent
src=ROOT/'avance_A_compresible_600kmh_Euler_diag_v3';dst=ROOT/'avance_A_compresible_600kmh_LTS_diag'
if dst.exists():raise FileExistsError(dst)
audit=json.loads((src/'FINAL_STARTUP_AUDIT.json').read_text())
assert audit['target_time_reached'] and audit['all_U_p_T_finite'] and audit['all_p_T_positive']
dst.mkdir()
for name in ('constant','system'):shutil.copytree(src/name,dst/name)
shutil.copytree(src/'0.0001',dst/'0')
timefile=dst/'0/uniform/time'
if timefile.exists():timefile.unlink()
p=dst/'system/fvSchemes';s=p.read_text().replace('default Euler','default localEuler');p.write_text(s)
p=dst/'system/fvSolution';s=p.read_text().replace('PIMPLE {','PIMPLE {maxCo 0.2; maxDeltaT 0.001; rDeltaTSmoothingCoeff 0.1; rDeltaTDampingCoeff 0.2;');p.write_text(s)
p=dst/'system/controlDict';s=p.read_text()
s=re.sub(r'endTime\s+[^;]+;','endTime 200;',s);s=re.sub(r'deltaT\s+[^;]+;','deltaT 1;',s)
s=s.replace('writeControl adjustableRunTime; writeInterval 0.000025;','writeControl timeStep; writeInterval 25;')
s=re.sub(r'\nadjustTimeStep yes; maxCo 0.2; maxDeltaT 1e-6;\n','\nadjustTimeStep no;\n',s);p.write_text(s)
meta=json.loads((src/'compressible_assumptions.json').read_text())
for name in ('target_physical_time_s','initial_deltaT_s','maxDeltaT_s'):meta.pop(name,None)
meta.update(purpose='Local pseudotime pressure-convergence diagnostic, slip body; not full drag validation',time_counter_is_physical_seconds=False,counter_kind='local_pseudo_iterations',target_steady_iterations=200,
 source_seed_case=str(src.resolve()),source_seed_time_s=.0001,source_seed_developed=False,local_maxCo=.2,local_maxDeltaT_s=.001,local_rDeltaT_smoothing=.1,local_rDeltaT_damping=.2,
 time_interpretation='Local cell steps are algorithmic. The displayed counter and local steps do not represent a flight trajectory.',source_basis='Installed Foundation13 angledDuctLTS example and isothermalFluid/setRDeltaT.C',
 single_parameter_comparison=False)
meta['input_sha256']={str(p.relative_to(dst)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('0','system','constant') for p in (dst/folder).iterdir() if p.is_file()}
(dst/'compressible_assumptions.json').write_text(json.dumps(meta,indent=2));print(dst)
