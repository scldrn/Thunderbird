# Cierre del análisis preliminar de sustentación y transición

**Actualización posterior:** `TRIMADO-Y-GEOMETRIA-VARIABLE.md` resuelve conjuntamente fuerza y momento con superficies sustentadoras. Los momentos a 10° de este documento no son cargas inevitables del vuelo rápido: la incidencia de equilibrio puede ser mucho menor. Sus umbrales de cuerpo solo tampoco son umbrales de una configuración con cola sustentadora.

## Resultado para el diseño

La arquitectura «ocho rotores retráctiles + reactor axial + fuselaje sin superficies sustentadoras» NO tiene todavía una transición demostrada. Retraer los rotores no puede depender exclusivamente de alcanzar una velocidad programada: antes debe existir capacidad suficiente para sostener el peso **y** compensar los momentos en los tres ejes. La opción que recomiendo desarrollar es un fuselaje circular con sustentación y control aerodinámicos explícitos, manteniendo los rotores operativos hasta completar la transferencia de fuerzas. Es una decisión de ingeniería condicionada, no una aeronave validada.

Se conserva el desarrollo independiente de 2, 5 y 10 kg. Los 405 casos nuevos estudian cuerpos cerrados de referencia; no son simulaciones de una transición dinámica ni sustituyen los presupuestos de masa existentes.

## Evidencia documental verificada

