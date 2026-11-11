# Auditoría del objetivo global

Referencia de planificación actual: [Plan maestro de cierre](plan_maestro/PLAN-MAESTRO.md), 2 de noviembre de 2026. La auditoría siguiente conserva observaciones históricas y sus actualizaciones; el plan identifica qué resultados pueden reutilizarse y sus límites. Su creación no reanuda solvers ni acredita el cierre del proyecto.


Objetivo conservado: encontrar la geometría/arquitectura más favorable para 2–10 kg, omnidireccionalidad brusca y 600–1000 km/h, cuantificando mecanismos. No se ha demostrado optimalidad global ni viabilidad de toda la misión. Los componentes y sus mapas aún deben diseñarse y caracterizarse; hay trabajo computacional pendiente. El 3 de noviembre de 2026 el usuario activó el objetivo de completar el plan maestro y autorizó comenzar su ejecución. `DATOS-PARA-CERRAR-VALIDACION.md` enumera carencias, no un impedimento para seguir diseñando.

Estado de seguimiento vigente: ejecución del plan maestro activa desde el 3 de noviembre de 2026. Se inspeccionaron los dos contenedores CFD históricos: continúan vivos y pausados; no se duplican ni reanudan automáticamente. Los nuevos benchmarks pequeños son casos separados. Las menciones de pausa/ejecuciones activas posteriores en el historial deben interpretarse con su fecha y configuración. La entrega A03 fue una tarea independiente que no reanudó aquellos cálculos. El objetivo activo sigue sin completarse.

## G6 — reparto ideal, centro de masa y potencia

`ejecucion/G6/potencia_cg_ideal/INFORME-POTENCIA-ASIGNACIONES.md` evalúa la potencia de discos libres ideal para las asignaciones SOCP certificadas; los máximos de vértice por escenario están aproximadamente entre 2,41 y 2,58 kW en las variantes 35°/45°. No son potencias instaladas ni soluciones optimizadas en potencia. Un ejemplo explícito de batería y carga constante muestra sensibilidad de masa sin cerrar misión ni hardware. Cuatro pruebas pasan; no se reanudaron CFD históricos.

`ejecucion/G6/potencia_cg_ideal/INFORME-CONTRASTE-CONO-CONTINUO.md` contrasta 6.912 esquinas con SOCP Clarabel: 6.624 resueltas, 288 con estado primal inviable del solver. Tres pruebas analíticas y 6.624 comparaciones LP/SOCP pasan; se mantiene el patrón de certificación anterior y la mayor diferencia LP−SOCP observada es 0,117 N. Se elimina la ambigüedad de discretización para el modelo ideal continuo, no para el dispositivo físico. No se reanudaron CFD históricos.

`ejecucion/G6/potencia_cg_ideal/INFORME-SENSIBILIDAD-CONO.md` repite 4.608 asignaciones con conos ideales de 35°/40°. Para CG equilibrado, 5/6 casos por reserva pasan el certificado supuesto de aceleración y momento; se registran 190 estados inviables y dos desconocidos, sin convertir fallo numérico en resultado físico. Se identificó sensibilidad de discretización frente a 45°; diferencias pequeñas no sustentan elección de geometría. Dos pruebas analíticas pasan. No se reanudaron CFD históricos.

`ejecucion/G6/potencia_cg_ideal/INFORME-ACELERACION-MOMENTOS.md` amplía el análisis a 4.608 esquinas de aceleración y momento simultáneos. Bajo supuestos ideales, con CG equilibrado, cinco de seis escenarios por reserva certifican la caja ±0,25 g por componente y ±0,5 N·m por eje con 21 N/módulo. Sin equilibrio ninguno de los escenarios la certifica. No hay validación física; un fallo del cono interior no descarta el continuo. La caja ±0,5 g por componente incluye una esquina imposible para fuerzas ascendentes en un cono de 45°, sin descartar aceleraciones aisladas. Se revisó una respuesta Antigravity y se rechazó su afirmación genérica sobre subactuación. No se reanudaron CFD históricos.

Una extensión de equilibrio estático con reserva simultánea de momentos resolvió 288 esquinas de 36 escenarios hipotéticos, y cuatro pruebas analíticas pasaron en un entorno SciPy temporal. Para reserva axial 80 mm, equipo genérico en x=0 y capacidad supuesta 21 N por módulo, ninguno de seis escenarios obtuvo certificado en el cono discretizado interior; el resultado no prueba imposibilidad física. Los otros grupos y las limitaciones constan en `ejecucion/G6/potencia_cg_ideal/ESTADO-RESERVA-MOMENTOS.md`. No se reanudaron CFD históricos.

`ejecucion/G6/potencia_cg_ideal/INFORME-MASAS-INTEGRADAS.md` conecta 36 escenarios hipotéticos previos de masa de 5 kg con tres reservas axiales. Para reserva 80 mm y equipo restante situado en x=0, 0/6 casos cumplen el límite supuesto de 21 N por módulo en estacionario vertical de fuerzas paralelas; equilibrando CG pasan 5/6 también la zona supuesta del equipo. No es un mapa C02 ni validación de control. Cuatro pruebas pasan y dos sesiones Antigravity terminaron con respuesta vacía. No se reanudaron CFD históricos.

`ejecucion/G6/potencia_cg_ideal/INFORME.md` documenta 800 escenarios de cuatro discos libres ideales y fuerzas paralelas. Para un desplazamiento hipotético del CG de 60 % de un semibrazo, la potencia ideal aumenta 13,84 % frente a CG centrado. En un ejemplo de 5 kg y 0,5 g lateral, el reparto paralelo exige 21,93 N en cada uno de dos módulos, frente al límite supuesto de 20,58 N; esto no descarta repartos con fuerzas no paralelas. Siete pruebas pasan. Se rechazaron errores de la revisión Antigravity. No es un mapa instalado ni valida el vuelo; no se reanudaron CFD históricos.

## G2 — alcance del modelo NASA con viento

`ejecucion/G2/referencia_nasa_edf/INFORME-VIENTO.md` registra una reproducción
tentativa y sin integración de los ajustes NASA 3F. El ensayo de factores
llegó a 6 psf: a densidad supuesta 1,225 kg/m³, la corriente libre de 600 y
1.000 km/h tendría q unas 59 y 165 veces mayor. No se trasladan esos valores
al flujo local del conducto instalado. El código rechaza q fuera de los
límites de factores e identifica como no demostrada la cobertura conjunta;
cuatro pruebas pasan. Un ejemplo sintético no es una medición ni un mapa C02.
No se reanudaron CFD históricos.

## G2 — referencia experimental NASA de ventilador

`ejecucion/G2/referencia_nasa_edf/` reproduce condicionalmente los ajustes
NASA de empuje y potencia sin viento, con centrado inferido de la tabla 7 y
comprobación visual aproximada de figura 14. Cinco pruebas pasan. El motor
especificado de la referencia pesa 1,1 kg y mide 56 mm de diámetro frente a
la reserva Ø21,8 mm de C02, de modo que no es una sustitución directa; cuatro
motores sumarían 4,4 kg. El modelo y un escenario ideal de 5/10 kg no son
prestaciones C02 ni datos medidos punto a punto. El límite de 8.000–24.000 rpm
es exploratorio, no un dominio DOE completo. No se reanudaron CFD históricos.

## C11 — candidata de tapa segmentada

`modelos_integrados/producto_C21_barras_desviadas/` ensayó 12 rutas desviadas: seis de una fila pasaron el cribado individual de posiciones y seis de la otra no. Una selección parcial combinada produjo una intersección fuera del vástago compartido y un booleano con error en 57 parejas; se rechaza ese conjunto, no todas las rutas posibles. El STEP rechazado reimporta 32 registros válidos. No hay elevador funcional ni CFD histórico reanudado.

`modelos_integrados/producto_C20_orientaciones/` ensayó 54 barras rectas usando las orientaciones de vástago que pasaron C17: todas encontraron una primera intersección con lámina en las poses muestreadas. No se encontró ruta de cuatro orientaciones con las tres conexiones rectas de una fila, pero esto no descarta otras curvas, rutas o mecanismos. No se reanudaron CFD históricos.

`modelos_integrados/producto_C19_barras/` criba seis barras rectas para sincronizar vástagos C17. Todas conectan geométricamente sus extremos, pero las seis intersectan láminas en alguna pose de giro muestreada; la configuración se rechaza para integración, sin descartar otras rutas. Un STEP de una interferencia se reimportó con 30 objetos válidos. No es mecanismo funcional ni barrido continuo. No se reanudaron CFD históricos.

`modelos_integrados/producto_C18_revision_giro/` examina 160 parejas casquillo–lámina en cinco ángulos sin intersección volumétrica detectada y comprueba los ocho recortes coaxiales propios. La invariancia ideal del recorte permite razonar sobre el par casquillo–lámina propio en giro continuo, no sobre el resto del mecanismo ni fabricación. El STEP abierto local reimporta 29 objetos; faltan soporte, elevador, montaje global y cargas. No se reanudaron CFD históricos.

`modelos_integrados/producto_C17_vastagos_radiales/` criba 64 vástagos inclinados en cinco poses de giro y cinco de elevación: 24 pasan, tres por casquillo, y 40 encuentran una primera intersección durante giro. Un conjunto con ocho candidatos reimporta 29 objetos y no muestra solapes entre vástagos ni con ejes/otros casquillos en cerrado en las parejas comprobadas. No se verificó barrido continuo, interacción de casquillos con láminas en giro, soporte estructural, montaje completo o vuelo. No se reanudaron CFD históricos.

`modelos_integrados/producto_C16_vastagos/` criba 32 vástagos ideales conectados geométricamente a casquillos C15; 28 presentan intersección con láminas en al menos uno de cinco ángulos muestreados, y cuatro correspondientes a la lámina 3 pasan el cribado local. Un STEP de esa lámina con dos vástagos reimporta 23 objetos válidos, sin conexión al elevador ni estructura. No se acredita mecanismo, movimiento continuo, montaje global o vuelo. No se reanudaron CFD históricos.

