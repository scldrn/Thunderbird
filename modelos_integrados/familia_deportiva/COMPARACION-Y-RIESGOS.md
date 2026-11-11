# Comparación y riesgos de la familia deportiva

Evaluación preliminar de los CAD actuales. Fuentes y archivos consultados: ensamblajes STEP de `familia_deportiva/`, generadores `familia_deportiva.py` y `diseno_industrial_v2.py`, y referencias técnicas enlazadas al final. Ninguna variante tiene resistencia ambiental, velocidad máxima o agilidad dinámica verificadas. Los cálculos de configuraciones anteriores no se transfieren a estas carrocerías.

## Dictamen

A (integración interna) es la candidata de desarrollo preferida si se priorizan volumen exterior compacto y protección de módulos, CONDICIONADA a resolver tomas/salidas y vectorización. No es un ganador de rendimiento demostrado. C es un comparador conveniente para simulación por su integración fija y acceso a los módulos. B se conserva como alternativa si el aumento de área propulsiva o la separación de regímenes justifica la masa, los cierres y el riesgo de transición. No se puede prometer «cualquier condición»; debe definirse una envolvente de funcionamiento con límites.

## Tabla comparativa

Las dimensiones y áreas siguientes proceden del CAD; las valoraciones cualitativas son inferencias de ingeniería, no datos de túnel ni probabilidades. El área frontal y el coeficiente de arrastre NO se deducen de la anchura máxima.

| Criterio | A: integración interna | B: retráctil | C: conductos carenados |
|---|---|---|---|
| Anchura máxima del ensamblaje | 322 mm | 322 mm guardado; 645 mm desplegado | 446 mm |
| Longitud máxima | 1345 mm | 1345 mm | 1345 mm |
| Discos representados | 4, diámetro real de punta aprox. 82 mm | 4, diámetro aprox. 98 mm | 4, diámetro aprox. 108 mm |
| Área geométrica total de discos | 0,02114 m² | 0,03018 m² | 0,03666 m² |
| Capacidad omnidireccional a orientación fija, tal como están dibujados | No; falta empuje lateral independiente | No; falta empuje lateral independiente | No; falta empuje lateral independiente |
| Potencial de reducir arrastre en crucero | Favorable si se cierran/gestionan los pasos; compuertas y propulsión axial aún ausentes en este CAD | Favorable una vez guardado y cerrado; transición y cierre sin validar | Conductos permanentemente expuestos; carenado y flujo transversal exigen atención |
| Protección frente a contacto exterior | Módulos dentro del cuerpo; entradas siguen abiertas | Dentro al guardar; más exposición y uniones al desplegar | Protección periférica del conducto; caras abiertas |
| Mecanismos adicionales | Compuertas/vectorización previstas, no dimensionadas | Guías, cierres, accionamiento y detección de posición; mayor complejidad de las tres propuestas | Integración fija; menor complejidad de retracción |
| Giro a baja velocidad | Masa próxima al cuerpo puede favorecer inercia; faltan pares y masas reales | Más brazo de palanca al desplegar, pero también mayor inercia: no garantiza mayor agilidad | Compromiso entre brazo e inercia; sin evaluación dinámica equivalente |
| Viento, lluvia, polvo y frío | No calificado; depende de flujo, drenaje y protección de entradas | No calificado; añade sensibilidad de guías/cierres a contaminación | No calificado; labios, rejillas y módulos expuestos |
| Mantenimiento/acceso, inferido | Menos directo por instalación interna | Depende del mecanismo y acceso a casetes | Acceso visual más directo a módulos externos |
| Velocidad de 600–1000 km/h | No demostrada | No demostrada | No demostrada |
| Papel recomendado | Candidata de producto a desarrollar | Alternativa condicionada a justificar mecanismos | Comparador inicial de simulación |

Diámetros calculados desde los vértices de las palas, respecto al centro de cada rotor. No se confunden el radio del conducto ni el parámetro nominal del generador con el radio real de punta. La disposición de cuatro rotores paralelos da rango uno para fuerzas en el sistema del cuerpo; cuatro mandos escalares no ofrecen seis fuerzas/momentos independientes. El cálculo de rango se conserva en `comparacion_cuantitativa.json`; el fundamento general está en Brescianini y D'Andrea [1]. Un sistema vectorial adicional podría cambiarlo, pero aún no está representado funcionalmente.

## Tabla de riesgos

Prioridad es un juicio de revisión, no probabilidad de fallo: **bloqueante** impide afirmar que se cumple el objetivo; **alta** exige análisis específico antes de seleccionar arquitectura. Sin datos de materiales, tolerancias, componentes y entorno, no se asignan frecuencias o porcentajes inventados.

