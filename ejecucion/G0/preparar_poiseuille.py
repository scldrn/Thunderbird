"""Newtonian transient verification adapted from Foundation 13's viscoelastic tutorial."""
from pathlib import Path
import shutil,json,re,hashlib
P=Path(__file__).resolve().parent
source=P/'planarPoiseuille_tutorial';case=P/'poiseuille_newtonian_40'
case.mkdir(exist_ok=True)
for folder in ('0','system','constant'):shutil.copytree(source/folder,case/folder,dirs_exist_ok=True)
control=(case/'system/controlDict').read_text().replace('endTime         25;','endTime         4;').replace('writeInterval   1;','writeInterval   4;').replace('writePrecision   8;','writePrecision   12;')
(case/'system/controlDict').write_text(control)
b=(case/'system/blockMeshDict').read_text().replace('simpleGrading (1 4 1)','simpleGrading (1 1 1)');(case/'system/blockMeshDict').write_text(b)
header='FoamFile { format ascii; class dictionary; object momentumTransport; }\n'
(case/'constant/momentumTransport').write_text(header+'simulationType laminar;\n')
# No Maxwell extra stress model in the Newtonian verification.
(case/'0/sigma').unlink(missing_ok=True)
s=(case/'system/fvSolution').read_text().replace('nOuterCorrectors    15;','nOuterCorrectors    2;').replace('nCorrectors         3;','nCorrectors         2;').replace('momentumPredictor   off;','momentumPredictor   on;').replace('1e-6','1e-10')
(case/'system/fvSolution').write_text(s)
(case/'system/functions').write_text('#includeFunc graphCell(name=graph, start=(0 0 0), end=(0 1 0), U)\n')
meta=dict(kind='analytic_solver_verification_not_physical_validation',
          source='OpenFOAM Foundation13 tutorials/incompressibleFluid/planarPoiseuille',
          modifications=['Maxwell model removed; default Newtonian Stokes laminar','uniform y spacing','2 outer/2 inner corrections, tighter linear tolerances','4 s transient window, zero initial velocity'],
          H_m=1.,nu_m2_s=.1,body_acceleration_m_s2=5.,Ny=40,dt_s=.005,end_s=4.,
          geometry='Half-channel wall y=0, symmetry y=H; cyclic x; empty z',
          expected_steady_Ux='G*(H*y-y*y/2)/nu',
          expected_transient_Ux='steady - sum[2G/(H*nu*k_n^3)*sin(k_n*y)*exp(-nu*k_n^2*t)], k_n=(n+.5)*pi/H',
          input_sha256={str(f.relative_to(case)):hashlib.sha256(f.read_bytes()).hexdigest() for f in case.rglob('*') if f.is_file()})
(case/'benchmark_inputs.json').write_text(json.dumps(meta,indent=2))
print(case)
