"""Prepare a bounded, forced native continuation without changing flow physics."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--steps', type=int, required=True)
    args = parser.parse_args()
    source, case = args.source.resolve(), args.case.resolve()
    assert 100 <= args.steps <= 5000
    assert not case.exists(), 'Inspect existing continuation; never overwrite it'
    terminal = json.loads((source/'EJECUCION.json').read_text())
    audit = json.loads((source/'AUDITORIA_SU2.json').read_text())
    assert terminal['stage'] == 'solver_exited' and terminal['exit_code'] == 0
    assert audit['rho_range_kg_m3'][0] > 0 and audit['pressure_range_Pa'][0] > 0
    case.mkdir()
    for name in ('mesh_RAE2822_turb.su2', 'ORIGINAL_turb_SST_RAE2822.cfg'):
        shutil.copy2(source/name, case/name)
    shutil.copy2(source/'restart_flow.csv', case/'solution_flow.csv')
    text = (source/'case.cfg').read_text()
    replacements = {'RESTART_SOL': 'YES', 'ITER': str(args.steps),
        'CONV_STARTITER': str(args.steps+1), 'OUTPUT_WRT_FREQ': str(args.steps),
        'HISTORY_OUTPUT': '(ITER, RMS_RES, MAX_RES, AERO_COEFF)',
        'VOLUME_OUTPUT': '(COORDINATES, SOLUTION, PRIMITIVE, RESIDUAL)'}
    for key, value in replacements.items():
        text, count = re.subn(r'^'+key+r'\s*=.*$', f'{key}= {value}', text, flags=re.M)
        assert count == 1, key
    if not re.search(r'^READ_BINARY_RESTART\s*=', text, re.M):
        text += '\nREAD_BINARY_RESTART= NO\n'
    (case/'case.cfg').write_text(text)
    inputs = json.loads((source/'ENTRADAS.json').read_text())
    inputs.update(scope='Forced full-state/residual continuation; not experimental validation',
        parent=source.name, iteration_limit=args.steps,
        changes_from_parent=['ASCII restart from audited finite positive seed',
            f'{args.steps} forced additional iterations; density-only early stop disabled',
            'Export max residual histories and residual fields'],
        physical_models_geometry_freestream_and_schemes_unchanged=True,
        source_audit_sha256=hashlib.sha256((source/'AUDITORIA_SU2.json').read_bytes()).hexdigest(),
        inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in case.iterdir() if p.is_file()})
    (case/'ENTRADAS.json').write_text(json.dumps(inputs, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(case=str(case), parent=source.name, additional_steps=args.steps), indent=2))


if __name__ == '__main__':
    main()
