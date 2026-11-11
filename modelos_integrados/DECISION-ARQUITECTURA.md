# Arquitectura seleccionada

Actualización vigente, 3 de noviembre de 2026: el plan maestro está en ejecución por autorización del usuario. La referencia identificada es `../configuraciones/A07_BASE.json`; A08 es una candidata de correcciones locales, sin promoción automática. `../ejecucion/INFORME-AVANCE-2026-11-03.md` registra auditoría CAD, conversión CAD→FLU y cribados nuevos. Las pausas mencionadas abajo son históricas: los dos solvers previos siguen pausados, mientras los benchmarks nuevos se ejecutaron por separado. Se conserva la arquitectura A; no se acreditan aún masa, control instalado ni velocidad objetivo.

Estudio de módulo C01: `../ejecucion/G2/INFORME-C01.md` añade dos rotores propios de ocho palas derivados de cálculo anular, sin seleccionar definitivamente número de palas, motor o diámetro. El mayor reduce potencia modelada pero aumenta masa y momento angular; ambos requieren rediseño de alojamiento. Los STEP de componente no sustituyen al rotor ilustrativo A07. Las operaciones calculadas y los presupuestos siguen condicionados a polares, instalación y hardware sin validar. La arquitectura de ventiladores internos y los objetivos de agilidad/velocidad se mantienen.

Fecha: 1 de noviembre de 2026, America/Bogota.

El usuario aceptó la recomendación de desarrollar **A: ventiladores internos**, con la carrocería deportiva del diseño industrial 02. Esta es la base seleccionada para continuar el prototipo virtual. B (retráctil) y C (conductos exteriores) se mantienen como referencias de comparación; no son la arquitectura principal.

Referencia de forma aprobada: `diseno_industrial_v2/diseno_industrial_v2.step`, también conservada en `familia_deportiva/A_integracion_interna/diseno_industrial_v2.step`. La selección expresa una preferencia de arquitectura y diseño industrial, no valida los cuatro rotores representativos, sus dimensiones o las prestaciones físicas.

Restricciones vigentes: trabajo por computador en esta etapa; objetivo de producto deportivo profesional, compacto y de aspecto agresivo; elementos giratorios integrados y protegidos; escalado objetivo de 2 a 10 kg con configuraciones propias; agilidad y estacionario omnidireccional, con velocidad objetivo de 600–1000 km/h. Ninguna de estas prestaciones está acreditada por el render.

Prioridad técnica siguiente: diseñar la distribución de fuerzas, canales y/o vectorización para producir empuje lateral y momentos independientes dentro del cuerpo. Verificar autoridad y saturaciones con un modelo único de geometría, masas y actuadores antes de trasladar resultados de geometrías anteriores. Después cerrar alojamiento, flujo, potencia, estabilidad dinámica y autonomía virtual. La silueta aprobada es una referencia de diseño; cualquier cambio necesario debe quedar documentado y visible.

Evidencia de comparación: `familia_deportiva/COMPARACION-Y-RIESGOS.md` y `familia_deportiva/comparacion_cuantitativa.json`.

## Rama de integración para continuar los cálculos

`vectorizacion_A/CAD_integracion_coherente/A_integracion_conductos_coherentes.step` consolida las camisas ilustrativas y conductos inferiores en cuatro sólidos con taladro de radio 42 mm. La reimportación verifica 101 piezas válidas y ausencia de intersección local de cada rotor con su conducto; la separación radial geométrica mínima es aproximadamente 0,988 mm. `VERIFICACION.json` conserva volúmenes y huella del STEP fuente. No es una aprobación de tolerancias, deformaciones, fabricación o interferencias globales.

`vectorizacion_A/area_y_escala/INFORME.md` contiene el cribado de área y escala para masas supuestas de 2, 5 y 10 kg. La referencia ideal de rotor libre no se interpreta como potencia eléctrica de estos conductos. El mapa presión–caudal–potencia y el presupuesto de masa permanecen abiertos.

La primera ejecución URANS v2 fue rechazada por crecimiento no físico de velocidades/cargas y parada antes del tiempo solicitado; `../CFD/ESTADO-TRANSITORIO.md` documenta el diagnóstico separado. Ninguna de esas cargas rechaza o valida por sí sola la arquitectura seleccionada: se trata de un fallo del cálculo pendiente de aislar.

## Estudio de control continuo y capacidad reversible

`vectorizacion_A/reversibilidad_6DOF/INFORME.md` compara el modo A con cuerpo horizontal y una variante de doble salida. En un modelo ideal con cono efectivo de 45°, el modo horizontal cubre una esfera de aceleraciones de radio 0,5 g más reservas de momento con capacidades útiles suficientes de 8,03 / 20,58 / 42,16 N por ventilador para 2 / 5 / 10 kg supuestos. Son cotas conservadoras del modelo, no una selección de motor ni empuje medido. El ángulo efectivo, CG y pares libres siguen sin validar.

