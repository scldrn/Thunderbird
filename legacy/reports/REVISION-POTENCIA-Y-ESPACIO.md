# Revisión de potencia y separación tridimensional — versión de 5 kg

## Cambio respecto al informe anterior

El presupuesto anterior de batería mantenía congelada una cota de 5,25 kW aunque cambiaba el rotor. Era una sensibilidad, no prueba de que todas las variantes superaran5kg. Se recalcula ahora para masa fija de5kg, rotores de45,72cm, eficiencia efectiva supuesta0,65 y asignación convexa de mínimo consumo de discos aislados. No hay nueva iteración de masa con hardware completo.

## Geometría

Cuerpo de91,4×22,9cm. Centros de gravedad supuestos a5cm hacia el reactor. Dos estaciones de cuatro rotores con radio45,7cm. La disposición anterior tenía separación longitudinal36,6cm.

Se minimizó la distancia entre cada par de discos circulares orientados en3D (28pares), mediante optimización convexa sobre dos discos unitarios. A36,6cm entre estaciones los discos ideales se intersectan. A45,7cm entre estaciones, la distancia mínima entre discos es8,44cm. A54,8cm es17,58cm. Se adopta para este estudio45,7cm, centros en±0,25L.

La verificación solo cubre discos desplegados de espesor cero. No incluye brazos, flexión, estelas, motor, palas durante plegado ni transición. Eliminar intersección no demuestra ausencia de interferencia aerodinámica. La zona de toma y escape tampoco está resuelta.

## Potencia calculada

126direcciones de fuerza (26estructuradas y100aleatorias reproducibles) y7momentos por dirección (cero y±1Nm en cada eje), para tres magnitudes de fuerza:2646casos. Optimización convexa de suma de empujes absolutos elevados a1,5, con8 límites bidireccionales supuestos de40,2N. Todos los casos pasan; error máximo de equilibrio3,3e-13 en las unidades normalizadas.

| Capacidad traslacional considerada | Máximo de potencia entre muestras |
|---|---:|
| Fuerza de magnitud igual al peso | 0,86kW |
| Fuerza de magnitud1,5veces el peso | 1,55kW |
| Fuerza de magnitud2veces el peso | 2,36kW |

Las magnitudes1,5y2veces el peso permiten contener, con gravedad, conjuntos de aceleración adicional de0,5gy1g. Los números de potencia son máximos muestreados, NO cotas continuas garantizadas, ni consumo medido, ni simulación dinámica. Fuerza igual al peso más momento de control es un conjunto para estudiar estacionario/control, no equilibrio angular estático bajo momento no nulo.

El máximo muestreado de potencia de la pseudoinversa coincide con el optimizado: NO se atribuye la reducción a una mejora espectacular del controlador. Cambian diámetro, masa evaluada, reserva de momento y uso de muestras frente a sumas de cotas individuales del estudio anterior.

La verificación geométrica exacta de la bola de fuerzas del modelo da101,42N con reserva simultánea de1Nm en cualquier dirección; supera98,07N requeridos para el conjunto de1g. Con reserva2Nm queda96,35N: ya no cumple ese mismo requisito. Esto supone empuje reversible simétrico no demostrado por los motores de referencia.

## Baterías y masa restante

Referencia P50B:71g por celda y60A continuos sujetos a corte térmico80°C, según fabricante. Hipótesis de tensión bajo carga3V/celda y15% adicional de masa de pack. No se garantiza refrigeración ni compatibilidad de tensión con la tabla de empuje del motor: el empuje máximo publicado corresponde a mayor tensión y debe medirse a lo largo de la descarga.

- Para1,55kW,12S1P da0,980kg estimados si se permite superar40A/celda y mantenerse por debajo de60A. Quedan1,760kg para TODOS los elementos distintos de reactor, motores, combustible y pack.
- Para2,36kW,12S2P da1,960kg estimados y quedan0,780kg para esos elementos. Es un presupuesto estrecho: no son780g de carga útil.
- Limitar a40A/celda exige12S2P también para el caso1,55kW.

No se ha descontado del remanente hélices, ESC, bujes y servos de paso variable, cableado, estructura, depósito, bomba, electrónica, refrigeración, articulaciones ni carenados. Por tanto no hay cierre de masa aprobado. Los packs no son recomendaciones de compra.

## Decisión

Continuar comparando0,5gy1g como requisitos independientes; no reducir silenciosamente la agilidad solicitada. Priorizar curvas bidireccionales del módulo de paso variable y distribución mecánica con estaciones separadas45,7cm. La versión5kg sigue abierta; no se ha demostrado la misión600–1000km/h. La geometría compactaL/D4 es solo soporte del estudio de estacionario.

## Fuentes y reproducción

- Batería: https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-P50B-80122.pdf
- Investigación experimental sobre paso variable y empuje inverso: https://dspace.mit.edu/entities/publication/cbf41dbd-220c-4616-b300-c116ec7841be
- Motor de referencia (tabla positiva, no validación reversible): https://store.tmotor.com/product/mn5008-kv400-motor-antigravity-type.html

Código: optimizar_potencia_5kg.py y espacio_rotores.py. Datos: resultados/potencia_5kg_resumen.json, potencia_5kg_muestreo.csv y separacion_discos_5kg.json. El dibujo previo conserva las posiciones anteriores y queda superado en la separación longitudinal por este estudio.
