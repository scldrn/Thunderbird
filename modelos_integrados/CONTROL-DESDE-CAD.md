# Control recalculado desde el CAD integrado

Resultado: la disposición desplegada actual NO conserva la buena asignación de fuerzas de los estudios anteriores. Combinar L/D=6, estaciones ±L/4 y los ángulos heredados produce una dirección de momento muy débil. Tener rango algebraico seis no implica buena autoridad de control.

## Datos y método

Fuente geométrica y de masas: `salida/{5,10}kg/mediciones_DIGITALES.json`. Script reproducible: `control_desde_cad.py`. Todos los resultados siguientes son cálculos condicionados, no medidas físicas. Se emplean fuerzas y momentos de ocho actuadores reversibles ideales, respecto al CG provisional del CAD. Se exige cubrir una esfera de fuerzas que incluye gravedad en cualquier orientación y aceleración adicional en cualquier dirección, simultáneamente con una esfera de aceleraciones angulares desde reposo. La imagen de esta esfera angular por el tensor de inercia se trata como elipsoide de par; no se sustituye por el mayor momento principal.

El límite de empuje positivo y negativo se supone igual. No se incluyen par de reacción de rotores, efectos giroscópicos, cargas aerodinámicas, interferencias de flujo, dinámica de paso, límites de potencia o calentamiento. Las partidas sin posición se colocan alternativamente en CG o en una distribución periférica simétrica respecto al CG; son sensibilidades, no montajes realizables ya comprobados. Tampoco se incluyen masas desconocidas salvo escenarios adicionales explícitos.

## Exigencia ideal de empuje por rotor

Escenario más favorable de los dos repartos de partidas: estas se concentran en el CG, sin añadir nuevas masas faltantes. Se reserva aceleración angular simultánea de 2 rad/s² en cualquier dirección, desde velocidad angular cero.

| Objetivo de variante | Presupuesto actual | Sostenerse, cualquier orientación | Añadir 0,5 g omnidireccional | Añadir 1 g omnidireccional |
|---|---:|---:|---:|---:|
| 5 kg | 5,498 kg | ±100,91 N/rotor | ±138,83 N/rotor | ±176,76 N/rotor |
| 10 kg | 10,685 kg | ±206,37 N/rotor | ±278,84 N/rotor | ±351,31 N/rotor |

Son capacidades mínimas simétricas necesarias para cubrir todo el conjunto de demandas de este modelo, no el empuje de cada rotor durante una maniobra particular. El valor alto no demuestra que cualquier arquitectura omnidireccional sea inviable: identifica una mala combinación concreta de posiciones y ejes.

## Diagnóstico geométrico independiente

Para 5 kg, la matriz con momentos normalizados por longitud tiene valores singulares aproximadamente 1,7602; 1,6382; 1,4931; 0,8247; 0,7660; 0,01318. Su condición es aproximadamente 133,5 en esta normalización. Este indicador no es adimensional respecto a cualquier elección de escala: se documenta la normalización utilizada.

Como diagnóstico, manteniendo masa, CG y ejes, y cambiando solamente la posición axial de las estaciones, el empuje ideal por rotor para sostenerse en cualquier orientación SIN reserva angular resulta:

| Estaciones | Empuje simétrico requerido |
|---|---:|
| ±0,15 L | 20,26 N |
| ±0,20 L | 24,20 N |
| ±0,25 L, CAD actual | 75,85 N |
| ±0,30 L | 28,71 N |
| ±0,35 L | 22,15 N |

Este barrido no autoriza mover los módulos: altera las inercias y holguras, que aquí se han congelado deliberadamente para aislar el origen de la pérdida de autoridad. Requiere verificar discos, brazos, paneles y trayectorias de retracción. Una alternativa es reoptimizar los ejes manteniendo las estaciones, también con comprobación de interferencias.

## Verificación numérica

108 escenarios: dos variantes, tres masas adicionales, dos repartos de masa no ubicada, tres reservas angulares y tres demandas de traslación. Se realizaron 1080 comprobaciones mediante programación lineal: demanda en la cara limitante, inviabilidad al reducir el límite de empuje un 0,01 %, y ocho demandas direccionales por escenario. Residuo máximo aproximado 5,33e-13 en las ecuaciones normalizadas. Esto verifica la implementación del modelo estático, NO la validez física de sus supuestos.

## Consecuencia para los renders y la investigación

Los renders representan fielmente una geometría preliminar que todavía necesita rediseño de asignación de fuerzas. No deben utilizarse para afirmar movimiento omnidireccional abrupto demostrado. La siguiente iteración debe optimizar conjuntamente posiciones/ejes, holguras, masa e inercia; después incorporar mapas de actuadores y respuesta temporal. No existe todavía evidencia de un óptimo global ni de viabilidad integrada a 600–1000 km/h.
