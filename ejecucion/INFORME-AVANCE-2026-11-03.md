# Ejecución del plan maestro: G0 y cribado G1

3 de noviembre de 2026. Objetivo activo: completar el plan maestro. Este informe registra trabajo ejecutado; no declara cerrados G0, G1 ni el diseño de producto. `ESTADO-TAREAS.csv` contiene seguimiento separado de la matriz inicial de planificación.

## Referencia y decisiones

Arquitectura A: ventiladores internos. A07 es la referencia geométrica actual; se identificaron nueve STEP de 2/5/10 kg objetivo y tres poses mediante SHA-256. Las masas son objetivos de integración, no masas reales verificadas. `../configuraciones/A07_BASE.json` y `ESCENARIOS_INVESTIGACION.json` conservan unidades, ejes, escenarios y carencias. Trece reconciliaciones históricas figuran en `G0/REGISTRO-RECONCILIACION.csv`.

Se encontró una incompatibilidad de ejes: nariz CAD hacia −X y avance de los modelos de vuelo hacia +X. La rotación propia CAD→FLU es diag(−1,−1,+1); longitudes CAD mm se convierten a m. `configuraciones/base.py` implementa conversión de puntos, vectores, tensores y referencia de momento. Seis pruebas pasan, incluidas las huellas de nueve STEP. No se han migrado todos los consumidores históricos. El origen es un datum geométrico; no es un CG físico medido.

## Herramientas operativas

- Blender 5.2.3 LTS: importación/render previos conservados.
- FreeCAD 1.1.4: se completó la instalación en Aplicaciones y su ejecutable instalado responde con salida 0.
- ParaView 6.2.0 arm64: se instaló la distribución oficial estándar, huella verificada, firma válida y notarización aceptada por macOS. Arranque, lectura OpenFOAM y render pasan; interfaz abierta y escena comprobada visualmente. Véase `../integracion_apps/REPARACION-PARAVIEW.md`.
- Entorno Python registrado en `G0/ENTORNO_PYTHON.json`. Docker dispone de aproximadamente 8 GB para sus contenedores; no se presupone la memoria completa del host.

Los dos solvers históricos de vehículo continúan pausados. Los benchmarks nuevos son procesos separados, ya terminados, y no se interpretan como continuación de aquellos campos.

## Auditoría CAD nominal

La referencia A07 cerrada de 5 kg objetivo contiene 208 registros de piezas válidas. Dimensiones medidas: **1341 × 321,821 × 242,538 mm**. Suma de volúmenes nominales de piezas: **1,977105 L**, sin descontar solapes. No es volumen útil ni masa. Las diferencias pequeñas con metadatos antiguos se registran usando los sólidos reimportados como fuente actual; el primer rechazo de tolerancia se conserva.

Se comprobaron 580 parejas BRep, tras descarte por cajas envolventes de 21.528 parejas posibles. Resultado: 73 intersecciones nominales, cero fallos booleanos. Clasificación: 4 duplicaciones de estilo, 48 encuentros eje–álabe, 12 de soportes, 4 de asientos de tornillo, 4 entradas de ejes en reservas de actuador y 1 encuentro pequeño de raíz. Las uniones por definir no se cuentan automáticamente como defectos; tampoco se declaran aprobadas.

**A08 candidata** conserva 208 registros válidos y corrige siete piezas por sustracción. Las nueve parejas locales corregidas dan volumen de intersección cero después de reimportar STEP. El asiento Ø4,6 mm es supuesto; no se ha dimensionado una unión de fabricación. A07 sigue siendo canónica. Esta candidata no incluye otras poses/escalas ni cierre de mecanismos, estructura o hardware.

## Masa, área y energía: resultados condicionados

Se generaron 18 escenarios de masa, 9 referencias de disco, 243 sensibilidades energéticas estacionarias y 216 de avance. No son observaciones ni bandas de confianza. Se listan **12 grupos de hardware sin identificar**, con masa vacía, nunca cero.

Para la escala objetivo de 5 kg, asignar 1600 kg/m³ a las piezas de la hipótesis compuesta, con otras densidades declaradas en el script, da aproximadamente **2,679 kg de geometría nominal** sin reservas de equipos ni tubo axial opcional. Con una reserva provisional del 15% quedan **1,571 kg** para el resto. Si la envolvente tubular OD60/ID56×800 mm se fabricara en aluminio a 2700 kg/m³, añadiría **0,787 kg**. Esa envolvente representa una reserva de instalación, no un tubo final obligatorio ni un motor. No hay cierre de masa; deben resolverse solapes/uniones, materiales y equipos antes de aceptar una BOM física.

Cuatro discos libres ideales del diámetro de taladro escalado dan referencias de potencia estacionaria de **506/1473/3307 W** para 2/5/10 kg. Se usa ρ=1,225 kg/m³. No son potencia eléctrica instalada ni una cota universal para ventiladores carenados. Las sensibilidades usan eficiencias y energía específica supuestas, sin acreditar potencia, temperatura o batería real.

Los límites geométricos de conos ascendentes se expresan como condiciones necesarias: a cuerpo horizontal, sin aerodinámica externa, un cono efectivo de 35° limita la bola isotrópica de aceleración adicional a como máximo 0,574 g y la aceleración horizontal a altura fija a como máximo 0,700 g, antes de saturaciones y equilibrio de momento. No se acredita el cono instalado ni se reduce el objetivo final a esos valores.

## Verificación CFD y datos recuperados

Diez casos pequeños de canal newtoniano se compararon con solución analítica transitoria y operador semidiscreto independiente. La familia inicial se rechaza para convergencia de malla. El caso de 80 celdas, 50 correctores exteriores y Δt=0,0025 s presenta error máximo normalizado **0,017932% a t=4 s**, con 37 s de reloj. No demuestra orden formal, turbulencia, choque o rotor. Se conservan todos los campos y registros: `G0/INFORME-BENCHMARK.md`.

Para el módulo se recuperó [Martin y Tung, NTRS 20050009943](https://ntrs.nasa.gov/citations/20050009943). La geometría completa de pala/conducto aún no está recuperada para reproducción exacta. Para compresible se recuperaron CAD y Cp del [ONERA M6 en TMR](https://tmbwg.github.io/turbmodels/onerawingnumerics_val.html); se registran diferencias de borde de salida y definiciones de Reynolds. Todavía no hay solución de esos benchmarks ni validación instalada del vehículo.

## Continuación priorizada

1. Completar un benchmark experimental reproducible del rotor y el piloto compresible con coste acotado; no iniciar campaña masiva por el éxito del canal.
2. Dimensionar el módulo propio con la misma geometría, definición de seis cargas, potencia y dinámica; usar sus resultados para cerrar la factibilidad de masa/energía antes de detallar el resto.
3. Resolver las interfaces mecánicas auditadas y migrar consumidores a la configuración/ejes únicos. Cada cambio propagará masa, CFD, control y visualización afectados.
4. Seguir G2–G8 y el plan de contraste físico. Un CAD o benchmark que pasa no sustituye esos hitos.

No se publica un porcentaje global de desempeño: las tareas no tienen el mismo coste y los hitos de validación siguen abiertos.
