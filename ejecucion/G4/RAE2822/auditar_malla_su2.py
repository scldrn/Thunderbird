"""Check the official SU2 2D mesh before running the independent benchmark."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT/'fuentes/benchmark_SU2_RAE2822'


def read_mesh(path):
    lines = iter(path.read_text().splitlines())
    points, cells, markers = None, [], {}
    for line in lines:
        if line.startswith('NDIME='):
            assert int(line.split('=')[1]) == 2
        elif line.startswith('NPOIN='):
            n = int(line.split('=')[1].split()[0])
            rows = [list(map(float,next(lines).split())) for _ in range(n)]
            a = np.array(rows)
            assert a.shape[1] in (3,4)
            np.testing.assert_array_equal(a[:,-1],np.arange(n))
            if a.shape[1] == 4:
                np.testing.assert_array_equal(a[:,2],0)
            points = a[:,:2]
        elif line.startswith('NELEM='):
            n = int(line.split('=')[1])
            for _ in range(n):
                row = list(map(int,next(lines).split()))
                count = {5:3,9:4}[row[0]]
                cells.append(row[1:1+count])
        elif line.startswith('MARKER_TAG='):
            name = line.split('=')[1].strip()
            row = next(lines)
            assert row.startswith('MARKER_ELEMS=')
            n = int(row.split('=')[1])
            edges=[]
            for _ in range(n):
                e=list(map(int,next(lines).split()));assert e[0] == 3
                edges.append(e[1:3])
            markers[name]=edges
    assert points is not None and len(cells) > 0
    assert np.isfinite(points).all()
    return points, cells, markers


def main():
    path=SOURCE/'mesh_RAE2822_turb.su2'
    xy,cells,markers=read_mesh(path)
    edge_counts=Counter()
    signs=[];areas=[]
    for cell in cells:
        assert min(cell) >= 0 and max(cell) < len(xy)
        p=xy[cell];r=np.roll(p,-1,axis=0)
        area=.5*np.sum(p[:,0]*r[:,1]-p[:,1]*r[:,0])
        assert area != 0
        signs.append(np.sign(area));areas.append(abs(area))
        for i in range(len(cell)):
            edge_counts[tuple(sorted((cell[i],cell[(i+1)%len(cell)])))] += 1
    assert set(edge_counts.values()) == {1,2}
    given={tuple(sorted(e)) for edges in markers.values() for e in edges}
    boundary={e for e,n in edge_counts.items() if n == 1}
    assert given == boundary
    assert set(markers) == {'AIRFOIL','FARFIELD'}
    adjacency=defaultdict(list)
    for a,b in markers['AIRFOIL']:
        adjacency[a].append(b);adjacency[b].append(a)
    assert all(len(v)==2 for v in adjacency.values())
    first=min(adjacency);loop=[first];previous=None;at=first
    for _ in range(len(adjacency)):
        nxt=next(v for v in adjacency[at] if v != previous)
        if nxt == first:break
        assert nxt not in loop
        loop.append(nxt);previous,at=at,nxt
    assert len(loop)==len(adjacency)
    surface=xy[loop]
    chord=float(np.ptp(surface[:,0]))
    body=surface.copy();body[:,0]-=surface[:,0].min();body/=chord
    raw=np.fromstring((ROOT/'fuentes/benchmark_RAE2822/raetaf.x.fmt').read_text(),sep=' ')
    nasa=raw[2:].reshape(2,65,369).transpose(1,2,0)[0,32:337]
    a=nasa[:-1];d=np.diff(nasa,axis=0)
    t=np.clip(np.einsum('ijk,jk->ij',body[:,None,:]-a,d)/np.sum(d*d,axis=1),0,1)
    dist=np.linalg.norm(body[:,None,:]-(a+t[...,None]*d),axis=2).min(axis=1)
    report=dict(scope='Official SU2 mesh integrity and geometric comparison only, not flow validation',
        source_URL='https://github.com/su2code/TestCases/tree/4d2b3728e93f657199c9eec1919c4a752e1159cb/rans/rae2822',
        source_mesh_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        points=len(xy),cells=len(cells),triangles=sum(len(c)==3 for c in cells),quadrilaterals=sum(len(c)==4 for c in cells),
        boundary_edges={k:len(v) for k,v in markers.items()},all_cells_nonzero_signed_area=True,
        orientation_counts={str(s):int(sum(np.asarray(signs)==s)) for s in (-1,1)},
        all_boundary_edges_match_markers=True,airfoil_is_single_closed_loop=True,
        minimum_planar_cell_area=float(min(areas)),summed_cell_area=float(sum(areas)),chord_mesh_units=chord,
        maximum_one_way_airfoil_vertex_distance_to_NASA_polygon_chords=float(dist.max()),
        geometry_not_assumed_identical_to_NASA=True,
        distinction='SU2 uses a node-centred dual control volume and this official mesh is not the previously audited OpenFOAM mesh; quality and model acceptance do not transfer.',
        physical_validation_accepted=False)
    (HERE/'AUDITORIA_MALLA_SU2.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