| Riesgo | A | B | C | Prioridad y acción para cerrarlo |
|---|---|---|---|---|
| No generar fuerzas y momentos independientes | Ejes paralelos | Ejes paralelos | Ejes paralelos | Bloqueante: diseñar vectorización/canales y verificar autoridad continua y saturaciones |
| Empuje o energía insuficientes | Menor área de discos de estos CAD; pérdidas internas desconocidas | Área intermedia; masa del mecanismo desconocida | Mayor área de estos CAD; pérdidas de conductos desconocidas | Bloqueante: mapas de fuerza/par/potencia y cierre de masa/energía para el MISMO modelo |
| Cargas a alta velocidad, vibración y flutter | Bordes de entradas, paneles y posibles compuertas | Tapas, guías, cierres y estado accidentalmente desplegado | Carenados, labios y anclajes expuestos | Bloqueante: CFD, cargas estructurales y aeroelasticidad; no basta forma afilada |
| Ingestión de agua, hielo, polvo o partículas | Entradas internas pueden ingerir contaminantes | Riesgo de ingestión y además atasco de guías/cierres | Ingestión por bocas expuestas | Alta: especificar entorno; estudiar separación, drenaje, erosión y protección contra hielo |
| Viento cruzado y ráfagas | Flujo de entrada y reparto entre canales | Flujo y momentos durante despliegue | Flujo asimétrico en labios externos | Alta: simular incidencia oblicua, distorsión, reservas de control y ráfagas [2] |
| Retracción o compuerta trabada | Aplica si se añaden compuertas/vectorización | Riesgo propio central; un atasco asimétrico puede alterar control y arrastre | No hay retracción; persisten otros actuadores y fallos | Alta: verificar estados de fallo y trayectoria completa bajo cargas, sensores y enclavamientos |
| Falla de un motor, controlador o alimentación | Tolerancia a fallo no demostrada | Tolerancia a fallo no demostrada | Tolerancia a fallo no demostrada | Bloqueante para exigir recuperación tras fallo: analizar autoridad restante y energía redundante |
| Refrigeración insuficiente | Integración interna requiere ruta térmica explícita | Casetes y cierres cambian ventilación según estado | Exposición no garantiza enfriamiento interno suficiente | Alta: balance térmico y simulación de los puntos críticos |
| Rotura de pala o impacto | Carcasa no equivale a contención de fragmentos | Soportes/casetes expuestos al desplegar | Aro/rejilla no equivale a contención certificada | Alta: definir impactos y velocidades de fragmento; analizar materiales, uniones y fallo |
| Confundir estética con capacidad | Aspecto compacto no prueba rendimiento | Forma cerrada no prueba transición | Carenado deportivo no prueba bajo arrastre | Bloqueante para decidir por rendimiento: mismas condiciones y métricas, incertidumbre explícita |

Los riesgos específicos de nuestros mecanismos y módulos son inferencias sobre el CAD, no resultados de ensayo. La evidencia externa establece principios: NASA documenta que un conducto mal diseñado puede tener arrastre excesivo y que la holgura de punta afecta al rendimiento [3]; no valida estos conductos. NASA también documenta formación de hielo en entradas/ventiladores y daños por ingestión [4]. Una rejilla de protección no convierte ninguna variante en impermeable o apta para toda condición.

## Qué significa girar bien sin sacrificar velocidad

Hay dos métricas distintas: reorientar el cuerpo y curvar la trayectoria. Deben compararse tiempo de reorientación, aceleración lateral disponible, error de orientación, recuperación de ráfagas y consumo en la misma masa/estado de vuelo. Más brazo de rotor puede aumentar el par y también la inercia; el cociente par/inercia y la respuesta de actuadores deciden el resultado.

A densidad supuesta 1,225 kg/m³, la presión dinámica calculada es 17,01 kPa a 600 km/h y 47,26 kPa a 1000 km/h. Un panel de 0,01 m² con diferencia de presión igual a esa presión dinámica (ΔCp=1, ejemplo) recibiría 170 o 473 N respectivamente. No son las cargas reales de nuestras tapas: requieren el campo de presión y sus apoyos.

Con aceleración lateral de 10 g, el radio cinemático calculado es 283 m a 600 km/h y 787 m a 1000 km/h. Ninguna de estas arquitecturas demuestra todavía 10 g. Que el cuerpo rote rápidamente no hace que su velocidad cambie de dirección instantáneamente.

El archivo de cálculo incluye una sensibilidad de disco actuador ideal por área. Es solo un comparador de discos aislados, no predicción de potencia de los conductos ni un límite inferior universal del vehículo; no se utiliza para declarar ganador.

## Decisión defendible hoy

Desarrollar A como candidata principal, conservando C como referencia fija para identificar efectos de conductos y control. B requiere demostrar una ventaja cuantificada suficiente para compensar su masa, tiempos de transición y modos de fallo. No se selecciona todavía un modelo para condiciones extremas o velocidad máxima.

Antes de una decisión final, las tres deben compararse a igual masa total, carga útil, batería y misión, con: matriz de fuerzas/momentos completa; campos de presión y distorsión en hover, transición y avance; resistencia de piezas/uniones y fallos; envolvente de temperatura, lluvia, viento, polvo e hielo; y simulación de maniobras con actuadores y sensores. Todo ello puede empezar digitalmente. Las probabilidades reales y la calificación ambiental necesitarán evidencia física posterior.

## Fuentes primarias

1. Brescianini y D'Andrea, *Design, Modeling and Control of an Omni-Directional Aerial Vehicle*, ICRA 2016: https://ethz.ch/content/dam/ethz/special-interest/mavt/dynamic-systems-n-control/idsc-dam/People/bdario/brescianini_dandrea_omnidirectional_aerial_vehicle.pdf
2. Ryu, Cho y Cho, *Aerodynamic Analysis of the Ducted Fan for a VTOL UAV in Crosswinds*, 2016, DOI 10.2322/tjsass.59.47: https://www.jstage.jst.go.jp/article/tjsass/59/2/59_T-14-79/_article/-char/en
3. Mort, NASA SP-116, *Summary of large-scale test of ducted fans*, 1966: https://ntrs.nasa.gov/citations/19660015325
4. NASA Glenn, *A Pilot's Guide to Ground Icing — Anticipating Contamination*: https://aircrafticing.grc.nasa.gov/2_2_2_1.html

Cálculos propios reproducibles: `comparar_riesgos.py` y `comparacion_cuantitativa.json`. Los resultados geométricos están verificados numéricamente dentro del modelo; no son medidas de un prototipo.