La variante `vectorizacion_A/CAD_doble_flujo/` agrega bancos por encima y debajo del rotor para estudiar empuje reversible y mayores dominios de aceleración/orientación. Sus 149 piezas válidas y comprobaciones locales no constituyen una decisión del usuario de añadir esa complejidad. La reversibilidad puede ser necesaria para aceleraciones descendentes muy superiores a g con cuerpo horizontal, además de servir al vuelo invertido; se calcularon escenarios de 1, 2 y 5 g para mantener abierto el objetivo de máxima agilidad.

La selección de A permanece vigente. No se reduce el objetivo final al caso de 0,5 g ni se afirma óptimo global. Antes de dimensionar propulsión o entrenar ML se requiere un mapa instalado de seis componentes de fuerza/momento, sus límites de potencia y respuesta, masas/inercias y análisis estructural/compresible.

## Envolvente de avance y ruta axial

`aerodinamica_A/INFORME-AVANCE-Y-TAPAS.md` registra la medición del loft cerrado de referencia: 1,340 m de largo, 0,8304 m² de superficie y 40,09 litros de volumen bruto. Es anterior a recortes, detalles y puerto posterior; no representa puertas de crucero ya instaladas. La integración adaptativa, las secciones y la triangulación tienen comprobaciones numéricas propias.

La referencia de fricción turbulenta para 5 kg supuestos a 1000 km/h es aproximadamente 96 N / 26,7 kW, sin onda, forma, tomas, base ni trimado. Es una estimación condicionada de placa lisa, no arrastre total, cota inferior universal o velocidad demostrada. No se transfieren coeficientes del huso circular anterior.

La ruta axial recta entre las cuatro camisas verticales tiene un diámetro exterior límite geométrico de 42 mm; con pared axial supuesta de 2 mm quedan 38 mm de paso interior y ningún margen. `aerodinamica_A/VERIFICACION_RUTA_AXIAL.json` contrasta diámetros de tubo con las camisas del STEP. No se considera resuelta una toma nariz–cola o un motor instalado. Hay que estudiar ruta y estación del propulsor rápido conjuntamente con los ventiladores internos.

Se calcularon escenarios de tapas en presión diferencial, con dos condiciones de apoyo y una verificación analítica externa. No existe todavía un diseño de tapa, soporte, sello o cierre validado; los espesores de cribado no se adoptan como planos de fabricación.

## Alternativas de estaciones para la propulsión axial

`empaquetado_axial_A/INFORME.md` compara redistribuciones dentro del loft elegido y conserva separada la elección original. Una candidata con x=±100 mm e y=±86 mm admite un volumen axial exterior de 80 mm entre x=−400/+400 mm, dejando 2 mm de separación radial respecto a las camisas ideales. Se verificaron todos los canales con barridos conservadores y mecanismos del STEP, más intersecciones y reimportación de los archivos de reserva. No es una toma nariz–cola, motor o conducto diseñado.

El espacio central ganado tiene un costo: a igual capacidad útil hipotética de 21 N por ventilador, la candidata de 80 mm tiene aproximadamente ±3,50 N·m de cabeceo puro frente a los momentos mayores de estaciones más separadas. Su intervalo de CG longitudinal con reserva de cabeceo ±0,5 N·m se estrecha a aproximadamente ±61 mm bajo esas mismas hipótesis. No se infiere aceleración angular sin tensor de inercia y masa reales.

Se comparan reservas de 38, 60 y 80 mm y sus dominios ideales de control, incluidos escenarios reversibles de mayor aceleración. Son opciones de investigación con prefiltrado y malla finita, no un óptimo global ni una nueva selección del usuario. El cierre conjunto de propulsor, batería, CG y mecanismos decidirá si alguna conviene más que la distribución original.

## Inercia, CG y perfiles de giro de las reservas

`empaquetado_axial_A/masa_y_agilidad/INFORME.md` añade 36 escenarios explícitos de material, masa residual y CG para la referencia de 5 kg. El giro de 30° prescribe actitud y posición inercial, transforma la gravedad al cuerpo y comprueba reservas de momento con la inercia; no mantiene una capacidad escalar de momento horizontal durante toda la maniobra. Las masas de equipos y material son supuestas, no un cierre de componentes.

Las candidatas 38/60/80 mm admiten 11/11/5 de los 12 escenarios explorados por grupo, respectivamente. Los recuentos no son probabilidades. Tres perfiles nominales reconstruidos pasan los balances ideales de Newton–Euler en 481 instantes, pero omiten dinámica y límites de tasa de actuadores, aerodinámica exterior y efectos internos del rotor. No se declaran tiempos reales de reorientación.

