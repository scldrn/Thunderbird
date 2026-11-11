from pathlib import Path
import json,numpy as np,csv,hashlib,shutil
from zipfile import ZipFile,ZIP_DEFLATED
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
r=json.loads((P/'RESULTADOS.json').read_text());v=json.loads((P/'VERIFICACION.json').read_text())
h=np.load(P/'5kg_nominal.npz')['history']
headers=['tiempo_s','x_m','y_m','z_m','vx_ms','vy_ms','vz_ms','qx','qy','qz','qw','omega_x_rads','omega_y_rads','omega_z_rads','objetivo_x_m','objetivo_y_m','objetivo_z_m']+[f'F{i}_{a}_N' for i in range(4) for a in 'xyz']+['ax_ms2','ay_ms2','az_ms2']+[f'cono{i}_deg' for i in range(4)]+['perturbacion_x_N','perturbacion_y_N','perturbacion_z_N']
np.savetxt(P/'trayectoria_5kg.csv',h,delimiter=',',header=','.join(headers),comments='')
fig,axes=plt.subplots(3,1,figsize=(10,7),sharex=True)
for i,a in enumerate(axes):
 a.plot(h[:,0],h[:,i+1],label='Integrado');a.plot(h[:,0],h[:,i+14],'--',label='Objetivo');a.set_ylabel('XYZ'[i]+' (m)');a.grid(alpha=.25)
