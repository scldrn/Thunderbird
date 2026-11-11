# C02: integración compacta del módulo interno

3 de noviembre de 2026. Trabajo computacional del plan maestro, principalmente T11/T16/T17. **C02 es una candidata de alojamiento y cinemática, no una selección de motor ni un producto aprobado.** A07 continúa como referencia canónica; las versiones de 2 y 10 kg siguen abiertas como configuraciones propias.

## Resultado materializado

Se generó una integración de referencia de 5 kg objetivo con cuatro rotores nominales D82 mm, estaciones CAD x=±160 mm e y=±76 mm. Conserva el loft exterior deportivo y las cuatro aletas posteriores del antecedente. Se trasladaron los puertos, tapas y aros; se reconstruyeron localmente sus zonas de piel. El tubo axial OD60 sigue siendo una reserva vacía, no un motor.

La candidata cerrada contiene **316 registros de piezas válidos reimportados**; el corte, 291. `integracion_x160/INTEGRACION.json` identifica fuentes A08/C01, cambios y huellas. Hay STEP, archivo FreeCAD y escenas Blender de la misma geometría. No se sustituyeron archivos A07/A08.

## Comprobado geométricamente

| Comprobación | Resultado y límite |
|---|---|
| Módulos aislados D82/D102,5, revisión r2 | 58 registros cada uno; 106 parejas nominales por módulo, sin intersecciones volumétricas en neutro |
| Primer módulo D82 en posición anterior x=−200 | Dentro de la envolvente interior de referencia; no acredita los otros módulos o todos los movimientos |
| Primer módulo D102,5 en posición anterior | 11 piezas sobresalen de esa envolvente; no se declara instalado |
| Integración compacta x=±160 | 314 parejas nuevas entre módulos y demás piezas, o entre módulos distintos, sin intersecciones nominales |
| Tapas trasladadas | 61 posiciones y 808 parejas geométricas evaluadas, sin fallos en el recorrido conceptual estudiado |
| Sincronización | Cuatro filas independientes; 181 ángulos por fila y tres ejes de pasador, error de alineación inferior a 10⁻¹² mm dentro del modelo rígido |

Las parejas internas del módulo se comprueban por separado de la integración; los encuentros históricos no modificados no quedan aprobados por esta auditoría. El barrido de tapas es discreto y no incluye guías, bisagras, cierres, deformaciones o tolerancias bajo carga.

El radio nominal R41 del BEM no limita por sí solo todas las esquinas de una pala con cuerda finita. Se rechazó inicialmente ese cilindro como envolvente del giro. Un cilindro anular de radio **41,5 mm**, con hueco del cubo apropiado, contiene el rotor C02 completo según la resta BRep; frente al taladro R42 queda una separación radial conservadora nominal de **0,5 mm**. No es una tolerancia aprobada frente a flexión, dilatación o fabricación. También se conservó el rechazo de una resta con `Compound` de sólidos solapados; las envolventes se unieron booleanamente antes de comprobar contención.

## Qué cambió en el módulo

La alternativa compacta reserva el motor dentro de un cubo ahuecado. Evita el eje largo que habría atravesado los bancos superiores. El rotor queda en z=0 del módulo; el cubo, el alojamiento, el asiento y cuatro soportes diagonales están definidos geométricamente. El motor y sus apoyos continúan como volúmenes reservados. Falta resolver transmisión de par al cubo, retención y diseño electromagnético/térmico.

Se unieron geométricamente álabe, vástago, manivela y pasador de cada unidad. Los vástagos atraviesan apoyos con casquillos y asientos definidos. Cada fila dispone de una barra que sincroniza sus tres álabes y una interfaz de accionamiento; se alojaron cuatro reservas de servo por módulo. La unión integral es una hipótesis constructiva: material, proceso, desgaste, cargas y acoplamientos no están aprobados.

