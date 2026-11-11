"""Separate first-order numerical diagnostic; never presented as validated URANS.

Keep the failed experiment intact. Several numerical controls change together,
so this study cannot attribute failure to one particular setting.
"""
from pathlib import Path
import shutil,json,re,hashlib

ROOT=Path(__file__).resolve().parent
src=ROOT/'transitorio_X35_Y-35_h0.006'
dst=ROOT/'diagnostico_Euler_upwind_X35_Y-35_h0.006'
if dst.exists():raise RuntimeError('Diagnostic case exists; do not overwrite it.')
dst.mkdir()
for name in ['constant','system','0']:shutil.copytree(src/name,dst/name)
for name in ['mesh_metadata.json','log.checkMesh']:shutil.copy2(src/name,dst/name)
p=dst/'0/uniform/time'
if p.exists():p.unlink()
p=dst/'system/controlDict';s=p.read_text()
s=re.sub(r'endTime\s+[^;]+;','endTime 0.001;',s)
s=re.sub(r'maxCo\s+[^;]+;','maxCo 0.5;',s)
s=re.sub(r'deltaT\s+[^;]+;','deltaT 1e-6;',s)
s=s.replace('writeInterval 0.001','writeInterval 0.00025')
p.write_text(s)
p=dst/'system/fvSchemes';s=p.read_text()
s=s.replace('default backward','default Euler')
s=s.replace('div(phi,U) Gauss linearUpwind grad(U)','div(phi,U) Gauss upwind')
p.write_text(s)
p=dst/'system/fvSolution';s=p.read_text()
s=s.replace('nOuterCorrectors 1','nOuterCorrectors 2')
s=s.replace('tolerance 1e-7','tolerance 1e-8')
p.write_text(s)
meta=json.loads((src/'transient_assumptions.json').read_text())
meta.update(end_time_s=.001,nominal_total_flow_through_times=.001/meta['flow_through_time_s'],maxCo=.5,initial_dt=1e-6,time_scheme='Euler first-order diagnostic',momentum_advection='Gauss upwind',outer_correctors=2,purpose='Numerical stability diagnostic only; target deliberately shorter than initial discard window. No statistical load estimates permitted.',comparison_case=src.name,not_a_single_variable_comparison=True)
meta['configuration_sha256']={str(p.relative_to(dst)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (dst/'system').iterdir() if p.is_file()}
(dst/'transient_assumptions.json').write_text(json.dumps(meta,indent=2))
print(dst)
