# Conos efectivos más estrechos en las trayectorias con tasas limitadas

Se revisaron las nueve trayectorias guardadas de 30° de cabeceo, de 5 kg supuestos, para las tres distribuciones candidatas con reservas axiales de 38/60/80 mm. No se ha elegido una distribución nueva del producto. Se conservan exactamente las fuerzas calculadas y los escenarios de masa/CG/inercia anteriores.

## Resultado

Todas las trayectorias usan como máximo 33,75° de inclinación efectiva de fuerza por ventilador, aunque el LP original permitía 45°. Por tanto, esas mismas fuerzas también satisfacen un cono de 35° y uno de 40°, en todos los instantes de la interpolación lineal. No fue necesario repetir los LP ni recalcular una trayectoria distinta. Se verificaron de nuevo fuerzas, precarga, tasas vectoriales y balance nodal directo de Newton–Euler.

La inclusión continua se sigue de la convexidad del cono circular: una combinación lineal entre dos fuerzas admisibles permanece dentro. La distancia a la superficie lateral se expresa Fz·sin(δ) − norma(Fxy)·cos(δ); es cóncava a lo largo de cada segmento, por lo que su mínimo ocurre en un extremo. Los valores negativos significan que la asignación guardada sale del cono, no que sea imposible encontrar otra asignación.

| Reserva axial | Parámetro de tasa | Duración de la trayectoria guardada | Ángulo máximo útil | Margen mínimo a la superficie del cono de 35° |
|---:|---:|---:|---:|---:|
| 38 mm | 20 N/s | 1.175 s | 33.75° | 0.1961 N |
| 38 mm | 50 N/s | 0.784 s | 33.75° | 0.1374 N |
| 38 mm | 100 N/s | 0.588 s | 33.75° | 0.1126 N |
| 60 mm | 20 N/s | 1.332 s | 33.75° | 0.2539 N |
| 60 mm | 50 N/s | 0.888 s | 33.75° | 0.1530 N |
| 60 mm | 100 N/s | 0.666 s | 33.75° | 0.1244 N |
| 80 mm | 20 N/s | 1.431 s | 33.75° | 0.1523 N |
| 80 mm | 50 N/s | 1.073 s | 33.75° | 0.1138 N |
| 80 mm | 100 N/s | 1.073 s | 33.75° | 0.0979 N |

## Interpretación y límites

La trayectoria ideal del cuerpo rígido es la misma porque no cambia la función de fuerza aplicada. Los errores numéricos de interpolación y propagación ya cuantificados en el estudio anterior se conservan; no se convierten en precisión de vuelo. No se demuestra un tiempo mínimo global ni la respuesta real de un propulsor. Las tasas de 20/50/100 N/s son parámetros supuestos, no especificaciones de motores.

El margen angular entre 33,75° y 35° es solo 1,25°. La tabla expresa distancia en espacio de fuerzas a la superficie lateral; no es tolerancia mecánica de un álabe, margen de estabilidad o robustez ante perturbaciones. Tampoco cubre simultáneamente incertidumbres de magnitud, precarga, tasa, pares libres o posición del centro de presión. Puede haber otras restricciones activas sin margen.

El ángulo útil de fuerza no equivale al ángulo de álabe. Los resultados requieren un mapa instalado de fuerza/momento/potencia y su dinámica. El canal CFD anterior tiene otra disposición de bancos y no calibra estas palancas de las candidatas. Los ensayos de cono siguen siendo modelos ideales.

El estudio estático de conos para 2/5/10 kg no permite trasladar estos tiempos de giro de 5 kg a las otras masas. El objetivo de máxima agilidad y 600–1000 km/h permanece abierto; 0,5 g y el giro de 30° son escenarios de investigación.

Archivos: `VERIFICACION.json` conserva comprobaciones y hashes de todas las trayectorias originales. Código: `auditar_conos_trayectorias_A.py`, en modelos_integrados. No se modificaron los NPZ originales ni la simulación CFD activa.
