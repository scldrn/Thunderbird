"""Screen body width using conservative moving envelopes of the C02 module.

The first passing sampled width is sufficient for these envelopes, not an
optimal/minimum physical body. Axial corridors and actuator sizes are reserves.
"""
from pathlib import Path
import json
import math

import cadquery as cq

from crear_modulo import OUT, inner_hull, old_parts, cylinder, box

HERE=Path(__file__).resolve().parent


def load_enclosures(folder,source_parts):
    meta=json.loads((folder/'MANIFIESTO.json').read_text())
    shapes={n.split('/')[-1]:s.moved(l) for s,n,l,c in cq.Assembly.load(str(folder/'modulo.step'))}
    p=meta['parameters'];f=p['factor'];rout=p['R_out']
    bounds={n:s for n,s in shapes.items() if not n.startswith(('alabe_integral_','barra_sincrona_','rotor_copa','camisa_cuna_'))}
    # Remove the old station's trimmed cylindrical skin; mount hardware remains
    # intact. A new casing is regenerated after a packing option is chosen.
    skin=cylinder(rout,260,(0,0,-130)).cut(cylinder(p['R_in'],262,(0,0,-131)))
    bounds['soportes_sin_piel_ducto']=shapes['camisa_cuna_y_soportes'].cut(skin)
    swept=cylinder(p['rotor_swept_R'],2*p['cup_half_height'],(0,0,-p['cup_half_height']))
    swept=swept.cut(cylinder(p['cavity_R'],p['cup_half_height']+p['cavity_top']+.1,(0,0,-p['cup_half_height']-.1)))
    swept=swept.cut(cylinder(p['shaft_R']+.05,30,(0,0,-15)))
    bounds['barrido_rotor_completo']=swept
    contained=[]
    for row,z in p['row_z'].items():
        along_x=row.endswith('X');axis=(1,0,0) if along_x else (0,1,0)
        drive=-1 if along_x else 1
        def xyz(q,t,h):return (q,t,h) if along_x else (t,q,h)
        def b(dq,dt,dh,q,t,h):return box(*( (dq,dt,dh) if along_x else (dt,dq,dh)),xyz(q,t,h))
        for index,t in enumerate((-22*f,0,22*f)):
            original=source_parts[f'canal_0_alabe_0_{row}_{index}'].BoundingBox()
            span=(original.xlen if along_x else original.ylen)*f
            half=math.hypot(8.,.75*f)
            vane=b(span+2e-5,2*half,2*half,0,t,z)
            wall=math.sqrt(rout*rout-t*t)
            start=-rout-12 if drive<0 else -wall-2.5
            end=wall+2.5 if drive<0 else rout+12
            stem=cylinder(p['vane_shaft_R']+1e-6,end-start,xyz(start,t,z),axis)
            # Crank+pin bounds for |angle|<=45deg. Its positive-Z sector is
            # retained so a full-circle bound does not falsely hit the base.
            crank=b(6.+2e-5,10.6,9.7,drive*(rout+6),t,z+2.65)
            # Overlapping solids must be boolean-united. A Compound is not a
            # material union and produced an invalid containment subtraction.
            enclosure=vane.fuse(stem,crank).clean()
            assert enclosure.isValid()
            name=f'alabe_integral_{row}_{index}'
            outside=shapes[name].cut(enclosure).Volume(1e-8)
            assert outside<1e-4,(name,outside)
            contained.append(dict(component=name,neutral_outside_enclosure_mm3=outside))
            bounds['barrido_'+name]=enclosure
        q=drive*(rout+5)
        t_half=22*f+1.5+6*math.sin(math.pi/4)
        z0=z+6*math.cos(math.pi/4)-1.5
        z1=z+7.5
        bounds['barrido_barra_'+row]=b(1.60002,2*t_half,z1-z0,q,0,(z1+z0)/2)
    return bounds,meta,contained


def main():
    source=old_parts()
    hulls={w:inner_hull(w) for w in (1.,1.05,1.10,1.15,1.20)}
    records=[]
    checks_by_module={}
    for label in ('C02_D82_neutro','C02_D102.5_neutro'):
        bounds,meta,checks=load_enclosures(OUT/label,source)
        checks_by_module[label]=checks
        p=meta['parameters'];rout=p['R_out']
        for axial_od in (40.,60.):
            # Reserve no smaller motor/servo simply to make the drawing fit.
            lateral=max(rout+axial_od/2+2,rout+29.)
            for x_station in (-200.,200.,-160.,160.):
                oriented={n:(s if x_station<0 else s.mirror('YZ')) for n,s in bounds.items()}
                for width,hull in hulls.items():
                    local=hull.translate((-x_station,lateral,0))
                    failures=[]
                    for n,s in oriented.items():
                        volume=s.cut(local).Volume(1e-8)
                        if volume>1e-4:failures.append(dict(enclosure=n,outside_mm3=volume))
                    record=dict(module=label,axial_corridor_OD_mm_ASSUMED=axial_od,
                        station_CAD_mm=[x_station,-lateral],width_multiplier=width,
                        all_conservative_enclosures_inside=not failures,
                        outside_enclosures=failures,checked_enclosures=len(bounds))
                    records.append(record)
                    (OUT/'CRIBADO_ENSANCHAMIENTO.json').write_text(json.dumps(dict(
                        scope='Sampled width adequacy for conservative module envelopes; not optimal body, actual engine or final skins/doors',
                        positive_Y_counterparts='mirror symmetry of hull and inward drive layout; cross-module interactions require separate check',
                        component_enclosure_checks=checks,
                        component_enclosure_checks_by_module=checks_by_module,
                        records=records),indent=2)+'\n')
                    print(label,'axial',axial_od,'x',x_station,'width',width,'outside',len(failures),flush=True)
                    if not failures:break


if __name__=='__main__':main()
