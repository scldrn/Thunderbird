"""Compare joint wrench certificates for reduced hypothetical force cones."""
import hashlib
import json
import itertools
from pathlib import Path
import numpy as np
from reserva_momentos import G, solve, SOURCE, STATIONS_M

HERE = Path(__file__).resolve().parent
BASE = HERE/'ACELERACION_MOMENTOS.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source = json.loads(SOURCE.read_text())
    base = json.loads(BASE.read_text())
    if base['source_sha256'] != digest(SOURCE) or base['allocation_sha256'] != digest(HERE/'reserva_momentos.py'):
        raise ValueError('Baseline provenance does not match current inputs')
    rows=[]
    for idx,r in enumerate(source['scenarios']):
        reserve=int(r['axial_reserve_outer_mm']); x0,x1,y=STATIONS_M[reserve]
        centres=np.array(list(itertools.product([x0,x1],[-y,y],[0.])))
        cg=np.array(r['CG_m'])
        baseline=next(b for b in base['cases'] if b['source_index']==idx and b['acceleration_component_g']==.25)
        for angle in (35.,40.):
            corners=[]
            for b in baseline['corners']:
                accel=b['accel_g']; moment=b['moment_Nm']
                force=5*G*np.array([accel[0],accel[1],1+accel[2]])
                try:
                    sol=solve(centres,cg,moment,angle_deg=angle,force_N=force)
                except RuntimeError as error:
                    sol={'feasible':None,'capacity_N':None,'solver_error':str(error)}
                corners.append({'accel_g':accel,'moment_Nm':moment,'capacity_N':sol['capacity_N'],
                                'feasible':sol['feasible'],'max_residual':sol.get('max_residual'),
                                'solver_error':sol.get('solver_error'),'baseline_45_capacity_N':b['capacity_N']})
            all_ok=all(c['feasible'] is True for c in corners)
            worst=max(c['capacity_N'] for c in corners) if all_ok else None
            rows.append({'source_index':idx,'reserve_mm':reserve,'mode':r['balancing_mode'],
                         'angle_deg':angle,'corners':corners,'all_corners_solved':all_ok,
                         'capacity_N':worst,'equipment_within_assumed_zone':baseline['equipment_within_assumed_zone'],
                         'certified_21N_and_zone':bool(all_ok and worst<=21.+1e-8 and baseline['equipment_within_assumed_zone'])})
        print('completed',idx+1,'of',len(source['scenarios']),flush=True)
    for reserve,mode,angle in itertools.product(STATIONS_M,('remaining_equipment_at_x0','x_CG_balanced'),(35.,40.)):
        group=[r for r in rows if (r['reserve_mm'],r['mode'],r['angle_deg'])==(reserve,mode,angle)]
        vals=[r['capacity_N'] for r in group if r['capacity_N'] is not None]
        print(reserve,mode,angle,'certified',sum(r['certified_21N_and_zone'] for r in group),'/ 6',
              'capacity N',round(min(vals),2) if vals else None,round(max(vals),2) if vals else None,flush=True)
    out={'source_sha256':digest(SOURCE),'baseline_sha256':digest(BASE),
         'allocator_sha256':digest(HERE/'reserva_momentos.py'),'script_sha256':digest(Path(__file__)),
         'scope':'5 kg, ±0.25 g per axis and ±0.5 Nm moments, cone sensitivity; hypothetical ideal', 'cases':rows}
    (HERE/'SENSIBILIDAD_CONO_ACELERACION.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')

if __name__=='__main__': main()
