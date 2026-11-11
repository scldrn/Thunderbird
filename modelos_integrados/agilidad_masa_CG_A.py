"""CAD-based material scenarios and sampled ideal 30-degree pitch feasibility.

No mass is measured, no propulsor is selected and no actuator dynamics is hidden
inside the result. This is a rigid-body/allocation study of declared scenarios.
"""
from pathlib import Path
import json,math,csv
import numpy as np
import cadquery as cq
from scipy.optimize import linprog
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from reversibilidad_6dof_A import cone_rays,wrench_matrix

ROOT=Path(__file__).resolve().parent;BASE=ROOT/'empaquetado_axial_A';OUT=BASE/'masa_y_agilidad';OUT.mkdir(exist_ok=True)
layout=json.loads((BASE/'RESUMEN.json').read_text())['selected_finite_search_candidates']
def shift(m,r):return m*(np.dot(r,r)*np.eye(3)-np.outer(r,r))
def solid_props(s,rho):
    p=GProp_GProps();BRepGProp.VolumeProperties_s(s.wrapped,p,1e-10,True,False)
    m=p.Mass()*rho*1e-9;c=np.array(p.CentreOfMass().Coord())/1000;mat=p.MatrixOfInertia()
    I=np.array([[mat.Value(i+1,j+1) for j in range(3)] for i in range(3)])*rho*1e-15
    return m,c,I
# Check the CAD inertia reference point independently on a translated analytic box.
test=cq.Workplane('XY').box(2,4,6).translate((10,0,0)).val();m,c,I=solid_props(test,1000)
np.testing.assert_allclose(c,[.01,0,0],atol=1e-12)
np.testing.assert_allclose(np.diag(I),m*np.array([4**2+6**2,2**2+6**2,2**2+4**2])*1e-6/12,rtol=1e-9)

def surface_props(s):
    vv,tt=s.tessellate(.3,angularTolerance=.08);v=np.array([a.toTuple() for a in vv])/1000;p=v[np.array(tt)]
    A=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)/2
    total=sum(A);first=np.einsum('i,ij->j',A,p.mean(axis=1))/total
    sums=p.sum(axis=1)
    second=np.einsum('i,ijk->jk',A,np.einsum('ni,nj->nij',sums,sums)+np.einsum('nki,nkj->nij',p,p))/(12*total)
    Q=second-np.outer(first,first)
    return float(total),first,np.trace(Q)*np.eye(3)-Q
sphere=cq.Solid.makeSphere(100,angleDegrees1=-90,angleDegrees2=90)
_,_,Is=surface_props(sphere);assert np.max(abs(np.diag(Is)/(2*.1**2/3)-1))<.002
outer=cq.importers.importStep(str(ROOT/'aerodinamica_A/envolvente_cerrada_referencia.step')).val();S,cs,Iskin=surface_props(outer)

def combine(parts):
    mass=sum(a[0] for a in parts);cg=sum(a[0]*a[1] for a in parts)/mass
    inertia=sum(a[2]+shift(a[0],a[1]-cg) for a in parts)
    return mass,cg,inertia

def trajectory(positions,cg,Iyy,n=61):
    # Exact moment intervals in the ray polytope for each temporal node and all
    # four roll/yaw reserve corners, then intersection of allowable 1/T^2.
    p=np.array(positions)-cg;rays=cone_rays(45);K=len(rays);B=np.array([wrench_matrix(a,-.039-cg[2],-.021-cg[2]) for a in p])
    A=np.hstack([b@rays.T for b in B]);keep=[0,1,2,3,5];Aeq=A[keep].copy();Aeq[3:]/=.4
    Aub=np.zeros((8,4*K));bu=np.r_[np.ones(4)*21,-np.ones(4)]
    for i in range(4):Aub[i,i*K:(i+1)*K]=1;Aub[4+i,i*K:(i+1)*K]=-rays[:,2]
    low=0.;high=float('inf');critical=None;maxres=0.
    for u in np.linspace(0,1,n):
        q=math.pi/6*(10*u**3-15*u**4+6*u**5);dd=math.pi/6*(60*u-180*u*u+120*u**3)
        force=5*9.80665*np.array([-math.sin(q),0,math.cos(q)])
        lo=-float('inf');hi=float('inf')
        for roll in [-.5,.5]:
            for yaw in [-.5,.5]:
                target=np.r_[force,roll/.4,yaw/.4]
                for sign in [1,-1]:
                    sol=linprog(sign*A[4],A_ub=Aub,b_ub=bu,A_eq=Aeq,b_eq=target,bounds=(0,None),method='highs')
                    if not sol.success:return dict(sampled_feasible=False,reason='A required roll/yaw reserve corner is infeasible even before prescribing pitch acceleration.',failed_normalized_time=float(u),nodes=n)
                    maxres=max(maxres,float(max(abs(Aeq@sol.x-target))))
                    value=float(A[4]@sol.x)
                    if sign==1:lo=max(lo,value)
                    else:hi=min(hi,value)
        lo+=.5;hi-=.5 # leave independent +/-0.5 Nm pitch correction as well
        if hi<lo:return dict(sampled_feasible=False,reason='Pitch reserve interval empty.',failed_normalized_time=float(u),nodes=n)
        c=Iyy*dd
        if abs(c)<1e-10:
            if lo>1e-7 or hi<-1e-7:return dict(sampled_feasible=False,reason='Rest/inflection node cannot support the prescribed attitude and moment reserves.',failed_normalized_time=float(u),nodes=n)
        else:
            a,b=sorted([lo/c,hi/c]);low=max(low,a)
            if b<high:high=b;critical=float(u)
    if high<=0 or low>high:return dict(sampled_feasible=False,reason='No common positive duration satisfies all sampled nodes.',nodes=n)
    return dict(sampled_feasible=True,quintic_30deg_minimum_sampled_duration_s=1/math.sqrt(high),maximum_sampled_duration_s=None if low<=0 else 1/math.sqrt(low),critical_normalized_time=critical,nodes=n,max_LP_residual=maxres,scope='Prescribed 0-to-30-degree pitch, fixed inertial position, instantaneous ideal forces, ray-cone approximation, sampled time. Not a globally time-optimal maneuver or hardware response.')

