"""Independent relocation checks using the actual neutral mechanism STEP."""
from pathlib import Path
import json,math,hashlib
import numpy as np
import cadquery as cq
from scipy.optimize import linprog
from scipy.spatial import ConvexHull

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'empaquetado_axial_A'
result=json.loads((OUT/'RESUMEN.json').read_text())
src=ROOT/'vectorizacion_A/CAD_doble_flujo/neutro.step'
parts=[(s.moved(loc),name.split('/')[-1],color) for s,name,loc,color in cq.Assembly.load(str(src))]
template=[]
for s,n,c in parts:
    if n.startswith(('alabe_0_','eje_0_')):template.append((s,n,c))
    elif n.startswith(('base_motor_','base_rotor_representativo_')) and math.hypot(s.Center().x+280,s.Center().y+65)<1e-5:template.append((s,n,c))
assert len(template)==26
outer=cq.importers.importStep(str(ROOT/'aerodinamica_A/envolvente_cerrada_referencia.step')).val()
if isinstance(outer,cq.Compound):outer=outer.Solids()[0]
checks=[];geometry=[];torques=[];W=5*9.80665;T=21.
for chosen in result['selected_finite_search_candidates']:
    positions=np.array(chosen['positions_m']);b=chosen['half_pitch_mm'];D=chosen['axial_diameter_with_2mm_radial_margin_mm']
    tube=cq.Solid.makeCylinder(D/2,800,cq.Vector(-400,0,0),cq.Vector(1,0,0))
    assert tube.cut(outer).Volume(tol=1e-8)<1e-5
    maxoutside=0.;maxoverlap=0.;assembly=cq.Assembly(name=f'reserva_axial_b{int(b)}')
    hull=outer
    for j,p in enumerate(positions):
        x,y=1000*p[0],1000*p[1]
        cutter=cq.Solid.makeCylinder(42,500,cq.Vector(x,y,-250));hull=hull.cut(cutter)
        duct=cq.Solid.makeCylinder(44,500,cq.Vector(x,y,-250)).cut(cutter).intersect(outer)
        maxoverlap=max(maxoverlap,tube.intersect(duct).Volume(tol=1e-8))
        assembly.add(duct,name=f'camisa_reserva_{j}',color=cq.Color(.25,.28,.3))
        for shape,name,col in template:
            s=shape.translate((x+280,y+65,0))
            if name.startswith('alabe_'):
                bb=s.BoundingBox();axis_x='_X_' in name
                half=math.hypot(bb.zlen/2,(bb.ylen if axis_x else bb.xlen)/2)
                dims=[bb.xlen,2*half,2*half] if axis_x else [2*half,bb.ylen,2*half]
                swept=cq.Workplane('XY').box(*dims).translate(s.Center().toTuple()).val()
                maxoutside=max(maxoutside,swept.cut(outer).Volume(tol=1e-8))
                maxoverlap=max(maxoverlap,swept.intersect(tube).Volume(tol=1e-8))
            for angle in ([-45,0,45] if name.startswith('alabe_') else [0]):
                test=s
                if angle:
                    center=s.Center();axis=cq.Vector(1,0,0) if '_X_' in name else cq.Vector(0,1,0)
                    test=s.rotate(center,center+axis,angle)
                maxoutside=max(maxoutside,test.cut(outer).Volume(tol=1e-8));maxoverlap=max(maxoverlap,test.intersect(tube).Volume(tol=1e-8))
            assembly.add(s,name=f'canal_{j}_{name}',color=col or cq.Color(.2,.3,.35))
    assert maxoutside<1e-5 and maxoverlap<1e-5
    assembly.add(hull.cut(tube),name='envolvente_de_reserva_no_pared',color=cq.Color(.12,.15,.18))
    assembly.add(tube,name='volumen_reservado_axial_no_motor',color=cq.Color(.7,.3,.1))
    path=OUT/f'reserva_axial_{int(D)}mm.step';assembly.save(str(path))
    shapes=[s.moved(loc) for s,_,loc,_ in cq.Assembly.load(str(path))];assert len(shapes)==110 and all(s.isValid() for s in shapes)
    d=np.load(OUT/'control'/(chosen['refined_control_case']+'.npz'));meta=json.loads((OUT/'control'/(chosen['refined_control_case']+'.json')).read_text());f=d['force_vectors_N'];w=d['targets_N_Nm']
    np.testing.assert_allclose(d['positions_m'],positions,atol=1e-12)
    x=positions[:,0];y=positions[:,1]
    moments=np.column_stack([(y*f[:,:,2]+.021*f[:,:,1]).sum(1),(-.039*f[:,:,0]-x*f[:,:,2]).sum(1),(x*f[:,:,1]-y*f[:,:,0]).sum(1)])
    residual=float(np.max(abs(np.c_[f.sum(1),moments]-w)));assert residual<1e-7
    assert np.max(np.linalg.norm(f,axis=2)-meta['positive_force_capacity_sufficient_N'])<1e-7
    assert np.min(f[:,:,2])>=1-1e-7 and np.max(np.linalg.norm(f[:,:,:2],axis=2)-f[:,:,2])<1e-7
    v=d['force_polytope_unit_vertices'];h=ConvexHull(v);assert np.min(-h.equations[:,3]/np.linalg.norm(h.equations[:,:3],axis=1))>=1-1e-8
    row=dict(half_pitch_mm=b,axial_reserved_outer_diameter_mm=D,fore_mm=chosen['fore'],aft_mm=chosen['aft'],maximum_outside_envelope_mm3=maxoutside,maximum_axial_reserve_intersection_mm3=maxoverlap,valid_reimported_parts=len(shapes),ideal_wrench_residual_N_or_Nm=residual,control_vertices=len(w),source_control_sha256=hashlib.sha256((OUT/'control'/(chosen['refined_control_case']+'.npz')).read_bytes()).hexdigest());checks.append(row)
    geometry.append(dict(**chosen,step=path.name))
    # Fixed installed ideal capacity: compare authority rather than only the
    # minimum-capacity certificate. Lateral total force is zero in these tests.
    torque={}
    for label,coefficient,other in [('pitch',-x,y),('roll',y,x)]:
        Aeq=np.vstack([np.ones(4),other]);beq=np.array([W,0.])
        vals=[]
        for sign in [1,-1]:
            sol=linprog(sign*coefficient,A_eq=Aeq,b_eq=beq,bounds=[(1,T)]*4,method='highs');assert sol.success;vals.append(float(coefficient@sol.x))
        torque[label+'_range_Nm']=[min(vals),max(vals)]
    limits=[]
    for sign in [1,-1]:
        sol=linprog(sign*x,A_eq=np.vstack([np.ones(4),y]),b_eq=[W,0],bounds=[(1,T)]*4,method='highs');assert sol.success;limits.append(float(x@sol.x/W))
    torque['CG_x_interval_with_plusminus_0p5Nm_pitch_reserve_m']=[min(limits)+.5/W,max(limits)-.5/W]
    torques.append(dict(half_pitch_mm=b,capacity_per_fan_N=T,mass_assumed_kg=5,**torque))
