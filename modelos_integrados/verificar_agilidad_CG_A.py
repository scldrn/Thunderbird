"""Reconstruct three sampled ideal trajectories and check Newton-Euler balances."""
from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import linprog
from reversibilidad_6dof_A import cone_rays,wrench_matrix
ROOT=Path(__file__).resolve().parent;BASE=ROOT/'empaquetado_axial_A';OUT=BASE/'masa_y_agilidad'
data=json.loads((OUT/'ESCENARIOS.json').read_text());layouts=json.loads((BASE/'RESUMEN.json').read_text())['selected_finite_search_candidates']
audits=[]
for layout in layouts:
    candidates=[a for a in data['scenarios'] if a['half_pitch_mm']==layout['half_pitch_mm'] and a['sampled_feasible']]
    best=min(candidates,key=lambda a:a['quintic_30deg_minimum_sampled_duration_s'])
    refined=best['refinement_241_nodes'];assert refined['sampled_feasible']
    duration=refined['quintic_30deg_minimum_sampled_duration_s']*1.01
    cg=np.array(best['CG_m']);I=np.array(best['inertia_kgm2']);p=np.array(layout['positions_m'])-cg
    rays=cone_rays(45);K=len(rays);B=np.array([wrench_matrix(x,-.039-cg[2],-.021-cg[2]) for x in p]);A=np.hstack([b@rays.T for b in B]);scales=np.r_[np.ones(3)*50,np.ones(3)*.5]
    Aub=np.zeros((8,4*K));bu=np.r_[np.ones(4)*21,-np.ones(4)]
    for i in range(4):Aub[i,i*K:(i+1)*K]=1;Aub[i+4,i*K:(i+1)*K]=-rays[:,2]
    records=[];errors=[];angular_errors=[];maxforce=0.
    for u in np.linspace(0,1,481):
        theta=math.pi/6*(10*u**3-15*u**4+6*u**5)
        omega=np.array([0,math.pi/6*(30*u*u-60*u**3+30*u**4)/duration,0])
        acceleration=np.array([0,math.pi/6*(60*u-180*u*u+120*u**3)/duration**2,0])
        tau=I@acceleration+np.cross(omega,I@omega)
        force=5*9.80665*np.array([-math.sin(theta),0,math.cos(theta)])
        target=np.r_[force,tau]
        sol=linprog(np.ones(4*K),A_ub=Aub,b_ub=bu,A_eq=A/scales[:,None],b_eq=target/scales,bounds=(0,None),method='highs')
        if not sol.success:raise RuntimeError('Finer-grid nominal trajectory is infeasible; no valid result.')
        f=sol.x.reshape(4,K)@rays;wrench=np.einsum('ijk,ik->j',B,f)
        c,s=math.cos(theta),math.sin(theta);rotation=np.array([[c,0,s],[0,1,0],[-s,0,c]])
        linear=rotation@f.sum(0)-np.array([0,0,5*9.80665]);angular=wrench[3:]-tau
        errors.append(float(np.linalg.norm(linear)));angular_errors.append(float(np.linalg.norm(angular)))
        maxforce=max(maxforce,float(np.linalg.norm(f,axis=1).max()))
        assert maxforce<=21+1e-7 and np.min(f[:,2])>=1-1e-7
        records.append(np.r_[u*duration,theta,omega[1],acceleration[1],f.ravel()])
    assert max(errors)<1e-6 and max(angular_errors)<1e-6
    saved=np.array(records);forces=saved[:,4:].reshape(-1,4,3);dt=np.diff(saved[:,0])
    vector_rate=np.linalg.norm(np.diff(forces,axis=0),axis=2)/dt[:,None]
    norms=np.linalg.norm(forces,axis=2);cosines=np.sum(forces[:-1]*forces[1:],axis=2)/(norms[:-1]*norms[1:])
    direction_rate=np.degrees(np.arccos(np.clip(cosines,-1,1)))/dt[:,None]
    np.savez_compressed(OUT/f"trayectoria_{int(layout['axial_diameter_with_2mm_radial_margin_mm'])}mm.npz",columns=np.array(['time_s','pitch_rad','pitch_rate_rad_s','pitch_acceleration_rad_s2']+[f'F{i}_{axis}_N' for i in range(4) for axis in 'xyz']),data=saved)
    audits.append(dict(axial_reserve_outer_mm=layout['axial_diameter_with_2mm_radial_margin_mm'],time_grid_nodes=481,duration_s=duration,coarse_screen_duration_s=best['quintic_30deg_minimum_sampled_duration_s'],refined_screen_duration_s=refined['quintic_30deg_minimum_sampled_duration_s'],coarse_to_refined_relative_change=refined['quintic_30deg_minimum_sampled_duration_s']/best['quintic_30deg_minimum_sampled_duration_s']-1,maximum_force_balance_error_N=max(errors),maximum_Euler_moment_balance_error_Nm=max(angular_errors),maximum_actuator_force_N=maxforce,maximum_sampled_force_vector_rate_N_s=float(vector_rate.max()),maximum_sampled_force_direction_rate_deg_s=float(direction_rate.max()),rate_scope='Finite differences of this pointwise LP allocation; not minimum required rates, servo rates or enforced slew limits.',skin_assumed_mm=best['skin_thickness_assumed_mm'],extra_station_mass_assumed_kg=best['extra_mass_per_station_assumed_kg'],balancing_mode=best['balancing_mode']))
