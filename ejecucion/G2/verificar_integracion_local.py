"""Radial integration sensitivity for selected local-law screening points."""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from bem_hover import Polar
from ley_elemento_rotor import local_loads

HERE = Path(__file__).resolve().parent


def main():
    out = HERE/'cargas_locales_C02_r1/INTEGRACION.json'
    assert not out.exists(), 'Preserve prior integration evidence'
    points = json.loads((out.parent/'ANILLOS.json').read_text())
    report = json.loads((out.parent/'PROCEDENCIA.json').read_text())
    key = 'ejecucion/G2/ley_elemento_rotor.py'
    assert hashlib.sha256((HERE/'ley_elemento_rotor.py').read_bytes()).hexdigest() == report['input_sha256'][key]
    design = json.loads((HERE/'modulo_preliminar/m5_d1_k0.85.json').read_text())['design']
    radial = [r['r_m'] for r in design['annuli']]
    chord = [r['chord_m'] for r in design['annuli']]
    beta = [r['beta_rad'] for r in design['annuli']]
    polar = Polar();R = design['radius_m'];cases = []
    for point in points:
        s = point['summary']
        if s['rpm_factor'] not in (.5,1.) or s['axial_disk_velocity_m_s'] not in (20.,40.):
            continue
        results = []
        for n in (64,128,256):
            dr = R*(1-s['hub_ratio'])/n
            radii = s['hub_ratio']*R+(np.arange(n)+.5)*dr
            rows = [local_loads(float(r),float(np.interp(r,radial,chord)),float(np.interp(r,radial,beta)),
                                s['rpm']*math.pi/30,s['axial_disk_velocity_m_s'],0.,8,1.225,polar) for r in radii]
            T = sum(r['dT_dr_N_m'] for r in rows)*dr
            P = sum(r['shaft_power_per_radius_W_m'] for r in rows)*dr
            assert np.isfinite([T,P]).all()
            results.append(dict(annuli=n,T_N=T,P_estimate_W=P))
        np.testing.assert_allclose([results[1]['T_N'],results[1]['P_estimate_W']],
                                  [s['local_integral_T_N'],s['local_integral_shaft_estimate_W']],rtol=1e-12,atol=1e-10)
        delta = {k:abs(results[1][k]-results[2][k])/max(abs(results[2][k]),1e-12) for k in ('T_N','P_estimate_W')}
        cases.append(dict(hub_ratio=s['hub_ratio'],rpm=s['rpm'],axial_disk_velocity_m_s=s['axial_disk_velocity_m_s'],
                          quadratures=results,relative_change_128_to_256=delta))
    result = dict(scope='Midpoint radial quadrature sensitivity only; not physical model accuracy',
                  cases=cases,all_128_results_reproduce_frozen_screen=True,
                  maximum_relative_change_128_to_256={k:max(r['relative_change_128_to_256'][k] for r in cases) for k in ('T_N','P_estimate_W')},
                  model_extrapolation_and_compressibility_not_resolved=True)
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(cases=len(cases),max_changes=result['maximum_relative_change_128_to_256']),indent=2))


if __name__ == '__main__':
    main()
