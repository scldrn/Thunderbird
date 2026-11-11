"""Paired restart from the SAME stable saved field; only ddt scheme differs.
The short window tests numerical behavior, not statistical load convergence.
"""
from pathlib import Path
import json,shutil,re,hashlib
ROOT=Path(__file__).resolve().parent
source=ROOT/'diagnostico_Euler_upwind_X35_Y-35_h0.006'
initial=source/'0.001';assert initial.is_dir()
hashes=lambda folder:{str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}
made=[]
for scheme in ['Euler','backward']:
    dst=ROOT/f'comparacion_{scheme}_reinicio_h0.006'
    if dst.exists():raise RuntimeError(f'{dst} already exists: do not overwrite a run.')
    dst.mkdir()
    for name in ['constant','system']:shutil.copytree(source/name,dst/name)
    shutil.copytree(initial,dst/'0')
    # Reset the clock consistently in both runs; otherwise saved metadata can
    # override controlDict and reproduce the previously diagnosed no-op bug.
    timefile=dst/'0/uniform/time'
    if timefile.exists():timefile.unlink()
    p=dst/'system/controlDict';s=p.read_text();s=re.sub(r'endTime\s+[^;]+;','endTime 0.0015;',s)
    diagnostics='''
maxVelocityDiagnostic {type volFieldValue; libs ("libfieldFunctionObjects.so"); cellZone all; operation maxMag; writeFields false; log true; fields (U); writeControl timeStep; writeInterval 20;}
minScalarsDiagnostic {type volFieldValue; libs ("libfieldFunctionObjects.so"); cellZone all; operation min; writeFields false; log true; fields (p k omega); writeControl timeStep; writeInterval 20;}
maxScalarsDiagnostic {type volFieldValue; libs ("libfieldFunctionObjects.so"); cellZone all; operation max; writeFields false; log true; fields (p k omega); writeControl timeStep; writeInterval 20;}
'''
    s=s.replace('functions {','functions {\n'+diagnostics);p.write_text(s)
    p=dst/'system/fvSchemes';p.write_text(p.read_text().replace('default Euler;',f'default {scheme};'))
    metadata=json.loads((source/'transient_assumptions.json').read_text())
    metadata.update(initial_field_source=str(initial),initial_state_converged=False,initial_physical_age_s=.001,restart_clock_origin_s=0,end_time_s=.0015,discard_before_s=.00725-.001,time_scheme=scheme,nominal_total_flow_through_times=.0015/metadata['flow_through_time_s'],purpose='Paired temporal-scheme diagnostic from identical fields. Not a statistical load run or full installation simulation.',comparison_isolated_parameter='ddtSchemes/default only',not_a_single_variable_comparison=False,initial_field_hashes=hashes(dst/'0'),mesh_sha256=hashes(dst/'constant/polyMesh'),system_hashes=hashes(dst/'system'),startup_note='Source implementation of backward uses effectively Euler coefficients while fewer than two old times exist. No old-time history is supplied; start-up must be excluded when comparing order.')
    (dst/'transient_assumptions.json').write_text(json.dumps(metadata,indent=2));made.append(dst)
a,b=made
assert hashes(a/'0')==hashes(b/'0') and hashes(a/'constant')==hashes(b/'constant')
for p in (a/'system').iterdir():
    if p.name!='fvSchemes':assert p.read_bytes()==(b/'system'/p.name).read_bytes()
assert (a/'system/fvSchemes').read_text().replace('default Euler;','default backward;')==(b/'system/fvSchemes').read_text()
audit=dict(cases=[p.name for p in made],identical_initial_fields=True,identical_mesh_and_models=True,only_dictionary_difference='ddtSchemes/default Euler versus backward',startup_history_available=False,loads_accepted=False,physical_initial_age_s=.001,requested_restart_window_s=.0015)
(ROOT/'COMPARACION_TEMPORAL_CONFIGURACION.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit))
