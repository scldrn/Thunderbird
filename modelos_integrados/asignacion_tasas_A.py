"""Joint sampled inverse dynamics with bounded useful-force change.
Piecewise-linear force interpolation is continuous and respects convex force
limits and slew bounds. It approximates the nonlinear prescribed rigid-body
wrench between nodes; dense residuals are reported, not hidden as exact flight.
"""
from pathlib import Path
import json,math,time,argparse
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import block_diag,kron,diags,vstack,csc_matrix
from reversibilidad_6dof_A import cone_rays,wrench_matrix

ROOT=Path(__file__).resolve().parent;BASE=ROOT/'empaquetado_axial_A';OUT=BASE/'masa_y_agilidad/tasas';OUT.mkdir(exist_ok=True)
source=json.loads((BASE/'masa_y_agilidad/ESCENARIOS.json').read_text())
layouts=json.loads((BASE/'RESUMEN.json').read_text())['selected_finite_search_candidates']
def target(u,T,I):
    q=math.pi/6*(10*u**3-15*u**4+6*u**5)
    w=np.array([0,math.pi/6*(30*u*u-60*u**3+30*u**4)/T,0])
    a=np.array([0,math.pi/6*(60*u-180*u*u+120*u**3)/T**2,0])
    return np.r_[5*9.80665*np.array([-math.sin(q),0,math.cos(q)]),I@a+np.cross(w,I@w)]

def solve(layout,scenario,T,S,n):
    start=time.monotonic();I=np.array(scenario['inertia_kgm2']);cg=np.array(scenario['CG_m']);p=np.array(layout['positions_m'])-cg
    rays=cone_rays(45);K=len(rays);H=block_diag([rays.T]*4,format='csc');B=np.hstack([wrench_matrix(x,-.039-cg[2],-.021-cg[2]) for x in p])
    scales=np.r_[np.ones(3)*50,np.ones(3)*.5];A=csc_matrix(B/scales[:,None])@H
    U=np.zeros((8,4*K));bu=np.r_[np.ones(4)*21,-np.ones(4)]
    for i in range(4):U[i,i*K:(i+1)*K]=1;U[4+i,i*K:(i+1)*K]=-rays[:,2]
    differences=diags([-np.ones(n-1),np.ones(n-1)],[0,1],shape=(n-1,n),format='csc')
    slew=kron(differences,H,format='csc');dt=T/(n-1);bound=S*dt/math.sqrt(3)
    Au=vstack([block_diag([csc_matrix(U)]*n,format='csc'),slew,-slew],format='csc')
    b=np.r_[np.tile(bu,n),np.ones(24*(n-1))*bound]
    u=np.linspace(0,1,n);wrench=np.array([target(a,T,I) for a in u])
    sol=linprog(np.ones(n*4*K),A_ub=Au,b_ub=b,A_eq=block_diag([A]*n,format='csc'),b_eq=(wrench/scales).ravel(),bounds=(0,None),method='highs',options={'time_limit':45})
    result=dict(axial_reserve_outer_mm=layout['axial_diameter_with_2mm_radial_margin_mm'],duration_s=T,force_vector_slew_limit_N_s=S,nodes=n,solver_status=int(sol.status),solver_message=sol.message,feasible=bool(sol.success),calculation_wall_s=time.monotonic()-start)
    if sol.success:
        f=sol.x.reshape(n,4,K)@rays;achieved=np.einsum('ij,nj->ni',B,f.reshape(n,12))
        rate=np.linalg.norm(np.diff(f,axis=0),axis=2)/dt
        error=float(np.max(abs(achieved-wrench)))
        assert error<2e-6 and rate.max()<=S+1e-6
        assert np.linalg.norm(f,axis=2).max()<=21+1e-7 and f[:,:,2].min()>=1-1e-7
        dense=np.linspace(0,1,20*(n-1)+1)
        interpolated=np.column_stack([np.interp(dense,u,col) for col in f.reshape(n,12).T])
        residual=interpolated@B.T-np.array([target(a,T,I) for a in dense])
        result.update(maximum_nodal_wrench_error_N_or_Nm=error,max_actual_piecewise_linear_force_vector_slew_N_s=float(rate.max()),maximum_interpolated_force_error_N=float(np.linalg.norm(residual[:,:3],axis=1).max()),maximum_interpolated_moment_error_Nm=float(np.linalg.norm(residual[:,3:],axis=1).max()))
        name=f"D{int(result['axial_reserve_outer_mm'])}_S{S:g}_T{T:.6f}_N{n}.npz"
        np.savez_compressed(OUT/name,time_s=u*T,force_vectors_N=f,requested_wrench_N_Nm=wrench,CG_m=cg,inertia_kgm2=I)
        result['trajectory_file']=name
    print(json.dumps(result),flush=True);return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');args=parser.parse_args()
    records=[];selected=[]
    for layout in layouts:
        candidates=[s for s in source['scenarios'] if s['half_pitch_mm']==layout['half_pitch_mm'] and s['sampled_feasible']]
        scenario=min(candidates,key=lambda s:s['quintic_30deg_minimum_sampled_duration_s'])
        lower=scenario['refinement_241_nodes']['quintic_30deg_minimum_sampled_duration_s']
        if args.pilot:
            solve(layout,scenario,lower*2,50,21);return
        for S in [20,50,100]:
            for factor in [1.01,1.5,2,3,5,10]:
                duration=lower*factor
                coarse=solve(layout,scenario,duration,S,41);records.append(coarse)
                (OUT/'PROGRESO.json').write_text(json.dumps(records,indent=2))
                if coarse['feasible']:
                    fine=solve(layout,scenario,duration,S,81);records.append(fine)
                    if fine['feasible']:
                        selected.append(fine);break
                if coarse['solver_status'] not in [0,2]:break
    (OUT/'RESULTADOS.json').write_text(json.dumps(dict(records=records,selected_finite_grid=selected,assumptions='Same fastest illustrative mass scenario for each layout. Nominal inverse dynamics with 21N, effective 45-degree positive cones, 1N preload; force component slew cube S/sqrt(3) implies vector slew <=S. No vane-angle/servo mapping, propulsion dynamics, power or rotor reaction.',reserve_scope='Durations start above the previous static reserve screen. Moment corrections are not jointly rate constrained; no dynamic disturbance-rejection guarantee.',actual_flight_validated=False),indent=2))
if __name__=='__main__':main()
