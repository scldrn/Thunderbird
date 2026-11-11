# Pala de referencia para evaluación aerodinámica y mecánica

## Geometría propuesta, no plano de fabricación

Rotor de dos palas, diámetro457,2mm, comienzo aerodinámico a40mm del eje, cuerda constante35mm, sin torsión geométrica y paso colectivo variable. Perfil simétrico NACA0012 como candidato geométrico; eje de paso al25% de cuerda. Masa15g por pala es una hipótesis para cargas, NO una masa estructural conseguida. Espesor máximo geométrico del perfil:4,2mm, que no equivale a espesor de pared ni determina un laminado.

La ausencia de torsión simplifica el estudio de inversión simétrica de paso. No se demuestra simetría real del empuje: estelas, hub y mecanismos pueden romperla. Se requiere validar ambos sentidos.

## Modelo y límites

Se evaluaron54casos: tres cuerdas25/35/45mm, tres regímenes6000/7000/8000rpm, dos empujes29,68/38,94N y tres límites supuestos de sustentación seccional0,7/0,9/1,1.

Modelo de elementos de pala con velocidad inducida uniforme obtenida del disco actuador en estacionario. Incluye arrastre de perfil y componente inducida del par. Polar SINTÉTICA: pendiente5,5/rad, CL recortado al límite supuesto, CD=0,02+0,03CL². No son polares medidas deNACA0012. El recorte no representa separación real: los casos con secciones recortadas son señales de incertidumbre, no soluciones aerodinámicas validadas.

No incluye pérdidas de punta, rotación de estela, compresibilidad, interacción entre rotores ni deformación. Refinamiento de500a1000estaciones radiales cambia potencia menos de0,1% en los casos comprobados; consistencia numérica, no exactitud física.

UIUC ofrece datos experimentales de bajo Reynolds; hace falta identificar una polar adecuada antes de aprobar perfil. No se usaron sus datos en este cálculo: https://m-selig.ae.illinois.edu/pd.html

Las referencias habituales de validaciónNACA0012 a millones de Reynolds no deben aplicarse directamente aquí: https://tmbwg.github.io/turbmodels/naca0012_val.html

## Resultados para cuerda35mm y6000rpm

| Magnitud | Rama0,5g del vehículo | Rama1g del vehículo |
|---|---:|---:|
| Empuje objetivo de un rotor | 29,68N | 38,94N |
| Paso colectivo estimado | 9,61° | 11,77° |
| Potencia mecánica de eje | 458W | 623W |
| Potencia eléctrica, eficiencia supuesta85% | 539W | 733W |
| Par de eje | 0,729Nm | 0,992Nm |
| Par de servo estimado | 0,288Nm | 0,335Nm |
| Recorrido completo entre pasos opuestos | 19,23° | 23,54° |
| Tiempo cinemático ideal del servo con reducción0,5 | 45ms | 55ms |

Los tiempos usan la velocidad publicada0,07s/60° del servo a8,4V y NO incluyen carga, respuesta del motor, asentamiento ni dinámica de estela. No contradicen los117ms anteriores: aquel cálculo suponía recorrer50° de paso, este estima un recorrido menor. Falta medir la curva conjunta par/velocidad del servo y el empuje transitorio.

Reynolds local aproximado64.000–345.000; Mach periférico0,42. Fuerza centrífuga por pala795N, con masa uniforme15g. La raíz aerodinámica pasó de25a40mm: por eso cambia la fuerza respecto al informe anterior. El par de paso incorpora masa centrada a media cuerda respecto al eje al25%, que eleva la contribución centrífuga. Se agrega incertidumbre de momento seccional|Cm|=0,03, fricción supuesta y término inercial; no es una historia temporal acoplada.

## Comparación y decisión

Cuerda25mm a6000rpm exige recortarCL en aproximadamente32% del tramo para el caso39N yCLmáx0,9: no se retiene como referencia principal. A7000rpm evita ese recorte pero aumenta fuerza centrífuga y velocidad periférica. Cuerda45mm aumenta par de paso y pérdidas de perfil. Cuerda35mm a6000rpm es un compromiso provisional de esta malla, no un óptimo global. ConCLmáx0,7, alrededor22% del tramo se recorta en el caso39N: la polar real puede cambiar la decisión.

El MN5008KV170 usado antes publica720W como potencia máxima de180s. La estimación733W eléctricos por rotor para39N no deja margen y no justifica conservarlo. La incertidumbre del modelo impide afirmar una imposibilidad definitiva, pero obliga a comparar motor/bobinado mayor o cambiar pala/diámetro. Fuente de motor: https://store.tmotor.com/product/mn5008-kv400-motor-antigravity-type.html

No multiplicar733W por ocho y llamarlo consumo de la maniobra: los ocho rotores no están necesariamente al máximo simultáneamente. Sí hay que reemplazar el modelo de potencia del asignador por mapas de esta pala para reconstruir el presupuesto eléctrico. A paso cero y régimen alto hay consumo de perfil, ausente del modelo ideal de potencia inducida previo.

## Qué queda concretamente abierto

1. Polar real del perfil en el rango local deRe yMach, incluyendo transición y pérdida.
2. Geometría y material que alcancen masa y resistencia, incluida retención de raíz y fatiga.
3. Mapa de motor a tensión mínima, con par de eje cercano a1Nm.
4. Mapa de potencia y empuje inverso, y respuesta del servo bajo carga.
5. Recalcular masa, potencia conjunta e inercia al sustituir el motor.

La pala de referencia está definida para simulación y comparación. No está dimensionada para fabricación ni validada estructuralmente.

Reproducción: pala_referencia.py. CSV completo y resumenJSON en resultados/pala_referencia_ESCENARIOS.csv y pala_referencia_resumen.json.
