"""Check force partition and reference-point transforms on saved CFD fields."""
from pathlib import Path
import json
import numpy as np
from analizar_series_transitorias import NUM,read_series

ROOT=Path(__file__).resolve().parent
case=ROOT/'auditoria_reaccion_Euler_t0.0005'
pp=case/'postProcessing'
loads={}
for folder in sorted(pp.glob('load_*')):
    files=list(folder.glob('*/forces.dat'))
    if len(files)!=1:raise ValueError(f'Expected one saved time in {folder}')
    rows=[np.array([float(x) for x in NUM.findall(s)]) for s in files[0].read_text().splitlines() if s.strip() and not s.startswith('#')]
    if len(rows)!=1 or len(rows[0])!=13:raise ValueError('Expected one complete pressure/viscous record')
    a=rows[0]
    if abs(a[0]-.0005)>1e-12:raise ValueError('Wrong snapshot time')
    loads[folder.name.removeprefix('load_')]=dict(force_N=(a[1:4]+a[4:7]).tolist(),moment_origin_Nm=(a[7:10]+a[10:13]).tolist())
names=[f'vane{axis}{j}' for axis in 'XY' for j in range(3)]
checks=[]
for quantity,tol in [('force_N',5e-6),('moment_origin_Nm',5e-8)]:
    individual=sum(np.array(loads[n][quantity]) for n in names)
    grouped=np.array(loads['vanes'][quantity])
    total=np.array(loads['all_solid'][quantity])
    wall=np.array(loads['walls'][quantity])
    np.testing.assert_allclose(individual,grouped,rtol=0,atol=tol)
    np.testing.assert_allclose(grouped+wall,total,rtol=0,atol=tol)
    checks.append(dict(quantity=quantity,individual_sum_error_max=float(max(abs(individual-grouped))),wall_plus_vanes_error_max=float(max(abs(grouped+wall-total))),absolute_tolerance=tol))
for name in names:
    a,_=read_series(ROOT/'snapshots_pareados/euler','force_'+name,'forces.dat',13)
    index=np.flatnonzero(abs(a[:,0]-.0005)<1e-12)
    if len(index)!=1:raise ValueError('Matching live force sample missing or ambiguous')
    row=a[index[0]];f=row[1:4]+row[4:7];m=row[7:10]+row[10:13]
    offset=[-.022,0,.022][int(name[-1])]
    center=np.array([0,offset,-.012] if 'X' in name else [offset,0,-.040])
    np.testing.assert_allclose(f,loads[name]['force_N'],rtol=0,atol=5e-6)
    np.testing.assert_allclose(m+np.cross(center,f),loads[name]['moment_origin_Nm'],rtol=0,atol=5e-8)
v=np.array(loads['vanes']['force_N']);w=np.array(loads['walls']['force_N']);s=np.array(loads['all_solid']['force_N'])
out=dict(snapshot_time_s=.0005,physical_loads_accepted=False,loads=loads,partition_checks=checks,
         six_reference_point_transforms_verified=True,
         lateral_magnitude_vanes_N=float(np.linalg.norm(v[:2])),
         lateral_magnitude_all_solids_N=float(np.linalg.norm(s[:2])),
         lateral_magnitude_ratio=float(np.linalg.norm(s[:2])/np.linalg.norm(v[:2])),
         interpretation='Underdeveloped isolated channel snapshot: wall reactions materially change local vane sums. Not an installed thrust measurement.',
         implementation='OpenFOAM Foundation13 forcesBase.C: pressure rho(p)*Sf*(p-pRef); moments about common origin; rhoInf=1.225 kg/m3.',
         scope_limits=['no rotor or exterior forces','no temporal/mesh independence','no closed control-volume momentum check','no actual actuator response'])
(case/'REACTION_AUDIT.json').write_text(json.dumps(out,indent=2,allow_nan=False))
print(json.dumps({k:out[k] for k in ('lateral_magnitude_vanes_N','lateral_magnitude_all_solids_N','lateral_magnitude_ratio','six_reference_point_transforms_verified','physical_loads_accepted')},indent=2))
