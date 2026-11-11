"""Centrifugal load resultants from actual C02 geometry and section screening.

Assumed homogeneous densities and C01 speed demands. No material selection,
allowable stress, 3D stress concentration, elastic deformation or approval.
"""
from pathlib import Path
import csv
import hashlib
import json

import cadquery as cq
import numpy as np
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE/'rotor_C02'


def props(shape):
    p = GProp_GProps()
    error = BRepGProp.VolumeProperties_s(shape.wrapped, p, 1e-8, True, False)
    I = p.MatrixOfInertia()
    return p.Mass()*1e-9, np.array([p.CentreOfMass().X(), p.CentreOfMass().Y(), p.CentreOfMass().Z()])*1e-3, np.array([[I.Value(i+1, j+1) for j in range(3)] for i in range(3)])*1e-15, error


def centrifugal_resultants(shape, origin_m, rho_kg_m3, omega_rad_s):
    V, c, I, error = props(shape)
    x0, y0, z0 = origin_m
    factor = rho_kg_m3*omega_rad_s**2
    integral_xz = V*c[0]*c[2]-I[0, 2]
    integral_yz = V*c[1]*c[2]-I[1, 2]
    force = factor*V*np.array([c[0], c[1], 0.])
    moment = factor*np.array([-(integral_yz-z0*V*c[1]),
                               integral_xz-z0*V*c[0],
                               y0*V*c[0]-x0*V*c[1]])
    return force, moment, dict(volume_m3=V, centroid_m=c.tolist(), integration_error_estimate=error)


def section_properties(blade, x_mm, thickness_mm=.02):
    slab = cq.Workplane('XY').box(thickness_mm, 120, 100).val().translate((x_mm, 0, 0))
    sample = blade.intersect(slab)
    assert sample.isValid() and len(sample.Solids()) == 1
    V, c, I, error = props(sample)
    dx = thickness_mm*.001
    A = V/dx
    # Thin-slice approximation; radial second moment of the slab is removed.
    Iyy = (I[1, 1]-V*dx*dx/12)/dx
    Izz = (I[2, 2]-V*dx*dx/12)/dx
    Iyz = I[1, 2]/dx
    area_moments = np.array([[Izz, -Iyz], [-Iyz, Iyy]])
    assert np.linalg.eigvalsh(area_moments).min() > 0
    vertices, _ = sample.tessellate(.002, .1)
    yz = np.array([[v.y, v.z] for v in vertices])*.001
    return dict(A_m2=A, centroid_m=c, area_moments_m4=area_moments,
                sample_boundary_yz_m=yz, integration_error_estimate=error)


