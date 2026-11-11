"""Rebuild skin/ports around compact C02 stations without modifying A07/A08.

5 kg is an integration target. New parts, hardware reserves and the inherited
tail/door concepts remain unqualified. This is not a manufacturing release.
"""
from pathlib import Path
import hashlib
import json

import cadquery as cq

from crear_modulo import ROOT, OUT, build, save, pose, old_parts, inner_hull, cylinder, box

HERE=Path(__file__).resolve().parent
DEST=HERE/'integracion_x160'
DEST.mkdir(exist_ok=True)


def main():
    base=ROOT/'modelos_integrados/producto_A08_candidato/A08_cerrado_5kg_candidato.step'
    original={n.split('/')[-1]:(s.moved(l),c) for s,n,l,c in cq.Assembly.load(str(base))}
    discarded=[];kept={}
    for n,record in original.items():
        if n.startswith(('canal_0_','canal_1_','canal_2_','canal_3_','conducto_','alojamiento_actuador_',
                         'compuerta_','aro_','junta_','carroceria_')):
            discarded.append(n)
        else:kept[n]=record
    # The original 1 mm section-inset skin convention is retained. This is not
    # a constant normal offset or an approved composite laminate thickness.
    outer_path=ROOT/'modelos_integrados/producto_A07/envolvente.step'
    outer=cq.importers.importStep(str(outer_path)).val().Solids()[0]
    inner1=inner_hull(inset_mm=1.).intersect(box(1334,1000,1000,(-10,0,0)))
    raw_skin=outer.cut(inner1)
    print('RAW_SKIN',flush=True)
    positions=[(-160.,-76.),(-160.,76.),(160.,-76.),(160.,76.)]
    ports=[cylinder(47.4,500,(x,y,-250)) for x,y in positions]
    modifications=[]
    # Fixed retained styling is trimmed at new moving-port openings, so it is
    # not silently attached to a moving door or allowed to obstruct that door.
    for n,(s,color) in list(kept.items()):
        if n.startswith(('sculpture_','epaule_','lame_','signature_')):
            original_volume=s.Volume(1e-8)
            for port in ports:s=s.cut(port)
            removed=original_volume-s.Volume(1e-8)
            if removed>1e-5:
                assert s.isValid() and s.Volume(1e-8)>1e-5,(n,removed)
                kept[n]=(s,color)
                modifications.append(dict(part=n,method='fixed styling trimmed at new ports',removed_mm3=removed))
    upper=box(2000,1000,400,(0,0,200.2))
    lower=box(2000,1000,400,(0,0,-200.2))
    skin_parts=[]
    # Preserve already-cut skin panels. Restore only the four previous ports;
    # no repeated cuts against unrelated interior ribs or tail components.
    for label,half in [('superior',upper),('inferior',lower)]:
        restored=original['carroceria_'+label][0]
        for old_x in (-200.,200.):
            for old_y in (-76.,76.):
                patch=raw_skin.intersect(cylinder(47.4,500,(old_x,old_y,-250))).intersect(half)
                pb=patch.BoundingBox()
                for n,(s,c) in kept.items():
                    sb=s.BoundingBox()
                    if all(max(getattr(pb,k+'min'),getattr(sb,k+'min'))<min(getattr(pb,k+'max'),getattr(sb,k+'max'))-1e-6 for k in 'xyz'):
                        patch=patch.cut(s)
                restored=restored.fuse(patch).clean()
        assert restored.isValid()
        skin_parts.append(restored)
        print('RESTORED_SKIN',label,flush=True)
    skin=cq.Compound.makeCompound(skin_parts) # separated upper/lower panels
    new={};door_rules=[]
    for i,(x,y) in enumerate(positions):
        cap=skin.intersect(cylinder(45.8,500,(x,y,-250)))
        trim=skin.intersect(cylinder(47.4,500,(x,y,-250)).cut(cylinder(46.6,502,(x,y,-251))))
        seal=skin.intersect(cylinder(46.55,500,(x,y,-250)).cut(cylinder(46.35,502,(x,y,-251))))
        for label,half,sign_z in [('superior',upper,1),('inferior',lower,-1)]:
            name=f'compuerta_C02_{i}_{label}'
            door=cap.intersect(half)
            assert door.isValid() and door.Volume(1e-8)>0
            new[name]=(door,cq.Color(.07,.085,.10))
            new[f'aro_C02_{i}_{label}']=(trim.intersect(half),cq.Color(.63,.27,.10))
            new[f'junta_C02_{i}_{label}']=(seal.intersect(half),cq.Color(.02,.025,.03))
            bb=door.BoundingBox()
            door_rules.append(dict(name=name,axis_closed=[x,(-1 if y<0 else 1)*124,
                bb.zmin-4 if sign_z>0 else bb.zmax+4],out=sign_z,
                sign=(-1 if y>0 else 1)*sign_z,lift_mm=10.,angle_deg=110.,
                scope='conceptual two-coordinate motion; guides/hinges/locks not synthesized'))
    for port in ports:skin=skin.cut(port)
    new['carroceria_C02_superior']=(skin.intersect(upper),cq.Color(.07,.085,.10))
    new['carroceria_C02_inferior']=(skin.intersect(lower),cq.Color(.045,.06,.07))
    kept.update(new)
    source=old_parts();hull=inner_hull()
    templates={}
    for x in (-160.,160.):
        m=build(1.,(x,-76.),parts=source,hull=hull)
        templates[x]=pose(m)
        save(m,f'C02_D82_x{int(x)}_neutro')
    for i,(x,y) in enumerate(positions):
        for name,s in templates[x].items():
            if y>0:s=s.mirror('XZ')
            # Opposite-handed rotor on the rear-left module; reflection gives
            # diagonal opposite-spin pairs. This is not torque-map calibration.
            if name=='rotor_copa_CCW' and x>0:s=s.mirror('XZ')
            s=s.translate((x,y,0))
            color=cq.Color(.16,.20,.23) if name=='rotor_copa_CCW' else (cq.Color(.65,.36,.15) if name.startswith(('barra','casquillo')) else cq.Color(.40,.44,.48))
            output_name='rotor_copa' if name=='rotor_copa_CCW' else name
            kept[f'modulo_C02_{i}_{output_name}']=(s,color)
    # All assembled records must survive STEP export/reimport. Interference,
    # motion and changed-world-hull checks are recorded separately.
    for label,cutaway in [('cerrado',False),('corte',True)]:
        assembly=cq.Assembly(name=f'C02_x160_5kg_TARGET_{label}')
        for n,(s,color) in kept.items():
            assert s.isValid() and s.Volume(1e-8)>0,n
            if cutaway and n.startswith(('carroceria_C02_superior','compuerta_C02_','aro_C02_','junta_C02_')):continue
            shown=s
            if cutaway and n.endswith('camisa_cuna_y_soportes') and n.startswith(('modulo_C02_0_','modulo_C02_2_')):
                shown=s.cut(box(2000,180,240,(0,-100,100)))
            if shown.Volume(1e-8)>0:assembly.add(shown,name=n,color=color)
        file=DEST/f'C02_integracion_x160_5kg_{label}_CANDIDATA.step'
        assembly.save(str(file))
        imported=list(cq.Assembly.load(str(file)))
        assert all(s.moved(l).isValid() for s,n,l,c in imported)
        print('INTEGRATED',label,len(imported),flush=True)
    (DEST/'REGLAS_TAPAS_CONCEPTUALES.json').write_text(json.dumps(door_rules,indent=2)+'\n')
    report=dict(kind='integrated_packaging_candidate_not_functional_release',
        mass_target_kg=5,mass_closed=False,positions_CAD_mm=positions,parts=len(kept),
        source_A08_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),
        original_outer_hull_sha256=hashlib.sha256(outer_path.read_bytes()).hexdigest(),
        exterior_reference_loft_changed=False,canonical_A07_changed=False,
        port_centres_changed_from_x200_to_x160=True,
        removed_original_records=discarded,retained_record_modifications=modifications,
        rotor_spins_viewed_from_plus_Z=['CCW','CW','CW','CCW'],
        hardware_selected=False,manufacturing_and_performance_validated=False,
        files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DEST.glob('*.step')},
        limitations=['Motor/servo/bearing volumes are reserves, not zero-mass physical hardware.',
                     'Cup/shaft torque coupling, retention, tolerances, fatigue and cooling need design.',
                     'Door paths remain conceptual and must be rechecked at new stations.',
                     'Base A08 local styling/screw corrections retained, not a structural approval.',
                     'No full installed fluid map, structural sizing, mass closure or flight performance.'])
    (DEST/'INTEGRACION.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
