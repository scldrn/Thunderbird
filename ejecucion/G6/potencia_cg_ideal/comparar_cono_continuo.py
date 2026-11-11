"""Recompute joint wrench-box corners against continuous ideal SOCP."""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from reserva_momentos import G,SOURCE,STATIONS_M
from cono_continuo import solve_continuous

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    data=json.loads(SOURCE.read_text());results=[]
    for idx,row in enumerate(data['scenarios']):
        reserve=int(row['axial_reserve_outer_mm']);x0,x1,y=STATIONS_M[reserve]
        points=np.array(list(itertools.product([x0,x1],[-y,y],[0.])))
        zone=row['remaining_zone_m'][0]<=row['remaining_equipment_x_m']<=row['remaining_zone_m'][1]
        for angle in (35,40,45):
            corners=[]
            for accel in itertools.product((-.25,.25),repeat=3):
                force=5*G*np.array([accel[0],accel[1],1+accel[2]])
                for moment in itertools.product((-.5,.5),repeat=3):
                    sol=solve_continuous(points,np.array(row['CG_m']),moment,force,angle)
                    corners.append({'accel_g':accel,'moment_Nm':moment,**sol})
            all_solved=all(c['status']=='Solved' for c in corners)
            cap=max(c['capacity_N'] for c in corners) if all_solved else None
            results.append({'source_index':idx,'reserve_mm':reserve,'mode':row['balancing_mode'],
                            'angle_deg':angle,'zone_ok':zone,'corners':corners,'capacity_N':cap,
                            'certified_21N_and_zone':bool(all_solved and cap<=21.+1e-6 and zone)})
        print('completed',idx+1,'/',len(data['scenarios']),flush=True)
    out={'source_sha256':sha(SOURCE),'model_sha256':sha(HERE/'cono_continuo.py'),
         'script_sha256':sha(Path(__file__)),'solver':'Clarabel 0.11.1; SOCP continuous cones',
         'scope':'5kg, ±0.25g per acceleration component and ±0.5Nm per moment component, ideal static forces',
         'results':results}
    (HERE/'CONO_CONTINUO.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    for reserve,mode,angle in itertools.product(STATIONS_M,('remaining_equipment_at_x0','x_CG_balanced'),(35,40,45)):
        g=[r for r in results if (r['reserve_mm'],r['mode'],r['angle_deg'])==(reserve,mode,angle)]
        cap=[r['capacity_N'] for r in g if r['capacity_N'] is not None]
        print(reserve,mode,angle,sum(r['certified_21N_and_zone'] for r in g),'/6',
              round(min(cap),3) if cap else None,round(max(cap),3) if cap else None,flush=True)

if __name__=='__main__':main()
