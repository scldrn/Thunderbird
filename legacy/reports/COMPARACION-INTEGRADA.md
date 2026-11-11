# Comparación integrada con incertidumbre explícita

## Resultado

Al incorporar simultáneamente sustentación, estabilidad estática, arrastre corporal y superficies, el presupuesto resulta más exigente que en los estudios de partes aisladas. No se ha identificado una arquitectura que cumpla de forma verificada toda la misión. Los resultados sí permiten descartar la selección de motor basada únicamente en el arrastre del fuselaje desnudo y muestran por qué un alargamiento universal de 6–8 no está demostrado como óptimo.

Se evaluaron 99 geometrías: masas de 2, 5 y 10 kg y L/D de 4 a 12 en pasos de 0,25. Cada una se examinó en 45 combinaciones de condición de vuelo y coeficientes: 4455 puntos en total. No es CFD; se reutilizan las ecuaciones y limitaciones documentadas en `TRIMADO-Y-GEOMETRIA-VARIABLE.md` y `calcular.py`.

## Criterios de dimensionamiento, todos condicionados

La cola se dimensiona para que su contribución estabilizadora lineal alrededor de incidencia cero exceda en un 20% la desestabilizadora del cuerpo, usando pendiente de sustentación 2 por radián. Ese 20% es un criterio elegido: no es margen estático certificado, reserva dinámica ni garantía frente a todas las incertidumbres.

El ala central se dimensiona por separado en cada masa y alargamiento para equilibrar el peso a 150 km/h con incidencia de 8°, pendiente de sustentación 2 por radián y coeficiente transversal corporal 0,3. El ala se sitúa idealmente sobre el centro de masa; la cola a 0,4 longitudes detrás. Las áreas no se escalan simplemente desde la versión de 5 kg: se resuelve de nuevo el requisito.

Se comprueban pendientes 2, 3 y 4 por radián y coeficientes transversales 0,3, 0,6 y 1,2. Los estados son 1 g a 150 km/h con ala desplegada, 1 g a 600 y 1000 km/h con ala central recogida, y 10 y 20 de sustentación/peso a 1000 km/h. Los estados de alta carga no equivalen a aceleración neta ni consideran resistencia estructural o empuje suficiente.

El filtro exige raíz de equilibrio, incidencia hasta 10°, deflexión hasta 15°, CL hasta 0,8 y derivada estática de cabeceo estabilizadora. Evaluar estos puntos discretos no demuestra robustez continua ni estabilidad en seis grados de libertad.

## Geometrías de referencia L/D 6

| Masa | Largo × diámetro corporal | Ala por plano | Cola por plano | Masa solo de paneles |
|---|---|---:|---:|---:|
| 2 kg | 0,883 × 0,147 m | 0,0358 m² | 0,0340 m² | 0,140 kg |
| 5 kg | 1,198 × 0,200 m | 0,1094 m² | 0,0626 m² | 0,344 kg |
| 10 kg | 1,509 × 0,252 m | 0,2418 m² | 0,0994 m² | 0,682 kg |

Masa de paneles calculada con 1 kg/m², cuatro superficies centrales y cuatro de cola. «Por plano» significa el área del par opuesto: el área física total es dos veces la suma de las dos columnas. No se incluyen actuadores, bisagras, cierres ni refuerzos. La densidad exterior de referencia sigue siendo 200 kg/m³ y no demuestra empaquetado real.

Estas geometrías pasan los puntos de 1 g y 10 de sustentación/peso del filtro estático. Las de 5 y 10 kg no pasan todos los puntos de 20. La de 2 kg sí pasa esos filtros algebraicos, lo cual **no acredita una aeronave capaz de maniobrar a 20 g**.

## Arrastre parcial con el ala central recogida

Se combinan dos factores de forma del modelo corporal anterior y coeficientes de arrastre de perfil de superficies entre 0,006 y 0,020. Se conserva el arrastre inducido del modelo de trimado. Son extremos de hipótesis seleccionadas, no bandas estadísticas, límites físicos ni intervalos que necesariamente contengan el valor real.