`modelos_integrados/producto_C15_apoyos/` ensaya ocho casquillos conceptuales y recortes en cuatro láminas: cada lámina conserva un sólido y se retiraron aproximadamente 18,25 mm³; la envolvente de los casquillos no choca con los obstáculos locales comprobados durante elevación ideal. El STEP se reimportó con 21 objetos y ocho parejas locales sin solape. Ejes y láminas conservan una penetración intencionada; faltan fijación, soportes, mecanismo, cargas, giro completo y montaje global. No se reanudaron CFD históricos.

`modelos_integrados/producto_C14_ejes_cortos/` compara 28 reservas de segmentos cortos mediante el sólido de barrido de una elevación ideal continua de 20 mm contra cinco piezas locales. Pasan 5/7, 7/7, 7/7 y 5/7 por lámina bajo las hipótesis documentadas. Cuatro reservas centrales se verificaron además contra otras láminas en cinco giros muestreados; dos STEP de poses se reimportaron con 13 objetos cada uno. No hay apoyos, conexión ni mecanismo funcional ni comprobación de montaje completo. Tres pruebas de barrido pasan; no se reanudaron CFD históricos.

`modelos_integrados/producto_C13_ejes_cinematicos/` reconstruye ejes de prueba con el criterio geométrico de C11 y criba 380 parejas en 10 poses de una tapa local. Encuentra 10 y 12 intersecciones a elevaciones 0 y 2 mm, y ninguna en las otras ocho poses muestreadas frente a los obstáculos revisados. No demuestra movimiento continuo, ausencia de colisiones globales ni mecanismo. Se reimportaron 13 objetos CAD válidos y verificaron centros de láminas. No se reanudaron CFD históricos.

`modelos_integrados/producto_C12_ejes/` ensaya reservas cilíndricas en un subconjunto local de C11: 12/16 pares con intersección en cerrado para radios 1/2 mm y ninguno contra cinco piezas fijas en posición elevada 20 mm. No son los ejes cinemáticos C11 ni un mecanismo; faltan trayectoria, otras láminas y el montaje completo. Un STEP de reservas elevadas se reimportó con nueve objetos válidos. No se reanudaron CFD históricos.

`modelos_integrados/producto_C11_laminas/` divide una tapa C03 en cuatro
láminas. El giro directo presentó interferencias; con elevación previa de 20 mm,
cuatro posiciones de subida y seis de giro no tuvieron volúmenes de
intersección superiores a 0,001 mm³ en 12.820 parejas cribadas. A 60° la
proyección de las láminas cubre aproximadamente 21,2 % del círculo nominal
D84; no es pérdida de flujo. Se generaron CAD locales y se reimportaron nueve
objetos válidos por estado. No hay ejes, mecanismos de elevación, cierres,
sellos, barrido continuo, cargas, flujo ni variante de 10 kg comprobados. C11
no sustituye la referencia A07 ni demuestra vuelo. No se reanudaron CFD.

## C10 — enlace de pivote fijo y longitud variable

`modelos_integrados/producto_C10_enlace_variable/` ensaya 20 enlaces ideales
con elevaciones de 10 y 30 mm. En cada serie 19 tuvieron una primera colisión
detectada y uno no estableció contacto con la tapa; ninguno pasó todas las
posiciones. Se permitió solo como hipótesis la penetración del componente
camisa–cuna–soportes. El CAD local C10 reproduce una colisión, no un mecanismo
válido. Los resultados no descartan otras rutas; faltan interfaces, sellos,
cargas y validación física. No se reanudaron CFD históricos.

## C09 — análisis de enlaces y pasos de conducto

`modelos_integrados/producto_C09_paso_sellado/` examina 36 enlaces rectos de
C08: 20 atraviesan solo el objeto combinado camisa–cuna–soportes en cerrado,
pero los 20 encuentran una interferencia adicional en las posiciones de
apertura muestreadas. Para dos enlaces representativos también se registraron
todas las colisiones en siete poses. Un recorte de la camisa solamente no
resuelve esos casos; no se ha aceptado ni generado un paso sellado. Quedan
abiertas otras rutas, geometrías y mecanismos. No se reanudaron CFD históricos.

## CAD C08 — reservas para guías deslizantes

`modelos_integrados/producto_C08_guias/` criba 72 posiciones de reserva de
guía para una compuerta de 5 kg. Ocho pasaron las muestras de techo/suelo, el
cribado nominal contra 316 registros y cuatro cilindros de rotor, y seis poses
de las ocho tapas. Una pareja a distintas alturas reduce las distancias
mínimas a la tapa cerrada a 45,22 y 27,80 mm; son reservas sin soportes.
Ninguno de 36 enlaces rectos muestreados para ese par evitó todos los
obstáculos. El paso a través de o alrededor de la camisa y el sellado siguen
abiertos; no se prueba imposibilidad de otras rutas ni se promueve un mecanismo.
Las dos posiciones del CAD local y sus STEP se reabrieron/reimportaron con
ocho objetos válidos. No se ensayó 10 kg ni se reanudaron CFD históricos.

## CAD C06 y C07 — apertura deslizante exploratoria

`modelos_integrados/producto_C06_busqueda_eje/` compara un eje interior y
una tapa que se eleva 10 mm y se desplaza 100 mm. En un módulo de referencia,
la proyección vertical de la tapa deslizante cubre 0 % del círculo nominal
D84 y la opción abatible examinada cubre aproximadamente 13,2 %; no es
caudal ni pérdida aerodinámica. Ambas carecen de mecanismo físico diseñado.

`modelos_integrados/producto_C07_deslizante/` integra ocho poses deslizantes
en el CAD completo de 5 y 10 kg; 10 kg es semejanza geométrica. En 5 kg, seis
poses simultáneas pasaron 1.416 cribados de pares seleccionados; en la pose
final se cribaron 2.492 parejas contra el resto de registros sin intersecciones
superiores a 0,001 mm³ según el procedimiento documentado. Los FCStd y STEP
reabrieron/reimportaron con 316 objetos válidos por escala y rotores sin
traslación de centro. No se verificó el barrido continuo ni todas las piezas
en posiciones intermedias. Faltan guías, accionadores, sellado, tolerancias,
cargas y planta física; A07 sigue como referencia, y no se acreditan masa o
prestaciones. No se reanudaron CFD históricos.

## CAD C05 — recorte y cierre de una compuerta

`modelos_integrados/producto_C05_alojamiento/` estudia el alojamiento de la
compuerta superior 0 de 5 kg. Una envolvente analítica de cajas da un recorte
aproximado de 357 mm³ en la piel; el modelo pasa de cuatro a seis sólidos con
dos fragmentos pequeños. Los dos brazos C04 v2 chocan con aro y junta en
cerrado. Ninguna de 19 barras rectas muestreadas elimina simultáneamente las
interferencias contra los cinco obstáculos elegidos. Este recorte y mecanismo
se mantienen **rechazados para integración**; no demuestran imposibilidad de
otras alternativas. Se generó y reimportó un CAD local de 16 objetos; no es
un montaje de vuelo ni una variante propia de 10 kg. La documentación detalla
comprobaciones, incertidumbres y la discrepancia entre operaciones booleanas.
No se reanudaron CFD históricos.

## CAD C04 — estudio local de compuerta

`modelos_integrados/producto_C04_estudio_bisagra_v2/` contiene un primer
estudio CAD local para la compuerta superior 0 de C03: guías, carro y eje, con
tres posiciones. La alternativa v2 elimina las dos intersecciones guía–piel
observadas en v1 para las tres muestras, pero persisten siete cruces de otras
piezas con la carrocería en cerrado. Ambas se conservan como **no aprobadas**.
Los tres pares FCStd/STEP de v2 se reabrieron/reimportaron con 14 objetos
válidos cada uno; esto no verifica el mecanismo, la equivalencia completa ni
la trayectoria continua. No se modificaron C03 ni el CAD canónico A07. Los
ventiladores siguen internos y no se reanudaron solvers CFD pausados.

## Entrega CAD C03 — 8 de noviembre de 2026

Por solicitud específica del usuario se generó
`modelos_integrados/producto_C03/`: cuatro ensamblajes FCStd/STEP de 5 y 10 kg
objetivo, con compuertas cerradas y abiertas, y renders basados en el CAD. La
fuente es la candidata C02 detallada; 10 kg es una semejanza geométrica, no una
configuración de hardware ni masa cerrada. A07 sigue siendo la referencia de
investigación. No se reanudaron los solvers CFD pausados.

Los cuatro STEP se reimportaron con 316 registros válidos; se reabrieron sus
FCStd y se comprobaron localmente las tapas frente a sus rotores, el movimiento
de las tapas y que los rotores permanecen fijos. La auditoría estricta registró
diferencias de etiquetas automáticas y de volumen entre STEP y FCStd; el
diagnóstico parcial posterior emparejó 316 registros del caso cerrado de 5 kg y
comprobó tres piezas seleccionadas, sin cerrar la equivalencia global. Los
detalles y límites están en `producto_C03/LEEME.md`, `AUDITORIA.json` y
`DIAGNOSTICO_INTERCAMBIO.json`.

El CAD no incluye un mecanismo físico de apertura aprobado ni acredita masa,
propulsión, cargas o prestaciones; las tapas abiertas son posiciones
conceptuales. La solicitud CAD no reinicia por sí sola la meta general pausada.

## Continuación del plan — contrato de propulsión