(OUT/'VERIFICACION_TRAYECTORIAS.json').write_text(json.dumps(dict(profiles=audits,Newton_Euler_sample_checks_passed=True,physical_response_validated=False,scope='481 nominal samples per selected scenario, full tensor Euler terms, 1% duration margin over 241-node torque-reserve screen. No continuous-time proof, flow/servo/motor dynamics or rotor gyroscopic model.'),indent=2))
lines=['# Masa, centro de gravedad y giro ideal de las candidatas A','',
'**Resultado condicionado:** abrir más espacio axial no garantiza mayor agilidad. Se añadieron distribuciones de masa explícitas y una maniobra prescrita de 30° sobre el eje de cabeceo, conservando la posición inercial. No se presenta una respuesta física validada ni un tiempo mínimo global de reorientación.','',
'## Qué masas se usan','',
'Las masas geométricas de camisas, álabes y ejes se calculan de los STEP de reserva con densidades SUPUESTAS de 1600/1600/7850 kg/m³. Se excluyen las representaciones macizas de motor y rotor: sus volúmenes no indican su masa real. La piel se sustituye por una masa superficial uniforme sobre el loft cerrado, con densidad supuesta 1600 kg/m³ y espesores de escenario 0,3 u 0,8 mm. Incluye zonas de tapas sin representar su desplazamiento al abrirse.','',
'Por estación se añaden 0,05 / 0,15 / 0,30 kg hipotéticos para equipos no diseñados. Se asigna un módulo propulsivo hipotético de 1 kg en x=+400 mm con radios de giro principales 25/60/60 mm. El equipo restante completa aritméticamente 5 kg y tiene radio de giro por eje de 60 mm. No es un motor seleccionado ni una asignación de batería, combustible o electrónica demostrada.','',
'Se compara colocar el resto en x=0 y desplazarlo para equilibrar CG x=0. El intervalo permitido de su centro, −350 a +50 mm, es una restricción de escenario: no prueba que los equipos quepan en ese lugar. Se rechazan los balances que exigen salir del intervalo. Un total de masa que suma 5 kg por definición no es cierre de masa de ingeniería.','',
'Se integran área, centroides y segundos momentos de triángulos de la piel; los sólidos usan propiedades volumétricas CAD y el teorema de ejes paralelos. El cálculo se comprobó con una caja trasladada analítica y una cáscara esférica. Se conserva el tensor completo en los datos.','',
'## Maniobra y control','',
'Se prescribe θ(u)=30°(10u³−15u⁴+6u⁵), u=t/T, entre reposos. Al girar, la fuerza corporal para mantener la posición se transforma con la actitud: F_B=Rᵀ(0,0,mg). La dinámica exige τ=Iω̇+ω×Iω, conforme a las [ecuaciones de Euler, MIT](https://ocw.mit.edu/courses/16-07-dynamics-fall-2009/resources/mit16_07f09_lec28/). No se usa el momento en posición horizontal como si fuese constante durante todo el giro.','',
'Se mantienen conos efectivos ideales de 45°, capacidad útil 21 N/fan, precarga vertical 1 N/fan y reservas simultáneas de ±0,5 N·m por eje. En cada nodo se calculan intervalos de cabeceo compatibles con las cuatro esquinas de reserva de alabeo/guiñada. Su intersección deja también la reserva de cabeceo y determina las duraciones posibles del perfil. Esta comprobación tiene 61 nodos; tres escenarios se refinan a 241 nodos.','',
'Las ecuaciones de masa rígida omiten giro interno de rotores, reacción, giroscopía, aerodinámica exterior, flexión e interacción entre conductos. Los actuadores realizan instantáneamente cualquier fuerza del modelo. Estas omisiones impiden interpretar los tiempos como velocidad de un producto real.','',
'| Reserva axial exterior | Escenarios que admiten el perfil / explorados | Intervalo de duraciones mínimas de cribado entre los admitidos |','|---:|---:|---:|']
for D in [38,60,80]:
    a=[x for x in data['scenarios'] if x['axial_reserve_outer_mm']==D];good=[x for x in a if x['sampled_feasible']]
    lines.append(f"| {D} mm | {len(good)} / {len(a)} | {min(x['quintic_30deg_minimum_sampled_duration_s'] for x in good):.3f}–{max(x['quintic_30deg_minimum_sampled_duration_s'] for x in good):.3f} s |")