La reserva de 80 mm resulta más sensible al módulo hipotético de 1 kg a x=400 mm y al desplazamiento del equipo restante para compensarlo. Esta evidencia mantiene abiertas las alternativas de menor paso axial; no autoriza una selección final solo por espacio central o fuerza mínima calculada.

## Trayectorias con cambio de fuerza limitado

`empaquetado_axial_A/masa_y_agilidad/tasas/INFORME.md` sustituye las asignaciones independientes por un LP temporal conjunto en los escenarios ilustrativos seleccionados. Se ensayan parámetros de cambio vectorial de fuerza de 20, 50 y 100 N/s por ventilador; no son especificaciones de un motor existente. Se conservan límites ideales de fuerza y cono, y se comprueban 41/81 nodos con duraciones de una malla finita.

Las nueve trayectorias elegidas se interpolan con fuerzas continuas y se integran como cuerpo rígido mediante Newton–Euler y cuaternión. Se informan diferencias respecto al movimiento prescrito, en vez de asumir que la igualdad en nodos prueba seguimiento exacto. La interpolación conserva las cotas convexas de fuerza y tasa; puede tener cambios de pendiente. No se afirma respuesta física de rotor/servo ni robustez temporal de las correcciones de control.

Este resultado cambia los tiempos condicionales, no la arquitectura seleccionada. Sigue siendo necesario caracterizar la planta instalada, dimensionar componentes y estudiar estructura, energía y aerodinámica antes de elegir la distribución definitiva.

## Reacción completa del canal aislado

`CFD/INFORME-REACCION-CONDUCTO.md` (desde modelos_integrados: `../CFD/`) registra una nueva integración de paredes y álabes sobre un campo guardado de Euler, sin alterar las ejecuciones activas. Las seis transformaciones de momento a origen común y las particiones de cargas pasan comprobaciones con tolerancias de redondeo.

En ese campo aún no desarrollado, la magnitud lateral pasa de 6,976 N sobre álabes a 2,110 N sobre todos los sólidos del dominio. No es una eficiencia física validada; evidencia que las cargas locales no bastan para calibrar el cono instalado. La acción siguiente debe incluir salida exterior, reacción del conducto y balance transitorio de cantidad de movimiento, además de desarrollo y sensibilidad numérica. El cono efectivo de 45° permanece supuesto y la arquitectura A elegida se conserva. El objetivo completo continúa sin demostrarse.

## Sensibilidad a la dirección útil del empuje

`vectorizacion_A/sensibilidad_angulo/INFORME.md` documenta límites necesarios y certificados ideales suficientes para conos 35°/40°, contrastados con 45°. Para la bola intermedia de 0,5 g con cuerpo horizontal y empujes de signo positivo, el mínimo geométrico necesario es 30°, no una garantía con reservas. Se verificaron 9.216 vértices nuevos para 2/5/10 kg. No se valida el ángulo instalado ni se cambia la arquitectura A elegida; se mantiene el objetivo mayor de agilidad y velocidad. Los tiempos de giro anteriores requieren recalcularse para cualquier mapa/cono nuevo.

Las nueve trayectorias ideales guardadas de 5 kg para las candidatas de reserva axial se comprobaron de nuevo contra conos de 35° y 40°: su máximo ángulo es 33,75°. Por ello se conservan las mismas fuerzas y propagación ideal, con margen angular de 1,25° respecto a 35°. `empaquetado_axial_A/masa_y_agilidad/tasas/sensibilidad_cono/INFORME.md` no declara tolerancia mecánica, robustez física, nueva selección de estaciones ni óptimo global.

## Malla exterior de la envolvente cerrada para avance

Se preparó y verificó `../CFD/avance_A_cerrada_h0.008/`: 326.013 tetraedros, pared cerrada, errores geométricos normalizados por el cuerpo y Mesh OK. Representa el loft cerrado anterior a aberturas/detalles, no puertas ni instalación funcional. `../AVANCE-A-TRANSONICO-EVIDENCIA-Y-MALLA.md` distingue la nueva evidencia NACA y la geometría elegida. No hay aún solución compresible, arrastre total o Mach crítico validado; se conserva A como base seleccionada.

El diagnóstico compresible a 600 km/h con pared deslizante completó un arranque físico corto y pasó la auditoría de campos finitos/positivos; no valida arrastre o Mach crítico. Una rama localEuler busca ahora convergencia de presión usando pseudotiempo. `../CFD/ESTADO-AVANCE-COMPRESIBLE.md` documenta fallos rechazados, alcance, procesos y campos. La arquitectura A sigue como base seleccionada, sin afirmar todavía viabilidad de la misión completa.

