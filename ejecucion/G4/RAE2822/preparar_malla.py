"""Convert NASA's supplied 369x65 C-grid to one-layer conformal hexahedra.

Preserves the near-wall spacing and glues the coincident wake cut. Benchmark
only: not vehicle geometry, solver convergence, mesh independence or validation.
"""
from pathlib import Path
import hashlib
import json

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT/'fuentes/benchmark_RAE2822'
CASE = HERE/'piloto_r1'


def main():
    CASE.mkdir(exist_ok=True)
    if (CASE/'fluid.msh').exists():
        raise FileExistsError('Preserve existing mesh')
    path = SOURCE/'raetaf.x.fmt'
    values = np.fromstring(path.read_text(), sep=' ')
    ni, nj = map(int, values[:2])
    assert (ni, nj) == (369, 65) and len(values) == 2+2*ni*nj
    g = values[2:].reshape(2, nj, ni).transpose(1, 2, 0)
    np.testing.assert_array_equal(g[0, :33], g[0, -1:-34:-1])
    unique, inverse = np.unique(g.reshape(-1, 2), axis=0, return_inverse=True)
    assert len(unique) == ni*nj-33
    index = inverse.reshape(nj, ni)
    chord = .3048
    span = .01*chord
    points = np.vstack([np.column_stack((unique*chord, np.full(len(unique), z))) for z in (-span/2, span/2)])
    n2 = len(unique)
    quads = np.array([[index[j, i], index[j, i+1], index[j+1, i+1], index[j+1, i]]
                      for j in range(nj-1) for i in range(ni-1)], dtype=int)
    xy = points[quads, :2]
    edges = np.roll(xy, -1, axis=1)-xy
    corner_cross = edges[:, :, 0]*np.roll(edges[:, :, 1], -1, axis=1)-edges[:, :, 1]*np.roll(edges[:, :, 0], -1, axis=1)
    assert np.all(corner_cross > 0), float(corner_cross.min())
    area = .5*np.sum(xy[:, :, 0]*np.roll(xy[:, :, 1], -1, axis=1)-xy[:, :, 1]*np.roll(xy[:, :, 0], -1, axis=1), axis=1)
    assert np.all(area > 0)
    hexes = np.column_stack((quads, quads+n2))
    # No explicit wake boundary: identified nodes make its32 faces internal.
    patches = {'airfoil': [], 'farfield': [], 'outlet': [], 'frontAndBack': []}
    for i in range(32, 336):
        a, b = index[0, i], index[0, i+1]
        patches['airfoil'].append([a, b, b+n2, a+n2])
    for i in range(ni-1):
        a, b = index[-1, i], index[-1, i+1]
        patches['farfield'].append([a, a+n2, b+n2, b])
    for j in range(nj-1):
        a, b = index[j, 0], index[j+1, 0]
        patches['outlet'].append([a, a+n2, b+n2, b])
        a, b = index[j, -1], index[j+1, -1]
        patches['outlet'].append([a, b, b+n2, a+n2])
    for quad in quads:
        patches['frontAndBack'].append(quad[::-1].tolist())
        patches['frontAndBack'].append((quad+n2).tolist())
    assert len(hexes) == 23552
    assert {k:len(v) for k,v in patches.items()} == dict(airfoil=304, farfield=368, outlet=128, frontAndBack=47104)
    with (CASE/'fluid.msh').open('w') as f:
        f.write('$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$PhysicalNames\n5\n')
        for tag, name in enumerate(patches, start=1):
            f.write(f'2 {tag} "{name}"\n')
        f.write('3 5 "fluid"\n$EndPhysicalNames\n$Nodes\n'+str(len(points))+'\n')
        for tag, xyz in enumerate(points, start=1):
            f.write(str(tag)+' '+' '.join(f'{x:.16g}' for x in xyz)+'\n')
        f.write('$EndNodes\n$Elements\n'+str(len(hexes)+sum(map(len, patches.values())))+'\n')
        element = 0
        for physical, (name, faces) in enumerate(patches.items(), start=1):
            for face in faces:
                element += 1
                f.write(f'{element} 3 2 {physical} {physical} '+' '.join(str(v+1) for v in face)+'\n')
        for hexahedron in hexes:
            element += 1
            f.write(f'{element} 5 2 5 5 '+' '.join(str(v+1) for v in hexahedron)+'\n')
        f.write('$EndElements\n')
    # Experimental Cp file contains one ordered lower/upper trace.
    cp = []
    for line in (SOURCE/'cp.exp.gen').read_text().splitlines():
        fields = line.split()
        if len(fields) == 2:
            try:
                cp.append([float(s) for s in fields])
            except ValueError:
                pass
    cp = np.asarray(cp)
    assert cp.shape == (103, 2)
    np.savetxt(CASE/'Cp_experimental.csv', cp, delimiter=',', header='x_over_c,minus_Cp_plot_ordinate', comments='')
    normal_gap = np.linalg.norm(g[1, 32:337]-g[0, 32:337], axis=1)*chord
    report = dict(source='NASA NPARC RAE2822 Study4 supplied C-grid',
                  grid_dimensions=[ni, nj], chord_m=chord, span_m=span,
                  two_dimensional_empty_direction='z', hexahedra=len(hexes), points=len(points),
                  conformal_wake_duplicate_nodes_removed=33, conformal_wake_internal_faces=32,
                  expected_internal_faces=46704, expected_total_faces=94608,
                  all_quads_convex_and_positive=True, min_volume_m3=float(area.min()*span),
                  summed_cell_volume_m3=float(area.sum()*span),
                  first_wall_point_gap_m=[float(normal_gap.min()), float(normal_gap.max())],
                  boundary_faces={k:len(v) for k,v in patches.items()}, experimental_Cp_points=len(cp),
                  source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.iterdir() if p.is_file()},
                  mesh_sha256=hashlib.sha256((CASE/'fluid.msh').read_bytes()).hexdigest(),
                  mesh_provenance_URL='https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html',
                  experimental_condition_from_file='Mach0.729, alpha2.31deg',
                  distinctions=['NASA overview lists nominal case6 Mach0.725/alpha2.92; this study and its Cp file specify0.729/2.31. Do not mix.',
                                'NASA computational grid has sharp TE and is scaled to1ft; measured geometry/transition not fully identical.',
                                'One supplied mesh is not a mesh-convergence study.',
                                'This is a solver benchmark, not the C02 vehicle or its transonic capability.'],
                  checkMesh_accepted=False, own_solver_executed=False, physical_validation_accepted=False)
    (CASE/'MALLA.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('hexahedra','points','summed_cell_volume_m3','first_wall_point_gap_m','experimental_Cp_points')}, indent=2))


if __name__ == '__main__':
    main()