lines+=['',
'Los recuentos son cobertura de escenarios elegidos, no probabilidades de éxito. Las duraciones son límites de una trayectoria y modelo concretos en malla temporal; no se han minimizado todas las trayectorias posibles ni probado factibilidad entre nodos. No se aplican a un giro de 90°, desplazamiento lateral o maniobra a 1000 km/h.','',
'Para comparar inercias con las mismas hipótesis, el caso de piel de 0,3 mm, extra de 50 g por estación y balance longitudinal da:','',
'| Reserva | Inercia de cabeceo | Centro x requerido del equipo restante |','|---:|---:|---:|']
for D in [38,60,80]:
    a=next(x for x in data['scenarios'] if x['axial_reserve_outer_mm']==D and x['skin_thickness_assumed_mm']==.3 and x['extra_mass_per_station_assumed_kg']==.05 and x['balancing_mode']=='x_CG_balanced')
    lines.append(f"| {D} mm | {a['pitch_inertia_kgm2']:.4f} kg·m² | {a['remaining_equipment_x_m']*1000:.0f} mm |")
lines+=['',
'## Comprobación de trayectorias reconstruidas','',
'Se reconstruyó una trayectoria nominal por reserva axial, usando el escenario admitido más rápido y añadiendo un 1 % a su duración refinada. Se resolvió nuevamente la asignación en 481 instantes y se verificaron fuerza en ejes inerciales y momento de Euler con el tensor completo. Se guardan fuerzas, ángulos, velocidades y aceleraciones, sin afirmar simulación de motores o seguimiento autónomo.','',
'| Reserva | Duración refinada del cribado | Duración nominal verificada | Cambio al refinar 61→241 nodos |','|---:|---:|---:|---:|']
for a in audits:lines.append(f"| {a['axial_reserve_outer_mm']:.0f} mm | {a['refined_screen_duration_s']:.4f} s | {a['duration_s']:.4f} s | {100*a['coarse_to_refined_relative_change']:.3f} % |")
lines+=['',
'El escenario más rápido de cada grupo usa piel de 0,3 mm, extra de 50 g por estación y balance longitudinal. No se declara estructuralmente admisible esa piel o disponible ese equipo: el cribado estructural anterior no valida esta carrocería. La comparación de tiempos no autoriza reducir espesores para ganar agilidad.','',
'El asignador LP de cada instante no exige continuidad entre soluciones y puede cambiar entre asignaciones equivalentes. Se registran diferencias finitas de fuerza y dirección para detectarlo; no son límites mínimos de hardware ni velocidades mecánicas de álabe. Antes de usar estas trayectorias como mandos, deben imponerse tasas, dinámica y una asignación continua. Un perfil suave del cuerpo no garantiza mandos suaves.','',
'En la reserva de 80 mm, los seis escenarios con el equipo restante centrado en x=0 incumplen el perfil o las reservas; el balance hacia delante recupera cinco de seis casos, y el restante exige situar la masa fuera de la zona supuesta. Esto cuantifica la sensibilidad al CG bajo el módulo hipotético de 1 kg en x=400 mm, sin descartar toda configuración con reserva de 80 mm.','',
'## Consecuencia de diseño','',
'La reserva de 80 mm sigue siendo una candidata de integración, pero no gana por sí sola en agilidad. Las de 38 y 60 mm conservan ventajas en este estudio. La elección debe incluir huella y mapa del propulsor, energía, masa y CG reales, estructura, velocidades de actuación y aerodinámica. No se declara ganador global ni se reduce el objetivo completo a la maniobra de 30°.','',
'Archivos: `ESCENARIOS.json`, `ESCENARIOS.csv`, `VERIFICACION_TRAYECTORIAS.json` y tres NPZ de trayectoria. Código: `agilidad_masa_CG_A.py` y `verificar_agilidad_CG_A.py`. Referencia de dinámica y control omnidireccional: [Brescianini y D’Andrea, ICRA 2016, copia oficial ETH](https://ethz.ch/content/dam/ethz/special-interest/mavt/dynamic-systems-n-control/idsc-dam/People/bdario/brescianini_dandrea_omnidirectional_aerial_vehicle.pdf); su prototipo no valida esta geometría.']
(OUT/'INFORME.md').write_text('\n'.join(lines)+'\n');print(json.dumps(audits))
