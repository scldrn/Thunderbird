"""Test nominal static replacement in fan 0 only; does not redesign A07.

Both candidates are placed at the current illustrative rotor datum. Intersections
identify required changes; they are not a verdict on a future motor integration.
"""
from pathlib import Path
import hashlib
import json

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAD = HERE / 'modulo_preliminar/CAD'


def main():
    source = ROOT / 'modelos_integrados/producto_A07/5kg/A07_cerrado.step'
    records = {n.split('/')[-1]: s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(source))}
    trials = []
    for name in ('rotor_8palas_D82mm_CCW.step', 'rotor_8palas_D102.5mm_CCW.step'):
        rotor_path = CAD / name
        rotor = cq.importers.importStep(str(rotor_path)).val().translate((-200, -76, 7.75))
        box = rotor.BoundingBox()
        tested, overlaps = [], []
        for other_name, other in records.items():
            if other_name == 'canal_0_base_rotor_representativo_4':
                continue
            b = other.BoundingBox()
            if any(getattr(box, axis+'max') <= getattr(b, axis+'min') or getattr(b, axis+'max') <= getattr(box, axis+'min') for axis in 'xyz'):
                continue
            intersection = rotor.intersect(other)
            volume = intersection.Volume(1e-8)
            tested.append(other_name)
            if volume > 1e-6:
                overlaps.append(dict(part=other_name, nominal_overlap_mm3=volume))
        trial = dict(file=name, source_sha256=hashlib.sha256(rotor_path.read_bytes()).hexdigest(),
                     replacement_datum_CAD_mm=[-200,-76,7.75], tested_pairs=len(tested),
                     tested_part_names=tested, intersections=overlaps,
                     fits_without_changes=not bool(overlaps),
                     scope='fan0 nominal closed pose; not swept rotor clearance, tolerance or modified integration')
        trials.append(trial)
        (CAD / 'PRUEBA_SUSTITUCION_A07.json').write_text(json.dumps(dict(
            A07_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            canonical_configuration_changed=False, trials=trials),indent=2)+'\n')
        print(name, 'tested',len(tested),'overlaps',len(overlaps), flush=True)


if __name__ == '__main__':
    main()
