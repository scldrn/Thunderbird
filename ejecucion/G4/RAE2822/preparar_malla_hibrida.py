"""Keep the NASA wall strip, remesh its exterior for cell-centred FV.

This is an explicitly modified benchmark mesh, not the published C-grid.
The original rejected conversion is preserved in piloto_r1.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json

import gmsh
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT/'fuentes/benchmark_RAE2822'
CASE = HERE/'piloto_r2_hibrido'


def main():
    global CASE
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, default=CASE)
    parser.add_argument('--refine-cap', action='store_true')
    parser.add_argument('--max-core-aspect', type=float)
    args = parser.parse_args()
    CASE = args.case.resolve()
    CASE.mkdir(exist_ok=True)
    assert not (CASE/'fluid.msh').exists(), 'Preserve previous mesh'
    raw = np.fromstring((SOURCE/'raetaf.x.fmt').read_text(), sep=' ')
    g = raw[2:].reshape(2, 65, 369).transpose(1, 2, 0)
    jlast, ilo, ihi = 20, 24, 344
    np.testing.assert_array_equal(g[0, ilo:33], g[0, ihi:335:-1])
    strip = g[:jlast+1, ilo:ihi+1].copy()
    inserted = 0
    params = np.arange(ilo, ihi+1, dtype=float)
    if args.refine_cap or args.max_core_aspect:
        columns = [strip[:, 0]]
        parameters = [float(ilo)]
        for i in range(strip.shape[1]-1):
            if args.refine_cap and i in (0, strip.shape[1]-2):
                length = np.linalg.norm(strip[0, i+1]-strip[0, i])
                target, ratio = 2e-5, .75
                count = max(2, int(np.ceil(np.log(target/(length*(1-ratio)))/np.log(ratio)))+1)
                steps = ratio**np.arange(count)
                if i == 0:
                    steps = steps[::-1]
                fractions = np.cumsum(steps/steps.sum())
            else:
                fractions = [1.]
            if args.max_core_aspect:
                along = .5*(np.linalg.norm(strip[:-1, i+1]-strip[:-1, i], axis=1)
                             +np.linalg.norm(strip[1:, i+1]-strip[1:, i], axis=1))
                across = .5*(np.linalg.norm(np.diff(strip[:, i], axis=0), axis=1)
                              +np.linalg.norm(np.diff(strip[:, i+1], axis=0), axis=1))
                max_ratio = float(np.max(along/across))
                refined, previous = [], 0.
                for t in fractions:
                    count = max(1, int(np.ceil((t-previous)*max_ratio/args.max_core_aspect)))
                    refined.extend(np.linspace(previous, t, count+1)[1:])
                    previous = t
                fractions = refined
            inserted += len(fractions)-1
            for t in fractions:
                columns.append((1-t)*strip[:, i]+t*strip[:, i+1])
                parameters.append(ilo+i+t)
        strip = np.stack(columns, axis=1)
        params = np.array(parameters)
    inner = np.vstack((strip[-1], strip[-2::-1, -1], strip[1:-1, 0]))
    outer = g[-1]
    def area(p):
        return .5*np.sum(p[:, 0]*np.roll(p[:, 1], -1)-p[:, 1]*np.roll(p[:, 0], -1))
    if area(outer) < 0:
        outer = outer[::-1]
    if area(inner) > 0:
        inner = inner[::-1]
    gmsh.initialize()
    gmsh.model.add('RAE2822_NASA_wall_strip_hybrid')
    def polygon(points, h, fixed):
        nodes = [gmsh.model.geo.addPoint(float(x), float(y), 0, h) for x, y in points]
        lines = [gmsh.model.geo.addLine(nodes[i], nodes[(i+1) % len(nodes)]) for i in range(len(nodes))]
        if fixed:
            for line in lines:
                gmsh.model.geo.mesh.setTransfiniteCurve(line, 2)
        return gmsh.model.geo.addCurveLoop(lines), lines
    outside, lines_outer = polygon(outer, .75, False)
    hole, _ = polygon(inner, .01, True)
    gmsh.model.geo.addPlaneSurface([outside, hole])
    gmsh.model.geo.synchronize()
    gmsh.option.setNumber('Mesh.Algorithm', 6)
    gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary', 1)
    gmsh.option.setNumber('Mesh.MeshSizeMin', 1e-6)
    gmsh.option.setNumber('Mesh.MeshSizeMax', .75)
    gmsh.model.mesh.generate(2)
    gmsh.model.mesh.optimize('Relocate2D', niter=5)
    gmsh.write(str(CASE/'exterior_2d.msh'))
    ntags, coords, _ = gmsh.model.mesh.getNodes()
    gmsh_coords = dict(zip(map(int, ntags), np.asarray(coords).reshape(-1, 3)[:, :2]))
    nodes, lookup = [], {}
    def vertex(xy):
        key = tuple(np.round(xy, 12))
        if key not in lookup:
            lookup[key] = len(nodes)
            nodes.append(np.asarray(xy))
        index = lookup[key]
        assert np.linalg.norm(nodes[index]-xy) < 2e-12
        return index
    core = [[vertex(strip[j, i]), vertex(strip[j, i+1]), vertex(strip[j+1, i+1]), vertex(strip[j+1, i])]
            for j in range(jlast) for i in range(strip.shape[1]-1)]
    node_map = {tag: vertex(xy) for tag, xy in gmsh_coords.items()}
    types, _, lists = gmsh.model.mesh.getElements(2)
    assert list(types) == [2], list(types)
    triangles = [[node_map[int(n)] for n in tri] for tri in lists[0].reshape(-1, 3)]
    patches_2d = {'airfoil': [[vertex(strip[0, i]), vertex(strip[0, i+1])]
                             for i in range(strip.shape[1]-1) if params[i] >= 32 and params[i+1] <= 336],
                  'farfield': [], 'outlet': []}
    for curve in lines_outer:
        _, _, elements = gmsh.model.mesh.getElements(1, curve)
        for line in elements[0].reshape(-1, 2):
            ids = [node_map[int(n)] for n in line]
            x = np.asarray([nodes[n] for n in ids])
            # The original open C boundary is closed by the downstream plane.
            patch = 'outlet' if np.all(np.abs(x[:, 0]-g[0, 0, 0]) < 1e-8) else 'farfield'
            patches_2d[patch].append(ids)
    gmsh.finalize()
    xy = np.array(nodes)
    cells = core+triangles
    # All planar cells positive and convex; normalize triangle orientation.
    for cell in cells:
        p = xy[cell]
        if area(p) < 0:
            cell.reverse()
            p = xy[cell]
        edges = np.roll(p, -1, axis=0)-p
        cross = edges[:, 0]*np.roll(edges[:, 1], -1)-edges[:, 1]*np.roll(edges[:, 0], -1)
        assert np.all(cross > 0), (cell, cross)
    edge_counts = Counter(tuple(sorted((cell[i], cell[(i+1) % len(cell)])))
                          for cell in cells for i in range(len(cell)))
    assert set(edge_counts.values()) == {1, 2}
    declared = {tuple(sorted(e)) for values in patches_2d.values() for e in values}
    actual = {e for e, count in edge_counts.items() if count == 1}
    assert declared == actual, (len(declared-actual), len(actual-declared))
    # Independent area closure: outer polygon minus the actual NASA airfoil.
    expected_area = abs(area(outer))-abs(area(g[0, 32:337]))
    total_area = sum(area(xy[cell]) for cell in cells)
    np.testing.assert_allclose(total_area, expected_area, rtol=1e-11)
    chord, span = .3048, .003048
    n2 = len(nodes)
    points = np.vstack([np.column_stack((xy*chord, np.full(n2, z))) for z in (-span/2, span/2)])
    patches = {name: [[a, b, b+n2, a+n2] for a, b in edges] for name, edges in patches_2d.items()}
    patches['frontAndBack'] = []
    for cell in cells:
        patches['frontAndBack'].extend([cell[::-1], [n+n2 for n in cell]])
    total_faces = len(edge_counts)+2*len(cells)
    internal_faces = sum(v == 2 for v in edge_counts.values())
    with (CASE/'fluid.msh').open('w') as f:
        f.write('$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$PhysicalNames\n5\n')
        for tag, name in enumerate(patches, 1):
            f.write(f'2 {tag} "{name}"\n')
        f.write('3 5 "fluid"\n$EndPhysicalNames\n$Nodes\n'+str(len(points))+'\n')
        for tag, xyz in enumerate(points, 1):
            f.write(str(tag)+' '+' '.join(f'{v:.16g}' for v in xyz)+'\n')
        f.write('$EndNodes\n$Elements\n'+str(len(cells)+sum(map(len, patches.values())))+'\n')
        element = 0
        for tag, faces in enumerate(patches.values(), 1):
            for face in faces:
                element += 1
                kind = 2 if len(face) == 3 else 3
                f.write(f'{element} {kind} 2 {tag} {tag} '+' '.join(str(n+1) for n in face)+'\n')
        for cell in cells:
            element += 1
            kind = 6 if len(cell) == 3 else 5
            f.write(f'{element} {kind} 2 5 5 '+' '.join(str(n+1) for n in cell+[n+n2 for n in cell])+'\n')
        f.write('$EndElements\n')
    np.savez(CASE/'TOPOLOGIA_2D.npz', xy_chord=xy,
             quads=np.asarray(core), triangles=np.asarray(triangles))
    (CASE/'Cp_experimental.csv').write_bytes((HERE/'piloto_r1/Cp_experimental.csv').read_bytes())
    metadata = dict(source='NASA RAE2822 Study4 wall strip + own Gmsh exterior',
        source_URL='https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html',
        source_grid_sha256=hashlib.sha256((SOURCE/'raetaf.x.fmt').read_bytes()).hexdigest(),
        gmsh_version=gmsh.__version__, source_strip=dict(jmax=jlast, imin=ilo, imax=ihi),
        added_source_column_subdivisions=inserted, requested_core_aspect_max=args.max_core_aspect,
        wall_and_first20_radial_rows_unchanged=True, original_farfield_polygon_unchanged=True,
        cells=len(cells), hexahedra=len(core), prisms=len(triangles), points=len(points),
        chord_m=chord, span_m=span, expected_internal_faces=internal_faces,
        expected_total_faces=total_faces, boundary_faces={k:len(v) for k,v in patches.items()},
        planar_area_closure_relative=abs(total_area-expected_area)/expected_area,
        summed_cell_volume_m3=total_area*chord**2*span,
        all_planar_cells_convex_positive=True, all_unpaired_edges_match_declared_boundaries=True,
        mesh_sha256=hashlib.sha256((CASE/'fluid.msh').read_bytes()).hexdigest(),
        checkMesh_accepted=False, physical_validation_accepted=False,
        limitation='Own hybrid mesh is not the NASA supplied grid; must compare mesh/domain/scheme sensitivity and experimental Cp before acceptance.')
    (CASE/'MALLA.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
