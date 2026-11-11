"""Ideal free-disk proxy for saved SOCP forces, not an installed fan model."""
import hashlib
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'CONO_CONTINUO.json'
RHO=1.225
DIAMETER_M=.082

def ideal_power(forces,rho=RHO,diameter_m=DIAMETER_M):
    if rho<=0 or diameter_m<=0 or len(forces)!=4:
        raise ValueError('invalid disk parameters or force count')
    area=math.pi*diameter_m**2/4
    magnitudes=[math.sqrt(sum(v*v for v in f)) for f in forces]
    if any(not math.isfinite(v) for v in magnitudes):raise ValueError('nonfinite force')
    return sum(t**1.5 for t in magnitudes)/math.sqrt(2*rho*area)

def battery_illustration(power_W, seconds, efficiency=.6, energy_Wh_kg=150., specific_power_W_kg=5000.):
    if min(power_W,seconds)<0 or not 0<efficiency<=1 or min(energy_Wh_kg,specific_power_W_kg)<=0:
        raise ValueError('invalid battery scenario')
    electrical=power_W/efficiency
    mass_energy=electrical*seconds/(3600*energy_Wh_kg)
    mass_power=electrical/specific_power_W_kg
    return {'electrical_W_assumed':electrical,'energy_Wh':electrical*seconds/3600,
            'mass_energy_kg':mass_energy,'mass_power_kg':mass_power,'mass_lower_assumption_kg':max(mass_energy,mass_power)}

def main():
    raw=SOURCE.read_bytes();data=json.loads(raw);rows=[]
    for r in data['results']:
        if not r['certified_21N_and_zone']:continue
        corners=[]
        for c in r['corners']:
            if c['status']!='Solved':raise ValueError('incomplete certified box')
            corners.append({'accel_g':c['accel_g'],'moment_Nm':c['moment_Nm'],
                            'power_W':ideal_power(c['fan_forces_N'])})
        worst=max(corners,key=lambda c:c['power_W'])
        rows.append({'source_index':r['source_index'],'reserve_mm':r['reserve_mm'],'angle_deg':r['angle_deg'],
                     'mode':r['mode'],'corners':corners,'worst_corner':worst,
                     'battery_scenarios':{str(s):battery_illustration(worst['power_W'],s) for s in (30,120,300)}})
    out={'source_sha256':hashlib.sha256(raw).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'scope':'Power proxy for one minimum-max-force allocation per vertex; ideal free disks, not installed power or optimum',
         'rho_kg_m3':RHO,'disk_diameter_m':DIAMETER_M,'battery_assumptions':{'efficiency':.6,'usable_Wh_kg':150,'W_kg':5000},
         'cases':rows}
    (HERE/'POTENCIA_FUERZAS_SOCP.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    for reserve in (38,60,80):
        for angle in (35,40,45):
            g=[r for r in rows if r['reserve_mm']==reserve and r['angle_deg']==angle]
            if g:print(reserve,angle,'n',len(g),'power W',round(min(r['worst_corner']['power_W'] for r in g)),round(max(r['worst_corner']['power_W'] for r in g)),flush=True)

if __name__=='__main__':main()
