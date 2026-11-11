"""Plot a verified SST/SA comparison without calling its spread uncertainty."""
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
import numpy as np
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy

from auditar_malla_su2 import read_mesh
from reconstruir_traccion_su2 import boundary_cycle

HERE = Path(__file__).resolve().parent


def surface(case):
    inputs = json.loads((case/'ENTRADAS.json').read_text())
    xy, _, markers = read_mesh(case/'mesh_RAE2822_turb.su2')
    reader = vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(case/'flow.vtu'))
    reader.Update()
    grid = reader.GetOutput()
    coords = vtk_to_numpy(grid.GetPoints().GetData())[:, :2]
    a, b = np.lexsort((coords[:,1],coords[:,0])), np.lexsort((xy[:,1],xy[:,0]))
    np.testing.assert_allclose(coords[a],xy[b],atol=1e-12,rtol=0)
    mapping=np.empty(len(xy),dtype=int);mapping[b]=a
    cp=vtk_to_numpy(grid.GetPointData().GetArray('Pressure_Coefficient'))[mapping]
    cf=vtk_to_numpy(grid.GetPointData().GetArray('Skin_Friction_Coefficient'))[mapping,0]
    cycle=boundary_cycle(markers['AIRFOIL'],xy)
    le,te=np.argmin(xy[cycle,0]),np.argmax(xy[cycle,0]);paths=[]
    for step in (1,-1):
        ix=[int(le)]
        while ix[-1]!=te:ix.append((ix[-1]+step)%len(cycle))
        paths.append(cycle[ix])
    paths.sort(key=lambda ix:np.mean(xy[ix,1]))
    result=[]
    for ix in paths:
        ix=ix[np.argsort(xy[ix,0])]
        result.append(np.column_stack((xy[ix,0]/inputs['declared_conditions']['chord'],cp[ix],cf[ix])))
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--comparison',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();data=json.loads(args.comparison.read_text())
    assert not args.output_dir.exists(),'Preserve the earlier scientific figure'
    for path,digest in data['source_sha256'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
    sst,sa=HERE/data['SST_case'],HERE/data['SA_case']
    cases=[('SST-2003m',sst,'#D55E00'),('SA-noft2',sa,'#0072B2')]
    arrays={name:surface(case) for name,case,_ in cases}
    exp=np.loadtxt(sa/'Cp_CONTRASTE_PROVISIONAL.csv',delimiter=',',skiprows=1)
    split=int(np.argmin(exp[:,0]));args.output_dir.mkdir(parents=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(2,2,figsize=(13,8.5),constrained_layout=True)
    for name,case,color in cases:
        lower,upper=arrays[name]
        axs[0,0].plot(upper[:,0],upper[:,1],color=color,label=name,lw=1.6)
        axs[0,0].plot(lower[:,0],lower[:,1],color=color,ls='--',lw=1.2)
        axs[0,1].plot(upper[:,0],upper[:,1],color=color,label=name,lw=1.6)
        axs[1,1].plot(upper[:,0],upper[:,2],color=color,label=name,lw=1.6)
    for ax in axs[0]:
        ax.scatter(exp[:split+1,0],exp[:split+1,1],s=22,facecolors='none',edgecolors='#222',label='Ensayo extradós')
        ax.invert_yaxis();ax.set(xlabel='x/c',ylabel='Cp físico');ax.grid(alpha=.15)
    axs[0,0].scatter(exp[split+1:,0],exp[split+1:,1],s=20,facecolors='none',edgecolors='#222',marker='^',label='Ensayo intradós')
    axs[0,0].set(title='Presiones: misma geometría y condiciones',xlim=(-.01,1.01))
    axs[0,0].legend(fontsize=8)
    axs[0,1].set(xlim=(.45,.65),ylim=(.0,-1.4),title='Detalle de recuperación de presión')
    axs[0,1].legend(fontsize=8)
    differences=[100*data['coefficients'][k]['relative_to_SST'] for k in ('last_CL','last_CD')]
    ax=axs[1,0];bars=ax.bar(['CL','CD'],differences,color=['#009E73','#7B6FA6'],width=.5)
    ax.axhline(0,color='#555',lw=.8);ax.bar_label(bars,labels=[f'{v:+.2f}%' for v in differences],padding=4)
    ax.set(ylabel='Cambio de SA respecto a SST, %',title='Sensibilidad calculada; no intervalo de confianza')
    ax.margins(y=.2);ax.grid(axis='y',alpha=.15)
    ax=axs[1,1];ax.axhline(0,color='#555',lw=.8)
    ax.set(xlim=(.35,.75),xlabel='x/c',ylabel='Cf,x sobre extradós',title='Fricción axial en la zona de recuperación')
    ax.legend(fontsize=8);ax.grid(alpha=.15)
    fig.suptitle('RAE2822 · SST frente a Spalart–Allmaras\nResultados de cálculo; validación física pendiente',fontsize=14,weight='bold')
    fig.savefig(args.output_dir/'COMPARACION.png',dpi=170)
    fig.savefig(args.output_dir/'COMPARACION.svg');plt.close(fig)
    provenance=dict(comparison_sha256=hashlib.sha256(args.comparison.read_bytes()).hexdigest(),
        renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_vtu_sha256={str(case/'flow.vtu'):hashlib.sha256((case/'flow.vtu').read_bytes()).hexdigest() for _,case,_ in cases},
        all103experimental_points_retained=True,physical_validation_accepted=False,vehicle_simulation=False)
    (args.output_dir/'PROCEDENCIA.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(args.output_dir/'COMPARACION.png')


if __name__=='__main__':main()
