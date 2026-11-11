# Informe consolidado de viabilidad

Consolidación: 30 de octubre de 2026.

## Dictamen

**No hay todavía una configuración de 2, 5 o 10 kg que haya demostrado simultáneamente estacionario omnidireccional abrupto, transición controlada y 600–1000 km/h. Tampoco se ha demostrado una geometría óptima global.** Hay modelos reproducibles que cuantifican compromisos y permiten rechazar algunas conclusiones preliminares. No son pruebas de vuelo ni planos para fabricar.

La arquitectura candidata es un cuerpo circular alargado, propulsión axial para avance, actuadores distribuidos para estacionario y superficies de sustentación/control adaptadas a cada régimen. El número de rotores, su retracción y la forma final siguen sujetos al cierre integrado. El anillo se conserva como alternativa de transición, sin validación transónica.

L/D 6 es una referencia común, no un óptimo demostrado. El estudio de control de rotores más detallado usa L/D 4: sus prestaciones no pueden trasladarse automáticamente a L/D 6.

## Familia de referencia

| Masa objetivo | Largo × diámetro corporal, L/D 6 | Estado |
|---|---|---|
| 2 kg | 0,883 × 0,147 m | Sin componentes completos ni propulsión rápida validada |
| 5 kg | 1,198 × 0,200 m | Mayor detalle de rotor/componentes; presupuesto integrado anterior no cierra |
| 10 kg | 1,509 × 0,252 m | Sin cierre de componentes, control y empuje instalado |

Volumen exterior supuesto: masa / 200 kg/m³. Las dimensiones no prueban empaquetado después de instalar conductos, depósitos y mecanismos. Ninguna fila representa un prototipo listo para construir.

## Tres niveles de evidencia

- **Documental:** ensayos originales y especificaciones publicadas, dentro de sus condiciones. Un perfil o anillo aislado no equivale al vehículo.
- **Numérica:** integración geométrica, asignación de fuerzas, equilibrios, contabilidad de masa y modelos estructurales. Convergencia y residuos pequeños verifican implementación, no exactitud física.
- **Hipótesis:** coeficientes integrados, eficiencias, materiales, masa de mecanismos, recuperación de toma y márgenes. Sus extremos no son intervalos de confianza ni garantías.

## Corrección decisiva del presupuesto de 5 kg

El presupuesto anterior sumaba 3,460 kg de reactor, motores, combustible, piel, brazos/cierres, electrónica, instalación y reserva. Con batería estimada de 0,754 kg y 0,560 kg supuestos para palas, ESC y servos, quedaban **0,226 kg para bujes y partidas restantes**, conservando una reserva de 0,250 kg dentro del subtotal.

Las superficies L/D 6 del estudio integrado añaden 0,344 kg con masa superficial supuesta de 1 kg/m², antes de actuadores y refuerzos nuevos. Reemplazando la piel anterior sin contarla dos veces:

| Escenario de piel L/D 6 | Subtotal con reserva anterior | Todavía no incluido |
|---|---:|---|
| Asignación anterior de 350 g | 5,118 kg | Bujes y mecanismos nuevos |
| Cascarón isotrópico hipotético de 0,2 mm | 5,090 kg | Bujes, mecanismos y validación estructural |
| Cascarón isotrópico hipotético de 0,5 mm | 5,574 kg | Bujes y mecanismos nuevos |

No son masas finales ni límites inferiores universales: contienen asignaciones y reserva. Eliminar la reserva liberaría 250 g, pero no demuestra que quepan las piezas faltantes. Aumentar la masa obliga a recalcular potencia, fuerzas, superficies y batería. Aquí se auditó contabilidad a demanda congelada, no otro equilibrio iterativo.

**Decisión:** retirar la afirmación de margen de masa del candidato anterior cuando se le incorporan estas superficies. Hay que rediseñar componentes/arquitectura o negociar prestaciones. Esto no descarta toda aeronave de 5 kg.

Reproducción: [auditoria_masa_consolidada.py](../scripts/auditoria_masa_consolidada.py). Nueve escenarios en `resultados/masa_consolidada_5kg_ESCENARIOS.csv`; desglose en `resultados/masa_consolidada_5kg_RESUMEN.json`.

## Omnidireccionalidad y mecanismos

