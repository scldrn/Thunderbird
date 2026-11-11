"""Check native fields, force integration and provisional experimental Cp."""
from pathlib import Path
import argparse
import csv
import hashlib
import json

import numpy as np
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy

from auditar_malla_su2 import read_mesh

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def table(path):
    with path.open() as f:
        rows=csv.reader(f);header=[s.strip().strip('"') for s in next(rows)]
        a=np.array([[float(v) for v in row] for row in rows if row])
    assert np.isfinite(a).all(),path
    return {name:a[:,i] for i,name in enumerate(header)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',type=Path,required=True)
    parser.add_argument('--reference-case',type=Path)
    args=parser.parse_args();case=args.case.resolve()
    terminal=json.loads((case/'EJECUCION.json').read_text())
    assert terminal['stage']=='solver_exited' and terminal['exit_code']==0
    inputs=json.loads((case/'ENTRADAS.json').read_text());cond=inputs['declared_conditions']
    log=(case/'log.SU2_CFD').read_text()
    gas_model=cond.get('gas_model','STANDARD_AIR')
    gamma=cond.get('gamma',1.4);R=cond.get('gas_R_J_kg_K',287.058)
    assert gas_model in log and 'SUTHERLAND' in log
    assert 'SST-2003m' in log
    xy,cells,markers=read_mesh(case/'mesh_RAE2822_turb.su2')
    fields=table(case/'restart_flow.csv');ids=fields['PointID'].astype(int)
    np.testing.assert_array_equal(np.sort(ids),np.arange(len(xy)))
    order=np.argsort(ids)
    fields={k:v[order] for k,v in fields.items()}
    np.testing.assert_allclose(np.column_stack((fields['x'],fields['y'])),xy,rtol=0,atol=1e-12)
    rho=fields['Density'];assert rho.min()>0
    velocity=np.column_stack((fields['Momentum_x'],fields['Momentum_y']))/rho[:,None]
    # The subtraction of turbulent kinetic energy follows CNSVariable::SetPrimVar.
    pressure=(gamma-1)*(fields['Energy']-.5*rho*np.sum(velocity**2,axis=1)-rho*fields['Turb_Kin_Energy'])
    temp=pressure/(rho*R)
    assert pressure.min()>0 and temp.min()>0
    reader=vtkXMLUnstructuredGridReader();reader.SetFileName(str(case/'flow.vtu'));reader.Update()
    grid=reader.GetOutput();assert grid.GetNumberOfPoints()==len(xy) and grid.GetNumberOfCells()==len(cells)
    xyz=vtk_to_numpy(grid.GetPoints().GetData())
    a=np.lexsort((xyz[:,1],xyz[:,0]));b=np.lexsort((xy[:,1],xy[:,0]))
    np.testing.assert_allclose(xyz[a,:2],xy[b],rtol=0,atol=1e-12)
    vtu_to_mesh=np.empty(len(xy),dtype=int);vtu_to_mesh[b]=a
    arrays={}
    for n in range(grid.GetPointData().GetNumberOfArrays()):
        name=grid.GetPointData().GetArrayName(n)
        values=vtk_to_numpy(grid.GetPointData().GetArray(n))[vtu_to_mesh]
        assert np.isfinite(values).all(),name
        arrays[name]=values
    # Primitive thermodynamics is evaluated before the segregated turbulence
    # update (CFluidIteration). Current k and retained p/T may therefore lag;
    # measure that discrepancy rather than invent an exact identity.
    thermo_difference=dict(pressure_max_abs_Pa=float(abs(arrays['Pressure']-pressure).max()),
        pressure_max_relative=float(np.max(abs(arrays['Pressure']-pressure)/arrays['Pressure'])),
        temperature_max_abs_K=float(abs(arrays['Temperature']-temp).max()))
    assert arrays['Pressure'].min()>0 and arrays['Temperature'].min()>0
    Tinf=cond['T_freestream_K'];mach=cond['Mach']
    mu_ref=cond.get('mu_reference_Pas',1.716e-5)
    mu_T_ref=cond.get('mu_reference_temperature_K',273.15)
    sutherland=cond.get('Sutherland_K',110.4)
    mu=mu_ref*(Tinf/mu_T_ref)**1.5*(mu_T_ref+sutherland)/(Tinf+sutherland)
    speed=mach*np.sqrt(gamma*R*Tinf)
    rhoinf=cond['Reynolds']*mu/(speed*cond['chord'])
    pinf=rhoinf*R*Tinf;q=.5*rhoinf*speed**2
    cp=(arrays['Pressure']-pinf)/q
    np.testing.assert_allclose(cp,arrays['Pressure_Coefficient'],rtol=1e-8,atol=1e-8)
    history=table(case/'history.csv')
    # Native 2D force coefficients are per unit span, reference area = chord.
    np.testing.assert_allclose(history['RefForce'],q*cond['chord'],rtol=1e-8)
    edges=np.array(markers['AIRFOIL'],dtype=int)
    vertices=np.unique(edges)
    adjacency={int(i):[] for i in vertices}
    for i,j in edges:
        adjacency[int(i)].append(int(j));adjacency[int(j)].append(int(i))
    start=int(vertices[0]);cycle=[start];previous=None;node=start
    for _ in vertices:
        nxt=next(i for i in adjacency[node] if i!=previous)
        if nxt==start:break
        assert nxt not in cycle
        cycle.append(nxt);previous,node=node,nxt
    assert len(cycle)==len(vertices)
    cycle=np.array(cycle);poly=xy[cycle]
    signed_area=.5*np.sum(poly[:,0]*np.roll(poly[:,1],-1)-poly[:,1]*np.roll(poly[:,0],-1))
    if signed_area<0:cycle=cycle[::-1];poly=xy[cycle]
    tangent=np.roll(poly,-1,axis=0)-poly
    outward_body=np.column_stack((tangent[:,1],-tangent[:,0]))
    pressure_coeff_force=-np.sum(.5*(cp[cycle]+np.roll(cp[cycle],-1))[:,None]*outward_body,axis=0)/cond['chord']
    cf=arrays['Skin_Friction_Coefficient'][cycle,:2]
    viscous_coeff_force=np.sum(.5*(cf+np.roll(cf,-1,axis=0))*np.linalg.norm(tangent,axis=1)[:,None],axis=0)/cond['chord']
    total=pressure_coeff_force+viscous_coeff_force
    # Skin_Friction_Coefficient contains only tangential traction. SU2 force
    # accumulation uses full Tau*normal and dual boundary areas (see
    # CFVMFlowSolverBase.inl). This polygon integral is an incomplete force
    # reconstruction, so report its difference without falsely accepting it.
    force_difference=total-np.array([history['CFx'][-1],history['CFy'][-1]])
    # Split the actual SU2 polygon into two LE-to-TE paths and classify their
    # vertical order. Match experimental chord positions without extrapolation.
    le=int(np.argmin(poly[:,0]));te=int(np.argmax(poly[:,0]));N=len(poly)
    paths=[]
    for step in (1,-1):
        indices=[le];i=le
        while i!=te:
            i=(i+step)%N;indices.append(i)
            assert len(indices)<=N
        paths.append(cycle[indices])
    paths.sort(key=lambda ix:float(np.mean(xy[ix,1])))
    lower,upper=paths
    exp=np.loadtxt(HERE/'piloto_r1/Cp_experimental.csv',delimiter=',',skiprows=1)
    convention=json.loads((HERE/'CONVENCION_CP_VERIFICADA.json').read_text())
    assert convention['physical_Cp_multiplier']==-1
    exp[:,1]*=-1
    split=int(np.argmin(exp[:,0]));predicted=[]
    for ix,taps in ((upper,exp[:split+1,0]),(lower,exp[split+1:,0])):
        order=np.argsort(xy[ix,0]);x=xy[ix[order],0]/cond['chord']
        assert taps.min()>=x.min() and taps.max()<=x.max()
        predicted.extend(np.interp(taps,x,cp[ix[order]]))
    predicted=np.asarray(predicted);error=predicted-exp[:,1]
    np.savetxt(case/'Cp_CONTRASTE_PROVISIONAL.csv',np.column_stack((exp,predicted,error)),delimiter=',',
               header='x_over_c,Cp_exp_normalized,Cp_own,error',comments='')
    changes=None
    if args.reference_case:
        earlier=table(args.reference_case.resolve()/'restart_flow.csv')
        order=np.argsort(earlier['PointID'])
        earlier={k:v[order] for k,v in earlier.items()}
        np.testing.assert_allclose(earlier['x'],xy[:,0],atol=1e-12)
        np.testing.assert_allclose(earlier['y'],xy[:,1],atol=1e-12)
        changes={k:dict(max_abs=float(abs(v-earlier[k]).max()),arithmetic_RMS=float(np.sqrt(np.mean((v-earlier[k])**2))))
                 for k,v in fields.items() if k not in ('PointID','x','y')}
        for k,item in changes.items():
            delta=fields[k]-earlier[k];scale=max(float(abs(earlier[k]).max()),1e-300)
            at=int(np.argmax(abs(delta)))
            item.update(relative_Linf_to_reference_Linf=float(abs(delta).max()/scale),
                relative_L2=float(np.linalg.norm(delta)/max(np.linalg.norm(earlier[k]),1e-300)),
                max_change_node_ID=at,max_change_xy=xy[at].tolist(),
                max_change_is_airfoil_node=bool(at in vertices),
                reference_value_at_max_change=float(earlier[k][at]),
                current_value_at_max_change=float(fields[k][at]))
    report=dict(scope='Native benchmark field and force audit with provisional Cp comparison; not accepted physical validation',
        last_inner_iteration_index=int(history['Inner_Iter'][-1]),
        source_solver_convergence_message=('All convergence criteria satisfied.' in log),
        convergence_message_does_not_cover_all_equations=True,
        actual_model=f'SST-2003m; {gas_model}/Sutherland/constantPr0.72/0.9',
        reconstructed_reference=dict(p_Pa=pinf,rho_kg_m3=rhoinf,T_K=Tinf,U_m_s=speed,q_Pa=q),
        rho_range_kg_m3=[float(rho.min()),float(rho.max())],pressure_range_Pa=[float(pressure.min()),float(pressure.max())],
        temperature_range_K=[float(temp.min()),float(temp.max())],maximum_local_Mach=float(arrays['Mach'].max()),
        CSV_VTU_coordinate_mapping_verified=True,retained_vs_recomputed_thermodynamics=thermo_difference,
        exact_thermodynamic_identity_not_asserted_due_segregated_update=True,
        Cp_reference_reconstruction_verified=True,
        pressure_and_tangential_shear_polygon_integrals_evaluated=True,
        complete_solver_force_identity_verified=False,
        incomplete_reconstruction_minus_solver_coeff_force=force_difference.tolist(),
        incomplete_reconstruction_limit='SurfaceCf is tangential only; full normal viscous stress and solver dual-area weights remain to reconstruct.',
        force_coeff_pressure=pressure_coeff_force.tolist(),force_coeff_viscous=viscous_coeff_force.tolist(),
        last_CL=float(history['CL'][-1]),last_CD=float(history['CD'][-1]),
        last20_log10_residual_max={k:float(v[-20:].max()) for k,v in history.items() if k.startswith('rms[')},
        adjacent20_force_coefficient_drift={k:float(abs(v[-20:].mean()-v[-40:-20].mean())) for k,v in history.items() if k in ('CL','CD')},
        Cp_points=len(exp),Cp_RMS_error_provisional=float(np.sqrt(np.mean(error**2))),Cp_max_abs_error_provisional=float(abs(error).max()),
        wall_reported_yPlus_range=[float(arrays['Y_Plus'][vertices].min()),float(arrays['Y_Plus'][vertices].max())],
        reference_field_changes=changes,
        remaining='Verify full-state convergence including turbulence, mesh/wall resolution and NASA geometry/conditions alignment; compare sensitivities before validation.',
        physical_validation_accepted=False,vehicle_performance_accepted=False,
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (case/'restart_flow.csv',case/'flow.vtu',case/'history.csv',case/'case.cfg')})
    (case/'AUDITORIA_SU2.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('last_inner_iteration_index','last_CL','last_CD','Cp_RMS_error_provisional',
        'complete_solver_force_identity_verified','last20_log10_residual_max')},indent=2))


if __name__=='__main__':
    main()
