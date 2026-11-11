"""Continue finite official-case fields with the supplied adaptive-CFL controls."""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil

import numpy as np

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'su2_r1_oficial'
CASE=HERE/'su2_r2_adaptativo'


def main():
    assert not CASE.exists(), 'Inspect existing continuation'
    terminal=json.loads((SOURCE/'EJECUCION.json').read_text())
    assert terminal['stage']=='solver_exited' and terminal['exit_code']==0
    with (SOURCE/'restart_flow.csv').open() as f:
        rows=csv.reader(f);header=[s.strip() for s in next(rows)]
        a=np.array([[float(x) for x in row] for row in rows if row])
    d={k:a[:,i] for i,k in enumerate(header)}
    assert np.isfinite(a).all()
    rho=d['Density'];assert rho.min()>0
    v2=(d['Momentum_x']**2+d['Momentum_y']**2)/rho**2
    p=.4*(d['Energy']-.5*rho*v2-rho*d['Turb_Kin_Energy'])
    assert p.min()>0, 'Do not use an inadmissible thermodynamic seed'
    CASE.mkdir()
    for name in ('mesh_RAE2822_turb.su2','ORIGINAL_turb_SST_RAE2822.cfg'):
        shutil.copy2(SOURCE/name,CASE/name)
    shutil.copy2(SOURCE/'restart_flow.csv',CASE/'solution_flow.csv')
    text=(SOURCE/'case.cfg').read_text()
    for pattern,replacement in [(r'^RESTART_SOL\s*=\s*NO\s*$','RESTART_SOL= YES'),
                                (r'^ITER\s*=\s*600\s*$','ITER= 2000'),
                                (r'^CFL_ADAPT\s*=\s*NO\s*$','CFL_ADAPT= YES'),
                                (r'^OUTPUT_WRT_FREQ\s*=\s*200\s*$','OUTPUT_WRT_FREQ= 500')]:
        text,n=re.subn(pattern,replacement,text,flags=re.M);assert n==1
    text+='''\nREAD_BINARY_RESTART= NO
HISTORY_OUTPUT= (ITER, RMS_RES, AERO_COEFF)
VOLUME_OUTPUT= (COORDINATES, SOLUTION, PRIMITIVE)
VOLUME_OUTPUT_PRECISION= DOUBLE
'''
    (CASE/'case.cfg').write_text(text)
    metadata=json.loads((SOURCE/'ENTRADAS.json').read_text())
    metadata.update(scope='Native SU2 continuation from finite unconverged600-step seed; not physical validation',
        iteration_limit=2000,counter_restart_note='New inner counter0..1999; up to2000 additional iterations after source600, not physical time',
        parent=SOURCE.name,changes_from_parent=['CFL_ADAPT NO_toYES using existing official parameters0.9/1.1/1/100/0.1',
        'ASCII restart from source600-step field','additional2000iteration limit','richer history/primitive output in double precision'],
        physical_models_geometry_and_freestream_unchanged=True,
        source_seed_checks=dict(all_conserved_fields_finite=True,minimum_rho_kg_m3=float(rho.min()),
            minimum_p_reconstructed_Pa=float(p.min()),formula='p=(gamma-1)*(rhoE-|momentum|^2/(2rho)-rho*k), from SU2 CNSVariable::SetPrimVar; gamma1.4'),
        inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CASE.iterdir() if p.is_file()})
    (CASE/'ENTRADAS.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(dict(case=str(CASE),source=SOURCE.name,additional_iteration_limit=2000,
                         source_minimum_p_Pa=float(p.min())),indent=2))


if __name__=='__main__':
    main()
