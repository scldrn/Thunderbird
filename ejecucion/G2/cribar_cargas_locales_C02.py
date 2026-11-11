"""Identified C02 blade-section screening versus prescribed disk velocity.

No induced velocity is added. Not a free-rotor or installed fan curve.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from bem_hover import Polar
from ley_elemento_rotor import local_loads

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    out = HERE/'cargas_locales_C02_r1'
    assert not out.exists(), 'Preserve previous local-law screening'
    audit = json.loads((HERE/'ley_elemento_verificacion_r2/AUDITORIA.json').read_text())
    assert audit['frozen_BEM_annuli_checked'] == 64
    source = HERE/'modulo_preliminar/m5_d1_k0.85.json'
    design = json.loads(source.read_text())['design']
    manifest_path = ROOT/'ejecucion/G3/C02/salida/C02_D82_neutro/MANIFIESTO.json'
    module = json.loads(manifest_path.read_text())
    rotor_path = HERE/'modulo_preliminar/CAD/rotor_8palas_D82mm_CCW.step'
    assert hashlib.sha256(rotor_path.read_bytes()).hexdigest() == module['source_rotor_sha256']
    geometry_path = HERE/'flujo_C02_conducto/neutro_r1/GEOMETRIA.json'
    geometry = json.loads(geometry_path.read_text())
    R = module['parameters']['rotor_R']*.001
    hub = geometry['sealed_hub_R_m']
    assert math.isclose(R,design['radius_m']) and math.isclose(hub/R,.315)
    radial = np.array([r['r_m'] for r in design['annuli']])
    chords = np.array([r['chord_m'] for r in design['annuli']])
    twists = np.array([r['beta_rad'] for r in design['annuli']])
    polar = Polar()
    out.mkdir()
    rows, detailed = [], []
    for hub_ratio in (.30,.315):
        dr = R*(1-hub_ratio)/128
        radii = hub_ratio*R+(np.arange(128)+.5)*dr
        active_area = math.pi*R**2*(1-hub_ratio**2)
        for rpm_factor in (.5,.75,1.):
            omega = design['rpm']*rpm_factor*math.pi/30
            for axial in (5.,10.,20.,30.,40.,50.,60.):
                sections = [local_loads(float(r),float(np.interp(r,radial,chords)),
                            float(np.interp(r,radial,twists)),omega,axial,0.,8,1.225,polar)
                            for r in radii]
                T = np.array([r['dT_dr_N_m'] for r in sections])
                Q = np.array([r['dQ_dr_Nm_m'] for r in sections])
                P = np.array([r['shaft_power_per_radius_W_m'] for r in sections])
                work = np.array([r['mean_force_work_per_radius_W_m'] for r in sections])
                deficit = np.array([r['profile_work_deficit_per_radius_W_m'] for r in sections])
                valid = np.array([r['polar_in_domain'] for r in sections])
                Mach = np.array([r['Mach_relative'] for r in sections])
                def fraction(weights, mask):
                    return float(abs(weights[mask]).sum()/abs(weights).sum()) if abs(weights).sum() else None
                assert np.isfinite(T).all() and np.isfinite(Q).all()
                np.testing.assert_allclose(P,work+deficit,rtol=1e-12,atol=1e-8)
                row = dict(hub_ratio=hub_ratio,rpm_factor=rpm_factor,rpm=omega*30/math.pi,
                           axial_disk_velocity_m_s=axial,swirl_disk_velocity_m_s=0.,
                           active_annular_area_m2=active_area,uniform_active_annular_Q_m3_s=active_area*axial,
                           local_integral_T_N=float(T.sum()*dr),local_integral_Q_Nm=float(Q.sum()*dr),
                           local_integral_shaft_estimate_W=float(P.sum()*dr),
                           local_integral_mean_force_work_W=float(work.sum()*dr),
                           local_integral_profile_deficit_W=float(deficit.sum()*dr),
                           outside_polar_abs_thrust_fraction=fraction(T,~valid),
                           outside_polar_abs_torque_fraction=fraction(Q,~valid),
                           Mach_gt_0p3_abs_torque_fraction=fraction(Q,Mach>.3),
                           max_relative_Mach=float(Mach.max()),
                           all_sections_in_polar=bool(valid.all()),
                           prescribed_uniform_disk_velocity_not_free_stream=True,
                           installed_map_accepted=False)
                rows.append(row);detailed.append(dict(summary=row,sections=sections))
    with (out/'CRIBADO.csv').open('w',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (out/'ANILLOS.json').write_text(json.dumps(detailed,indent=2,allow_nan=False)+'\n')
    area_change = (1-.315**2)/(1-.30**2)-1
    report = dict(scope='Local blade law with prescribed uniform disk velocity; not a physical fan curve',
                  operating_points=len(rows),annuli_per_point=128,
                  original_BEM_hub_ratio=.30, C02_sealed_hub_ratio=.315,
                  relative_active_area_change=area_change,
                  source_C01_BEM_design_point=dict(rpm=design['rpm'],
                      shaft_estimate_W=design['shaft_model_W'],
                      outside_polar_abs_torque_fraction=design['outside_polar_torque_fraction'],
                      Mach_gt_0p3_abs_torque_fraction=design['Mach_gt_0_3_torque_fraction']),
                  points_with_any_polar_extrapolation=sum(not r['all_sections_in_polar'] for r in rows),
                  no_points_discarded=True, CFD_or_CAD_changed=False,
                  local_velocity_not_far_field_velocity=True, induced_velocity_added=False,
                  original_C01_predictions_frozen=True, physical_validation=False,
                  limitations=['Nominal chord/twist interpolation; not exact continuous BRep section recovery.',
                    'Uniform axial disk velocity and zero disk swirl are prescribed, not solved operating states.',
                    'C02 hub uses sealed-envelope assumption; real cavities/tip leakage are unresolved.',
                    '2D polar endpoint extension remains flagged; no compressibility/cascade/rotation correction.',
                    'No tip/root force multiplier or installed CFD coupling is introduced here.',
                    'Annular Q excludes bypass gap; it is not total duct flow.',
                    'Do not assign this shaft estimate to the CAD motor reserve or accepted vehicle power.'],
                  input_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()
                      for f in [source,manifest_path,rotor_path,geometry_path,polar.path,HERE/'ley_elemento_rotor.py']})
    (out/'PROCEDENCIA.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    fig,axs = plt.subplots(2,2,figsize=(12,8),layout='constrained')
    colors = ['#397da8','#65757f','#c77736']
    for factor,color in zip((.5,.75,1.),colors):
        for ratio,style in [(.30,'--'),(.315,'-')]:
            subset = [r for r in rows if r['hub_ratio']==ratio and r['rpm_factor']==factor]
            x = [r['axial_disk_velocity_m_s'] for r in subset]
            label = f'{factor:.2f} RPM ref.; cubo {ratio:.3f}R'
            for ax,key,scale in [(axs[0,0],'local_integral_T_N',1),
                                 (axs[0,1],'local_integral_shaft_estimate_W',1),
                                 (axs[1,0],'outside_polar_abs_torque_fraction',100),
                                 (axs[1,1],'Mach_gt_0p3_abs_torque_fraction',100)]:
                ax.plot(x,[r[key]*scale for r in subset],style,color=color,
                        marker='o' if ratio==.315 else None,markersize=3,label=label)
    for ax,title,ylabel in [(axs[0,0],'Carga axial local integrada','T estimado [N]'),
                            (axs[0,1],'Potencia de la ley seccional','P estimada [W]'),
                            (axs[1,0],'Extrapolación de polar','Fracción de |par| [%]'),
                            (axs[1,1],'Compresibilidad sin modelar','|par| con M relativo > 0,3 [%]')]:
        ax.set_title(title,fontsize=11);ax.set_xlabel('Velocidad axial impuesta en disco [m/s]')
        ax.set_ylabel(ylabel);ax.grid(alpha=.2)
    axs[0,0].legend(fontsize=7,ncol=2)
    for ax in axs[1]:ax.set_ylim(-2,102)
    fig.suptitle('C02 — cribado de cargas locales; NO es una curva instalada',fontsize=14)
    fig.savefig(out/'CRIBADO.png',dpi=170);fig.savefig(out/'CRIBADO.svg');plt.close(fig)
    print(json.dumps(dict(points=len(rows),relative_active_area_change=area_change,
                          points_with_extrapolation=report['points_with_any_polar_extrapolation'],physical_validation=False),indent=2))


if __name__ == '__main__':
    main()
