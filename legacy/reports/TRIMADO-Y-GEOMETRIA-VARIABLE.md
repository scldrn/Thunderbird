# Equilibrio aerodinámico y geometría variable: comparación preliminar

## Decisión que cambia con este cálculo

Las grandes fuerzas y momentos del informe anterior se calcularon a una incidencia fija de 10°. No son una exigencia inevitable del vuelo rápido. Al resolver simultáneamente sustentación y momento, una cola puede aportar sustentación mientras compensa el momento del cuerpo, y el ángulo de equilibrio disminuye al aumentar la velocidad. Por tanto, **no se justifica descartar el huso basándose únicamente en su momento a 10°**.

Se compararon tres configuraciones en 945 puntos de masa, alargamiento, velocidad y factor de carga. Se añadieron 81 escenarios de masa/inercia de superficies, una sensibilidad a su pendiente de sustentación y una reducción gradual de área. Todo es un modelo de cribado; no hay coeficientes medidos del vehículo integrado.

La hipótesis de trabajo que sale reforzada es: rotores para estacionario omnidireccional, superficies sustentadoras desplegadas durante la transición y menor área expuesta en vuelo rápido, conservando control suficiente. No se declara esta arquitectura óptima: falta comparar su masa, resistencia y fiabilidad con una transición mediante empuje orientado.

## Definición reproducible del modelo

