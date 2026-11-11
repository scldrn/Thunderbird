"""Adaptive BRep mass properties and conditional spin loads of the candidates."""
from pathlib import Path
import json
import cadquery as cq
import numpy as np
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

HERE = Path(__file__).resolve().parent
CAD = HERE / 'modulo_preliminar/CAD'


def main():
    geometry = json.loads((CAD / 'GEOMETRIA.json').read_text())
    rows = []
    for candidate in geometry['candidates']:
        shape = cq.importers.importStep(str(CAD / candidate['files']['CCW']['file'])).val()
        props = GProp_GProps()
        error = BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-8, True, False)
        tensor = props.MatrixOfInertia()
        density = 1600.0
        # GProp unit-density tensor is in mm^5; rho kg/m^3 -> kg m^2.
        inertia = np.array([[tensor.Value(i+1,j+1) for j in range(3)] for i in range(3)])*1e-15*density
        mass = props.Mass()*1e-9*density
        omega = candidate['performance_rpm_unapproved']*2*np.pi/60
        H = inertia[2,2]*omega
        assert np.all(np.linalg.eigvalsh(inertia) > 0)
        assert np.isclose(mass, candidate['nominal_rotor_mass_sensitivity_kg'], rtol=1e-5)
        assert np.isclose(inertia[0,0], inertia[1,1], rtol=1e-5)
        c = props.CentreOfMass()
        rows.append(dict(file=candidate['files']['CCW']['file'],
                         rho_ASSUMED_kg_m3=density, mass_sensitivity_kg=mass,
                         centre_of_mass_local_mm=[c.X(), c.Y(), c.Z()],
                         adaptive_volume_error_estimate=error,
                         inertia_about_centroid_sensitivity_kgm2=inertia.tolist(),
                         spin_angular_momentum_sensitivity_Nms=float(H),
                         spin_kinetic_energy_sensitivity_J=float(.5*inertia[2,2]*omega**2),
                         local_gyroscopic_moment_at_5rad_s_perpendicular_Nm=float(5*H),
                         geometry_and_spin_approved=False))
    j_ratio = rows[1]['inertia_about_centroid_sensitivity_kgm2'][2][2]/rows[0]['inertia_about_centroid_sensitivity_kgm2'][2][2]
    assert abs(j_ratio/1.25**5-1) < 1e-5
    (CAD / 'INERCIA_Y_GIRO_CONDICIONAL.json').write_text(json.dumps(dict(
        material_and_RPM_approved=False, candidates=rows, inertia_ratio_large_small=j_ratio,
        limitations=['Uniform-density monolithic geometric sensitivity; no material, retention, stress/fatigue, motor or RPM approval.',
                     'Counterrotation can cancel equal aggregate spin momentum, not local support loads; unequal operation breaks exact cancellation.',
                     'Acceleration/braking time requires motor excess torque, controller and energy sink; not derived from steady shaft power.']),indent=2)+'\n')
    print(json.dumps(rows,indent=2))


if __name__ == '__main__':
    main()