Tras reactivar la meta, se copió el contrato experimental generado por
Antigravity a `ejecucion/G6/contrato_mapa_candidato_r1/`. Se retiró la política
`ADVERTIR`, que permitía aceptar silenciosamente muestras fuera del dominio;
validador y esquema solo admiten `RECHAZAR`. Las 27 pruebas pasan. El contrato
es candidato, usa datos sintéticos y no está integrado al simulador; el rango
de módulo de velocidad no demuestra cobertura de direcciones ni cobertura
multidimensional conjunta. Tras recuperar una dependencia SciPy desde iCloud,
se corrigió la serialización de la batería 6DOF: tres casos numéricos pasaron,
el JSON se leyó correctamente y un fallo inducido produjo código 1 y estado
`FALLIDO`. Se conserva el error original. Detalles en
`ejecucion/G6/verificacion_6dof_antigravity_r1/RESULTADO-2026-11-08.md`.
Son verificaciones numéricas, no validación física del vehículo.

## Aceleración ideal — 2, 5 y 10 kg

`ejecucion/G1/aceleracion_ideal_2_5_10/INFORME.md` agrega 24 escenarios de
cinemática horizontal ideal. A 1000 km/h y aceleración longitudinal supuesta
de 2 g, el recorrido calculado es 1967 m y, para 5 kg, la potencia útil final
es 27,24 kW. No se incluyen arrastre, sustentación ni transición. La batería
ilustrativa excede 5 kg bajo las hipótesis de eficiencia y potencia específica
indicadas; esto no descarta otras tecnologías ni misiones. Pasan cuatro pruebas
analíticas y Antigravity contrastó el caso de referencia. Siguen pendientes
presupuestos físicos propios de cada escala y mapas instalados.

## Actualización del 7 de noviembre de 2026

Antigravity está trabajando mediante conversaciones CLI independientes y
espacios aislados, con revisión antes de integrar resultados. El estado y los
incidentes constan en `integracion_antigravity/ESTADO-ORQUESTACION-2026-11-07.md`.
Se incorporó `ejecucion/G2/referencia_uiuc_mi32_r1/` con código y datos UIUC de
una hélice abierta en estático y avance. Sus 18 y 11 pruebas locales pasan;
se retiraron afirmaciones y una aserción de incertidumbre que no estaban
sustentadas. Los datos verifican procedimientos de cálculo y no son un mapa
instalado ni validan los ventiladores C02. No se reanudaron los CFD históricos.

El usuario reactivó la meta y autorizó usar Antigravity. Se verificaron dos
conversaciones simultáneas y la lectura de la guía de integración. Después,
cuatro agentes analizaron en paralelo documentos concretos de flujo, masa,
propulsión y control. Sus respuestas se revisaron; algunas conclusiones
excesivas se descartaron. Evidencia y límites: `integracion_antigravity/LEEME.md`
y `integracion_antigravity/REVISION-LOTE-2026-11-07.md`.

`ejecucion/G1/potencia_simultanea_c02/INFORME.md` añade 192 sensibilidades y
48 umbrales condicionales para C02 de 5 kg con potencia eléctrica hipotética
simultánea en avance. Para 600 km/h, arrastre supuesto de 50 N, aceleración en
60 s y apoyo supuesto de 1 kW, el modelo exige 3,24 kg de batería frente a
2,204 kg asignables en la hipótesis geométrica ligera sin hardware adicional.
No son datos medidos ni una demostración de imposibilidad general. La revisión
r2 corrigió 20 selecciones de tiempo en mesetas sin cambiar masas mínimas ni
umbrales, y pasa siete pruebas; quedan pendientes los mapas, el hardware y los
presupuestos propios de 2/10 kg. Los CFD históricos continúan sin reanudarse.

`ejecucion/G6/autoridad_C02/INFORME.md` añade 400 sensibilidades estáticas
ideales del brazo vertical de fuerza para C02: con CG x supuesto de +0,096 m,
cono ideal 45°, 20,58 N por módulo y brazo de −0,039 m, los máximos calculados
son 0,731 g en +x CAD (hacia cola) y 0,254 g en −x CAD (hacia nariz). Ni ese
CG ni ese brazo son datos instalados; siete comprobaciones analíticas pasan y
no se afirma capacidad de vuelo.
`ejecucion/G6/autoridad_C02/INFORME-VERTICAL.md` agrega 560 escenarios ideales
con aceleración vertical: sin fuerzas adicionales ni reversibilidad, el modelo
no produce aceleración descendente superior a g con actitud fija. Para CG
supuesto +0,096 m y 20,58 N/módulo, el máximo vertical ideal sin demanda
horizontal es +0,049 g. No representa una limitación medida del vehículo.

Por instrucción posterior del usuario, Antigravity también realiza código y
pruebas en espacios aislados. Doce sesiones simultáneas produjeron ocho
respuestas completas y cuatro con error o tiempo agotado; las últimas también
conservan archivos parciales. No se promueven sus resultados sin revisión.
`integracion_antigravity/ESTADO-LOTE-AUTONOMO-01.md` registra tareas, pruebas
informadas y una segunda ronda de revisión iniciada.

## Actualización del 4 de noviembre de 2026

`ejecucion/G2/xfoil_sd8020/INFORME-XFOIL-INICIAL.md` registra fallos SIGFPE del paquete Ubuntu y una compilación separada del código MIT que produce resultados exploratorios. En diez puntos UIUC, el residuo acoplado final pasa su criterio, pero todos presentan avisos de marcha; el cribado estricto acepta 0/10. Se verifica una diferencia de orden entre encabezados y datos de transición en esa compilación. No hay polar ni prestaciones de rotor aceptadas.

`ejecucion/G2/INFORME-COBERTURA-POLAR-C02.md` distingue tablas UIUC combinadas de sustentación/arrastre y datos adicionales solo de sustentación, preserva sus ramas y demuestra una condición cinemática de cuerda/Re/M para la geometría interpolada. No acredita el rotor ni selecciona RPM. El preparador de depósito ahora tiene una prueba de modificación de ambos extremos y mantiene el rechazo de la referencia 1700 sin convergencia.

La malla fina terminó en 600, salida/reconstrucción 0: p cumple su criterio, pero Ux, Uy y k aún no. ΔU máximo 580–600 es 0,344632 m/s; el RMS ponderado por volumen es 0,00429881 m/s. La continuación separada hacia 800 se observó en 609 a las 02:05 UTC; comprobar el proceso real antes de actuar. Los resultados de malla no se aceptan aún. Véase `ejecucion/G2/flujo_C02_conducto/INFORME-INTEGRIDAD-COPIAS.md`.

La rama de fuente de 1 N terminó en 1700: su residuo inicial máximo de presión es 1,04064 × 10⁻⁴ y no pasa el criterio de 1 × 10⁻⁴. El máximo cambio local de velocidad 1680–1700 es 2,41489 m/s y está a 0,2735 mm de una aleta; la proximidad no demuestra su causa. Se han verificado las copias históricas del mapeo fino y se han reforzado los preparadores posteriores. Informe y límites: `ejecucion/G2/flujo_C02_conducto/INFORME-INTEGRIDAD-COPIAS.md`.

La continuación de1N a1600 y la fina a200 terminaron con residuos aún fuera de criterio. Dos copias iniciales posteriores contenían archivos de0bytes y fallaron; orígenes verificados. Se corrigió y verificó la copia por bloques y huellas dentro de contenedor; se iniciaron dos ramas nuevas, cuyo estado posterior figura arriba. Véase `ejecucion/G2/flujo_C02_conducto/INFORME-INTEGRIDAD-COPIAS.md`.

Referencia1N1500 terminó: presión aún falla1e−4, resto de cribados pasa; CV0,00142258%. Se ensaya relajación de presión0,2 en rama1600 sin cambiar física/umbrales. Preparador de depósito con caudal libre implementado y probado en rechazo/preservación de campos; no se inició ese caso. Véase `ejecucion/G2/flujo_C02_conducto/PROTOCOLO-CAUDAL-LIBRE.md`.

Ley local de pala verificada en9casos/64anillos, con42puntos de cribado todos marcados con alguna extrapolación; no curva instalada. Benchmark caudal libre conserva acuerdo analítico final pero falla criterio lineal: aceptación global falsa. Fuente1400/fina100 terminados y auditados, residuos aún fallan; siguen ramas1500/200. Informes `ejecucion/G2/INFORME-LEY-LOCAL-C02.md` y `INFORME-CAUDAL-LIBRE.md`.

Contraste C02: fuente1N terminó1200 y se auditó con reacción/trabajo; residuos fallan y CV0,346214%, por lo que la comparación sigue preliminar. Continuación separada hasta1400 activa. Malla fina1.283.005celdas/checkMeshOK, campos transferidos verificados y solver independiente100 activo. Dos casos nuevos activos; históricos pausados; sin cierre de prestaciones. Informes `INFORME-F1N-PRELIMINAR.md` y `INFORME-MALLA-FINA-R1.md` en `ejecucion/G2/flujo_C02_conducto/`.

Reanudación del objetivo tras entrega CAD: r9 terminó1200/reconstrucción0 y pasa los cinco cribados numéricos sin relajar umbrales. CVfinal0,001693%; persisten cambios locales y sensibilidad pendiente. Nueva malla del mismo STEP:1.283.005celdas/checkMeshOK, transferencia inicial en curso. No hay cargas físicas aceptadas. `ejecucion/G2/flujo_C02_conducto/INFORME-R9-TERMINADO.md` conserva resultados y límites.

Fuente axial: contrastes a fuerza cero y no nula rotada terminados con salida0 y diferencia de velocidad0; trabajo2,58316W verificado en canal sintético. El primer C02 con fuerza prescrita1N/banda4mm arrancó separado como UID1000/MPI4. Balance de volumen de control incorpora la fuerza y trabajo; ningún mapa instalado está aceptado. Véase `ejecucion/G2/flujo_C02_conducto/INFORME-FUENTE-AXIAL.md`.

