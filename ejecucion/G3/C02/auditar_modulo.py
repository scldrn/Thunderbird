"""Audit saved C02 geometry. This is not a force, torque or durability test."""
from pathlib import Path
import hashlib
import itertools
import json
import math

import cadquery as cq
import numpy as np

from crear_modulo import inner_hull

HERE=Path(__file__).resolve().parent
OUT=HERE/'salida'


def bbox_overlap(a,b):
    return all(max(getattr(a,k+'min'),getattr(b,k+'min'))<min(getattr(a,k+'max'),getattr(b,k+'max'))-1e-7 for k in 'xyz')


def main():
    hull=inner_hull()
    results=[]
    for label in ('C02_D82_neutro','C02_D102.5_neutro'):
        folder=OUT/label
        meta=json.loads((folder/'MANIFIESTO.json').read_text())
        path=folder/'modulo.step'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['STEP_sha256']
        parts={n.split('/')[-1]:s.moved(loc) for s,n,loc,c in cq.Assembly.load(str(path))}
        boxes={n:s.BoundingBox() for n,s in parts.items()}
        intersections=[];tested=0
        with (folder/'PARES_STATICOS.ndjson').open('w') as log:
            for a,b in itertools.combinations(parts,2):
                if not bbox_overlap(boxes[a],boxes[b]):continue
                v=parts[a].intersect(parts[b]).Volume(1e-8)
                record=dict(a=a,b=b,overlap_mm3=v)
                log.write(json.dumps(record)+'\n');log.flush()
                tested+=1
                if v>1e-5:intersections.append(record)
        station=meta['station_CAD_mm']
        local=hull.translate((-station[0],-station[1],0))
        outside=[]
        for n,s in parts.items():
            v=s.cut(local).Volume(1e-8)
            if v>1e-4:outside.append(dict(part=n,outside_inset_hull_mm3=v))
        p=meta['parameters']
        # Every blade rectangle fits its full-rotation circumscribed cross-circle.
        half=math.hypot(8.,.75*p['factor'])
        z=p['row_z']
        continuous=dict(
            vane_half_enclosing_cross_radius_mm=half,
            upper_row_vertical_enclosure_gap_mm=z['superior_Y']-z['superior_X']-2*half,
            lower_row_vertical_enclosure_gap_mm=z['inferior_X']-z['inferior_Y']-2*half,
            lower_X_to_motor_seat_gap_mm=(p['support_bottom']-.6)-(z['inferior_X']+half),
            rotor_bottom_to_strut_top_gap_mm=-p['cup_half_height']-p['support_top'],
            rotor_top_to_upper_X_enclosure_gap_mm=z['superior_X']-half-p['cup_half_height'],
            motor_to_cup_radial_gap_mm=p['cavity_R']-p['motor_R'],
            motor_to_cup_axial_gap_mm=p['cavity_top']-p['motor_top'],
            rotor_swept_cylinder_to_bore_gap_mm=p['R_in']-p['rotor_swept_R'])
        assert min(v for k,v in continuous.items() if k!='vane_half_enclosing_cross_radius_mm')>0
        alignment=[]
        for row in z:
            max_error=0.
            for a in np.linspace(-45,45,181):
                rad=math.radians(a)
                for t in (-22*p['factor'],0,22*p['factor']):
                    # Independent rigid-crank transform vs translating tiebar hole.
                    if row.endswith('X'):
                        pin=np.array([t-6*math.sin(rad),z[row]+6*math.cos(rad)])
                        hole=np.array([t,z[row]+6])+[-6*math.sin(rad),6*(math.cos(rad)-1)]
                    else:
                        pin=np.array([t+6*math.sin(rad),z[row]+6*math.cos(rad)])
                        hole=np.array([t,z[row]+6])+[6*math.sin(rad),6*(math.cos(rad)-1)]
                    max_error=max(max_error,float(np.linalg.norm(pin-hole)))
            assert max_error<1e-12
            alignment.append(dict(row=row,angles=181,pins=3,max_pin_hole_axis_error_mm=max_error,
                                  exact_identity='delta=(+/-6sin(a),6(cos(a)-1)); common angles are a kinematic constraint, not servo performance'))
        result=dict(label=label,parts=len(parts),valid=all(s.isValid() for s in parts.values()),
            boolean_pairs_tested=tested,intersections=intersections,inside_reference_inset_hull=not bool(outside),
            outside_reference_inset_hull=outside,continuous_partial_enclosures=continuous,
            pin_alignment=alignment,geometric_interference_free_neutral=not bool(intersections),
            all_motion_and_installed_hardware_approved=False,
            scope='Neutral local nominal pairs; partial analytic motion enclosures and pin alignment; not all 4DOF collision states, aircraft interactions or loaded tolerances')
        (folder/'AUDITORIA.json').write_text(json.dumps(result,indent=2)+'\n')
        results.append(result)
        print(label,'pairs',tested,'intersections',len(intersections),'outside',len(outside),flush=True)
    (OUT/'AUDITORIA_RESUMEN.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':main()