allrows=[];details=[];geom=[]
for row in layout:
    material=[]
    for s,name,loc,_ in cq.Assembly.load(str(BASE/('reserva_axial_'+str(int(row['axial_diameter_with_2mm_radial_margin_mm']))+'mm.step'))):
        label=name.split('/')[-1]
        rho=1600 if label.startswith('camisa_reserva_') or '_alabe_' in label else 7850 if '_eje_' in label else None
        if rho:material.append(solid_props(s.moved(loc),rho))
    gm,gc,gI=combine(material);geom.append(dict(half_pitch_mm=row['half_pitch_mm'],material_mass_scenario_kg=gm,material_CG_m=gc.tolist(),material_inertia_kgm2=gI.tolist()))
    for skin_mm in [.3,.8]:
        ms=S*skin_mm/1000*1600
        for extra in [.05,.15,.30]:
            for balanced in [False,True]:
                common=material+[(ms,cs,ms*Iskin)]
                for p in row['positions_m']:common.append((extra,np.array(p),np.zeros((3,3))))
                common.append((1.,np.array([.4,0,0]),np.diag(np.array([.025,.06,.06])**2)))
                rest=5-sum(a[0] for a in common)
                if rest<=0:raise RuntimeError('Scenario exceeds 5 kg before remaining equipment.')
                xrest=-sum(a[0]*a[1][0] for a in common)/rest if balanced else 0.
                zone_ok=-.35<=xrest<=.05
                common.append((rest,np.array([xrest,0,0]),np.eye(3)*rest*.06**2))
                mass,cg,I=combine(common);assert abs(mass-5)<1e-10 and max(abs(I[[0,2],1]))<1e-7
                res=trajectory(row['positions_m'],cg,I[1,1]) if zone_ok else dict(sampled_feasible=False,reason='Balancing requires the residual mass center outside the assumed x zone.',nodes=0)
                record=dict(half_pitch_mm=row['half_pitch_mm'],axial_reserve_outer_mm=row['axial_diameter_with_2mm_radial_margin_mm'],skin_thickness_assumed_mm=skin_mm,extra_mass_per_station_assumed_kg=extra,remaining_equipment_mass_kg=rest,balancing_mode='x_CG_balanced' if balanced else 'remaining_equipment_at_x0',remaining_equipment_x_m=xrest,remaining_zone_m=[-.35,.05],CG_m=cg.tolist(),inertia_kgm2=I.tolist(),pitch_inertia_kgm2=float(I[1,1]),**res)
                details.append(record)
                print(json.dumps({k:record[k] for k in ['axial_reserve_outer_mm','skin_thickness_assumed_mm','extra_mass_per_station_assumed_kg','balancing_mode','sampled_feasible']}),flush=True)
    # Refine the fastest feasible illustrative scenario, keeping its exact mass model.
    feasible=[a for a in details if a['half_pitch_mm']==row['half_pitch_mm'] and a['sampled_feasible']]
    if feasible:
        best=min(feasible,key=lambda a:a['quintic_30deg_minimum_sampled_duration_s']);refined=trajectory(row['positions_m'],np.array(best['CG_m']),best['pitch_inertia_kgm2'],n=241)
        best['refinement_241_nodes']=refined

result=dict(skin_reference=dict(area_m2=S,area_centroid_m=cs.tolist(),inertia_per_unit_surface_mass_m2=Iskin.tolist(),warning='Equivalent uniform closed-hull skin including door zones; not an actual open-hover skin/door assembly.'),station_material_scenarios=geom,assumptions=dict(total_mass_kg=5,material_densities_duct_vane_shaft_kgm3=[1600,1600,7850],fast_propulsor_assumed_mass_kg=1,fast_propulsor_assumed_x_m=.4,fast_propulsor_assumed_axis_radii_of_gyration_m=[.025,.06,.06],remaining_equipment_assumed_axis_radius_of_gyration_m=.06,per_fan_useful_capacity_N=21,per_fan_vertical_preload_N=1,moment_reserves_per_axis_Nm=.5,not_included=['Real motor/rotor mass or spinning inertia','Motor/servo/flow lag','Exterior aerodynamics and rotor interaction','Reaction torque and gyroscopic loads','Geometric containment of generic remaining equipment and fast propulsor','Structural flexibility and aeroelasticity']),scenarios=details,actual_mass_closure_or_flight_validated=False)
(OUT/'ESCENARIOS.json').write_text(json.dumps(result,indent=2))
flat=[]
for a in details:flat.append({k:a.get(k) for k in ['axial_reserve_outer_mm','skin_thickness_assumed_mm','extra_mass_per_station_assumed_kg','balancing_mode','remaining_equipment_x_m','pitch_inertia_kgm2','sampled_feasible','reason','quintic_30deg_minimum_sampled_duration_s']})
with (OUT/'ESCENARIOS.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=flat[0].keys());w.writeheader();w.writerows(flat)
print(json.dumps(dict(scenarios=len(details),sampled_feasible=sum(a['sampled_feasible'] for a in details))))
