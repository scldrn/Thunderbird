"""Cross-check stored cone matrix against ray LP and cone nesting."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
continuous=json.loads((HERE/'CONO_CONTINUO.json').read_text())['results']
old45=json.loads((HERE/'ACELERACION_MOMENTOS.json').read_text())['cases']
oldsmall=json.loads((HERE/'SENSIBILIDAD_CONO_ACELERACION.json').read_text())['cases']
indexed={(r['source_index'],r['angle_deg']):r for r in continuous}
gaps=[]; unknown=[]
for r in continuous:
    if r['angle_deg']==45:
        old=next(x for x in old45 if x['source_index']==r['source_index'] and x['acceleration_component_g']==.25)
    else:
        old=next(x for x in oldsmall if x['source_index']==r['source_index'] and x['angle_deg']==r['angle_deg'])
    for c,p in zip(r['corners'],old['corners']):
        assert c['accel_g']==p['accel_g'] and c['moment_Nm']==p['moment_Nm']
        if p['feasible'] is None:unknown.append((r['source_index'],r['angle_deg'],c['status']))
        if p['feasible'] is True:
            assert c['status']=='Solved'
            gap=p['capacity_N']-c['capacity_N']
            assert gap>=-2e-5, (r['source_index'],r['angle_deg'],gap)
            gaps.append(gap)
for idx in range(36):
    r=[indexed[idx,angle] for angle in (35,40,45)]
    for c35,c40,c45 in zip(*(x['corners'] for x in r)):
        if all(c['status']=='Solved' for c in (c35,c40,c45)):
            assert c35['capacity_N']+2e-5>=c40['capacity_N']
            assert c40['capacity_N']+2e-5>=c45['capacity_N']
print('Comparaciones LP/SOCP:',len(gaps),'mayor diferencia N:',max(gaps))
print('Estados LP desconocidos contrastados:',unknown)
