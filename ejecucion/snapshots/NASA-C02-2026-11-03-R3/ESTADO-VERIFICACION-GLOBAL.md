# Auditoría del objetivo global

Referencia de planificación actual: [Plan maestro de cierre](plan_maestro/PLAN-MAESTRO.md), 2 de noviembre de 2026. La auditoría siguiente conserva observaciones históricas y sus actualizaciones; el plan identifica qué resultados pueden reutilizarse y sus límites. Su creación no reanuda solvers ni acredita el cierre del proyecto.


Objetivo conservado: encontrar la geometría/arquitectura más favorable para 2–10 kg, omnidireccionalidad brusca y 600–1000 km/h, cuantificando mecanismos. No se ha demostrado optimalidad global ni viabilidad de toda la misión. Los componentes y sus mapas aún deben diseñarse y caracterizarse; hay trabajo computacional pendiente. El 3 de noviembre de 2026 el usuario activó el objetivo de completar el plan maestro y autorizó comenzar su ejecución. `DATOS-PARA-CERRAR-VALIDACION.md` enumera carencias, no un impedimento para seguir diseñando.

Estado de seguimiento vigente: ejecución del plan maestro activa desde el 3 de noviembre de 2026. Se inspeccionaron los dos contenedores CFD históricos: continúan vivos y pausados; no se duplican ni reanudan automáticamente. Los nuevos benchmarks pequeños son casos separados. Las menciones de pausa/ejecuciones activas posteriores en el historial deben interpretarse con su fecha y configuración. La entrega A03 fue una tarea independiente que no reanudó aquellos cálculos. El objetivo activo sigue sin completarse.

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
