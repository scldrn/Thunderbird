"""Create two 5-kg-reference rotor candidates from the computed twist.

CAD in mm; local Z rotor axis, CCW viewed from +Z, intended thrust +Z.
This does not change A07 or approve material, balance, attachment or RPM.
"""
from pathlib import Path
import hashlib
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'modulo_preliminar/CAD'
OUT.mkdir(exist_ok=True)


def main():
    coordinates_path = ROOT / 'fuentes/uiuc/sd8020.dat'
    foil = np.loadtxt(coordinates_path, skiprows=1)
    leading = int(np.argmin(foil[:, 0]))
    assert np.allclose(foil[0], foil[-1])
    report = dict(kind='preliminary_rotor_geometry_not_installed_product',
                  coordinate_units='mm', spin_convention='CCW viewed from +Z; intended thrust +Z',
                  source_airfoil_sha256=hashlib.sha256(coordinates_path.read_bytes()).hexdigest(),
                  material_RPM_and_manufacturing_approved=False, canonical_configuration_changed=False,
                  candidates=[])
    for factor in (1., 1.25):
        source = HERE / f'modulo_preliminar/m5_d{factor:g}_k0.85.json'
        data = json.loads(source.read_text())
        design = data['design']
        radius = 1000*design['radius_m']
        radial = np.array([r['r_m']*1000 for r in design['annuli']])
        chord = np.array([r['chord_m']*1000 for r in design['annuli']])
        beta = np.array([r['beta_rad'] for r in design['annuli']])
        # Retain every BEM cell centre and extend only its nearest endpoint
        # to the root/tip. The interpolating loft is an approximation between wires.
        stations = np.r_[.30*radius, radial, radius]
        wires = []
        for r in stations:
            c = np.interp(r, radial, chord)
            b = np.interp(r, radial, beta)
            s = (.25-foil[:, 0])*c
            h = foil[:, 1]*c
            xyz = np.column_stack((-s*np.cos(b)+h*np.sin(b), np.full(len(foil), r),
                                   s*np.sin(b)+h*np.cos(b)))
            upper = cq.Edge.makeSpline([cq.Vector(*p) for p in xyz[:leading+1]])
            lower = cq.Edge.makeSpline([cq.Vector(*p) for p in xyz[leading:]])
            wire = cq.Wire.assembleEdges([upper, lower])
            assert wire.IsClosed()
            wires.append(wire)
        blade = cq.Solid.makeLoft(wires)
        assert blade.isValid() and blade.Volume() > 0
        blades = [blade.rotate((0, 0, 0), (0, 0, 1), 45*i) for i in range(8)]
        pairs = [dict(relative_angle_deg=45*i, overlap_mm3=blades[0].intersect(blades[i]).Volume()) for i in range(1, 5)]
        assert max(p['overlap_mm3'] for p in pairs) < 1e-6
        hub_radius, hub_height, bore_radius = .315*radius, .38*radius, .05*radius
        hub = cq.Solid.makeCylinder(hub_radius, hub_height, cq.Vector(0, 0, -hub_height/2))
        hub = hub.cut(cq.Solid.makeCylinder(bore_radius, hub_height+2, cq.Vector(0, 0, -hub_height/2-1)))
        hub_join = blade.intersect(hub).Volume(1e-8)
        assert hub_join > 0
        print(source.stem, 'loft valid; fusing rotor', flush=True)
        rotor = hub.fuse(*blades).clean()
        assert rotor.isValid() and len(rotor.Solids()) == 1
        default_volume = rotor.Volume()
        volume = rotor.Volume(1e-8)
        expected_union = hub.Volume(1e-8)+8*(blade.Volume(1e-8)-hub_join)
        volume_audit = dict(case_id=source.stem, fused_volume_mm3=volume,
                            expected_union_from_parts_mm3=expected_union,
                            relative_difference=volume/expected_union-1,
                            default_nonadaptive_fused_volume_mm3=default_volume,
                            adaptive_integration_tolerance=1e-8,
                            blade_volume_mm3=blade.Volume(1e-8), hub_volume_mm3=hub.Volume(1e-8),
                            hub_blade_intersection_mm3=hub_join,
                            pair_checks=pairs)
        (OUT / f'{source.stem}_AUDITORIA_UNION.json').write_text(json.dumps(volume_audit, indent=2)+'\n')
        print(json.dumps(volume_audit), flush=True)
        assert abs(volume/expected_union-1) < 1e-5
        name = f'rotor_8palas_D{2*radius:g}mm'
        exported = {}
        for hand, shape in (('CCW', rotor), ('CW', rotor.mirror('XZ'))):
            path = OUT / f'{name}_{hand}.step'
            cq.exporters.export(shape, str(path))
            imported = cq.importers.importStep(str(path)).val()
            assert imported.isValid() and len(imported.Solids()) == 1
            assert abs(imported.Volume(1e-8)/volume-1) < 1e-5
            exported[hand] = dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        bb = rotor.BoundingBox()
        density = 1600 # mass/centrifugal sensitivity only, not approved material
        mass = volume*1e-9*density
        blade_mass = blade.Volume(1e-8)*1e-9*density
        blade_centre = blade.Center()
        omega = design['rpm']*2*np.pi/60
        centrifugal = blade_mass*omega**2*blade_centre.y*.001
        record = dict(design_source=str(source.relative_to(ROOT)), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                      radius_mm=radius, hub_diameter_mm=2*hub_radius, hub_height_mm=hub_height,
                      bore_diameter_mm=2*bore_radius, loft_sections=len(wires),
                      bounding_dimensions_mm=[bb.xlen, bb.ylen, bb.zlen],
                      volume_mm3=volume, one_blade_volume_mm3=blade.Volume(1e-8),
                      hub_blade_join_overlap_before_union_mm3=hub_join,
                      blade_pair_checks_by_rotational_symmetry=pairs,
                      single_solid_after_fusion=True,
                      material_density_sensitivity_kg_m3=density,
                      nominal_rotor_mass_sensitivity_kg=mass,
                      one_blade_mass_sensitivity_kg=blade_mass,
                      one_blade_centrifugal_root_resultant_sensitivity_N=centrifugal,
                      performance_rpm_unapproved=design['rpm'],
                      files=exported,
                      limitations=['No root fillet, tolerances, retention, structural/FEM/fatigue or balancing design approved.',
                                   'Smooth interpolating loft between airfoil wires; no identical continuous CFD/BEM geometry claim.',
                                   'Bore/hub are layout assumptions, not a motor or bearing interface selection.',
                                   'Candidate is a separate local component, not fitted into or substituted for A07.'])
        report['candidates'].append(record)
        (OUT / 'GEOMETRIA.json').write_text(json.dumps(report, indent=2)+'\n')
        print(name, 'STEP and mirror reimported', flush=True)


if __name__ == '__main__':
    main()
