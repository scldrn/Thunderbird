"""Audit analytical velocity, pressure gradient, flux, sign and solver work."""
from pathlib import Path
import hashlib
import json
import re
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'CFD'))
from foam_fields import read_internal


def patch_values(path,name):
    text=Path(path).read_text().split('boundaryField',1)[1]
    match=re.search(r'\b'+name+r'\s*\{',text)
    assert match,name
    level=1;end=match.end()
    while level:
        if text[end]=='{':level+=1
        elif text[end]=='}':level-=1
        end+=1
    block=text[match.end():end-1]
    m=re.search(r'value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)\s*;',block,re.S)
    assert m,'Nonuniform scalar patch expected'
    values=np.fromstring(m[2],sep=' ')
    assert values.size==int(m[1]) and np.isfinite(values).all()
    return values


def main():
    root=HERE/'benchmark_salto'
    y=(np.arange(40)+.5)/40
    k=(np.arange(1000)+.5)*np.pi
    expected=50*(y-y*y/2)-np.sin(y[:,None]*k)@(100/k**3*np.exp(-.1*k*k*4))
    results=[];velocity={}
    for nx in (1,4):
        for orientation in ('forward','reverse'):
            name=f'fan_jump_{orientation}' if nx==1 else f'fan_jump_nx4_{orientation}'
            case=root/name
            u=read_internal(case/'4/U',40*nx,3).reshape(40,nx,3)
            p=read_internal(case/'4/p',40*nx,1).reshape(40,nx)
            sign=-1 if orientation=='forward' else 1
            error=float(np.max(np.abs(u[:,:,0]-sign*expected[:,None]))/expected.max())
            log=(case/'log.foamRun').read_text()
            assert log.rstrip().endswith('End')
            iterations=np.array([int(i) for i in re.findall(r'Solving for p,.*No Iterations (\d+)',log)])
            times=re.findall(r'ExecutionTime = ([\d.eE+-]+) s\s+ClockTime = ([\d.eE+-]+) s',log)[-1]
            left=patch_values(case/'4/phi','left').sum()
            right=patch_values(case/'4/phi','right').sum()
            q_from_cells=float(u[:,:,0].mean()*.2)
            assert np.isclose(right,q_from_cells,rtol=1e-9,atol=1e-12)
            assert abs(left+right)<1e-10
            work_fan=abs(right)*1.0 # kinematic jump * volumetric flux
            equivalent_source_work=5*.04*abs(float(u[:,:,0].mean()))
            assert np.isclose(work_fan,equivalent_source_work,rtol=1e-10)
            gradient_error=None
            if nx>1:
                gradient_error=float(np.max(np.abs(np.diff(p,axis=1)/(.2/nx)+sign*5)))
                assert gradient_error<1e-7
                assert np.max(iterations)<1000 and error<.001
            record=dict(case=name,Nx=nx,Ny=40,velocity_Linf_relative=error,
                mean_velocity_m_s=float(u[:,:,0].mean()),max_transverse_velocity_m_s=float(np.max(np.abs(u[:,:,1:]))),
                pressure_internal_min=float(p.min()),pressure_internal_max=float(p.max()),
                expected_dpdx_kinematic=-sign*5,dpdx_max_abs_error=gradient_error,
                pressure_solves=len(iterations),pressure_max_iterations=int(iterations.max()),
                pressure_solves_hitting_1000=int(np.sum(iterations>=1000)),
                pressure_iter_p95=float(np.percentile(iterations,95)),
                execution_CPU_s=float(times[0]),wall_s=float(times[1]),
                left_volume_flux_m3_s=float(left),right_volume_flux_m3_s=float(right),
                mass_balance_volume_flux_error_m3_s=float(abs(left+right)),
                hydraulic_power_at_rho_1_225_W=float(1.225*work_fan),
                pressure_jump_source_work_identity_relative_error=float(abs(work_fan/equivalent_source_work-1)),
                accepted_for_this_operator_verification=nx==4,
                rejection_if_any='One streamwise cell gives degenerate near-zero internal pressure and repeated iteration cap; do not use as production settings' if nx==1 else None,
                input_sha256=json.loads((case/'ENTRADAS.json').read_text())['input_sha256'],
                output_sha256={str(q.relative_to(case)):hashlib.sha256(q.read_bytes()).hexdigest() for q in (case/'4/U',case/'4/p',case/'4/phi',case/'log.foamRun')})
            results.append(record)
            velocity[(nx,orientation)]=u
    for nx in (1,4):assert np.max(np.abs(velocity[nx,'forward']+velocity[nx,'reverse']))<1e-8
    report=dict(scope='Verification of pressure-jump operator against channel PDE, not fan or vehicle validation',
        reference=dict(H_m=1.,L_m=.2,nu_m2_s=.1,t_s=4.,jump_kinematic_m2_s2=1.,G_equivalent_m_s2=5.),
        cases=results,orientation_in_this_mesh='owner=left; reverse=false gives -X flow, reverse=true gives +X flow',
        conclusion='Resolving the streamwise gradient removes the iteration-cap pathology while preserving velocity and pressure/flux/work identities.',
        limitations=['No formal space/time order or turbulence/rotor/wall-loss validation from these four cases.',
                     'Do not transfer the measured tiny-case cost to a 3D installed map.',
                     'Pressure input has kinematic units because p dimensions are [0 2 -2]; multiply by density for Pa.',
                     'Boundary conditions are a numerical actuator model, not a measured pressure-flow curve.'],
        primary_method='https://cpp.openfoam.org/v13/classFoam_1_1fanPressureJumpFvPatchScalarField.html')
    (root/'AUDITORIA.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('case','velocity_Linf_relative','pressure_max_iterations','pressure_solves_hitting_1000','execution_CPU_s','accepted_for_this_operator_verification')} for r in results],indent=2))


if __name__=='__main__':main()