def normal_stress(section, axial_force_N, moment_yz_Nm):
    My, Mz = moment_yz_Nm
    linear = np.linalg.solve(section['area_moments_m4'], [-Mz, My])
    stress = axial_force_N/section['A_m2']+(section['sample_boundary_yz_m']-section['centroid_m'][1:])@linear
    return dict(mean_axial_Pa=axial_force_N/section['A_m2'],
                sampled_min_normal_Pa=float(stress.min()), sampled_max_normal_Pa=float(stress.max()),
                sampled_abs_normal_max_Pa=float(abs(stress).max()))


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'RESULTADOS.json').exists():
        raise FileExistsError('Preserve existing structural screening')
    with (ROOT/'ejecucion/G2/modulo_preliminar/OPERACION_CONDICIONAL.csv').open() as f:
        operations = list(csv.DictReader(f))
    all_results = []
    sections = []
    sensitivity = []
    sources = []
    for factor, folder in [(1., 'C02_D82_x-160_neutro'), (1.25, 'C02_D102.5_neutro')]:
        source = ROOT/'ejecucion/G3/C02/salida'/folder/'modulo.step'
        parts = {n.split('/')[-1]: s.moved(loc) for s, n, loc, _ in cq.Assembly.load(str(source))}
        rotor = parts['rotor_copa_CCW']
        R_mm = 41*factor
        # Angular sectors clip a finite-chord blade near the root and may also
        # include its neighbour. Remove only the hub, identify eight connected
        # blades, and work beyond that radial removal at x/R >= .33.
        hub_removal = cq.Solid.makeCylinder(.32*R_mm, 100, cq.Vector(0, 0, -50))
        separate = rotor.cut(hub_removal).Solids()
        assert len(separate) == 8, len(separate)
        volumes = np.array([props(s)[0] for s in separate])
        assert np.ptp(volumes)/volumes.mean() < 1e-6
        blade = max(separate, key=lambda s: s.BoundingBox().xmax)
        selected = [row for row in operations if row['mass_target_kg'] == '5'
                    and float(row['diameter_factor']) == factor and float(row['force_transfer_ASSUMED']) == .85]
        assert len(selected) == 3
        sources.append(dict(diameter_factor=factor, path=str(source.relative_to(ROOT)),
                            SHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
                            reference_only_not_installed=factor != 1))
        for ratio in (.33, .4, .5, .6, .7, .8, .9, .95):
            x = ratio*R_mm
            section = section_properties(blade, x)
            if ratio in (.33, .6):
                alternate = section_properties(blade, x, .04)
                delta_A = alternate['A_m2']/section['A_m2']-1
                delta_S = np.max(abs(alternate['area_moments_m4']-section['area_moments_m4']))/np.max(abs(section['area_moments_m4']))
                assert abs(delta_A) < .001 and delta_S < .001
                sensitivity.append(dict(factor=factor, ratio=ratio, slice_mm=[.02, .04],
                                        relative_A_change=delta_A, normalized_area_tensor_change=float(delta_S)))
            remaining = blade.intersect(cq.Workplane('XY').box(150, 150, 100).val().translate((x+75, 0, 0)))
            assert remaining.isValid() and len(remaining.Solids()) == 1
            sections.append(dict(diameter_factor=factor, x_over_R=ratio, x_mm=x,
                                 area_mm2=section['A_m2']*1e6, centroid_m=section['centroid_m'].tolist(),
                                 area_moments_m4=section['area_moments_m4'].tolist()))
            for operation in selected:
                omega = float(operation['rpm_model'])*np.pi/30
                for rho in (1200., 1600., 2700.):
                    force, moment, mass_props = centrifugal_resultants(remaining, section['centroid_m'], rho, omega)
                    stress = normal_stress(section, force[0], moment[1:])
                    row = dict(diameter_factor=factor, x_over_R=ratio, x_mm=x,
                               operating_scenario=operation['maneuver'], rpm_ASSUMED=float(operation['rpm_model']),
                               density_ASSUMED_kg_m3=rho, force_N=force.tolist(), moment_Nm=moment.tolist(),
                               mass_outboard_kg=rho*mass_props['volume_m3'], area_mm2=section['A_m2']*1e6,
                               **stress, material_and_structural_approval=False)
                    all_results.append(row)
            print('SECTION', factor, ratio, section['A_m2']*1e6, 'mm2', flush=True)
    report = dict(scope='Centrifugal body-force resultants and linear section-normal stress screening only',
                  geometric_sources=sources, sections=sections, results=all_results,
                  slice_sensitivity=sensitivity, physical_stress_validation_accepted=False,
                  assumptions=['Homogeneous density; linear section stress with uniform longitudinal elastic modulus over each section; no selected material.',
                               'Undeformed rigid CAD rotating at hypothetical C01 operating speeds.',
                               'Stress assumes linear section traction; no 3D fillet, notch, laminate or interface concentration.',
                               'No aerodynamic load, torsional/shear stress, gyroscopic, impact, fatigue, thermal, elastic or modal approval.',
                               'A positive geometry or conditional stress does not prove rotor retention or containment.',
                               'Large diameter is a prototype not installed in the same exterior.'],
                  formula='F=rho*Omega^2*integral(x,y,0)dV; M=integral((r-r0) cross f)dV; sigma=N/A+[y-yc,z-zc] dot inverse(S) dot[-Mz,My]',
                  source_theory='https://ocw.mit.edu/courses/16-20-structural-mechanics-fall-2002/resources/unit14/')
    (OUT/'RESULTADOS.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    with (OUT/'RESULTADOS.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader(); writer.writerows(all_results)
    print('CENTRIFUGAL_SCREEN', len(all_results), 'conditional section cases', flush=True)


if __name__ == '__main__':
    main()
