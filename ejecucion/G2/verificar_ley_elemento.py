"""Analytic vector-work cases and bridge to frozen, verified BEM annuli."""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from bem_hover import Polar
from ley_elemento_rotor import local_loads

HERE = Path(__file__).resolve().parent


class ConstantPolar:
    def __init__(self, cl, cd):
        self.cl, self.cd = cl, cd

    def lookup(self, alpha_deg, reynolds):
        return self.cl, self.cd, True


def main():
    out = HERE/'ley_elemento_verificacion_r2'
    assert not out.exists(), 'Preserve prior operator verification'
    out.mkdir()
    cases = []
    for cl, cd in [(1.,0.),(1.,.02),(-.2,.05)]:
        for swirl in (0.,5.,-5.):
            r,c,omega,axial,rho,B = .03,.01,3000.,20.,1.225,8
            row = local_loads(r,c,.3,omega,axial,swirl,B,rho,ConstantPolar(cl,cd))
            # Cartesian vector projection oracle, independent of the law's
            # sine/cosine expressions and energy calculation.
            w = np.array([axial,omega*r-swirl])
            W = np.linalg.norm(w)
            q = .5*rho*W**2*c*B
            expected = q*(cl*np.array([w[1],w[0]])+cd*np.array([-w[0],w[1]]))/W
            np.testing.assert_allclose([row['dT_dr_N_m'],row['dFtheta_dr_N_m']],expected,rtol=1e-13,atol=1e-12)
            shaft = expected[1]*(omega*r)
            mean = expected@np.array([axial,swirl])
            np.testing.assert_allclose(shaft-mean,q*cd*W,rtol=1e-12,atol=1e-10)
            np.testing.assert_allclose(row['energy_identity_residual_W_m'],0.,rtol=0,atol=1e-10)
            cases.append(row)
    source = HERE/'modulo_preliminar/m5_d1_k0.85.json'
    design = json.loads(source.read_text())['design']
    omega = design['rpm']*math.pi/30
    polar = Polar()
    bridge = []
    for old in design['annuli']:
        row = local_loads(old['r_m'],old['chord_m'],old['beta_rad'],omega,
                          old['vi_m_s'],old['swirl_at_disk_m_s'],8,1.225,polar)
        np.testing.assert_allclose([row['dT_dr_N_m'],row['dQ_dr_Nm_m']],
                                  [old['dT_dr_N_m'],old['dQ_dr_Nm_m']],rtol=1e-10,atol=1e-10)
        bridge.append(row)
    rejected = []
    for axial,swirl in [(0.,0.),(-1.,0.),(20.,90.),(20.,100.)]:
        try:
            local_loads(.03,.01,.3,3000.,axial,swirl,8,1.225,ConstantPolar(1.,.02))
        except ValueError:
            rejected.append([axial,swirl])
    assert len(rejected) == 4
    report = dict(scope='Local force/torque/work algebra and frozen-BEM bridge; no physical rotor validation',
                  analytic_vector_cases=cases, frozen_BEM_annuli_checked=len(bridge),
                  unsupported_forward_branch_cases_rejected=rejected,
                  source_design_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  induced_velocity_not_added_twice=True, CFD_source_applied=False,
                  source_code_sha256=hashlib.sha256((HERE/'ley_elemento_rotor.py').read_bytes()).hexdigest())
    (out/'AUDITORIA.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(analytic_cases=len(cases),BEM_annuli=len(bridge),rejected_cases=len(rejected),physical_validation=False),indent=2))


if __name__ == '__main__':
    main()
