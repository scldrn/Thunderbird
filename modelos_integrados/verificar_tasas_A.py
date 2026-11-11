"""Independent PWL-force checks and open-loop ideal rigid-body integration."""
from pathlib import Path
import json,math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parent;BASE=ROOT/'empaquetado_axial_A';OUT=BASE/'masa_y_agilidad/tasas'
source=json.loads((OUT/'RESULTADOS.json').read_text())
layouts=json.loads((BASE/'RESUMEN.json').read_text())['selected_finite_search_candidates']
g=9.80665
def forward(duration,mass,I,forcing,maxstep,rtol=1e-9):
    inverse=np.linalg.inv(I)
    def rhs(t,y):
        F,M=forcing(t);q=y[6:10];omega=y[10:13]
        a=Rotation.from_quat(q).apply(F)/mass-np.array([0,0,g])
        qdot=.5*np.r_[q[3]*omega+np.cross(q[:3],omega),-q[:3]@omega]
        return np.r_[y[3:6],a,qdot,inverse@(M-np.cross(omega,I@omega))]
    initial=np.zeros(13);initial[9]=1
    sol=solve_ivp(rhs,[0,duration],initial,method='DOP853',rtol=rtol,atol=rtol/100,max_step=maxstep,dense_output=True)
    assert sol.success
    return sol
# External analytic identities test coordinate conventions and Euler integration.
Itest=np.diag([.2,.3,.4]);Ttest=.5
fall=forward(Ttest,5,Itest,lambda t:(np.zeros(3),np.array([0,.6,0])),.01)
y=fall.y[:,-1];expected_angle=.5*.6/.3*Ttest**2
assert abs(y[2]+.5*g*Ttest**2)<1e-9 and abs(y[5]+g*Ttest)<1e-9
angle_error=(Rotation.from_rotvec([0,expected_angle,0]).inv()*Rotation.from_quat(y[6:10])).magnitude()
assert angle_error<1e-9 and abs(y[11]-.6/.3*Ttest)<1e-9
hover=forward(1,5,Itest,lambda t:(np.array([0,0,5*g]),np.zeros(3)),.02)
assert np.linalg.norm(hover.y[:6,-1])<1e-10
audits=[]
for record in source['selected_finite_grid']:
    d=np.load(OUT/record['trajectory_file']);t=d['time_s'];f=d['force_vectors_N'];cg=d['CG_m'];I=d['inertia_kgm2'];duration=t[-1]
    layout=next(a for a in layouts if a['axial_diameter_with_2mm_radial_margin_mm']==record['axial_reserve_outer_mm']);p=np.array(layout['positions_m'])-cg
    # Explicit moments, independent of the LP generator's matrix helper.
    def wrench(F):
        return F.sum(axis=0),np.array([np.sum(p[:,1]*F[:,2]-(-.021-cg[2])*F[:,1]),np.sum((-.039-cg[2])*F[:,0]-p[:,0]*F[:,2]),np.sum(p[:,0]*F[:,1]-p[:,1]*F[:,0])])
    rates=np.diff(f,axis=0)/np.diff(t)[:,None,None]
    maximum=float(np.linalg.norm(rates,axis=2).max());assert maximum<=record['force_vector_slew_limit_N_s']+1e-6
    assert np.max(np.linalg.norm(f,axis=2))<=21+1e-7 and f[:,:,2].min()>=1-1e-7
    assert np.max(np.linalg.norm(f[:,:,:2],axis=2)-f[:,:,2])<1e-7
    # Exact maximum direction rate along each straight force-vector segment.
    dt=np.diff(t)[:,None];v=f[:-1];speed2=(rates*rates).sum(axis=2)
    closest=np.clip(-np.sum(v*rates,axis=2)/np.maximum(speed2,1e-30),0,dt)
    minimum=np.sum((v+closest[:,:,None]*rates)**2,axis=2)
    angular=np.linalg.norm(np.cross(v,rates),axis=2)/minimum
    def forcing(ti):
        F=np.array([np.interp(ti,t,col) for col in f.reshape(len(t),12).T]).reshape(4,3)
        return wrench(F)
    sol=forward(duration,5,I,forcing,duration/(len(t)-1)/2)
    dense=np.linspace(0,duration,1001);states=sol.sol(dense);u=dense/duration
    angles=math.pi/6*(10*u**3-15*u**4+6*u**5)
    desired=Rotation.from_rotvec(np.column_stack([np.zeros(len(u)),angles,np.zeros(len(u))]))
    attitude=(desired.inv()*Rotation.from_quat(states[6:10].T)).magnitude()
    report=dict(**record,verified_actual_PWL_vector_rate_N_s=maximum,maximum_continuous_PWL_force_direction_rate_deg_s=float(np.degrees(angular.max())),maximum_forward_position_drift_m=float(np.linalg.norm(states[:3],axis=0).max()),final_position_drift_m=float(np.linalg.norm(states[:3,-1])),maximum_forward_attitude_error_deg=float(np.degrees(attitude.max())),final_attitude_error_deg=float(np.degrees(attitude[-1])),final_angular_speed_rad_s=float(np.linalg.norm(states[10:,-1])),quaternion_norm_max_error=float(np.max(abs(np.linalg.norm(states[6:10],axis=0)-1))),forward_solver_success=bool(sol.success),scope='Continuous ideal PWL forces, open-loop rigid-body integration. Force/cone/slew bounds hold for that interpolation; deviations from the prescribed motion are recorded. No real actuator dynamics or flight validation.')
    if not audits:
        repeat=forward(duration,5,I,forcing,duration/(len(t)-1)/4,rtol=1e-10)
        report['solver_refinement_final_position_difference_m']=float(np.linalg.norm(repeat.y[:3,-1]-sol.y[:3,-1]));assert report['solver_refinement_final_position_difference_m']<1e-5
    audits.append(report)
    np.savez_compressed(OUT/(record['trajectory_file'].replace('.npz','_forward.npz')),time_s=dense,state=states,desired_pitch_rad=angles)