Se usa el cuerpo esferoidal cerrado del estudio anterior, con densidad media de referencia 200 kg/m³. Sustentación y momento corporales siguen la implementación condicional de [Allen y Perkins, TR 1048](https://ntrs.nasa.gov/citations/19930090962). La cola actúa a 0,4 longitudes detrás del centro de masa; el centro aerodinámico del ala principal se sitúa idealmente sobre este centro. Se resuelven equilibrio vertical y momento de cabeceo. No se incluyen momento propio del perfil, fuerza vertical del reactor, momento debido al arrastre de la cola ni interferencia ala-cuerpo-cola. Por ello es una aproximación a pequeñas incidencias.

Las áreas siguientes corresponden a **un par de superficies opuestas en un plano**. Para una cruz completa, el área física es el doble. En el cálculo de cabeceo solo un plano produce sustentación; el otro también aporta arrastre de perfil. No se ha verificado movimiento combinado de cabeceo/guiñada ni balanceo.

| Configuración, referencia de 5 kg | Ala por plano | Cola por plano | Área física total |
|---|---:|---:|---:|
| Solo cola | 0 | 0,040 m² | 0,080 m² |
| Cruz compacta + cola | 0,040 m² | 0,040 m² | 0,160 m² |
| Cruz mayor + cola | 0,090 m² | 0,040 m² | 0,260 m² |

Para comparar tamaños se escalan áreas con masa elevada a 2/3. Esto define un experimento numérico comparable, **no una optimización independiente ya terminada**. Se evalúan masas 2, 5 y 10 kg, L/D 4, 6 y 8, siete velocidades de 100 a 1000 km/h y cinco factores de carga de 1 a 20.

Hipótesis centrales de las superficies: pendiente de sustentación 3 por radián, alargamiento equivalente 2, eficiencia inducida 0,7 y coeficiente de arrastre de perfil 0,012. Son parámetros elegidos, no resultados experimentales del diseño. Se emplea la relación clásica de arrastre inducido resumida por [NASA Glenn](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/winglets/). Aplicarla con parámetros constantes hasta Mach 0,82 es una extrapolación exploratoria; no representa arrastre de onda ni certifica capacidad transónica.

Límites arbitrarios de cribado: incidencia hasta 10°, deflexión de cola hasta 15° y magnitud de CL hasta 0,8. Cumplirlos solo significa pasar ese filtro, no demostrar vuelo seguro, estabilidad dinámica, potencia disponible o resistencia estructural.

## Equilibrio a 1 g: resultado principal

L/D 6, parámetros centrales:

| Masa y configuración | Incidencia a 150 km/h | Incidencia a 1000 km/h | Arrastre de superficies a 1000 km/h |
|---|---:|---:|---:|
| 5 kg, solo cola | 19,48°: fuera de límite | 0,564° | 45,7 N |
| 5 kg, cruz compacta | 10,83°: fuera de límite | 0,264° | 90,9 N |
| 5 kg, cruz mayor | 6,82° | 0,159° | 147,5 N |
| 10 kg, solo cola | 23,84°: fuera de límite | 0,708° | 72,7 N |
| 10 kg, cruz compacta | 13,43°: fuera de límite | 0,333° | 144,4 N |
| 10 kg, cruz mayor | 8,53° | 0,200° | 234,3 N |

Estos arrastres excluyen cuerpo, tomas, base, rotor plegado, juntas y compensación de efectos no modelados. No se pueden comparar directamente con empuje nominal para declarar una velocidad máxima.

En el caso de 5 kg con solo cola a 1000 km/h, el momento corporal en equilibrio baja a 23,25 N·m, frente a los 402,6 N·m del cuerpo a 10°. La cola lo compensa en el modelo. Con la cruz mayor, la incidencia menor reduce ese momento a 6,54 N·m. Esto corrige la interpretación de la etapa anterior, sin convertir estos números en prestaciones verificadas.

La cruz mayor facilita el equilibrio temprano, pero mantenerla desplegada hasta 1000 km/h resulta costoso en esta hipótesis. Suprimir el área central ahorraría unos 102 N en 5 kg y 162 N en 10 kg de arrastre estimado de superficies. La ganancia real debe restar el arrastre residual de alojamientos y mecanismos y contabilizar su masa.

## Reducción de área: cuándo existe equilibrio en el modelo

Se calculó el área central mínima necesaria para mantener incidencia no superior a 8° mientras se conserva la cola. No es una trayectoria temporal: no incluye flujo sobre rotores, transitorios de retracción, cambios de centro de masa ni aceleración.

| Masa | Velocidad calculada a partir de la cual el área central puede ser cero |
|---|---:|
| 2 kg | 214 km/h |
| 5 kg | 250 km/h |
| 10 kg | 280 km/h |

Estas velocidades son umbrales algebraicos para la configuración con cola del presente modelo, **no velocidades autorizadas de plegado**. Los umbrales de 478–625 km/h del estudio anterior correspondían al cuerpo solo, sin esta cola sustentadora; no son resultados incompatibles.

En 10 kg, a 150 km/h ni la cruz mayor satisface el objetivo más estricto de 8° bajo la hipótesis central, aunque sí pasa el límite exploratorio de 10°. Haría falta más velocidad, más área efectiva o apoyo adicional para cumplir aquel objetivo.

## La estabilidad todavía depende de un dato no medido

Con pendiente de sustentación 3 por radián, la derivada estática de cabeceo calculada resulta estabilizadora para los ejemplos de la tabla. Al reducir esa pendiente a 2 por radián, la misma cola deja de compensar la derivada desestabilizadora del cuerpo. Con 4 vuelve a ser estabilizadora. La incertidumbre en la aerodinámica de la cola cambia, por tanto, la decisión de estabilidad.

No basta con encontrar una posición de equilibrio ni con colocar el centro de presión cerca del centro de masa. Deben medirse o calcularse las derivadas alrededor del equilibrio, el amortiguamiento, la autoridad del actuador y sus márgenes. Tampoco se deduce estabilidad de guiñada/balanceo de este cálculo de cabeceo.

La literatura sobre [combinaciones cruciformes ala-cuerpo](https://ntrs.nasa.gov/api/citations/19930082875/downloads/19930082875.pdf) identifica precisamente las interferencias como parte del problema; no se han incorporado coeficientes de ese informe sin verificar su correspondencia geométrica.

## Efecto mecánico cuantificado

Escenario de paneles rectangulares de 5 kg, L/D 6, masa superficial supuesta 1 kg/m². Cada panel se extiende desde el radio corporal. La comparación plegado/desplegado conserva la estación axial y sustituye la distribución radial plegada por una idealización en el radio del cuerpo. No es una cinemática de plegado diseñada.

| Configuración | Masa solo de paneles | Incremento de inercia de cabeceo | Incremento de inercia axial |
|---|---:|---:|---:|
| Solo cola | 0,080 kg | 0,00083 kg·m² | 0,00166 kg·m² |
| Cruz compacta + cola | 0,160 kg | 0,00166 kg·m² | 0,00333 kg·m² |
| Cruz mayor + cola | 0,260 kg | 0,00409 kg·m² | 0,00817 kg·m² |

No incluyen bisagras, actuadores, cierres, cableado ni refuerzos. Con masas superficiales de 0,5 o 2 kg/m², esos resultados se reducen a la mitad o se duplican. Para convertirlos en tiempo de reorientación hay que incorporarlos a la inercia total y al par disponible del vehículo, no usarlos aisladamente.

La cruz mayor del escenario tiene semienvergadura expuesta de 0,212 m y cuerda 0,212 m por panel; diámetro exterior aproximado 0,624 m. La cola tiene semienvergadura/cuerda 0,141 m y diámetro exterior 0,482 m. Son dimensiones para estudiar fuerzas y empaquetado, no geometría transónica optimizada ni CAD validado.

Como sensibilidad estructural, una diferencia uniforme de coeficiente de presión de 1 a la presión dinámica de 1000 km/h daría unos 226 N·m sobre la bisagra de raíz de un panel central y 67 N·m sobre uno de cola, suponiendo eje de plegado longitudinal y carga uniforme. **No son pares del servo de control ni cargas predichas de vuelo**: muestran la escala que pueden alcanzar las cargas de un mecanismo expuesto. Cierres estructurales, deflexión, flutter y fatiga siguen sin dimensionar.

## Ala anular: evidencia conservada, selección pendiente

[NACA TN 4117](https://digital.library.unt.edu/ark:/67531/metadc56676/) ensayó cinco alas anulares de igual área proyectada y alargamientos entre 1/3 y 3. Encontró ventajas de relación sustentación/arrastre frente a alas rectangulares específicas por debajo de alargamiento 2,4. Ese resultado justifica mantener el anillo como candidato; no demuestra que supere a esta aeronave completa en transónico, masa o transición.

No se asigna al anillo el CL de un ala plana ni se compara su superficie mojada con el área proyectada de otra geometría. Falta una comparación normalizada con sus polares, diámetro exterior, interferencia con el fuselaje y masa de soporte. La sección circular exterior por sí sola tampoco proporciona fuerza aerodinámica en estacionario.

## Verificación y archivos

Se resolvieron 705 raíces de equilibrio dentro del intervalo matemático de búsqueda de 0–60°; 240 puntos no tenían raíz en ese intervalo. Una raíz por encima de los límites aerodinámicos se etiqueta como fuera de límites y no como vuelo viable. El residuo máximo numérico de las ecuaciones resueltas fue inferior a 1,2×10⁻⁸ en las unidades correspondientes. Esto comprueba el equilibrio matemático, no la validez física del modelo.

- `trimado_superficies.py`: código reproducible.
- `resultados/trimado_superficies_CONDICIONAL.csv`: 945 casos y filtros.
- `resultados/mecanismos_superficies_CONDICIONAL.csv`: 81 escenarios mecánicos.
- `resultados/trimado_superficies_RESUMEN.json`: selección, sensibilidad y reducción de área.
- `resultados/trimado_superficies.png`: comparación visual; trazo punteado fuera de límites supuestos.

El siguiente cierre necesita coeficientes integrados y mapas en avance, con presupuesto de masa revisado. El objetivo global continúa abierto: ninguna de estas comparaciones demuestra todavía que la arquitectura sea la mejor posible ni que cumpla toda la misión.