El radio de manivela es 6 mm. La barra se traslada según `δt=±6 sin α`, `δz=6(cos α−1)`. Los pasadores son Ø2 y los taladros Ø2,2 mm nominales. Los acoplamientos tienen 2 mm de inserción nominal por extremo; falta su apriete/retención. No se equipara α mecánico con desviación del chorro, ni la identidad cinemática con velocidad de respuesta de un servo real.

Para D82, las envolventes parciales dan 1,93 mm entre filas ortogonales, 1,56 mm entre asiento de motor y barrido inferior, y 1,71 mm entre soportes y límite inferior del rotor. Hay 0,5 mm entre reserva de motor y cubo tanto radial como axialmente. Son dimensiones del candidato rígido, no márgenes estructurales certificados. Fuente: `salida/*/AUDITORIA.json`.

## Compromiso de tamaño y posiciones

Se evaluaron **44 combinaciones** de envolventes conservadoras, posiciones, corredores axiales reservados OD40/OD60 y multiplicadores de anchura del loft. Se reservaron los mismos tamaños de actuador: no se redujeron para hacer pasar el dibujo. La separación lateral también conserva espacio entre las dos reservas de servo orientadas hacia el centro.

| Rotor nominal | Corredor axial | Estaciones x | Primer ancho ensayado suficiente, frente / atrás |
|---|---:|---:|---:|
| D82 | OD60 | ±160 mm | 1,00 / 1,00 |
| D82 | OD60 | ±200 mm | 1,00 / 1,05 |
| D102,5 | OD40 | ±160 mm | 1,10 / 1,20 |
| D102,5 | OD60 | ±160 mm | 1,15 / 1,20 |
| D102,5 | OD60 | ±200 mm | 1,15 / ninguno hasta 1,20 |

Estos factores son suficientes para las cajas/envolventes utilizadas, no mínimos físicos ni geometrías óptimas. Cambiar el corredor exige estudiar la propulsión axial; OD40 no acredita que quepa un reactor. El rotor mayor reduce potencia en C01, pero puede exigir más anchura, masa o cambios de disposición. Sus prestaciones de avance no se heredan del cuerpo original.

Pasar de x=±200 a ±160 reduce 20% el brazo longitudinal para una misma fuerza diferencial. La contribución de masas puntuales de los módulos a la inercia de cabeceo baja 36% si esas masas permanecen iguales. El cambio de agilidad total depende de la masa e inercia del resto del vehículo; no se declara una mejora dinámica sin ese cierre.

## Requisitos de motor: cálculo, no hardware disponible

Se aplican los puntos C01 de estacionario de 5 kg, κ=0,85 y eficiencia eléctrica conjunta 0,90 como **demandas de diseño**. No son cargas instaladas aceptadas del C02.

| Requisito por módulo | D82 | D102,5 |
|---|---:|---:|
| Reserva cilíndrica de motor | Ø21,8×16,1 mm | Ø27,5×19,35 mm |
| Potencia de eje del escenario | 668 W | 534 W |
| Par de eje del escenario | 0,138 N·m | 0,172 N·m |
| Régimen del escenario | 46.231 rpm | 29.588 rpm |
| Pérdida conjunta motor+ESC supuesta | 74,2 W | 59,4 W |
| Corriente DC de cuatro módulos a 24 V supuestos | 123,7 A | 99,0 A |

A 48 V, las corrientes calculadas se reducen a la mitad; esto no selecciona tensión, bobinado, batería o controlador. La corriente de fase no se obtiene de esa división. Con radio de entrehierro y longitud activa supuestos, los esfuerzos tangenciales medios exigidos son 22,7 y 14,8 kPa: son objetivos para un diseño electromagnético posterior, no prueba de que el motor exista o quepa con esas prestaciones.

