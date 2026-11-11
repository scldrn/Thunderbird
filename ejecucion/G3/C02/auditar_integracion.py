"""Check changed-module interfaces and relocated conceptual door paths.

Unchanged legacy joints are not silently approved by this scoped audit.
"""
from pathlib import Path
import hashlib
import itertools
import json

import cadquery as cq

from crear_modulo import ROOT
from auditar_modulo import bbox_overlap

HERE=Path(__file__).resolve().parent
DEST=HERE/'integracion_x160'


def main():
    path=DEST/'C02_integracion_x160_5kg_cerrado_CANDIDATA.step'
    meta=json.loads((DEST/'INTEGRACION.json').read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['files'][path.name]
    parts={n.split('/')[-1]:s.moved(l) for s,n,l,c in cq.Assembly.load(str(path))}
    boxes={n:s.BoundingBox() for n,s in parts.items()}
    modules={n for n in parts if n.startswith('modulo_C02_')}
    retained=set(parts)-modules
    tests=[];failures=[]
    for a in sorted(modules):
        for b in sorted(retained):
            if not bbox_overlap(boxes[a],boxes[b]):continue
            volume=parts[a].intersect(parts[b]).Volume(1e-8)
            r=dict(a=a,b=b,overlap_mm3=volume);tests.append(r)
            if volume>1e-4:failures.append(r)
    for a,b in itertools.combinations(sorted(modules),2):
        if a.split('_')[2]==b.split('_')[2] or not bbox_overlap(boxes[a],boxes[b]):continue
        volume=parts[a].intersect(parts[b]).Volume(1e-8)
        r=dict(a=a,b=b,overlap_mm3=volume);tests.append(r)
        if volume>1e-4:failures.append(r)
    (DEST/'AUDITORIA_INTERFACES.json').write_text(json.dumps(dict(
        STEP_sha256=meta['files'][path.name],parts=len(parts),new_module_records=len(modules),
        neutral_pairs_tested=len(tests),intersections=failures,records=tests,
        all_original_legacy_joints_reviewed=False,
        scope='New modules vs non-module records, and cross-module pairs; within-module neutral checks reported separately'),indent=2)+'\n')
    print('NEUTRAL_INTERFACES',len(tests),'intersections',len(failures),flush=True)
    rules=json.loads((DEST/'REGLAS_TAPAS_CONCEPTUALES.json').read_text())
    outer_path=ROOT/'modelos_integrados/producto_A07/envolvente.step'
    obstacle=cq.importers.importStep(str(outer_path)).val().Solids()[0]
    for rule in rules:obstacle=obstacle.cut(parts[rule['name']])
    outside_fins={n:s for n,s in parts.items() if n.startswith(('aleta_movil_','carenado_raiz_'))}
    fixed={n:parts[n] for n in modules}|outside_fins|{'reference_hull_minus_closed_caps':obstacle}
    fixed_boxes={n:s.BoundingBox() for n,s in fixed.items()}
    stages=[(float(z),0.) for z in range(0,11,2)]+[(10.,float(a)) for a in range(2,111,2)]
    door_fail=[];door_tests=0
    for lift,angle in stages:
        doors={}
        for r in rules:
            axis=list(r['axis_closed']);axis[2]+=r['out']*lift
            s=parts[r['name']].translate((0,0,r['out']*lift))
            doors[r['name']]=s.rotate(axis,(axis[0]+100,axis[1],axis[2]),r['sign']*angle)
        for name,s in doors.items():
            bb=s.BoundingBox()
            for other,t in fixed.items():
                if not bbox_overlap(bb,fixed_boxes[other]):continue
                volume=s.intersect(t).Volume(1e-8);door_tests+=1
                if volume>1e-3:door_fail.append(dict(door=name,other=other,lift_mm=lift,angle_deg=angle,overlap_mm3=volume))
        for (a,s),(b,t) in itertools.combinations(doors.items(),2):
            if not bbox_overlap(s.BoundingBox(),t.BoundingBox()):continue
            volume=s.intersect(t).Volume(1e-8);door_tests+=1
            if volume>1e-3:door_fail.append(dict(door=a,other=b,lift_mm=lift,angle_deg=angle,overlap_mm3=volume))
        (DEST/'AUDITORIA_TAPAS.json').write_text(json.dumps(dict(
            completed_nodes=stages.index((lift,angle))+1,total_nodes=len(stages),
            boolean_pairs_tested=door_tests,failures=door_fail,
            actual_guide_hinge_lock_and_actuator_designed=False,
            scope='Discrete nominal two-coordinate door paths vs reference body, fins, new module hardware and simultaneously posed doors; not continuous loaded clearance'),indent=2)+'\n')
        print('DOOR_NODE',lift,angle,'failures',len(door_fail),flush=True)


if __name__=='__main__':main()
