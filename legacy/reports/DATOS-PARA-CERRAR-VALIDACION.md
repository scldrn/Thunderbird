# Datos necesarios para cerrar la validación integrada

Revisión de disponibilidad: 30 de octubre de 2026. No se enviaron consultas a fabricantes ni se compraron componentes.

## Resultado de la búsqueda adicional

Se localizaron fuentes primarias relacionadas, pero no un mapa instalado que valide nuestro reactor ni un mapa medido del rotor SD8020 de 457,2 mm propuesto. Esto significa «no localizado en las fuentes revisadas», no inexistencia universal de esos datos.

- [OSPRI, revisión final de University of Colorado](https://www.colorado.edu/aerospace/sites/default/files/attached-files/ospri_sfr.pdf): proyecto de toma en S para P100-RX, con punto de diseño estático. Las diapositivas 22–25 describen inconsistencias en la medición de empuje, fricción y restricción de pruebas a 120 kRPM tras problemas de estabilidad. No se adopta como mapa de empuje en avance ni como prueba de que nuestra toma conserve el empuje.
- [Vlady, Yatsko y Mavris, efecto de álabes guía variables](https://www.tedvlady.com/sciTech_Vlady2020VIGV.pdf): estudio específico de modificación de entrada sobre un P100-RX. Se identifica como referencia de integración, no como línea de operación del P100-RX-BL de nuestra configuración en Mach 0,49–0,82.
- [Grupo de investigación de hélices de paso variable](https://sidsresearchcommunity.com/research/propeller-aerodynamics-and-distributed-propulsion/variable-pitch-propeller.html): identifica los trabajos AIAA 2025-1267 y 2026-0026 sobre incidencia y vuelo casi transversal. En esta revisión se verificó su identificación bibliográfica; no se recuperó del editor el texto de 2025 mediante la herramienta web. No se han incorporado coeficientes numéricos no consultados.
- [MIT, quadrotor de paso variable](https://acl.mit.edu/projects/variable-pitch-quadrotor): demuestra el principio en otro prototipo. No suministra por sí solo un mapa escalable sin validación a nuestro rotor, masa y fuerzas.

## Estado del entorno de cálculo

En la carpeta del proyecto no se localizaron archivos STEP, IGES, STL, MSH, SU2 o FOAM de la aeronave integrada. `SU2_CFD`, `simpleFoam` y `gmsh` no se encontraron en el PATH de la sesión. Esto no prueba que no existan otras instalaciones; registra lo comprobado.

Instalar un programa no resolvería automáticamente el problema: primero hace falta una geometría coherente, condiciones de contorno y datos de contraste. Un resultado CFD sin verificación y sin correspondencia con la configuración no convertiría las estimaciones existentes en prestaciones demostradas.

## Matriz de entradas imprescindibles

| ID | Datos necesarios | Condiciones que deben acompañarlos | Qué cálculo desbloquean |
|---|---|---|---|
| R01 | Empuje, par y potencia eléctrica del rotor completo en ambos sentidos | Geometría identificada, paso, RPM, tensión, temperatura, densidad e incertidumbre | Envolvente continua de fuerza/momento y potencia de estacionario |
| R02 | Respuesta temporal del rotor y del mecanismo de paso bajo carga | Comando y respuesta sincronizados, límites, inversión, retardo y asentamiento | Reorientación/traslación brusca con saturación real |
| R03 | Fuerzas y momentos del rotor en flujo axial y oblicuo | Velocidad y ángulo del flujo, paso/RPM, instalación, régimen de avance | Transición con rotores desplegados y durante descarga |
| E01 | Empuje neto o bruto del reactor instalado, claramente identificado | Presión/temperatura totales de entrada, caudal, velocidad libre, combustible, RPM/control y salida | Balance de empuje–arrastre y aceleración en avance |
| E02 | Recuperación y distorsión de toma, pérdidas y geometría del escape | Mismo motor, caudal, incidencia y configuración que E01 | Integración de conducto y límites de operación |
| G01 | Geometría exterior/interior y cinemática completa | Coordenadas, unidades, piezas, entradas/salidas y posiciones desplegadas/recogidas | Colisiones, área, volumen útil y dominio CFD |
| M01 | Lista de masas e inercias de componentes completos | Posiciones, tolerancias, combustible y batería; sin doble contabilización | Cierre iterativo, centro de masa y matriz de inercia |
| A01 | Fuerzas, momentos y derivadas aerodinámicas del conjunto | Reynolds, Mach, incidencia/deriva y estados de mecanismos | Equilibrio, estabilidad y comparación de geometrías |
| S01 | Materiales, espesores, uniones y modos de la estructura real | Aberturas, cierres, holguras, cargas y condiciones de apoyo | Resistencia, pandeo, vibración y aeroelasticidad |

No basta un único número de empuje máximo, un tiempo de servo sin carga ni una curva de perfil bidimensional. Los datos deben cubrir los estados demandados y tener procedencia y unidades. Una celda desconocida permanece desconocida: no debe rellenarse con cero ni con el extremo de una curva distinta.

## Requisitos de cobertura del candidato actual

Para R01/R02, la envolvente debe permitir comprobar las demandas alrededor de ±39 N por módulo y la reserva de momentos usada en el estudio de 5 kg, incluyendo la rama negativa. Esto es una referencia de demanda del modelo, no un ensayo validado ni un requisito universal para cualquier arquitectura.

Para R03, la cobertura se deriva de la trayectoria de transición finalmente elegida, no solo de la velocidad máxima de crucero. No se debe suponer que todos los rotores experimentan el mismo flujo ni usar directamente su mapa estático a velocidad alta.

Para E01, hay que distinguir empuje neto de bruto para evitar restar dos veces el término de entrada. La curva debe corresponder al motor y versión empleados: datos de P100-RX, RX-BL y otras revisiones no se consideran intercambiables sin justificarlo.

Para G01/M01, el candidato de control L/D 4 y las referencias aerodinámicas L/D 6 deben reconciliarse antes de afirmar que sus resultados pertenecen al mismo vehículo. La masa adicional de superficies y cierres necesita volver al dimensionamiento de rotor y batería.

Para A01/S01, la convergencia numérica se documenta por separado de la incertidumbre del modelo y del contraste experimental. No se llamará «validado» a un resultado solo porque el solucionador converja.

## Orden de resolución

Primero comprobar R01, R02 y M01 del conjunto reversible: su masa y potencia condicionan todas las variantes. Después fijar G01 y seleccionar el reactor con E01, no solo con catálogo. Con esa configuración se resuelven R03/E02/A01 y la transición, incorporando S01. Cada cambio material de masa o forma obliga a repetir los balances afectados.

La comparación final debe conservar alternativas: si el conjunto no cierra, procede cambiar arquitectura/componentes y reevaluar, no declarar imposible toda la clase de vehículos. La decisión de «mejor» necesita además la frontera entre masa, velocidad, agilidad y autonomía.

Este documento especifica las entradas pendientes. No acredita su disponibilidad ni reemplaza ensayos. El informe consolidado conserva el dictamen de viabilidad no demostrada.
