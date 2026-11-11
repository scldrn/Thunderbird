"""Joint ideal acceleration/torque boxes, not physical vehicle performance."""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from reserva_momentos import G, solve, SOURCE, STATIONS_M

HERE=Path(__file__).resolve().parent

def main():
    raw=SOURCE.read_bytes()
    mass=json.loads(raw)
    rows=[]
    for idx,r in enumerate(mass['scenarios']):
        reserve=int(r['axial_reserve_outer_mm']); x0,x1,y=STATIONS_M[reserve]
        centres=np.array(list(itertools.product([x0,x1],[-y,y],[0.])))
        cg=np.array(r['CG_m']); zone=r['remaining_zone_m'][0]<=r['remaining_equipment_x_m']<=r['remaining_zone_m'][1]
        for alpha in (.25,.5):
            corners=[]
            for accel in itertools.product((-alpha,alpha),repeat=3):
                force=5*G*np.array([accel[0],accel[1],1+accel[2]])
                for moment in itertools.product((-.5,.5),repeat=3):
                    output=solve(centres,cg,moment,force_N=force)
                    corners.append({'accel_g':accel,'moment_Nm':moment,**output})
            all_solved=all(c['feasible'] for c in corners)
            worst=max(c['capacity_N'] for c in corners) if all_solved else None
            rows.append({'source_index':idx,'reserve_mm':reserve,'mode':r['balancing_mode'],
                         'acceleration_component_g':alpha,'equipment_within_assumed_zone':zone,
                         'corners':corners,'all_corners_solved':all_solved,'capacity_N':worst,
                         'certified_21N_and_zone':bool(all_solved and worst<=21+1e-8 and zone)})
        print('completed',idx+1,'of',len(mass['scenarios']),flush=True)
    out={'source_sha256':hashlib.sha256(raw).hexdigest(),
         'allocation_sha256':hashlib.sha256((HERE/'reserva_momentos.py').read_bytes()).hexdigest(),
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'scope':'5kg, acceleration box in body frame, simultaneous ±0.5 Nm moment box; ideal inner cone',
         'cases':rows}
    (HERE/'ACELERACION_MOMENTOS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    for reserve,mode,alpha in itertools.product(STATIONS_M,('remaining_equipment_at_x0','x_CG_balanced'),(.25,.5)):
        rs=[r for r in rows if (r['reserve_mm'],r['mode'],r['acceleration_component_g'])==(reserve,mode,alpha)]
        vals=[r['capacity_N'] for r in rs if r['capacity_N'] is not None]
        print(reserve,mode,alpha,'certified',sum(r['certified_21N_and_zone'] for r in rs),'/',len(rs),
              'capacity',round(min(vals),2) if vals else None,round(max(vals),2) if vals else None,flush=True)

if __name__=='__main__':main()
