# Modelo A: estudio inicial de salidas vectoriales internas

Se continúa la arquitectura A seleccionada el 1 de noviembre de 2026. Se conserva como referencia visual la carrocería deportiva aprobada. Este estudio numérico no altera el CAD y no representa un mecanismo ya dimensionado.

## Pregunta resuelta

¿Puede una fuerza vectorial independiente en cada uno de los cuatro ventiladores corregir la ausencia de empuje lateral de los cuatro ejes paralelos? En el modelo ideal, sí permite añadir fuerzas laterales y momentos; la capacidad está limitada por ángulo efectivo, magnitud de fuerza y fuerzas simultáneas necesarias para sostenerse. Esto aún no resuelve todo el objetivo de omnidireccionalidad con cualquier orientación.

## Hipótesis y método

Script: `../vectorizacion_A.py`. Cuatro puntos de aplicación x=−0,280/+0,285 m, y=±0,065 m y z=0,058 m, tomados de la disposición ilustrada. Masa de referencia SUPUESTA de 5 kg y CG en el origen; no se afirma cierre de masa ni CG real de esta carrocería.

Cada punto puede generar una fuerza dentro de un cono hacia +z, con magnitud limitada por un valor T a dimensionar. Se usan 32 direcciones azimutales en el borde del cono, su eje y fuerza cero; su envolvente convexa es una aproximación interior de las fuerzas posibles del actuador vectorial ideal. Las fuerzas resultantes reconstruidas se verifican contra el cono circular y el límite de magnitud. No se convexifica la unión de conos de empuje directo e inverso: eso podría inventar fuerzas laterales físicamente inaccesibles para un solo actuador.

Se minimiza T mediante programación lineal para cada demanda: fuerza igual a gravedad más aceleración adicional, con 26 direcciones de aceleración y siete demandas de momento (cero, ±0,5 N·m sobre cada eje). Aceleraciones adicionales de 0, 0,5 y 1 g; ángulos efectivos de 0°, 15°, 30° y 45°. Total: 1484 demandas, incluyendo siete por condición sin aceleración adicional. La reserva de 0,5 N·m es una hipótesis de dimensionamiento, no una aceleración angular inferida desde una inercia real.

Ángulo efectivo significa dirección de la fuerza/chorro saliente. NO equivale a ángulo mecánico de una aleta. No se asigna una relación entre ambos sin CFD o datos. Se omiten pérdidas de flujo, estelas, par de reacción, cargas sobre álabes de control, dinámica de actuadores y giro del cuerpo.

## Resultados

| Desviación efectiva máxima | Estacionario + demandas de par | +0,5 g: casos con solución / muestreados | Mayor capacidad T por ventilador entre esos casos | +1 g: casos con solución / muestreados |
|---|---:|---:|---:|---:|
| 0° | 5/7 | 10/182 | 20,31 N | 6/182 |
| 15° | 7/7 | 38/182 | 23,14 N | 8/182 |
| 30° | 7/7 | 174/182 | 23,03 N | 64/182 |
| 45° | 7/7 | 182/182 | 22,71 N | 78/182 |

La columna T se calcula sobre casos resueltos; no debe compararse entre filas como si todas cubrieran la misma envolvente. La cobertura completa de 182 puntos no demuestra cobertura continua de todas las direcciones. Los puntos que no pertenecen al politopo interior no se declaran físicamente imposibles en el cono circular exacto.

El caso 0° omite par de reacción: la falta de control de guiñada en esa fila es una limitación del modelo sin reacción, no la afirmación de que un cuadricóptero no pueda girar en guiñada. Sigue sin poder generar fuerza lateral con orientación fija.

## Límites fundamentales

Para sostener altura y producir una aceleración horizontal a con fuerza resultante inclinada, sin otros aportes, el ángulo efectivo requerido es atan(a/g). Para +0,5 g horizontal da 26,565°; para +1 g horizontal, 45°. Esto no incluye reserva de momentos ni pérdidas.

Cubrir una esfera de aceleraciones adicionales de radio 0,5 g alrededor del estacionario es más exigente que cubrir solo el plano horizontal: el límite geométrico sin reserva de momento llega a 30°. Para una esfera de radio 1 g se aproxima a 90° en ciertas direcciones; además el punto de fuerza total cero no permite sostener un momento no nulo con fuerzas estrictamente ascendentes. Los resultados del muestreo son coherentes con estas restricciones, pero no prueban una envolvente real.

Con fuerza solo dentro de conos hacia +z del cuerpo no se puede permanecer estacionario con el cuerpo invertido. La omnidireccionalidad completa a cualquier actitud requeriría empuje reversible/rutas alternativas u otra arquitectura. Movimiento en distintas direcciones con actitud aproximadamente horizontal y movimiento a cualquier actitud son requisitos diferentes; se mantienen explícitos hasta validar el conjunto completo.

## Mecanismo candidato y alojamiento pendiente

Candidato para la siguiente etapa: dos familias de álabes de desviación, con ejes de mando ortogonales, después de cada ventilador; accionamiento protegido dentro del cuerpo. No implica que dos aletas ideales alcancen el cono calculado. Deben dimensionarse secciones, separación respecto al rotor, ejes, servos, transmisión y topes, midiendo/calculando simultáneamente fuerza, par y pérdidas.

El CAD aprobado muestra ventiladores y rejillas superiores, pero no tiene un recorrido completo de salida y vectorización funcional. El flujo debe atravesar rutas de entrada y salida que no se bloqueen con carcasas o componentes. Si esas rutas no caben, habrá que modificar la distribución interior o documentar un cambio de envolvente. No basta añadir dos superficies en un dibujo.

Los 22,71 N son una exigencia de fuerza ÚTIL del actuador vectorial ideal en los casos considerados. No son el empuje axial de catálogo, no seleccionan motor y no validan los pequeños rotores del render. Las pérdidas podrían aumentar la demanda del ventilador y la potencia; no se introduce un porcentaje arbitrario como si estuviera medido.

## Fuentes primarias y alcance

NASA/TM–2020-220484, *Wind Tunnel Performance Test of a Ducted Fan System*: ensayos que varían condiciones de vuelo y geometría/deflexión de álabes de salida, no de nuestro vehículo. https://rotorcraft.arc.nasa.gov/Publications/files/NASA_TM-2020-220484_Final.pdf

Young, *Novel Tilting Ducted-Fan Configurations*, NASA 2023: estudio paramétrico que considera control diferencial y álabes de control; sus ventiladores y coeficientes no se transfieren a este diseño. https://ntrs.nasa.gov/api/citations/20230000799/downloads/1603_Young_011723.pdf

Los resultados propios están en `CASOS.json` y `RESUMEN.json`. Constituyen una prueba matemática del modelo declarado, no una validación de funcionamiento, estructura, autonomía o velocidad máxima.