`ejecucion/G2/flujo_C02_conducto/INFORME-FUENTE-AXIAL.md` registra fuente programada uniforme terminada con diferencia de velocidad 0 frente al canal de referencia, ejecutada como usuario sin privilegios. Cuatro bandas generan operadores con 32 contrastes algebraicos; fuerza cero generada sigue en comprobación. No hay fuente aplicada al conducto ni mapa instalado aceptado.

Diagnóstico adicional: `ejecucion/G2/flujo_C02_conducto/INFORME-FLUJO-MECANICO.md` verifica flujo nominal de presión total con los campos r8:21,5632W y194,593Pa a20m/s, sin rotor. No es potencia de eje ni cierre RANS. Se corrige la identidad de caudal para usar el área poligonal, no el CAD. MPI4 confirmado con cuatro procesos y contador1037; observar su estado real antes de continuar.

R8 terminó1000, salida0, contenedor detenido. CVfinal0,00679%; continuidad y deriva pasan, residuos p/Ux/Uy/k todavía no. `ejecucion/G2/flujo_C02_conducto/INFORME-R8-TERMINADO.md` registra una continuación separada MPI4 hasta1200 con misma física; cuatro procesos observados realmente, comprobar su estado actual. Los históricos siguen pausados.

`ejecucion/G4/RAE2822/INFORME-SENSIBILIDAD-MODELO.md` compara SST/SA en la misma malla: CL+4,80%, CD+5,38%; todos103puntos retenidos. No es incertidumbre total ni validación del vehículo. Dos tareas digitales siguen cerradas y15parciales; estimación orientativa de trabajo digital alrededor20%, sin prestaciones de vuelo demostradas.

## Ejecución vigente — 3 de noviembre de 2026

## NASA/SU2: estado estable y fuerza de superficie reconstruida

Comprobación tardía finalizada: finaR3 completa600pasos, salida0, CL0,67880791/CD0,01259346 yCpRMS0,123141/103. La variación relativaL2 de k baja a0,0888%; ΔCD tardío2,99e-7. Todos los casos SU2 actuales están terminados; sigue pendiente sensibilidad de modelo/transición/malla y validación. El único solver de flujo nuevo activo esC02r8; comprobar su proceso antes de intervenir.

Resultado posterior: `ejecucion/G4/RAE2822/INFORME-NASA-SU2-FINA-R2.md` registra finaR2 terminada1800pasos adicionales, y+max0,97625, CD0,01259316 y diferencia−3,424% respecto a gruesa. La tracción nativa se reconstruye de forma independiente; k todavía cambia0,479% en normaL2 entre ramas. FinaR3sonda añade600pasos para comprobar el intervalo tardío; verificar proceso. No se cierra validación experimental ni T21.

Actualización del 3 de noviembre de 2026, 23 UTC. `ejecucion/G4/RAE2822/INFORME-NASA-SU2.md` documenta la conversión directa de la malla NASA, condiciones dimensionales alineadas y6200iteraciones SU2 terminadas. La sonda adicional compara todos los campos y conserva cargas casi constantes; la mayor diferencia relativaL2 es4,57e-5 en k. La tracción completa reconstruida coincide con las fuerzas nativas. No equivale a validación experimental: RMS deCp0,12210 sobre103puntos, y+hasta3,308, sensibilidad de malla/modelo y transición pendientes.

La reconstrucción de fronteras características y flujoRoe reduce el defecto de momento a1,866e-4 normalizado porq·c; masa relativa2,45e-11. No se afirma identidad completa del ensamblaje. La malla refinada de97152cuadriláteros termina1200pasos: y+máximo0,976 yCDprovisional−3,438% frente a la gruesa. Se verifican mismo polígono, condiciones, opciones y binario. FineR2añade1800pasos para separar evolución residual de sensibilidad de malla; consultar proceso real. C02r8 continúa, verificado en contador790/1000 conUmax36,310m/s, sin cargas aceptadas. La instantáneaC02r8 de780/800, capturada con el mismo proceso vivo en825, reduce el defectoCV a0,02089/0,01892%; RMSvolΔU0,01222m/s, con cambios locales pendientes. Véase `ejecucion/G2/flujo_C02_conducto/INFORME-SNAPSHOT-R8.md`. Dos tareas digitales siguen cerradas y15parciales; no aumenta la estimación orientativa15–20% ni se acepta velocidad/maniobra. Los dos solvers históricos siguen pausados.

Actualización posterior: `ejecucion/G2/flujo_C02_conducto/INFORME-GRADIENTE-Y-R7.md` identifica la falta de identidad entre gradiente limitado de presión e integral de frontera. En los mismos campos r6 explica casi todo el defecto; una corrida separada r7 conserva grad(p)Gauss y termina500, conCV reconstruido2,072% yUmax38,027m/s. Residuos/derivas no pasan. R8continúa de500a1000 con relajación declarada; verificar su proceso. Doce estados analíticos no uniformes de esfuerzo/flujo pasan, sin validar cargas instaladas.

`ejecucion/G4/RAE2822/INFORME-R5-Y-REARRANQUE.md` rechaza r5LTS por casi vacío y congelación de variables pese a residuos pequeños; r6/r7/r8estacionarios se conservan como fallos de configuración o divergencia. Se añadieron centinelas y parada acotada. SU2 8.6.0 se compiló paraARM64 y completó un caso oficial600/exit0/campos finitos; r2adaptativo permite2000pasos adicionales. Su malla, temperatura y turbulencia difieren deNASA, por lo que aún no hay validación. Dos tareas digitales cerradas,15parciales; objetivo global activo y solvers históricos pausados.

Actualización más reciente: C02r6 terminó300, campos finitos, continuidad mejorada, pero residuos/deriva/Mach local y defectoCV18,78% no aceptados. Solo2celdas superanMref0,3; diagnosticar la interfaz y el esfuerzo no uniforme antes de extender cargas. Véase `ejecucion/G2/flujo_C02_conducto/INFORME-R6-TERMINADO.md`. La prueba uniforme del posprocesado pasó, con alcance limitado.

`ejecucion/G4/RAE2822/INFORME.md` incorpora malla propia365478celdas/MeshOK, piloto100 terminado no convergido y contraste corregido de103presiones. La ordenada NASA es−Cp y su recorrido experimental empieza por el extrados; comparación anterior archivada como inválida. RMS corregido1,19972, sin validación aceptada. Continuación separada r5hasta600 identificada; comprobar proceso real antes de intervenir. Hay2tareas digitales cerradas y15parciales; estimación orientativa15–20% conservada. El objetivo global sigue activo.

`ejecucion/INFORME-AVANCE-2026-11-03.md` registra configuración identificada, discrepancia de ejes CAD/vuelo y conversión verificada, auditoría nominal completa del A07 cerrado, candidata A08 con nueve correcciones locales y cribados condicionados de masa/energía. La referencia canónica continúa siendo A07; sus masas 2/5/10 kg son objetivos. La candidata no se promueve automáticamente ni acredita mecanismo, estructura o flujo.

Blender funciona; FreeCAD se completó en Aplicaciones y ParaView se reparó con la distribución oficial estándar firmada/notarizada. Lectura OpenFOAM, render y escena nativa de ParaView comprobados. Diez benchmarks analíticos pequeños terminaron separadamente; no reanudaron los solvers históricos pausados. Datos experimentales ONERA M6 recuperados, sin solución propia de ese benchmark todavía.

Seguimiento de las 48 tareas: `ejecucion/ESTADO-TAREAS.csv`. No se ha cerrado el objetivo global. Las tablas siguientes conservan evidencia anterior con sus límites; el loft cerrado previo no sustituye la metrología de las 208 piezas A07 ni los mapas pendientes de su instalación.

Actualización C01: `ejecucion/G2/INFORME-C01.md` incorpora contraste de 16 ensayos UIUC con predicción publicada APC (sin validar el BEM propio), 15 diseños de rotor, 45 operaciones anulares condicionadas y cinco verificaciones de ecuaciones/interpolación. Se crearon dos rotores CAD de 5 kg de referencia, con cuatro STEP para ambos sentidos de giro, propiedades de masa/inercia supuestas y render nativo Blender. La prueba de sustitución nominal falla en ambos; son candidatos separados, no rotores ya instalados en A07. El presupuesto acoplado de 54 escenarios conserva motores/equipos pendientes. G2, control instalado y prestaciones permanecen abiertos; el siguiente rediseño debe resolver alojamiento motor–álabes y conducto/ruta axial.

Actualización C02: `ejecucion/G3/C02/INFORME-C02.md` materializa una candidata compacta de 5 kg objetivo: cuatro módulos D82 en x=±160 e y=±76 mm, motor reservado dentro del cubo y transmisión sincronizada de álabes. STEP cerrado de 316 registros, corte de 291 y archivo FreeCAD importado/reabierto sin formas inválidas. Las 314 parejas nuevas de interfaces y 808 parejas en 61 posiciones discretas de tapas no presentan intersecciones en el alcance auditado. A07 sigue canónica; C02 no hereda mapas de flujo ni capacidades de vuelo.

El cribado C02 conserva 44 combinaciones de alojamiento; D102,5 requiere cambios de anchura/disposición. La masa geométrica parcial depende de densidades supuestas y excluye 54 reservas/interfaces sin hardware. Motor, refrigeración, transmisión, tolerancias, cierres, estructura, energía y variantes propias 2/10 kg permanecen abiertos. `configuraciones/C02_CANDIDATA.json` identifica geometría y supuestos; no representa una planta predictiva aceptada.

`ejecucion/G2/benchmark_salto/AUDITORIA.json` añade cuatro contrastes analíticos de `fanPressureJump`: dos configuraciones de una celda longitudinal rechazadas por iteraciones de presión y dos de cuatro celdas aceptadas para este operador/caso, con error normalizado de velocidad de 0,03317%. No es validación de rotor ni flujo instalado. La continuación aporta progreso computacional; G2/G3 y el objetivo global siguen abiertos.

