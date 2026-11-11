"""Recheck existing time-coupled force profiles against narrower useful cones.

No new optimum or actuator model: identical forces imply identical ideal rigid
body motion. Convexity proves continuous PWL cone inclusion from endpoints.
"""
from pathlib import Path
import json,math,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'empaquetado_axial_A';SOURCE=BASE/'masa_y_agilidad/tasas'
OUT=SOURCE/'sensibilidad_cono';OUT.mkdir(exist_ok=True)
source=json.loads((SOURCE/'RESULTADOS.json').read_text())
forward=json.loads((SOURCE/'VERIFICACION.json').read_text())
layouts=json.loads((BASE/'RESUMEN.json').read_text())['selected_finite_search_candidates']
checks=[]
for record in source['selected_finite_grid']:
 path=SOURCE/record['trajectory_file'];d=np.load(path)
 t=d['time_s'];f=d['force_vectors_N'];cg=d['CG_m'];I=d['inertia_kgm2'];T=float(t[-1]);u=t/T
 assert np.all(np.diff(t)>0)
 layout=next(x for x in layouts if x['axial_diameter_with_2mm_radial_margin_mm']==record['axial_reserve_outer_mm'])
 p=np.asarray(layout['positions_m'])-cg
 fx,fy,fz=(f[:,:,j] for j in range(3));zx=-.039-cg[2];zy=-.021-cg[2]
 actual=np.column_stack([fx.sum(1),fy.sum(1),fz.sum(1),(p[:,1]*fz-zy*fy).sum(1),(zx*fx-p[:,0]*fz).sum(1),(p[:,0]*fy-p[:,1]*fx).sum(1)])
 pitch=math.pi/6*(10*u**3-15*u**4+6*u**5)
 omega=np.column_stack([np.zeros(len(t)),math.pi/6*(30*u**2-60*u**3+30*u**4)/T,np.zeros(len(t))])
 angular_acc=np.column_stack([np.zeros(len(t)),math.pi/6*(60*u-180*u**2+120*u**3)/T**2,np.zeros(len(t))])
 expected=np.column_stack([-5*9.80665*np.sin(pitch),np.zeros(len(t)),5*9.80665*np.cos(pitch),angular_acc@I.T+np.cross(omega,omega@I.T)])
 error=float(abs(actual-expected).max());assert error<2e-6
 rate=float(np.linalg.norm(np.diff(f,axis=0)/np.diff(t)[:,None,None],axis=2).max())
 assert rate<=record['force_vector_slew_limit_N_s']+1e-6
 maxforce=float(np.linalg.norm(f,axis=2).max());assert maxforce<=21+1e-7
 assert fz.min()>=1-1e-7
 radial=np.hypot(fx,fy);angle=np.degrees(np.arctan2(radial,fz))
 cone_results=[]
 for delta in (30.,33.,33.75,35.,40.,45.):
  margin=fz*math.sin(math.radians(delta))-radial*math.cos(math.radians(delta))
  cone_results.append(dict(cone_deg=delta,saved_profile_inside_continuously=bool(margin.min()>=-1e-8),minimum_distance_to_cone_side_N=float(margin.min())))
 assert all(x['saved_profile_inside_continuously'] for x in cone_results if x['cone_deg']>=35)
 prior=next(x for x in forward['profiles'] if x['trajectory_file']==record['trajectory_file'])
 checks.append(dict(axial_reserve_outer_mm=record['axial_reserve_outer_mm'],duration_s=T,force_vector_slew_limit_N_s=record['force_vector_slew_limit_N_s'],source_file=str(path),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),max_direct_nodal_wrench_error=error,maximum_force_N=maxforce,maximum_vector_slew_N_s=rate,maximum_force_angle_deg=float(angle.max()),cone_checks=cone_results,
 retained_forward_position_drift_m=prior['maximum_forward_position_drift_m'],retained_forward_attitude_error_deg=prior['maximum_forward_attitude_error_deg'],
 interpretation='Same force function as independently integrated source; no recomputation of a different physical plant.'))
