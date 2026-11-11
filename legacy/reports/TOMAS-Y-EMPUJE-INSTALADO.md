# Tomas, conductos y contabilidad del empuje

## Resultado

Se pueden dimensionar secciones preliminares de paso compatibles con los caudales publicados. Esto no cierra la integración: faltan labio de entrada, recuperación real, distorsión, refrigeración, escape y mapa del motor. El empuje estático de catálogo no basta para comprobar 600–1000 km/h.

Se calcularon 216 condiciones de conducto y 36 requisitos de empuje bruto. Los resultados distinguen sección física de paso, tubo de corriente capturado, empuje bruto y empuje neto. No hay una predicción validada de velocidad máxima.

## Datos primarios utilizados

| Referencia | Caudal publicado | Empuje máximo de referencia |
|---|---:|---:|
| [JetCat P20-SX](https://www.jetcat.de/changelang/de/en/productdetails/produkte/jetcat/produkte/Eingestellte%20Produkte%20Zubehoer/p20_sx) | 0,05 kg/s | 24 N |
| [JetCat P100-RX-BL](https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/RC%20ENGINES/Engines/p100_rx-bl) | 0,23 kg/s | 100 N |
| [JetCat P250-Pro-S, versión histórica](https://www.jetcat.de/de/productdetails/produkte/jetcat/produkte/Eingestellte%20Produkte%20Zubehoer/p250%20pro%20s) | 0,47 kg/s | 250 N |

Se usa el caudal publicado como caudal de aire de referencia. No se mezcla la ficha histórica del P250-Pro-S con especificaciones de revisiones V2/R2. Los modelos históricos sirven de referencia física, no de recomendación de compra o disponibilidad actual. Tampoco se presupone que el caudal publicado permanezca constante al variar las condiciones de entrada.

Las ecuaciones de continuidad compresible se contrastaron con [NASA, caudal másico](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/mass-flow-rate-equations/). La distinción entre empuje bruto, término de entrada y empuje neto sigue [NASA, ecuación de empuje](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/thrust-force/). Las condiciones a la cara del compresor dependen de la entrada y del flujo libre, como resume [NASA, ecuaciones del motor](https://www.grc.nasa.gov/www/k-12/VirtualAero/BottleRocket/airplane/thsum.html).

## Hipótesis del cálculo

Atmósfera a nivel del mar, 288,15 K y 101325 Pa; aire ideal con relación de calores 1,4. Velocidades 0, 150, 600 y 1000 km/h; recuperación supuesta de presión total 90%, 95% o 100%; Mach local elegido para el conducto 0,15, 0,25 o 0,40.

Se comparan dos hipótesis de operación: caudal nominal fijo y caudal corregido constante respecto de las condiciones totales de entrada. La segunda es una sensibilidad de semejanza, no una línea de operación del compresor: no resuelve velocidad corregida, control, bombeo, temperatura límite ni acoplamiento turbina-compresor.

El conducto se trata como una sección unidimensional uniforme. Se comprueba capacidad sónica, pero no se simulan fricción, curvatura, capa límite, distorsión o flujo separado. La recuperación es una entrada del estudio, no una propiedad demostrada de la forma propuesta.

## Sección de paso: ejemplo a Mach local 0,25

Caudal nominal fijo y recuperación 95%:

| Motor | Diámetro circular equivalente en estacionario | A 1000 km/h |
|---|---:|---:|
| P20-SX | 25,8 mm | 21,4 mm |
| P100-RX-BL | 55,4 mm | 45,9 mm |
| P250-Pro-S | 79,2 mm | 65,7 mm |

Son áreas libres de paso expresadas como diámetro equivalente. **No son el diámetro exterior del motor, el labio de toma ni una tobera diseñada.** Que el cálculo con caudal fijo dé menor área en avance se debe al cambio de condiciones totales; no demuestra que convenga cerrar físicamente la toma.

La columna de tubo de corriente capturado del CSV corresponde al área equivalente lejos de la entrada para suministrar el caudal a velocidad libre. No debe emplearse como tamaño directo del labio. En estacionario esa construcción no tiene área finita definida mediante velocidad libre cero: el motor induce el flujo y el código deja el dato vacío.

## Ejemplo anular alrededor de un núcleo

Se tomó, solo como prueba de espacio, un núcleo de diámetro igual a la mitad del diámetro exterior del cuerpo L/D 6 asociado a cada masa: 2, 5 y 10 kg. Para el caso anterior, la separación radial libre necesaria sería:

| Motor/masa de referencia | En estacionario | A 1000 km/h |
|---|---:|---:|
| P20 / 2 kg | 2,2 mm | 1,5 mm |
| P100 / 5 kg | 7,2 mm | 5,0 mm |
| P250 / 10 kg | 11,4 mm | 8,1 mm |

Estas holguras solo representan área geométrica neta. Un paso anular tan estrecho puede perder una fracción relevante de su área efectiva por paredes, soportes y capas límite; la cifra no prueba que la solución sea realizable. Tampoco confirma que el núcleo aloje batería, depósito y mecanismos. Las dimensiones deben recalcularse a lo largo de todo el conducto y con el área bloqueada real.

## Empuje bruto requerido: por qué el catálogo no cierra la misión

Con caudal nominal fijo, el término de cantidad de movimiento del aire entrante a 1000 km/h es 13,9, 63,9 y 130,6 N para los tres motores. Este término ya forma parte de la definición de empuje neto; **no debe restarse otra vez a un mapa de empuje neto instalado**.

Al añadirlo al intervalo de arrastre parcial de la comparación integrada L/D 6, resulta el siguiente requisito de empuje bruto, incluyendo en ese concepto la contribución de presión de salida:

| Masa/motor de referencia | Empuje bruto requerido a 1000 km/h |
|---|---:|
| 2 kg / P20 | 79–130 N |
| 5 kg / P100 | 179–273 N |
| 10 kg / P250 | 310–458 N |

Son requisitos derivados de hipótesis de arrastre y caudal; no prestaciones de esos motores. El arrastre sigue siendo parcial y no incluye tomas, base, onda e interferencias. Tampoco son intervalos estadísticos.

El CSV incluye una columna que resta el término de entrada al empuje estático suponiendo empuje bruto invariable. **Es una sensibilidad deliberada, no una predicción de empuje en vuelo.** El avance puede cambiar presión total, caudal y condiciones de expansión, por lo que no es válido concluir a partir de esa columna cuánto empuje real queda disponible.

## Consecuencias para la forma

- El cuerpo cerrado usado como referencia aerodinámica debe convertirse en un volumen con entrada y salida reales. Su área exterior, base y distribución interna ya no son las del esferoide cerrado.
- La suavidad de la sección exterior no garantiza un conducto de baja pérdida: área interior, curvatura, labio, incidencia y distorsión son problemas adicionales.
- La toma debe funcionar durante estacionario y transición, cuando la dirección del flujo puede diferir mucho del eje corporal. El presente cálculo es axial y no demuestra esa capacidad.
- La salida exige geometría y protección térmica compatibles con el reactor y con los rotores desplegados. No se dimensiona una nueva tobera a partir del diámetro del conducto de entrada.

Estas condiciones impiden cerrar el motor y sus dimensiones externas únicamente con el mejor alargamiento del estudio de fuselaje.

## Verificación y entregables

`tomas_y_empuje.py` comprueba que cada sección reproduce el caudal introducido, que su área supera la crítica para la condición total elegida y que el flujo másico por unidad de área alcanza el máximo local a Mach 1. Eso verifica la implementación unidimensional, no la recuperación ni el empuje instalado.

- `resultados/tomas_dimensionamiento_CONDICIONAL.csv`: 216 condiciones.
- `resultados/empuje_bruto_requerido_CONDICIONAL.csv`: 36 requisitos.
- `resultados/tomas_y_empuje_RESUMEN.json`: selección, datos de motores y procedencia.

El siguiente cierre necesita un mapa de motor compatible con presión/temperatura de entrada, una geometría integrada y cálculo o ensayo de toma/escape. Sin esos datos no se puede certificar 600–1000 km/h ni seleccionar una arquitectura ganadora. El objetivo global permanece abierto.
