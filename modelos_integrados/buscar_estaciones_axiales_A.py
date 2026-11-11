"""Coupled finite station search: exact CAD containment plus ideal wrench LP.

This is a packaging/control comparison, not a new selected or optimized aircraft.
"""
from pathlib import Path
import itertools,json,math,hashlib
import numpy as np
import cadquery as cq
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN,TopAbs_ON
import reversibilidad_6dof_A as control

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'empaquetado_axial_A';OUT.mkdir(exist_ok=True)
control.OUT=OUT/'control';control.OUT.mkdir(exist_ok=True)
source=ROOT/'diseno_industrial_v2.py';env={'__file__':str(source)}
exec(compile(source.read_text().split('# Recessed fan ports')[0],str(source),'exec'),env)
outer=env['body'];classifier=BRepClass3d_SolidClassifier(outer.wrapped)
cad=json.loads((ROOT/'vectorizacion_A/CAD_doble_flujo/VERIFICACION.json').read_text())
half=math.hypot(8,.75);blocks=[];probes=[]
for row in cad['rows']:
    axis=row['axis'];z=row['z_mm']
    for offset in [-22.,0,22.]:
        span=2*math.sqrt(40**2-(abs(offset)+half)**2)-2
        center=np.array([0,offset,z]) if axis=='X' else np.array([offset,0,z])
        dims=[span,2*half,2*half] if axis=='X' else [2*half,span,2*half]
        box=cq.Workplane('XY').box(*dims).translate(tuple(center)).val();blocks.append(box);probes.append(box)
        direction=np.array([1,0,0]) if axis=='X' else np.array([0,1,0]);length=2*math.sqrt(43.5**2-offset**2)
        probes.append(cq.Solid.makeCylinder(1.2,length,cq.Vector(*(center-direction*length/2)),cq.Vector(*direction)))
probes+=[cq.Solid.makeCylinder(41.013,1.5,cq.Vector(0,0,7)),cq.Solid.makeCylinder(12,20,cq.Vector(0,0,-11))]
compound=cq.Compound.makeCompound(probes)
# Necessary point test is only a fast reject; every accepted pose then undergoes
# a full CAD boolean on the swept boxes, rotating disc, motor and shaft probes.
points=[v.Center().toTuple() for s in probes for v in s.Vertices()]
poses=[];fit={}
for b in [65.,76.,86.,96.]:
    for x in range(-350,351,25):
        if abs(x)<100:continue
        okay=True
        for px,py,pz in points:
            classifier.Perform(gp_Pnt(px+x,py+b,pz),1e-7)
            if classifier.State() not in [TopAbs_IN,TopAbs_ON]:okay=False;break
        outside=None
        if okay:
            outside=compound.translate((x,b,0)).cut(outer).Volume(tol=1e-8);okay=outside<1e-5
        fit[(b,x)]=okay;poses.append(dict(half_pitch_mm=b,x_mm=x,full_probe_boolean_checked=outside is not None,outside_envelope_volume_mm3=outside,conservative_packaging_pass=okay))
    print(json.dumps(dict(half_pitch_mm=b,feasible_x_mm=[x for (bb,x),yes in fit.items() if bb==b and yes])),flush=True)
(OUT/'POSES.json').write_text(json.dumps(poses,indent=2))
trials=[]
for b in [65.,76.,86.,96.]:
    fore=[x for (bb,x),yes in fit.items() if bb==b and x<0 and yes]
    aft=[x for (bb,x),yes in fit.items() if bb==b and x>0 and yes]
    # Retain the nondominated station pairs in separation and static imbalance.
    pairs=[dict(fore=a,aft=c,span=c-a,imbalance=abs(a+c)/(c-a)) for a in fore for c in aft]
    frontier=[p for p in pairs if not any(q['span']>=p['span'] and q['imbalance']<=p['imbalance'] and (q['span']>p['span'] or q['imbalance']<p['imbalance']) for q in pairs)]
    for j,pair in enumerate(frontier):
        positions=np.array([[x/1000,y/1000,.007] for x in [pair['fore'],pair['aft']] for y in [-b,b]])
        c=control.certificate(f'b{int(b)}_coarse_{j}',positions_m=positions,z=.007,lever_z_fx=-.039,lever_z_fy=-.021,upright_only=True,resolution=1)
        trials.append(dict(half_pitch_mm=b,**pair,axial_outer_diameter_limit_mm=2*(b-44),axial_diameter_with_2mm_radial_margin_mm=2*(b-46),capacity_sufficient_coarse_N=c['positive_force_capacity_sufficient_N'],control_case=c['name'],positions_m=positions.tolist()))
selected=[]
for b in [65.,76.,86.,96.]:
    available=[r for r in trials if r['half_pitch_mm']==b]
    if not available:continue
    chosen=min(available,key=lambda r:r['capacity_sufficient_coarse_N'])
    final=control.certificate(f'b{int(b)}_refined',positions_m=chosen['positions_m'],z=.007,lever_z_fx=-.039,lever_z_fy=-.021,upright_only=True,resolution=2)
    selected.append(dict(**chosen,capacity_sufficient_refined_N=final['positive_force_capacity_sufficient_N'],refined_control_case=final['name']))
baseline=control.certificate('baseline_original_stations_refined',positions_m=[[-.28,-.065,.007],[-.28,.065,.007],[.285,-.065,.007],[.285,.065,.007]],z=.007,lever_z_fx=-.039,lever_z_fy=-.021,upright_only=True,resolution=2)
result=dict(source_shape_script_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_stack_report_sha256=hashlib.sha256((ROOT/'vectorizacion_A/CAD_doble_flujo/VERIFICACION.json').read_bytes()).hexdigest(),search=dict(half_pitch_mm=[65,76,86,96],fore_aft_grid_mm=25,minimum_abs_station_x_mm=100,maximum_abs_station_x_mm=350,geometry='Same styling hull; four-bank mechanical sweeps, shafts, rotor disc and motor surrogate. Positive-y tested; negative-y requires separate final checks.'),all_station_pairs_controlled=trials,selected_finite_search_candidates=selected,baseline_same_stack_capacity_N=baseline['positive_force_capacity_sufficient_N'],scope='Finite geometry grid with a geometric Pareto prefilter, then ideal control screening. No global optimum; omitted dominated geometric pairs can have different control costs. No installed rotor, support/servo, axial mass-flow, pressure or external aerodynamic validation.',selected_by_user=False)
(OUT/'RESUMEN.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(selected=selected,baseline_capacity_N=baseline['positive_force_capacity_sufficient_N'])))
