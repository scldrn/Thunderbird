"""Prepare a bounded official SU2 smoke benchmark, not NASA validation."""
from pathlib import Path
import hashlib
import json
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLS = ROOT/'integracion_apps/SU2'
CASE = HERE/'su2_r1_oficial'


def main():
    assert not CASE.exists(), 'Preserve existing SU2 case'
    source = Path(json.loads((TOOLS/'FUENTE_VERIFICADA.json').read_text())['source_dir'])
    config = source/'TestCases/rans/rae2822/turb_SST_RAE2822.cfg'
    mesh = ROOT/'fuentes/benchmark_SU2_RAE2822/mesh_RAE2822_turb.su2'
    audit = json.loads((HERE/'AUDITORIA_MALLA_SU2.json').read_text())
    assert hashlib.sha256(mesh.read_bytes()).hexdigest() == audit['source_mesh_sha256']
    CASE.mkdir()
    shutil.copy2(mesh,CASE/mesh.name)
    shutil.copy2(config,CASE/'ORIGINAL_turb_SST_RAE2822.cfg')
    text = config.read_text()
    text, n = re.subn(r'^ITER\s*=\s*99999\s*$', 'ITER= 600',text,flags=re.M)
    assert n == 1
    text, n = re.subn(r'^OUTPUT_WRT_FREQ\s*=\s*250\s*$', 'OUTPUT_WRT_FREQ= 200',text,flags=re.M)
    assert n == 1
    assert not re.search(r'^OUTPUT_FILES\s*=',text,re.M)
    text += '\n% Workspace diagnostic output; no model parameter fitting.\nOUTPUT_FILES= (RESTART_ASCII, SURFACE_CSV, PARAVIEW)\n'
    (CASE/'case.cfg').write_text(text)
    metadata=dict(scope='Official SU2 RAE2822 case operability/convergence pilot; not accepted physical validation',
        source_SU2_version='8.6.0', source_config_sha256=hashlib.sha256(config.read_bytes()).hexdigest(),
        source_mesh_sha256=audit['source_mesh_sha256'],iteration_limit=600,counter_is_physical_time=False,
        declared_conditions=dict(Mach=.729,alpha_deg=2.31,Reynolds=6.5e6,chord=1.0,
            T_freestream_K=288.15,turbulence_intensity=.001,eddy_to_molecular_viscosity_ratio=100.0),
        numerics='Official JST + implicit Euler + multigrid3 + FGMRES/LU_SGS + CFL100, unchanged from source case',
        changes_from_official=['iteration limit99999_to600','output interval250_to200','explicit restartASCII/surfaceCSV/ParaView output'],
        pending_defaults_confirmation='Verify actual freestream pressure, gas and viscosity constants and SST variant in runtime output/source before comparing dimensional physics.',
        distinctions_from_NASA_OpenFOAM_case=['T288.15K and chord1 rather than255.5556K and0.3048m.',
            'Freestream turbulent viscosity ratio100 rather than1; model settings and boundary treatment differ.',
            'Official SU2 geometry differs from NASA polygon by up to0.001509chord in one-way vertex distance.',
            'Native node-centred mesh/algorithm differs from the OpenFOAM cell-centred discretization.'],
        physical_validation_accepted=False,vehicle_performance_accepted=False,
        inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CASE.iterdir() if p.is_file()})
    (CASE/'ENTRADAS.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:v for k,v in metadata.items() if not k.endswith('sha256')},indent=2))


if __name__ == '__main__':
    main()