(OUT/'VERIFICACION.json').write_text(json.dumps(dict(analytic_freefall_and_principal_torque_tests_passed=True,profiles=audits,continuous_ideal_force_constraints_checked=True,physical_actuator_response_validated=False),indent=2))
lines=['# Límites de cambio de fuerza y giro de las candidatas A','',
'Se añade una restricción temporal al estudio anterior de masa y CG. **No es una medición de respuesta de motor ni servo.** Se usa el escenario ilustrativo más rápido de cada candidata (piel de 0,3 mm, extra de 50 g por estación, balance longitudinal y módulo hipotético de 1 kg en x=400 mm). Esa asignación de masa sigue sin demostrar componentes disponibles o resistencia de piel.','',
'## Formulación y alcance','',
'Se conserva el giro prescrito de 0 a 30° con perfil quíntico, masa 5 kg, fuerza transformada con la actitud, tensor de inercia y límites útiles 21 N/fan, cono efectivo 45° y precarga 1 N. Las fuerzas de todos los instantes se resuelven conjuntamente mediante LP disperso. Por componente se impone |ΔF|≤S Δt/√3: es una condición conservadora que asegura ||ΔF||/Δt≤S para la interpolación lineal. No equivale a un límite calibrado de ángulo mecánico o potencia.','',
'Se exploran S=20/50/100 N/s, parámetros de estudio. Las duraciones son una malla finita de factores 1,01/1,5/2/3/5/10 respecto al cribado sin tasas. La tabla muestra el primer caso probado que pasó 41 y 81 nodos; no es el tiempo mínimo global ni una búsqueda continua de óptimo. Un fallo del LP corresponde a este modelo y aproximación, no prueba imposibilidad física de otra asignación o geometría.','',
'Los tiempos parten del cribado anterior con reservas instantáneas de momento. No se obliga a que las correcciones de perturbación respeten a la vez estos límites de tasa: no se acredita rechazo dinámico de perturbaciones ni robustez de vuelo. La aproximación de cono y la caja de tasas pueden ser conservadoras.','',
'## Resultado e integración directa','',
'La interpolación lineal mantiene continuamente los límites convexos de fuerza, precarga y cambio vectorial. Su fuerza y momento no reproducen exactamente la trayectoria no lineal entre nodos. Se integran posición, velocidad, cuaternión y velocidad angular con Newton–Euler para cuantificar ese error en la dinámica rígida ideal. El integrador pasó comprobaciones analíticas de caída libre, par constante sobre eje principal y estacionario; un caso se repitió con paso y tolerancia menores.','',
'| Reserva axial exterior | Límite vectorial S | Primera duración admitida de la malla | Deriva máxima de posición integrada | Error máximo de actitud |','|---:|---:|---:|---:|---:|']
for a in audits:lines.append(f"| {a['axial_reserve_outer_mm']:.0f} mm | {a['force_vector_slew_limit_N_s']:.0f} N/s | {a['duration_s']:.3f} s | {1000*a['maximum_forward_position_drift_m']:.3f} mm | {a['maximum_forward_attitude_error_deg']:.4f}° |")
lines+=['',
'La precisión numérica de esta integración no es precisión física del vehículo. No incluye aerodinámica exterior, interacción de chorros, reacción y giroscopía de los rotores, flexibilidad, motores, ESC, transmisión, servo o fluido transitorio. La velocidad de dirección efectiva guardada se calcula sobre el vector de fuerza interpolado; no es velocidad de servo.','',
'Las fuerzas son continuas, pero sus pendientes pueden cambiar bruscamente en los nodos. No se imponen todavía límites a la segunda derivada de fuerza o a la aceleración mecánica del álabe; un actuador físico podría exigir más suavizado o duración.','',
'El estudio confirma que un perfil factible con fuerzas instantáneas puede necesitar más duración cuando se limita su cambio. Las candidatas no se pueden ordenar solo por el paso axial o una inercia: también importan la distribución de masas y las capacidades temporales del propulsor. No se afirma todavía cuál es óptima para 600–1000 km/h o para la envolvente completa de aceleraciones.','',
'Archivos: `RESULTADOS.json` conserva casos admitidos/rechazados y la malla; `VERIFICACION.json` comprueba interpolación e integración; NPZ con fuerzas y estados. Código: `asignacion_tasas_A.py` y `verificar_tasas_A.py`. El siguiente cierre exige mapas instalados de fuerza/momento/potencia y límites de actuación antes de transferir estas demandas a un prototipo autónomo.']
(OUT/'INFORME.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(profiles=len(audits),max_forward_attitude_error_deg=max(a['maximum_forward_attitude_error_deg'] for a in audits))))
