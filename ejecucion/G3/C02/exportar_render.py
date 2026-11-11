"""Mesh the same identified STEP artifacts for native Blender review."""
from pathlib import Path
import gzip
import hashlib
import json
import cadquery as cq

HERE=Path(__file__).resolve().parent
DEST=HERE/'integracion_x160'


def mesh(shape):
    v,t=shape.tessellate(.15,.18)
    return dict(vertices_m=[[q.x*.001,q.y*.001,q.z*.001] for q in v],triangles=t)


def main():
    closed=DEST/'C02_integracion_x160_5kg_cerrado_CANDIDATA.step'
    cut=DEST/'C02_integracion_x160_5kg_corte_CANDIDATA.step'
    parts=[]
    for s,n,l,c in cq.Assembly.load(str(closed)):
        name=n.split('/')[-1]
        parts.append(dict(name=name,color=list(c.toTuple()[:3]) if c else [.4,.44,.48],
            hardware_reserve='reserva_' in name,
            hidden_in_cut=name.startswith(('carroceria_C02_superior','compuerta_C02_','aro_C02_','junta_C02_')),
            **mesh(s.moved(l))))
    cut_overrides={}
    for s,n,l,c in cq.Assembly.load(str(cut)):
        name=n.split('/')[-1]
        if name.endswith('camisa_cuna_y_soportes') and name.startswith(('modulo_C02_0_','modulo_C02_2_')):
            cut_overrides[name]=mesh(s.moved(l))
    data=dict(closed_STEP_sha256=hashlib.sha256(closed.read_bytes()).hexdigest(),
        cut_STEP_sha256=hashlib.sha256(cut.read_bytes()).hexdigest(),
        units='m',display_tessellation_tolerance_mm=.15,parts=parts,cut_overrides=cut_overrides,
        scope='Native CAD rendering. Hardware reserves, loads, material and performance unqualified.')
    with gzip.open(DEST/'mallas_C02.json.gz','wt') as f:json.dump(data,f)
    print('C02_DISPLAY_MESHES',len(parts),sum(len(p['triangles']) for p in parts),flush=True)


if __name__=='__main__':main()
