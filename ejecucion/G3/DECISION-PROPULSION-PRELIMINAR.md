# G3 — Propulsión axial: decisión preliminar

Fecha: 2026-11-04. Alcance: comparación conceptual para C02 de 5 kg, con referencias para 2 y 10 kg. **No es una selección de motor ni demuestra que el vehículo pueda volar a 600–1000 km/h.** La arquitectura seleccionada mantiene ventiladores internos para estacionario; el propulsor axial es una función separada todavía por resolver.

## Decisión de trabajo

Estudiar en paralelo dos rutas de avance: un ventilador eléctrico entubado (EDF), como candidato para un demostrador de menor velocidad, y un microturborreactor, como candidato al estudio de alta velocidad. La arquitectura mixta combinaría ventiladores eléctricos internos para estacionario con un reactor alimentado por combustible para avance; necesita ambos sistemas de energía. No hay datos suficientes para declarar ganadora ninguna ruta, ni para concluir que el peso, la autonomía o la aceleración caben en 5 kg.

La comparación requiere **empuje neto instalado frente a velocidad**, potencia y energía de misión, no solo empuje de banco. En particular, los ensayos de NASA de un EDF miden variaciones con velocidad de ventilador, tensión, presión dinámica y ángulo de incidencia; corresponden a un túnel de baja velocidad y no validan extrapolación a Mach 0,82. [NASA NTRS, caracterización experimental de EDF](https://ntrs.nasa.gov/citations/20230017299).

## Comprobación geométrica y datos de ficha

**Dato del proyecto:** `configuraciones/C02_CANDIDATA.json` y la lista de piezas de C02 reservan un corredor axial de Ø exterior 60 mm e interior 56 mm; el corredor es una reserva, no un motor instalado. Hay que volver a comprobarlo en el CAD vigente antes de hacer un cambio de arquitectura.

| Referencia | Valor declarado por fabricante | Consecuencia para el corredor de Ø56 mm |
|---|---|---|
| [Xicoy X50](https://www.xicoyturbines.com/X50.html) | Turborreactor; Ø59,8 × 158 mm; 385 g motor, 463 g peso instalado declarado sin batería; 25–50 N; 160 g/min a 50 N. | El diámetro nominal supera el espacio interior en 3,8 mm. No cabe incluso antes de considerar holguras, tomas, soportes o aislamiento térmico. |
| [Xicoy X52](https://www.xicoyturbines.com/page29.html) | Ø59,8 × 158 mm; 385 g motor, 463 g peso instalado declarado sin batería; 25–52 N; 160 g/min a 52 N. | Mismo conflicto geométrico nominal. |
| [JetCat P20 SX](https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/Eingestellte%20Produkte%20Zubehoer/p20_sx) | Referencia histórica descatalogada: Ø60 × 171 mm, 350 g motor, 24 N, 90 mL/min a régimen máximo. | Excede el diámetro interior por 4 mm; tampoco es una propuesta de compra. |

Los 463 g son el alcance de peso indicado por Xicoy, **no una medición del sistema completo en C02**. Falta demostrar depósito, batería, combustible, tomas, escape, aislamiento y compatibilidad con el resto del vehículo. Las cifras de empuje son valores de ficha: no se conoce aquí su mapa completo a velocidad y configuración instalada; no deben compararse directamente con el arrastre calculado en vuelo.

## Ejemplo de masa de combustible — cálculo, no diseño

Supuestos exclusivamente ilustrativos: X50 a 160 g/min constantes durante todo el intervalo; se suman 0,463 kg de la ficha y el combustible consumido, sin extrapolar comportamiento ni autonomía real. El fabricante especifica queroseno con 4 % de aceite; no se agrega otra masa de aceite en este ejemplo porque no se ha aclarado su tratamiento en el caudal publicado. [Ficha X50](https://www.xicoyturbines.com/X50.html).

| Tiempo a ese consumo | Combustible | Paquete de ficha + combustible | Fracción de 2 / 5 / 10 kg |
|---:|---:|---:|---:|
| 30 s | 0,080 kg | 0,543 kg | 27,2 / 10,9 / 5,4 % |
| 2 min | 0,320 kg | 0,783 kg | 39,2 / 15,7 / 7,8 % |
| 5 min | 0,800 kg | 1,263 kg | 63,2 / 25,3 / 12,6 % |

No incluye batería, depósito ni complementos no identificados. Es la **misma referencia comercial**, no un dimensionamiento de motores para las tres masas. Consumo real varía con el punto de operación; no es una predicción de recorrido.

## Potencia y empuje: límites de lo que se sabe

En vuelo rectilíneo estacionario, con un arrastre total supuesto `D` y velocidad `V`, la potencia útil de avance es `D·V`; la potencia eléctrica o química de entrada es mayor si la eficiencia global es menor que uno. Valores de sensibilidad, sin atribuirlos al CAD ni a un motor concreto:

| Arrastre supuesto | 600 km/h | 1000 km/h |
|---:|---:|---:|
| 10 N | 1,67 kW | 2,78 kW |
| 20 N | 3,33 kW | 5,56 kW |
| 50 N | 8,33 kW | 13,89 kW |

La fuerza neta del propulsor depende de la cantidad de movimiento del aire entrante y saliente y, cuando corresponda, del término de presión; entrada, escape y vehículo deben contabilizarse con una convención consistente para no contar pérdidas dos veces. [NASA, modelos de propulsión NDARC](https://rotorcraft.arc.nasa.gov/Publications/files/NDARC_propulsion_johnson.pdf); [NASA, exceso de empuje](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/excess-thrust-thrust-drag/).

## Siguientes verificaciones y criterios de selección

1. Congelar envolvente geométrica real del eje y evaluar una variante de corredor mayor con admisión, escape y protección térmica; no basta pasar de Ø56 a Ø60 mm.
2. Para ambos candidatos, obtener mapas verificables de empuje neto, consumo y potencia frente a velocidad, densidad y mando, además de masas y dimensiones **instaladas**. Si faltan, mantener intervalos y sensibilidad, sin declarar viabilidad.
3. Cerrar misión de referencia y presupuesto integrado para 2, 5 y 10 kg: energía, combustible, alimentación eléctrica de ventiladores de estacionario, estructura, controles y margen de masa. El vehículo de 2 kg necesita un dimensionamiento propio; no se supone que esta microturbina sirva.
4. Modelar transiciones y autoridad de control con márgenes conservadores; el reactor axial por sí solo no acredita vuelo estacionario ni movimiento omnidireccional. Validar interferencia de flujos entre sistemas y temperaturas.

Hasta terminar estas verificaciones, el EDF y el microturborreactor son **alternativas de investigación**, no componentes seleccionados ni promesas de velocidad.