summary=dict(profiles_checked=len(checks),profiles=checks,mass_assumed_kg=5,
 continuous_inclusion_method='PWL interpolation of endpoint forces in a convex circular cone; cone-side distance is concave, so minimum on each segment is at an endpoint.',
 rates_remain_identical=True,ideal_rigid_body_trajectory_unchanged=True,minimum_duration_proven=False,physical_actuator_response_validated=False,
 source_results_sha256=hashlib.sha256((SOURCE/'RESULTADOS.json').read_bytes()).hexdigest(),source_forward_verification_sha256=hashlib.sha256((SOURCE/'VERIFICACION.json').read_bytes()).hexdigest())
(OUT/'VERIFICACION.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
lines=['# Conos efectivos más estrechos en las trayectorias con tasas limitadas','','Se revisaron las nueve trayectorias guardadas de 30° de cabeceo, de 5 kg supuestos, para las tres distribuciones candidatas con reservas axiales de 38/60/80 mm. No se ha elegido una distribución nueva del producto. Se conservan exactamente las fuerzas calculadas y los escenarios de masa/CG/inercia anteriores.','','## Resultado','','Todas las trayectorias usan como máximo 33,75° de inclinación efectiva de fuerza por ventilador, aunque el LP original permitía 45°. Por tanto, esas mismas fuerzas también satisfacen un cono de 35° y uno de 40°, en todos los instantes de la interpolación lineal. No fue necesario repetir los LP ni recalcular una trayectoria distinta. Se verificaron de nuevo fuerzas, precarga, tasas vectoriales y balance nodal directo de Newton–Euler.','','La inclusión continua se sigue de la convexidad del cono circular: una combinación lineal entre dos fuerzas admisibles permanece dentro. La distancia a la superficie lateral se expresa Fz·sin(δ) − norma(Fxy)·cos(δ); es cóncava a lo largo de cada segmento, por lo que su mínimo ocurre en un extremo. Los valores negativos significan que la asignación guardada sale del cono, no que sea imposible encontrar otra asignación.','','| Reserva axial | Parámetro de tasa | Duración de la trayectoria guardada | Ángulo máximo útil | Margen mínimo a la superficie del cono de 35° |','|---:|---:|---:|---:|---:|']
for r in checks:
 margin=next(x['minimum_distance_to_cone_side_N'] for x in r['cone_checks'] if x['cone_deg']==35)
 lines.append(f"| {r['axial_reserve_outer_mm']:.0f} mm | {r['force_vector_slew_limit_N_s']:.0f} N/s | {r['duration_s']:.3f} s | {r['maximum_force_angle_deg']:.2f}° | {margin:.4f} N |")
lines += ['','## Interpretación y límites','','La trayectoria ideal del cuerpo rígido es la misma porque no cambia la función de fuerza aplicada. Los errores numéricos de interpolación y propagación ya cuantificados en el estudio anterior se conservan; no se convierten en precisión de vuelo. No se demuestra un tiempo mínimo global ni la respuesta real de un propulsor. Las tasas de 20/50/100 N/s son parámetros supuestos, no especificaciones de motores.','','El margen angular entre 33,75° y 35° es solo 1,25°. La tabla expresa distancia en espacio de fuerzas a la superficie lateral; no es tolerancia mecánica de un álabe, margen de estabilidad o robustez ante perturbaciones. Tampoco cubre simultáneamente incertidumbres de magnitud, precarga, tasa, pares libres o posición del centro de presión. Puede haber otras restricciones activas sin margen.','','El ángulo útil de fuerza no equivale al ángulo de álabe. Los resultados requieren un mapa instalado de fuerza/momento/potencia y su dinámica. El canal CFD anterior tiene otra disposición de bancos y no calibra estas palancas de las candidatas. Los ensayos de cono siguen siendo modelos ideales.','','El estudio estático de conos para 2/5/10 kg no permite trasladar estos tiempos de giro de 5 kg a las otras masas. El objetivo de máxima agilidad y 600–1000 km/h permanece abierto; 0,5 g y el giro de 30° son escenarios de investigación.','','Archivos: `VERIFICACION.json` conserva comprobaciones y hashes de todas las trayectorias originales. Código: `auditar_conos_trayectorias_A.py`, en modelos_integrados. No se modificaron los NPZ originales ni la simulación CFD activa.']
(OUT/'INFORME.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(profiles=len(checks),all_35deg_pass=True,max_force_angle_deg=max(x['maximum_force_angle_deg'] for x in checks),physical_actuator_response_validated=False)))