`salida/REQUISITOS_MOTOR.csv` tiene 12 filas. Otras 108 sensibilidades térmicas separan la fracción de pérdida atribuida al motor y supuestos de conducción/convección. La exposición directa de todo el cilindro es deliberadamente optimista: el motor está dentro de una copa y faltan resistencias en serie, contactos y flujo de cavidad. No se predicen temperaturas reales ni se asigna una temperatura admisible de componente. La refrigeración es un requisito pendiente decisivo del alojamiento compacto.

## Masa e inercia: contabilidad parcial actualizada

Se recalcularon las propiedades de las 316 geometrías, con integración adaptativa, y tres hipótesis explícitas de densidad. Se excluyen **54 registros de reservas o interfaces sin hardware identificado**, con masa real vacía. No se tratan como cero. Las masas suman volúmenes nominales; uniones heredadas pueden compartir material. No son una cota inferior física.

| Hipótesis | Masa geométrica asignada | Remanente de 5 kg tras reserva provisional de 0,75 kg |
|---|---:|---:|
| Ligera, envolvente 1200 | 2,046 kg | 2,204 kg |
| Mixta, envolvente 1600 | 2,784 kg | 1,466 kg |
| Aluminio, 2700 | 4,421 kg | −0,171 kg |

Ese remanente debe cubrir energía y equipos todavía no identificados. No se transfieren automáticamente los 2,679 kg del A07 o la masa del rotor macizo C01 al nuevo cubo. `BOM_GEOMETRICA_PARCIAL.csv` y `MASA_INERCIA_PARCIAL.json` conservan densidades, roles, CG/tensores parciales y conversión CAD→FLU. Excluir equipos impide usarlos como inercia física de un simulador predictivo.

## Preparación numérica para el mapa de flujo

Se contrastó `fanPressureJump` de OpenFOAM 13 con un canal analítico, sin simular todavía el vehículo. La [documentación primaria](https://cpp.openfoam.org/v13/classFoam_1_1fanPressureJumpFvPatchScalarField.html) define la curva en función del caudal y la opción de inversión de signo. Se usó `fanCurve` y presión cinemática; un salto de 1 m²/s² equivale a 1,225 Pa con la densidad de referencia.

Con una celda longitudinal, la velocidad coincidía pero decenas de miles de soluciones de presión alcanzaban 1000 iteraciones; esos ajustes se rechazaron. Con cuatro celdas longitudinales, el gradiente ±5 m/s² queda resuelto, no hay soluciones alcanzando ese límite, y ambos signos dan error máximo relativo de velocidad **0,03317% a t=4 s**. Las comprobaciones de caudal y trabajo del salto frente a fuerza volumétrica equivalente pasan. Cada caso nuevo consumió unos 10,9 s CPU/11 s de reloj. Se conserva todo, incluidos los rechazos: `../../G2/benchmark_salto/AUDITORIA.json` desde este directorio.

Esto verifica ese operador y problema. No acredita curva de ventilador, turbulencia, pérdidas de álabe, empuje, respuesta o coste de una campaña tridimensional.

## Archivos y próximos cierres

`integracion_x160/` contiene dos STEP, FreeCAD, dos escenas Blender, imágenes, reglas de tapas y auditorías. FreeCAD importó, validó y reabrió el archivo: 349 objetos documentales y 345 con Shape, que **no son un nuevo recuento de piezas**. El archivo conserva sólidos importados; la parametrización reproducible está en los generadores Python, no en un historial nativo de fabricación reconstruido. Los acabados de los renders son cosméticos.

Sigue pendiente el primer dominio fluido identificado del módulo, con hipótesis de sellado y rotor/disco explícitas, reacción de todas las paredes, balances, sensibilidad y contraste. Después: diseño del motor/ESC/refrigeración, mapa de seis cargas y potencia, respuesta temporal, mecanismos reales de tapas, estructura y masa integrada. El alcance global de agilidad, 2–10 kg, 600–1000 km/h y autonomía permanece sin cerrar. No se ha completado G2/G3 ni el plan maestro.