Actualización de flujo C02: `ejecucion/G2/flujo_C02_conducto/INFORME.md` identifica un banco interno pasivo del CAD, 212 superficies y 581.786 tetraedros con Mesh OK. Se conservan malla inicial costosa, fallo de diagnóstico, arranque uniforme rechazado y dos inicializaciones potenciales. Un pico potencial localizado en una celda mantiene fallido el cribado inicial M<0,3. La rama r5 explora el flujo viscoso a20m/s desde esa semilla matemática; no acepta el campo potencial, cargas, potencia o empuje instalado. Consultar su proceso/estado vigente antes de continuar. No hay flujo exterior/rotor, capas prismáticas ni sensibilidad física cerrada; el objetivo sigue activo.

Actualización de contraste y estructura: `ejecucion/G2/benchmark_bem_publico/INFORME.md` verifica17 ángulos CCBlade y coherencia conC01; el contraste propio de16 ensayos UIUC con perfil aproximado da errores medios2,12%CT/9,30%CP, sin validar el rotor instalado. `ejecucion/G5/rotor_C02/INFORME.md` añade144 cribados centrífugos, dos referencias analíticas y72 pares de semejanza; no aprueba material, torsión, raíz orpm.

Actualización terminal C02r5: `ejecucion/G2/flujo_C02_conducto/INFORME-R5-TERMINADO.md` registra100 iteraciones completas, campos finitos y caudal global dentro del criterio, pero residuos/deriva y defecto estacionario reconstruido21,10% no aceptados. R6 deriva del campo100 con resolución lineal de presión estricta y meta300; verificar su proceso antes de continuar. Mapa instalado, potencia, masa, control y prestaciones siguen abiertos. La estimación orientativa de trabajo digital15–20% no es un porcentaje de aceptación física; hay2 de41 tareas digitales formalmente cerradas y14 con avances parciales.

## Evidencia anterior de la arquitectura A elegida

| Frente | Evidencia vigente | Pendiente principal |
|---|---|---|
| Identidad geométrica | CAD A elegido y metrología propia del loft de 1,340 m, 40,09 L y 0,8304 m² | Instalación, paredes, puertas, estructura y masa reales |
| Control estático ideal | Cobertura continua de conos con reservas y revisión independiente para masas supuestas | Mapa instalado de fuerzas, momentos, potencia y respuesta |
| Giro temporal ideal | Nueve perfiles de 5 kg con tasas limitadas; también cumplen cono de 35° | Actuadores, fluido, giroscopía, perturbaciones y otras masas |
| Canal de álabes | Ensayos pareados Euler/backward terminados y auditados; balance de paredes y acumulación | Desarrollo físico, malla/paso/dominio y calibración instalada |
| Chorro exterior | URANS de arranque activo con vigilancia; balance parcial por paso | Terminar diagnóstico y demostrar validez física antes de aceptar cargas |
| Avance rápido | Correlación de fricción condicionada; nueva malla exterior cerrada de 326.013 celdas, geométricamente auditada y Mesh OK | Solución compresible, presión/fricción/base, incidencia y sensibilidad |
| Geometría mejor posible | Comparaciones y alternativas condicionadas | Optimización acoplada con restricciones y mapas verificados; no está demostrada |

Detalles actuales: `modelos_integrados/DECISION-ARQUITECTURA.md`, `CFD/ESTADO-SALIDA-EXTERIOR.md` y `AVANCE-A-TRANSONICO-EVIDENCIA-Y-MALLA.md`.

## Inventario inicial y estudios de otras geometrías

Las filas siguientes conservan el historial de modelos anteriores. Sus recuentos, mapas de rotor, masas y coeficientes no se transfieren automáticamente al CAD A seleccionado.

| Requisito | Estado de evidencia | Pendiente |
|---|---|---|
| Versiones2,5,10kg independientes |324escenarios de masa y motores | Hardware real, volúmenes e integración de cada versión |
| Geometría de mínimo arrastre | Barridos de modelos viscosos, formas de referencia | CFD/túnel, tomas/base, arrastre transónico, optimización multidisciplinar |
| Mach crítico/divergencia | Contraste puntual deCp NASA paraL/D7y10 | Familias comparablesL/D1–8, curvas de arrastre, incidencia |
| Movimiento omnidireccional | Matriz estática, facetas y simulación6DOF | Mapa medido de actuadores, reacción/giroscopía dinámica, todos los estados |
| Empuje reversible | Mapa condicionado324puntos con cobertura explícita | Datos negativos completos y ensayo del rotor |
| Potencia |546asignaciones con perfil y546con reacción | Cota continua, mapas medidos, batería/ESC/temperatura |
| Masa5kg | Auditoría integrada: nueve escenarios exceden5kg con reserva anterior, antes de bujes/mecanismos nuevos | Rediseño, lista completa pesada y cierre iterativo con estructura real |
| Mecanismos | Cargas de pala, par de paso y separación de discos | CADcinemático, rodamientos/retención, fatiga, plegado |
| Sustentación del cuerpo/aletado | TR 1048 revisado; 405 sensibilidades corporales y 945 casos de equilibrio con superficies; sensibilidad de estabilidad | Coeficientes integrados, base abierta, interferencias, trimado y estabilidad dinámica; CFD/túnel |
| Transición | Umbrales de cuerpo solo y reducción algebraica de área con cola; 81 escenarios de paneles e inercia | Trayectoria dinámica, mapa de rotores en avance, transferencia de control, cinemática y cierres |
| 600–1000km/h | 216 secciones de conducto y 36 requisitos de empuje bruto con caudales de catálogo | Mapa de empuje instalado, tomas/escape reales, arrastre total y estabilidad |
| Estructura47kPa y aeroelasticidad | 324 escenarios de viga verificada y 27 paneles; SP-8007 consultado | Cascarón con aberturas, materiales reales, pandeo, uniones, modos libres y flutter |
| Geometrías no convencionales | TN 4117 revisado visualmente; 15 casos anulares con área y Reynolds normalizados | Anillo integrado/transónico, cuerpos sustentadores y mecanismos retráctiles |
| Mejor posible | 99 geometrías, 4455 puntos y Pareto condicional con arrastre, masa superficial e inercia | Ampliar arquitecturas; coeficientes, estructura, propulsión y restricciones verificadas |

No se presentará una simulación de rotor como prueba de aeronave. No se marcará el objetivo completo mientras existan estas carencias. Puede ampliarse el estudio exploratorio, pero eso no sustituye la validación requerida. El informe vigente es `INFORME-CONSOLIDADO-VIABILIDAD.md`.

Auditoría del 30 de octubre de 2026: la consolidación, la búsqueda adicional de mapas y la revisión actual encuentran la misma carencia de datos integrados/medidos. La última búsqueda aportó referencias relacionadas, no mapas directamente aplicables. La inspección actual no localizó CAD integrado ni nueva evidencia de ensayo en el proyecto. El usuario confirmó que esos datos/modelos deben producirse por nosotros, pero todavía no. No se inicia esa etapa ni se interpreta esta decisión como validación del diseño.

La revisión más reciente está en `TRIMADO-Y-GEOMETRIA-VARIABLE.md`. Complementa `TRANSICION-Y-SUSTENTACION.md`: los momentos a incidencia fija no son cargas inevitables del vuelo rápido. El nuevo equilibrio es matemático y condicionado, sin validación de coeficientes integrados. Los umbrales de reducción de área no autorizan una retracción real.

`COMPARACION-INTEGRADA.md` añade dimensionamiento con sensibilidad de estabilidad, arrastre parcial de cuerpo y cola, paneles y frontera no dominada. No debe confundirse el mínimo en el extremo L/D 12 del barrido con un óptimo global ni los extremos de hipótesis con bandas de confianza.

`ESTRUCTURA-PRELIMINAR.md` cuantifica la penalización de alargamiento y separa flexión global de presión sobre paneles. La verificación numérica de la viga no valida la estructura real ni su aeroelasticidad.

`ALA-ANULAR-CONTRASTE.md` incorpora evidencia de túnel a Mach 0,13 y comparación de anillos aislados. La interferencia con el cuerpo y el Reynolds de las variantes pequeñas impiden transferir esa evidencia como validación del vehículo.

`TOMAS-Y-EMPUJE-INSTALADO.md` incorpora caudales publicados y continuidad compresible. El área de paso no es área de captura ni diámetro exterior; el empuje estático menos cantidad de movimiento de entrada se presenta únicamente como sensibilidad, no como mapa de motor.


## Actualización: inicio de CAD integrado, 30-10-2026

El usuario autorizó ahora crear modelos y preparar mediciones. La postergación anterior queda superada para esta etapa. Se generaron modelos paramétricos de integración de 5 y 10 kg en `modelos_integrados/`, con STEP, masas asignadas, centros, tensor provisional y comprobación de interferencias. Véase `modelos_integrados/PROTOCOLO-MEDICIONES.md`. No existen todavía medidas físicas ni mecanismo de retracción validado; las masas objetivo no están cerradas.


## Hallazgo al recalcular control desde CAD

`modelos_integrados/CONTROL-DESDE-CAD.md` documenta una pérdida de autoridad de momento al combinar L/D=6, estaciones ±L/4 y los ejes heredados. La disposición actual de los renders no puede heredar la viabilidad estática calculada para otra geometría. 108 escenarios y 1080 verificaciones LP confirman el resultado del modelo ideal; se requiere rediseño de posiciones/ejes y comprobación conjunta de holguras e inercias.


## Candidato posterior con ejes revisados

`modelos_integrados/CANDIDATO-EJES-REVISADOS.md` documenta una búsqueda de dos ángulos, regeneración CAD, actualización de CG/inercia y 108 escenarios de control. Mejora sustancialmente la autoridad estática ideal sin intersecciones adicionales desplegadas. No demuestra óptimo global, empuje reversible disponible, retracción o viabilidad de alta velocidad. El candidato se conserva separado en `modelos_integrados/candidato_ejes/`; los renders anteriores no muestran estos nuevos ejes.


