"""Static 3-axis moment-box screening for hypothetical mass scenarios."""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from integrar_masas import SOURCE, STATIONS_M

HERE = Path(__file__).resolve().parent
G = 9.80665

def solve(centres, cg, target_moment, angle_deg=45., preload_N=1., force_N=None):
    """Minimize common ray-coefficient capacity, a conservative ideal model."""
    rays = [[0., 0., 1.]]
    for angle in np.linspace(0, math.radians(angle_deg), 5)[1:]:
        for az in np.arange(32)*2*math.pi/32:
            rays.append([math.sin(angle)*math.cos(az), math.sin(angle)*math.sin(az), math.cos(angle)])
    rays = np.array(rays)
    k = len(rays)
    blocks = []
    for point in centres:
        x, y = point[0]-cg[0], point[1]-cg[1]
        # Same separate lateral-force moment arms as the earlier A study.
        zx, zy = -.039-cg[2], -.021-cg[2]
        b = np.array([[1,0,0],[0,1,0],[0,0,1],[0,-zy,y],[zx,0,-x],[-y,x,0]])
        blocks.append(b @ rays.T)
    aeq = np.column_stack((np.hstack(blocks),np.zeros(6)))
    target = np.array([*(force_N if force_N is not None else (0.,0.,5*G)),*target_moment])
    aub = np.zeros((8,4*k+1)); bub = np.r_[np.zeros(4),-np.full(4,preload_N)]
    for i in range(4):
        aub[i,i*k:(i+1)*k]=1.; aub[i,-1]=-1.
        aub[i+4,i*k:(i+1)*k]=-rays[:,2]
    objective = np.r_[np.zeros(4*k),1.]
    sol = linprog(objective,A_ub=aub,b_ub=bub,A_eq=aeq,b_eq=target,bounds=(0,None),method='highs')
    if not sol.success:
        if sol.status != 2:
            raise RuntimeError(f'LP failed: {sol.status} {sol.message}')
        return {'feasible':False, 'solver_status':int(sol.status), 'capacity_N':None}
    if not np.isfinite(sol.x).all():
        raise ArithmeticError('non-finite LP solution')
    forces = np.array([rays.T@sol.x[i*k:(i+1)*k] for i in range(4)])
    residual = float(np.max(np.abs(aeq@sol.x-target)))
    inequality_residual = float(np.max(aub@sol.x-bub))
    if not np.isfinite(residual) or not np.isfinite(inequality_residual) or residual>1e-7 or inequality_residual>1e-7:
        raise ArithmeticError('invalid LP solution')
    return {'feasible':True,'solver_status':int(sol.status),'capacity_N':float(sol.x[-1]),
            'fan_forces_N':forces.tolist(),'max_residual':residual}

def calculate(data):
    result=[]
    for idx,row in enumerate(data['scenarios']):
        reserve=int(row['axial_reserve_outer_mm']); x0,x1,y=STATIONS_M[reserve]
        centres=np.array(list(itertools.product([x0,x1],[-y,y],[0.])))
        cg=np.array(row['CG_m'])
        corners=[]
        for moment in itertools.product((-.5,.5),repeat=3):
            corners.append({'moment_Nm':list(moment),**solve(centres,cg,moment)})
        all_solved=all(c['feasible'] for c in corners)
        worst=max((c['capacity_N'] for c in corners),default=None) if all_solved else None
        zone=row['remaining_zone_m'][0]<=row['remaining_equipment_x_m']<=row['remaining_zone_m'][1]
        result.append({'source_index':idx,'reserve_mm':reserve,'mode':row['balancing_mode'],
                       'CG_m':row['CG_m'],'equipment_within_assumed_zone':zone,'corners':corners,
                       'max_required_capacity_N':worst,
                       'passes_21N_and_zone':bool(all_solved and worst<=21.+1e-8 and zone)})
    return result

def main():
    raw=SOURCE.read_bytes(); cases=calculate(json.loads(raw))
    output={'source_sha256':hashlib.sha256(raw).hexdigest(), 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'assumptions':'5kg, hover, 45deg inner ray cone, 1N vertical preload, torque box ±0.5Nm, ideal lever arms, no dynamics', 'cases':cases}
    (HERE/'RESERVA_MOMENTOS.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    for reserve,mode in itertools.product(STATIONS_M,('remaining_equipment_at_x0','x_CG_balanced')):
        rows=[r for r in cases if r['reserve_mm']==reserve and r['mode']==mode]
        vals=[r['max_required_capacity_N'] for r in rows if r['max_required_capacity_N'] is not None]
        print(reserve,mode,'pass',sum(r['passes_21N_and_zone'] for r in rows),'/',len(rows),
              'capacity range N',round(min(vals),3) if vals else None,round(max(vals),3) if vals else None,flush=True)

if __name__=='__main__': main()
