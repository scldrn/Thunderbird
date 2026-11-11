# Requisito de paso para invertir la aceleración

Se estudia el candidato de masa provisional 5,498 kg con el mapa restringido −28 a +38 N, 6000 rpm, par de reacción incluido y orientación del cuerpo fija: gravedad en −z, x longitudinal e y lateral. En cada ensayo se cambia la aceleración neta de −a a +a sobre un eje, manteniendo equilibrio de momento en los dos extremos. Esto invierte una aceleración, NO invierte instantáneamente una velocidad del vehículo.

## Cálculo y optimización

Se buscan simultáneamente los dos repartos de ocho empujes para minimizar el mayor cambio de ángulo de paso entre extremos. `requisito_inversion_paso.py` emplea selección entera de tramos del mapa y `transicion_paso_local.py` aporta soluciones locales verificadas. El problema global alcanzó su límite de 20 segundos en cada caso: no se proclama optimalidad. En dos casos no encontró una solución entera dentro de ese tiempo; posteriormente sí se encontraron soluciones locales, por lo que no se interpretan como inviables.

Las mejores soluciones factibles aquí informadas son las de la búsqueda local. Para a=1 g, las cotas globales inferiores disponibles son 7,016° (x), 7,239° (y) y 8,692° (z); los recorridos factibles de la tabla son cotas superiores del mínimo. No se ha demostrado el recorrido mínimo exacto.

| Eje | Inversión de aceleración neta | Mayor cambio de paso factible | Tiempo ideal de recorrido a 300°/s |
|---|---|---:|---:|
| x | −0,5 g → +0,5 g | 3,381° | 11,27 ms |
| y | −0,5 g → +0,5 g | 3,501° | 11,67 ms |
| z | −0,5 g → +0,5 g | 4,306° | 14,35 ms |
| x | −1 g → +1 g | 7,089° | 23,63 ms |
| y | −1 g → +1 g | 7,254° | 24,18 ms |
| z | −1 g → +1 g | 9,889° | 32,96 ms |

300°/s es una velocidad HIPOTÉTICA en el eje de paso de la pala bajo carga, no la velocidad declarada o medida de un servo. Estos tiempos son solamente recorrido/velocidad para los extremos escogidos. Omiten latencia, aceleración y frenado del mecanismo, saturación de par, elasticidad, realimentación, dinámica de flujo y variación de RPM. No son tiempos de respuesta del vehículo ni demuestran que el movimiento a esa velocidad sea realizable. Una transmisión entre servo y pala modifica velocidad, par y recorrido; no está diseñada aquí.

## La transición lineal de paso no mantiene el equilibrio

Se recorrieron 101 fracciones entre los ángulos iniciales y finales, interpolando simultáneamente los ocho pasos. Se reconstruyeron empuje y par mediante el mismo mapa cuasiestático, y se compararon con la fuerza interpolada deseada y momento cero.

| Caso | Máximo error de fuerza muestreado | Máximo momento no deseado muestreado |
|---|---:|---:|
| x, ±0,5 g | 0,435 N | 0,0555 N·m |
| y, ±0,5 g | 0,407 N | 0,0420 N·m |
| z, ±0,5 g | 0,681 N | 0,0503 N·m |
| x, ±1 g | 3,715 N | 0,7284 N·m |
| y, ±1 g | 3,283 N | 0,1436 N·m |
| z, ±1 g | 10,172 N | 2,9440 N·m |

Estos son máximos sobre una malla, no cotas certificadas sobre todo el recorrido. El caso vertical ±1 g pasa de fuerza neta propulsiva cero (aceleración descendente gravitatoria) a dos veces el peso; no es vuelo estacionario en ambos extremos.

Las desviaciones anteriores invalidan la idea de mandar simplemente dos posiciones y esperar orientación fija durante el cambio. Se requiere una trayectoria coordinada o control de momento durante la transición. No se integra aquí el movimiento real del cuerpo: eso exigiría cerrar el controlador y la dinámica de actuadores y flujo.

## Evidencia y límites

Los dos extremos de cada solución local satisfacen el equilibrio normalizado con residuo máximo aproximadamente 1,60e-10. Datos completos: `masas_distribuidas/transicion_paso_LOCAL.json`; búsqueda global y cotas: `masas_distribuidas/inversion_paso_REQUISITOS.json`. El mapa de ángulo de paso es monótono en el dominio empleado y se invierte por interpolación a tramos.

Los recorridos dependen del mapa aerodinámico condicional: no son todavía especificaciones de fabricación del buje. No hay datos suficientes para aprobar un servo o prometer movimientos abruptos sin dificultad. El cálculo establece un requisito y detecta un error transitorio que debe resolverse antes de evaluar la maniobra física.