audit=dict(source_mechanism_step_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),checks=checks,authority_at_equal_capacity=torques,full_range_boxes_rechecked_in_all_four_channels=True,geometry_and_ideal_model_checks_passed=True,flight_installation_validated=False,scope='Real STEP mechanisms translated to selected finite-search positions; actual vanes checked at -45/0/+45 and conservative whole-range boxes reconstructed from their STEP dimensions in all four channels. Reserve tube is not an engine, a designed duct or a complete flow route.')
(OUT/'VERIFICACION.json').write_text(json.dumps(audit,indent=2))
lines=['# A: redistribución para una reserva axial','',
'Se estudia la carrocería elegida, sin declarar una nueva selección del usuario ni un óptimo global. La ruta recta original tiene poco espacio entre camisas. Esta búsqueda comprueba si desplazar las estaciones puede abrirla conservando alojamiento y control ideal.','',
'Se probaron semiseparaciones laterales de 65, 76, 86 y 96 mm y estaciones longitudinales cada 25 mm entre −350/−100 y +100/+350 mm. Los 12 prismas de barrido por canal cubren el intervalo mecánico ±45°, junto con ejes, disco giratorio y motor representativo. Los casos que pasan el filtro de puntos se verifican mediante diferencia de volúmenes en CAD. No incluyen servos, rodamientos o soportes futuros.','',
'Se prefiltraron pares de estaciones por separación longitudinal y desequilibrio geométrico, y se calculó su control. Por eso el mejor resultado del conjunto retenido no es el mejor posible entre todos los pares, ni entre todas las formas. Ninguna posición con semiseparación 96 mm pasó el criterio conservador en esta malla; no prueba imposibilidad fuera de ella.','',
'Hipótesis de control: 5 kg, CG=(0,0,0), cuatro fuerzas ascendentes dentro de conos efectivos de 45°, aceleraciones dentro de esfera de radio 0,5 g con cuerpo horizontal, reserva por componente de momento ±0,5 N·m y precarga vertical 1 N. Las palancas laterales se aproximan por los centros de las filas inferiores (z_x=−39 mm, z_y=−21 mm). No son centros de presión medidos.','',
'| Semiseparación lateral | Estaciones x | Reserva axial exterior con 2 mm de separación radial | Capacidad útil suficiente por fan, modelo refinado |','|---:|---|---:|---:|']
for a in geometry:lines.append(f"| {a['half_pitch_mm']:.0f} mm | {a['fore']} / +{a['aft']} mm | {a['axial_diameter_with_2mm_radial_margin_mm']:.0f} mm | {a['capacity_sufficient_refined_N']:.2f} N |")
lines+=['',
'Cada caso refinado comprueba los 1536 vértices de un dominio exterior de fuerzas × caja de momentos. Por convexidad y signos fijos la cobertura es continua en el modelo ideal. Se releyeron sus arrays y se recalculó el equilibrio con ecuaciones explícitas. Faltan el mapa de empuje/potencia/par instalado y la respuesta dinámica.','',
'## El espacio ganado cambia la maniobrabilidad','',
'Con la misma capacidad útil ideal de 21 N por ventilador y precarga de 1 N, se calcularon límites de momento puro en estacionario mediante LP, manteniendo nula la fuerza lateral y el otro momento. Esta comparación usa la misma capacidad instalada hipotética, no capacidades distintas por diseño. La aceleración angular exige una inercia real que todavía no se conoce.','',
'| Semiseparación | Momento puro de cabeceo | Momento puro de alabeo | Intervalo CG x con reserva de cabeceo ±0,5 N·m |','|---:|---|---|---|']
for a in torques:lines.append(f"| {a['half_pitch_mm']:.0f} mm | {a['pitch_range_Nm'][0]:.2f} a {a['pitch_range_Nm'][1]:.2f} N·m | {a['roll_range_Nm'][0]:.2f} a {a['roll_range_Nm'][1]:.2f} N·m | {a['CG_x_interval_with_plusminus_0p5Nm_pitch_reserve_m'][0]*1000:.0f} a {a['CG_x_interval_with_plusminus_0p5Nm_pitch_reserve_m'][1]*1000:.0f} mm |")
lines+=['',
'La reserva de 80 mm se logra con x=±100 mm, y=±86 mm en este conjunto. El cabeceo pierde brazo frente a estaciones más separadas, mientras el alabeo gana separación lateral. Una pequeña mejora de la capacidad mínima de fuerza no permite declarar mejor agilidad: falta masa, CG, tensor de inercia y respuesta.','',
'Los tres STEP contienen 110 piezas válidas reimportadas y se denominan **reservas de empaquetado**. El cilindro central es un volumen exterior reservado entre x=−400 y +400 mm; no es un motor, conducto aerodinámico o toma nariz–cola. Se comprobó su contención y ausencia de intersección con camisas y mecanismos en las posiciones revisadas. La carcasa sigue siendo una representación volumétrica, sin pared/material cerrados.','',
'Las estaciones nuevas necesitan entradas, salidas, tapas, cierres, soportes y transmisión propios. No se han resuelto flujo, distorsión, sellado, refrigeración ni arrastre compresible. La masa del propulsor rápido puede desplazar el CG fuera del intervalo disponible; debe cerrarse con el resto de los componentes antes de adoptar esta distribución.','',
'Archivos: `RESUMEN.json` conserva la búsqueda y sus límites; `POSES.json` los ensayos de alojamiento; `VERIFICACION.json` las intersecciones, el puente STEP/control y los límites de momento; `control/` los casos LP. Código: `buscar_estaciones_axiales_A.py`, `verificar_candidato_axial_A.py` y el asignador parametrizado de fuerzas. El objetivo global sigue abierto.']
(OUT/'INFORME.md').write_text('\n'.join(lines)+'\n');print(json.dumps(audit))