## A03: nueva entrega CAD solicitada por el usuario

Se creó `producto_A03/` con presentación de producto y tres escalas objetivo, 2/5/10 kg. Cada STEP integrado contiene 178 piezas válidas reimportadas y cada corte 145. Se incluyen carcasas huecas, ocho cubiertas enrasadas, mecanismos internos de doble banco, pasos de ejes perforados, alojamientos de actuadores y estructura geométrica de apoyo.

Esta rama propone las estaciones intermedias x=±200, y=±76 mm y una interfaz axial exterior de 60 mm, a escala de referencia 5 kg. Es una propuesta de integración de la revisión, no una prueba de óptimo global ni una validación de masa/propulsión. El tubo central y la interfaz posterior no representan un reactor seleccionado. La apertura de tapas y transmisión de los actuadores siguen pendientes. No heredar tiempos de giro o mapas instalados de otras masas/pieles.

La investigación fue pausada por el usuario; sus dos contenedores CFD se suspendieron con docker pause conservando memoria y sin reiniciarlos. Esta entrega CAD no reanudó ni completó el objetivo de investigación. `producto_A03/LEEME.md`, `REVISION_ENTREGA.json` y los manifiestos detallan medidas, comprobaciones y límites.


## Confirmación explícita y CAD A06 — 2 de noviembre de 2026

El usuario confirmó: «el escogido fue el Ventiladores internos genera el cad». Se mantiene A: los rotores permanecen dentro del cuerpo. Se descarta la interpretación de convertir la entrega en B retráctil. A06 consolida la geometría A05 y sus cuatro aletas posteriores en X; incluye cerrado y corte de inspección, sin afirmar cinemática de tapas o prestaciones validadas. Las variantes de masa siguen siendo escalas geométricas objetivo. No se reanudan los solvers CFD pausados.


## A07 — Estudio de compuertas, 2 de noviembre de 2026

Se mantiene A con ventiladores internos. El estudio detectó ocho solapes tapa–camisa en A06 y los elimina recortando las camisas con un loft interior de secciones desplazadas 2 mm. Se estudia elevación de 10 mm seguida de abatimiento 110° (referencia 5 kg). El cribado discreto revisa 61 posiciones y 488 parejas contra envolvente de referencia, aletas/carenados y otras tapas, con solape máximo cero; ocho comprobaciones nominales tapa–camisa recortada también dan cero. No es un barrido continuo ni mecanismo de guías/bisagras/actuadores dimensionado. Las poses no acreditan flujo, cargas o transición. Solvers CFD permanecen pausados.


## Visualización de vuelo rápido — 2 de noviembre de 2026

vuelo_rapido_visual entrega escenas detalladas a 600 y 1000 km/h con trayectoria prescrita y reconstrucción inversa de fuerzas/momentos. No es predicción de vuelo real ni validación de velocidad, cargas o aletas. Los pulsos de 3/6/10 g son exigencias elegidas, no capacidad demostrada. La planta instalada sigue sin identificar; la investigación CFD no se reanudó. Se mantiene A con ventiladores internos.


## Plan de cierre consolidado — 2 de noviembre de 2026

`../plan_maestro/PLAN-MAESTRO.md` y sus registros de requisitos/tareas/riesgos fijan la ruta de ejecución. Se conserva A (ventiladores internos) y A07 como referencia conceptual, con 5 kg como ancla de integración propuesta y versiones 2/10 kg a recalcular. No se congelan capacidades, motor axial, número/área de módulos, aletas o mecanismo de tapas sin cierre físico y de masa. El plan no reanuda los solvers pausados ni crea un objetivo persistente.

## C02 — integración compacta candidata, 3 de noviembre de 2026

Se conserva A con ventiladores internos y A07 como referencia canónica. `../ejecucion/G3/C02/INFORME-C02.md` documenta una candidata separada de 5 kg objetivo, estaciones x=±160/y=±76 mm, cuatro rotores nominales D82 y motor reservado dentro del cubo. STEP cerrado/corte, FreeCAD y Blender proceden de geometría identificada en `../configuraciones/C02_CANDIDATA.json`.

Las 314 parejas nuevas de interfaces no presentan intersecciones nominales; las tapas pasan 61 posiciones discretas y 808 parejas dentro del alcance estudiado. No se aprueban las uniones históricas, la trayectoria continua ni los mecanismos reales de guía/cierre. Requisitos de motor y masa parcial son cálculos condicionados, sin componentes o materiales seleccionados. El mayor D102,5 no se declara instalado ni superior en agilidad global. Faltan flujo instalado, potencia/temperatura, masa física, estructura y variantes propias de 2/10 kg. No se reanudaron los solvers históricos pausados.