Se revisó visualmente la página impresa 9 de [Allen y Perkins, NACA TR 1048](https://ntrs.nasa.gov/citations/19930090962), ecuaciones 14–15 y figura 6. El término potencial de sustentación depende del área de base; no se puede sustituir esta por el área frontal máxima de un huso que termina en punta. El término potencial de momento conserva una contribución del volumen incluso con base nula. La contribución viscosa requiere un coeficiente transversal y su posición de aplicación.

La comparación principal de fuerzas del informe corresponde a cuerpos con nariz ojival y tramo cilíndrico, alargamientos 13,1 y 21,1, a Mach 1,98. Los ensayos transversales a 90° cubren Mach 0,3–0,7. Por tanto, este informe aporta un método y evidencia para esas configuraciones, no validación directa de nuestro huso L/D 4–8 a Mach 0,82. Sus coeficientes no deben trasladarse sin comprobar Reynolds, separación y forma.

## Hipótesis de los cálculos nuevos

- Esferoide cerrado, simétrico longitudinalmente; volumen exterior igual a masa / 200 kg/m³. Este supuesto de densidad global no es un cierre volumétrico de componentes.
- Masas de 2, 5 y 10 kg; L/D de 4, 6 y 8; incidencias de 5°, 10° y 15°; velocidades de 100, 200, 300, 600 y 1000 km/h.
- Coeficiente transversal efectivo constante: 0,3, 0,6 o 1,2. Son tres sensibilidades elegidas, **no valores medidos ni límites de confianza**. La incertidumbre real puede excederlos.
- Resultante viscosa en el centro geométrico y centro de masa allí situado. No se traslada aquí el desplazamiento de 50 mm usado en la auditoría del rotor de 5 kg: es un estudio de referencia diferente.
- Se conserva la dependencia trigonométrica de la ecuación 14. Se omiten, como allí en la expresión de sustentación, pequeñas contribuciones del arrastre axial. No hay corrección transónica, interferencias, tomas, escape, trimado ni deformación.
- El momento mostrado es el momento potencial del cuerpo sin compensar. No representa la carga de un vehículo trimado ni una aceleración angular efectivamente alcanzada.

## Revisión de los 12–20 g

Sustentación dividida por peso a 1000 km/h, L/D 8 y 10°:

| Masa | C transversal 0,3 | C transversal 0,6 | C transversal 1,2 |
|---|---:|---:|---:|
| 2 kg | 2,41 | 4,82 | 9,64 |
| 5 kg | 1,78 | 3,55 | 7,10 |
| 10 kg | 1,41 | 2,82 | 5,64 |

Son resultados de sensibilidad propios. No se confirma la estimación anterior de 20,5 g para 2 kg ni 12 g para 10 kg. Tampoco se demuestra que sean imposibles: faltan coeficientes del cuerpo real, su base abierta y el sistema sustentador integrado. Además, sustentación/peso no equivale automáticamente a aceleración de trayectoria; deben combinarse gravedad, empuje y arrastre.

El mismo modelo da momentos sin compensar de aproximadamente 161, 403 y 805 N·m, respectivamente. Es una advertencia sobre la extrapolación de un huso cerrado y la necesidad de trimado. No deben adoptarse como cargas de diseño verificadas. Añadir cola, toma y tobera altera la geometría y obliga a recalcular ambas fuerzas y momentos conjuntamente.

## El hueco de sustentación durante la retracción

Para L/D 6, incidencia 10° y C transversal 0,6, la velocidad algebraica a la que la sustentación corporal iguala al peso es:

| Masa | Velocidad calculada | Momento sin compensar en ese punto |
|---|---:|---:|
| 2 kg | 478 km/h | 36,8 N·m |
| 5 kg | 557 km/h | 124,8 N·m |
| 10 kg | 625 km/h | 314,5 N·m |

**No son velocidades autorizadas de retracción ni vuelos de equilibrio.** No se comprueba que el reactor acelere hasta ellas, que los rotores toleren ese flujo ni que puedan compensarse los momentos. Su utilidad es mostrar que el cuerpo solo no resuelve por sí mismo una transición temprana bajo esta hipótesis.

El mapa de rotor existente es de estacionario. No permite calcular empuje, potencia ni cargas al atravesar una corriente oblicua durante la aceleración; utilizarlo sin modificaciones en esta fase produciría una falsa validación.

## Dos vías cuantificadas para cubrir ese hueco

### Superficies sustentadoras

Si se exige sostener todo el peso a 150 km/h con CL efectivo supuesto de 0,5, ignorando conservadoramente la sustentación corporal, el área efectiva necesaria es:

| Masa | Área efectiva |
|---|---:|
| 2 kg | 0,0369 m² |
| 5 kg | 0,0922 m² |
| 10 kg | 0,1844 m² |

Son áreas aerodinámicas de referencia, no área mojada, suma indiscriminada de cuatro aletas ni área superficial de un anillo. El CL es una hipótesis: no garantiza ausencia de pérdida ni un momento compensable. Para una cruz debe calcularse qué superficies contribuyen en cada azimut y su interacción con el cuerpo; para un anillo se requiere su propia polar. El mecanismo retráctil y sus refuerzos deben entrar en el cierre de masa.

Esta opción merece prioridad en el estudio siguiente porque permite repartir explícitamente sustentación y control. No establece todavía dimensiones de ala definitivas.

### Empuje inclinado

Como condición de fuerza vertical solamente, si se dispone realmente de 100 N, un vehículo de 5 kg necesita inclinar ese empuje al menos 29,4° sobre la horizontal para sostenerse sin sustentación aerodinámica. Con 10 kg y los mismos 100 N, necesita 78,7°; con 250 N, 23,1°. Estos valores se calcularon con empuje constante hipotético: el empuje nominal de catálogo no demuestra empuje instalado.

Un reactor axial puede aportar esa componente inclinando el cuerpo; una tobera vectorial permite modificar la dirección del empuje respecto al fuselaje. Ninguno de esos hechos garantiza por sí solo seis grados de libertad independientes. Hacen falta control del momento, márgenes térmicos, mapa de empuje y una trayectoria viable. La masa de vectorización no está presupuestada como componente real.

## Secuencia propuesta y criterios comprobables

1. Estacionario con rotores; reactor estabilizado cuando se necesite. Debe verificarse el efecto de su empuje residual y del chorro sobre los rotores.
2. Aceleración con rotores desplegados dentro de una envolvente de flujo medida. Las superficies sustentadoras y el control aerodinámico toman carga gradualmente.
3. Transferencia de sustentación y de control. Antes de detener un rotor, comprobar que el conjunto restante puede producir fuerzas y momentos requeridos con margen, a la masa y centro de gravedad actuales.
4. Detención, indexación y retracción según cinemática comprobada. Recalcular inercia, control y cargas de los mecanismos durante todo el movimiento; no tratarlo como cambio instantáneo.
5. Aceleración rápida con configuración bloqueada. Validar arrastre total, empuje instalado, estabilidad y aeroelasticidad.

Esta secuencia es una especificación para calcular/ensayar, no una trayectoria ya simulada. No se fijan tiempos de transición ni velocidades de retracción sin los mapas que los determinen.

## Qué queda resuelto y qué no

Quedan cerrados la lectura de las ecuaciones relevantes, su implementación para el cuerpo de referencia y el barrido de sensibilidad. La evidencia disponible obliga a retirar la sustentación de 12–20 g como prestación validada y a introducir un problema explícito de trimado y transferencia de sustentación.

Siguen abiertos el cuerpo con conductos, fuerzas y momentos medidos/CFD, superficies de control, mapa de rotores en avance, empuje instalado, cinemática y masa completa. Ni la versión de 5 kg ni la de 10 kg tiene aún demostrado el conjunto estacionario omnidireccional + transición + 1000 km/h. Los estudios de escritorio no deben presentarse como un prototipo listo para fabricar.

## Reproducción y entregables

- Código: `transicion_sustentacion.py`.
- 405 casos: `resultados/cuerpo_transicion_SENSIBILIDAD.csv`.
- 27 umbrales algebraicos de sustentación y escenarios de empuje: `resultados/transicion_sustentacion_RESUMEN.json`.
- Figura: `resultados/transicion_sustentacion.png`.
- Comprobaciones ejecutadas: fuerza y momento nulos a velocidad cero y a incidencia cero; escalado cuadrático con velocidad; sustitución de todos los umbrales calculados para recuperar el peso.
- Fuente primaria: [NACA TR 1048, ficha y descarga NASA](https://ntrs.nasa.gov/citations/19930090962). Copia local: `fuentes/nasa/19930090962.pdf`.

Las comprobaciones verifican implementación y consistencia; no validan las hipótesis aerodinámicas.