## Masa distribuida de palas y cargas de giro

`modelos_integrados/INERCIA-Y-CARGAS-DE-GIRO.md` corrige la concentración de palas en el motor, recalcula el tensor y añade cotas conservadoras de Euler/giroscopía con desajustes de RPM. La cancelación global ideal no elimina las cargas locales. Los resultados siguen condicionados a masas y mapas no medidos; las capacidades suficientes con velocidad angular no deben confundirse con mínimos exactos.


## Contraste del candidato con el dominio de rotor

`modelos_integrados/DOMINIO-ROTOR-Y-MANIOBRA.md` enlaza la geometría revisada y masa 5,498 kg con los límites asimétricos del mapa de 6000 rpm. Distingue el mapa condicional completo del filtro de contribución fuera de polar. No se extrapola a 10 kg ni se equipara un mapa aerodinámico con prestaciones de motor instalado. Faltan reacción de rotor, potencia y respuesta temporal para el mismo reparto.


## Reacción y potencia para el mismo candidato

`modelos_integrados/REACCION-POTENCIA-CANDIDATO.md` añade el par de reacción del mapa de rotor y optimización local de consumo en 1092 demandas muestreadas. Se verificaron directamente 1032 soluciones; 60 fallos de búsqueda no prueban inviabilidad global. La estimación energética es un cociente condicionado, no autonomía validada ni cobertura dinámica continua.


## Clasificación global de fallos de asignación

`modelos_integrados/VERIFICACION-GLOBAL-ASIGNACION.md` reemplaza la incertidumbre numérica de los 60 fallos locales: una solución recuperada y 59 casos inviables dentro del mapa interpolado restringido, no en toda la física posible. La formulación por segmentos adyacentes se comprobó contra 486 puntos positivos. El grupo restringido de fuerza/peso=2 queda en 123/182 con equilibrio encontrado.


## Recorrido de paso e inversión de aceleración

`modelos_integrados/INVERSION-PASO-REQUISITOS.md` calcula extremos equilibrados y recorridos de paso para inversiones ±0,5/±1 g. Los tiempos recorrido/velocidad son hipotéticos, no respuesta física. La interpolación lineal de paso introduce errores de fuerza y momento; queda pendiente la trayectoria coordinada y la dinámica real. La búsqueda global agotó tiempo y no certifica optimalidad.


## Arquitectura A seleccionada: vectorización ideal

La decisión vigente está en `modelos_integrados/DECISION-ARQUITECTURA.md`. `modelos_integrados/vectorizacion_A/INFORME.md` estudia cuatro fuerzas vectoriales internas de cono ascendente: cobertura muestreada, límites geométricos y exigencia de empuje útil. No introduce una capacidad de aletas medida, una salida de flujo ya alojada o cobertura a cualquier actitud. Se mantiene el objetivo de prototipo virtual y el requisito de cerrar mecanismos, potencia y flujo.


## Alojamiento geométrico de filas vectoriales A

`modelos_integrados/vectorizacion_A/CAD_modulo/LEEME.md` documenta dos filas ortogonales de álabes, 168 posiciones y 24 prismas de barrido contenidos en la envolvente. Se exportaron y reimportaron módulos neutros/desviados y una rama de integración con pasos inferiores. No se ha validado el ángulo del chorro, el par aerodinámico ni el alojamiento de servos/transmisiones.


## Primera ejecución CFD del conducto A

`CFD/ESTADO-CFD.md` registra instalación verificada de OpenFOAM 13, corrección de orientación neutra, mallas de 181015/170277 celdas que pasan checkMesh y ejecuciones neutra/desviada. Ninguna cumple todos los residuos exigidos: las cargas quedan como diagnósticos, sin aprobar servos ni mapas de control. Se requiere estudio de pared/malla, dominio y posible formulación transitoria.


## Cálculo transitorio del conducto A

`CFD/ESTADO-TRANSITORIO.md` documenta una continuación URANS desde los campos estacionarios, corrección de metadatos heredados y avance físico comprobado. El objetivo de integración es 0,03 s, con control adaptativo de Courant y auditoría de cargas posterior. Consultar el proceso real antes de reanudar o volver a lanzar: no se aceptan todavía medias o mapas del mecanismo.

Actualización del 1 de noviembre: esa continuación v2 fue detenida ordenadamente y **rechazada** tras colapso del paso temporal y crecimiento no físico de velocidades/cargas; código cero no significó simulación terminada. La evidencia está en `CFD/transitorio_X35_Y-35_h0.006/REJECTION_AUDIT.json`. Se inició un diagnóstico independiente Euler/upwind de 0,001 s, con controles más conservadores; esa ventana no permite estadísticas de cargas. La selección de la arquitectura A sigue vigente, sin validación aerodinámica ni cierre del objetivo global.

El diagnóstico Euler/upwind terminó en 903 pasos, t=0,001 s y 536 s de reloj, sin colapso del paso y con campos finales finitos. `CFD/diagnostico_Euler_upwind_X35_Y-35_h0.006/STABILITY_AUDIT.json` documenta la comprobación. Sus cargas siguen sin aceptarse: solo cubre 0,276 tiempos de paso y no llega al descarte inicial. Los contenedores de estas ejecuciones están detenidos; no hay cálculo activo que deba recuperarse ni un bloqueo externo que impida continuar los estudios numéricos.

## Coherencia local de conductos y cribado de área de la arquitectura A

`modelos_integrados/vectorizacion_A/CAD_integracion_coherente/VERIFICACION.json` registra la consolidación de las camisas y conductos, 101 piezas válidas reimportadas, ausencia de intersección local rotor/conducto y separación radial geométrica mínima aproximada de 0,988 mm. No constituye revisión global de interferencias ni aceptación de tolerancias, cargas o fabricación.

`modelos_integrados/vectorizacion_A/area_y_escala/INFORME.md` calcula referencias de área y potencia para escalas algebraicas de 2/5/10 kg. La potencia de cuatro rotores libres ideales de área equivalente es aproximadamente 518/1509/3387 W en estacionario sin maniobra. Son referencias de modelo declarado, no potencia eléctrica instalada ni cota universal de un ventilador carenado. No cierran motor, batería o autonomía.

## Dominio continuo de control, respuesta ideal y variante de doble salida

Actualización del 1 de noviembre: la continuación anterior produjo progreso verificable (corrección CAD y diagnóstico CFD terminado). Esta etapa también produce progreso: `modelos_integrados/vectorizacion_A/reversibilidad_6DOF/INFORME.md` y sus datos distinguen el movimiento 3D con cuerpo horizontal del vuelo en cualquier actitud; no se impone vuelo invertido como requisito nuevo. Se calcularon cotas suficientes continuas mediante poliedros interiores de conos individuales y un dominio exterior de fuerzas × caja de momentos, manteniendo signos fijos sin mezclar conos de un mismo fan.

La revisión independiente contrasta 15.360 vértices guardados en diez condiciones y 48.048 estados de trayectorias ideales, además de coordenadas de bancos del STEP. La exportación inicial del modo horizontal omitía el centro mg en los targets guardados; la auditoría la detectó y quedó corregida/regenerada, con copia histórica separada. Los resultados actuales pasan; esto verifica el modelo matemático, no las fuerzas físicas del vehículo.

Se añadieron asignaciones que minimizan una referencia convexa de potencia de rotor libre con comprobación KKT, y comparaciones que reparten cambios de fuerza con dualidad de LP. Las rampas de 50–500 ms producen demandas de respuesta; no simulan motor, servo, flujo transitorio o vuelo. Incluyen escenarios de 1, 2 y 5 g de empuje reversible, para no confundir el escenario inicial de 0,5 g con el objetivo final de máxima agilidad.

`modelos_integrados/vectorizacion_A/CAD_doble_flujo/` contiene una rama opcional de bancos a ambos lados del rotor: dos STEP de 149 piezas válidas, 48 barridos conservadores comprobados y comprobaciones locales de ejes/ductos/motores. Faltan accionamientos, buje reversible, rodamientos/sellos, tolerancias y revisión global de montaje. El modo A seleccionado sigue siendo la base; no se presenta esta variante como elección adicional del usuario ni como producto funcional.

El objetivo completo continúa sin lograrse: se requiere mapa realista instalado de fuerza/momento/potencia/dinámica, cierre de masa/CG/inercia, estructura y aeroelasticidad, integración de alta velocidad, comparación global de geometrías y simulación/autonomía calibrada. Hay trabajo numérico disponible; no se cumple un bloqueo externo ni procede marcar el objetivo completado.

## Metrología de avance, tapas y paso axial de la arquitectura A

Continuación con progreso: `modelos_integrados/aerodinamica_A/METROLOGIA.json` mide el loft cerrado mediante integración adaptativa y contrasta el volumen con dos conjuntos de secciones, además de elipsoide analítico y triangulaciones. El volumen bruto es 40,09 L y la superficie cerrada 0,8304 m². No equivale a una carcasa de pared/material definidos ni al vehículo completo de 53/101/149 piezas.

`INFORME-AVANCE-Y-TAPAS.md`, `AVANCE_Y_TAPAS.json` y sus CSV contienen nueve escenarios de fricción de referencia, 288 escenarios lineales de discos y 72 espesores de cribado. La fricción usa una correlación de placa lisa turbulenta verificada en DLR IB 124-2010/3, no un solver compresible de la forma A. Los discos son sustitutos planos con propiedades y presión diferencial supuestas, dos apoyos y exclusión de validez lineal para flechas grandes; la fórmula reproduce un benchmark Ansys/Roark. No validan arrastre total, puertas curvas, cierres, resistencia o flutter.

El contraste geométrico de tubos coaxiales con las cuatro camisas del STEP verifica el límite local de 42 mm de diámetro exterior. Con 2 mm de pared supuesta el paso interior sería 38 mm sin margen. Esta evidencia cambia la siguiente acción: resolver ruta/bahía del propulsor rápido antes de heredar la idea de un conducto recto nariz–cola.