| Masa, L/D 6 | A 600 km/h | A 1000 km/h |
|---|---:|---:|
| 2 kg | 25–44 N | 65–116 N |
| 5 kg | 45–80 N | 115–209 N |
| 10 kg | 71–125 N | 179–328 N |

Faltan arrastre de onda, base, toma, flujo interno, interferencias, alojamientos y detalles de mecanismos. Tampoco se incorpora un modelo completo del incremento de arrastre corporal por incidencia. Por tanto, se denomina **arrastre parcial**, no total ni cota inferior rigurosa.

La comparación con motores de catálogo requiere curvas de empuje instalado frente a velocidad y altitud. El empuje estático publicado no debe usarse como constante para declarar una velocidad máxima. Los intervalos anteriores ya bastan para mostrar que seleccionar el motor con una sola estimación del fuselaje es insuficiente.

## Reducción de área y efectos mecánicos

Con la cola redimensionada, el modelo permite reducir a cero el área central manteniendo incidencia no mayor que 8° a unos 222, 258 y 290 km/h para 2, 5 y 10 kg. Se usa el coeficiente transversal 0,3. Son umbrales de equilibrio, no autorización de plegado ni trayectoria temporal.

El despliegue de los paneles L/D 6 añade, en la idealización radial del estudio anterior:

| Masa | Incremento de inercia de cabeceo | Incremento de inercia axial |
|---|---:|---:|
| 2 kg | 0,00108 kg·m² | 0,00217 kg·m² |
| 5 kg | 0,00631 kg·m² | 0,01261 kg·m² |
| 10 kg | 0,02474 kg·m² | 0,04949 kg·m² |

Esto cuantifica solo redistribución radial de paneles; motores, actuadores, movimiento longitudinal de piezas y cierre de masa siguen pendientes. La reorientación debe recalcularse con la inercia total y los pares realmente disponibles.

## Qué significa «mejor» en este barrido

La menor estimación superior de arrastre parcial aparece en L/D 12, el extremo del dominio, con aproximadamente 90, 162 y 253 N a 1000 km/h según masa. **Un mínimo en el borde del barrido no identifica un óptimo físico.** El modelo premia el brazo mayor de la cola, pero no resuelve la estructura y las penalizaciones completas de un cuerpo más largo.

Se construye también una frontera no dominada en tres objetivos: extremo superior de arrastre parcial, masa de piel más paneles y su inercia de cabeceo desplegada. Piel y paneles usan 1 kg/m² como referencia uniforme; su inercia incluye distribución superficial corporal, estaciones axiales y extensión de los paneles. Son indicadores geométricos, no una masa estructural dimensionada ni inercia del vehículo completo. No se ha agregado una ponderación arbitraria para proclamar un ganador.

La frontera solo vale para esta malla y estas hipótesis. Faltan ala anular, formas sustentadoras, otros sistemas de propulsión, flexión, aeroelasticidad y geometría integrada del conducto. Por ello no se convierte ninguno de sus puntos en la recomendación final del proyecto.

## Verificación y reproducción

`comparacion_integrada.py` genera `resultados/comparacion_integrada_CONDICIONAL.csv`, `resultados/comparacion_integrada_ESQUINAS.csv` y `resultados/comparacion_integrada_RESUMEN.json`. Los equilibrios reutilizan las comprobaciones de residuo de fuerza y momento de `trimado_superficies.py`. La caché geométrica añadida a ese módulo solo evita repetir integraciones idénticas.

Las fuentes y las limitaciones aerodinámicas originales están vinculadas en `TRIMADO-Y-GEOMETRIA-VARIABLE.md`; no se han introducido coeficientes nuevos como si fueran datos de túnel. Esta comparación es progreso hacia la selección, no cierre del objetivo global.
