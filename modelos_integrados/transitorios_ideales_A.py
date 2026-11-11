"""Feasible ideal wrench ramps and actuator-rate requirements; no hardware dynamics.

Convex interpolation uses one fixed fan sign in each channel, never alternates
opposed force directions of an individual fan. Inactive-bank losses are unknown.
"""
from pathlib import Path
import argparse,json,math
import numpy as np
from scipy.optimize import linprog,minimize,lsq_linear
from reversibilidad_6dof_A import cone_rays

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'vectorizacion_A/reversibilidad_6DOF'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preload',type=float,default=1.);parser.add_argument('--case',choices=['doble_salida_refinada','base_horizontal_5kg'],default='doble_salida_refinada');args=parser.parse_args()
    if args.preload<1:raise ValueError('This study only raises the certified 1 N preload for selected endpoint examples.')
    preload=args.preload;suffix='' if preload==1 else '_precarga_'+str(preload).replace('.','p')
    prefix='BASE_HORIZONTAL_' if args.case=='base_horizontal_5kg' else ''
    meta=json.loads((OUT/(args.case+'.json')).read_text())
    d=np.load(OUT/(args.case+'.npz'))
    W=d['targets_N_Nm'];V=d['force_vectors_N'];B=d['wrench_matrices'];signs=d['signs'];limits=d['capacity_factors']*meta['positive_force_capacity_sufficient_N']
    mass=meta['mass_assumed_kg'];g=9.80665
    scale=np.r_[np.ones(3)*mass*g,np.ones(3)*.5]
    rays=cone_rays(meta['effective_cone_half_angle_deg']);K=len(rays)
    signed=rays[None,:,:]*signs[:,None,None]
    Aeq=np.zeros((6,4*K));Aub=np.zeros((8,4*K))
    for i in range(4):
        Aeq[:,i*K:(i+1)*K]=(B[i]@signed[i].T)/scale[:,None]
        Aub[i,i*K:(i+1)*K]=1
        Aub[4+i,i*K:(i+1)*K]=-rays[:,2]
    bub=np.r_[limits,-np.ones(4)*preload]
    # Direct ray allocation avoids a restriction to mixtures of stored domain
    # vertex solutions. Sum of weights bounds summed force magnitudes; it is
    # not electrical power, a nonlinear power optimum or a rate optimum.
    cost=np.ones(4*K)
    demands={'hover':np.array([0,0,mass*g]),'x_plus':mass*g*np.array([.5,0,1]),'x_minus':mass*g*np.array([-.5,0,1]),'y_plus':mass*g*np.array([0,.5,1]),'y_minus':mass*g*np.array([0,-.5,1]),'z_low':mass*g*np.array([0,0,.5]),'z_high':mass*g*np.array([0,0,1.5])}
    endpoints={};endpoint_json={}
    for name,force in demands.items():
        target=np.r_[force,[0.,0,0]]
        sol=linprog(cost,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=target/scale,bounds=(0,None),method='highs')
        if not sol.success:raise RuntimeError(f'No direct ray allocation for {name}')
        initial=np.einsum('ik,ikj->ij',sol.x.reshape(4,K),signed)
        # Refine in 12 force components on the circular cone. This minimizes
        # the isolated-free-rotor equal-area reference sum(||F_i||^1.5), not
        # installed fan power. Convex objective and concave >=0 constraints.
        T=meta['positive_force_capacity_sufficient_N']
        Ac=np.hstack([B[i] for i in range(4)])*T/scale[:,None]
        tangent=math.tan(math.radians(meta['effective_cone_half_angle_deg']))
        def objective(u):return float(np.sum(np.linalg.norm(u.reshape(4,3),axis=1)**1.5))
        def objective_jac(u):
            v=u.reshape(4,3);return (1.5*v/np.sqrt(np.linalg.norm(v,axis=1))[:,None]).ravel()
        def inequalities(u):
            v=u.reshape(4,3)
            return np.r_[signs*v[:,2]*tangent-np.linalg.norm(v[:,:2],axis=1),(limits/T)**2-(v*v).sum(axis=1),signs*v[:,2]-preload/T]
        def inequalities_jac(u):
            v=u.reshape(4,3);J=np.zeros((12,12))
            for i in range(4):
                h=np.linalg.norm(v[i,:2]);J[i,3*i:3*i+2]=-v[i,:2]/max(h,1e-15);J[i,3*i+2]=signs[i]*tangent
                J[4+i,3*i:3*i+3]=-2*v[i];J[8+i,3*i+2]=signs[i]
            return J
        opt=minimize(objective,(initial/T).ravel(),jac=objective_jac,constraints=[{'type':'eq','fun':lambda u:Ac@u-target/scale,'jac':lambda u:Ac},{'type':'ineq','fun':inequalities,'jac':inequalities_jac}],method='SLSQP',options={'ftol':1e-12,'maxiter':1000})
        if not opt.success:raise RuntimeError(f'Convex reference-power allocation failed for {name}: {opt.message}')
        f=opt.x.reshape(4,3)*T
        gg=inequalities(opt.x);active=np.flatnonzero(gg<1e-7)
        C=np.c_[Ac.T,inequalities_jac(opt.x)[active].T]
        lb=np.r_[np.full(6,-np.inf),np.zeros(len(active))]
        multipliers=lsq_linear(C,objective_jac(opt.x),bounds=(lb,np.full(len(lb),np.inf)),tol=1e-13,max_iter=1000).x
        stationarity=float(max(abs(C@multipliers-objective_jac(opt.x))))
        complementarity=float(max(abs(multipliers[6:]*gg[active]))) if len(active) else 0.
        assert stationarity<2e-5 and complementarity<1e-6 and min(gg)>-1e-8
        actual=np.einsum('ijk,ik->j',B,f)
        assert np.max(abs(actual-target))<1e-7
        assert np.min(signs*f[:,2])>=preload-1e-7
        assert np.max(np.linalg.norm(f,axis=1)-limits)<1e-7
        endpoints[name]=f
        # Open-rotor equivalent-area comparison only; not installed duct power.
        area=math.pi*(math.hypot(41,1)/1000)**2
        refpower=float(np.sum(np.linalg.norm(f,axis=1)**1.5/math.sqrt(2*1.225*area)))
        endpoint_json[name]=dict(target_wrench_N_Nm=target.tolist(),force_vectors_N=f.tolist(),allocation='Convex numerical minimization of isolated-free-rotor equal-area power reference on circular cones; not installed power.',dimensionless_KKT_stationarity_max_residual=stationarity,dimensionless_KKT_complementarity_max_residual=complementarity,force_cancellation_fraction=float(1-np.linalg.norm(force)/np.linalg.norm(f,axis=1).sum()),isolated_free_rotor_equal_area_power_reference_W=refpower)
    rows=[];saved={};slew_balanced=[];high_bias=[]
    pairs=[('x_minus','x_plus'),('y_minus','y_plus'),('x_plus','y_plus'),('z_low','z_high')]
    r=np.linspace(0,1,10001);blend=.5*(1-np.cos(np.pi*r))
    for a,b in pairs:
        f0=endpoints[a];delta=endpoints[b]-f0
        ff=f0[None,:,:]+blend[:,None,None]*delta[None,:,:]
        norms=np.linalg.norm(ff,axis=2)
        assert np.max(norms-limits)<1e-7
        assert np.min(ff[:,:,2]*signs)>=preload-1e-7
        actual=np.einsum('ijk,nik->nj',B,ff)
        target=(1-blend[:,None])*np.r_[demands[a],[0.,0,0]]+blend[:,None]*np.r_[demands[b],[0.,0,0]]
        residual=float(np.max(abs(actual-target)));assert residual<1e-7
        for duration in [.05,.1,.2,.5]:
            rate=(np.pi/(2*duration)*np.sin(np.pi*r))[:,None,None]*delta
            normrate=np.sum(ff*rate,axis=2)/norms
            angular=np.linalg.norm(np.cross(ff,rate),axis=2)/norms**2
            row=dict(start=a,end=b,duration_s=duration,max_useful_force_vector_slew_N_s_per_fan=np.max(np.linalg.norm(rate,axis=2),axis=0).tolist(),max_force_magnitude_slew_N_s_per_fan=np.max(abs(normrate),axis=0).tolist(),max_effective_force_direction_rate_deg_s_per_fan=np.degrees(np.max(angular,axis=0)).tolist(),max_commanded_acceleration_jerk_ms3=math.pi/(2*duration)*float(np.linalg.norm(demands[b]-demands[a]))/mass,max_equilibrium_residual_N_or_Nm=residual,peak_rates_method='10001 normalized-time samples of analytic raised-cosine interpolation; numerical maxima, not guaranteed hardware bandwidth.',physical_response_validated=False)
            rows.append(row)
            if duration==.1:
                saved[a+'_to_'+b+'_forces_N']=ff[::10]
        # Joint endpoint LP: minimize maximum absolute Cartesian force-component
        # change, then minimize ray-weight sum while retaining that optimum.
        N=4*K;Ae=np.zeros((12,2*N+1));Ae[:6,:N]=Aeq;Ae[6:,N:2*N]=Aeq
        be=np.r_[np.r_[demands[a],[0.,0,0]]/scale,np.r_[demands[b],[0.,0,0]]/scale]
        Au=np.zeros((40,2*N+1));Au[:8,:N]=Aub;Au[8:16,N:2*N]=Aub
        bu=np.r_[bub,bub,np.zeros(24)]
        c=16
        for i in range(4):
            for component in range(3):
                v=signed[i,:,component]
                for direction in [-1,1]:
                    Au[c,i*K:(i+1)*K]=-direction*v
                    Au[c,N+i*K:N+(i+1)*K]=direction*v
                    Au[c,-1]=-1;c+=1
        objective=np.zeros(2*N+1);objective[-1]=1
        optimum=linprog(objective,A_ub=Au,b_ub=bu,A_eq=Ae,b_eq=be,bounds=(0,None),method='highs')
        if not optimum.success:raise RuntimeError('Slew endpoint LP failed')
        dual=float(bu@optimum.ineqlin.marginals+be@optimum.eqlin.marginals)
        gap=abs(float(optimum.fun)-dual);assert gap<1e-6
        secondary_cost=np.r_[np.ones(2*N),0.]
        bounds=[(0,None)]*(2*N)+[(0,float(optimum.fun)*(1+1e-8)+1e-9)]
        second=linprog(secondary_cost,A_ub=Au,b_ub=bu,A_eq=Ae,b_eq=be,bounds=bounds,method='highs')
        if not second.success:raise RuntimeError('Slew secondary allocation failed')
        f0=np.einsum('ik,ikj->ij',second.x[:N].reshape(4,K),signed)
        f1=np.einsum('ik,ikj->ij',second.x[N:2*N].reshape(4,K),signed);df=f1-f0
        ff=f0[None,:,:]+blend[:,None,None]*df[None,:,:]
        norms=np.linalg.norm(ff,axis=2)
        assert np.max(norms-limits)<1e-7 and np.min(ff[:,:,2]*signs)>=preload-1e-7
        assert np.max(abs(np.einsum('ijk,nik->nj',B,ff)-target))<1e-7
        rate=(np.pi/(2*.1)*np.sin(np.pi*r))[:,None,None]*df
        angular=np.linalg.norm(np.cross(ff,rate),axis=2)/norms**2
        powers=[float(np.sum(np.linalg.norm(f,axis=1)**1.5/math.sqrt(2*1.225*area))) for f in [f0,f1]]
        slew_balanced.append(dict(start=a,end=b,duration_s=.1,start_force_vectors_N=f0.tolist(),end_force_vectors_N=f1.tolist(),optimal_Linf_cartesian_component_difference_N=float(optimum.fun),LP_primal_dual_gap_N=gap,max_useful_force_vector_slew_N_s_per_fan=np.max(np.linalg.norm(rate,axis=2),axis=0).tolist(),max_effective_force_direction_rate_deg_s_per_fan=np.degrees(np.max(angular,axis=0)).tolist(),endpoint_isolated_free_rotor_power_references_W=powers,scope='Optimizes component difference in this fixed ray LP with fixed capacity. Not minimum mechanical angular rate, electrical power or globally fastest physical maneuver. Endpoint allocations are specific to this transition.'))
        saved[a+'_to_'+b+'_slew_balanced_forces_N']=ff[::10]
        # Keep the component-change optimum, then maximize the minimum signed
        # axial force to reduce direction-rate sensitivity near a weak actuator.
        Aeb=np.c_[Ae,np.zeros(12)];Aubias=np.zeros((48,2*N+2));Aubias[:40,:-1]=Au
        bbias=np.r_[bu,np.zeros(8)]
        for end in range(2):
            for i in range(4):
                start=end*N+i*K
                Aubias[40+4*end+i,start:start+K]=-rays[:,2]
                Aubias[40+4*end+i,-1]=1
        cbias=np.zeros(2*N+2);cbias[-1]=-1
        biasbounds=bounds+[(preload,None)]
        ob=linprog(cbias,A_ub=Aubias,b_ub=bbias,A_eq=Aeb,b_eq=be,bounds=biasbounds,method='highs')
        if not ob.success:raise RuntimeError('High-bias allocation failed')
        best_bias=float(ob.x[-1]);biasbounds[-1]=(max(preload,best_bias-1e-7),None)
        pb=linprog(np.r_[np.ones(2*N),0.,0.],A_ub=Aubias,b_ub=bbias,A_eq=Aeb,b_eq=be,bounds=biasbounds,method='highs')
        if not pb.success:raise RuntimeError('High-bias secondary allocation failed')
        f0=np.einsum('ik,ikj->ij',pb.x[:N].reshape(4,K),signed)
        f1=np.einsum('ik,ikj->ij',pb.x[N:2*N].reshape(4,K),signed);df=f1-f0
        ff=f0[None,:,:]+blend[:,None,None]*df[None,:,:];norms=np.linalg.norm(ff,axis=2)
        assert np.max(norms-limits)<1e-7 and np.min(ff[:,:,2]*signs)>=best_bias-2e-7
        assert np.max(abs(np.einsum('ijk,nik->nj',B,ff)-target))<1e-7
        rate=(np.pi/(2*.1)*np.sin(np.pi*r))[:,None,None]*df
        angular=np.linalg.norm(np.cross(ff,rate),axis=2)/norms**2
        powers=[float(np.sum(np.linalg.norm(f,axis=1)**1.5/math.sqrt(2*1.225*area))) for f in [f0,f1]]
        high_bias.append(dict(start=a,end=b,duration_s=.1,optimized_minimum_signed_axial_force_N=best_bias,start_force_vectors_N=f0.tolist(),end_force_vectors_N=f1.tolist(),max_useful_force_vector_slew_N_s_per_fan=np.max(np.linalg.norm(rate,axis=2),axis=0).tolist(),max_effective_force_direction_rate_deg_s_per_fan=np.degrees(np.max(angular,axis=0)).tolist(),endpoint_isolated_free_rotor_power_references_W=powers,scope='Higher counteracting bias under the same force capacity and component-change optimum; no direct optimization or guarantee of mechanical angular speed or electric power.'))
        saved[a+'_to_'+b+'_high_bias_forces_N']=ff[::10]
    result=dict(model='Static convex reference-power endpoint allocations plus ray-LP slew comparisons and raised-cosine feasible ramps; no motor, pitch, servo, flow or body dynamics is simulated.',source=args.case+'.npz',selected_endpoint_preload_signed_vertical_N=preload,full_domain_certificate_preload_N=1,endpoints=endpoint_json,ramps=rows,slew_balanced_100ms=slew_balanced,high_bias_100ms=high_bias,notes=['These allocations and rates are feasible examples, not globally necessary or minimum rates.','A preload above 1 N is only checked at the selected endpoints and ramps, not recertified over the full wrench domain.','Acceleration reversal is not instantaneous velocity reversal.','Effective force direction rate is not mechanical vane angular speed.','One sign pattern is held throughout; only the optional mixed-sign mode requires a transition from all-positive operation.','Reference open-rotor powers are not installed electrical powers or universal shrouded-fan lower bounds.','Preload is a prescribed ideal useful-force margin, not a demonstrated rotor operating point.'])
    (OUT/(prefix+'TRANSITORIOS_IDEALES'+suffix+'.json')).write_text(json.dumps(result,indent=2))
    np.savez_compressed(OUT/(prefix+'TRANSITORIOS_100ms'+suffix+'.npz'),time_s=np.linspace(0,.1,1001),**saved)
    print(json.dumps(dict(ramps=len(rows),endpoint_cases=len(endpoints),max_100ms_effective_rate_deg_s=max(max(x['max_effective_force_direction_rate_deg_s_per_fan']) for x in rows if x['duration_s']==.1),max_100ms_force_vector_slew_N_s=max(max(x['max_useful_force_vector_slew_N_s_per_fan']) for x in rows if x['duration_s']==.1))))

if __name__=='__main__':main()
