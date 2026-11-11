"""Produce an auditable scientific diagnostic from saved native CFD outputs."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import tempfile

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'codex-aero-matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
import numpy as np
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy

from auditar_malla_su2 import read_mesh
from auditar_su2 import table
from reconstruir_traccion_su2 import boundary_cycle
from verificar_convencion_cp import read_gen

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, required=True)
    args = parser.parse_args()
    case = args.case.resolve()
    assert not (case/'DIAGNOSTICO.png').exists(), 'Keep previous diagnostic snapshot'
    audit = json.loads((case/'AUDITORIA_SU2.json').read_text())
    cond = json.loads((case/'ENTRADAS.json').read_text())['declared_conditions']
    xy, cells, markers = read_mesh(case/'mesh_RAE2822_turb.su2')
    xy /= cond['chord']
    reader = vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(case/'flow.vtu'))
    reader.Update()
    grid = reader.GetOutput()
    xyz = vtk_to_numpy(grid.GetPoints().GetData())[:, :2]/cond['chord']
    a, b = np.lexsort((xyz[:, 1], xyz[:, 0])), np.lexsort((xy[:, 1], xy[:, 0]))
    np.testing.assert_allclose(xyz[a], xy[b], atol=1e-12, rtol=0)
    mapping = np.empty(len(xy), dtype=int)
    mapping[b] = a
    cp = vtk_to_numpy(grid.GetPointData().GetArray('Pressure_Coefficient'))[mapping]
    mach = vtk_to_numpy(grid.GetPointData().GetArray('Mach'))[mapping]
    cycle = boundary_cycle(markers['AIRFOIL'], xy)
    poly = xy[cycle]
    le, te = np.argmin(poly[:, 0]), np.argmax(poly[:, 0])
    paths = []
    for direction in (1, -1):
        path = [int(le)]
        while path[-1] != te:
            path.append((path[-1]+direction) % len(poly))
        paths.append(cycle[path])
    paths.sort(key=lambda ix: np.mean(xy[ix, 1]))
    lower, upper = paths
    exp = np.loadtxt(case/'Cp_CONTRASTE_PROVISIONAL.csv', delimiter=',', skiprows=1)
    split = np.argmin(exp[:, 0])
    wind = read_gen(HERE.parents[2]/'fuentes/benchmark_RAE2822/cp.wind.gen', 305)
    wind_le = np.argmin(wind[:, 0])
    wlo, wup = wind[:wind_le+1][::-1], wind[wind_le:]
    triangles = []
    for cell in cells:
        triangles.append(cell[:3])
        if len(cell) == 4:
            triangles.append([cell[0], cell[2], cell[3]])
    triangles = np.asarray(triangles)
    centers = xy[triangles].mean(axis=1)
    keep = (centers[:, 0] > -.15) & (centers[:, 0] < 1.3) & (abs(centers[:, 1]) < .35)
    triang = Triangulation(xy[:, 0], xy[:, 1], triangles[keep])
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axs = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    ax = axs[0, 0]
    for ix, color, label in ((upper, '#0072B2', 'SU2 extradós'), (lower, '#D55E00', 'SU2 intradós')):
        order = np.argsort(xy[ix, 0])
        ax.plot(xy[ix[order], 0], cp[ix[order]], color=color, lw=1.6, label=label)
    ax.scatter(exp[:split+1, 0], exp[:split+1, 1], facecolors='none', edgecolors='#222', s=22, label='Ensayo: 103 puntos')
    ax.scatter(exp[split+1:, 0], exp[split+1:, 1], facecolors='none', edgecolors='#222', s=22, marker='^')
    for i, w in enumerate((wup, wlo)):
        ax.plot(w[:, 0], -w[:, 1], ':', color='#777', alpha=.8, label='WIND publicado (SA)' if i == 0 else None)
    ax.invert_yaxis()
    ax.set(xlabel='x/c', ylabel='Cp físico', title='Presiones: contraste provisional')
    ax.legend(fontsize=8, loc='best')
    ax.grid(alpha=.15)
    ax = axs[0, 1]
    image = ax.tripcolor(triang, mach, shading='gouraud', cmap='viridis', vmin=0, vmax=max(1.3, float(mach.max())))
    if mach.max() > 1:
        ax.tricontour(triang, mach, levels=[1.], colors='white', linewidths=.7)
    ax.fill(poly[:, 0], poly[:, 1], '#151923', zorder=10)
    ax.set(xlim=(-.07, 1.15), ylim=(-.22, .24), aspect='equal', xlabel='x/c', ylabel='y/c', title='Campo calculado de Mach; línea blanca M=1')
    fig.colorbar(image, ax=ax, shrink=.75, label='Mach local')
    h = table(case/'history.csv')
    ax = axs[1, 0]
    for name in ('rms[Rho]', 'rms[RhoE]', 'rms[k]', 'rms[w]'):
        ax.plot(h['Inner_Iter'], h[name], label=name, lw=1.)
    ax.set(xlabel='Iteración de esta rama; sin tiempo físico', ylabel='log10 del residuo reportado', title='Cada ecuación conserva su escala dimensional')
    ax.legend(fontsize=8)
    ax.grid(alpha=.15)
    ax = axs[1, 1]
    ax.scatter(exp[:split+1, 0], exp[:split+1, 3], color='#0072B2', s=18, label='Error extradós')
    ax.scatter(exp[split+1:, 0], exp[split+1:, 3], color='#D55E00', s=18, marker='^', label='Error intradós')
    ax.axhline(0, color='#555', lw=.8)
    ax.set(xlabel='x/c', ylabel='Cp calculado − Cp experimental', title=f"RMS={audit['Cp_RMS_error_provisional']:.5f}; sin excluir puntos")
    ax.legend(fontsize=8)
    ax.grid(alpha=.15)
    fig.suptitle(f"RAE2822 · {case.name} · M∞={cond['Mach']} · α={cond['alpha_deg']}°\nDiagnóstico CFD: convergencia y validación física pendientes", fontsize=14, weight='bold')
    fig.savefig(case/'DIAGNOSTICO.png', dpi=170)
    fig.savefig(case/'DIAGNOSTICO.svg')
    plt.close(fig)
    (case/'DIAGNOSTICO_PROCEDENCIA.json').write_text(json.dumps(dict(
        physical_validation_accepted=False, vehicle_simulation=False,
        source_URL='https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (case/'flow.vtu', case/'history.csv', case/'AUDITORIA_SU2.json', case/'Cp_CONTRASTE_PROVISIONAL.csv')},
        renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()), indent=2)+'\n')
    print(case/'DIAGNOSTICO.png')


if __name__ == '__main__':
    main()