axes[0].legend();axes[-1].set_xlabel('Tiempo (s)');fig.suptitle('Ventiladores internos — simulación condicional, 5 kg supuestos');fig.tight_layout();fig.savefig(P/'trayectoria.png',dpi=160);plt.close(fig)
text='''# Simulación condicional de vuelo — ventiladores internos

Se integra un cuerpo rígido de seis grados de libertad (posición, velocidad, cuaternión y velocidad angular). La trayectoria del video procede de la integración numérica, no de posiciones prescritas para la animación. Los objetivos sí son comandos programados. Es un demostrador de dinámica y control idealizados, no CFD ni predicción validada del prototipo.

## Escenario de 24 segundos
- 0–4 s: estacionario a 2 m y recuperación desde roll=5°, yaw=5°.
- 4–8 s: objetivo +2 m en X, manteniendo actitud de referencia horizontal.
- 8–12 s: objetivo +2 m en Y.
- 12–16 s: objetivo de altura 3,5 m. Entre 12 y 13 s se aplica una fuerza externa hipotética (3, −2, 0) N y un momento (0,03, 0,02, 0,01) N·m para la masa de 5 kg; no equivale a una velocidad de viento calculada.
- 16–20 s: objetivo (−1, −1, 2) m.
- 20–24 s: regreso a (0, 0, 2) m.

No prueba maniobras arbitrarias, vuelo invertido, transiciones o velocidad de 600–1000 km/h. Las aletas aparecen en la geometría visual, pero no tienen modelo de fuerzas aerodinámicas en este escenario.

## Supuestos físicos y control
Masa nominal 5 kg; también se ejecutan 2 y 10 kg. CG=(0,0,0), sin estimación desde componentes. Tensor diagonal obtenido de un elipsoide homogéneo con dimensiones exteriores de referencia 1,341×0,321821×0,194110 m: aproximadamente (0,03531, 0,45899, 0,47546) kg·m². NO es el tensor medido o calculado de la distribución real de piezas A07. Las dimensiones se escalan con m^(1/3) y las inercias con m^(5/3).

Cuatro canales en x=±0,200 m, y=±0,076 m para 5 kg. Se heredan brazos efectivos HIPOTÉTICOS de −0,039 m para Fx y −0,021 m para Fy, no centros de presión verificados. La matriz de asignación incluye esos brazos y las posiciones longitudinales/laterales. No se modelan pares libres y giroscópicos del rotor.

Cada módulo se sustituye por una fuerza vectorial ideal limitada: norma ≤21 N, Fz≥1 N, semicono efectivo 35°. No se deduce el cono del ángulo mecánico del álabe. El empuje máximo y el límite de tasa se escalan linealmente con la masa: son hipótesis, no motores seleccionados. Constante de respuesta de primer orden 0,08 s y tasa máxima de cambio vectorial 50 N/s por módulo a 5 kg, ambos supuestos. El incremento limitado y el filtro conservan convexamente el dominio de fuerzas.

Asignación SLSQP a 50 Hz con restricciones de cono/norma y regularización; posición PD (ganancias 3 y 3), actitud por vector de rotación (8 y 5), saturación de aceleración adicional solicitada a 0,5 g y límites de momento de mando. Observación perfecta del estado, sin ruido ni retraso de sensores. Se integra con RK4, paso 5 ms y normalización del cuaternión, actualizando las fuerzas al comienzo de cada intervalo. La comprobación de paso menor incluye esa discretización de actuadores.

Sin arrastre exterior, sustentación del cuerpo/aletas, interacción de chorros, pérdidas de conductos, aerodinámica de tapas, deformaciones, efecto suelo, potencia/batería, temperatura o fallos de motores. El modelo de planta no está identificado. Esto puede cambiar sustancialmente el comportamiento del vehículo real.

## Video
24 s, 15 fotogramas/s, reproducción 1:1. La malla visual se extrae del STEP A07 abierto; las tapas se omiten para evitar representar un mecanismo aún inexistente. Esa omisión no demuestra un estado de vuelo físicamente realizable. La visualización no calcula aerodinámica desde la malla.

## Resultados calculados del modelo
'''
text+='\n| Masa supuesta | Velocidad máxima (m/s) | Aceleración neta máxima (g) | Fuerza máxima por módulo (N) | Cono máximo (°) |\n|---|---:|---:|---:|---:|\n'
for s in r[:3]:text+=f"| {s['mass_assumed_kg']:g} kg | {s['max_speed_ms']:.3f} | {s['max_acceleration_ms2']/9.80665:.3f} | {s['max_fan_force_N']:.3f} | {s['max_force_angle_deg']:.3f} |\n"
text+='''
Las tres ejecuciones nominales no reportan asignaciones inviables ni fallos del optimizador. Esto verifica únicamente los estados ensayados y el dominio ideal. El máximo ángulo de fuerza de 5 kg deja unos 0,08° respecto a la cota supuesta: no hay margen suficiente para afirmar robustez. La variante de 5 kg con capacidad máxima reducida 20% cambia solo la cota de fuerza, no el resto de la planta; no es una prueba general de incertidumbre.

## Verificación numérica
Casos analíticos: caída libre, estacionario y par constante en un eje principal. Errores máximos registrados inferiores a 2×10⁻¹³ en sus variables respectivas. Repetir 5 kg con paso 2,5 ms cambia la posición hasta aproximadamente 3,63 mm y la actitud hasta 0,0165°. Es convergencia numérica local; no precisión física. No se ejecutó la batería completa de casos NASA.

## Fuentes primarias y alcance
- [Brescianini y D’Andrea, ICRA 2016](https://ethz.ch/content/dam/ethz/special-interest/mavt/dynamic-systems-n-control/idsc-dam/People/bdario/brescianini_dandrea_omnidirectional_aerial_vehicle.pdf): fundamentos de asignación de fuerza/momento y dinámica de vehículos omnidireccionales. Su prototipo de ocho rotores es distinto del nuestro; sus ensayos no validan los cuatro conductos ni los parámetros de esta simulación.
- [NASA/TM-2015-218675, volumen I](https://ntrs.nasa.gov/citations/20150001263): necesidad y metodología de verificación de simuladores 6DOF. No se atribuye certificación NASA al código.
- Datos de proyecto: modelo de palancas de verificar_tasas_A.py y disposición de reserva axial 60 mm. Los datos instalados de fuerza/par siguen pendientes.

## Reproducción y próximos pasos
simular.py genera escenarios NPZ/JSON; verificar.py ejecuta comprobaciones analíticas y paso menor; animar.py extrae malla STEP y produce PNG; codificar_ffmpeg.py crea MP4 usando imageio-ffmpeg. Se incluyen malla_visual.npz y todos los estados para reproducir la visualización sin reextraer el CAD. El código Swift queda como intento de codificación no disponible en este equipo, no es necesario para reproducir el MP4.

Para identificar la planta real faltan mapas instalados fuerza/momento/potencia frente a órdenes de rotor/álabes, su respuesta temporal, masas/inercias y efectos exteriores. La investigación CFD global permanece pausada; esta simulación local fue autorizada por la solicitud de comportamiento en vuelo.
'''
(P/'INFORME.md').write_text(text)
shutil.copyfile(P/'frames/0180.png',P/'vista_simulacion.png')