El rotor más estudiado tiene diámetro 457,2 mm, dos palas SD8020 de cuerda 30 mm y paso variable. Ocho unidades se modelaron sobre un cuerpo de 0,914 × 0,229 m y masa fija de 5 kg. Los datos de perfil proceden de [UIUC](https://m-selig.ae.illinois.edu/pd.html); parte de la rama inversa queda fuera del dominio experimental.

Las solicitudes discretas con par de reacción dieron máximos muestreados de unos 1,20, 1,80 y 2,52 kW para fuerzas resultantes de una, una y media y dos veces el peso, con reserva de control. No son autonomías ni máximos garantizados en toda dirección.

La auditoría continua simplificada sin reacción, con límites condicionados −37/+40 N, alcanza aproximadamente 0,976 g adicionales en cualquier dirección con reserva de 1 N·m. **No demuestra el objetivo de 1 g omnidireccional.** La rapidez también depende de respuesta, saturación y seguimiento de orientación.

La velocidad del servo sin carga no prueba inversión de empuje bajo carga. Las palas supuestas implican retención cercana a 0,8 kN por pala a 6000 rpm. Cancelar idealmente el momento giroscópico total no elimina cargas locales. Véase [evaluación integrada del rotor](EVALUACION-INTEGRADA-ROTOR.md).

## Vuelo rápido y transición

El [contraste NASA](CONTRASTE-NASA-TRANSONICO.md), basado en [Harris y Landrum](https://ntrs.nasa.gov/citations/19660003947), no valida una tabla universal de Mach crítico frente a alargamiento ni prueba que L/D ≥ 6 sea obligatorio.

Las estimaciones originales de 12–20 g del cuerpo no quedaron confirmadas. Los momentos a incidencia fija de 10° tampoco son cargas inevitables en crucero: el equilibrio con cola puede requerir incidencia mucho menor. El método corporal se contrastó con [Allen y Perkins, TR 1048](https://ntrs.nasa.gov/citations/19930090962); el cuerpo integrado con conductos sigue sin validarse. Un borde de salida afilado no es requisito universal para toda fuerza sustentadora corporal.

Los modelos favorecen estudiar superficies grandes durante transición y menor área expuesta al acelerar. Se calcularon equilibrios con reducción de área, **no una transición dinámica validada**. El mapa de rotor en estacionario no cubre el flujo oblicuo de esa fase.

| Masa, L/D 6 y ala central recogida | Arrastre parcial a 600 km/h | A 1000 km/h |
|---|---:|---:|
| 2 kg | 25–44 N | 65–116 N |
| 5 kg | 45–80 N | 115–209 N |
| 10 kg | 71–125 N | 179–328 N |

Extremos de hipótesis de fricción, forma y superficies; excluyen onda, tomas, base e interferencias. No permiten calcular velocidad máxima con el empuje estático. Los [caudales publicados del P100](https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/RC%20ENGINES/Engines/p100_rx-bl) permiten dimensionar pasos preliminares, pero no sustituyen un mapa de empuje instalado. Véase [tomas y empuje](TOMAS-Y-EMPUJE-INSTALADO.md).

## Estructura y alternativas

Alargar el cuerpo aumenta masa superficial y flexibilidad en la comparación de viga. El modelo continuo no representa aberturas; algunas tapas salen del régimen de pequeñas deformaciones bajo los escenarios de presión. Ni esa viga ni su frecuencia con apoyo central prueban ausencia de pandeo o flutter. Véanse [estructura](ESTRUCTURA-PRELIMINAR.md) y [NASA SP-8007](https://ntrs.nasa.gov/citations/20205011530).

El anillo tiene evidencia favorable en ciertas condiciones de baja velocidad, pero nuestros tamaños cambian Reynolds y el fuselaje introduce interferencia. [NACA TN 4117](https://ntrs.nasa.gov/citations/19930084906) no valida un anillo integrado a Mach 0,82. Véase [comparación anular](ALA-ANULAR-CONTRASTE.md). Cuerpos sustentadores y formas achatadas aún no tienen comparación integrada equivalente: no se declaran inferiores por falta de cálculo.

## Decisiones permitidas por la evidencia

| Decisión | Estado |
|---|---|
| Mantener variantes independientes de 2, 5 y 10 kg | Sí, como requisito y proceso |
| Usar cuerpo circular alargado como referencia | Razonable; no selección óptima definitiva |
| Afirmar 1 g en toda dirección con orientación independiente | No demostrado |
| Declarar cerrado el candidato integrado de 5 kg | No; excede el presupuesto con sus asignaciones conservadas |
| Garantizar 600 o 1000 km/h | No demostrado |
| Elegir L/D 6–8 o 12 como óptimo global | No demostrado |
| Afirmar imposibilidad física del concepto | No justificado |
| Usar dibujos como planos de fabricación | No; son conceptos |

## Evidencia necesaria para el cierre real

1. **Rotor completo:** empuje, par y potencia bidireccionales frente a paso/régimen/tensión; respuesta bajo carga; masa e inercia reales. La rama inversa incompleta no se resuelve aumentando decimales.
2. **Configuración única:** posiciones, volúmenes, masas y cinemática de todos los componentes; colisiones durante plegado; cuerpo con entradas y salidas. Los cálculos de geometrías distintas deben trasladarse a una única configuración consistente.
3. **Aerodinámica y propulsión:** fuerzas, momentos y derivadas en estacionario, transición y avance; empuje instalado y distorsión de entrada. CFD requiere verificación de malla/modelo y contraste experimental.
4. **Estructura real:** material, espesores, uniones, aberturas, cierres, modos, pandeo y aeroelasticidad. Los modelos preliminares no acreditan mecanismos listos para volar.
5. **Selección óptima:** dominio de arquitecturas y criterios explícitos, incluyendo autonomía, aceleración y respuesta. Sin esos datos no existe un ganador único defendible como «el mejor posible».

No se exige inventar ahora una duración exacta: puede estudiarse una frontera de prestaciones. Pero ninguna duración queda garantizada sin cerrar conjuntamente energía, combustible, masa y temperatura.

## Lectura de los archivos anteriores

La búsqueda adicional y la especificación de entradas están en [DATOS-PARA-CERRAR-VALIDACION.md](DATOS-PARA-CERRAR-VALIDACION.md). Distingue fuentes relacionadas de mapas directamente aplicables y registra las capacidades de cálculo comprobadas.

Este documento es la síntesis vigente. Los informes previos conservan escenarios propios, no configuraciones finales compatibles por defecto. [ESTADO-VERIFICACION-GLOBAL.md](../../ESTADO-VERIFICACION-GLOBAL.md) audita los requisitos. Scripts y resultados permiten reproducir los cálculos; más puntos del mismo modelo no sustituyen evidencia ausente.

El informe consolidado queda entregado. **El objetivo global no está completado y su validación queda bloqueada por datos pendientes**, sin declaración de diseño óptimo validado ni listo para fabricar. El 30 de octubre de 2026 el usuario confirmó que los modelos y datos adicionales deben producirse por nosotros, pero todavía no; esa etapa no se inicia ahora.


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
