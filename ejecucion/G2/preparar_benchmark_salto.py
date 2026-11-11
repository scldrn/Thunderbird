"""Check the fanPressureJump operator against the verified Poiseuille PDE.

Two opposite jump orientations, no body acceleration; no vehicle solver run.
"""
from pathlib import Path
import hashlib
import json
import shutil

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'G0/poiseuille_40_outer50'
OUT=HERE/'benchmark_salto'
OUT.mkdir(exist_ok=True)


def main():
    for reverse in (False,True):
        case=OUT/('fan_jump_reverse' if reverse else 'fan_jump_forward')
        if (case/'4/U').exists():raise RuntimeError('Preserve existing result before regeneration')
        for folder in ('0','constant','system'):
            shutil.copytree(SOURCE/folder,case/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('polyMesh'))
        (case/'constant/fvModels').write_text('FoamFile { format ascii; class dictionary; object fvModels; }\n')
        p=(case/'0/p').read_text()
        blocks=''
        for name in ('left','right'):
            blocks+=f'''    {name}
    {{
        type fanPressureJump;
        patchType cyclic;
        fanCurve constant 1;
        reverse {'true' if reverse else 'false'};
        jump uniform 0;
        value uniform 0;
    }}
'''
        p=p.replace('    #includeEtc',blocks+'    #includeEtc')
        (case/'0/p').write_text(p)
        metadata=dict(kind='fan_operator_verification_not_rotor_or_vehicle_validation',
            reference_case=str(SOURCE),reference_operator='G=abs(jump)/L=5 m/s2',
            jump_kinematic_m2_s2=1.,physical_pressure_jump_at_rho_1_225_Pa=1.225,
            reverse=reverse,Ny=40,dt_s=.005,outer_correctors=50,end_s=4.,
            input_sha256={str(p.relative_to(case)):hashlib.sha256(p.read_bytes()).hexdigest() for p in case.rglob('*') if p.is_file()})
        (case/'ENTRADAS.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (OUT/'run.sh').write_text('''#!/bin/bash
set -e
source /opt/openfoam13/etc/bashrc
for case in /tmp/fan_jump_forward /tmp/fan_jump_reverse
do
    cd "$case"
    blockMesh > log.blockMesh 2>&1
    foamRun > log.foamRun 2>&1
done
''')
    print(OUT)


if __name__=='__main__':main()
