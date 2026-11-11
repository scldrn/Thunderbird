from pathlib import Path
import numpy as np,json,csv
P=Path(__file__).resolve().parent
checks=[];sens=[]
for speed in (600,1000):
 d=np.load(P/f'{speed}kmh.npz');t=d['time'];dt=t[1]-t[0];V=speed/3.6
 vel=d['velocity'];acc=d['acceleration'];pos=d['position']
 ck=dict(speed_kmh=speed,max_speed_difference_ms=float(np.abs(np.linalg.norm(vel,axis=1)-V).max()),max_position_derivative_difference_ms=float(np.linalg.norm(np.gradient(pos,dt,axis=0)[1:-1]-vel[1:-1],axis=1).max()),max_velocity_derivative_difference_ms2=float(np.linalg.norm(np.gradient(vel,dt,axis=0)[1:-1]-acc[1:-1],axis=1).max()),max_velocity_dot_acceleration=float(np.abs(np.sum(vel*acc,axis=1)).max()))
 assert ck['max_speed_difference_ms']<1e-9 and ck['max_position_derivative_difference_ms']<.01 and ck['max_velocity_derivative_difference_ms2']<.01
 checks.append(ck)
 with (P/f'{speed}kmh.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['tiempo_s','x_m','y_m','z_m','vx_ms','vy_ms','vz_ms','ax_ms2','ay_ms2','az_ms2','fuerza_normal_requerida_N','carga_normal_requerida_g','alabeo_grados','arrastre_supuestamente_N','empuje_requerido_supuestamente_N'])
  for i in range(len(t)):w.writerow([t[i],*pos[i],*vel[i],*acc[i],d['normal_force'][i],d['load_factor'][i],d['bank_deg'][i],d['drag_assumed'][i],d['thrust_required_assumed'][i]])
 for cd0 in (.04,.06,.12):
  q=float(d['q_Pa']);N=d['normal_force'];cn=N/(q*.04977);drag=q*.04977*(cd0+.12*cn**2);thrust=drag+5*9.80665*vel[:,2]/V
  sens.append(dict(speed_kmh=speed,Cd0_assumed=cd0,max_thrust_demand_N=float(thrust.max()),max_useful_power_demand_kW=float((thrust*V).max()/1000)))
(P/'VERIFICACION.json').write_text(json.dumps(dict(checks=checks,scope='Kinematic and reconstruction checks, not physical validation'),indent=2))
(P/'SENSIBILIDAD_ARRASTRE.json').write_text(json.dumps(sens,indent=2))
(P/'INFORME.md').write_text('''# Vuelo rápido — visualización detallada y reconstrucción de demandas

## Qué se entrega
Video Full HD de 24 s: dos escenas de 12 s físicos, una a 600 km/h y otra a 1000 km/h, a velocidad de reproducción 1:1. Se utiliza una malla extraída de los STEP del proyecto, con tapas cerradas y alerones posteriores en posición neutra. La cámara sigue el marco de velocidad y además realiza una órbita de inspección; su órbita no representa guiñada del vehículo. Las rotaciones globales y el ascenso se recogen en la trayectoria y datos. El alabeo de la vista principal sigue la orientación normal de fuerza requerida relativa al marco de velocidad. No se dibujan ondas de choque, partículas de flujo, flexión o gases porque no se han calculado.

**NO es una simulación predictiva del vuelo real del A07 ni una solución CFD.** Se prescribe una trayectoria a velocidad constante y se reconstruyen las fuerzas y momentos que harían falta. Es una ampliación visual y cuantitativa respecto al anterior demostrador de baja velocidad, no su validación ni una extrapolación de sus cuatro fuerzas de 21 N hasta 1000 km/h.

## Trayectoria prescrita y cálculos
Masa supuesta 5 kg, gravedad 9,80665 m/s², densidad uniforme supuesta 1,225 kg/m³ y velocidad del sonido supuesta 340,3 m/s. La densidad se mantiene constante aunque la trayectoria cambie de altura. No se simula una atmósfera estratificada. Arranque a 150 m, ya a la velocidad objetivo: no se demuestra aceleración hasta esa velocidad.

Se prescriben pulsos suaves sin² de aceleración horizontal normal: +3 g entre 1 y 4 s, −6 g entre 4,5 y 8 s, +10 g entre 8,5 y 11,5 s. También se prescriben aceleraciones normales verticales +2 g entre 3 y 5 s, −2 g entre 6 y 8 s y +1 g entre 9 y 11 s. Esas cargas son exigencias del escenario, no prestaciones demostradas o límites estructurales. En parte del perfil se requiere alabeo superior a 90°, que tampoco está validado.

Con V constante se integran rumbo psi, ángulo de trayectoria gamma y posición mediante:
- dpsi/dt = a_horizontal / (V cos(gamma)).
- dgamma/dt = a_vertical / V.
- dp/dt = V (cos(gamma)cos(psi), cos(gamma)sin(psi), sin(gamma)).

Se reconstruye aceleración como suma de las dos componentes normales y la fuerza no gravitatoria requerida m(a+g ez). Se descompone en fuerza axial y normal respecto a la velocidad. La actitud se elige alineando X con la velocidad y Z con esa fuerza normal. No hay ángulo de ataque de equilibrio resuelto, modelo de pérdida ni modelo de estabilidad. No se deduce una deflexión funcional de las cuatro aletas: por eso permanecen neutras en la vista.

La velocidad angular se obtiene de las rotaciones sucesivas y el momento requerido de I*alpha + omega×(I*omega). I≈diag(0,03531, 0,45899, 0,47546) kg·m² es el elipsoide homogéneo hipotético del estudio anterior; no la masa distribuida real del CAD. Que se calcule un momento requerido no demuestra que las superficies, propulsor o actuadores puedan producirlo.

## Cifras cinemáticas
Con aceleración horizontal normal 10 g en vuelo horizontal, R=V²/(10g): 283,25 m a 600 km/h y 786,82 m a 1000 km/h. El radio horizontal mostrado durante el ascenso usa (V cos(gamma))²/|a_horizontal|. A misma aceleración el giro de trayectoria es más amplio a mayor velocidad; reorientar rápidamente el cuerpo no permite una esquina instantánea.

La presión dinámica calculada q=0,5 rho V² es 17,01 kPa y 47,26 kPa. El máximo de fuerza normal exigida por esta secuencia es aproximadamente 500 N en ambas escenas, es decir unas 10,2 veces el peso supuesto de 5 kg. No son resultados de túnel ni fuerzas aerodinámicas producidas por nuestro diseño.

## Arrastre y propulsión: sensibilidad exclusivamente hipotética
Se utiliza, fuera del video principal, D=q S (Cd0+k Cn²), con S=0,04977 m² como área de referencia histórica del cuerpo, Cd0=0,06 y k=0,12 SUPUESTOS, y Cn=N/(qS). No son coeficientes obtenidos del CAD/CFD, tampoco un modelo transónico identificado. No se incluyen choques, separación, interferencias, tomas, escape o trimado reales. Se exploran Cd0=0,04 y 0,12 para evidenciar dependencia del supuesto; ese intervalo no es incertidumbre estadística ni contiene garantizadamente el valor real.

La demanda axial para mantener V incluye D+m g sin(gamma). El producto T*V es potencia útil demandada bajo ese modelo, no potencia eléctrica, consumo o motor instalado. El escenario nominal da máximos aproximados de 87,7 N / 14,6 kW a 600 km/h y 154,8 N / 43,0 kW a 1000 km/h. No se selecciona un motor ni se demuestra autonomía.

## Verificación y alcance
VERIFICACION.json compara derivadas numéricas de posición y velocidad con las variables analíticas y comprueba constancia de la rapidez y ortogonalidad velocidad–aceleración. RESULTADOS.json registra la reconstrucción de fuerzas. Es verificación algebraica/cinemática local, no comprobación física ni ejecución completa de casos NASA. Se mantienen abiertos los mapas de fuerzas, presión, estabilidad, actuación, estructura y aeroelasticidad del A07.

Los solvers CFD del proyecto permanecen pausados. No se presenta una nueva convergencia aerodinámica ni se afirma terminada la investigación global.

## Fuentes primarias de fundamento
- [NASA — Turns](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/aircraft-motion-turns/): fuerzas y orientación de sustentación durante un giro. La selección del perfil de 3/6/10 g es propia y no proviene de un ensayo NASA del dispositivo.
- [NASA — NDARC Theory](https://rotorcraft.arc.nasa.gov/Publications/files/NDARCTheory_v1_6_938.pdf): cinemática de trayectoria, razón de giro, radio y carga de giro nominales. No respalda la viabilidad de este CAD.
- [NASA/TM-2015-218675, volumen I](https://ntrs.nasa.gov/citations/20150001263): verificación de simuladores de vuelo. No implica certificación del presente código.

## Para obtener una predicción del vehículo
Hace falta un modelo aerodinámico instalado con fuerzas y momentos frente a Mach, Reynolds, incidencia, resbalamiento y deflexiones; propulsión con empuje neto, dinámica y consumos; masas/inercias de componentes; límites estructurales y aeroelásticos; y un control cerrado acoplado a esa planta. El aspecto del video no sustituye esos datos.

## Reproducción
calcular.py genera estados NPZ y resultados; documentar.py verifica y exporta CSV; animar_detalle.py produce 360 PNG a 1920×1080 y 15 fps; codificar.py genera y decodifica MP4. malla_cerrada.npz permite regenerar la visualización sin reabrir los STEP. Los archivos de fotogramas pueden regenerarse y se omiten del ZIP para reducir tamaño.
''')
print(checks)
