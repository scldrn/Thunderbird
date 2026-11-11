"""Compare existing hypothetical mass scenarios at vertical hover only."""
import hashlib
import json
from pathlib import Path
from modelo import scenario

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'modelos_integrados/empaquetado_axial_A/masa_y_agilidad/ESCENARIOS.json'
STATIONS_M = {38: (-.300, .275, .065), 60: (-.200, .200, .076), 80: (-.100, .100, .086)}

def compute(data):
    output = []
    for index, record in enumerate(data['scenarios']):
        reserve = int(record['axial_reserve_outer_mm'])
        x0, x1, half_y = STATIONS_M[reserve]
        half_x = (x1 - x0) / 2
        midpoint_x = (x0 + x1) / 2
        x, y, z = record['CG_m']
        result = scenario(data['assumptions']['total_mass_kg'], (x-midpoint_x)/half_x,
                          y/half_y, 0, per_fan_limit_N=21)
        output.append({'source_index': index, 'reserve_mm': reserve,
                       'mode': record['balancing_mode'], 'CG_m': [x,y,z],
                       'station_midpoint_x_m': midpoint_x, 'half_x_m': half_x,
                       'remaining_equipment_x_m': record['remaining_equipment_x_m'],
                       'remaining_zone_m': record['remaining_zone_m'],
                       'remaining_equipment_within_assumed_zone': record['remaining_zone_m'][0] <= record['remaining_equipment_x_m'] <= record['remaining_zone_m'][1],
                       'scenario': result})
    return output

def main():
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    rows = compute(data)
    result = {'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': hashlib.sha256(raw).hexdigest(),
              'description': 'Vertical hover ideal comparison, no moments reserved; hypothetical masses', 'cases': rows}
    (HERE/'MASAS_INTEGRADAS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for reserve in STATIONS_M:
        for mode in ('remaining_equipment_at_x0','x_CG_balanced'):
            subset=[r for r in rows if r['reserve_mm']==reserve and r['mode']==mode]
            feasible=[r for r in subset if r['scenario']['cap_feasible_common_direction'] and r['remaining_equipment_within_assumed_zone']]
            print(reserve,mode,'feasible',len(feasible),'/',len(subset),
                  'CG x mm',round(min(r['CG_m'][0] for r in subset)*1000,1),round(max(r['CG_m'][0] for r in subset)*1000,1),
                  'P W',round(min(r['scenario']['min_ideal_W'] for r in subset)),round(max(r['scenario']['min_ideal_W'] for r in subset)))

if __name__ == '__main__':
    main()