Se verificó el registro de NASA TM-X-3129 sobre cuerpos elípticos; la descarga local del PDF falló sin transferencia y el lector web rechazó su tamaño. No se inventaron datos de figuras. La consulta de esa fuente sigue pendiente para comparación cuantitativa, pero no bloquea el trabajo restante de geometría/flujo. No se demuestra óptimo global ni se cierra el objetivo.

## Redistribución acoplada de estaciones, alojamiento y control

Esta continuación aporta progreso: `modelos_integrados/empaquetado_axial_A/` contiene una búsqueda finita de estaciones con mecanismos conservadores de doble flujo dentro de la misma envolvente. Se calculó control solo después de pasar el alojamiento, con prefiltrado geométrico explícito. Los resultados no constituyen un óptimo global entre formas o entre todos los pares de estaciones.

Tres alternativas dejan reservas axiales exteriores de 38/60/80 mm. La de 80 mm utiliza x=±100, y=±86 mm en la escala de referencia de 5 kg supuestos. Sus mecanismos del STEP, cajas de barrido completas en los cuatro canales y reserva axial pasan las comprobaciones locales. Se exportaron tres STEP de 110 piezas válidas cada uno. No contienen motor, ruta completa de toma/tobera, pared/material funcional o apoyos/accionamientos cerrados.

Se recalculan dominios ideales de fuerza/momento por posición y se contrastan momentos puros a una misma capacidad útil de 21 N por ventilador. El cabeceo y la tolerancia longitudinal al CG se reducen cuando las estaciones se acercan, aunque se abra el paso axial. Los escenarios reversibles añaden cualquier actitud a 0,5 g y aceleraciones de 5 g con cuerpo horizontal, como exigencias del modelo y sin demostrar disponibilidad de propulsión.

La evidencia orienta el siguiente trabajo hacia presupuesto de masa/CG/inercia y ruta/huella del propulsor, junto con mapas de fuerza/momento/potencia verificados. No se cierra velocidad, autonomía, estructura o maniobrabilidad real. El objetivo sigue activo y no se cumple un bloqueo externo.

## Distribución de masa y giro ideal con gravedad transformada

Nueva continuación con progreso: `modelos_integrados/empaquetado_axial_A/masa_y_agilidad/` integra propiedades de material de los STEP de reserva y una piel superficial equivalente, comprueba caja trasladada y cáscara esférica analíticas, y genera 36 escenarios de 5 kg supuestos. No se cuentan los volúmenes representativos de motores/rotores como si fueran masas materiales verificadas. El equipo residual completa aritméticamente la masa objetivo, sin acreditar alojamiento o componentes disponibles.

Se estudia un giro prescrito de 30° con posición inercial constante y fuerza de gravedad transformada con la actitud. Se usa la inercia de cada escenario y se exigen reservas simultáneas de momento a través de LP por nodo, sin tratar el momento de hover horizontal como constante en toda la rotación. Se refinaron tres casos de 61 a 241 nodos y se reconstruyeron perfiles nominales con margen temporal de 1 %, comprobando el tensor completo y los balances de Newton–Euler en 481 instantes.

Los datos actuales son consistentes con el modelo ideal; no constituyen simulación de respuesta de rotor/servo/flujo ni prueba continua entre nodos. Se registran cambios de fuerza de las asignaciones LP: la suavidad del perfil corporal no garantiza mandos suaves. El cierre requiere imponer tasas y dinámica, caracterizar fuerzas/momentos/potencia, masa/CG/inercia, estructura y propulsión rápida. Las conclusiones de casos hipotéticos no se extienden al rango completo de masas ni completan el objetivo global.

## Asignación temporal conjunta y propagación de estados

Continuación con progreso: `modelos_integrados/empaquetado_axial_A/masa_y_agilidad/tasas/` contiene LP dispersos con cambio de fuerza limitado, nueve perfiles seleccionados tras comprobar 41/81 nodos e integración directa de posición, velocidad, cuaternión y velocidad angular. Los 35 LP de búsqueda terminaron como factibles o infactibles en el modelo, sin tiempos agotados; los nueve perfiles nominales pasan la verificación de límites e integración ideal.

Las fuerzas lineales por intervalos cumplen continuamente capacidad, cono, precarga y cota vectorial de tasa gracias a convexidad. Su demanda no lineal de fuerza/momento se aproxima entre nodos y produce una desviación de estados cuantificada. El integrador pasó pruebas analíticas y un refinamiento numérico. Nada de ello demuestra precisión física: faltan la planta instalada, geometría de accionamientos, límites de aceleración/potencia y respuesta de rotor/servo/flujo.

La comparación conserva el carácter condicionado de las masas y de la maniobra prescrita; no encuentra un tiempo mínimo global ni demuestra el objetivo de 600–1000 km/h. Las reservas de perturbación anteriores se comprobaron instantáneamente, no con restricciones conjuntas de tasa de corrección. El objetivo sigue activo y hay trabajo de caracterización y diseño por computador disponible.

## Comparación pareada de esquema temporal en curso

La continuación anterior fue una espera verificada: Docker y registros confirmaron ambos solvers vivos. Esta continuación aporta progreso mediante `CFD/comparar_esquemas_temporales.py`, pruebas analíticas y extracción de series sin modificar los procesos. `CFD/INFORME-COMPARACION-PARCIAL.md` compara las cargas a tiempos coincidentes y conserva la falta de desarrollo físico.

La ventana parcial 0,00005–0,00050 s muestra diferencias de componente de fuerza RMS de hasta aproximadamente 0,00214 N; no son incertidumbre física ni aceptación de álabes. Los procesos siguen vivos, se mantiene el objetivo de 0,0015 s y falta comprobar los resultados finales, sensibilidad de malla/paso y balance instalado completo. El objetivo global permanece activo y no demostrado.

## Reacción completa del canal aislado

`CFD/INFORME-REACCION-CONDUCTO.md` (desde modelos_integrados: `../CFD/`) registra una nueva integración de paredes y álabes sobre un campo guardado de Euler, sin alterar las ejecuciones activas. Las seis transformaciones de momento a origen común y las particiones de cargas pasan comprobaciones con tolerancias de redondeo.

En ese campo aún no desarrollado, la magnitud lateral pasa de 6,976 N sobre álabes a 2,110 N sobre todos los sólidos del dominio. No es una eficiencia física validada; evidencia que las cargas locales no bastan para calibrar el cono instalado. La acción siguiente debe incluir salida exterior, reacción del conducto y balance transitorio de cantidad de movimiento, además de desarrollo y sensibilidad numérica. El cono efectivo de 45° permanece supuesto y la arquitectura A elegida se conserva. El objetivo completo continúa sin demostrarse.

## Balance integral transitorio y dominio exterior

La continuación anterior aportó progreso mediante integración independiente de paredes y álabes. En esta continuación se evaluaron volumen, flujo convectivo y tracción total sobre tres campos guardados (0/0,00025/0,00050 s), sin modificar el solver original. `CFD/INFORME-BALANCE-MOMENTO.md` registra un residuo integral medio de norma 0,01809 N (0,383 % normalizado). El cambio de cuadratura de dos a tres campos es mayor que el residuo; no se declara cierre convergido ni exactitud física. La acumulación lateral es relevante y no debe omitirse.

`CFD/mallar_salida_exterior.py` inició una malla del conducto antiguo con aire exterior, radio 0,336 m y longitud aguas abajo del labio 0,504 m. La sesión de ejecución 74494 permanece activa en la última consulta; aún no se ha confirmado su terminación. La carpeta es `CFD/salida_exterior_X35_Y-35_h0.006`. No reiniciar ni interpretar una carpeta vacía como proceso detenido. `auditar_malla_exterior.py` queda preparado para verificar volúmenes y tetraedros cuando termine; aún no se ejecutó. No hay solución de flujo exterior.

Ambos foamRun pareados se confirmaron activos por Docker; último avance observado aproximadamente 0,000968 y 0,000959 s, objetivo relativo 0,0015 s. Permanecen en sus contenedores originales. El objetivo global sigue activo; faltan caracterización instalada, propulsión, masa/energía, estructura, aerodinámica compresible y comparación óptima.

La malla exterior terminó: 1.263.510 tetraedros. `GEOMETRY_AUDIT.json` verifica volúmenes OCC frente a fórmula independiente y orientación positiva de todos los tetraedros; la aproximación poligonal difiere un 0,1314 % en volumen. La sesión 74494 terminó. La conversión OpenFOAM y `checkMesh -allGeometry -allTopology` están en ejecución con sesión 76689, contenedor `codex-aero-exterior-mesh-v1`; no se ha lanzado flujo. No reiniciar la conversión por una consulta que ceda el control.

La búsqueda de la versión alternativa del ensayo NASA TM-2020-220484 confirmó el registro y un enlace alternativo; el lector web agotó tiempo y curl falló por negociación TLS. No se extrajeron coeficientes ni figuras y no se usan como datos de validación. Fuente oficial localizada: https://rotorcraft.arc.nasa.gov/Publications/files/Narbuntas_TM-2020-220484_102820.pdf .

## Arranque URANS con dominio exterior

La continuación anterior fue progreso: balance integral y malla exterior. En esta continuación terminó `checkMesh` con Mesh OK y se inicializó U/phi mediante potencial, comprobando finitud y continuidad. Apareció un máximo inicial de 226,93 m/s cerca de un álabe (Mach supuesto 0,667 para a=340,3 m/s): no se acepta el campo como solución incompresible física.

