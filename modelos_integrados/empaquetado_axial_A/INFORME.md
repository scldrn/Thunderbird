# A: redistribución para una reserva axial

Se estudia la carrocería elegida, sin declarar una nueva selección del usuario ni un óptimo global. La ruta recta original tiene poco espacio entre camisas. Esta búsqueda comprueba si desplazar las estaciones puede abrirla conservando alojamiento y control ideal.

Se probaron semiseparaciones laterales de 65, 76, 86 y 96 mm y estaciones longitudinales cada 25 mm entre −350/−100 y +100/+350 mm. Los 12 prismas de barrido por canal cubren el intervalo mecánico ±45°, junto con ejes, disco giratorio y motor representativo. Los casos que pasan el filtro de puntos se verifican mediante diferencia de volúmenes en CAD. No incluyen servos, rodamientos o soportes futuros.

Se prefiltraron pares de estaciones por separación longitudinal y desequilibrio geométrico, y se calculó su control. Por eso el mejor resultado del conjunto retenido no es el mejor posible entre todos los pares, ni entre todas las formas. Ninguna posición con semiseparación 96 mm pasó el criterio conservador en esta malla; no prueba imposibilidad fuera de ella.

Hipótesis de control: 5 kg, CG=(0,0,0), cuatro fuerzas ascendentes dentro de conos efectivos de 45°, aceleraciones dentro de esfera de radio 0,5 g con cuerpo horizontal, reserva por componente de momento ±0,5 N·m y precarga vertical 1 N. Las palancas laterales se aproximan por los centros de las filas inferiores (z_x=−39 mm, z_y=−21 mm). No son centros de presión medidos.

| Semiseparación lateral | Estaciones x | Reserva axial exterior con 2 mm de separación radial | Capacidad útil suficiente por fan, modelo refinado |
|---:|---|---:|---:|
| 65 mm | -300 / +275 mm | 38 mm | 20.78 N |
| 76 mm | -200 / +200 mm | 60 mm | 20.43 N |
| 86 mm | -100 / +100 mm | 80 mm | 20.26 N |

Cada caso refinado comprueba los 1536 vértices de un dominio exterior de fuerzas × caja de momentos. Por convexidad y signos fijos la cobertura es continua en el modelo ideal. Se releyeron sus arrays y se recalculó el equilibrio con ecuaciones explícitas. Faltan el mapa de empuje/potencia/par instalado y la respuesta dinámica.

## El espacio ganado cambia la maniobrabilidad

Con la misma capacidad útil ideal de 21 N por ventilador y precarga de 1 N, se calcularon límites de momento puro en estacionario mediante LP, manteniendo nula la fuerza lateral y el otro momento. Esta comparación usa la misma capacidad instalada hipotética, no capacidades distintas por diseño. La aceleración angular exige una inercia real que todavía no se conoce.

| Semiseparación | Momento puro de cabeceo | Momento puro de alabeo | Intervalo CG x con reserva de cabeceo ±0,5 N·m |
|---:|---|---|---|
| 65 mm | -9.44 a 10.67 N·m | -2.27 a 2.27 N·m | -207 a 182 mm |
| 76 mm | -6.99 a 6.99 N·m | -2.66 a 2.66 N·m | -132 a 132 mm |
| 86 mm | -3.50 a 3.50 N·m | -3.01 a 3.01 N·m | -61 a 61 mm |

La reserva de 80 mm se logra con x=±100 mm, y=±86 mm en este conjunto. El cabeceo pierde brazo frente a estaciones más separadas, mientras el alabeo gana separación lateral. Una pequeña mejora de la capacidad mínima de fuerza no permite declarar mejor agilidad: falta masa, CG, tensor de inercia y respuesta.

Los tres STEP contienen 110 piezas válidas reimportadas y se denominan **reservas de empaquetado**. El cilindro central es un volumen exterior reservado entre x=−400 y +400 mm; no es un motor, conducto aerodinámico o toma nariz–cola. Se comprobó su contención y ausencia de intersección con camisas y mecanismos en las posiciones revisadas. La carcasa sigue siendo una representación volumétrica, sin pared/material cerrados.

Las estaciones nuevas necesitan entradas, salidas, tapas, cierres, soportes y transmisión propios. No se han resuelto flujo, distorsión, sellado, refrigeración ni arrastre compresible. La masa del propulsor rápido puede desplazar el CG fuera del intervalo disponible; debe cerrarse con el resto de los componentes antes de adoptar esta distribución.

Archivos: `RESUMEN.json` conserva la búsqueda y sus límites; `POSES.json` los ensayos de alojamiento; `VERIFICACION.json` las intersecciones, el puente STEP/control y los límites de momento; `control/` los casos LP. Código: `buscar_estaciones_axiales_A.py`, `verificar_candidato_axial_A.py` y el asignador parametrizado de fuerzas. El objetivo global sigue abierto.

## Extensión reversible de las estaciones

Se conserva el objetivo de máxima agilidad: además del dominio horizontal inicial se evaluó la capacidad adicional de cualquier actitud con 0,5 g y una esfera de aceleraciones de 5 g con cuerpo horizontal. Se usan signos diagonales fijos, fuerza útil simétrica, bancos de salida de cada sentido y las mismas reservas de ±0,5 N·m. Estas son exigencias del modelo, no prestaciones del rotor de dibujo.

| Reserva axial exterior | Cualquier actitud, 0,5 g | Cuerpo horizontal, 5 g |
|---:|---:|---:|
| 38 mm | ±43.72 N/fan | ±162.45 N/fan |
| 60 mm | ±42.80 N/fan | ±159.37 N/fan |
| 80 mm | ±43.27 N/fan | ±160.57 N/fan |

Cada condición añade 1536 solicitudes de comprobación y una cobertura continua suficiente por convexidad. La caracterización real de fuerza/momento, potencia, inversión y dinámica sigue pendiente. No se reinterpreta el paso geométrico reservado como motor capaz de proporcionar estas fuerzas. Código: `control_reversible_estaciones_A.py`.