Se inició una prueba corta de arranque con tiempo objetivo 0,00025 s, Euler/upwind, dos PIMPLE, maxCo=0,3. Se confirmó foamRun vivo por Docker top. Solver: sesión 23250, contenedor `codex-aero-exterior-urans-v1`; vigilante sesión 36522. `CFD/ESTADO-SALIDA-EXTERIOR.md` documenta configuración, límites y procesos. Ninguna fuerza se considera instalada o validada. El contenedor auxiliar `codex-aero-exterior-mesh-v1` se detuvo deliberadamente después de inicializar; no confundirlo con el nuevo solver activo.

Los solvers pareados anteriores siguen en sus contenedores originales; último avance observado aproximadamente 0,001289/0,001284 s, objetivo 0,0015 s. No se reiniciaron. El objetivo global continúa activo: ni el cálculo de arranque ni la calidad de malla demuestran prestaciones u óptimo global.

### Terminación confirmada de los dos ensayos pareados

Después de la consulta anterior terminaron ambos foamRun: las sesiones 17077 y 40084 devolvieron éxito y los run_state registran objetivo t=0,0015 s alcanzado. El vigilante confirma ambos contenedores detenidos sin razones de catástrofe. `auditar_final_pareados.py` verificó seis campos finales finitos, campos iniciales idénticos, cambio aislado de esquema y retención de estadísticas por descarte físico no alcanzado.

`CFD/ESTADO-COMPARACION-PAREADA.md` sustituye el estado en ejecución por la auditoría final. En 0,00005–0,0015 s, máximo RMS de diferencia de componente de fuerza 0,004214 N y de par local de bisagra 6,229e−6 N·m. No demuestra independencia de paso ni validación física. La única simulación de flujo activa de esta rama es ahora la exterior, sesión 23250, con vigilante 36522. No reiniciar los pareados ya terminados.

## Sensibilidad del cono efectivo con cuerpo horizontal

La continuación anterior aportó progreso con auditoría final pareada e inicio exterior. Esta continuación añade límites analíticos necesarios y seis certificados de cobertura continua del modelo ideal, con 9.216 vértices verificados independientemente en `modelos_integrados/vectorizacion_A/sensibilidad_angulo/`. Se contrastan 35°/40° con la referencia anterior de 45° para 2/5/10 kg. Las capacidades útiles suficientes por ventilador permanecen aproximadamente 8,029/20,578/42,155 N para el escenario de bola de aceleración de 0,5 g y sus reservas declaradas. No es empuje instalado ni motor disponible.

La bola tridimensional de aceleraciones de radio 0,5 g centrada en hover requiere al menos 30° de dirección efectiva bajo empujes de signo positivo; la sección de aceleración horizontal pura solo requiere 26,565°. El límite necesario no prueba suficiencia con reservas y los certificados no encuentran el mínimo ángulo ni la agilidad máxima. El objetivo de máxima agilidad y vuelo rápido se conserva. La gráfica se renderizó y revisó visualmente; el informe explica por qué los perfiles temporales anteriores de 45° no se transfieren automáticamente a 35°.

El solver exterior se confirmó vivo con Docker top, sin reiniciarlo. Sus archivos de diagnóstico muestran caída del pico inicial de 226,93 a aproximadamente 116,20 m/s a t=0,00001651 s. No hay desarrollo ni cargas aceptadas. Se habilitó log=true de los diagnósticos, pero no se confía en el registro para observar el máximo: un vigilante complementario lee directamente `postProcessing/maxVelocityDiagnostic/0/volFieldValue.dat`. Su sesión es 29596 y guarda `WATCHDOG_FIELDS_STATE.json`; el vigilante de paso/log 36522 permanece activo. Ambos apuntan al mismo solver 23250 y al contenedor `codex-aero-exterior-urans-v1`.

El objetivo global sigue activo y no acreditado. Estos resultados no demuestran cierre de masa/potencia, estructura, velocidad transónica, respuesta real ni óptimo global.

## Conos en las trayectorias y balance exterior por paso

La continuación anterior aportó progreso con seis certificados estáticos de cono y vigilancia por archivo. Esta continuación verifica las nueve fuerzas temporales ya guardadas de las candidatas 38/60/80 mm de 5 kg: el máximo ángulo útil es 33,75°, por lo que las mismas fuerzas, tasas y estados ideales cumplen conos de 35°/40°. No se repitieron LP ni se modificaron trayectorias. `modelos_integrados/empaquetado_axial_A/masa_y_agilidad/tasas/sensibilidad_cono/INFORME.md` conserva prueba por convexidad, comprobación de Newton–Euler y hashes. No valida mecanismos ni extiende tiempos a otras masas.

La instantánea `CFD/snapshots_exterior_1` permitió balance integral sobre 54 registros completos comunes entre 5,0615e−6 y 3,02387e−5 s. El residuo por extremo derecho es 0,0002571 N (0,002357 % normalizado); con trapecios 0,006155 N (0,05642 %). No son incertidumbres físicas ni prueba de convergencia. La acumulación axial es significativa (−6,462 N); no se interpretan fuerzas estacionarias. `CFD/INFORME-BALANCE-EXTERIOR-PARCIAL.md` detalla límites y método. El objetivo global sigue activo y faltan los cierres previamente declarados.

## Rama compresible de avance sobre la geometría A

La continuación anterior aportó progreso mediante revisión de trayectorias de cono y balance exterior por paso. Esta continuación descargó y revisó visualmente la fuente primaria NACA 19790079920 (Wetmore, 1947), figuras 9–12 y texto de cuerpos: las curvas corresponden a caída libre con colas y a wing-flow, no a nuestro objeto. Se conservan PDF, renders, hash y procedencia en `fuentes/naca_transonico/`. No se digitalizaron curvas ni se obtiene de ellas un Mach crítico del CAD A.

Se generó una malla 3D de la envolvente cerrada medida: 326.013 tetraedros, volumen/área del cuerpo discretizados a 0,00403/0,00287 % del CAD, pared cerrada y tetraedros positivos. `checkMesh -allGeometry -allTopology` terminó con Mesh OK, sesión 41695 completada. Archivos en `CFD/avance_A_cerrada_h0.008/`. No se inició flujo compresible. El contenedor auxiliar `codex-aero-avance-mesh-v1` se reinició solo para consultar fuentes y ejemplos de OpenFOAM13; está inactivo de solver y se detendrá tras la consulta.

`AVANCE-A-TRANSONICO-EVIDENCIA-Y-MALLA.md` conserva alcance, fuente y tareas de presión/compresibilidad. Se corrigió el encabezado de esta auditoría para separar la evidencia vigente A de inventarios de otras geometrías y evitar tratar componentes pendientes como bloqueo externo. El objetivo global sigue activo, sin prueba de optimalidad ni de prestaciones completas.

## Primer arranque compresible sobre la envolvente A

La continuación anterior aportó progreso con malla completa de A y fuente NACA. En esta continuación se preparó el modelo de gas perfecto y contornos a 600 km/h, contrastados con ejemplos/fuentes instaladas. El arranque estacionario divergió: se rechazó con auditoría. Dos errores de preparación del primer arranque transitorio se conservaron y corrigieron sin reutilizar campos fallidos.

El diagnóstico v3 usa tiempo físico Euler/CFL, ha completado pasos con p/T positivas y sigue en el contenedor `codex-aero-avance-compresible-600-euler-v3`, sesión 24226. Objetivo 1e−4 s, solo 0,0124 recorridos de la longitud: ninguna carga estacionaria aceptada. `CFD/ESTADO-AVANCE-COMPRESIBLE.md` conserva modelo, fallos, límites y próximos controles. El ensayo exterior de álabes sigue en `codex-aero-exterior-urans-v1`, sesión 23250, vigilantes 36522/29596.

La inspección de fuentes confirmó soporte de LTS como posible método de convergencia estacionaria; aún no se activó. El objetivo global sigue activo y no demostrado.

### Arranque compresible terminado y paso local iniciado

El diagnóstico físico v3 terminó con 144 pasos y alcanzó 1e−4 s. `FINAL_STARTUP_AUDIT.json` verificó U/p/T finitos y p/T positivos en las 326.013 celdas. El máximo Mach interior derivado es 0,64599, sin celdas interiores sónicas en ese campo inicial; no es Mach crítico ni prueba de vuelo desarrollado. La fuerza instantánea de presión de arranque no se usa como arrastre estacionario.

Se inició LTS desde ese campo finito auditado, en `CFD/avance_A_compresible_600kmh_LTS_diag`, sesión 16295, contenedor `codex-aero-avance-compresible-600-lts-v1`, objetivo 200 iteraciones locales. No representan tiempo físico. La sesión v3 24226 está completada, no reiniciarla. El solver de álabes exterior 23250 sigue vivo con sus vigilantes. Ninguna carga se acepta todavía; continúan los pendientes de validación, integración y óptimo global.

## Cribado de convergencia LTS y continuación

La continuación anterior aportó progreso al terminar el arranque compresible físico e iniciar LTS. Esta continuación terminó y auditó las 200 iteraciones LTS: campos finitos/positivos, pero fallan residuos iniciales de primera corrección, deriva/rango de cargas y balance de masa a escala corporal. `CFD/INFORME-CONVERGENCIA-AVANCE-A.md` documenta criterios elegidos y diferencias entre pequeños residuos lineales y convergencia global.

Se conservaron campos 125/150 y su comparación muestra cambios máximos de 32,456 m/s, 4198,20 Pa y 5,026 K. No se acepta arrastre. Se verificó el lector ASCII con fixtures conocidos y casos inválidos. Los JSON conservan hashes.

Se inició la continuación `CFD/avance_A_compresible_600kmh_LTS_cont_1000`, contenedor `codex-aero-avance-compresible-600-lts-cont-v1`, sesión 54702, objetivo 1000 iteraciones nuevas desde el campo 200 auditado. La sesión 16295 está completada y el contenedor original se detuvo normalmente. El solver exterior de álabes y sus vigilantes siguen en sus procesos originales. El objetivo global permanece activo: esta continuación no demuestra prestaciones ni óptimo global.
